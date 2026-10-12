"""Shared drawing helpers for the GachaNight rubber-hose animation sheets.

Art contract v3: old-cartoon sepia, sprites at 1.5 px per world pixel.
A frame is a sparse canvas (dict of (x, y) -> colour). Parts are pixel masks
(sets) stamped back to front with a 1 px ink outline. Limbs are "hoses":
quadratic Bezier curves stamped with a constant-width brush, re-posed on every
frame, so they bend in smooth arcs and never grow elbows or knees.
Everything is whole pixels and alpha 0 or 255.
"""
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from pixlib import ell, poly, shift  # noqa: E402,F401  (shared, read-only)


from sepia import (INK, INK_SOFT, PAPER, SEPIA, GREY, BLACK, BRASS, COPPER, GOLD, RED, MUSTARD,  # noqa: E402,F401
                   OLIVE, TEAL, BLUE, ROSE, PLUM, GLASS, CAPSULE)

# Every colour comes from the shared sepia ramps (tools/pixel/sepia.py).
S = 1.5                      # sprite pixels per world pixel (art contract v3)
WHITE = PAPER[4]             # the brightest tone of the look: warm paper, never pure white
GLOVE_RAMP = (PAPER[2], PAPER[3], PAPER[4], PAPER[4])
BACKDROP = (118, 98, 72)     # review sheets only

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def rnd(v):
    """Round half up (Python's round() is banker's rounding)."""
    return int(math.floor(v + 0.5))


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    """Smooth ease in/out on 0..1."""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


# --- masks ---------------------------------------------------------------------
def oval(x0, y0, x1, y1):
    """Ellipse filling the inclusive pixel box (stable extents)."""
    return ell((x0 + x1 + 1) / 2.0, (y0 + y1 + 1) / 2.0, (x1 - x0 + 1) / 2.0, (y1 - y0 + 1) / 2.0)


def disc(cx, cy, r):
    """Disc centred on the middle of pixel (cx, cy)."""
    cx, cy = rnd(cx), rnd(cy)
    return ell(cx + 0.5, cy + 0.5, r, r)


def rect(x0, y0, x1, y1):
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}


BRUSH = {
    1: ((0, 0),),
    2: ((0, 0), (1, 0), (0, 1), (1, 1)),
    3: ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)),
    4: tuple((x, y) for x in range(-1, 3) for y in range(-1, 3) if (x, y) not in ((-1, -1), (2, -1), (-1, 2), (2, 2))),
    5: tuple((x, y) for x in range(-2, 3) for y in range(-2, 3) if abs(x) + abs(y) < 4),
}


def bezier(p0, c, p1, n=48):
    out = []
    for i in range(n + 1):
        t = i / float(n)
        a = (1 - t) * (1 - t)
        b = 2 * t * (1 - t)
        d = t * t
        out.append((a * p0[0] + b * c[0] + d * p1[0], a * p0[1] + b * c[1] + d * p1[1]))
    return out


def stroke(points, w=3):
    """Constant-width stroke through a list of float points."""
    out = set()
    brush = BRUSH[w]
    last = None
    for (x, y) in points:
        q = (rnd(x), rnd(y))
        if q == last:
            continue
        last = q
        for (a, b) in brush:
            out.add((q[0] + a, q[1] + b))
    return out


def bend_ctrl(a, b, bend):
    """Control point so the curve a->b bows `bend` px sideways.

    The normal is (b - a) turned so that, for a limb pointing down, a positive
    bend bows towards +x (forward).
    """
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy) or 1.0
    nx, ny = dy / d, -dx / d
    return ((a[0] + b[0]) / 2.0 + nx * bend * 2.0, (a[1] + b[1]) / 2.0 + ny * bend * 2.0)


def slack(a, b, length):
    """How far a hose of rest `length` has to bow to span a..b (0 when stretched)."""
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    if d >= length:
        return 0.0
    return math.sqrt(3.0 * max(d, 1.0) * (length - d) / 8.0)


def hose(a, b, bend=0.0, w=3):
    return stroke(bezier(a, bend_ctrl(a, b, bend), b), w)


def noodle(a, b, length, side=1, w=3, extra=0.0):
    """Rubber limb of a rest length: straight when stretched, bows when slack."""
    return hose(a, b, side * (slack(a, b, length) + extra), w)


