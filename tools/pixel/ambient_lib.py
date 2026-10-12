"""Drawing helpers for the GachaNight ambient-life animations (rubber hose).

A frame is a sparse canvas (`Cv`: dict of (x, y) -> RGB) painted back to
front. Shapes are pixel masks (sets) from pixlib; `Cv.part` paints a mask as a
flat colour with one shadow shade, one highlight shade and a 1 px ink outline.
Everything is integer pixels, hard edges, alpha 0 or 255.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from PIL import Image  # noqa: E402

from pixlib import box, ell, line, poly  # noqa: E402,F401  (re-exported)


def rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# --- contract palette ---------------------------------------------------------
INK = rgb("161320")
RED = rgb("e2231a")
DRED = rgb("9c1420")
ORANGE = rgb("f0802a")
MUSTARD = rgb("f2b632")
CREAM = rgb("f6e7c1")
PAPER = rgb("fff8e3")
NAVY = rgb("1f3a8a")
BLUE = rgb("2f7de1")
SKY = rgb("9fd3f5")
GREEN = rgb("2e9e4f")
STEEL = rgb("8a93a3")
DSTEEL = rgb("4a5160")
WHITE = rgb("fffdf5")
PINK = rgb("f59ab5")
# --- sparing extensions: the shadow / highlight partners and wood ---------------
RED_HI = rgb("f7705c")
ORANGE_SH = rgb("b8501c")
ORANGE_HI = rgb("f9b070")
MUSTARD_SH = rgb("c07c1e")
MUSTARD_HI = rgb("fbe08a")
CREAM_SH = rgb("cdb88c")
NAVY_SH = rgb("14245c")
SKY_SH = rgb("6aa9dc")
SKY_HI = rgb("e3f4ff")
GREEN_SH = rgb("1b6b3a")
GREEN_HI = rgb("7ed68a")
STEEL_HI = rgb("c5ccd6")
DSTEEL_SH = rgb("2c3040")
WHITE_SH = rgb("cfc9bd")
PINK_SH = rgb("c9607f")
PINK_HI = rgb("fcd0dc")
WOOD = rgb("b5763a")
WOOD_SH = rgb("7d4a25")
WOOD_HI = rgb("d99a55")
GREY = (120, 124, 132)

SH = {RED: DRED, DRED: rgb("6a0e1c"), ORANGE: ORANGE_SH, MUSTARD: MUSTARD_SH, CREAM: CREAM_SH,
      PAPER: CREAM, NAVY: NAVY_SH, BLUE: NAVY, SKY: SKY_SH, GREEN: GREEN_SH, STEEL: DSTEEL,
      DSTEEL: DSTEEL_SH, WHITE: WHITE_SH, PINK: PINK_SH, WOOD: WOOD_SH, INK: INK}
HI = {RED: RED_HI, DRED: RED, ORANGE: ORANGE_HI, MUSTARD: MUSTARD_HI, CREAM: PAPER, PAPER: WHITE,
      NAVY: BLUE, BLUE: SKY, SKY: SKY_HI, GREEN: GREEN_HI, STEEL: STEEL_HI, DSTEEL: STEEL,
      WHITE: WHITE, PINK: PINK_HI, WOOD: WOOD_HI, INK: DSTEEL}

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
TAU = 2.0 * math.pi


def rnd(v):
    """Round half up (Python's round() is banker's rounding)."""
    return int(math.floor(v + 0.5))


def wave(i, n, phase=0.0):
    """Sine of the loop position: frame i of n, exact loop closure."""
    return math.sin(TAU * (i / float(n) + phase))


def curve(pts, steps=16):
    """Catmull-Rom spline through the control points, as a list of float points."""
    if len(pts) < 3:
        return list(pts)
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for k in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[k - 1], p[k], p[k + 1], p[k + 2]
        for s in range(steps):
            t = s / float(steps)
            t2, t3 = t * t, t * t * t
            out.append(tuple(
                0.5 * ((2 * p1[a]) + (-p0[a] + p2[a]) * t + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t2
                       + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t3) for a in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def stroke(pts, w=1, smooth=True):
    """Pixels of a constant-thickness line through float points (a rubber hose)."""
    pts = curve(pts) if smooth else list(pts)
    out = set()
    off = (w - 1) / 2.0
    for k in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[k], pts[k + 1]
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for s in range(n + 1):
            t = s / float(n)
            x = rnd(x0 + (x1 - x0) * t - off)
            y = rnd(y0 + (y1 - y0) * t - off)
            for a in range(w):
                for b in range(w):
                    out.add((x + a, y + b))
    return out


def dilate(m):
    out = set(m)
    for (x, y) in m:
        for a, b in N4:
            out.add((x + a, y + b))
    return out


def disc(cx, cy, r):
    """Disc centred on the middle of pixel (cx, cy)."""
    return ell(cx + 0.5, cy + 0.5, r, r)


class Cv:
    def __init__(self, w, h, name=""):
        self.w, self.h, self.name = w, h, name
        self.px = {}

    # -- raw ---------------------------------------------------------------
    def dot(self, x, y, c):
        self.px[(int(x), int(y))] = c

    def dots(self, pts, c):
        for (x, y) in pts:
            self.px[(int(x), int(y))] = c

    def fill(self, m, c):
        for q in m:
            self.px[q] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                self.px[(x, y)] = c

    def erase(self, m):
        for q in m:
            self.px.pop(q, None)

    def ring(self, m, c=INK):
        """Outline around a mask (4-neighbours outside it)."""
        for (x, y) in m:
            for a, b in N4:
                q = (x + a, y + b)
                if q not in m:
                    self.px[q] = c

    # -- shaded part ---------------------------------------------------------
    def part(self, m, c, sh=True, hi=True, outline=True, ink=INK, sc=None, hc=None):
        m = set(m)
        if not m:
            return m
        if outline:
            self.ring(m, ink)
        sc = sc or SH.get(c, c)
        hc = hc or HI.get(c, c)
        xs = [q[0] for q in m]
        ys = [q[1] for q in m]
        cx = (min(xs) + max(xs) + 1) / 2.0
        cy = (min(ys) + max(ys) + 1) / 2.0
        hw = max(1.0, (max(xs) - min(xs) + 1) / 2.0)
        hh = max(1.0, (max(ys) - min(ys) + 1) / 2.0)
        for (x, y) in m:
            d = (x + 0.5 - cx) / hw + (y + 0.5 - cy) / hh
            col = c
            if sh and d > -0.15 and ((x + 1, y) not in m or (x, y + 1) not in m):
                col = sc
            elif hi and d < -0.45 and ((x - 1, y) not in m or (x, y - 1) not in m):
                col = hc
            self.px[(x, y)] = col
        return m

    def panel(self, x0, y0, x1, y1, c, r=0, **kw):
        return self.part(box(x0, y0, x1, y1, r), c, **kw)

    # -- rubber hose ---------------------------------------------------------
    def noodle(self, pts, w=2, c=INK, smooth=True):
        self.fill(stroke(pts, w, smooth), c)

    def glove(self, cx, cy, r=2.5, cuff=None):
        """White glove blob; cuff = (dx, dy) direction towards the arm."""
        self.part(disc(cx, cy, r), WHITE, hi=False)
        if cuff:
            self.dot(cx + cuff[0], cy + cuff[1], WHITE_SH)

    def shoe(self, x0, y, w=4, c=WHITE):
        """Flat rounded shoe: its sole on row y, toe towards +x."""
        self.part(box(x0, y - 1, x0 + w - 1, y, 0) | {(x0 + w - 2, y - 2), (x0 + w - 3, y - 2)}, c, hi=False)

    def eyes(self, x, y, ew=3, eh=5, look=1, blink=False, gap=1, lid=None, ringed=True, down=0):
        """Tall-oval eyes; (x, y) is the top-left pixel of the left eye's white."""
        for k in range(2):
            x0 = x + k * (ew + gap)
            m = box(x0, y, x0 + ew - 1, y + eh - 1, 1 if (ew >= 3 and eh >= 4) else 0)
            if blink:
                if lid is not None:
                    self.fill(m, lid)
                self.rect(x0, y + eh // 2, x0 + ew - 1, y + eh // 2, INK)
                continue
            if ringed:
                self.ring(m)
            self.fill(m, WHITE)
            pw = 1 if ew <= 3 else 2
            if eh >= 4:
                py0, py1 = y + 1 + down, y + eh - 2 + down
            else:
                py0, py1 = y + max(0, eh - 2), y + eh - 1
            if look > 0:
                px0 = x0 + ew - pw
            elif look < 0:
                px0 = x0
            else:
                px0 = x0 + (ew - pw + 1) // 2
            self.rect(px0, py0, px0 + pw - 1, min(py1, y + eh - 1), INK)

    # -- transforms ------------------------------------------------------------
    def sheared(self, pivot_y, ref_y, dx):
        """Shift every row sideways, 0 at pivot_y growing to dx at ref_y."""
        out = Cv(self.w, self.h, self.name)
        span = float(ref_y - pivot_y)
        for (x, y), c in self.px.items():
            out.px[(x + rnd(dx * (y - pivot_y) / span), y)] = c
        return out

    def shifted(self, dx, dy):
        out = Cv(self.w, self.h, self.name)
        for (x, y), c in self.px.items():
            out.px[(x + dx, y + dy)] = c
        return out

    def paste(self, other, dx=0, dy=0):
        for (x, y), c in other.px.items():
            self.px[(x + dx, y + dy)] = c

    def image(self, clip_ok=False):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        p = img.load()
        for (x, y), c in self.px.items():
            if 0 <= x < self.w and 0 <= y < self.h:
                p[x, y] = (c[0], c[1], c[2], 255)
            elif not clip_ok:
                raise ValueError("%s: pixel (%d, %d) outside the %dx%d frame" % (self.name, x, y, self.w, self.h))
        return img


def frames(fn, n, clip_ok=False):
    return [fn(i).image(clip_ok) for i in range(n)]


# ---------------------------------------------------------------- sheets

def strip(imgs):
    w, h = imgs[0].size
    out = Image.new("RGBA", (w * len(imgs), h), (0, 0, 0, 0))
    for i, f in enumerate(imgs):
        out.paste(f, (i * w, 0))
    return out


def contact_sheet(imgs, scale=4, gap=2):
    w, h = imgs[0].size
    n = len(imgs)
    out = Image.new("RGBA", (n * w * scale + (n + 1) * gap, h * scale + 2 * gap), (86, 88, 96, 255))
    for i, f in enumerate(imgs):
        cell = Image.new("RGBA", (w, h), GREY + (255,))
        cell.alpha_composite(f)
        out.paste(cell.resize((w * scale, h * scale), Image.NEAREST), (gap + i * (w * scale + gap), gap))
    return out.convert("RGB")


def save_gif(imgs, path, fps, scale=4, bg=GREY):
    w, h = imgs[0].size
    out = []
    for f in imgs:
        cell = Image.new("RGBA", (w, h), bg + (255,))
        cell.alpha_composite(f)
        out.append(cell.resize((w * scale, h * scale), Image.NEAREST).convert("RGB")
                   .quantize(colors=64, method=Image.MEDIANCUT, dither=Image.NONE))
    ms = max(20, int(round(1000.0 / fps / 10.0)) * 10)
    out[0].save(path, save_all=True, append_images=out[1:], duration=ms, loop=0, disposal=2)


def overview(items, path, scale=3, pad=6, cols_w=300, bg=GREY):
    """items: list of (name, first frame). Packs rows up to cols_w source pixels wide."""
    rows, cur, cur_w = [], [], pad
    for it in items:
        w = it[1].size[0] + pad
        if cur and cur_w + w > cols_w:
            rows.append(cur)
            cur, cur_w = [], pad
        cur.append(it)
        cur_w += w
    if cur:
        rows.append(cur)
    height = pad + sum(max(im.size[1] for _, im in r) + pad for r in rows)
    out = Image.new("RGBA", (cols_w, height), bg + (255,))
    y = pad
    for r in rows:
        rh = max(im.size[1] for _, im in r)
        x = pad
        for _, im in r:
            out.alpha_composite(im, (x, y + rh - im.size[1]))
            x += im.size[0] + pad
        y += rh + pad
    out = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)
    out.convert("RGB").save(path)


