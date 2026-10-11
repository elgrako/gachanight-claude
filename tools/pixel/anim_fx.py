"""Effects and small objects: coins, capsule opening, sparkles, bursts, zzz,
lamp flicker and the CRT screen glow.

Light effects are drawn by per-pixel tests around a half-pixel centre so they
stay perfectly symmetric; timing is fast expansion followed by a slower fade.
"""
import math
import os
import random

from PIL import Image

from anim_lib import (Layer, glyph, rnd, INK, DARK, CREAM, CREAM_SH, WHITE, CORAL, CORAL_HI, CORAL_SH,
                      MINT, MINT_HI, MINT_SH, MUSTARD, MUSTARD_HI, MUSTARD_SH, TEAL, TEAL_HI, TEAL_SH,
                      BATH_MINT, GOLD_HI, SCREEN_BG, SCREEN_BAND, TUBE_OFF)


# --- generic light shapes ------------------------------------------------------
def star(layer, cx, cy, arm, core, c, diag=0):
    """Four-point twinkle: 2 px wide arms of length `arm`, diamond core, optional diagonal arms."""
    r = int(max(arm, core, diag) + 2)
    for y in range(int(cy) - r, int(cy) + r + 2):
        for x in range(int(cx) - r, int(cx) + r + 2):
            dx, dy = abs(x - cx), abs(y - cy)
            if (dx < 1 and dy <= arm) or (dy < 1 and dx <= arm) or dx + dy <= core:
                layer.px[(x, y)] = c
            elif diag and abs(dx - dy) < 0.5 and dx <= diag:
                layer.px[(x, y)] = c


def burst(layer, cx, cy, c, disc=0.0, ring=None, rays=None, box=48, mask=None):
    """disc radius; ring (radius, thickness); rays (r0, r1, half_width, count, rotation_deg)."""
    for y in range(box):
        for x in range(box):
            dx, dy = x - cx, y - cy
            d = math.hypot(dx, dy)
            hit = d <= disc
            if not hit and ring and abs(d - ring[0]) <= ring[1] / 2.0:
                hit = mask is None or mask(math.degrees(math.atan2(dy, dx)) % 360.0)
            if not hit and rays and rays[0] <= d <= rays[1]:
                r0, r1, hw, count, rot = rays
                step = 360.0 / count
                ang = (math.degrees(math.atan2(dy, dx)) - rot) % step
                ang = min(ang, step - ang)
                taper = 1.0 - 0.7 * (d - r0) / max(0.001, r1 - r0)
                hit = d * math.sin(math.radians(ang)) <= hw * taper
            if hit:
                layer.px[(x, y)] = c


# --- coin -------------------------------------------------------------------------
COIN_ROWS = [4, 6, 8, 8, 8, 8, 6, 4]


def coin(layer, ox, oy, w, rim=0):
    """Coin with fill 8 px tall and `w` px wide inside a 10 x 10 box at (ox, oy). rim: -1 left, 1 right."""
    for r, full in enumerate(COIN_ROWS):
        rw = max(1 if w < 4 else 2, rnd(full * w / 8.0))
        rw = min(rw, w)
        x0 = ox + 1 + (8 - rw) // 2
        for i in range(rw):
            if r >= 6 or (i == rw - 1 and r >= 2):
                c = MUSTARD_SH
            elif r <= 0 or (i == 0 and r <= 5):
                c = MUSTARD_HI
            else:
                c = MUSTARD
            if rim == 1 and i == rw - 1 and rw > 2:
                c = MUSTARD_SH
            if rim == -1 and i == 0 and rw > 2:
                c = MUSTARD_SH
            layer.px[(x0 + i, oy + 1 + r)] = c
    if w >= 6:
        # square hole, like an old five-yen coin, and a glint
        layer.px[(ox + 4, oy + 4)] = MUSTARD_SH
        layer.px[(ox + 5, oy + 4)] = MUSTARD_SH
        layer.px[(ox + 4, oy + 5)] = MUSTARD_SH
        layer.px[(ox + 5, oy + 5)] = MUSTARD_HI
        layer.px[(ox + (3 if w == 8 else 4), oy + 2)] = WHITE
    elif w == 4:
        layer.px[(ox + 4 if rim == 1 else ox + 5, oy + 4)] = MUSTARD_SH
        layer.px[(ox + 4 if rim == 1 else ox + 5, oy + 5)] = MUSTARD_SH
    else:
        for r in range(1, 7):
            layer.px[(ox + 4, oy + 1 + r)] = MUSTARD_HI


COIN_SEQ = [(8, 0), (6, 1), (4, 1), (2, 0), (4, -1), (6, -1)]


