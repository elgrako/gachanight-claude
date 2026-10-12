"""Rubber-hose machines for GachaNight (art contract v2, section A).

Every machine is assembled from posable parts (cap, globe with balls, base,
crank plate, chute, noodle arms, gloves, eyes) by one drawing function that
takes a pose. Animation frames are re-poses of the same parts with integer
parameters, so volumes stay stable and nothing flickers.

View: raised oblique camera (front of the object plus its top). Everything
is anchored at the bottom centre of its canvas; the last row is the outline
that touches the floor.
"""
import math

from pixlib import Spr, hx, ell, box, poly, line

# ------------------------------------------------------------------ palette

INK = hx("161320")
RED = hx("e2231a")
DRED = hx("9c1420")
ORANGE = hx("f0802a")
MUSTARD = hx("f2b632")
CREAM = hx("f6e7c1")
PAPER = hx("fff8e3")
NAVY = hx("1f3a8a")
BLUE = hx("2f7de1")
SKY = hx("9fd3f5")
GREEN = hx("2e9e4f")
STEEL = hx("8a93a3")
DSTEEL = hx("4a5160")
GLOVE = hx("fffdf5")
PINK = hx("f59ab5")
# sparing extensions (one shadow / one highlight for hues the contract lacks)
LRED = hx("ff7a5c")      # highlight on red
DGREEN = hx("1c6b3c")    # shadow on green
LGREEN = hx("7fd66b")    # highlight on green
DMUST = hx("c07a1e")     # shadow on mustard
LMUST = hx("ffe08a")     # highlight on mustard
DNAVY = hx("14245c")     # shadow on navy
DPINK = hx("cf5f86")     # shadow on pink
LPINK = hx("ffd0dc")     # highlight on pink
DORANGE = hx("b8521c")   # shadow on orange
LSTEEL = hx("c9d0da")    # highlight on steel
DSKY = hx("6fb1e4")      # shadow on glass
OFFSKY = hx("86b2d4")    # unpowered glass
OFFDSKY = hx("6492bb")   # unpowered glass shadow
DCREAM = hx("d6c49c")    # shadow on cream / glove
HOLE = hx("2b2838")      # inner wall of chutes and holes
GOLD = hx("ffd84a")      # gold capsule
OFFCREAM = hx("e6d6ae")  # unpowered plinko board ray

# name -> (base, shadow, highlight)
BODY = {
    "red": (RED, DRED, LRED),
    "green": (GREEN, DGREEN, LGREEN),
    "mustard": (MUSTARD, DMUST, LMUST),
    "blue": (BLUE, NAVY, SKY),
    "navy": (NAVY, DNAVY, BLUE),
    "pink": (PINK, DPINK, LPINK),
}

BALL = {
    "R": (RED, DRED), "Y": (MUSTARD, DMUST), "B": (BLUE, NAVY), "G": (GREEN, DGREEN),
    "W": (GLOVE, DCREAM), "P": (PINK, DPINK), "O": (ORANGE, DORANGE),
}

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def edge(m):
    """Pixels just outside a mask (4-neighbourhood): its outline."""
    out = set()
    for (x, y) in m:
        for a, b in N4:
            q = (x + a, y + b)
            if q not in m:
                out.add(q)
    return out


def rows_mask(rows, cx):
    """rows: {y: half_width}; symmetric span around the centre line cx."""
    return {(x, y) for y, hw in rows.items() for x in range(cx - hw, cx + hw)}


class Cv(Spr):
    """Canvas with outlined hard-edged shapes and string stamps."""

    def shape(self, m, c, sh=None, shc=None, hl=None, hlc=None, ink=INK):
        self.puts(edge(m), ink)
        self.puts(m, c)
        if sh:
            self.puts(m & sh, shc)
        if hl:
            self.puts(m & hl, hlc)

    def stamp(self, rows, x, y, pal, flip=False):
        for j, row in enumerate(rows):
            if flip:
                row = row[::-1]
            for i, ch in enumerate(row):
                if ch != ".":
                    self.put(x + i, y + j, pal[ch])

    def paste_mask(self, other, mask):
        for (x, y) in mask:
            v = other.get(x, y)
            if v is not None:
                self.put(x, y, v)


# ------------------------------------------------------------------ eyes

def eye_pair(s, cx, top, w, h, state, look=0):
    """Two tall-oval eyes touching each other, pupils resting to one side.

    cx is the ink column between the eyes, top the first row of the whites.
    States: open, wide, half, closed (asleep), happy, wink (right eye shut).
    look: -1 / 0 / 1 or (lx, ly). lx = 0 makes the pupils converge (a look
    straight at the viewer) so the eyes never read as a pair of zeros;
    ly = 1 looks down at the floor in front, ly = -1 up.
    """
    lx, ly = look if isinstance(look, tuple) else (look, 0)
    big = w >= 5
    for k, x0 in enumerate((cx - w, cx + 1)):
        st = state
        if state == "wink":
            st = "happy" if k == 1 else "open"
        if st in ("closed", "happy"):
            r = top + h // 2
            a, b = (r, r + 1) if st == "closed" else (r + 1, r)
            s.put(x0, a, INK)
            s.put(x0 + w - 1, a, INK)
            for x in range(x0 + 1, x0 + w - 1):
                s.put(x, b, INK)
            continue
        y0, y1 = top, top + h - 1
        if st == "wide":
            y0 -= 1
        white = box(x0, y0, x0 + w - 1, y1, 2 if big else 0)
        if st == "half":
            y0 = top + h // 2 - (1 if big else 0)
            white = {q for q in white if q[1] >= y0}
        s.puts(edge(white), INK)
        s.puts(white, GLOVE)
        if big:
            pw, ph = 3, h - 4
            if st == "wide":
                ph = h - 6
            px = (x0, (x0 + w - pw - 1) if k == 0 else (x0 + 1), x0 + w - pw)[lx + 1]
            if st == "wide":
                py = (y0 + y1 + 1 - ph) // 2
            elif ly > 0:
                py = y1 - ph + 1
                if lx == 0:               # straight down: white above and beside
                    px = x0 + (2 if k == 0 else 1)
            elif ly < 0:
                py = y0 + 1
            else:
                py = y1 - ph
            pupil = box(px, py, px + pw - 1, py + ph - 1, 1 if pw == 3 else 0) & white
            s.puts(pupil, INK)
            if st != "half" and pw == 3:
                s.put(px + 1, py + 1, GLOVE)          # glint
        else:
            px = (x0, (x0 + w - 1) if k == 0 else x0, x0 + w - 1)[lx + 1]
            if st == "wide":
                mid = (y0 + y1) // 2
                rows = (mid, mid + 1)
            else:
                if st == "half":
                    rows = range(y0, y1)
                elif ly > 0:
                    rows = range(y1 - 2, y1 + 1)
                elif ly < 0:
                    rows = range(y0, y0 + 3)
                else:
                    rows = range(y0 + 1, y1)
            for y in rows:
                s.put(px, y, INK)


# ------------------------------------------------------------------ arms and gloves

GLOVE_PAL = {"K": INK, "W": GLOVE, "S": DCREAM}

# All gloves are written for the LEFT arm (thumb towards the body, on the right).
_DOWN_TOP = [
    "..KKKKK...",
    ".KWWWWSK..",
    "..KKKKK...",
    ".KWWWWWK..",
    "KWWWWWWWKK",
    "KWWWWWWKWK",
]
GLOVES = {
    # hanging hand with a rolled cuff; wrist at the top
    "down": (_DOWN_TOP + [
        "KWWKWKWWKK",
        "KWWKWKWSK.",
        ".KKKKKKK..",
    ], (4, 0)),
    # the same hand drumming: outer finger down / middle finger down
    "drum_a": (_DOWN_TOP + [
        "KWWKWKWWKK",
        "KWWKWKWSK.",
        "KWWKKKKK..",
        ".KK.......",
    ], (4, 0)),
    "drum_b": (_DOWN_TOP + [
        "KWWKWKWWKK",
        "KWWKWKWSK.",
        ".KKKWKKK..",
        "....K.....",
    ], (4, 0)),
    # raised open hand, fingers up; wrist at the bottom
    "open": ([
        ".K.K.K..",
        "KWKWKWK.",
        "KWKWKWK.",
        "KWWWWWKK",
        "KWWWWWWK",
        "KWWWWWK.",
        ".KWWWSK.",
        ".KKKKK..",
        "KWWWWSK.",
        ".KKKKK..",
    ], (3, 9)),
    # hand flicked outwards (wave); wrist at the bottom right
    "wave": ([
        ".K.K......",
        "KWKWK.K...",
        "KWKWKKWK..",
        "KWWWWWWK..",
        "KWWWWWWKK.",
        ".KWWWWWWWK",
        "..KWWWSKK.",
        "...KKKKWK.",
        "....KWWWK.",
        ".....KKK..",
    ], (6, 9)),
    # closed fist that grabs the crank; wrist on the left
    "fist": ([
        ".K.KKKKKK.",
        "KWKWWWWWWK",
        "KWKWWKWKWK",
        "KWKSWKWKWK",
        "KWKSSWWWWK",
        ".K.KKKKKK.",
    ], (0, 3)),
}


