"""Oblique-view room tiles (opaque, seamless) for the rubber-hose art contract.

Also hosts the palette and the small drawing helpers shared with props.py:
flat colour + ONE shadow + ONE highlight, bold near-black outline, no gradients.
"""
import os

from PIL import Image

from pixlib import Spr, hx, mix, box, sheet

INK = hx("161320")
WHITE = hx("fffdf5")


def pal(base, sh, hi):
    """A colour ramp: (flat, shadow, highlight)."""
    return (hx(base), hx(sh), hx(hi))


RED = pal("e2231a", "9c1420", "ff6f55")
ORANGE = pal("f0802a", "b8521a", "ffb060")
MUSTARD = pal("f2b632", "c07f1c", "ffe07a")
CREAM = pal("f6e7c1", "d4bd8c", "fff8e3")
NAVY = pal("1f3a8a", "142456", "2f7de1")
BLUE = pal("2f7de1", "1f3a8a", "9fd3f5")
SKY = pal("9fd3f5", "5fa3d8", "e6f6ff")
GREEN = pal("2e9e4f", "1c6b3a", "6fd07a")
STEEL = pal("8a93a3", "4a5160", "c4ccd6")
DSTEEL = pal("4a5160", "2c3040", "8a93a3")
PINK = pal("f59ab5", "c9607f", "ffc9d8")
PORC = pal("fffdf5", "c9cfd9", "ffffff")
WOOD = pal("b5722f", "7d4a22", "dea05a")
CARD = pal("d49a55", "a06c34", "ecc084")
LOCK = pal("6f8fb5", "46618a", "a9c4e0")


