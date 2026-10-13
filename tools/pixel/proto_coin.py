"""The protagonist as a coin, after the owner's `diseños/moneda1.png`: a
1 PESETA piece with laurel branches, a tilted hat, white gloves, noodle limbs
and big dark shoes. This sheet shows its sprites (poses) and the faces it
will wear, at 0.55 saturation like the game's screen.

Nothing here is used by the game. It writes
tools/pixel/previews/proto_coin.png (not shipped). Run from the repository
root:

    python tools/pixel/proto_coin.py

The drawing kit is in proto_hero.py (shapes rasterised four times larger and
reduced, cel colouring with hatched shadows, heavier ink on the shadow side);
gloves and the sheet helpers come from proto_cast.py.
"""
import math
import os

from PIL import Image

from proto_hero import Sprite, ramp, pie_eye, cuff, _row, INK, INK_SOFT, WHITE, CREAM, BLACK, BACKDROP
from proto_cast import limb, open_hand, big_fist, desaturate, _tile, SATURATION

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "previews", "proto_coin.png")
W, H = 124, 146
GROUND = 141.5

COIN = ramp("#96701e", "#dcb24a", "#f8e49a")
COIN_EDGE = ramp("#5c4212", "#a07a26", "#dcb24a")
HAT = ramp("#1c1310", "#3a2a22", "#6c5646")
BAND = ramp("#96701e", "#dcb24a", "#f8e49a")
BOOT = ramp("#17100e", "#3a2a21", "#705a48")
MOUTH = ramp("#3a0f12")[0]
TONGUE = ramp("#c9543f")[0]
TEAR = ramp("#3d7f96", "#8cc8d6", "#e6f6f4")
ROSE = ramp("#d98f78")[0]

FONT = {
    "P": ["110", "101", "110", "100", "100"], "E": ["111", "100", "110", "100", "111"],
    "S": ["011", "100", "010", "001", "110"], "T": ["111", "010", "010", "010", "010"],
    "A": ["010", "101", "111", "101", "101"],
}
ONE = ["00110", "01110", "11110", "00110", "00110", "00110", "00110", "11111"]


# --- the coin itself ------------------------------------------------------------------

def coin(s, cx, cy, back=False):
    """The disc, seen a little from the side so its reeded edge shows. Returns
    the mask of the face that looks at us."""
    side = -6.0 if back else 6.0
    rear = s.oval(cx + side, cy, 30.0, 31.0)
    front = s.oval(cx, cy, 30.0, 31.0)
    s.part(rear, COIN_EDGE, shade=0.3, mode="tube")
    s.dots([(x, y) for x, y in rear - front if y % 3 == 0 and (x - 1, y) in rear and (x + 1, y) in rear], INK_SOFT)   # reeding
    s.part(front, COIN, shade=0.22, gloss=True)
    ring = s.oval(cx, cy, 27.0, 28.0) - s.oval(cx, cy, 25.6, 26.6)
    s.dots(ring & front, COIN[0])
    s.dots(({(x + 1, y + 1) for x, y in ring} & front) - ring, COIN[2])
    return front


def laurel(s, cx, cy, side, clip):
    """A branch struck into the metal along the rim: a stem and paired leaves."""
    radius = 21.5
    stem = set()
    for angle in range(128, 200):
        a = math.radians(angle)
        stem.add((int(round(cx + side * -math.cos(a) * -radius)), int(round(cy + math.sin(a) * radius))))
    leaves = set()
    for angle in range(134, 200, 16):
        a = math.radians(angle)
        px, py = cx + side * math.cos(a) * radius, cy + math.sin(a) * radius
        tangent = math.degrees(a) + 90.0
        for lean, reach in ((40.0, 2.6), (-40.0, -2.6)):
            lx = px + side * math.cos(a) * reach
            ly = py + math.sin(a) * reach
            leaves |= s.oval(lx, ly - 1.5, 3.0, 1.3, side * (tangent + lean))
    drawn = (stem | leaves) & clip
    s.dots(drawn, COIN[0])


def stamp(s, rows, x0, y0, clip, color):
    s.dots([(x0 + x, y0 + y) for y, row in enumerate(rows) for x, bit in enumerate(row) if bit == "1" and (x0 + x, y0 + y) in clip], color)


def legend(s, cx, cy, clip):
    """1 PESETA, the word following the rim."""
    stamp(s, ONE, int(cx - 2), int(cy + 10), clip, INK_SOFT)
    word = "PESETA"
    for index, letter in enumerate(word):
        offset = index - (len(word) - 1) / 2.0
        stamp(s, FONT[letter], int(round(cx + offset * 4.0 - 1)), int(round(cy + 22.0 - abs(offset) ** 1.7 * 0.7)), clip, INK_SOFT)


