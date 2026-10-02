"""Editor visual del manual: página web local para editar los archivos .md sin ver Markdown.

Uso: doble clic en "USAR EL MANUAL/Windows/2. Editar el manual.bat" o en "USAR EL MANUAL/Mac/2. Editar el manual.command",
o  python sistema/herramientas/editor.py [--sin-navegador]
Abre http://127.0.0.1:8001. Solo usa la biblioteca estándar de Python.
Protecciones: solo toca archivos dentro de docs/, respalda cada guardado en herramientas/respaldos/,
las páginas eliminadas van a herramientas/papelera/ y se pueden recuperar, y no guarda encima
de una página que cambió en el disco mientras se editaba.
Versiones: cada respaldo es una versión anterior de la página. Se listan en /api/versiones y se
recuperan con /api/restaurar, que antes respalda la versión actual para poder deshacer.
Vista previa: /vista/... reenvía a "mkdocs serve" (puerto 8000). Así la vista previa es del mismo
origen que el editor, y este puede recordar y ajustar dónde está la pantalla.
"""
import base64, http.server, json, os, re, shutil, socket, subprocess, sys, threading, time, unicodedata, urllib.error, urllib.request, webbrowser
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # carpeta sistema
DOCS = os.path.join(RAIZ, "docs")
RESPALDOS = os.path.join(RAIZ, "herramientas", "respaldos")
PAPELERA = os.path.join(RAIZ, "herramientas", "papelera")
MKDOCS_YML = os.path.join(RAIZ, "mkdocs.yml")
PUERTO_EDITOR, PUERTO_VISTA = 8001, 8000
PROTEGIDAS = {"index.md"}                 # páginas que no se pueden eliminar
MAX_IMAGEN = 10 * 1024 * 1024
BLOQUEO = threading.Lock()                # evita escrituras simultáneas en mkdocs.yml


class ErrorUsuario(Exception):
    """Error con un mensaje pensado para mostrarse tal cual a la persona."""


def ruta_segura(rel):
    """Ruta absoluta dentro de docs/; cualquier intento de salir de ahí se rechaza."""
    p = os.path.normpath(os.path.join(DOCS, rel))
    if not p.startswith(DOCS + os.sep):
        raise ErrorUsuario("Esa ruta no pertenece al manual.")
    return p


def leer(p):
    return open(p, encoding="utf-8").read()


def escribir(p, texto):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def normal(x):
    return "".join(c for c in unicodedata.normalize("NFD", x.lower()) if unicodedata.category(c) != "Mn")


def titulo(md_path):
    try:
        for linea in open(md_path, encoding="utf-8"):
            if linea.startswith("# "):
                return linea[2:].strip()
    except OSError:
        pass
    return os.path.splitext(os.path.basename(md_path))[0]


# ---------------- Menú del manual (nav de mkdocs.yml) ----------------
def rutas_en_menu():
    return re.findall(r":\s*([\w/.-]+\.md)\s*$", leer(MKDOCS_YML), re.M)


def agregar_al_menu(rel, nombre):
    """Agrega la página dentro de 'Módulos', antes de Glosario. El nombre va entre comillas
    para que un ':' o un '#' en el nombre no dañe el archivo de configuración."""
    with BLOQUEO:
        txt = leer(MKDOCS_YML)
        if re.search(r":\s*" + re.escape(rel) + r"\s*$", txt, re.M):
            return
        linea = f"      - {json.dumps(nombre, ensure_ascii=False)}: {rel}"
        if "  - Glosario: glosario.md" in txt:
            txt = txt.replace("  - Glosario: glosario.md", linea + "\n  - Glosario: glosario.md", 1)
        else:
            raise ErrorUsuario("No encontré dónde agregar la página en el menú. Pide ayuda técnica.")
        escribir(MKDOCS_YML, txt)


def quitar_del_menu(rel):
    with BLOQUEO:
        txt = leer(MKDOCS_YML)
        nuevo = re.sub(r"^[ \t]*- [^\n]*:\s*" + re.escape(rel) + r"[ \t]*\n", "", txt, flags=re.M)
        escribir(MKDOCS_YML, nuevo)


