/**
 * Backend del editor web del manual (Cloudflare Pages Functions). Atiende todo /api/*.
 *
 * Hace lo mismo que herramientas/editor.py, pero en vez de escribir en el disco guarda cada cambio
 * como un commit en GitHub. Las rutas y respuestas son las mismas, así el editor no cambia.
 *
 * Variables del proyecto en Cloudflare:
 *   GITHUB_TOKEN   (secreto) token de grano fino con Contents: lectura y escritura, solo para el repositorio
 *   GITHUB_REPO    p. ej. dnanez01/ziclo-manual-usuario
 *   GITHUB_BRANCH  p. ej. main
 *   CLAVE_EDITOR   (secreto) clave compartida de edición.
 *   ACCESS_TEAM_DOMAIN y ACCESS_AUD (opcionales): solo si se usa Cloudflare Access; entonces además
 *   se exige y verifica la firma de Access (Cf-Access-Jwt-Assertion) como capa extra.
 *
 * Inicio de sesión: cada llamada debe traer
 *   X-Correo-Editor  un correo que termine en @nextepinnovation.com (sin importar mayúsculas)
 *   X-Clave-Editor   igual a CLAVE_EDITOR, comparada en tiempo constante.
 * Si algo falla: 401 con un mensaje claro, después de una pausa de 1 segundo (frena los intentos al azar).
 *
 * El token de GitHub solo vive aquí, en el servidor; nunca se envía al navegador.
 */

const PROTEGIDAS = new Set(["index.md"]);
const MAX_IMAGEN = 10 * 1024 * 1024;
const PAPELERA = "herramientas/papelera";
const ZONA = "America/Caracas";
const RX_CORREO = /^[a-z0-9._%+-]+@nextepinnovation\.com$/i;
const PAUSA_FALLO = 1000;
const TIPOS = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", svg: "image/svg+xml", woff2: "font/woff2" };
const CONFLICTO = "Esta página cambió mientras la editabas, quizás otra persona la guardó. " +
  "Copia tu texto, vuelve a abrir la página y aplica tus cambios de nuevo.";

class ErrorUsuario extends Error {
  constructor(msg, codigo = 400, extra = {}) { super(msg); this.codigo = codigo; this.extra = extra; }
}
const conflicto = (msg = CONFLICTO) => new ErrorUsuario(msg, 409, { conflicto: true });

const json = (datos, codigo = 200) => new Response(JSON.stringify(datos), {
  status: codigo, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
});

/* ---------------- Texto <-> base64 (UTF-8) ---------------- */
function aBase64(texto) {
  const bytes = new TextEncoder().encode(texto);
  let s = "";
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(s);
}
function deBase64(b64) {
  const bin = atob(b64.replace(/\s/g, ""));
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder().decode(bytes);
}
const b64url = s => atob(s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4));

/* ---------------- Rutas seguras ---------------- */
function normalizar(rel) {
  const partes = [];
  for (const p of String(rel || "").replace(/\\/g, "/").split("/")) {
    if (!p || p === ".") continue;
    if (p === "..") { if (!partes.length) return null; partes.pop(); } else partes.push(p);
  }
  return partes.join("/");
}
/** Ruta dentro de docs/ (sin el prefijo). Cualquier intento de salir de ahí se rechaza. */
function rutaSegura(rel) {
  const r = normalizar(rel);
  if (!r || r.split("/")[0] === "editar") throw new ErrorUsuario("Esa ruta no pertenece al manual.");
  return r;
}
function rutaPagina(rel) {
  const r = rutaSegura(rel);
  if (!r.endsWith(".md")) throw new ErrorUsuario("Esa ruta no es una página del manual.");
  return r;
}
function relativa(desdeDir, hasta) {
  const a = desdeDir ? desdeDir.split("/") : [], b = hasta.split("/");
  let i = 0;
  while (i < a.length && i < b.length - 1 && a[i] === b[i]) i++;
  return [...Array(a.length - i).fill(".."), ...b.slice(i)].join("/");
}
const dirDe = r => r.includes("/") ? r.slice(0, r.lastIndexOf("/")) : "";