class Cv(Spr):
    """Spr with contract ink and explicit hard-edged shading helpers."""

    def ol(self, m, c=INK):
        for (x, y) in m:
            for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + a, y + b) not in m:
                    self.put(x + a, y + b, c)

    def shape(self, m, p, sh=1, hi=0, outline=True):
        """Outlined flat shape; sh/hi = thickness of the bottom-right shadow rim
        and of the top-left highlight rim (0 = none)."""
        if outline:
            self.ol(m)
        self.puts(m, p[0])
        if sh:
            self.puts(rim(m, 1, 0, sh) | rim(m, 0, 1, sh), p[1])
        if hi:
            self.puts((rim(m, -1, 0, hi) | rim(m, 0, -1, hi)) - rim(m, 1, 0, sh + 1) - rim(m, 0, 1, sh + 1), p[2])

    def block(self, x0, y0, x1, y1, top, p, r=0, tp=None, sh=True):
        """Cuboid in the oblique view. The rectangle includes its ink border;
        the first `top` inner rows are the top surface (highlight shade), the
        rest is the front face with a shadow on its bottom row and right column."""
        m = box(x0, y0, x1, y1, r)
        inner = {q for q in m if all((q[0] + a, q[1] + b) in m for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        self.puts(m - inner, INK)
        tc = (tp or p)[2]
        for (x, y) in inner:
            if y <= y0 + top:
                c = tc
            else:
                c = p[0]
                if sh and ((x, y + 1) not in inner or (x + 1, y) not in inner):
                    c = p[1]
            self.put(x, y, c)

    def stamp(self, rows, x, y, c, scale=1):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == "1":
                    self.rect(x + i * scale, y + j * scale, x + i * scale + scale - 1, y + j * scale + scale - 1, c)


def rim(m, dx, dy, n=1):
    out = set()
    for (x, y) in m:
        for k in range(1, n + 1):
            if (x + dx * k, y + dy * k) not in m:
                out.add((x, y))
                break
    return out


# ---------------------------------------------------------------- tiles

SIZES = {
    "wall_bath": (16, 16), "wall_corridor": (16, 16), "wall_hall": (16, 16), "wall_gallery": (16, 16),
    "wall_reception": (16, 16), "wall_staff": (16, 16),
    "floor_bath": (16, 10), "floor_hall": (16, 10), "floor_gallery": (16, 10), "floor_staff": (16, 10),
    "wall_top": (16, 8), "trim": (16, 6), "pillar": (14, 16), "front_ledge": (16, 8),
}

WALL = hx("f6e7c1")


def wall_bath():
    """Small glazed ceramic tiles, aqua, two tints in a quiet checker."""
    s = Cv(16, 16, hx("b4e2e4"))
    grout = hx("7fbccb")
    for y in range(16):
        for x in range(16):
            alt = ((x // 8) + (y // 8)) % 2
            c = hx("a6dade") if alt else hx("b9e5e6")
            if x % 8 == 7 or y % 8 == 7:
                c = grout
            elif (x % 8 == 0 and y % 8 < 6) or (y % 8 == 0 and x % 8 < 6):
                c = hx("e2f6f5")
            s.put(x, y, c)
    return s


def wall_corridor():
    """Plain cream plaster with a faint woven fleck."""
    s = Cv(16, 16, WALL)
    d = mix(WALL, CREAM[1], 0.4)
    for (x, y) in ((3, 4), (4, 4), (11, 12), (12, 12), (13, 2), (6, 10)):
        s.put(x, y, d)
    for (x, y) in ((8, 6), (0, 14)):
        s.put(x, y, CREAM[2])
    return s


def wall_hall():
    s = Cv(16, 16, WALL)
    r = mix(WALL, RED[0], 0.26)
    n = mix(WALL, NAVY[0], 0.2)
    m = mix(WALL, MUSTARD[0], 0.4)
    for (cx, cy, c) in ((4, 4, r), (12, 12, n)):
        for (a, b) in ((0, -2), (-1, -1), (1, -1), (-2, 0), (2, 0), (-1, 1), (1, 1), (0, 2), (0, -1), (0, 1),
                       (-1, 0), (1, 0)):
            s.put(cx + a, cy + b, c)
        s.put(cx, cy, WALL)
    for (cx, cy) in ((12, 4), (4, 12)):
        s.put(cx, cy, m)
    return s


GALLERY_WALL = hx("7cc3b8")


def wall_gallery():
    """Display backing of the figure gallery: a light sea-green felt with a
    tone-on-tone diamond dot lattice. Clearly lighter than the near-black
    silhouettes of undiscovered figures and than rubber-hose limbs."""
    base = GALLERY_WALL
    s = Cv(16, 16, base)
    d = hx("6bb5ab")
    lgt = hx("92d0c4")
    for (cx, cy) in ((4, 4), (12, 12)):
        for (a, b) in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            s.put(cx + a, cy + b, d)
        s.put(cx, cy, lgt)
    for (cx, cy) in ((12, 4), (4, 12)):
        s.put(cx, cy, lgt)
    for (x, y) in ((0, 0), (8, 8), (8, 0), (0, 8)):
        s.put(x, y, d)
    return s


def wall_reception():
    s = Cv(16, 16, WALL)
    a = mix(WALL, MUSTARD[0], 0.3)
    b = mix(WALL, RED[0], 0.22)
    for x in (2, 10):
        s.vline(x, 0, 15, a)
        s.vline(x + 1, 0, 15, a)
    for x in (6, 14):
        s.vline(x, 0, 15, b)
    return s


def wall_staff():
    base = hx("d9b98a")
    s = Cv(16, 16, base)
    d = hx("c29f6c")
    lgt = hx("e8cfa6")
    for (cx, cy) in ((4, 4), (12, 12)):
        for (a, b) in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            s.put(cx + a, cy + b, d)
        s.put(cx, cy, lgt)
    for x in (0, 8):
        s.vline(x, 0, 15, mix(base, d, 0.5))
    return s


def _checker(a, b, grout=None, gloss=0.0):
    s = Cv(16, 10, a)
    for y in range(10):
        for x in range(16):
            c = b if ((x // 8) + (y // 5)) % 2 else a
            if grout is not None and (x % 8 == 7 or y % 5 == 4):
                c = grout
            elif gloss and y % 5 == 0:
                c = mix(c, WHITE, gloss)
            s.put(x, y, c)
    return s


def floor_bath():
    """Warm sand mosaic with small blue cabochons: a different hue family
    from the aqua wall tiles, so wall and floor separate at a glance."""
    a, b = hx("f1e6c9"), hx("e4d3ab")
    s = _checker(a, b)
    grout = hx("d8c79e")
    for y in range(10):
        for x in range(16):
            if x % 8 == 7 or y % 5 == 4:
                s.put(x, y, grout)
    for (x, y) in ((7, 4), (15, 9)):
        s.put(x, y, hx("5f9fca"))
        s.put((x + 1) % 16, y, hx("5f9fca"))
    for (x, y) in ((1, 0), (9, 5)):
        s.hline(x, x + 2, y, hx("fbf3dc"))
    return s


def floor_hall():
    """Quiet Showa lino: big low-contrast cream / peach harlequin diamonds
    (one diamond per 16 x 10 tile) with a small red stud where they meet."""
    a, b = hx("f3e4c2"), hx("ecc9a9")
    s = Cv(16, 10, a)
    for y in range(10):
        for x in range(16):
            dx = abs(x + 0.5 - 8) / 8.0
            dy = abs(y + 0.5 - 5) / 5.0
            if dx + dy < 1.0:
                s.put(x, y, b)
    s.put(0, 0, hx("d98672"))
    s.put(15, 0, hx("d98672"))
    s.put(7, 5, hx("d98672"))
    s.put(8, 5, hx("d98672"))
    return s


def _planks(p, joints):
    s = Cv(16, 10, p[0])
    for row in range(2):
        y0 = row * 5
        s.hline(0, 15, y0 + 4, p[1])
        s.vline(joints[row], y0 + 1, y0 + 3, mix(p[0], p[1], 0.6))
        s.hline((joints[row] + 5) % 16, (joints[row] + 5) % 16 + 3, y0 + 2, p[2])
    return s


def floor_gallery():
    return _planks((hx("70483a"), hx("5a372c"), hx("7e5545")), (5, 11))


def floor_staff():
    return _planks((hx("c69252"), hx("a87740"), hx("d2a366")), (9, 2))


def wall_top():
    s = Cv(16, 8, RED[0])
    s.hline(0, 15, 0, INK)
    s.hline(0, 15, 1, RED[2])
    s.hline(0, 15, 4, RED[1])
    s.hline(0, 15, 5, INK)
    s.hline(0, 15, 6, MUSTARD[0])
    s.hline(0, 15, 7, INK)
    for x in (3, 11):
        s.rect(x, 2, x + 1, 3, CREAM[0])
    return s


def trim():
    s = Cv(16, 6, WOOD[0])
    s.hline(0, 15, 0, INK)
    s.hline(0, 15, 1, WOOD[2])
    s.hline(0, 15, 4, WOOD[1])
    s.hline(0, 15, 5, INK)
    return s


def pillar():
    s = Cv(14, 16, RED[0])
    s.vline(0, 0, 15, INK)
    s.vline(13, 0, 15, INK)
    s.vline(1, 0, 15, RED[0])
    s.vline(2, 0, 15, RED[2])
    s.vline(3, 0, 15, RED[2])
    for x in (10, 11, 12):
        s.vline(x, 0, 15, RED[1])
    return s


def front_ledge():
    top = hx("3a4056")
    s = Cv(16, 8, top)
    s.hline(0, 15, 0, INK)
    s.hline(0, 15, 1, STEEL[0])
    s.hline(0, 15, 5, INK)
    s.hline(0, 15, 6, DSTEEL[1])
    s.hline(0, 15, 7, INK)
    s.vline(15, 2, 4, DSTEEL[1])
    return s


def build_all():
    return {name: globals()[name]() for name in SIZES}


def previews(out, prev):
    tiled = []
    for name in SIZES:
        t = out[name].img
        big = Image.new("RGBA", (t.size[0] * 6, t.size[1] * 6))
        for j in range(6):
            for i in range(6):
                big.paste(t, (i * t.size[0], j * t.size[1]))
        tiled.append(big)
    sheet(tiled, os.path.join(prev, "rh_tiles.png"), cols=5, scale=4)
