"""Genera las imágenes del manual a partir de las capturas en raw/.
partes(): recuadros rojos con número en una franja izquierda (o en la esquina).
paso():   solo recuadros rojos, para indicar qué tocar.
plano():  solo recorte."""
import os
from PIL import Image, ImageDraw, ImageFont
ROJO = "#E53935"; GUT = 150
F = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 66)
BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw")
DEST = os.path.join(os.path.dirname(BASE), "docs", "imagenes") + os.sep   # sistema/docs/imagenes/

def _abrir(src):
    p = src if os.path.isabs(src) else os.path.join(RAW, src)
    return Image.open(p).convert("RGB")

def _guardar(im, out):
    os.makedirs(os.path.dirname(DEST + out), exist_ok=True)
    im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
    im.save(DEST + out, optimize=True)
    print(out, im.size)

def partes(src, out, crop, marcas):
    im = _abrir(src).crop(crop)
    W, H = im.size
    can = Image.new("RGB", (W + GUT, H), "#FFFFFF"); can.paste(im, (GUT, 0)); d = ImageDraw.Draw(can)
    for m in marcas:
        n, (x0, y0, x1, y1) = m[0], m[1]; esquina = len(m) > 2
        x0 += GUT - crop[0]; x1 += GUT - crop[0]; y0 -= crop[1]; y1 -= crop[1]
        d.rounded_rectangle([x0, y0, x1, y1], 26, outline=ROJO, width=9)
        if esquina:
            cx, cy, r = x1 - 8, max(y0 + 8, 54), 50
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ROJO, outline="white", width=7)
        else:
            cx, cy, r = GUT // 2, max(y0 + 48, 54), 50
            d.line([(cx + r, cy), (x0, cy)], fill=ROJO, width=9)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ROJO)
        t = str(n); w = d.textlength(t, font=F); d.text((cx - w / 2, cy - 47), t, font=F, fill="white")
    _guardar(can, out)

def paso(src, out, crop, cajas=()):
    im = _abrir(src); d = ImageDraw.Draw(im)
    for c in cajas: d.rounded_rectangle(c, 26, outline=ROJO, width=10)
    _guardar(im.crop(crop), out)

def plano(src, out, crop):
    _guardar(_abrir(src).crop(crop), out)