def bez(pts, t):
    pts = [(float(p[0]), float(p[1])) for p in pts]
    while len(pts) > 1:
        pts = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(pts, pts[1:])]
    return pts[0]


def noodle(pts):
    """Constant-thickness (3 px) black arm along a Bezier curve (3 or 4 points)."""
    out = set()
    n = 72
    for i in range(n + 1):
        x, y = bez(pts, i / float(n))
        xi, yi = int(math.floor(x + 0.5)), int(math.floor(y + 0.5))
        out |= {(xi, yi), (xi + 1, yi), (xi - 1, yi), (xi, yi + 1), (xi, yi - 1)}
    return out


def mirror_pt(p, w):
    return (w - 1 - p[0], p[1])


def draw_arm(s, side, shoulder, spec, part):
    """spec = (ctrl, wrist, glove, front) in LEFT-arm coordinates.

    ctrl is one control point, or a pair of them for an S or loop shaped arm.
    part: "arm", "glove" or "both". The right arm is the mirror image.
    """
    ctrl, wrist, glove, _front = spec
    w = s.w
    if part in ("arm", "both"):
        mid = list(ctrl) if isinstance(ctrl[0], (tuple, list)) else [ctrl]
        m = noodle([shoulder] + mid + [wrist])
        if side == "R":
            m = {mirror_pt(q, w) for q in m}
        s.puts(m, INK)
    if part in ("glove", "both"):
        rows, (ax, ay) = GLOVES[glove]
        gx, gy = wrist[0] - ax, wrist[1] - ay
        if side == "R":
            gx = w - 1 - (gx + len(rows[0]) - 1)
        s.stamp(rows, gx, gy, GLOVE_PAL, flip=(side == "R"))


# ------------------------------------------------------------------ shared machine parts

HANDLE_DIRS = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))


def handle_tip(x0, y0, handle):
    dx, dy = HANDLE_DIRS[handle % 8]
    n = 4 if dx and dy else 5
    return (x0 + 5 + dx * n, y0 + 4 + dy * n)


def crank_plate(s, x0, y0, handle=0, lamp=0, glint=-1):
    """12 x 10 grey mechanism plate: rivets, dial, crank handle, pilot lamp.

    glint 0..3 slides a specular tick across the dial (idle sparkle).
    """
    m = box(x0, y0, x0 + 11, y0 + 9)
    top_left = {q for q in m if q[1] == y0 or q[0] == x0}
    bot_right = {q for q in m if q[1] == y0 + 9 or q[0] == x0 + 11}
    s.shape(m, STEEL, bot_right, DSTEEL, top_left - bot_right, LSTEEL)
    for q in ((x0 + 10, y0 + 1), (x0 + 1, y0 + 8), (x0 + 10, y0 + 8)):
        s.put(q[0], q[1], DSTEEL)
    lamp_c = (DSTEEL, MUSTARD, PAPER)[lamp]
    s.rect(x0 + 1, y0 + 1, x0 + 2, y0 + 2, lamp_c)
    if lamp == 1:
        s.put(x0 + 1, y0 + 1, PAPER)
    cx, cy = x0 + 6, y0 + 5
    dial = ell(cx, cy, 3.0, 3.0)
    s.shape(dial, LSTEEL, dial - ell(cx - 0.8, cy - 0.8, 3.0, 3.0), STEEL)
    if 0 <= glint <= 3:
        gx, gy = ((x0 + 4, y0 + 7), (x0 + 4, y0 + 6), (x0 + 5, y0 + 3), (x0 + 7, y0 + 2))[glint]
        s.put(gx, gy, PAPER)
    # handle: a pale bar from the hub to the plate edge
    dx, dy = HANDLE_DIRS[handle % 8]
    n = 4 if dx and dy else 5
    bar = set()
    for i in range(n + 1):
        px, py = x0 + 5 + dx * i, y0 + 4 + dy * i
        bar |= {(px, py), (px + 1, py), (px, py + 1), (px + 1, py + 1)}
    s.puts(edge(bar), INK)
    s.puts(bar, PAPER)
    s.rect(x0 + 5, y0 + 4, x0 + 6, y0 + 5, DSTEEL)


def chute(s, x0, y0, x1, y1):
    """Dark exit mouth with a steel frame; (x0, y0)-(x1, y1) is the frame."""
    m = box(x0, y0, x1, y1, r=1)
    top_left = {q for q in m if q[1] == y0 or q[0] == x0}
    bot_right = {q for q in m if q[1] == y1 or q[0] == x1}
    s.shape(m, STEEL, bot_right, DSTEEL, top_left - bot_right, LSTEEL)
    hole = box(x0 + 2, y0 + 2, x1 - 2, y1 - 2)
    s.puts(edge(hole) & m, INK)
    s.puts(hole, INK)
    s.rect(x1 - 3, y0 + 3, x1 - 2, y1 - 2, HOLE)      # inner right wall
    s.rect(x0 + 3, y1 - 3, x1 - 2, y1 - 2, HOLE)      # tray floor


def lamp(s, x, y, lit):
    """2 x 2 sign bulb with outline. lit: 0 off, 1 warm, 2 flash."""
    m = {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)}
    s.puts(edge(m), INK)
    s.puts(m, (DSTEEL, MUSTARD, PAPER)[lit])
    if lit == 1:
        s.put(x, y, PAPER)
    elif lit == 0:
        s.put(x, y, STEEL)


KANA = {
    "ku": [".####", ".#..#", "#...#", "...#.", ".##.."],
    "re": ["#....", "#....", "#...#", "#..#.", "###.."],
    "bar": [".....", ".....", "#####", ".....", "....."],
    "n": ["#....", ".#..#", "....#", "...#.", "###.."],
    "ra": [".###.", ".....", "#####", "....#", "..##."],
    "tsu": [".....", "#.#.#", "....#", "...#.", ".##.."],
    "ki": ["..#..", "#####", "..#..", "#####", "..#.."],
}
DIGITS = {
    1: [".#.", "##.", ".#.", ".#.", "###"],
    2: ["##.", "..#", ".#.", "#..", "###"],
    3: ["##.", "..#", ".#.", "..#", "##."],
    4: ["#.#", "#.#", "###", "..#", "..#"],
}


def glyph_rows(s, rows, x, y, c):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "#":
                s.put(x + i, y + j, c)


def kana_line(s, names, x, y, c):
    for i, name in enumerate(names):
        glyph_rows(s, KANA[name], x + i * 6, y, c)


# ------------------------------------------------------------------ capsule machines 001-004

GW, GH = 48, 84
GCX = 24                 # centre line (between pixel 23 and 24)
G_BOT = GH - 2           # last filled row; row GH-1 is the floor outline
BASE_TOP = 50
GLOBE_CY = 32
PLATE = (18, 55)         # crank plate top-left at rest
CHUTE_FRAME = (17, 65, 30, 77)
GACHA_CHUTE = (24, 72)   # centre of the resting 12 x 12 capsule

# ball layout inside the globe, back to front: (dx, dy, radius, has_eyes).
# The three balls with eyes are, in order: top right, front centre, bottom right.
BALL_SPOTS = (
    (-9, 9, 5.6, False),
    (-3, 11, 5.8, False),
    (-13, 3, 5.8, False),
    (-9, -7, 6.2, False),
    (12, 0, 6.0, False),
    (5, -8, 6.4, True),
    (-4, 2, 6.4, True),
    (7, 9, 6.4, True),
)

STYLES = {
    1: dict(col="red", cap="ref", base="cone", balls="GWRWGYBR"),
    2: dict(col="green", cap="dome", base="bell", balls="BWGWPRYB"),
    3: dict(col="mustard", cap="flat", base="step", balls="GWBWPBRG"),
    4: dict(col="blue", cap="pagoda", base="pot", balls="OWRWPYGR"),
}

