"""CLEAN ROOM: character portraits painted from our own descriptions (facepaint briefs).

FACES: one brief per character, in cell coordinates (0..1, x right, y down).
LAYOUTS: where portraits (and their name captions) sit inside the game's portrait textures.
The frame/background of each texture stays the default rendering (colour grid + alpha outline).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from cleanroom.gfx import facepaint
from games.drmario64.labels import FONT

SKIN = [255, 200, 150]
BLACK = [25, 20, 25]
WHITE = [250, 250, 250]


def eye(cx, cy, r, iris=(60, 110, 220), gaze=(0.0, 0.1), ry=None, lid=0.0, lidc=SKIN):
    return {"eye": {"c": [cx, cy], "r": [r, ry or r * 1.3], "iris": list(iris), "look": list(gaze), "lid": lid,
                    "lidc": list(lidc), "border": 0.25, "borderc": [30, 25, 30]}}


def e(cx, cy, rx, ry, c, rot=0):
    return {"e": [cx, cy, rx, ry], "c": list(c), "rot": rot}


def line(pts, w, c):
    return {"line": pts, "w": w, "c": list(c)}


def poly(pts, c):
    return {"poly": pts, "c": list(c)}


def arc(cx, cy, rx, ry, a0, a1, w, c):
    return {"arc": [cx, cy, rx, ry, a0, a1], "w": w, "c": list(c)}


def mario(skin=SKIN, hair=(90, 50, 20), coat=(245, 245, 245), iris=(40, 90, 220), bg=(120, 220, 170), metal=False):
    ops = [
        e(0.5, 1.02, 0.55, 0.30, coat),                      # coat shoulders
        line([[0.30, 0.78], [0.42, 0.95]], 0.05, (70, 70, 80)),   # stethoscope
        e(0.50, 0.55, 0.30, 0.33, skin),                     # face
        e(0.22, 0.55, 0.07, 0.10, skin),                     # ear
        e(0.50, 0.26, 0.33, 0.12, hair),                     # hair
        {"rect": [0.18, 0.20, 0.82, 0.30], "c": list(coat)},  # head band
        e(0.50, 0.17, 0.10, 0.08, (200, 205, 215)),          # head mirror
        e(0.50, 0.17, 0.05, 0.04, (240, 240, 250)),
        eye(0.42, 0.44, 0.07, iris), eye(0.62, 0.44, 0.07, iris),
        e(0.55, 0.60, 0.11, 0.09, [min(255, c + 15) for c in skin]),   # nose
        poly([[0.28, 0.72], [0.50, 0.64], [0.74, 0.72], [0.62, 0.78], [0.50, 0.72], [0.38, 0.78]], hair),  # moustache
        arc(0.52, 0.80, 0.08, 0.04, 20, 160, 0.03, (150, 40, 40)),
    ]
    return {"base": list(bg), "ops": ops, "detail": 0.03}


def wario(skin=SKIN, cap=(255, 215, 40), bg=(250, 150, 70), overall=(120, 50, 150), face_tint=None):
    sk = face_tint or skin
    ops = [
        e(0.5, 1.02, 0.60, 0.28, overall),
        e(0.50, 0.58, 0.36, 0.33, sk),
        e(0.50, 0.25, 0.40, 0.17, cap),
        {"rect": [0.12, 0.30, 0.88, 0.36], "c": list(cap)},
        e(0.50, 0.21, 0.09, 0.08, WHITE),
        line([[0.44, 0.18], [0.47, 0.25], [0.50, 0.19], [0.53, 0.25], [0.56, 0.18]], 0.025, (80, 60, 200)),  # W
        eye(0.39, 0.45, 0.07, (60, 60, 220), lid=0.3), eye(0.61, 0.45, 0.07, (60, 60, 220), lid=0.3),
        line([[0.30, 0.37], [0.46, 0.42]], 0.04, (90, 50, 20)), line([[0.54, 0.42], [0.70, 0.37]], 0.04, (90, 50, 20)),
        e(0.50, 0.60, 0.13, 0.11, (240, 120, 170)),          # nose
        poly([[0.20, 0.72], [0.35, 0.66], [0.50, 0.70], [0.65, 0.66], [0.80, 0.72], [0.66, 0.76], [0.50, 0.73], [0.34, 0.76]], BLACK),
        e(0.50, 0.83, 0.20, 0.08, WHITE),                    # teeth grin
        line([[0.32, 0.83], [0.68, 0.83]], 0.02, (120, 120, 120)),
    ]
    return {"base": list(bg), "ops": ops, "detail": 0.03}


FACES = {
    "Dr.Mario": mario(),
    "Metal Mario": mario(skin=(190, 195, 205), hair=(120, 125, 135), coat=(215, 220, 230), iris=(120, 130, 150), bg=(150, 205, 245)),
    "Wario": wario(),
    "Vampire Wario": wario(face_tint=(110, 130, 210), cap=(150, 110, 60), bg=(190, 235, 90), overall=(60, 60, 70)),
    "Spearhead": {"base": [245, 170, 190], "ops": [
        e(0.50, 0.58, 0.44, 0.38, (40, 110, 230)),
        poly([[0.10, 0.40], [0.00, 0.15], [0.25, 0.30]], (40, 110, 230)), poly([[0.90, 0.40], [1.00, 0.15], [0.75, 0.30]], (40, 110, 230)),
        e(0.35, 0.52, 0.14, 0.16, BLACK), e(0.65, 0.52, 0.14, 0.16, BLACK),
        {"hl": [0.31, 0.47, 0.04]}, {"hl": [0.61, 0.47, 0.04]},
        e(0.50, 0.30, 0.20, 0.08, (140, 190, 255)),
        arc(0.50, 0.76, 0.12, 0.05, 10, 170, 0.03, BLACK)]},
    "Webber": {"base": [120, 200, 150], "ops": [
        e(0.50, 0.60, 0.42, 0.36, (120, 75, 40)),
        e(0.50, 0.24, 0.30, 0.10, (230, 220, 180)),           # leaf hat
        eye(0.37, 0.52, 0.12, (30, 30, 30), gaze=(0.1, 0.2)), eye(0.63, 0.52, 0.12, (30, 30, 30), gaze=(-0.1, 0.2)),
        poly([[0.30, 0.78], [0.36, 0.95], [0.42, 0.78]], WHITE), poly([[0.58, 0.78], [0.64, 0.95], [0.70, 0.78]], WHITE),
        line([[0.08, 0.70], [0.00, 0.95]], 0.05, (100, 60, 30)), line([[0.92, 0.70], [1.00, 0.95]], 0.05, (100, 60, 30))]},
    "Silky": {"base": [240, 230, 110], "ops": [
        e(0.50, 0.70, 0.40, 0.38, (60, 200, 110)),
        e(0.33, 0.33, 0.13, 0.15, (60, 200, 110)), e(0.67, 0.33, 0.13, 0.15, (60, 200, 110)),
        eye(0.33, 0.33, 0.09, (30, 30, 30)), eye(0.67, 0.33, 0.09, (30, 30, 30)),
        e(0.52, 0.70, 0.16, 0.12, (200, 40, 60)), e(0.52, 0.76, 0.10, 0.06, (250, 140, 170)),
        e(0.30, 0.62, 0.05, 0.03, (150, 240, 170))]},
    "Appleby": {"base": [70, 180, 240], "ops": [
        e(0.50, 0.50, 0.40, 0.36, (245, 110, 160)),
        eye(0.38, 0.36, 0.10, (30, 30, 30)), eye(0.60, 0.34, 0.10, (30, 30, 30)),
        e(0.40, 0.62, 0.20, 0.07, (250, 150, 60)),              # lips
        e(0.35, 0.90, 0.16, 0.14, (225, 30, 40)), {"hl": [0.30, 0.85, 0.03]},   # apple
        line([[0.35, 0.76], [0.37, 0.70]], 0.03, (90, 60, 20)),
        line([[0.70, 0.75], [0.85, 1.0]], 0.07, (245, 110, 160)), line([[0.58, 0.80], [0.62, 1.0]], 0.07, (245, 110, 160))]},
    "Jellybob": {"base": [250, 170, 90], "ops": [
        e(0.50, 0.45, 0.46, 0.34, (250, 245, 245)),
        e(0.28, 0.38, 0.13, 0.13, (240, 240, 240)), {"ring": [0.28, 0.38, 0.13, 0.13], "w": 0.04, "c": [60, 60, 60]},
        eye(0.66, 0.40, 0.10, (30, 30, 30), gaze=(0.3, 0.0)),
        e(0.50, 0.62, 0.36, 0.08, (245, 150, 170)),
        line([[0.25, 0.75], [0.20, 1.0]], 0.07, (250, 245, 245)), line([[0.45, 0.78], [0.45, 1.0]], 0.07, (250, 245, 245)),
        line([[0.65, 0.78], [0.70, 1.0]], 0.07, (250, 245, 245))]},
    "Octo": {"base": [150, 180, 210], "ops": [
        e(0.15, 0.80, 0.18, 0.25, (60, 130, 200)), e(0.85, 0.80, 0.18, 0.25, (60, 130, 200)),
        e(0.50, 0.50, 0.34, 0.34, (240, 120, 50)),
        eye(0.38, 0.44, 0.08, (40, 40, 40), lid=0.4), eye(0.62, 0.44, 0.08, (40, 40, 40), lid=0.4),
        line([[0.28, 0.34], [0.45, 0.40]], 0.04, BLACK), line([[0.55, 0.40], [0.72, 0.34]], 0.04, BLACK),
        e(0.30, 0.60, 0.07, 0.05, (230, 60, 60)), e(0.70, 0.60, 0.07, 0.05, (230, 60, 60)),
        e(0.50, 0.68, 0.12, 0.08, (200, 30, 40))]},
    "Helio": {"base": [60, 150, 230], "ops": [
        e(0.50, 0.95, 0.40, 0.25, (40, 80, 200)),
        e(0.50, 0.50, 0.30, 0.40, (240, 80, 40)),
        e(0.40, 0.42, 0.08, 0.10, WHITE), e(0.60, 0.42, 0.08, 0.10, WHITE),
        e(0.42, 0.44, 0.04, 0.06, BLACK), e(0.58, 0.44, 0.04, 0.06, BLACK),
        line([[0.28, 0.30], [0.47, 0.38]], 0.06, BLACK), line([[0.53, 0.38], [0.72, 0.30]], 0.06, BLACK),
        poly([[0.44, 0.62], [0.56, 0.62], [0.50, 0.78]], (250, 200, 60))]},
    "Lump": {"base": [90, 200, 160], "ops": [
        e(0.50, 0.60, 0.46, 0.42, (160, 150, 140)),
        eye(0.36, 0.42, 0.07, (40, 40, 40)), eye(0.64, 0.42, 0.07, (40, 40, 40)),
        e(0.50, 0.70, 0.26, 0.12, (200, 50, 50)), e(0.50, 0.65, 0.24, 0.05, WHITE),
        {"ring": [0.50, 0.60, 0.46, 0.42], "w": 0.03, "c": [110, 100, 90]}]},
    "Hammer-Bot": {"base": [240, 120, 110], "ops": [
        e(0.50, 0.95, 0.44, 0.24, (40, 70, 180)),
        e(0.50, 0.45, 0.38, 0.36, (235, 225, 190)),
        {"rect": [0.20, 0.42, 0.80, 0.62], "c": [40, 40, 50]},
        poly([[0.30, 0.46], [0.44, 0.50], [0.36, 0.58]], (240, 40, 40)), poly([[0.70, 0.46], [0.56, 0.50], [0.64, 0.58]], (240, 40, 40)),
        line([[0.14, 0.30], [0.86, 0.30]], 0.03, (150, 140, 110))]},
    "Mad Scienstain": {"base": [170, 130, 220], "ops": [
        e(0.50, 0.95, 0.46, 0.20, WHITE),
        e(0.50, 0.50, 0.32, 0.36, SKIN),
        e(0.20, 0.35, 0.12, 0.18, (210, 210, 220)), e(0.80, 0.35, 0.12, 0.18, (210, 210, 220)),
        {"ring": [0.38, 0.42, 0.10, 0.09], "w": 0.03, "c": [80, 80, 90]}, {"ring": [0.62, 0.42, 0.10, 0.09], "w": 0.03, "c": [80, 80, 90]},
        e(0.38, 0.42, 0.04, 0.04, BLACK), e(0.62, 0.42, 0.04, 0.04, BLACK),
        e(0.50, 0.58, 0.07, 0.06, (240, 170, 130)),
        e(0.50, 0.78, 0.26, 0.16, (235, 235, 240)),            # beard
        e(0.50, 0.66, 0.18, 0.05, (225, 225, 230))]},           # moustache
    "Rudy": {"base": [110, 200, 120], "ops": [
        e(0.50, 0.55, 0.40, 0.38, (60, 170, 90)),
        poly([[0.30, 0.25], [0.50, 0.00], [0.70, 0.25]], (60, 100, 220)),
        e(0.38, 0.42, 0.08, 0.09, WHITE), e(0.62, 0.42, 0.08, 0.09, WHITE),
        e(0.38, 0.44, 0.04, 0.05, BLACK), e(0.62, 0.44, 0.04, 0.05, BLACK),
        e(0.50, 0.55, 0.09, 0.08, (235, 30, 40)), {"hl": [0.48, 0.52, 0.025]},
        e(0.50, 0.74, 0.18, 0.09, (210, 40, 50)), e(0.50, 0.71, 0.14, 0.03, WHITE)]},
}
FACES["?"] = {"base": [90, 90, 95], "ops": [{"glow": [0.5, 0.4, 0.6, 0.6], "c": [170, 170, 175]}], "question": True}

GRID = ["Dr.Mario", "Wario", "Spearhead", "Webber", "Silky",
        "Appleby", "Jellybob", "Octo", "Helio", "Lump",
        "Hammer-Bot", "Mad Scienstain", "Rudy", "?", "?"]

# texture -> (cells [(face, x, y, w, h, caption or None)], extra captions [(text, x, y, w, h, ink)])
LAYOUTS = {
    "menu_char_titexdata_05_texs_tex": (
        [(GRID[r * 5 + c], [14, 68, 122, 176, 229][c], [14, 68, 121][r], 38, 40, None if GRID[r * 5 + c] == "?" else GRID[r * 5 + c])
         for r in range(3) for c in range(5)],
        [("Select a character!", 60, 0, 170, 12, (255, 190, 40))]),
    "menu_p4_titexdata_00_texs_tex": (
        [(f, 0, 35 * k, 48, 35, None) for k, f in enumerate(
            ["Dr.Mario", "Wario", "Silky", "Spearhead", "Jellybob", "Helio", "Webber", "Appleby", "Lump", "Octo",
             "Hammer-Bot", "Mad Scienstain", "Rudy", "Metal Mario", "Vampire Wario"])], []),
    "menu_char_titexdata_03_texs_tex": ([("Metal Mario", 6, 3, 38, 38, "Metal Mario")], []),
    "menu_char_titexdata_04_texs_tex": ([("Vampire Wario", 7, 3, 38, 38, "Vampire Wario")], []),
}


def _question(w, h):
    img = Image.new("L", (w * 4, h * 4), 0)
    f = ImageFont.truetype(FONT, int(h * 4 * 0.9))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = d.textbbox((0, 0), "?", font=f)
    d.text(((w * 4 - (x1 - x0)) / 2 - x0, (h * 4 - (y1 - y0)) / 2 - y0), "?", font=f, fill=255)
    return np.asarray(img, np.float32).reshape(h, 4, w, 4).mean((1, 3)) / 255


def paint_face(name, w, h, seed=0):
    brief = FACES[name]
    out = facepaint.render(brief, w, h, seed=seed)[..., :3]
    if brief.get("question"):
        q = _question(w, h)
        edge = np.asarray(Image.fromarray((q * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
        out = out * (1 - edge[..., None]) + np.array([120, 40, 10]) * edge[..., None]
        grad = np.linspace(0, 1, h)[:, None, None]
        ink = np.array([255, 220, 40]) * (1 - grad) + np.array([240, 90, 20]) * grad
        out = out * (1 - q[..., None]) + ink * q[..., None]
    return out


def caption(im, text, x, y, w, h, ink=(90, 230, 60), edge=(20, 50, 20)):
    H, W = im.shape[:2]
    SS = 4
    layer = Image.new("L", (W * SS, H * SS), 0)
    f = ImageFont.truetype(FONT, int(h * SS * 1.1))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    if x1 - x0 > w * SS:
        f = ImageFont.truetype(FONT, int(h * SS * 1.1 * w * SS / (x1 - x0)))
        x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    d.text(((x + w / 2) * SS - (x1 - x0) / 2 - x0, (y + h / 2) * SS - (y1 - y0) / 2 - y0), text, font=f, fill=255)
    out_l = layer.filter(ImageFilter.MaxFilter(2 * SS + 1))
    a = np.asarray(layer, np.float32).reshape(H, SS, W, SS).mean((1, 3)) / 255
    o = np.asarray(out_l, np.float32).reshape(H, SS, W, SS).mean((1, 3)) / 255
    im[..., :3] = im[..., :3] * (1 - o[..., None]) + np.asarray(edge, np.float32) * o[..., None]
    im[..., :3] = im[..., :3] * (1 - a[..., None]) + np.asarray(ink, np.float32) * a[..., None]


def render(name, base):
    if name not in LAYOUTS:
        return None
    cells, extra = LAYOUTS[name]
    im = base.astype(np.float32).copy()
    for k, (face, x, y, w, h, cap) in enumerate(cells):
        if cap:                                                       # framed cells (select grids)
            im[max(0, y - 2):y + h + 2, max(0, x - 2):x + w + 2, :3] = (70, 40, 20)
            im[max(0, y - 1):y + h + 1, max(0, x - 1):x + w + 1, :3] = (150, 95, 50)
        im[y:y + h, x:x + w, :3] = paint_face(face, w, h, seed=k)
        if cap:
            caption(im, cap, x - 7, y + h + 1, w + 14, 9)
    for text, x, y, w, h, ink in extra:
        caption(im, text, x, y, w, h, ink=ink, edge=(60, 30, 10))
    return np.clip(im, 0, 255).astype(np.uint8)