# ---------------- Páginas ----------------
def listar_paginas():
    paginas = []
    for base, _, archivos in os.walk(DOCS):
        for a in sorted(archivos):
            if a.endswith(".md"):
                abs_ = os.path.join(base, a)
                paginas.append({"ruta": os.path.relpath(abs_, DOCS).replace("\\", "/"), "titulo": titulo(abs_)})
    nav = rutas_en_menu()
    paginas.sort(key=lambda p: nav.index(p["ruta"]) if p["ruta"] in nav else len(nav))
    for p in paginas:
        p["protegida"] = p["ruta"] in PROTEGIDAS
    return paginas


def paginas_que_enlazan(rel):
    """Páginas que tienen un enlace a 'rel'. Se usa para avisar antes de eliminar."""
    destino = ruta_segura(rel)
    quienes = []
    for p in listar_paginas():
        if p["ruta"] == rel:
            continue
        origen = ruta_segura(p["ruta"])
        for enlace in re.findall(r"\]\(([^)#\s]+\.md)", leer(origen)):
            if os.path.normpath(os.path.join(os.path.dirname(origen), enlace)) == destino:
                quienes.append(p["titulo"])
                break
    return quienes


RX_RESPALDO = re.compile(r"(\d{8}-\d{6}(?:-\d+)?)__(.+)$")