def coin_spin():
    frames = []
    for i, (w, rim) in enumerate(COIN_SEQ):
        lay = Layer()
        coin(lay, 0, 0, w, rim)
        frames.append(lay.outlined().to_image(10, 10, name="coin_spin[%d]" % i))
    return frames, 10, True


def coin_pickup():
    frames = []
    cx, cy = 7.5, 6.5
    rises = [0, 6, 10, 12, 13]                 # fast pop, eased at the top
    for i, up in enumerate(rises):
        lay = Layer()
        w, rim = COIN_SEQ[(i * 2) % 6] if i < 4 else (2, 0)
        coin(lay, 3, 14 - up, w, rim)
        lay = lay.outlined()
        if i == 1:
            for p in ((5, 21), (10, 21), (7, 23), (8, 22)):   # dust kicked at the start
                lay.px[p] = CREAM
        frames.append(lay)
    fx = [dict(arm=6, core=2.5, diag=0),
          dict(arm=5, core=1.5, diag=3),
          dict(arm=3, core=0, diag=0),
          None]
    for i, f in enumerate(fx):
        lay = Layer()
        if f:
            star(lay, cx, cy, f["arm"], f["core"], WHITE, f["diag"])
            if i == 0:
                star(lay, cx, cy, 2, 1.5, GOLD_HI)
            if i == 2:
                for p in list(lay.px):
                    if abs(p[0] - cx) < 2 and abs(p[1] - cy) < 2:
                        del lay.px[p]
        if i >= 1:
            d = 4 + i
            for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                lay.px[(int(cx + sx * d * 0.8 + 0.5), int(cy + sy * d * 0.8 + 0.5 + (i - 1)))] = GOLD_HI
        frames.append(lay)
    return [f.to_image(16, 24, name="coin_pickup") for f in frames], 16, False


# --- sparkle ------------------------------------------------------------------------
def sparkle():
    c = 7.5
    specs = [dict(arm=0.5, core=0.6),
             dict(arm=3, core=1.5),
             dict(arm=7, core=3, tip=True),
             dict(arm=6, core=1.5, diag=3),
             dict(arm=4, core=0, hole=1),
             dict(arm=6, core=0, hole=4)]
    frames = []
    for s in specs:
        lay = Layer()
        star(lay, c, c, s["arm"], s["core"], WHITE, s.get("diag", 0))
        if s.get("tip"):
            star(lay, c, c, 2, 2.5, GOLD_HI)
            star(lay, c, c, 0.5, 1.2, WHITE)
        if "hole" in s:
            for p in list(lay.px):
                if max(abs(p[0] - c), abs(p[1] - c)) < s["hole"]:
                    del lay.px[p]
        frames.append(lay.to_image(16, 16, name="sparkle"))
    return frames, 14, False


# --- rarity burst (pure white, tinted by the game) -------------------------------------
def rarity_burst():
    c = 23.5
    rng = random.Random(7)
    dots = []
    for k in range(16):
        a = (k + rng.uniform(-0.3, 0.3)) * 2 * math.pi / 16
        dots.append((a, rng.uniform(9, 15), (k * 5) % 3))

    def dashes(n, duty):
        return lambda deg: (deg % (360.0 / n)) < (360.0 / n) * duty

    specs = [dict(disc=3.5),
             dict(disc=9, rays=(8, 16, 2.4, 8, 0)),
             dict(disc=6, ring=(14, 3.5), rays=(13, 23, 2.2, 8, 0)),
             dict(ring=(18.5, 2.2), rays=(17, 24, 1.6, 8, 22.5)),
             dict(ring=(21, 1.4), rays=(21, 24, 1.0, 16, 0), dots=(1.25, 0)),
             dict(ring=(22.5, 1.2), mask=dashes(12, 0.5), dots=(1.42, 0)),
             dict(dots=(1.52, 1)),
             dict(dots=(1.58, 2))]
    frames = []
    for s in specs:
        lay = Layer()
        burst(lay, c, c, WHITE, s.get("disc", 0), s.get("ring"), s.get("rays"), 48, s.get("mask"))
        if "dots" in s:
            scale, drop = s["dots"]
            for a, r, kind in dots:
                if kind < drop:
                    continue
                x = int(c + math.cos(a) * r * scale)
                y = int(c + math.sin(a) * r * scale)
                if not (1 <= x <= 46 and 1 <= y <= 46):
                    continue
                lay.px[(x, y)] = WHITE
                if kind == 2 and drop < 2:
                    for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        lay.px[(x + ax, y + ay)] = WHITE
        frames.append(lay.to_image(48, 48, name="rarity_burst"))
    return frames, 16, False


# --- capsule opening --------------------------------------------------------------------
CAPSULE_COLOURS = {
    "coral": (CORAL, CORAL_HI, CORAL_SH),
    "mint": (MINT, MINT_HI, MINT_SH),
    "mustard": (MUSTARD, MUSTARD_HI, MUSTARD_SH),
    "teal": (TEAL, TEAL_HI, TEAL_SH),
    "gold": (MUSTARD_HI, GOLD_HI, MUSTARD),
}
CAP_R = 5.3


