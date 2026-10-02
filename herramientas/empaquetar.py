"""Deja el manual web listo para enviar: dos archivos .zip en la carpeta que se indique
(la de Windows o la de Mac dentro de "USAR EL MANUAL", según quién lo ejecute).

Genera una versión aparte, pensada para publicarse en un servidor: se construye sin el
complemento "offline". Ese complemento sirve para abrir el manual con doble clic, pero hace
que el buscador dependa de un archivo que se descarga de internet. Sin él, el buscador
funciona siempre en el servidor.

Uso: python herramientas/empaquetar.py CARPETA_DESTINO. Lo llama "4. Enviar el manual" (.bat o .command)."""
import os, re, shutil, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # sistema/
CARPETA_USO = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(os.path.dirname(RAIZ), "USAR EL MANUAL")
NOMBRE = "Manual de usuario - App Ron Santa Teresa"
SITE = os.path.join(RAIZ, "site")

LEEME = """MANUAL DE USUARIO - APP RON SANTA TERESA

Para abrir el manual en tu computador:

1. Descomprime esta carpeta.
   En Windows: clic derecho sobre el archivo .zip y luego "Extraer todo".
   En Mac: doble clic sobre el archivo .zip.
2. Entra a la carpeta que se creó.
3. Haz doble clic en el archivo   ABRIR EL MANUAL

El manual se abre en tu navegador. No necesitas instalar nada.
Funciona sin internet; solo el buscador necesita conexión.
"""

ABRIR = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Manual de usuario - App Ron Santa Teresa</title>
<meta http-equiv="refresh" content="0; url=index.html">
<style>body{font-family:"Segoe UI",system-ui,sans-serif;background:#F7F4EE;color:#163340;
text-align:center;padding:80px 20px}a{color:#24546A}</style></head>
<body><h1>Manual de usuario</h1>
<p>Abriendo el manual…</p>
<p>Si no se abre solo, toca aquí: <a href="index.html">Abrir el manual</a></p>
</body></html>
"""

LEEME_TECNICO = """MANUAL DE USUARIO - APP RON SANTA TERESA
Notas para el equipo que lo publica

QUÉ ES
Un sitio estático generado con MkDocs Material. No tiene backend, ni base de
datos, ni proceso que deba quedar corriendo.

CÓMO PUBLICARLO
Copia el contenido de esta carpeta en la raíz que sirva el servidor web.
El punto de entrada es index.html. No requiere configuración especial:
sirve cualquier servidor de archivos estáticos, por ejemplo Nginx, Apache,
IIS, S3 o Netlify.

DETALLES ÚTILES
- Las rutas son relativas, así que el manual funciona en la raíz del dominio
  o dentro de un subdirectorio, por ejemplo /manual/.
- El buscador es del lado del cliente: usa search/search_index.json.
- print_page.html es la versión de una sola página, pensada para imprimir
  o generar el PDF.
- El contenido es público para quien tenga el enlace. Si debe ser interno,
  protégelo con la autenticación del servidor.
- Para actualizarlo, se reemplaza la carpeta completa con una versión nueva.

ACTUALIZACIONES
El manual se edita en otro proyecto y se vuelve a generar allí. Quien lo
mantiene envía un archivo .zip nuevo como este.
"""

def construir_para_servidor(destino):
    """Genera el manual sin el complemento 'offline', usando una copia de mkdocs.yml."""
    config = open(os.path.join(RAIZ, "mkdocs.yml"), encoding="utf-8").read()
    config = re.sub(r"^\s*-\s*offline\s*$", "", config, flags=re.M)
    temporal = os.path.join(RAIZ, "mkdocs-servidor.yml")
    open(temporal, "w", encoding="utf-8", newline="\n").write(config)
    try:
        r = subprocess.run([sys.executable, "-m", "mkdocs", "build", "-q", "-f", temporal, "-d", destino],
                           cwd=RAIZ, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit("No se pudo generar el manual:\n" + (r.stderr or r.stdout))
    finally:
        os.remove(temporal)


def empaquetar(sufijo, preparar_carpeta):
    """Arma un .zip en CARPETA_USO con la carpeta del manual adentro."""
    destino = os.path.join(CARPETA_USO, f"{NOMBRE} - {sufijo}")
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, NOMBRE)
        preparar_carpeta(base)
        if os.path.exists(destino + ".zip"):
            os.remove(destino + ".zip")
        shutil.make_archive(destino, "zip", tmp)
    mb = round(os.path.getsize(destino + ".zip") / 1024 / 1024, 1)
    print(f"  Listo: {NOMBRE} - {sufijo}.zip  ({mb} MB)")


def para_el_servidor(base):
    construir_para_servidor(base)
    with open(os.path.join(base, "LEEME - para publicarlo en un servidor.txt"), "w", encoding="utf-8") as f:
        f.write(LEEME_TECNICO)


def para_abrir_en_el_computador(base):
    if not os.path.isdir(SITE):
        raise SystemExit("Falta generar el manual antes de enviarlo.")
    shutil.copytree(SITE, base)
    with open(os.path.join(base, "ABRIR EL MANUAL.html"), "w", encoding="utf-8") as f:
        f.write(ABRIR)
    with open(os.path.join(base, "LEEME - como abrir el manual.txt"), "w", encoding="utf-8") as f:
        f.write(LEEME)


print("Preparando los dos archivos para enviar...")
empaquetar("para publicar en el servidor", para_el_servidor)
empaquetar("para abrir en el computador", para_abrir_en_el_computador)
