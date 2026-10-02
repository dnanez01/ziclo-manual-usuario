"""Recorrido seguro de la app por adb. Uso: python app.py <comando> [args]
Comandos: fg | dump | shot NOMBRE | tap X Y | taptext REGEX [n] | swipe up|down [px] | back
Cada acción verifica antes que la app de ventas esté al frente."""
import subprocess, sys, re, os, time, html
os.environ["MSYS_NO_PATHCONV"] = "1"
APP = "io.ziclo.app.dev"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
os.makedirs(RAW, exist_ok=True)

def adb(*a, binary=False):
    r = subprocess.run(["adb", *a], capture_output=True)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")

def fg():
    out = adb("shell", "dumpsys", "activity", "activities")
    m = re.search(r"topResumedActivity=.*", out)
    return m.group(0) if m else ""

def guard():
    f = fg()
    if APP not in f:
        print("ABORTADO: la app al frente no es la de ventas ->", f); sys.exit(1)

def dump(show=True):
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    x = adb("shell", "cat", "/sdcard/ui.xml")
    adb("shell", "rm", "-f", "/sdcard/ui.xml")
    nodes = []
    for m in re.finditer(r"<node ([^>]*?)/?>", x):
        at = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
        t = html.unescape(at.get("text", "")) or html.unescape(at.get("content-desc", ""))
        b = list(map(int, re.findall(r"\d+", at.get("bounds", "0,0,0,0"))))
        nodes.append({"t": t, "b": b, "click": at.get("clickable") == "true",
                      "scroll": at.get("scrollable") == "true", "cls": at.get("class", "").split(".")[-1]})
    if show:
        for n in nodes:
            if n["t"] or n["scroll"]:
                print(("*" if n["click"] else " ") + ("S" if n["scroll"] else " "),
                      repr(n["t"].replace("\n", " | "))[:110], n["b"])
    return nodes

def shot(name):
    png = adb("exec-out", "screencap", "-p", binary=True)
    p = os.path.join(RAW, name + ".png"); open(p, "wb").write(png)
    from PIL import Image
    Image.open(p).resize((360, 812)).save(os.path.join(RAW, name + "_small.png"))
    print("captura:", p)

def tap(x, y):
    guard(); adb("shell", "input", "tap", str(x), str(y)); print("tap", x, y); time.sleep(2)

def taptext(rx, idx=0):
    ns = [n for n in dump(False) if re.search(rx, n["t"], re.I)]
    if len(ns) <= idx: print("NO ENCONTRADO:", rx); sys.exit(1)
    b = ns[idx]["b"]; tap((b[0] + b[2]) // 2, (b[1] + b[3]) // 2)

def swipe(direction, px=900):
    guard()
    y0, y1 = (1700, 1700 - px) if direction == "up" else (700, 700 + px)
    adb("shell", "input", "swipe", "540", str(y0), "540", str(y1), "700"); print("swipe", direction, px); time.sleep(1.5)

def back():
    guard(); adb("shell", "input", "keyevent", "4"); print("back"); time.sleep(2)

if __name__ == "__main__":
    c, a = sys.argv[1], sys.argv[2:]
    if c == "fg": print(fg())
    elif c == "dump": dump()
    elif c == "shot": shot(a[0])
    elif c == "tap": tap(int(a[0]), int(a[1]))
    elif c == "taptext": taptext(a[0], int(a[1]) if len(a) > 1 else 0)
    elif c == "swipe": swipe(a[0], int(a[1]) if len(a) > 1 else 900)
    elif c == "back": back()