# ---------------------------------------------------------------- shared potted plant
# One drawing for the static prop (props.plant) and for amb_plant_sway, so the
# two are interchangeable in a room. base, control point, tip, half width, dark.
PLANT_LEAVES = [
    ((12.0, 28.0), (12.5, 16.0), (12.0, 4.0), 3.6, True),
    ((11.5, 28.0), (9.0, 17.0), (4.5, 9.5), 3.3, False),
    ((12.5, 28.0), (15.5, 16.0), (19.5, 8.5), 3.3, False),
    ((11.5, 29.0), (7.0, 21.0), (3.5, 20.5), 2.8, True),
    ((12.5, 29.0), (17.0, 20.0), (20.5, 19.5), 2.8, False),
    ((12.0, 29.0), (11.0, 22.0), (9.5, 15.5), 2.7, False),
]
LEAF_DEEP = rgb("124f2e")


def plant_pixels(sway=(0, 0, 0, 0, 0, 0)):
    """{(x, y): rgb} of the 24 x 40 potted plant; sway[k] moves the tip of leaf k sideways."""
    px = {}

    def ring(m):
        for (x, y) in m:
            for a, b in N4:
                if (x + a, y + b) not in m:
                    px[(x + a, y + b)] = INK

    def put(m, c):
        for q in m:
            px[q] = c

    steps = 48
    for k, (p0, p1, p2, wd, dark) in enumerate(PLANT_LEAVES):
        d = sway[k]
        tip = (p2[0] + d, p2[1] + 0.35 * abs(d))
        ctl = (p1[0] + 0.45 * d, p1[1])
        pts = []
        for j in range(steps + 1):
            t = j / float(steps)
            pts.append(((1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * ctl[0] + t * t * tip[0],
                        (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * ctl[1] + t * t * tip[1]))
        start = int(steps * 0.3)
        stem, blade, low, rib = set(), set(), set(), set()
        for j in range(start + 1):
            stem.add((int(math.floor(pts[j][0])), int(math.floor(pts[j][1]))))
        for j in range(start, steps + 1):
            u = (j - start) / float(steps - start)
            half = wd * math.sin(math.pi * min(1.0, u * 0.94 + 0.03)) ** 0.7
            a, b = pts[max(0, j - 1)], pts[min(steps, j + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(tx, ty) or 1.0
            nx, ny = -ty / ln, tx / ln
            if nx < 0:                      # the shaded half is the one facing right / down
                nx, ny = -nx, -ny
            x, y = pts[j]
            e = -half
            while e <= half:
                q = (int(math.floor(x + nx * e)), int(math.floor(y + ny * e)))
                blade.add(q)
                if e > 0.7:
                    low.add(q)
                e += 0.3
            if 0.08 < u < 0.8:
                rib.add((int(math.floor(x)), int(math.floor(y))))
        put(stem, GREEN_SH)
        ring(blade)
        put(blade, GREEN_SH if dark else GREEN)
        put(low & blade, LEAF_DEEP if dark else GREEN_SH)
        put(rib & blade, GREEN if dark else GREEN_HI)
    # terracotta pot seen from above-front: rim ellipse with soil, banded body
    pot = poly([(5.5, 31), (18.5, 31), (17, 40), (7, 40)])
    ring(pot)
    put(pot, ORANGE)
    put({q for q in pot if (q[0] + 1, q[1]) not in pot or q[1] == 39}, ORANGE_SH)
    put({q for q in pot if q[1] in (34, 35)}, CREAM)
    put({q for q in pot if q[1] == 35}, CREAM_SH)
    for x in (8, 11, 14):
        px[(x, 34)] = RED
        px[(x + 1, 34)] = RED
    px[(7, 32)] = ORANGE_HI
    px[(7, 33)] = ORANGE_HI
    px[(7, 36)] = ORANGE_HI
    px[(7, 37)] = ORANGE_HI
    lip = ell(12, 29.5, 7.6, 2.5)
    ring(lip)
    put(lip, ORANGE_HI)
    put({q for q in lip if (q[0], q[1] + 1) not in lip}, ORANGE)
    put(ell(12, 29.3, 5.2, 1.3), rgb("5a3418"))
    # the stems leave the soil in front of the rim's far edge
    for (x, y) in ((11, 28), (12, 28), (11, 29), (12, 29)):
        px[(x, y)] = GREEN_SH
    return {q: c for q, c in px.items() if 0 <= q[0] < 24 and 0 <= q[1] < 40}