def reverse(s, cx, cy, clip):
    """The other side: a plain shield in a wreath, worn smooth."""
    shield = s.poly([(cx - 9, cy - 12), (cx + 9, cy - 12), (cx + 9, cy + 2), (cx, cy + 13), (cx - 9, cy + 2)])
    s.dots(({(x + 1, y + 1) for x, y in shield} & clip) - shield, COIN[2])
    s.dots((shield - s.poly([(cx - 7, cy - 10), (cx + 7, cy - 10), (cx + 7, cy + 1), (cx, cy + 10), (cx - 7, cy + 1)])) & clip, COIN[0])
    s.dots((s.hose([(cx - 7, cy - 4), (cx + 7, cy - 4)], 1.0) | s.hose([(cx, cy - 10), (cx, cy + 9)], 1.0)) & clip, COIN[0])
    for step in range(0, 360, 12):
        point = (int(round(cx + math.cos(math.radians(step)) * 22.5)), int(round(cy + math.sin(math.radians(step)) * 23.5)))
        if point in clip:
            s.dots([point], COIN[0])
    s.dots((s.hose([(cx + 12, cy - 16), (cx + 18, cy - 8)], 1.0) | s.hose([(cx - 16, cy + 10), (cx - 11, cy + 15)], 1.0)) & clip, COIN[0])   # scratches


def hat(s, cx, cy, turn):
    """A flat-crowned hat with a pale band, worn at an angle."""
    a = math.radians(turn)

    def at(dx, dy):
        return (cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a))
    crown = s.poly([at(-10, -11), at(-7, -13), at(7, -13), at(10, -11), at(11, 0), at(-11, 0)])
    s.part(crown, HAT, shade=0.3, gloss=True)
    s.part(s.poly([at(-11, -4.5), at(11, -4.5), at(11, -0.5), at(-11, -0.5)]) & crown, BAND, shade=0.3, mode="tube", outline=None, form=crown)
    s.part(s.oval(cx, cy + 0.5, 17.0, 3.6, turn), HAT, shade=0.35, gloss=True)
    s.dots(s.hose([at(-12, -0.5), at(-4, -2.2), at(5, -2.4)], 1.0), HAT[2])


# --- faces -----------------------------------------------------------------------------

FACES = ["alegre", "euforico", "sorpresa", "triste", "enfado", "sueno", "guino", "miedo", "codicia", "pillo"]
FACE_NAMES = {"alegre": "ALEGRE (normal)", "euforico": "EUFORICO (premio raro)", "sorpresa": "SORPRESA", "triste": "TRISTE (sin monedas)",
              "enfado": "ENFADO", "sueno": "SUENO (sofa)", "guino": "GUINO", "miedo": "MIEDO", "codicia": "CODICIA", "pillo": "PILLO (compra)"}


def _brow(s, x, y, tilt, clip, lift=0.0):
    """A brow over the eye at x; `tilt` > 0 raises its outer end."""
    side = -1.0 if x < 0 else 1.0
    del side
    s.dots(s.hose([(x - 4.2, y - lift + tilt), (x, y - lift - 1.4), (x + 4.2, y - lift - tilt)], 1.8) & clip, INK)


def _lid(s, eye, x, ey, inner, outer, left, clip):
    """A slanted upper lid: `inner` and `outer` are how far it comes down at
    each end of the eye."""
    a, b = (outer, inner) if left else (inner, outer)
    lid = s.poly([(x - 7, ey - 12), (x + 7, ey - 12), (x + 7, ey - 9.5 + b), (x - 7, ey - 9.5 + a)]) & eye & clip
    s.dots(lid, COIN[0])
    s.dots(s.hose([(x - 6, ey - 9.5 + a), (x + 6, ey - 9.5 + b)], 1.0) & eye & clip, INK)


def _d_mouth(s, cx, y, half, deep, clip, tongue=True):
    """An open laugh: flat on top, round below, tongue inside."""
    mouth = {(px, py) for px, py in s.oval(cx, y, half, deep) if py >= y} & clip
    s.part(mouth, [MOUTH, MOUTH, MOUTH], mode="flat")
    if tongue:
        s.dots(s.oval(cx + 0.5, y + deep * 0.78, half * 0.55, deep * 0.36) & mouth, TONGUE)
    s.dots(s.hose([(cx - half - 2.5, y - 2.0), (cx - half - 0.5, y)], 1.0) | s.hose([(cx + half + 2.5, y - 2.0), (cx + half + 0.5, y)], 1.0), INK)


