"""Shared pixel-art helpers for the GachaNight static sprite generators.

Everything is integer pixels, hard edges, alpha 0 or 255. Shapes are built as
masks (sets of (x, y) pixels) and painted as "parts": a flat colour with one
highlight shade (top-left), one shadow shade (bottom-right) and a 1 px ink
outline.
"""
import colorsys
import math
import os

from PIL import Image


def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


INK = hx("1d2a44")
DARK = hx("2b2b33")
CREAM = hx("f4ecd8")
WALL = hx("efe4c8")
CORAL = hx("ef7a6d")
MINT = hx("7ec8a4")
MUSTARD = hx("e3b44c")
TEAL = hx("4f9ea3")
BATH = hx("c9e6dc")
TAN = hx("dccaa6")
WOOD = hx("a9825a")
WHITE = (255, 255, 255)
# sparing extensions
NIGHT = hx("27375c")      # night sky / unlit glass
GLASS = hx("5b7f96")      # unlit glass tint
GLASS_HI = hx("a9d3da")   # glass highlight / lit glass
STEEL = hx("9aa7b4")      # metal
PINK = hx("f1a7b5")       # blush
RED = hx("c9412f")        # deep red accent
GLOW = hx("fff3a8")       # lamp light
GREEN = hx("6fe08a")      # CRT / pilot lamp green


def _lerp_hue(h, target, t):
    d = ((target - h + 0.5) % 1.0) - 0.5
    return (h + d * t) % 1.0


def shade(c, k):
    """k < 0: shadow shade, k > 0: highlight shade. |k| = 1 is the standard step."""
    r, g, b = [v / 255.0 for v in c[:3]]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    if k < 0:
        t = -k
        if s < 0.06:
            h = 0.64
        h = _lerp_hue(h, 0.68, 0.14 * t)
        s2 = min(1.0, s + 0.13 * t)
        v2 = v * (1.0 - 0.21 * t)
    else:
        t = k
        if s < 0.06:
            h = 0.13
        h = _lerp_hue(h, 0.14, 0.12 * t)
        s2 = s * (1.0 - 0.38 * t)
        v2 = v + (1.0 - v) * 0.55 * t
        if v < 0.35:
            v2 = v + 0.2 * t
    r, g, b = colorsys.hsv_to_rgb(h, max(0.0, s2), max(0.0, min(1.0, v2)))
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


# ---------------------------------------------------------------- masks

def ell(cx, cy, rx, ry):
    """Ellipse in continuous coordinates; pixel (x, y) has its centre at x+.5."""
    out = set()
    for y in range(int(math.floor(cy - ry)) - 1, int(math.ceil(cy + ry)) + 1):
        for x in range(int(math.floor(cx - rx)) - 1, int(math.ceil(cx + rx)) + 1):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                out.add((x, y))
    return out


def box(x0, y0, x1, y1, r=0):
    """Inclusive rectangle with corners cut by r pixels."""
    out = set()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = min(x - x0, x1 - x)
            dy = min(y - y0, y1 - y)
            if dx + dy < r:
                continue
            out.add((x, y))
    return out