RIM_H = {"cone": 7, "bell": 6, "step": 8, "pot": 5}


def base_profile(style, t):
    """Half width of the base body, t = 0 under the collar .. 1 above the rim."""
    if style == "cone":
        return int(round(12 + 4 * t))
    if style == "bell":
        return int(round(11 + 6 * t ** 2.4))
    if style == "step":
        return 12 if t < 0.5 else 15
    return int(round(12 + 5 * math.sin(t * math.pi / 2)))      # pot


def ball(s, cx, cy, r, key):
    base, sh = BALL[key]
    m = ell(cx + 0.5, cy + 0.5, r, r)
    s.shape(m, base, m - ell(cx - 0.9, cy - 0.9, r, r), sh)
    # glossy crescent, top left
    s.put(cx - 3, cy - 4, PAPER)
    s.put(cx - 4, cy - 3, PAPER)
    if key != "W":
        s.put(cx - 2, cy - 5, PAPER)
        s.put(cx - 4, cy - 2, PAPER)


CAP_ROWS = {
    "ref": ({5: 8, 6: 10, 7: 11, 8: 11, 9: 11, 10: 11}, {11: 14, 12: 15, 13: 15, 14: 15, 15: 14}),
    "dome": ({5: 5, 6: 8, 7: 10, 8: 11, 9: 12, 10: 12, 11: 12}, {12: 14, 13: 15, 14: 15, 15: 14}),
    "flat": ({5: 3, 6: 4, 7: 4, 8: 11, 9: 12, 10: 12}, {11: 15, 12: 16, 13: 16, 14: 16, 15: 15}),
    "pagoda": ({5: 2, 6: 3, 7: 2, 8: 5, 9: 7, 10: 9, 11: 11}, {12: 14, 13: 15, 14: 15, 15: 13}),
}


def gacha_cap(s, style, ox, oy, cols, bulbs=None):
    """Cap = crown + wider brim. bulbs: 3 states (0 off, 1 warm, 2 flash) or None."""
    base, sh, hl = cols
    crown, brim = CAP_ROWS[style]
    rows = {}
    rows.update(crown)
    rows.update(brim)
    rows = {y + oy: hw for y, hw in rows.items()}
    cx = GCX + ox
    m = rows_mask(rows, cx)
    s.shape(m, base)
    brim_top = min(brim) + oy
    crown_top = min(crown) + oy
    wide_top = min(y for y, hw in crown.items() if hw >= 8) + oy
    for y, hw in rows.items():
        x0, x1 = cx - hw, cx + hw - 1
        if y < brim_top:
            # crown: lit streak on the left, shade on the right, seam above the brim
            for x in (x0 + 2, x0 + 3):
                if y > crown_top and x < cx - 1:
                    s.put(x, y, hl)
            for x in (x1 - 1, x1):
                if x >= cx + 1:
                    s.put(x, y, sh)
            if y == brim_top - 1:
                s.hline(x0, x1, y, sh)
        else:
            # brim: its top face catches the light (we look from above)
            if y == brim_top:
                s.hline(x0 + 1, cx + 4, y, hl)
            if y == max(rows):
                s.hline(x0, x1, y, sh)
            for x in (x1 - 2, x1 - 1, x1):
                s.put(x, y, sh)
    # specular tick on the crown
    s.put(cx - rows[wide_top + 1] + 4, wide_top + 1, PAPER)
    s.put(cx - rows[wide_top + 1] + 5, wide_top + 1, PAPER)
    if bulbs is not None:
        for i, bx in enumerate((cx - 10, cx - 1, cx + 8)):
            st = bulbs[i]
            s.rect(bx, brim_top + 1, bx + 1, brim_top + 2, (DSTEEL, MUSTARD, PAPER)[st])
            if st == 1:
                s.put(bx, brim_top + 1, PAPER)
            elif st == 0:
                s.put(bx, brim_top + 1, STEEL)
            s.hline(bx, bx + 1, brim_top + 3, INK)
            s.put(bx + 2, brim_top + 2, INK)


def price_tag(s, n, ax, ay, swing):
    """Cream tag with the machine number, hanging by a string from the brim."""
    tx, ty = ax + 1 + swing, ay + 3
    s.put(ax, ay, INK)
    s.put(ax + 1, ay + 1, INK)
    s.put(ax + 1 + (1 if swing > 0 else 0), ay + 2, INK)
    m = box(tx, ty, tx + 4, ty + 6)
    s.shape(m, PAPER, {q for q in m if q[0] == tx + 4 or q[1] == ty + 6}, DCREAM)
    glyph_rows(s, DIGITS[n], tx + 1, ty + 1, RED)


def gacha_base(s, style, top, widen, cols):
    base, sh, hl = cols
    rim_h = RIM_H[style]
    rim_top = G_BOT - rim_h + 1
    rows = {}
    for y in range(top, top + 3):
        rows[y] = 13
    body_top = top + 3
    n = rim_top - body_top
    for i in range(n):
        t = i / float(max(1, n - 1))
        rows[body_top + i] = base_profile(style, t) + widen
    rim_hw = {"cone": 18, "bell": 19, "step": 18, "pot": 18}[style] + widen
    for y in range(rim_top, G_BOT + 1):
        k = G_BOT - y
        rows[y] = rim_hw - (3 if k == 0 else 1 if k == 1 else 0)
    if style == "pot":
        rows[rim_top] = rim_hw - 1
    m = rows_mask(rows, GCX)
    s.shape(m, base)
    for y, hw in rows.items():
        x0, x1 = GCX - hw, GCX + hw - 1
        if y < body_top:                      # collar ring
            s.put(x0 + 2, y, hl)
            s.put(x0 + 3, y, hl)
            for x in (x1 - 2, x1 - 1, x1):
                s.put(x, y, sh)
            if y == body_top - 1:
                s.hline(x0, x1, y, sh)
        elif y < rim_top:                     # flared body
            if y > body_top:
                s.put(x0 + 2, y, hl)
                s.put(x0 + 3, y, hl)
            for x in (x1 - 2, x1 - 1, x1):
                s.put(x, y, sh)
            if y == rim_top - 1:
                s.hline(x0, x1, y, sh)
        else:                                 # foot rim, top face lit
            if y == rim_top:
                s.hline(x0 + 2, GCX + 6, y, hl)
            for x in (x1 - 3, x1 - 2, x1 - 1, x1):
                s.put(x, y, sh)
            if y == G_BOT:
                s.hline(x0, x1, y, sh)
    if style == "step":                       # ledge of the lower tier
        ys = [y for y in range(body_top + 1, rim_top) if rows[y] > rows[y - 1]]
        for y in ys:
            s.hline(GCX - rows[y] + 1, GCX + 5, y, hl)
    # specular tick at the top of the body streak, scuffs on the foot rim
    s.put(GCX - rows[body_top + 2] + 2, body_top + 2, PAPER)
    s.put(GCX - rows[body_top + 3] + 2, body_top + 3, PAPER)
    x0 = GCX - rows[G_BOT - 2]
    s.put(x0 + 5, G_BOT - 2, sh)
    s.put(x0 + 6, G_BOT - 1, sh)
    s.put(GCX + 9, G_BOT - 2, hl)
    return rows


# arm specs in LEFT-arm coordinates: (ctrl, wrist, glove, front)
G_ARM_OFF = ((6, 62), (8, 71), "down", False)
G_ARM_IDLE = ((2, 57), (5, 67), "down", False)