def face(s, cx, cy, clip, kind="alegre"):
    lx, rx, ey = cx - 5.8, cx + 5.8, cy - 8.0
    left_eye, right_eye = s.oval(lx, ey, 5.0, 9.0, -4), s.oval(rx, ey - 0.5, 5.0, 9.0, -4)
    brows = {"alegre": (1.0, 1.0, 1.5), "sorpresa": (1.5, 1.5, 4.0), "triste": (-2.6, -2.6, 0.5), "enfado": (3.0, 3.0, -2.5),
             "sueno": (0.0, 0.0, -1.0), "guino": (1.0, 2.5, 1.5), "miedo": (-2.6, -2.6, 3.0), "codicia": (2.0, 2.0, 2.0), "pillo": (2.4, -0.5, 0.0)}
    open_eyes = kind not in ("euforico", "sueno")
    if kind in ("sorpresa", "miedo"):
        for x, eye in ((lx, left_eye), (rx, right_eye)):
            s.part(eye, CREAM, mode="flat", clip=clip)
            s.dots(eye & clip, WHITE)
            s.dots(s.oval(x + (0.0 if kind == "sorpresa" else -0.6), ey + 0.5, 1.9, 2.6) & eye, INK)
    elif kind == "codicia":
        for x, eye in ((lx, left_eye), (rx, right_eye)):
            s.part(eye, CREAM, mode="flat", clip=clip)
            s.dots(eye & clip, WHITE)
            disc = s.oval(x + 0.3, ey + 1.5, 3.4, 4.6) & eye
            s.part(disc, COIN, shade=0.3, gloss=True)
            s.dots(s.hose([(x + 0.3, ey - 0.5), (x + 0.3, ey + 3.5)], 1.0) & disc, INK)
    elif open_eyes:
        if kind == "guino":
            s.dots(s.hose([(lx - 4.5, ey + 1.5), (lx, ey - 3.0), (lx + 4.5, ey + 1.5)], 2.4) & clip, INK)
            pie_eye(s, rx, ey - 0.5, 5.0, 9.0, -4, clip=clip)
        else:
            look = {"triste": (0.4, 2.4), "pillo": (1.8, 0.6)}.get(kind, (1.0, 1.4))
            pie_eye(s, lx, ey, 5.0, 9.0, -4, look=look, clip=clip)
            pie_eye(s, rx, ey - 0.5, 5.0, 9.0, -4, look=look, clip=clip)
            if kind == "triste":
                _lid(s, left_eye, lx, ey, 1.0, 6.0, True, clip)
                _lid(s, right_eye, rx, ey - 0.5, 1.0, 6.0, False, clip)
            elif kind == "enfado":
                _lid(s, left_eye, lx, ey, 7.0, 2.0, True, clip)
                _lid(s, right_eye, rx, ey - 0.5, 7.0, 2.0, False, clip)
            elif kind == "pillo":
                _lid(s, left_eye, lx, ey, 6.0, 6.0, True, clip)
                _lid(s, right_eye, rx, ey - 0.5, 6.0, 6.0, False, clip)
    elif kind == "euforico":
        for x in (lx, rx):
            s.dots(s.hose([(x - 4.5, ey + 2.0), (x, ey - 4.5), (x + 4.5, ey + 2.0)], 2.6) & clip, INK)
    else:  # sueno
        for x in (lx, rx):
            s.dots(s.hose([(x - 4.0, ey - 1.0), (x, ey + 6.0), (x + 4.0, ey - 1.0)], 2.4) & clip, INK)
    if kind in brows:
        tl, tr, lift = brows[kind]
        _brow(s, lx, ey - 11.5, -tl, clip, lift)
        _brow(s, rx, ey - 12.0, tr, clip, lift)
    my = cy + 4.5
    if kind in ("alegre", "guino", "codicia"):
        _d_mouth(s, cx, my, 8.0 if kind != "codicia" else 9.5, 6.0, clip)
    elif kind == "euforico":
        _d_mouth(s, cx, my - 1.0, 10.5, 8.5, clip)
    elif kind == "sorpresa":
        s.part(s.oval(cx, my + 3.0, 3.6, 4.6) & clip, [MOUTH, MOUTH, MOUTH], mode="flat")
    elif kind == "triste":
        s.dots(s.hose([(cx - 7, my + 5.5), (cx, my + 1.5), (cx + 7, my + 5.5)], 2.2) & clip, INK)
        s.part(s.hose([(lx - 1.5, ey + 10.5), (lx - 2.5, ey + 15.5)], 3.0, 4.0) & clip, TEAR, shade=0.3, gloss=True)
    elif kind == "enfado":
        teeth = s.poly([(cx - 8, my + 0.5), (cx + 8, my - 0.5), (cx + 7, my + 5.5), (cx - 7, my + 6.5)]) & clip
        s.part(teeth, CREAM, mode="flat")
        s.dots(teeth, WHITE)
        s.dots((s.hose([(cx - 7.5, my + 3.4), (cx + 7.5, my + 2.6)], 1.0) | {(x, y) for x, y in teeth if (x - int(cx)) % 4 == 0}) & teeth, INK_SOFT)
        s.dots(s.hose([(cx + 13, ey - 16), (cx + 17, ey - 12)], 1.0) | s.hose([(cx + 17, ey - 16), (cx + 13, ey - 12)], 1.0), INK)   # vein
    elif kind == "sueno":
        s.part(s.oval(cx + 1.0, my + 3.0, 2.4, 2.0) & clip, [MOUTH, MOUTH, MOUTH], mode="flat")
    elif kind == "miedo":
        wave = set()
        points = [(cx - 8 + step * 3.2, my + 3.0 + (1.6 if step % 2 else -1.6)) for step in range(6)]
        for index in range(len(points) - 1):
            wave |= s.hose([points[index], points[index + 1]], 1.0)
        s.dots({(x, y + dy) for x, y in wave for dy in (0, 1)} & clip, INK)
        s.part(s.hose([(cx + 17, ey - 9), (cx + 18.5, ey - 3.5)], 2.2, 4.0) & clip, TEAR, shade=0.3, gloss=True)   # sweat
    elif kind == "pillo":
        s.dots(s.hose([(cx - 8, my + 2.0), (cx, my + 5.5), (cx + 9, my + 0.5)], 2.2) & clip, INK)
        s.dots(s.hose([(cx + 9, my + 0.5), (cx + 11, my - 2.0)], 1.0) & clip, INK)
    if kind not in ("enfado", "miedo", "triste"):
        s.dots(s.oval(cx - 15.5, cy + 3.0, 2.8, 1.6) & clip, ROSE)
        s.dots(s.oval(cx + 15.5, cy + 2.0, 2.8, 1.6) & clip, ROSE)