function normal(x) { return x.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
function nombreArchivo(nombre) { return normal(nombre).replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 50).replace(/-+$/, ""); }
function tituloDe(texto, rel) {
  const m = texto.match(/^# (.+)$/m);
  return m ? m[1].trim() : rel.split("/").pop().replace(/\.md$/, "");
}
function marcaTiempo(d = new Date()) {
  const p = Object.fromEntries(new Intl.DateTimeFormat("en-GB", {
    timeZone: ZONA, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23",
  }).formatToParts(d).map(x => [x.type, x.value]));
  return `${p.year}${p.month}${p.day}-${p.hour}${p.minute}${p.second}`;
}

/* ---------------- Inicio de sesión (Cloudflare Access) ---------------- */
let certs = null;
async function verificarJWT(req, env, correo) {
  if (!env.ACCESS_TEAM_DOMAIN || !env.ACCESS_AUD) return true;   // solo la revisión del encabezado
  try {
    const token = req.headers.get("Cf-Access-Jwt-Assertion") || "";
    const [h, p, firma] = token.split(".");
    const cab = JSON.parse(b64url(h)), datos = JSON.parse(b64url(p));
    const aud = [].concat(datos.aud || []);
    if (!aud.includes(env.ACCESS_AUD) || datos.exp * 1000 < Date.now()) return false;
    if (datos.email && datos.email.toLowerCase() !== correo.toLowerCase()) return false;
    const dominio = env.ACCESS_TEAM_DOMAIN.replace(/^https?:\/\//, "").replace(/\/+$/, "");
    if (!certs || !certs.some(k => k.kid === cab.kid)) {
      certs = (await (await fetch(`https://${dominio}/cdn-cgi/access/certs`)).json()).keys || [];
    }
    const jwk = certs.find(k => k.kid === cab.kid);
    if (!jwk) return false;
    const llave = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
    const sig = Uint8Array.from(b64url(firma), c => c.charCodeAt(0));
    return await crypto.subtle.verify("RSASSA-PKCS1-v1_5", llave, sig, new TextEncoder().encode(`${h}.${p}`));
  } catch (e) {
    return false;
  }
}

/* ---------------- Clave compartida de edición ---------------- */
/** Compara en tiempo constante: se comparan los resúmenes SHA-256 (mismo largo) byte por byte, sin salir antes. */
async function igualSeguro(a, b) {
  const enc = new TextEncoder();
  const [x, y] = (await Promise.all([a, b].map(s => crypto.subtle.digest("SHA-256", enc.encode(s))))).map(h => new Uint8Array(h));
  let dif = 0;
  for (let i = 0; i < x.length; i++) dif |= x[i] ^ y[i];
  return dif === 0;
}

/* ---------------- GitHub ---------------- */
function github(env) {
  const base = `https://api.github.com/repos/${env.GITHUB_REPO}`, rama = env.GITHUB_BRANCH || "main";
  async function gh(metodo, ruta, cuerpo, aceptar) {
    const r = await fetch(base + ruta, {
      method: metodo,
      headers: {
        Authorization: `Bearer ${env.GITHUB_TOKEN}`, "User-Agent": "editor-manual-santa-teresa",
        Accept: aceptar || "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
        ...(cuerpo ? { "Content-Type": "application/json" } : {}),
      },
      body: cuerpo ? JSON.stringify(cuerpo) : undefined,
    });
    return r;
  }
  async function ghJson(metodo, ruta, cuerpo) {
    const r = await gh(metodo, ruta, cuerpo);
    const j = await r.json().catch(() => ({}));
    if (!r.ok) {
      const e = new Error(`GitHub ${r.status}: ${j.message || ""}`); e.status = r.status; throw e;
    }
    return j;
  }
  const enc = p => p.split("/").map(encodeURIComponent).join("/");

  /** Archivo del repositorio: { texto, sha } o null si no existe. */
  async function leer(ruta, ref = rama) {
    const r = await gh("GET", `/contents/${enc(ruta)}?ref=${encodeURIComponent(ref)}`);
    if (r.status === 404) return null;
    const j = await r.json();
    if (!r.ok) throw new Error(`GitHub ${r.status}: ${j.message || ""}`);
    if (Array.isArray(j)) return null;
    let texto;
    if (j.content || j.size === 0) texto = deBase64(j.content || "");
    else texto = deBase64((await ghJson("GET", `/git/blobs/${j.sha}`)).content);   // archivos de más de 1 MB
    return { texto, sha: j.sha };
  }
  async function leerBinario(ruta) {
    const r = await gh("GET", `/contents/${enc(ruta)}?ref=${encodeURIComponent(rama)}`, null, "application/vnd.github.raw");
    return r.ok ? r : null;
  }
  async function listarCarpeta(ruta) {
    const r = await gh("GET", `/contents/${enc(ruta)}?ref=${encodeURIComponent(rama)}`);
    if (r.status === 404) return [];
    const j = await r.json();
    return Array.isArray(j) ? j : [];
  }
  /** Guarda un archivo con un commit. 'sha' es la versión que se leyó: si alguien guardó otra cosa
   *  entretanto, GitHub lo rechaza y avisamos del conflicto en vez de pisar el cambio ajeno. */
  async function escribir(ruta, contenidoB64, sha, mensaje, correo) {
    const r = await gh("PUT", `/contents/${enc(ruta)}`, {
      message: mensaje, content: contenidoB64, branch: rama, ...(sha ? { sha } : {}),
      author: { name: correo, email: correo },
    });
    if (r.status === 409 || r.status === 422) {
      const j = await r.json().catch(() => ({}));
      if (r.status === 409 || /sha/i.test(j.message || "")) throw conflicto();
      throw new Error(`GitHub ${r.status}: ${j.message || ""}`);
    }
    if (!r.ok) throw new Error(`GitHub ${r.status}: ${(await r.json().catch(() => ({}))).message || ""}`);
    return (await r.json()).commit;
  }
  async function cabeza() {
    return (await ghJson("GET", `/git/ref/heads/${encodeURIComponent(rama)}`)).object.sha;
  }
  /** Varios cambios en un solo commit. Si la rama avanzó mientras tanto, no se fuerza: conflicto. */
  async function commitVarios(base, cambios, mensaje, correo) {
    const commitBase = await ghJson("GET", `/git/commits/${base}`);
    const arbol = await ghJson("POST", "/git/trees", {
      base_tree: commitBase.tree.sha,
      tree: cambios.map(c => c.borrar ? { path: c.ruta, mode: "100644", type: "blob", sha: null }
        : { path: c.ruta, mode: "100644", type: "blob", content: c.texto }),
    });
    const nuevo = await ghJson("POST", "/git/commits", {
      message: mensaje, tree: arbol.sha, parents: [base], author: { name: correo, email: correo, date: new Date().toISOString() },
    });
    const r = await gh("PATCH", `/git/refs/heads/${encodeURIComponent(rama)}`, { sha: nuevo.sha, force: false });
    if (r.status === 422 || r.status === 409) throw conflicto("Otra persona guardó un cambio al mismo tiempo. Inténtalo de nuevo.");
    if (!r.ok) throw new Error(`GitHub ${r.status}`);
    return nuevo.sha;
  }
  async function arbol() {
    return (await ghJson("GET", `/git/trees/${encodeURIComponent(rama)}?recursive=1`)).tree;
  }
  async function blob(sha) { return deBase64((await ghJson("GET", `/git/blobs/${sha}`)).content); }
  async function commits(ruta, n = 30) {
    return ghJson("GET", `/commits?sha=${encodeURIComponent(rama)}&path=${encodeURIComponent(ruta)}&per_page=${n}`);
  }
  return { leer, leerBinario, listarCarpeta, escribir, cabeza, commitVarios, arbol, blob, commits };
}

/* ---------------- Menú (nav de mkdocs.yml) ---------------- */
const escaparRx = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const rutasEnMenu = yml => [...yml.matchAll(/:\s*([\w/.-]+\.md)\s*$/gm)].map(m => m[1]);
function agregarAlMenu(yml, rel, nombre) {
  if (new RegExp(":\\s*" + escaparRx(rel) + "\\s*$", "m").test(yml)) return yml;
  const linea = `      - ${JSON.stringify(nombre)}: ${rel}`;
  if (!yml.includes("  - Glosario: glosario.md"))
    throw new ErrorUsuario("No encontré dónde agregar la página en el menú. Pide ayuda técnica.");
  return yml.replace("  - Glosario: glosario.md", linea + "\n  - Glosario: glosario.md");
}
const quitarDelMenu = (yml, rel) => yml.replace(new RegExp("^[ \\t]*- [^\\n]*:\\s*" + escaparRx(rel) + "[ \\t]*\\n", "gm"), "");
/** Estructura del menú: [{ titulo, ruta }] o [{ titulo, hijos: [...] }]. */
function leerNav(yml) {
  const m = yml.match(/^nav:\s*\n((?:[ \t]+.*\n|\s*\n)*)/m);
  const raiz = [], pila = [{ sangria: -1, hijos: raiz }];
  for (const linea of (m ? m[1] : "").split("\n")) {
    const x = linea.match(/^(\s*)- (.+?):\s*(\S.*)?$/);
    if (!x) continue;
    const sangria = x[1].length, titulo = x[2].replace(/^"(.*)"$/, "$1").replace(/^'(.*)'$/, "$1");
    while (pila.length > 1 && pila[pila.length - 1].sangria >= sangria) pila.pop();
    const item = x[3] ? { titulo, ruta: x[3].trim() } : { titulo, hijos: [] };
    pila[pila.length - 1].hijos.push(item);
    if (item.hijos) pila.push({ sangria, hijos: item.hijos });
  }
  return raiz;
}

/* ---------------- Páginas ---------------- */
async function todasLasPaginas(g, conTexto) {
  const arbol = await g.arbol();
  const md = arbol.filter(e => e.type === "blob" && e.path.startsWith("docs/") && e.path.endsWith(".md") && !e.path.startsWith("docs/editar/"));
  const ymlE = arbol.find(e => e.path === "mkdocs.yml");
  const [yml, ...textos] = await Promise.all([ymlE ? g.blob(ymlE.sha) : "", ...md.map(e => g.blob(e.sha))]);
  const nav = rutasEnMenu(yml);
  const paginas = md.map((e, i) => {
    const ruta = e.path.slice(5);
    return { ruta, titulo: tituloDe(textos[i], ruta), protegida: PROTEGIDAS.has(ruta), ...(conTexto ? { texto: textos[i] } : {}) };
  });
  const orden = r => nav.includes(r) ? nav.indexOf(r) : nav.length;
  paginas.sort((a, b) => orden(a.ruta) - orden(b.ruta) || a.ruta.localeCompare(b.ruta));
  const carpetas = arbol.filter(e => e.type === "tree" && /^docs\/imagenes\/[^/]+$/.test(e.path)).map(e => e.path.slice(14)).sort();
  return { paginas, carpetas, yml };
}

function textoLimpio(linea) {
  let t = linea.replace(/!\[([^\]]*)\]\([^)]*\)(\{[^}]*\})?/g, "Imagen: $1");
  t = t.replace(/\[([^\]]+)\]\([^)]*\)/g, "$1");
  t = t.replace(/^\s*(#+|\d+\.|[-*]|!!!\s*\w+|\?\?\?\s*\w+)\s*/, "");
  t = t.replaceAll("**", "").replaceAll("|", " ").replaceAll('"', "").replaceAll("\\", "");
  return t.replace(/\s+/g, " ").trim();
}

const PLANTILLA = n => `# ${n}\n\n**Para qué sirve:** escribe aquí para qué sirve esta pantalla.\n\n## Las partes de la pantalla\n\n## Cómo se hace\n\n1. Primer paso.\n`;
const RX_PAPELERA = /^(\d{8})-(\d{6})__(.+\.md)$/;
const esSha = s => /^[0-9a-f]{40}$/.test(s || "");

/* ---------------- Rutas ---------------- */
async function atender(req, env) {
  const falla = async (error, codigo = 401) => { await new Promise(r => setTimeout(r, PAUSA_FALLO)); return json({ error, sesion: true }, codigo); };
  const correo = (req.headers.get("X-Correo-Editor") || "").trim().toLowerCase();
  if (!env.CLAVE_EDITOR) return json({ error: "El editor web no está configurado (falta CLAVE_EDITOR)." }, 500);
  const claveOk = await igualSeguro(req.headers.get("X-Clave-Editor") || "", env.CLAVE_EDITOR);
  if (!RX_CORREO.test(correo)) return falla("Usa tu correo corporativo");
  if (!claveOk) return falla("Clave incorrecta");
  if (!(await verificarJWT(req, env, correo))) return falla("Tu sesión no es válida. Vuelve a iniciar sesión.");
  if (!env.GITHUB_TOKEN || !env.GITHUB_REPO) return json({ error: "El editor web no está configurado (faltan GITHUB_TOKEN o GITHUB_REPO)." }, 500);

  const url = new URL(req.url), q = url.searchParams;
  const ruta = url.pathname.replace(/^\/api\/?/, "").replace(/\/+$/, "");
  const g = github(env);
  const msg = `Edición de ${correo} desde la web`;

  if (req.method === "GET") {
    switch (ruta) {
      case "yo": case "sesion": return json({ ok: true, correo });
      case "paginas": {
        const { paginas, carpetas, yml } = await todasLasPaginas(g, false);
        return json({ paginas, carpetas, nav: leerNav(yml) });
      }
      case "pagina": {
        const f = await g.leer("docs/" + rutaPagina(q.get("ruta")));
        if (!f) throw new ErrorUsuario("No se encontró el archivo.", 404);
        return json({ contenido: f.texto, sha: f.sha });
      }
      case "archivo": {      // imágenes de la página, recién subidas aunque el manual aún no se haya publicado
        const r = rutaSegura(q.get("ruta")), ext = r.split(".").pop().toLowerCase();
        if (!TIPOS[ext]) throw new ErrorUsuario("No se encontró el archivo.", 404);
        const res = await g.leerBinario("docs/" + r);
        if (!res) throw new ErrorUsuario("No se encontró el archivo.", 404);
        return new Response(res.body, { headers: { "Content-Type": TIPOS[ext], "Cache-Control": "private, max-age=60" } });
      }
      case "buscar": {
        const c = normal((q.get("q") || "").trim()), resultados = [];
        if (c.length >= 2) {
          for (const p of (await todasLasPaginas(g, true)).paginas) {
            p.texto.split("\n").forEach((linea, i) => {
              const limpio = textoLimpio(linea);
              if (limpio && normal(limpio).includes(c)) resultados.push({ ruta: p.ruta, titulo: p.titulo, linea: i + 1, texto: limpio.slice(0, 160) });
            });
          }
        }
        return json({ resultados: resultados.slice(0, 80) });
      }
      case "enlaces": {
        const destino = rutaPagina(q.get("ruta")), quienes = [];
        for (const p of (await todasLasPaginas(g, true)).paginas) {
          if (p.ruta === destino) continue;
          for (const m of p.texto.matchAll(/\]\(([^)#\s]+\.md)/g)) {
            if (normalizar(dirDe(p.ruta) + "/" + m[1]) === destino) { quienes.push(p.titulo); break; }
          }
        }
        return json({ paginas: quienes });
      }
      case "papelera": {
        const archivos = (await g.listarCarpeta(PAPELERA)).filter(e => e.type === "file" && RX_PAPELERA.test(e.name))
          .sort((a, b) => b.name.localeCompare(a.name)).slice(0, 30);
        const items = await Promise.all(archivos.map(async e => {
          const [, d, h, r] = e.name.match(RX_PAPELERA), rel = r.replaceAll("__", "/");
          const f = await g.leer(`${PAPELERA}/${e.name}`);
          return { archivo: e.name, ruta: rel, titulo: tituloDe(f ? f.texto : "", rel),
            fecha: `${d.slice(6, 8)}/${d.slice(4, 6)}/${d.slice(0, 4)} ${h.slice(0, 2)}:${h.slice(2, 4)}` };
        }));
        return json({ items });
      }
      case "versiones": {
        const rel = rutaPagina(q.get("ruta"));
        const lista = await g.commits("docs/" + rel);
        if (!lista.length) throw new ErrorUsuario("La página ya no existe.");
        return json({ versiones: lista.map((c, i) => ({
          archivo: i === 0 ? null : c.sha, actual: i === 0, fecha: c.commit.author.date,
          autor: c.commit.author.name, mensaje: c.commit.message.split("\n")[0],
        })) });
      }
      case "version": {
        const rel = rutaPagina(q.get("ruta")), sha = q.get("archivo");
        if (!esSha(sha)) throw new ErrorUsuario("Esa versión no pertenece a esta página.");
        const f = await g.leer("docs/" + rel, sha);
        if (!f) throw new ErrorUsuario("Esa versión ya no existe.");
        return json({ contenido: f.texto });
      }
    }
    return json({ error: "No existe" }, 404);
  }

  if (req.method !== "POST") return json({ error: "Método no permitido" }, 405);
  let d;
  try { d = await req.json(); } catch (e) { throw new ErrorUsuario("La solicitud no es válida."); }

  switch (ruta) {
    case "guardar": {
      const rel = rutaPagina(d.ruta), f = await g.leer("docs/" + rel);
      if (!f) throw new ErrorUsuario("Esta página ya no existe. Puede que la hayan eliminado.");
      if (typeof d.contenido !== "string" || !/^# \S/m.test(d.contenido)) throw new ErrorUsuario("La página necesita su título principal. No se guardó.");
      if ("base" in d && d.base !== f.texto) throw conflicto();
      if (d.sha && d.sha !== f.sha) throw conflicto();
      if (d.contenido === f.texto) return json({ ok: true, sinCambios: true });
      const c = await g.escribir("docs/" + rel, aBase64(d.contenido), f.sha, msg, correo);
      return json({ ok: true, commit: c && c.sha });
    }
    case "restaurar": {
      const rel = rutaPagina(d.ruta), f = await g.leer("docs/" + rel);
      if (!f) throw new ErrorUsuario("Esta página ya no existe. Puede que la hayan eliminado.");
      if (!esSha(d.archivo)) throw new ErrorUsuario("Esa versión no pertenece a esta página.");
      const v = await g.leer("docs/" + rel, d.archivo);
      if (!v) throw new ErrorUsuario("Esa versión ya no existe.");
      if ("base" in d && d.base !== f.texto) throw conflicto("Esta página cambió mientras la tenías abierta, quizás otra persona la guardó. Vuelve a abrirla e inténtalo de nuevo.");
      const [ultimo] = await g.commits("docs/" + rel, 1);           // la versión actual queda en el historial
      await g.escribir("docs/" + rel, aBase64(v.texto), f.sha, `${msg} (restaura una versión anterior)`, correo);
      return json({ ok: true, respaldo: ultimo ? ultimo.sha : null, contenido: v.texto });
    }
    case "imagen": {
      const paginaDir = dirDe(rutaPagina(d.pagina));
      const carpeta = String(d.carpeta || "").toLowerCase().replace(/[^a-z0-9-]/g, "") || "varias";
      const nom = String(d.nombre || ""), punto = nom.lastIndexOf(".");
      const nombre = nombreArchivo(punto > 0 ? nom.slice(0, punto) : nom) || "captura";
      const ext = punto > 0 ? nom.slice(punto).toLowerCase() : ".png";
      if (![".png", ".jpg", ".jpeg"].includes(ext)) throw new ErrorUsuario("Solo se aceptan imágenes PNG o JPG.");
      const b64 = String(d.datos || "").split(",").pop().replace(/\s/g, "");
      if (b64.length * 3 / 4 > MAX_IMAGEN + 3) throw new ErrorUsuario("La imagen pesa más de 10 MB.");
      let inicio;
      try { inicio = atob(b64.slice(0, 12)); } catch (e) { inicio = ""; }
      if (!(inicio.startsWith("\x89PNG\r\n\x1a\n") || inicio.startsWith("\xff\xd8\xff"))) throw new ErrorUsuario("El archivo no es una imagen PNG o JPG válida.");
      const destino = `imagenes/${carpeta}/${nombre}${ext}`;
      const existente = (await g.listarCarpeta(`docs/imagenes/${carpeta}`)).find(e => e.name === `${nombre}${ext}`);
      if (existente && !d.reemplazar) throw new ErrorUsuario(`Ya existe una imagen llamada ${nombre}${ext}.`);
      await g.escribir("docs/" + destino, b64, existente && existente.sha, `${msg} (imagen ${destino})`, correo);
      return json({ ruta: relativa(paginaDir, destino) });
    }
    case "nueva": {
      const nombre = String(d.nombre || "").replace(/\s+/g, " ").trim().replace(/^#+/, "").trim().slice(0, 60);
      const archivo = nombreArchivo(nombre);
      if (!archivo) throw new ErrorUsuario("Escribe un nombre para la página, con letras o números.");
      const rel = `modulos/${archivo}.md`, base = await g.cabeza();
      if (await g.leer("docs/" + rel, base)) throw new ErrorUsuario("Ya existe una página con ese nombre.");
      const yml = (await g.leer("mkdocs.yml", base)).texto;
      await g.commitVarios(base, [
        { ruta: "docs/" + rel, texto: PLANTILLA(nombre) },
        { ruta: "mkdocs.yml", texto: agregarAlMenu(yml, rel, nombre) },
      ], `${msg} (nueva página ${rel})`, correo);
      return json({ ruta: rel });
    }
    case "eliminar": {
      const rel = rutaPagina(d.ruta);
      if (PROTEGIDAS.has(rel)) throw new ErrorUsuario("Esta página no se puede eliminar.");
      const base = await g.cabeza(), f = await g.leer("docs/" + rel, base);
      if (!f) throw new ErrorUsuario("La página ya no existe.");
      const yml = (await g.leer("mkdocs.yml", base)).texto;
      const archivo = `${marcaTiempo()}__${rel.replaceAll("/", "__")}`;
      await g.commitVarios(base, [
        { ruta: `${PAPELERA}/${archivo}`, texto: f.texto },
        { ruta: "docs/" + rel, borrar: true },
        { ruta: "mkdocs.yml", texto: quitarDelMenu(yml, rel) },
      ], `${msg} (a la papelera ${rel})`, correo);
      return json({ ok: true, archivo });
    }
    case "recuperar": {
      const archivo = String(d.archivo || ""), m = archivo.match(RX_PAPELERA);
      if (!m || /[\\/]|\.\./.test(archivo)) throw new ErrorUsuario("Archivo no válido.");
      const rel = rutaPagina(m[3].replaceAll("__", "/")), base = await g.cabeza();
      const f = await g.leer(`${PAPELERA}/${archivo}`, base);
      if (!f) throw new ErrorUsuario("Esa página ya no está en la papelera.");
      if (await g.leer("docs/" + rel, base)) throw new ErrorUsuario("Ya existe una página con ese nombre. Cámbiale el nombre a la actual antes de recuperar esta.");
      const yml = (await g.leer("mkdocs.yml", base)).texto;
      await g.commitVarios(base, [
        { ruta: "docs/" + rel, texto: f.texto },
        { ruta: `${PAPELERA}/${archivo}`, borrar: true },
        { ruta: "mkdocs.yml", texto: agregarAlMenu(yml, rel, tituloDe(f.texto, rel)) },
      ], `${msg} (recupera ${rel})`, correo);
      return json({ ruta: rel });
    }
  }
  return json({ error: "No existe" }, 404);
}

export async function onRequest(context) {
  try {
    return await atender(context.request, context.env);
  } catch (e) {
    if (e instanceof ErrorUsuario) return json({ error: e.message, ...e.extra }, e.codigo);
    return json({ error: "Ocurrió un error inesperado: " + e.message }, 500);
  }
}