def rot_px(fn, ox, oy, ang_deg, radius):
    """Rasterise a shape given in local coordinates, rotated around (ox, oy).

    fn(u, v) -> colour or None, with u forward and v up before rotation.
    A positive angle turns the forward axis downwards on screen (clockwise).
    """
    a = math.radians(ang_deg)
    fx, fy = math.cos(a), math.sin(a)
    ux, uy = math.sin(a), -math.cos(a)
    out = {}
    for y in range(int(math.floor(oy - radius)), int(math.ceil(oy + radius)) + 1):
        for x in range(int(math.floor(ox - radius)), int(math.ceil(ox + radius)) + 1):
            dx, dy = x + 0.5 - ox, y + 0.5 - oy
            c = fn(dx * fx + dy * fy, dx * ux + dy * uy)
            if c is not None:
                out[(x, y)] = c
    return out


def rot_pt(u, v, ox, oy, ang_deg):
    a = math.radians(ang_deg)
    return (ox + u * math.cos(a) + v * math.sin(a), oy + u * math.sin(a) - v * math.cos(a))


# --- shading ---------------------------------------------------------------------
def shade_px(px, ramps, depth=(3, 2), rim=True):
    """Turn a dict pixel -> material key into colours with four tones.

    ramps[key] is (deep shadow, shadow, base, highlight) or one flat colour.
    Light comes from the upper left: a highlight line on that edge, a shadow
    band on the lower right with a deep core, and a rim light on the last
    pixel before the outline. The bands follow the whole silhouette.
    """
    mask = set(px)
    shadow = mask - shift(mask, -depth[0], -depth[1])
    edge = mask - shift(mask, -1, -1)
    deep = mask - shift(mask, -2, -2)
    if rim:
        deep = deep - edge
    light = (mask - shift(mask, 1, 1)) - shadow
    out = {}
    for q, key in px.items():
        r = ramps[key]
        if isinstance(r[0], int):
            out[q] = r
        elif q in deep:
            out[q] = r[0]
        elif q in shadow:
            out[q] = r[1]
        elif q in light:
            out[q] = r[3]
        else:
            out[q] = r[2]
    return out


def shade_mask(mask, ramp, depth=(3, 2), rim=True):
    return shade_px({q: 0 for q in mask}, {0: ramp}, depth, rim)


# --- canvas ----------------------------------------------------------------------
class Cv:
    def __init__(self):
        self.px = {}

    def blob(self, mask, col, ink=INK):
        """Stamp a flat part with a 1 px outline."""
        for (x, y) in mask:
            for ax, ay in N4:
                q = (x + ax, y + ay)
                if q not in mask:
                    self.px[q] = ink
        for q in mask:
            self.px[q] = col

    def blob_px(self, pixels, ink=INK):
        """Stamp a multi-colour part (dict) with a 1 px outline."""
        for (x, y) in pixels:
            for ax, ay in N4:
                q = (x + ax, y + ay)
                if q not in pixels:
                    self.px[q] = ink
        self.px.update(pixels)

    def shaded(self, mask, ramp, depth=(3, 2), rim=True, ink=INK):
        """Stamp a part in four tones with a 1 px outline."""
        self.blob_px(shade_mask(mask, ramp, depth, rim), ink)

    def thicken(self, w, h, ymax=None):
        """Second pixel of ink around the whole silhouette (2 px outer contour)."""
        ymax = h - 1 if ymax is None else ymax
        add = set()
        for (x, y) in self.px:
            for ax, ay in N4:
                q = (x + ax, y + ay)
                if q not in self.px and 0 <= q[0] < w and 0 <= q[1] <= ymax:
                    add.add(q)
        for q in add:
            self.px[q] = INK

    def fill(self, mask, col, within=None):
        for q in mask:
            if within is None or q in within:
                self.px[q] = col

    def dots(self, points, col, ox=0, oy=0):
        for (x, y) in points:
            self.px[(x + ox, y + oy)] = col

    def erase(self, mask):
        for q in mask:
            self.px.pop(q, None)

    def merge(self, other, dx=0, dy=0):
        for (x, y), c in other.px.items():
            self.px[(x + dx, y + dy)] = c

    def bbox(self):
        xs = [p[0] for p in self.px]
        ys = [p[1] for p in self.px]
        return min(xs), min(ys), max(xs), max(ys)

    def image(self, w, h, name="", strict=True):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for (x, y), c in self.px.items():
            if 0 <= x < w and 0 <= y < h:
                img.putpixel((x, y), (c[0], c[1], c[2], 255))
            elif os.environ.get("ANIM_LENIENT"):      # review aid: clip and report instead of failing
                print("warning: %s: pixel (%d, %d) outside the %dx%d frame" % (name, x, y, w, h))
            elif strict:
                raise ValueError("%s: pixel (%d, %d) outside the %dx%d frame" % (name, x, y, w, h))
        return img