def gacha(n, on=True, sq=0, gdx=0, gdy=0, capdx=0, capdy=0, balls=None, eyes=None, la=None,
          ra=None, handle=0, lamp_on=1, bulbs=None, tag=0, glint=-1):
    """One capsule machine in a pose.

    sq > 0 squashes the base by sq pixels (and widens it), sq < 0 stretches.
    gdx / gdy lean and lower the globe and cap, capdx / capdy move only the cap.
    balls: 8 (dx, dy) offsets; eyes: 3 (state, look) for the balls with eyes.
    bulbs: the 3 brim lamps; tag: swing of the price tag; glint: dial sparkle.
    """
    st = STYLES[n]
    cols = BODY[st["col"]]
    s = Cv(GW, GH)
    balls = balls or [(0, 0)] * 8
    eyes = eyes or [("open", 1)] * 3
    la = la or G_ARM_IDLE
    ra = ra or G_ARM_IDLE
    bulbs = bulbs or [1, 1, 1]
    top = BASE_TOP + sq
    widen = (sq + 1) // 2 if sq > 0 else -((-sq) // 2)
    gcy = GLOBE_CY + sq + gdy
    gx = GCX + gdx
    shoulder = (GCX - 12 - widen + 1, top + 6)
    arms = (("L", la), ("R", ra))

    # globe
    gm = ell(gx, gcy, 20, 18.5)
    glass, glass_sh = (SKY, DSKY) if on else (OFFSKY, OFFDSKY)
    s.shape(gm, glass, gm - ell(gx - 1.0, gcy - 1.0, 18.6, 17.1), glass_sh)
    tmp = Cv(GW, GH)
    e = 0
    for i, (dx, dy, r, eyed) in enumerate(BALL_SPOTS):
        bx, by = gx + dx + balls[i][0], gcy + dy + balls[i][1]
        ball(tmp, bx, by, r, st["balls"][i])
        if eyed:
            state, look = eyes[e]
            eye_pair(tmp, bx + 1, by - 3, 3, 6, state, look)
            e += 1
    s.paste_mask(tmp, gm)
    # glass gloss, drawn over the balls: a pale rim on the lit side, a hard
    # streak with a dot inside it, and a small bounce light bottom right
    rim = gm - ell(gx, gcy, 19.0, 17.5)
    streak = ell(gx, gcy, 17.4, 15.9) - ell(gx, gcy, 15.2, 13.7)
    for (x, y) in rim:
        a = math.degrees(math.atan2(gcy - (y + 0.5), (x + 0.5) - gx)) % 360
        if on and (104 <= a <= 198 or 306 <= a <= 322):
            s.put(x, y, PAPER)
        elif not on and 120 <= a <= 170:
            s.put(x, y, SKY)
    for (x, y) in streak:
        a = math.degrees(math.atan2(gcy - (y + 0.5), (x + 0.5) - gx)) % 360
        if on and (130 <= a <= 162 or 114 <= a <= 121):
            s.put(x, y, PAPER)
        elif not on and 140 <= a <= 158:
            s.put(x, y, SKY)

    cap_oy = sq + gdy + capdy
    gacha_cap(s, st["cap"], gdx + capdx, cap_oy, cols, bulbs if on else [0, 0, 0])
    price_tag(s, n, gx + capdx + 14, 16 + cap_oy, tag)

    for side, spec in arms:
        if not spec[3]:
            draw_arm(s, side, shoulder, spec, "arm")

    gacha_base(s, st["base"], top, widen, cols)
    py = PLATE[1] + (sq // 2 if sq < 0 else 0)
    crank_plate(s, PLATE[0], py, handle, lamp_on if on else 0, glint)
    chute(s, *CHUTE_FRAME)

    for side, spec in arms:
        draw_arm(s, side, shoulder, spec, "both" if spec[3] else "glove")
    return s


def crank_arm(handle, sq, swing=0):
    """Right arm (in LEFT coordinates) holding the crank handle.

    The shoulder is right next to the crank, so the noodle loops outwards in a
    wide C before coming back to the fist; swing moves the elbow of the loop.
    """
    py = PLATE[1] + (sq // 2 if sq < 0 else 0)
    tx, ty = handle_tip(PLATE[0], py, handle)
    # mirror the handle tip into left-arm space; the fist's wrist is on its left
    mx = GW - 1 - tx
    wrist = (mx - 5, ty)
    widen = (sq + 1) // 2 if sq > 0 else -((-sq) // 2)
    sx, sy = GCX - 12 - widen + 1, BASE_TOP + sq + 6
    c1 = (sx - 15, sy - 13 + swing)
    c2 = (wrist[0] - 19, ty + 12 + swing)
    return ((c1, c2), wrist, "fist", True)


def gacha_static(n):
    return gacha(n, on=False, eyes=[("closed", 0)] * 3, la=G_ARM_OFF, ra=G_ARM_OFF, lamp_on=0)


def _arm(dx, dy, glove="down"):
    c, w, g, f = G_ARM_IDLE
    return ((c[0] + dx, c[1] + dy), (w[0] + dx, w[1] + dy), glove, f)


IDLE_FRAMES = 48


def _blink(f, at):
    """Eye state override for a three-frame blink centred on frame `at`."""
    if f in (at - 1, at + 1):
        return "half"
    if f == at:
        return "closed"
    return None


def gacha_idle_frames(n):
    """6 s loop: breathing, staggered glances, blinks, a look at the player, a
    wink, balls jostling, drumming fingers and a yawn that lifts the cap."""
    frames = []
    for f in range(IDLE_FRAMES):
        p = f % 12
        breath = 1 if 6 <= p <= 11 else 0
        capdy = -1 if p == 6 else 1 if p == 0 and f else 0      # the cap lags the globe
        lag = 1 if 8 <= p or p <= 1 else 0
        sway_l = -1 if 3 <= p <= 8 else 0
        sway_r = -1 if 9 <= p or p <= 2 else 0
        tag = (0, 0, 1, 1, 1, 0, 0, 0, -1, -1, 0, 0)[p]
        sq = 0
        # eyes: [top right ball, front ball, bottom right ball]
        if f < 9:
            looks = [1, 1, 1]
        elif f < 16:
            looks = [(0, 1), (0, 1), (0, 1)]                       # down at the player
        elif f < 26:
            looks = [-1 if f >= 17 else 1, -1, -1 if f >= 18 else 1]
        elif f < 32:
            looks = [1 if f >= 27 else -1, 1, 1 if f >= 28 else -1]
        elif f < 40:
            looks = [1, (-1, 1), (-1, 1)]                          # watching the drumming hand
        else:
            looks = [1, 1, 1]
        states = ["open", "open", "open"]
        for i, at in ((0, 5), (2, 13), (1, 22), (0, 30), (2, 37)):
            b = _blink(f, at)
            if b:
                states[i] = b
        if 27 <= f <= 29:
            states[1] = "wink"
        b = [(0, 0)] * 8
        if f in (19, 21):
            b[4] = (0, -1)
        if f == 20:
            b[4] = (0, -2)
            b[5] = (0, -1)
        if f in (33, 35):
            b[3] = (0, -1)
        if f == 34:
            b[3] = (1, -2)
            b[2] = (0, -1)
        la = _arm(sway_l, lag)
        if 32 <= f <= 39:
            la = _arm(0, 0, "drum_a" if f % 2 == 0 else "drum_b")
        # yawn: a slow stretch, lids droop, the cap lifts like a lid
        if 40 <= f <= 45:
            k = f - 40
            sq = (0, -1, -1, -1, 0, 1)[k]
            capdy = (-1, -2, -3, -2, 0, 0)[k]
            breath = 0 if k < 5 else 1
            states = [("half", "closed", "closed", "half", "open", "open")[k]] * 3
            b = [(0, (0, -1, -1, -1, 0, 0)[k])] * 8
        elif f in (46, 47):
            breath = 1 if f == 46 else 0
            capdy = 0
        frames.append(gacha(
            n, sq=sq, gdy=breath, capdy=capdy, balls=b,
            eyes=list(zip(states, looks)), la=la, ra=_arm(sway_r, lag),
            lamp_on=1 if f % 8 < 6 else 2,
            bulbs=[2 if (f // 2) % 3 == i else 1 for i in range(3)],
            tag=tag, glint=(f - 10) if 10 <= f <= 13 else -1))
    return frames


G_UP_MID = ((-1, 56), (3, 49), "open", True)
G_UP_HIGH = ((-3, 50), (4, 40), "open", True)
G_UP_OUT = ((-3, 47), (3, 38), "open", True)
G_DN = ((1, 56), (4, 62), "down", False)


def gacha_wake_frames(n, idle0):
    """Power arrives, a crouch, a big Y stretch that pops the cap, settle."""
    j1 = [(0, -1)] * 8
    j2 = [(0, -2), (0, -1), (0, -2), (0, -1), (0, -2), (0, -2), (0, -1), (0, -2)]
    flash, warm = [2, 2, 2], [1, 1, 1]
    return [
        gacha_static(n),
        gacha(n, sq=1, eyes=[("closed", 0)] * 3, la=G_ARM_OFF, ra=G_ARM_OFF, lamp_on=2, bulbs=flash),
        gacha(n, sq=2, eyes=[("half", 0)] * 3, la=G_DN, ra=G_DN, lamp_on=2, bulbs=warm),
        gacha(n, sq=-1, capdy=-1, eyes=[("wide", 0)] * 3, la=G_UP_MID, ra=G_UP_MID, balls=j1,
              lamp_on=1, bulbs=flash, tag=1),
        gacha(n, sq=-2, capdy=-2, eyes=[("wide", 0)] * 3, la=G_UP_HIGH, ra=G_UP_HIGH, balls=j2,
              lamp_on=2, bulbs=warm, tag=1),
        gacha(n, sq=-2, capdy=-1, eyes=[("happy", 0)] * 3, la=G_UP_OUT, ra=G_UP_OUT, balls=j1,
              lamp_on=1, bulbs=flash, tag=-1),
        gacha(n, sq=1, capdy=1, eyes=[("open", 0)] * 3, la=G_UP_MID, ra=G_UP_MID, lamp_on=1,
              bulbs=warm, tag=-1),
        gacha(n, sq=1, eyes=[("open", 1)] * 3, la=G_DN, ra=G_DN, lamp_on=1, bulbs=flash),
        idle0,
    ]


def gacha_play_frames(n, idle0):
    """Anticipation (lean away, wind the handle back), one full turn with squash
    and stretch, an overshoot past the stop, a flick of the hand, settle."""
    bal = ((0, 53), (3, 59), "open", True)           # left arm out for balance
    bal_up = ((-2, 50), (3, 52), "open", True)
    bal_wave = ((2, 55), (7, 62), "wave", True)
    ja = [(1, 0), (-1, 0), (0, 1), (1, -1), (-1, 0), (0, -1), (1, 0), (-1, 1)]
    jb = [(-1, -1), (1, -2), (0, -1), (-1, -2), (1, -1), (0, -2), (-1, -1), (1, -2)]
    jc = [(0, 1), (1, 0), (-1, 0), (0, 0), (1, 1), (-1, 0), (0, 1), (1, 0)]
    at_crank = [("open", (1, 1))] * 3
    squint = [("half", 1)] * 3
    wide = [("wide", 0)] * 3
    happy = [("happy", 0)] * 3
    flash, warm = [2, 2, 2], [1, 1, 1]
    return [
        gacha(n, sq=1, gdx=-1, eyes=at_crank, la=bal_wave, ra=crank_arm(7, 1, -2), handle=7,
              lamp_on=2, bulbs=warm, tag=1),
        gacha(n, sq=2, gdx=-2, capdx=-1, eyes=squint, la=bal, ra=crank_arm(0, 2, 0), handle=0,
              balls=ja, lamp_on=2, bulbs=flash, tag=1),
        gacha(n, sq=2, gdx=1, eyes=squint, la=bal, ra=crank_arm(2, 2, 3), handle=2, balls=jc,
              lamp_on=1, bulbs=warm, tag=-1),
        gacha(n, sq=-1, gdx=2, capdx=1, capdy=-1, eyes=wide, la=bal_up, ra=crank_arm(4, -1, 1),
              handle=4, balls=jb, lamp_on=2, bulbs=flash, tag=-1),
        gacha(n, sq=-3, gdx=0, capdy=-1, eyes=wide, la=bal_up, ra=crank_arm(6, -3, -3), handle=6,
              balls=jb, lamp_on=1, bulbs=warm),
        gacha(n, sq=2, gdx=-1, capdy=-2, eyes=squint, la=bal, ra=crank_arm(1, 2, 2), handle=1,
              balls=jc, lamp_on=2, bulbs=flash, tag=1),
        gacha(n, sq=1, gdx=1, capdy=1, eyes=happy, la=bal_wave, ra=crank_arm(0, 1, 0), handle=0,
              balls=ja, lamp_on=2, bulbs=warm, tag=-1),
        gacha(n, sq=-1, capdy=-1, eyes=happy, la=bal_wave, ra=bal_wave, balls=j_up(), lamp_on=1,
              bulbs=flash),
        gacha(n, sq=1, eyes=happy, la=_arm(0, -2), ra=_arm(0, -2), lamp_on=1, bulbs=warm),
        idle0,
    ]


def j_up():
    return [(0, -1)] * 8


# ------------------------------------------------------------------ cabinets 005 / 006 (shared)

CW, CH = 72, 104
CCX = 36
C_BOT = CH - 2
CAB_SHOULDER = {5: (11, 78), 6: (11, 85)}

C_ARM_OFF = {5: ((4, 80), (6, 90), "down", False), 6: ((5, 88), (6, 94), "down", False)}
C_ARM_IDLE = {5: ((2, 76), (5, 86), "down", False), 6: ((2, 83), (5, 91), "down", False)}


def cab_arm(n, dx, dy, glove="down"):
    c, w, g, f = C_ARM_IDLE[n]
    return ((c[0] + dx, c[1] + dy), (w[0] + dx, w[1] + dy), glove, f)


def panel(s, x0, y0, x1, y1, cols, r=0):
    """Outlined box, lit on its top and left edge, shaded on bottom and right."""
    base, sh, hl = cols
    m = box(x0, y0, x1, y1, r)
    s.shape(m, base,
            {q for q in m if q[1] == y1 or q[0] >= x1 - 1}, sh,
            {q for q in m if (q[1] == y0 or q[0] == x0) and q[1] != y1 and q[0] < x1 - 1}, hl)


def sticker(s, x0, y0, x1, y1):
    m = box(x0, y0, x1, y1)
    s.shape(m, PAPER, {q for q in m if q[1] == y1 or q[0] == x1}, DCREAM)


# ------------------------------------------------------------------ 005 crane catcher

CR_GLASS = (13, 25, 58, 61)          # glass interior, pixel-stable in idle / react
CR_CHUTE_FRAME = (40, 80, 57, 97)
CRANE_ANCHORS = {
    "chute": [49, 89], "claw_rail_y": 28, "claw_min_x": 23, "claw_max_x": 49,
    "claw_rest_x": 25, "grab_y": 33, "drop_x": 49, "drop_y": 55,
}

PLUSH = {
    "bear": (MUSTARD, DMUST), "bunny": (PINK, DPINK), "cat": (CREAM, DCREAM),
    "frog": (GREEN, DGREEN), "blob": (BLUE, NAVY), "fox": (ORANGE, DORANGE),
}


def plush(s, cx, cy, kind, awake):
    base, sh = PLUSH[kind]
    head = ell(cx + 0.5, cy + 0.5, 5.2, 4.8)
    ears = set()
    if kind == "bear":
        ears = ell(cx - 3.5, cy - 4, 2, 2) | ell(cx + 4.5, cy - 4, 2, 2)
    elif kind == "bunny":
        ears = box(cx - 4, cy - 10, cx - 2, cy - 3, r=1) | box(cx + 2, cy - 10, cx + 4, cy - 3, r=1)
    elif kind in ("cat", "fox"):
        ears = poly([(cx - 5, cy - 2), (cx - 4, cy - 8), (cx - 0.5, cy - 3)]) | \
               poly([(cx + 6, cy - 2), (cx + 5, cy - 8), (cx + 1.5, cy - 3)])
    elif kind == "frog":
        ears = ell(cx - 2.5, cy - 4, 2.2, 2.2) | ell(cx + 3.5, cy - 4, 2.2, 2.2)
    m = head | ears
    s.shape(m, base, m - ell(cx - 0.6, cy - 0.6, 5.2, 4.8) - ears, sh)
    if kind == "bunny":
        s.vline(cx - 3, cy - 8, cy - 5, PAPER)
        s.vline(cx + 3, cy - 8, cy - 5, PAPER)
    for ex in (cx - 2, cx + 2):
        if awake:
            s.put(ex, cy - 1, INK)
            s.put(ex, cy, INK)
        else:
            s.put(ex, cy, INK)
            s.put(ex + (1 if ex > cx else -1), cy, INK)
    s.put(cx, cy + 2, INK)
    if kind in ("bear", "cat", "fox"):
        s.put(cx - 1, cy + 1, PAPER)
        s.put(cx, cy + 1, PAPER)
        s.put(cx + 1, cy + 1, PAPER)
        s.put(cx, cy + 1, INK)
        s.put(cx, cy + 2, PAPER)


def mini_capsule(s, cx, cy, key):
    base, sh = BALL[key]
    m = ell(cx + 0.5, cy + 0.5, 3.6, 3.6)
    s.shape(m, CREAM, m - ell(cx - 0.3, cy - 0.3, 3.6, 3.6), DCREAM)
    s.puts({q for q in m if q[1] <= cy}, base)
    s.put(cx - 1, cy - 2, PAPER)


def crane(on=True, hdy=0, eyes=("open", 0), lamps=None, la=None, ra=None, joy=0, bulge=0,
          btn=-1, coin=1, hop=None, slots=None):
    """Crane catcher. hdy <= 0 lifts the head (roof + marquee) off the box.

    btn: index of the panel button that is lit; coin: coin lamp state;
    hop: 6 vertical offsets for the plush prizes (wake only: the glass
    interior must not change in idle / react).
    """
    n = 5
    cols = BODY["navy"]
    base, sh, hl = cols
    s = Cv(CW, CH)
    la = la or C_ARM_IDLE[n]
    ra = ra or C_ARM_IDLE[n]
    lamps = lamps or [0] * 6
    hop = hop or [0] * 6
    shoulder = CAB_SHOULDER[n]
    arms = (("L", la), ("R", ra))
    for side, spec in arms:
        if not spec[3]:
            draw_arm(s, side, shoulder, spec, "arm")

    # lower cabinet and plinth
    panel(s, 12, 100, 59, C_BOT, (DSTEEL, HOLE, STEEL))
    for x in (15, 18, 21, 50, 53, 56):                       # vents and feet
        s.put(x, 101, INK)
    panel(s, 10 - bulge, 75, 61 + bulge, 99, cols)
    s.rect(11 - bulge, 77, 12 - bulge, 97, hl)
    # coin plate with its lamp, price badge
    panel(s, 15, 78, 25, 88, (STEEL, DSTEEL, LSTEEL))
    s.rect(19, 80, 20, 85, INK)
    s.put(19, 80, DSTEEL)
    lamp_c = (DSTEEL, MUSTARD, PAPER)[coin if on else 0]
    s.rect(23, 80, 23, 81, lamp_c)
    badge = ell(33, 83, 4.2, 4.2)
    s.shape(badge, RED, badge - ell(32.4, 82.4, 4.2, 4.2), DRED)
    s.rect(32, 81, 33, 84, PAPER)                            # coin mark
    s.put(31, 81, LRED)
    # sign plate: ku-re-e-n (crane)
    sticker(s, 14, 91, 37, 97)
    kana_line(s, ("ku", "re", "bar", "n"), 15, 92, RED)
    chute(s, *CR_CHUTE_FRAME)
    s.put(59, 96, DNAVY)                                     # wear
    s.put(58, 97, DNAVY)
    s.put(59, 78, hl)

    # glass box frame (cream pillars); it continues under the head as a neck
    frame = box(10, 15, 61, 64)
    s.shape(frame, CREAM, {q for q in frame if q[0] >= 60 or q[1] >= 64}, DCREAM,
            {q for q in frame if q[0] == 10}, PAPER)
    gx0, gy0, gx1, gy1 = CR_GLASS
    inner = box(gx0, gy0, gx1, gy1)
    s.puts(edge(inner), INK)
    glass, glass_sh = (SKY, DSKY) if on else (OFFSKY, OFFDSKY)
    s.puts(inner, glass)
    s.rect(gx0, gy0, gx1, gy0 + 2, DSTEEL)                   # rail
    s.hline(gx0, gx1, gy0, STEEL)
    s.hline(gx0, gx1, gy0 + 3, INK)
    s.rect(gx1 - 1, gy0 + 4, gx1, gy1, glass_sh)             # inner right wall
    # prize bed seen from above
    s.rect(gx0, 48, gx1, gy1, PINK)
    s.hline(gx0, gx1, 48, DPINK)
    s.rect(gx1 - 1, 49, gx1, gy1, DPINK)
    # drop hole with a steel collar
    collar = ell(49.5, 56.5, 8, 5)
    s.puts(edge(collar) & inner, INK)
    s.puts(collar & inner, STEEL)
    s.puts(ell(49.5, 55.6, 8, 4.2) & collar & inner, LSTEEL)
    hole = ell(49.5, 56.2, 6, 3.2)
    s.puts(edge(hole), INK)
    s.puts(hole, INK)
    s.puts(hole - ell(48.6, 55.6, 6, 3.2), HOLE)
    # highlights on the glass (behind the prizes: the game draws the claw on top)
    for (x, y) in inner:
        if 30 <= y <= 44:
            d = (x - gx0) + (y - gy0)
            if 22 <= d <= 24 or (on and 28 <= d <= 28):
                s.put(x, y, PAPER if on else SKY)
    # pile of plush prizes
    tmp = Cv(CW, CH)
    for i, (px, py, kind) in enumerate(((19, 49, "bear"), (30, 48, "frog"), (39, 50, "fox"))):
        plush(tmp, px, py + hop[i], kind, on)
    mini_capsule(tmp, 25, 54, "R")
    mini_capsule(tmp, 35, 55, "B")
    for i, (px, py, kind) in enumerate(((17, 57, "bunny"), (28, 58, "cat"), (38, 58, "blob"))):
        plush(tmp, px, py + hop[3 + i], kind, on)
    s.paste_mask(tmp, inner)

    # control panel: sloped top (lit) and front lip, joystick and buttons
    top_face = poly([(11, 66), (61, 66), (64, 72), (8, 72)])
    s.shape(top_face, LSTEEL)
    panel(s, 8, 72, 63, 74, (STEEL, DSTEEL, LSTEEL))
    jx = 21 + joy
    s.puts(edge(ell(21.5, 69.5, 2.5, 1.2)), INK)
    s.puts(ell(21.5, 69.5, 2.5, 1.2), DSTEEL)
    s.puts(line(21, 69, jx, 67, 2), INK)
    knob = ell(jx + 1.0, 65.5, 2.5, 2.5)
    s.shape(knob, RED, knob - ell(jx + 0.4, 64.9, 2.5, 2.5), DRED)
    s.put(jx - 1, 64, PAPER)
    for i, (bx, bc, bs) in enumerate(((32, MUSTARD, DMUST), (41, RED, DRED), (50, GREEN, DGREEN))):
        b = box(bx, 68, bx + 4, 69)
        s.puts(edge(b), INK)
        s.puts(b, bc)
        s.hline(bx, bx + 4, 69, bs)
        s.put(bx, 68, PAPER)
        if on and i == btn:
            s.hline(bx, bx + 4, 68, PAPER)
            s.hline(bx, bx + 4, 69, bc)

    # head: roof seen from above + marquee with the eyes and the lamps
    roof = poly([(13, 6 + hdy), (59, 6 + hdy), (63, 10 + hdy), (9, 10 + hdy)])
    s.shape(roof, hl)
    s.hline(18, 53, 7 + hdy, SKY)
    panel(s, 8, 10 + hdy, 63, 22 + hdy, cols, r=1)
    s.hline(10, 61, 21 + hdy, MUSTARD)
    eye_pair(s, CCX, 9 + hdy, 6, 10, eyes[0], eyes[1])
    for i, x in enumerate((11, 17, 23, 47, 53, 59)):
        lamp(s, x, 14 + hdy, lamps[i] if on else 0)

    for side, spec in arms:
        draw_arm(s, side, shoulder, spec, "both" if spec[3] else "glove")
    return s


# ------------------------------------------------------------------ 006 lucky plinko

PK_BOARD = (8, 26, 63, 76)           # board interior, pixel-stable in idle / react
PK_CHUTE_FRAME = (27, 82, 44, 97)
PK_ROWS, PK_ROW_STEP, PK_COL_STEP = 6, 6, 5
PK_START = (36, 29)
PK_SLOT_Y = 72
PK_SLOT_XS = [16, 26, 36, 46, 56]
PLINKO_ANCHORS = {
    "chute": [36, 90], "ball_start": list(PK_START), "rows": PK_ROWS, "row_step": PK_ROW_STEP,
    "column_step": PK_COL_STEP, "slot_y": PK_SLOT_Y, "slot_xs": PK_SLOT_XS,
}


def plinko_pegs():
    """Top-left pixel of every 2 x 2 peg. Row k catches the ball after k hops."""
    out = []
    for k in range(PK_ROWS):
        y = PK_START[1] + k * PK_ROW_STEP + 3
        for o in range(-5, 6):
            if (o - k) % 2 == 0:
                out.append((PK_START[0] + o * PK_COL_STEP - 1, y))
    return out


def plinko(on=True, hdy=0, eyes=("open", 0), lamps=None, la=None, ra=None, bulge=0,
           slots=None, coin=1, joy=0, btn=-1, hop=None):
    """Lucky Plinko. hdy <= 0 lifts the arched head off the board.

    slots: states of the five lamps on the ledge, one under each slot (they sit
    outside the board interior, which must not change in idle / react).
    """
    n = 6
    cols = BODY["pink"]
    base, sh, hl = cols
    s = Cv(CW, CH)
    la = la or C_ARM_IDLE[n]
    ra = ra or C_ARM_IDLE[n]
    lamps = lamps or [0] * 6
    slots = slots or [0] * 5
    shoulder = CAB_SHOULDER[n]
    arms = (("L", la), ("R", ra))
    for side, spec in arms:
        if not spec[3]:
            draw_arm(s, side, shoulder, spec, "arm")

    # pedestal (as wide as the crane's), plinth, tray ledge
    panel(s, 12, 100, 59, C_BOT, (DSTEEL, HOLE, STEEL))
    for x in (15, 18, 21, 50, 53, 56):
        s.put(x, 101, INK)
    panel(s, 10 - bulge, 81, 61 + bulge, 99, cols)
    s.rect(11 - bulge, 83, 12 - bulge, 97, hl)
    s.rect(11 - bulge, 95, 25, 96, MUSTARD)                    # trim stripe
    s.hline(11 - bulge, 25, 97, DMUST)
    panel(s, 15, 84, 21, 92, (STEEL, DSTEEL, LSTEEL))          # coin plate
    s.rect(18, 86, 18, 90, INK)
    lamp_c = (DSTEEL, MUSTARD, PAPER)[coin if on else 0]
    s.rect(23, 85, 24, 86, lamp_c)
    s.puts(edge(box(23, 85, 24, 86)), INK)
    s.rect(23, 89, 24, 91, RED)                                # price dot
    s.puts(edge(box(23, 89, 24, 91)), INK)
    s.put(23, 89, LRED)
    # square sticker: ra-tsu / ki-i (lucky)
    sticker(s, 47, 84, 59, 96)
    kana_line(s, ("ra", "tsu"), 48, 85, RED)
    kana_line(s, ("ki", "bar"), 48, 91, NAVY)
    chute(s, *PK_CHUTE_FRAME)
    ledge = poly([(9, 78), (63, 78), (66, 81), (6, 81)])
    s.shape(ledge, LSTEEL)
    s.hline(6, 65, 80, STEEL)
    for i, cx in enumerate(PK_SLOT_XS):                        # slot lamps on the ledge
        lamp(s, cx - 1, 78, slots[i] if on else 0)

    # board frame; it continues under the head as a neck
    bx0, by0, bx1, by1 = PK_BOARD
    frame = box(bx0 - 2, 18, bx1 + 2, by1 + 1)
    s.shape(frame, base, {q for q in frame if q[0] >= bx1 + 2 or q[1] > by1}, sh,
            {q for q in frame if q[0] == bx0 - 2}, hl)
    inner = box(bx0, by0, bx1, by1)
    ray_a, ray_b = (PAPER, CREAM) if on else (CREAM, OFFCREAM)
    for (x, y) in inner:                                      # rising-sun rays
        a = math.degrees(math.atan2(68 - (y + 0.5), (x + 0.5) - CCX))
        s.put(x, y, ray_a if int((a + 7.5) // 15) % 2 == 0 else ray_b)
    s.rect(bx0, by0, bx1, by0, DCREAM)                        # shade under the head
    s.rect(bx0, by0, bx0, by1, DCREAM)
    # slots
    slot_top = PK_SLOT_Y - 6
    slot_cols = (RED, MUSTARD, GREEN, MUSTARD, RED)
    slot_sh = (DRED, DMUST, DGREEN, DMUST, DRED)
    s.rect(bx0, slot_top + 2, bx1, by1, INK)
    for i, cx in enumerate(PK_SLOT_XS):
        s.rect(cx - 4, slot_top + 3, cx + 3, by1 - 1, slot_cols[i])
        s.rect(cx - 4, by1 - 1, cx + 3, by1 - 1, slot_sh[i])
        s.rect(cx + 3, slot_top + 3, cx + 3, by1 - 1, slot_sh[i])
    for i in range(6):                                         # divider posts
        x = PK_SLOT_XS[0] - PK_COL_STEP + i * 2 * PK_COL_STEP
        s.rect(x - 1, slot_top, x, slot_top + 2, INK)
        s.put(x - 1, slot_top, DSTEEL)
    # pegs
    for (px, py) in plinko_pegs():
        peg = {(px, py), (px + 1, py), (px, py + 1), (px + 1, py + 1)}
        s.puts(edge(peg) & inner, INK)
        s.puts(peg, RED)
        s.put(px, py, LRED)
        s.put(px + 1, py + 1, DRED)

    # head: arch with a lit top face, eyes and lamps
    top_face = {q for q in ell(CCX, 25 + hdy - 3, 30, 17) if q[1] <= 21 + hdy}
    s.shape(top_face, hl)
    front = {q for q in ell(CCX, 25 + hdy, 30, 17) if q[1] <= 24 + hdy}
    s.shape(front, base, front - ell(CCX - 1.5, 25 + hdy, 30, 17), sh)
    s.hline(7, 64, 24 + hdy, sh)
    s.hline(7, 64, 22 + hdy, MUSTARD)
    eye_pair(s, CCX, 9 + hdy, 6, 10, eyes[0], eyes[1])
    for i, (ang, sx) in enumerate(((22, -1), (42, -1), (60, -1), (60, 1), (42, 1), (22, 1))):
        a = math.radians(ang)
        lx = int(round(CCX + sx * 24.5 * math.cos(a) - 1))
        ly = int(round(24 + hdy - 13.0 * math.sin(a)))
        lamp(s, lx, ly, lamps[i] if on else 0)

    for side, spec in arms:
        draw_arm(s, side, shoulder, spec, "both" if spec[3] else "glove")
    return s


# ------------------------------------------------------------------ cabinet animations

CAB = {5: crane, 6: plinko}


def cab_static(n):
    return CAB[n](on=False, eyes=("closed", 0), la=C_ARM_OFF[n], ra=C_ARM_OFF[n])


def chase(f):
    """Six sign lamps, a lit pair running along them."""
    return [2 if (i - f) % 3 == 0 else 1 for i in range(6)]


def ping(f):
    """Five slot lamps, one bright lamp running to and fro."""
    k = (0, 1, 2, 3, 4, 3, 2, 1)[f % 8]
    return [2 if i == k else 1 for i in range(5)]


def cab_idle_frames(n):
    """6 s loop: breathing head, glances, blinks, a wink, a look down at the
    player, drumming fingers, a chuckle; lamps chase, the joystick wiggles."""
    frames = []
    for f in range(IDLE_FRAMES):
        p = f % 12
        hdy = -1 if 6 <= p <= 11 else 0
        lag = -1 if 8 <= p or p <= 1 else 0
        sway_l = -1 if 3 <= p <= 8 else 0
        sway_r = -1 if 9 <= p or p <= 2 else 0
        if f < 8:
            look = 1
        elif f < 14:
            look = 0
        elif f < 20:
            look = (0, 1)                 # down at the player
        elif f < 28:
            look = -1
        elif f < 32:
            look = 0
        elif f < 40:
            look = (-1, 1)                # watching the drumming hand
        else:
            look = 1
        state = "open"
        for at in (5, 16, 37):
            state = _blink(f, at) or state
        if 28 <= f <= 30:
            state = "wink"
        la = cab_arm(n, sway_l, lag)
        ra = cab_arm(n, sway_r, lag)
        if 32 <= f <= 39:
            la = cab_arm(n, 0, 0, "drum_a" if f % 2 == 0 else "drum_b")
        if 41 <= f <= 46:                 # chuckle: the head bobs, eyes squeezed
            state = "happy"
            hdy = (-2, 0, -2, 0, -1, 0)[f - 41]
            la = cab_arm(n, -1, -1 + (f % 2))
            ra = cab_arm(n, -1, -1 + (f % 2))
        joy = (1, 1, -1, -1, 1, 0)[f - 21] if 21 <= f <= 26 else 0
        frames.append(CAB[n](
            hdy=hdy, eyes=(state, look), lamps=chase(f // 2), la=la, ra=ra,
            joy=joy, btn=(f // 4) % 3, coin=1 if f % 8 < 6 else 2, slots=ping(f // 2)))
    return frames


def _cab_up(n, k):
    """Raised-arm poses beside the glass box / board, never over their interior."""
    if n == 5:
        return (((-2, 77), (3, 68), "open", True), ((-3, 70), (4, 56), "open", True),
                ((-4, 68), (3, 54), "open", True))[k]
    return (((-3, 84), (3, 75), "open", True), ((-5, 79), (3, 64), "open", True),
            ((-5, 76), (3, 62), "open", True))[k]


def cab_wake_frames(n, idle0):
    fn = CAB[n]
    off = C_ARM_OFF[n]
    all2, all1 = [2] * 6, [1] * 6
    return [
        cab_static(n),
        fn(eyes=("closed", 0), lamps=all2, slots=[2] * 5, la=off, ra=off, bulge=1, coin=2),
        fn(eyes=("half", 0), lamps=all1, slots=[1] * 5, la=off, ra=off, bulge=1,
           hop=[0, -1, 0, -1, 0, -1]),
        fn(hdy=-2, eyes=("wide", 0), lamps=all2, slots=[2] * 5, la=_cab_up(n, 0), ra=_cab_up(n, 0),
           hop=[-1, -2, -1, -2, -1, -2], btn=0),
        fn(hdy=-4, eyes=("wide", 0), lamps=all1, slots=[1] * 5, la=_cab_up(n, 1), ra=_cab_up(n, 1),
           hop=[-2, -1, -2, -1, -2, -1], btn=1),
        fn(hdy=-4, eyes=("happy", 0), lamps=all2, slots=[2] * 5, la=_cab_up(n, 2), ra=_cab_up(n, 2),
           hop=[-1, 0, -1, 0, -1, 0], btn=2),
        fn(hdy=-1, eyes=("open", 0), lamps=all1, slots=[1] * 5, la=_cab_up(n, 0), ra=_cab_up(n, 0)),
        fn(hdy=0, eyes=("open", 0), lamps=chase(1), slots=ping(1), la=cab_arm(n, 0, -1),
           ra=cab_arm(n, 0, -1), bulge=1),
        idle0,
    ]


def cab_react_frames(n, idle0):
    """Happy bounce: crouch, both arms thrown up beside the cabinet, a double
    wave at the top, land with a bulge."""
    fn = CAB[n]
    all2, all1 = [2] * 6, [1] * 6
    s2, s1 = [2] * 5, [1] * 5
    return [
        fn(hdy=0, eyes=("wide", 0), lamps=all2, slots=s2, la=_cab_up(n, 0), ra=_cab_up(n, 0),
           bulge=1, joy=1, btn=0, coin=2),
        fn(hdy=-3, eyes=("happy", 0), lamps=all1, slots=s1, la=_cab_up(n, 1), ra=_cab_up(n, 1),
           joy=-1, btn=1),
        fn(hdy=-5 if n == 5 else -4, eyes=("happy", 0), lamps=all2, slots=s2, la=_cab_up(n, 2),
           ra=_cab_up(n, 1),
           joy=1, btn=2, coin=2),
        fn(hdy=-4, eyes=("happy", 0), lamps=all1, slots=s1, la=_cab_up(n, 1), ra=_cab_up(n, 2),
           joy=-1, btn=0),
        fn(hdy=-1, eyes=("happy", 0), lamps=all2, slots=s2, la=_cab_up(n, 0), ra=_cab_up(n, 0),
           btn=1, coin=2),
        fn(hdy=0, eyes=("open", 0), lamps=all1, slots=s1, la=cab_arm(n, 0, -1),
           ra=cab_arm(n, 0, -1), bulge=1),
        idle0,
    ]


# ------------------------------------------------------------------ small pieces

CAPSULES = {
    "red": (RED, DRED, CREAM, DCREAM),
    "blue": (BLUE, NAVY, CREAM, DCREAM),
    "green": (GREEN, DGREEN, CREAM, DCREAM),
    "mustard": (MUSTARD, DMUST, CREAM, DCREAM),
    "gold": (GOLD, MUSTARD, MUSTARD, DMUST),
}


def capsule(name):
    top, top_sh, bot, bot_sh = CAPSULES[name]
    s = Cv(12, 12)
    m = ell(6, 6, 5.3, 5.3)
    s.puts(edge(m), INK)
    lit = ell(5.0, 5.0, 5.3, 5.3)
    for (x, y) in m:
        upper = (y + 0.5 - 6) < 0.9 - 0.3 * (x + 0.5 - 6)
        if upper:
            s.put(x, y, top if (x, y) in lit else top_sh)
        else:
            s.put(x, y, bot if (x, y) in lit else bot_sh)
    for q in ((3, 3), (4, 2), (3, 2)):
        s.put(q[0], q[1], PAPER)
    if name == "gold":
        for q in ((7, 3), (6, 4), (8, 4), (7, 5), (7, 4)):
            s.put(q[0], q[1], PAPER)
    return s


CLAW_PAL = {"K": INK, "R": RED, "D": DRED, "W": GLOVE, "S": DCREAM, "L": LRED, "T": STEEL}

CLAW_OPEN = [
    ".........KK.........",
    ".........KK.........",
    ".......KKKKKK.......",
    "......KLRRRRRK......",
    ".....KRWKRRWKDK.....",
    ".....KRWKRRWKDK.....",
    ".....KRRRRRRDDK.....",
    "......KKKKKKKK......",
    "....KKK......KKK....",
    "...KKK........KKK...",
    "..KKK..........KKK..",
    ".KKK............KKK.",
    ".KK..............KK.",
    ".KK..............KK.",
    ".KKK............KKK.",
    "KWWWK..........KWWWK",
    "KWWWWK........KWWWWK",
    ".KWWSK........KWWSK.",
    "..KKK..........KKK..",
    "....................",
]

CLAW_CLOSED = [
    ".........KK.........",
    ".........KK.........",
    ".......KKKKKK.......",
    "......KLRRRRRK......",
    ".....KRKKRRKKDK.....",
    ".....KRWWRRWWDK.....",
    ".....KRRRRRRDDK.....",
    "......KKKKKKKK......",
    ".....KKK....KKK.....",
    "....KKK......KKK....",
    "....KK........KK....",
    "....KK........KK....",
    "....KK........KK....",
    "....KKK......KKK....",
    ".....KKK....KKK.....",
    "......KWWKKWWK......",
    ".....KWWWWWWWSK.....",
    "......KWWKKWSK......",
    ".......KK..KK.......",
    "....................",
]


def claw(is_open):
    rows = CLAW_OPEN if is_open else CLAW_CLOSED
    assert all(len(r) == 20 for r in rows) and len(rows) == 20
    s = Cv(20, 20)
    s.stamp(rows, 0, 0, CLAW_PAL)
    return s


BALL_PAL = {"K": INK, "W": GLOVE, "L": LSTEEL, "S": STEEL, "D": DSTEEL}
PLINKO_BALL = [
    ".KKKK.",
    "KLWLLK",
    "KWLLSK",
    "KLLSSK",
    "KLSSDK",
    ".KKKK.",
]


def plinko_ball():
    s = Cv(6, 6)
    s.stamp(PLINKO_BALL, 0, 0, BALL_PAL)
    return s


# ------------------------------------------------------------------ catalogue

def anchors():
    out = {}
    for n in (1, 2, 3, 4):
        out["machine_%03d" % n] = {"chute": list(GACHA_CHUTE)}
    out["machine_005"] = dict(CRANE_ANCHORS)
    out["machine_006"] = dict(PLINKO_ANCHORS)
    return out


def statics():
    """name -> sprite, for every still image of section A."""
    out = {}
    for n in (1, 2, 3, 4):
        out["machine_%03d" % n] = gacha_static(n)
    out["machine_005"] = cab_static(5)
    out["machine_006"] = cab_static(6)
    for name in CAPSULES:
        out["capsule_" + name] = capsule(name)
    out["claw_open"] = claw(True)
    out["claw_closed"] = claw(False)
    out["plinko_ball"] = plinko_ball()
    return out


def animations():
    """name -> (frames, fps, loop)."""
    out = {}
    for n in (1, 2, 3, 4):
        idle = gacha_idle_frames(n)
        key = "machine_%03d" % n
        out[key + "_wake"] = (gacha_wake_frames(n, idle[0]), 15, False)
        out[key + "_idle"] = (idle, 8, True)
        out[key + "_play"] = (gacha_play_frames(n, idle[0]), 15, False)
    for n in (5, 6):
        idle = cab_idle_frames(n)
        key = "machine_%03d" % n
        out[key + "_wake"] = (cab_wake_frames(n, idle[0]), 15, False)
        out[key + "_idle"] = (idle, 8, True)
        out[key + "_react"] = (cab_react_frames(n, idle[0]), 15, False)
    return out