def poly(pts):
    """Polygon fill, even-odd, sampled at pixel centres. Points are continuous."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    out = set()
    n = len(pts)
    for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
        py = y + 0.5
        for x in range(int(math.floor(min(xs))), int(math.ceil(max(xs))) + 1):
            px = x + 0.5
            inside = False
            j = n - 1
            for i in range(n):
                xi, yi = pts[i]
                xj, yj = pts[j]
                if (yi > py) != (yj > py):
                    if px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                        inside = not inside
                j = i
            if inside:
                out.add((x, y))
    return out


def line(x0, y0, x1, y1, w=1):
    """Bresenham line between pixel coordinates, stamped with a w x w square."""
    out = set()
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        for a in range(w):
            for b in range(w):
                out.add((x + a, y + b))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
    return out


def path(pts, w=1):
    out = set()
    for i in range(len(pts) - 1):
        out |= line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], w)
    return out


def shift(m, dx, dy):
    return {(x + dx, y + dy) for (x, y) in m}


def mir(m, width=32):
    """Mirror horizontally inside a canvas of the given width."""
    return {(width - 1 - x, y) for (x, y) in m}


def clip(m, x0=-99, y0=-99, x1=999, y1=999):
    return {(x, y) for (x, y) in m if x0 <= x <= x1 and y0 <= y <= y1}


# ---------------------------------------------------------------- sprite

class Spr:
    def __init__(self, w, h, bg=None):
        self.w = w
        self.h = h
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0) if bg is None else tuple(bg) + (255,))
        self.p = self.img.load()

    # -- raw pixels
    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[x, y] = (c[0], c[1], c[2], 255)

    def clear(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[x, y] = (0, 0, 0, 0)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            v = self.p[x, y]
            return v[:3] if v[3] else None
        return None

    def puts(self, m, c):
        for (x, y) in m:
            self.put(x, y, c)

    def pts(self, coords, c):
        for (x, y) in coords:
            self.put(x, y, c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def frame(self, x0, y0, x1, y1, c):
        self.hline(x0, x1, y0, c)
        self.hline(x0, x1, y1, c)
        self.vline(x0, y0, y1, c)
        self.vline(x1, y0, y1, c)

    def panel(self, x0, y0, x1, y1, c, r=0, ink=INK, hl=True, sh=True):
        """Outlined box: ink border on the rectangle edge, bevel inside."""
        m = box(x0, y0, x1, y1, r)
        inner = {q for q in m if all((q[0] + a, q[1] + b) in m for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        self.puts(m - inner, ink)
        self.puts(inner, c)
        if hl:
            for (x, y) in inner:
                if (x, y - 1) not in inner or (x - 1, y) not in inner:
                    self.put(x, y, shade(c, 1))
        if sh:
            for (x, y) in inner:
                if (x, y + 1) not in inner or (x + 1, y) not in inner:
                    self.put(x, y, shade(c, -1))

    # -- shaded part with outline
    def part(self, m, c, outline=True, depth=1, hl=True, sh=True, ink=INK, hc=None, sc=None):
        if not m:
            return
        if outline:
            for (x, y) in m:
                for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + a, y + b)
                    if q not in m:
                        self.put(q[0], q[1], ink)
        xs = [q[0] for q in m]
        ys = [q[1] for q in m]
        cx = (min(xs) + max(xs) + 1) / 2.0
        cy = (min(ys) + max(ys) + 1) / 2.0
        hw = max(1.0, (max(xs) - min(xs) + 1) / 2.0)
        hh = max(1.0, (max(ys) - min(ys) + 1) / 2.0)
        hc = hc or shade(c, 1)
        sc = sc or shade(c, -1)
        for (x, y) in m:
            d = (x + 0.5 - cx) / hw + (y + 0.5 - cy) / hh
            col = c
            if sh and d > -0.25:
                edge = (x + 1, y) not in m or (x, y + 1) not in m
                if depth > 1:
                    edge = edge or (x + 1, y + 1) not in m or (x + 2, y) not in m or (x, y + 2) not in m
                if edge:
                    col = sc
            if hl and col == c and d < -0.5:
                if (x - 1, y) not in m or (x, y - 1) not in m:
                    col = hc
            self.put(x, y, col)

    def outline_all(self, ink=INK):
        add = []
        for y in range(self.h):
            for x in range(self.w):
                if self.p[x, y][3]:
                    continue
                for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if self.get(x + a, y + b) is not None:
                        add.append((x, y))
                        break
        for (x, y) in add:
            self.put(x, y, ink)

    def blit(self, other, ox, oy):
        img = other.img if isinstance(other, Spr) else other
        src = img.load()
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                v = src[x, y]
                if v[3]:
                    self.put(ox + x, oy + y, v[:3])

    def bbox(self):
        return self.img.getbbox()

    def fitted(self, w, h, name="sprite"):
        """Crop to content and paste bottom-centre into a w x h canvas."""
        bb = self.img.getbbox()
        if bb is None:
            raise ValueError(name + ": empty sprite")
        cw, ch = bb[2] - bb[0], bb[3] - bb[1]
        if cw > w or ch > h:
            raise ValueError("%s: content %dx%d does not fit %dx%d" % (name, cw, ch, w, h))
        out = Spr(w, h)
        out.img.paste(self.img.crop(bb), ((w - cw) // 2, h - ch))
        out.p = out.img.load()
        return out

    def save(self, path_):
        os.makedirs(os.path.dirname(path_), exist_ok=True)
        self.img.save(path_)


# ---------------------------------------------------------------- pixel font (5 x 7, chunky)

FONT = {
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["10010", "10010", "10010", "11111", "00010", "00010", "00010"],
}

TINY = {  # 3 x 5 digits
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "011", "001", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "110", "001", "110"],
    "0": ["111", "101", "101", "101", "111"],
}


def glyph(spr, rows, x, y, c, scale=1):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "1":
                spr.rect(x + i * scale, y + j * scale, x + i * scale + scale - 1, y + j * scale + scale - 1, c)


# ---------------------------------------------------------------- contact sheets

GREY = (120, 124, 132)


def sheet(items, path_, cols=8, scale=4, pad=4, bg=GREY, label_h=0):
    """items: list of PIL images (or Spr). Writes a x-scaled contact sheet."""
    imgs = [i.img if isinstance(i, Spr) else i for i in items]
    cw = max(i.size[0] for i in imgs) + pad
    rows = (len(imgs) + cols - 1) // cols
    row_h = []
    for r in range(rows):
        row_h.append(max(i.size[1] for i in imgs[r * cols:(r + 1) * cols]) + pad)
    out = Image.new("RGBA", (cw * min(cols, len(imgs)) + pad, sum(row_h) + pad), bg + (255,))
    y = pad
    for r in range(rows):
        for k, im in enumerate(imgs[r * cols:(r + 1) * cols]):
            x = pad + k * cw + (cw - pad - im.size[0]) // 2
            out.alpha_composite(im.convert("RGBA"), (x, y + row_h[r] - pad - im.size[1]))
        y += row_h[r]
    out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)
    os.makedirs(os.path.dirname(path_), exist_ok=True)
    out.save(path_)
    return out