# --- gloves (shared by the player and the robot) -----------------------------------
def glove(cv, pos, direction, kind="fist", r=5.0, thumb=1):
    """Puffy white cartoon glove at `pos`; `direction` points from the wrist to
    the fingers. Rolled cuff, thumb, three ink lines on the back."""
    x, y = rnd(pos[0]), rnd(pos[1])
    d = math.hypot(direction[0], direction[1]) or 1.0
    dx, dy = direction[0] / d, direction[1] / d
    px_, py_ = -dy, dx
    big = r >= 4.5
    half = r * 0.75
    cxw, cyw = x - dx * (r + 1.0), y - dy * (r + 1.0)
    cuff = stroke([(cxw + px_ * half * k / 8.0, cyw + py_ * half * k / 8.0) for k in range(-8, 9)], 3 if big else 2)
    cv.shaded(cuff, GLOVE_RAMP, (1, 1), False)
    fw = 3 if big else 2
    if kind == "open":
        for ang in (-38, 0, 38):
            a = math.radians(ang)
            fx = dx * math.cos(a) - dy * math.sin(a)
            fy = dx * math.sin(a) + dy * math.cos(a)
            n = int(r + 4)
            finger = stroke([(x + fx * (r - 1.5 + k * 0.5), y + fy * (r - 1.5 + k * 0.5)) for k in range(n)], fw)
            cv.shaded(finger, GLOVE_RAMP, (1, 1), False)
    elif kind == "point":
        n = int(r + 8)
        finger = stroke([(x + dx * (r - 1.5 + k * 0.5), y + dy * (r - 1.5 + k * 0.5)) for k in range(n)], fw)
        cv.shaded(finger, GLOVE_RAMP, (1, 1), False)
    if thumb:
        cv.shaded(disc(x + px_ * thumb * (r - 0.6) + dx * 0.8, y + py_ * thumb * (r - 0.6) + dy * 0.8, 2.0 if big else 1.4),
                  GLOVE_RAMP, (1, 1), False)
    cv.shaded(disc(x, y, r), GLOVE_RAMP, (2, 1), False)
    # the three lines on the back of the hand
    lines = (-1, 0, 1) if big else (-0.6, 0.6)
    for s_ in lines:
        for k in ((-3.4, -2.4, -1.4) if big else (-1.8, -0.8)):
            cv.px[(rnd(x + px_ * s_ * 2.0 + dx * k), rnd(y + py_ * s_ * 2.0 + dy * k))] = INK_SOFT


def ribbed_hose(cv, a, b, bend, w=3, dark=None, light=None, pitch=2.0):
    """A corrugated hose: rings of two tones along the curve, inked."""
    dark = dark or GREY[1]
    light = light or GREY[3]
    pts = bezier(a, bend_ctrl(a, b, bend), b, 64)
    cv.blob(stroke(pts, w), dark)
    run, last = 0.0, pts[0]
    for (x, y) in pts:
        run += math.hypot(x - last[0], y - last[1])
        last = (x, y)
        if int(run / pitch) % 2 == 0:
            for (ax, ay) in BRUSH[w]:
                cv.px[(rnd(x) + ax, rnd(y) + ay)] = light
    return pts


# --- shapes for effects ---------------------------------------------------------
def star_mask(cx, cy, r_out, r_in, points=4, rot=0.0):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot) + math.pi * i / points - math.pi / 2.0
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return poly(pts)


# --- sheets and previews ----------------------------------------------------------
def strip(frames):
    w, h = frames[0].size
    sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * w, 0))
    return sheet


def contact_sheet(frames, scale=3, gap=2):
    w, h = frames[0].size
    n = len(frames)
    sheet = Image.new("RGBA", (n * w * scale + (n + 1) * gap, h * scale + 2 * gap), (58, 46, 36, 255))
    for i, f in enumerate(frames):
        cell = Image.new("RGBA", (w, h), BACKDROP + (255,))
        cell.alpha_composite(f)
        cell = cell.resize((w * scale, h * scale), Image.NEAREST)
        sheet.paste(cell, (gap + i * (w * scale + gap), gap))
    return sheet.convert("RGB")


def save_gif(frames, path, fps, loop, scale=4):
    w, h = frames[0].size
    out = []
    for f in frames:
        cell = Image.new("RGBA", (w, h), BACKDROP + (255,))
        cell.alpha_composite(f)
        out.append(cell.resize((w * scale, h * scale), Image.NEAREST).convert("P", palette=Image.ADAPTIVE, colors=64))
    ms = max(20, int(round(1000.0 / fps / 10.0)) * 10)
    durations = [ms] * len(out)
    if not loop:
        durations[-1] = 900  # hold the last frame so one-shots are readable in review
    out[0].save(path, save_all=True, append_images=out[1:], duration=durations, loop=0, disposal=2)