def sparkle(s, x, y, size=2):
    s.dots([(x + step, y) for step in range(-size, size + 1)] + [(x, y + step) for step in range(-size, size + 1)], COIN[2])
    s.dots([(x, y)], WHITE)


def head(kind):
    """Just the coin and its hat, for the face sheet."""
    s = Sprite(84, 86)
    front = coin(s, 38.0, 51.0)
    laurel(s, 38.0, 51.0, -1, front)
    laurel(s, 38.0, 51.0, 1, front)
    legend(s, 38.0, 51.0, front)
    face(s, 38.0, 51.0, front, kind)
    hat(s, 34.0, 20.0, -12.0)
    if kind == "euforico":
        for x, y in ((6, 30), (76, 22), (80, 46)):
            sparkle(s, x, y)
    if kind == "sueno":
        for index, (zx, zy) in enumerate(((66, 22), (72, 14), (78, 6))):
            size = 4 - index
            s.dots(s.hose([(zx, zy), (zx + size, zy)], 1.0) | s.hose([(zx + size, zy), (zx, zy + size)], 1.0) | s.hose([(zx, zy + size), (zx + size, zy + size)], 1.0), INK)
    heavy = [(x + dx, y + dy) for (x, y) in list(s.px) for dx, dy in ((1, 0), (0, 1)) if (x + dx, y + dy) not in s.px]
    s.dots(heavy, INK)
    return s


# --- poses -----------------------------------------------------------------------------

def boot(s, cx, cy, facing=1, turn=0.0):
    """A big dark shoe with a pale sole and a shine on the toe."""
    upper = s.oval(cx, cy, 11.0, 6.0, turn) | s.oval(cx + facing * 5.0, cy - 0.8, 6.6, 6.0, turn)
    if turn == 0.0:
        upper = s.rows(upper, 0, int(cy + 4))
    s.part(upper, BOOT, shade=0.3, gloss=True)
    s.dots([(x, y) for x, y in upper if (x, y + 1) not in upper or (x, y + 2) not in upper], CREAM[1])                # sole
    s.dots(s.hose([(cx + facing * 5.0, cy - 4.0), (cx + facing * 9.5, cy - 3.2), (cx + facing * 11.0, cy - 0.5)], 1.0) & upper, WHITE)
    for step in range(3):                                                                                            # laces
        lx = cx - facing * (1.0 + step * 2.6)
        s.dots(s.hose([(lx - 1, cy - 4.4), (lx + 1, cy - 2.8)], 1.0) & upper, BOOT[2])


