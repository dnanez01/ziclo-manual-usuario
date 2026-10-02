"""Convierte instrucciones-windows.md e instrucciones-mac.md en "Instrucciones.html", una en cada carpeta
de "USAR EL MANUAL" (Windows y Mac). Cada página se abre con doble clic y lleva la letra Montserrat
adentro, así que se ve igual sin internet.
Uso: python sistema/herramientas/generar_instrucciones.py   (después de cambiar cualquiera de los dos .md)"""
import base64, os
import markdown   # viene instalado con MkDocs

AQUI = os.path.dirname(os.path.abspath(__file__))
USAR = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "USAR EL MANUAL")
FUENTES = os.path.join(os.path.dirname(AQUI), "docs", "estilos", "fuentes")


def fuente(nombre):
    return base64.b64encode(open(os.path.join(FUENTES, nombre), "rb").read()).decode("ascii")


ESTILO = """
  @font-face { font-family:"Montserrat"; font-style:normal; font-weight:100 900; src:url(data:font/woff2;base64,__NORMAL__) format("woff2"); }
  :root { --marino:#163340; --azul:#24546A; --bronce:#9A6E2A; --crema:#F7F4EE; --linea:#E6E0D5; --texto:#1F2D35; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:"Montserrat", system-ui, sans-serif; background:var(--crema); color:var(--texto); -webkit-font-smoothing:antialiased; }
  main { max-width:860px; margin:32px auto 64px; padding:44px 52px 52px; background:#fff; border-radius:22px; box-shadow:0 1px 2px rgba(22,51,64,.05), 0 8px 28px rgba(22,51,64,.07); }
  h1 { color:var(--marino); font-size:30px; line-height:1.25; margin:0 0 18px; padding-bottom:16px; border-bottom:3px solid var(--bronce); }
  h2 { color:var(--marino); font-size:22px; margin:44px 0 12px; padding-top:22px; border-top:1px solid var(--linea); }
  h3 { color:var(--azul); font-size:17px; margin:28px 0 10px; }
  p, li { font-size:16px; line-height:1.75; }
  li { margin:4px 0; }
  ol li::marker { color:var(--azul); font-weight:700; }
  strong { color:var(--marino); }
  code { background:#F1ECE2; padding:2px 7px; border-radius:6px; font-size:14px; }
  table { border-collapse:separate; border-spacing:0; width:100%; margin:16px 0; border:1px solid var(--linea); border-radius:14px; overflow:hidden; }
  th { background:var(--azul); color:#fff; text-align:left; padding:12px 14px; font-size:14px; font-weight:600; }
  td { padding:12px 14px; font-size:15px; line-height:1.6; vertical-align:top; border-top:1px solid #F0ECE5; }
  tr:nth-child(even) td { background:#FCFBF9; }
  @media (max-width:700px) { main { margin:0; border-radius:0; padding:28px 16px; } td, th { padding:10px; overflow-wrap:anywhere; } }
"""


def generar(origen, carpeta):
    cuerpo = markdown.markdown(open(os.path.join(AQUI, origen), encoding="utf-8").read(), extensions=["tables"])
    titulo = "Cómo usar el manual en " + carpeta
    html = (f'<!DOCTYPE html>\n<html lang="es"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{titulo}</title>\n'
            f'<style>{ESTILO.replace("__NORMAL__", fuente("montserrat-latin-wght-normal.woff2"))}</style></head>\n'
            f'<body><main>\n{cuerpo}\n</main></body></html>\n')
    destino = os.path.join(USAR, carpeta, "Instrucciones.html")
    open(destino, "w", encoding="utf-8").write(html)
    print("Listo:", destino)


generar("instrucciones-windows.md", "Windows")
generar("instrucciones-mac.md", "Mac")