def respaldar(abs_):
    """Copia el archivo a respaldos/ y devuelve el nombre de la copia. copy2 conserva la fecha
    de modificación, que es la hora en que se guardó esa versión."""
    if not os.path.exists(abs_):
        return None
    os.makedirs(RESPALDOS, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d-%H%M%S")
    nombre = os.path.relpath(abs_, DOCS).replace(os.sep, "__")
    archivo, n = f"{marca}__{nombre}", 1
    while os.path.exists(os.path.join(RESPALDOS, archivo)):     # dos respaldos en el mismo segundo
        archivo, n = f"{marca}-{n}__{nombre}", n + 1
    shutil.copy2(abs_, os.path.join(RESPALDOS, archivo))
    return archivo


# ---------------- Versiones anteriores ----------------
def fecha_de(p):
    return datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%dT%H:%M:%S")


def listar_versiones(rel):
    """Versión actual y versiones anteriores de una página, de la más nueva a la más vieja.
    Se omiten las idénticas a la siguiente más nueva: guardar sin cambios no crea una versión."""
    p = ruta_segura(rel)
    if not os.path.isfile(p):
        raise ErrorUsuario("La página ya no existe.")
    clave = rel.replace("/", "__")
    copias = []
    if os.path.isdir(RESPALDOS):
        for a in os.listdir(RESPALDOS):
            m = RX_RESPALDO.match(a)
            if m and m.group(2) == clave:
                copias.append((os.path.getmtime(os.path.join(RESPALDOS, a)), a))
    copias.sort(reverse=True)
    versiones = [{"archivo": None, "fecha": fecha_de(p), "actual": True}]
    siguiente = leer(p)
    for _, a in copias:
        contenido = leer(os.path.join(RESPALDOS, a))
        if contenido == siguiente:
            continue
        versiones.append({"archivo": a, "fecha": fecha_de(os.path.join(RESPALDOS, a)), "actual": False})
        siguiente = contenido
    return versiones


def archivo_de_version(rel, archivo):
    m = RX_RESPALDO.match(archivo or "")
    if not m or "/" in archivo or "\\" in archivo or m.group(2) != rel.replace("/", "__"):
        raise ErrorUsuario("Esa versión no pertenece a esta página.")
    p = os.path.join(RESPALDOS, archivo)
    if not os.path.isfile(p):
        raise ErrorUsuario("Esa versión ya no existe.")
    return p


# ---------------- Vista previa ----------------
RX_LIVERELOAD = re.compile(rb"<script>\s*var livereload = function.*?livereload\((\d+), \d+\);\s*</script>", re.S)
ESPERA_VISTA = ("<!DOCTYPE html><meta charset='utf-8'><meta http-equiv='refresh' content='2'>"
                "<body style='font-family:sans-serif;color:#667884;text-align:center;padding-top:80px'>"
                "Preparando la vista previa…</body>").encode("utf-8")


def pedir_vista(ruta_y_consulta):
    """Trae una página de mkdocs serve. Le quita su recarga automática, porque de recargar se
    encarga el editor, y devuelve el número de compilación para saber cuándo hay una versión nueva."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PUERTO_VISTA}/{ruta_y_consulta}", timeout=15) as r:
            cuerpo, tipo, codigo = r.read(), r.headers.get("Content-Type", "application/octet-stream"), 200
    except urllib.error.HTTPError as e:
        cuerpo, tipo, codigo = e.read(), e.headers.get("Content-Type", "text/html"), e.code
    except OSError:
        return ESPERA_VISTA, "text/html; charset=utf-8", 200, ""
    epoca = ""
    if tipo.startswith("text/html"):
        m = RX_LIVERELOAD.search(cuerpo)
        if m:
            epoca = m.group(1).decode()
            cuerpo = cuerpo[:m.start()] + cuerpo[m.end():]
    return cuerpo, tipo, codigo, epoca


def texto_limpio(linea):
    """Quita los símbolos de Markdown para mostrar resultados de búsqueda legibles."""
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)(\{[^}]*\})?", r"Imagen: \1", linea)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"^\s*(#+|\d+\.|[-*]|!!!\s*\w+|\?\?\?\s*\w+)\s*", "", t)
    t = t.replace("**", "").replace("|", " ").replace('"', "").replace("\\", "")
    return re.sub(r"\s+", " ", t).strip()


def buscar(consulta):
    q = normal(consulta.strip())
    resultados = []
    if len(q) < 2:
        return resultados
    for pag in listar_paginas():
        for n, linea in enumerate(open(os.path.join(DOCS, pag["ruta"]), encoding="utf-8"), 1):
            limpio = texto_limpio(linea)
            if limpio and q in normal(limpio):
                resultados.append({"ruta": pag["ruta"], "titulo": pag["titulo"], "linea": n, "texto": limpio[:160]})
    return resultados[:80]


def carpetas_imagenes():
    base = os.path.join(DOCS, "imagenes")
    return sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))


def nombre_archivo(nombre):
    base = normal(nombre)
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")[:50]


# ---------------- Papelera ----------------
def a_papelera(rel):
    if rel in PROTEGIDAS:
        raise ErrorUsuario("Esta página no se puede eliminar.")
    p = ruta_segura(rel)
    if not os.path.isfile(p):
        raise ErrorUsuario("La página ya no existe.")
    os.makedirs(PAPELERA, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d-%H%M%S")
    archivo = f"{marca}__{rel.replace('/', '__')}"
    shutil.move(p, os.path.join(PAPELERA, archivo))
    quitar_del_menu(rel)
    return archivo


def listar_papelera():
    if not os.path.isdir(PAPELERA):
        return []
    items = []
    for a in sorted(os.listdir(PAPELERA), reverse=True):
        m = re.match(r"(\d{8})-(\d{6})__(.+\.md)$", a)
        if m:
            fecha = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").strftime("%d/%m/%Y %H:%M")
            items.append({"archivo": a, "ruta": m.group(3).replace("__", "/"), "fecha": fecha,
                          "titulo": titulo(os.path.join(PAPELERA, a))})
    return items


def recuperar(archivo):
    if "/" in archivo or "\\" in archivo or ".." in archivo:
        raise ErrorUsuario("Archivo no válido.")
    origen = os.path.join(PAPELERA, archivo)
    m = re.match(r"\d{8}-\d{6}__(.+\.md)$", archivo)
    if not m or not os.path.isfile(origen):
        raise ErrorUsuario("Esa página ya no está en la papelera.")
    rel = m.group(1).replace("__", "/")
    destino = ruta_segura(rel)
    if os.path.exists(destino):
        raise ErrorUsuario("Ya existe una página con ese nombre. Cámbiale el nombre a la actual antes de recuperar esta.")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.move(origen, destino)
    agregar_al_menu(rel, titulo(destino))
    return rel


# ---------------- Servidor ----------------
class Manejador(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _enviar(self, cuerpo, tipo, codigo=200, extra=None):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _json(self, datos, codigo=200):
        self._enviar(json.dumps(datos, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", codigo)

    def _error(self, e):
        if isinstance(e, ErrorUsuario):
            self._json({"error": str(e)}, 400)
        elif isinstance(e, FileNotFoundError):
            self._json({"error": "No se encontró el archivo."}, 404)
        else:
            self._json({"error": "Ocurrió un error inesperado: " + str(e)}, 500)

    def _cuerpo(self):
        n = int(self.headers.get("Content-Length", 0))
        if n > MAX_IMAGEN * 1.5:
            raise ErrorUsuario("El archivo es demasiado grande. El máximo es 10 MB.")
        return json.loads(self.rfile.read(n).decode("utf-8"))

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path == "/":
                html = leer(os.path.join(os.path.dirname(__file__), "editor.html")).replace("__PUERTO_VISTA__", str(PUERTO_VISTA))
                self._enviar(html.encode("utf-8"), "text/html; charset=utf-8")
            elif u.path.startswith("/docs/"):          # imágenes y letra del manual, para el editor
                p = ruta_segura(unquote(u.path[len("/docs/"):]))
                tipos = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml",
                         ".woff2": "font/woff2"}
                ext = os.path.splitext(p)[1].lower()
                if ext not in tipos or not os.path.isfile(p):
                    raise FileNotFoundError(p)
                self._enviar(open(p, "rb").read(), tipos[ext])
            elif u.path == "/api/paginas":
                self._json({"paginas": listar_paginas(), "carpetas": carpetas_imagenes()})
            elif u.path == "/api/pagina":
                self._json({"contenido": leer(ruta_segura(q["ruta"][0]))})
            elif u.path == "/api/buscar":
                self._json({"resultados": buscar(q.get("q", [""])[0])})
            elif u.path == "/api/enlaces":
                self._json({"paginas": paginas_que_enlazan(q["ruta"][0])})
            elif u.path == "/api/papelera":
                self._json({"items": listar_papelera()})
            elif u.path == "/api/versiones":
                self._json({"versiones": listar_versiones(q["ruta"][0])})
            elif u.path == "/api/version":
                self._json({"contenido": leer(archivo_de_version(q["ruta"][0], q.get("archivo", [""])[0]))})
            elif u.path.startswith("/vista/"):
                cuerpo, tipo, codigo, epoca = pedir_vista(self.path[len("/vista/"):])
                self._enviar(cuerpo, tipo, codigo, {"X-Epoca": epoca})
            else:
                self._json({"error": "No existe"}, 404)
        except Exception as e:
            self._error(e)

    def do_POST(self):
        try:
            d = self._cuerpo()
            if self.path == "/api/guardar":
                p = ruta_segura(d["ruta"])
                if not os.path.isfile(p):
                    raise ErrorUsuario("Esta página ya no existe. Puede que la hayan eliminado.")
                if "base" in d and leer(p) != d["base"]:
                    self._json({"error": "Esta página cambió mientras la editabas, quizás en otra ventana. "
                                         "Copia tu texto, vuelve a abrir la página y aplica tus cambios de nuevo.",
                                "conflicto": True}, 409)
                    return
                if not re.search(r"^# \S", d["contenido"], re.M):
                    raise ErrorUsuario("La página necesita su título principal. No se guardó.")
                respaldar(p)
                escribir(p, d["contenido"])
                self._json({"ok": True})
            elif self.path == "/api/restaurar":
                p = ruta_segura(d["ruta"])
                if not os.path.isfile(p):
                    raise ErrorUsuario("Esta página ya no existe. Puede que la hayan eliminado.")
                contenido = leer(archivo_de_version(d["ruta"], d.get("archivo")))
                if "base" in d and leer(p) != d["base"]:
                    self._json({"error": "Esta página cambió mientras la tenías abierta, quizás en otra ventana. "
                                         "Vuelve a abrirla e inténtalo de nuevo.", "conflicto": True}, 409)
                    return
                respaldo = respaldar(p)          # la versión actual queda como versión anterior
                escribir(p, contenido)
                self._json({"ok": True, "respaldo": respaldo, "contenido": contenido})
            elif self.path == "/api/imagen":
                pagina_dir = os.path.dirname(ruta_segura(d["pagina"]))   # se valida todo antes de escribir
                carpeta = re.sub(r"[^a-z0-9-]", "", d["carpeta"].lower()) or "varias"
                nombre = nombre_archivo(os.path.splitext(d["nombre"])[0]) or "captura"
                ext = os.path.splitext(d["nombre"].lower())[1] or ".png"
                if ext not in (".png", ".jpg", ".jpeg"):
                    raise ErrorUsuario("Solo se aceptan imágenes PNG o JPG.")
                datos = base64.b64decode(d["datos"].split(",", 1)[-1])
                if len(datos) > MAX_IMAGEN:
                    raise ErrorUsuario("La imagen pesa más de 10 MB.")
                if not (datos[:8] == b"\x89PNG\r\n\x1a\n" or datos[:3] == b"\xff\xd8\xff"):
                    raise ErrorUsuario("El archivo no es una imagen PNG o JPG válida.")
                destino = ruta_segura(f"imagenes/{carpeta}/{nombre}{ext}")
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                if os.path.exists(destino):
                    if not d.get("reemplazar"):
                        raise ErrorUsuario(f"Ya existe una imagen llamada {nombre}{ext}.")
                    respaldar(destino)
                open(destino, "wb").write(datos)
                rel = os.path.relpath(destino, pagina_dir).replace("\\", "/")
                self._json({"ruta": rel})
            elif self.path == "/api/nueva":
                nombre = re.sub(r"\s+", " ", d.get("nombre", "")).strip().lstrip("#").strip()[:60]
                archivo = nombre_archivo(nombre)
                if not archivo:
                    raise ErrorUsuario("Escribe un nombre para la página, con letras o números.")
                rel = f"modulos/{archivo}.md"
                p = ruta_segura(rel)
                if os.path.exists(p):
                    raise ErrorUsuario("Ya existe una página con ese nombre.")
                escribir(p, f"# {nombre}\n\n**Para qué sirve:** escribe aquí para qué sirve esta pantalla.\n\n"
                            "## Las partes de la pantalla\n\n## Cómo se hace\n\n1. Primer paso.\n")
                agregar_al_menu(rel, nombre)
                self._json({"ruta": rel})
            elif self.path == "/api/eliminar":
                self._json({"ok": True, "archivo": a_papelera(d["ruta"])})
            elif self.path == "/api/recuperar":
                self._json({"ruta": recuperar(d["archivo"])})
            else:
                self._json({"error": "No existe"}, 404)
        except Exception as e:
            self._error(e)


def puerto_libre(p):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", p)) != 0


def main():
    if puerto_libre(PUERTO_VISTA):   # levanta la vista previa si no está corriendo
        subprocess.Popen([sys.executable, "-m", "mkdocs", "serve", "-a", f"127.0.0.1:{PUERTO_VISTA}"],
                         cwd=RAIZ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not puerto_libre(PUERTO_EDITOR):
        print("El editor ya está abierto.")
        webbrowser.open(f"http://127.0.0.1:{PUERTO_EDITOR}")
        return
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", PUERTO_EDITOR), Manejador)
    if "--sin-navegador" not in sys.argv:
        threading.Thread(target=lambda: (time.sleep(2), webbrowser.open(f"http://127.0.0.1:{PUERTO_EDITOR}")),
                         daemon=True).start()
    print(f"Editor abierto en http://127.0.0.1:{PUERTO_EDITOR}  (cierra esta ventana para salir)")
    servidor.serve_forever()


if __name__ == "__main__":
    main()