def _capsule_px(dx, dy, cols, seam_glow=False):
    """Colour of a capsule pixel at offset (dx, dy) from its centre (dy < 0 is the clear half)."""
    base, hi, sh = cols
    if dy < 0:
        if -1 < dy and seam_glow:
            return WHITE
        if dx < -1 and dy < -2 and dx * dx + dy * dy < 18:
            return WHITE
        if dx > 2.5 or (dx > 1 and dy > -2):
            return CREAM_SH if dx > 3.5 else BATH_MINT
        return BATH_MINT
    if dy < 1:
        return WHITE if seam_glow else sh
    if dx < -2 and dy < 3.5:
        return hi
    if dx * 0.7 + dy > 4.2:
        return sh
    return base


def _capsule(cols, cx, cy, sx=1.0, sy=1.0, tilt=0, glow=False):
    lay = Layer()
    for y in range(int(cy - 10), int(cy + 10)):
        for x in range(int(cx - 10), int(cx + 10)):
            dy = (y - cy) / sy
            dx = (x - cx - tilt * (cy - y) / 5.0) / sx
            if dx * dx + dy * dy <= CAP_R * CAP_R:
                lay.px[(x, y)] = _capsule_px(dx, dy, cols, glow)
    return lay.outlined()


def _half(cols, cx, cy, top, angle):
    """One capsule half, rotated by `angle` degrees, as an outlined layer."""
    a = math.radians(angle)
    lay = Layer()
    for y in range(int(cy - 9), int(cy + 9)):
        for x in range(int(cx - 9), int(cx + 9)):
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy > CAP_R * CAP_R:
                continue
            # rotate into the capsule's own frame
            lx = dx * math.cos(a) + dy * math.sin(a)
            ly = -dx * math.sin(a) + dy * math.cos(a)
            if top and ly < -0.5:
                lay.px[(x, y)] = _capsule_px(lx, ly, cols)
            elif not top and ly > 0.5:
                lay.px[(x, y)] = _capsule_px(lx, ly + 0.6, cols)
    return lay.outlined()


def capsule_open(colour="coral"):
    cols = CAPSULE_COLOURS[colour]
    cx, cy = 15.5, 16.5
    frames = []

    def add(*layers):
        lay = Layer()
        for l in layers:
            lay.merge(l)
        frames.append(lay.to_image(32, 32, strict=False))

    add(_capsule(cols, cx, cy))
    add(_capsule(cols, cx - 1, cy, tilt=-1))
    add(_capsule(cols, cx + 1, cy, tilt=1))
    add(_capsule(cols, cx - 2, cy, tilt=-2))
    add(_capsule(cols, cx + 2, cy, tilt=2))
    add(_capsule(cols, cx, cy + 1, sx=1.2, sy=0.84, glow=True))         # squash: anticipation

    def light(**kw):
        lay = Layer()
        if "gold" in kw:
            burst(lay, cx, cy, GOLD_HI, kw["gold"], None, kw.get("grays"), 32)
        burst(lay, cx, cy, WHITE, kw.get("disc", 0), kw.get("ring"), kw.get("rays"), 32, kw.get("mask"))
        for sx, sy, arm in kw.get("stars", ()):
            star(lay, sx + 0.5, sy + 0.5, arm, 0 if arm < 2 else 1.5, WHITE)
        for p in kw.get("dots", ()):
            lay.px[p] = GOLD_HI
        return lay

    # pop: halves jump apart, white core
    add(light(disc=4.5, rays=(4, 9, 1.6, 8, 0)),
        _half(cols, cx, cy - 3, True, -6), _half(cols, cx, cy + 2, False, 4))
    # burst: biggest frame
    add(light(gold=10.5, disc=8, rays=(8, 16, 2.4, 8, 0)),
        _half(cols, cx - 4, cy - 9, True, -28), _half(cols, cx + 3, cy + 6, False, 18))
    add(light(gold=6.5, disc=4.5, ring=(11.5, 2.0), rays=(11, 16.5, 1.5, 8, 22.5)),
        _half(cols, cx - 8, cy - 13, True, -55), _half(cols, cx + 6, cy + 11, False, 40))
    add(light(disc=2.5, ring=(14, 1.2), mask=lambda d: (d % 30) < 15,
              stars=((6, 8, 3), (25, 11, 2), (9, 25, 2), (23, 24, 3))),
        _half(cols, cx - 12, cy - 13, True, -80), _half(cols, cx + 9, cy + 17, False, 60))
    add(light(stars=((5, 6, 2), (26, 9, 3), (8, 26, 3), (24, 26, 2), (15, 16, 1)),
              dots=((3, 12), (28, 18), (16, 4), (17, 29))))
    add(light(stars=((26, 8, 1), (8, 27, 1)), dots=((4, 5), (25, 27), (2, 13), (29, 19), (16, 2))))
    return frames, 14, False