POSES = {
    # legs: (points, shoe x, y, facing, turn); arms: (points, hand kind, x, y, extra)
    "saludo": {
        "legs": [([(52, 93), (42, 105), (33, 115)], 26.0, 121.0, -1, -18.0), ([(68, 93), (77, 107), (73, 124)], 81.0, 131.0, 1, 0.0)],
        "far": ([(94, 66), (112, 72), (108, 86)], "fist", 107.5, 91.5), "near": ([(33, 62), (10, 60), (21, 37)], "open", 25.0, 29.0),
        "hat": (47.0, 27.0, -16.0),
    },
    "quieto": {
        "legs": [([(54, 93), (50, 110), (49, 126)], 43.0, 132.0, -1, 0.0), ([(68, 93), (73, 110), (74, 126)], 81.0, 132.0, 1, 0.0)],
        "far": ([(94, 68), (110, 82), (104, 98)], "fist", 103.0, 103.0), "near": ([(33, 66), (12, 76), (24, 90)], "fist", 27.0, 93.0),
        "hat": (58.0, 26.0, -5.0),
    },
    "paso": {
        "legs": [([(54, 93), (44, 107), (34, 116)], 27.0, 121.0, -1, -28.0), ([(68, 93), (84, 99), (82, 114)], 91.0, 119.0, 1, 12.0)],
        "far": ([(94, 64), (112, 56), (112, 42)], "fist", 112.0, 37.0), "near": ([(33, 66), (14, 74), (16, 90)], "fist", 16.5, 95.0),
        "hat": (56.0, 26.0, -9.0),
    },
}


def figure(pose="saludo", kind="alegre", back=False):
    s = Sprite(W, H)
    data = POSES[pose]
    cx, cy = 62.0, 62.0
    for points, sx, sy, facing, turn in data["legs"]:
        limb(s, points, 4.8)
        boot(s, sx, sy, facing, turn)
    far_points, far_hand, fx, fy = data["far"]
    limb(s, far_points)
    front = coin(s, cx, cy, back)
    if back:
        reverse(s, cx, cy, front)
    else:
        laurel(s, cx, cy, -1, front)
        laurel(s, cx, cy, 1, front)
        legend(s, cx, cy, front)
        face(s, cx, cy, front, kind)
    big_fist(s, fx, fy)
    hx, hy, turn = data["hat"]
    hat(s, hx, hy, turn)
    near_points, near_hand, nx, ny = data["near"]
    limb(s, near_points)
    cuff(s, near_points[-1][0], near_points[-1][1], 4.4, 2.6, 10)
    if near_hand == "open":
        open_hand(s, nx, ny, up=True, thumb=1)                                              # fingers on the brim
    else:
        big_fist(s, nx, ny, thumb=(1, -1))
    s.finish(GROUND, 36.0, 60.0)
    return s


# --- sheet --------------------------------------------------------------------------------

def build():
    sprites = [("SALUDO (pose de moneda1)", figure("saludo", "alegre")), ("QUIETO", figure("quieto", "pillo")),
               ("PASO (andando)", figure("paso", "alegre")), ("ESPALDA (reverso)", figure("quieto", "alegre", back=True))]
    rows = [_row([_tile(sprite.image(), 3, name) for name, sprite in sprites], "LA MONEDA: SPRITES  %d x %d px, saturacion %.2f" % (W, H, SATURATION))]
    faces = [(FACE_NAMES[kind], head(kind)) for kind in FACES]
    rows.append(_row([_tile(sprite.image(), 3, name) for name, sprite in faces[:5]], "CARAS"))
    rows.append(_row([_tile(sprite.image(), 3, name) for name, sprite in faces[5:]], ""))
    sheet = Image.new("RGBA", (max(row.width for row in rows), sum(row.height for row in rows)), BACKDROP)
    y = 0
    for row in rows:
        sheet.alpha_composite(row, (0, y))
        y += row.height
    return desaturate(sheet, SATURATION)


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    build().save(OUT)
    print("wrote %s" % os.path.relpath(OUT))