# --- zzz ---------------------------------------------------------------------------------
Z_GLYPHS = [["###", ".#.", "###"],
            ["####", "..#.", ".#..", "####"],
            ["#####", "...#.", "..#..", ".#...", "#####"]]


def zzz():
    frames = []
    n = 6                      # frames between two letters; two letters are alive at once
    for f in range(n):
        out = Layer()
        for i in range(2):
            p = (f + i * n) / (2.0 * n)                 # 0..1 along the path
            size = 0 if p < 0.3 else (1 if p < 0.6 else 2)
            half = (size + 3) / 2.0
            x = rnd(3.5 + 8.0 * p + math.sin(p * math.pi * 2) * 0.8 - half)
            y = rnd(12.5 - 9.0 * p - half)
            if p < 0.04:
                lay = Layer()
                lay.px[(x + 1, y + 1)] = CREAM
                out.stamp(lay)
                continue
            lay = glyph(Z_GLYPHS[size], {"#": WHITE if size == 2 else CREAM}, x, y)
            if p > 0.93:
                # last frame of a letter: it breaks up instead of popping out
                for q in list(lay.px):
                    if (q[0] + q[1]) % 2:
                        del lay.px[q]
                out.merge(lay)
            else:
                out.stamp(lay)
        frames.append(out.to_image(16, 16, name="zzz[%d]" % f))
    return frames, 5, True


# --- lamp flicker --------------------------------------------------------------------------
def _own_lamp(lit):
    lay = Layer()
    body = Layer()
    body.rect(3, 4, 28, 5, CREAM_SH)
    body.rect(3, 4, 28, 4, CREAM)
    body.rect(3, 6, 4, 8, DARK)
    body.rect(27, 6, 28, 8, DARK)
    body.rect(5, 6, 26, 8, WHITE if lit else TUBE_OFF)
    if lit:
        body.rect(5, 8, 26, 8, GOLD_HI)
    else:
        body.rect(5, 6, 26, 6, BATH_MINT)
    lay.stamp(body)
    for x in (8, 23):
        lay.rect(x, 0, x, 2, INK)
    return lay.to_image(32, 12, name="lamp")


def lamp_flicker(props_dir=None):
    off = on = None
    source = "own"
    if props_dir:
        p_off = os.path.join(props_dir, "ceiling_lamp_off.png")
        p_on = os.path.join(props_dir, "ceiling_lamp_on.png")
        if os.path.exists(p_off) and os.path.exists(p_on):
            a, b = Image.open(p_off).convert("RGBA"), Image.open(p_on).convert("RGBA")
            if a.size == (32, 12) and b.size == (32, 12):
                off, on, source = a, b, "props"
    if off is None:
        off, on = _own_lamp(False), _own_lamp(True)
    # "ends": only the two tube ends glow, the classic fluorescent start-up
    ends = off.copy()
    ends.paste(on.crop((0, 0, 9, 12)), (0, 0))
    ends.paste(on.crop((23, 0, 32, 12)), (23, 0))
    left = off.copy()
    left.paste(on.crop((0, 0, 16, 12)), (0, 0))
    seq = [off, ends, off, off, on, ends, off, left, on, off, on, on]
    return [f.copy() for f in seq], 14, False, source


# --- CRT screen glow ---------------------------------------------------------------------------
SCREEN_TEXT = [(4, 5, 12), (6, 5, 9), (8, 5, 15), (10, 5, 11)]   # (row, x0, x1)


def screen_glow():
    frames = []
    n = 6
    for f in range(n):
        lay = Layer()
        band = 2 + rnd(f * 13.0 / n)
        for y in range(2, 15):
            for x in range(3, 21):
                if (x in (3, 20)) and (y in (2, 14)):
                    continue
                lit = y in (band, band + 1) or y == band - 13 + 1
                lay.px[(x, y)] = SCREEN_BAND if lit else SCREEN_BG
        for row, x0, x1 in SCREEN_TEXT:
            bright = row in (band, band + 1)
            for x in range(x0, x1 + 1):
                if (x + row) % 5 == 0:
                    continue                     # gaps between "words"
                lay.px[(x, row)] = MINT_HI if bright else MINT
        # prompt and blinking cursor on the last line
        lay.px[(5, 12)] = MINT
        lay.px[(6, 12)] = MINT
        if f < n // 2:
            lay.rect(8, 12, 9, 12, WHITE)
        frames.append(lay.to_image(24, 22, name="screen_glow[%d]" % f))
    return frames, 8, True
