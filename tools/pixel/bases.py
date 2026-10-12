"""The five rarity bases, 56 x 30 per frame.

Contract: art-contract.md, section B. All five share one geometry so any figure
stacks on any base: the base is centred, touches the bottom row, and the
figure's feet stand on FEET = (28, 12), the centre of the top ellipse. Nothing
but that top surface may sit above y = 12 inside x 14..41.

The ladder (each step adds tiers, ornament, shine and motion), and the rarity
is also countable: every base carries 1 to 5 pips on its front.
  common     one moulded plastic puck with a groove and a mould ring, 1 pip, static
  uncommon   puck on a foot ring, cream rim stripe, name plate with 2 pips and a slow glint
  rare       two tiers, studs all round with a glint travelling from stud to stud,
             a light sweep over the lower deck, navy plate with 3 pips
  epic       three tiers, gold trim and filigree, two orb finials, 4 gem pips that
             light up one after the other and then flash together
  legendary  gold trophy: red velvet top, laurels, red sash with 5 stars lighting in
             a chase, a ring of orbiting stars and a shimmer over the gold
"""
import math

from pixlib import Spr, hx, shade, ell, box, poly, shift, clip

W, H = 56, 30
CX = 28
FEET = (28, 12)

INK = hx("161320")
WHITE = (255, 255, 255)
PAPER = hx("fff8e3")
CREAM = hx("f6e7c1")
RED = hx("e2231a")
DRED = hx("9c1420")
MUST = hx("f2b632")
SKY = hx("9fd3f5")
PINK = hx("f59ab5")
GREEN = hx("2e9e4f")

RARITY = {
    "common": hx("c9c2b0"),
    "uncommon": hx("7ec8a4"),
    "rare": hx("5fb3c9"),
    "epic": hx("c48ad6"),
    "legendary": hx("e3b44c"),
}

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))

# name -> pixels of the standing surface (top ellipse of the first tier plus its
# outline): the only thing allowed above y 12 inside x 14..41.
SURFACE = {}


def dk(c, k=1.1):
    return shade(c, -k)


def lt(c, k=1.0):
    return shade(c, k)


def M(m):
    return {(W - 1 - x, y) for (x, y) in m}


def outline(s, m, ink=INK):
    for (x, y) in m:
        for a, b in N4:
            if (x + a, y + b) not in m:
                s.put(x + a, y + b, ink)


def part(s, m, c, sh=True, sc=None):
    outline(s, m)
    sc = sc or dk(c)
    for (x, y) in m:
        s.put(x, y, sc if (sh and (x + 1, y + 1) not in m) else c)


def tier(s, rx, ry, cy, wall, col, top=None, lip=None, hl=None, sd=None):
    """One cylinder seen from above-front: top ellipse + front wall.
    Returns (top mask, wall mask)."""
    top = top or lt(col, 0.7)
    lip = lip or lt(col, 1.3)
    hl = hl or lt(col, 0.9)
    sd = sd or dk(col)
    t = ell(CX, cy, rx, ry)
    side = set()
    for k in range(1, wall + 1):
        side |= shift(t, 0, k)
    side -= t
    outline(s, t | side)
    x_hl = int(round(CX - rx * 0.72))
    for (x, y) in side:
        c = col
        if x >= CX + rx * 0.42:
            c = sd
        elif x_hl <= x < x_hl + 2:
            c = hl
        s.put(x, y, c)
    for (x, y) in t:
        s.put(x, y, lip if (x, y + 1) in side else top)
    return t, side


def offset_band(t, side, k0, k1):
    """Wall pixels lying k0..k1 rows under the top edge."""
    return (shift(t, 0, k1) - shift(t, 0, k0 - 1)) & side


def front_y(rx, ry, cy, x):
    """y of the lowest top-ellipse pixel in column x (the front edge)."""
    d = 1.0 - ((x + 0.5 - CX) / float(rx)) ** 2
    if d <= 0:
        return None
    return int(math.floor(cy + ry * math.sqrt(d) - 0.5))


def contact(s, t, col):
    """Soft-looking but hard-edged shadow where the figure stands."""
    for (x, y) in ell(CX, 12.6, 11.5, 2.6) & t:
        s.put(x, y, col)


def ring(s, t, rx, ry, cy, col):
    m = (ell(CX, cy, rx, ry) - ell(CX, cy, rx - 1.2, ry - 0.9)) & t
    for (x, y) in m:
        s.put(x, y, col)


def twinkle(s, x, y, level, c=WHITE, c2=None):
    if level <= 0:
        return
    s.put(x, y, c)
    if level >= 2:
        for a, b in N4:
            s.put(x + a, y + b, c2 or c)
    if level >= 3:
        for a, b in N4:
            s.put(x + 2 * a, y + 2 * b, c2 or c)


def surface(name, t):
    m = set(t)
    for (x, y) in t:
        for a, b in N4:
            m.add((x + a, y + b))
    SURFACE[name] = m


def pip(s, x, y, col, hi=None):
    """2 x 2 rarity pip with an ink setting; (x, y) is its top-left pixel."""
    for a in range(-1, 3):
        for b in range(-1, 3):
            if (a in (-1, 2)) != (b in (-1, 2)):
                s.put(x + a, y + b, INK)
    for a in (0, 1):
        for b in (0, 1):
            s.put(x + a, y + b, col)
    s.put(x, y, hi or lt(col, 1.2))


def pip_xs(n, step=5):
    """Left pixels of n pips centred on the base."""
    x0 = CX - 1 - (n - 1) * step / 2.0
    return [int(round(x0 + k * step)) for k in range(n)]


# ------------------------------------------------------------------ common

def common_frame(i=0):
    s = Spr(W, H)
    c = RARITY["common"]
    t, side = tier(s, 21, 9, 12, 8, c)
    # moulded plastic stand: a groove round the wall, a bevel under the lip,
    # a mould ring and two peg holes on top
    for (x, y) in offset_band(t, side, 6, 6):
        s.put(x, y, dk(c, 1.3))
    for (x, y) in offset_band(t, side, 7, 7):
        s.put(x, y, lt(c, 0.6) if x < CX + 9 else c)
    for (x, y) in offset_band(t, side, 1, 1):
        if x < CX + 9:
            s.put(x, y, lt(c, 0.5))
    ring(s, t, 18.5, 7.6, 12, dk(c, 0.45))
    contact(s, t, dk(c, 0.45))
    for x in (11, 44):
        s.put(x, 12, dk(c, 1.6))
        s.put(x, 11, lt(c, 1.4))
    pip(s, CX - 1, 23, dk(c, 1.6), lt(c, 0.4))
    surface("base_common", t)
    return s


# ------------------------------------------------------------------ uncommon

def uncommon_frame(i=0):
    s = Spr(W, H)
    c = RARITY["uncommon"]
    tier(s, 24, 10, 16, 3, dk(c, 0.6))
    t, side = tier(s, 21, 9, 12, 4, c)
    for (x, y) in offset_band(t, side, 2, 3):
        s.put(x, y, PAPER if x < CX + 9 else CREAM)
    ring(s, t, 18, 7.4, 12, c)
    contact(s, t, c)
    # name plate
    plate = box(21, 21, 34, 26, r=1)
    part(s, plate, PAPER, sc=CREAM)
    for x in pip_xs(2, 5):
        for (a_, b_) in ((0, 0), (1, 0), (0, 1), (1, 1)):
            s.put(x + a_, 23 + b_, GREEN)
        s.put(x, 23, lt(GREEN, 1.2))
    for x in (22, 33):                              # plate screws
        s.put(x, 24, dk(CREAM, 1.5))
    for x in range(8, 49, 5):                       # notches on the foot ring
        fy = front_y(24, 10, 16, x)
        if fy is not None and not (20 <= x <= 35):
            s.put(x, fy + 2, dk(c, 1.6))
    # slow glint crossing the plate
    g = {1: 22, 2: 26, 3: 30}.get(i)
    if g is not None:
        for k in range(4):
            q = (g + 2 - k, 22 + k)
            if q in plate and s.get(q[0], q[1]) in (PAPER, CREAM):
                s.put(q[0], q[1], WHITE)
    surface("base_uncommon", t)
    return s


# ------------------------------------------------------------------ rare

def rare_frame(i=0):
    s = Spr(W, H)
    c = RARITY["rare"]
    deep = dk(c, 1.5)
    t2, side2 = tier(s, 25, 10, 16, 3, deep, top=c, lip=lt(c, 1.2))
    for x in range(4, 53, 4):                       # rivet dots on the lower wall
        fy = front_y(25, 10, 16, x)
        if fy is not None and (x, fy + 2) in side2:
            s.put(x, fy + 2, lt(c, 1.3))
    t, side = tier(s, 18, 8, 12, 4, c)
    for (x, y) in offset_band(t, side, 4, 4):
        s.put(x, y, deep)
    ring(s, t, 15, 6.4, 12, c)
    contact(s, t, c)
    studs = []
    for deg in (-72, -52, -32, -11, 11, 32, 52, 72):
        x = int(round(CX - 0.5 + 17.2 * math.sin(math.radians(deg))))
        fy = front_y(18, 8, 12, x)
        studs.append((x, fy + 1))
    for k, (x, y) in enumerate(studs):
        lit = (k == i % len(studs))
        col = WHITE if lit else PAPER
        for a in (0, 1):
            for b in (0, 1):
                s.put(x + a, y + b, col)
        s.put(x + 1, y + 1, lt(c, 1.2) if lit else STEEL_SH)
        s.put(x, y + 2, INK)
        s.put(x + 1, y + 2, INK)
        if lit:
            for (a, b) in ((-1, 0), (2, 0), (0, -1), (1, -1), (-2, 0), (3, 0)):
                if s.get(x + a, y + b) is not None:
                    s.put(x + a, y + b, WHITE)
    # light sweeping over the lower deck
    p = -8 + (i % 10) * 8
    for (x, y) in t2 - t:
        if p <= x + (y - 16) * 2 < p + 3 and s.get(x, y) == c and (x, y + 1) in t2:
            s.put(x, y, lt(c, 1.4))
    # navy plate with three pips
    plate = box(19, 23, 36, 28, r=1)
    part(s, plate, NAVY, sc=dk(NAVY, 0.6))
    for x in pip_xs(3, 5):
        for (a_, b_) in ((0, 0), (1, 0), (0, 1), (1, 1)):
            s.put(x + a_, 25 + b_, SKY)
        s.put(x, 25, WHITE)
    surface("base_rare", t)
    return s


STEEL_SH = hx("8a93a3")
NAVY = hx("1f3a8a")
LEAF = hx("ffd84a")


# ------------------------------------------------------------------ epic

def gem(s, x, y, c, level):
    """3 x 3 cut gem with an ink setting; level 0..3 is its sparkle."""
    for a in range(-2, 3):
        for b in range(-2, 3):
            if abs(a) + abs(b) == 2 and s.get(x + a, y + b) is not None:
                s.put(x + a, y + b, INK)
    for a, b in N4:
        s.put(x + a, y + b, c)
    s.put(x, y, lt(c, 1.3))
    s.put(x + 1, y, dk(c, 0.8))
    s.put(x, y + 1, dk(c, 0.8))
    if level >= 1:
        s.put(x, y, WHITE)
        s.put(x - 1, y, WHITE)
    if level >= 2:
        s.put(x, y - 1, WHITE)
        twinkle(s, x - 1, y - 1, level - 1)


def epic_frame(i=0):
    s = Spr(W, H)
    c = RARITY["epic"]
    deep = dk(c, 1.4)
    gold = MUST
    n = 12
    # finials first so the tiers overlap their feet
    for flip in (False, True):
        post = box(4, 12, 5, 21)
        orb = ell(5, 8.5, 2.6, 2.6)
        if flip:
            post, orb = M(post), M(orb)
        part(s, post, gold)
        part(s, orb, PINK)
        ox = min(q[0] for q in orb)
        oy = min(q[1] for q in orb)
        s.put(ox + 1, oy + 1, WHITE)
        ph = (i + (4 if flip else 0)) % n
        if ph in (0, 1, 2):
            twinkle(s, ox + 1, oy + 1, (2, 3, 2)[ph], WHITE)
    t3, side3 = tier(s, 26.5, 9.5, 17, 3, deep, top=c, lip=gold)
    t2, side2 = tier(s, 21.5, 8, 15, 2, c, top=lt(c, 0.5), lip=gold)
    for x in range(8, 49, 3):                       # bead row on the middle tier
        fy = front_y(21.5, 8, 15, x)
        if fy is not None and (x, fy + 2) in side2:
            s.put(x, fy + 2, gold)
    t, side = tier(s, 16.5, 6.5, 12, 3, c, lip=gold)
    for (x, y) in offset_band(t, side, 3, 3):
        s.put(x, y, deep)
    ring(s, t, 14, 5.2, 12, gold)
    contact(s, t, c)
    # gold drops along the bottom tier
    for x in range(7, 50, 6):
        fy = front_y(26.5, 9.5, 17, x)
        if fy is not None and (x, fy + 2) in side3:
            s.put(x, fy + 2, gold)
            s.put(x + 1, fy + 2, lt(gold, 1.0))
    # four gem pips on the front of the top tier: they light up one by one,
    # then all together
    gems = []
    for x in (15, 23, 32, 40):
        gems.append((x, front_y(16.5, 6.5, 12, x) + 3))
    for k, (x, y) in enumerate(gems):
        level = 0
        if i == 2 * k:
            level = 2
        elif i == 2 * k + 1:
            level = 3
        elif i == 2 * k + 2:
            level = 1
        if i == 9:
            level = 3
        elif i == 10:
            level = 2
        gem(s, x, y, SKY, level)
    surface("base_epic", t)
    return s


# ------------------------------------------------------------------ legendary

LEAF_OUT = ((0, 0), (0, 1), (1, 1), (2, 1), (1, 2), (2, 2), (3, 2), (2, 3))   # points up-left
LEAF_IN = tuple((3 - a, b) for (a, b) in LEAF_OUT)                           # points up-right


def laurel(flip):
    """Left laurel branch (mirrored if flip): (stem pixels, leaf masks bottom to top)."""
    p0, pc, p1 = (12.5, 25.0), (0.5, 21.0), (9.5, 3.0)
    n = 200
    stem, leaves = [], []
    last = None
    travelled = 0.0
    nxt = 3.0
    for k in range(n + 1):
        u = k / float(n)
        a, b, d = (1 - u) ** 2, 2 * (1 - u) * u, u * u
        x = a * p0[0] + b * pc[0] + d * p1[0]
        y = a * p0[1] + b * pc[1] + d * p1[1]
        if last is not None:
            travelled += math.hypot(x - last[0], y - last[1])
        last = (x, y)
        ix, iy = int(math.floor(x)), int(math.floor(y))
        stem.append((ix, iy))
        if travelled >= nxt:
            nxt += 4.2
            leaves.append({(ix - 4 + a_, iy - 3 + b_) for (a_, b_) in LEAF_OUT})
            leaves.append({(ix + 1 + a_, iy - 5 + b_) for (a_, b_) in LEAF_IN})
    leaves = [{q for q in l if 1 <= q[0] <= 12 and q[1] >= 1} for l in leaves]
    stem = [q for q in stem if 1 <= q[0] <= 12 and q[1] >= 1]
    if flip:
        return [(W - 1 - x, y) for (x, y) in stem], [M(l) for l in leaves]
    return stem, leaves


def orbit_star(s, x, y, big):
    m = {(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)}
    if big:
        m |= {(x - 2, y), (x + 2, y), (x, y - 2), (x, y + 2)}
    outline(s, m)
    for q in m:
        s.put(q[0], q[1], PAPER)
    s.put(x, y, WHITE)


def legendary_frame(i=0):
    s = Spr(W, H)
    c = RARITY["legendary"]
    deep = dk(c, 1.2)
    hl = hx("fff0a8")
    n = 12
    stars = []
    for k in range(3):
        a = 2 * math.pi * (i / float(n) + k / 3.0 + 0.125)   # frame 0: no star over the sash
        stars.append((int(round(CX - 0.5 + 26 * math.cos(a))), int(math.floor(20.5 + 4.5 * math.sin(a))), math.sin(a) > 0))
    for (x, y, front) in stars:                     # far side of the ring, behind the base
        if not front and 2 <= x <= 53:
            orbit_star(s, x, y, False)
    t3, side3 = tier(s, 23.5, 9, 17.5, 3, c, top=lt(c, 0.6), lip=hl, hl=hl, sd=deep)
    for x in range(6, 51, 3):                       # fluting on the bottom tier
        fy = front_y(23.5, 9, 17.5, x)
        if fy is not None and (x, fy + 2) in side3:
            s.put(x, fy + 2, deep)
            s.put(x, fy + 3, deep)
    t2, side2 = tier(s, 20, 8, 15, 2, c, top=lt(c, 0.6), lip=hl, hl=hl, sd=deep)
    for x in range(10, 47, 2):                      # red bead row
        fy = front_y(20, 8, 15, x)
        if fy is not None and (x, fy + 2) in side2:
            s.put(x, fy + 2, RED)
    t, side = tier(s, 16.5, 6.5, 12, 3, c, top=c, lip=hl, hl=hl, sd=deep)
    velvet = ell(CX, 12, 14.5, 5.3) & t
    for (x, y) in velvet:
        s.put(x, y, RED)
    for (x, y) in velvet:
        if (x, y - 1) not in velvet:
            s.put(x, y, DRED)
    contact(s, velvet, DRED)
    # laurels
    for flip in (False, True):
        stem, leaves = laurel(flip)
        outline(s, set(stem))
        for q in stem:
            s.put(q[0], q[1], deep)
        for j, l in enumerate(leaves):
            if not l:
                continue
            outline(s, l)
            for q in l:
                s.put(q[0], q[1], LEAF)
            for q in l:
                if (q[0] + 1, q[1] + 1) not in l and (q[0], q[1] + 1) not in l:
                    s.put(q[0], q[1], c)
            top_q = min(l, key=lambda q: (q[1], q[0]))
            s.put(top_q[0], top_q[1], PAPER)
            if (i + j + (5 if flip else 0)) % n == 0:
                twinkle(s, top_q[0], top_q[1], 2)
        # ribbon knot at the foot
        kx = 11 if not flip else W - 12
        part(s, {(kx, 24), (kx + 1, 24), (kx, 25), (kx + 1, 25)}, RED, sh=False)
    # red sash with five stars, lit in a chase
    plaque = box(15, 20, 41, 26, r=1) | {(14, 22), (14, 23), (14, 24), (42, 22), (42, 23), (42, 24)}
    part(s, plaque, RED, sc=DRED)
    for (x, y) in plaque:
        if y == 20:
            s.put(x, y, lt(RED, 0.8))
    for k, x in enumerate((18, 23, 28, 33, 38)):
        lit = (i // 2) % 6 == k or (i // 2) % 6 == 5
        col = WHITE if lit else hl
        for (a_, b_) in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            s.put(x + a_, 23 + b_, col)
        s.put(x, 23, WHITE)
        if lit:
            for (a_, b_) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                s.put(x + a_, 23 + b_, hl)
    # shimmer sweeping over the gold walls
    p = -6 + i * 7
    gold_px = side | side2 | side3
    for (x, y) in gold_px:
        if p <= x + (y - 20) < p + 2 and s.get(x, y) in (c, deep, hl) and (x, y) not in plaque:
            s.put(x, y, WHITE)
    for (x, y, front) in stars:                     # near side of the ring
        if front and 2 <= x <= 53:
            orbit_star(s, x, y, True)
    surface("base_legendary", t)
    return s


BASES = [
    # name, frame function, frames, fps
    ("base_common", common_frame, 1, 1),
    ("base_uncommon", uncommon_frame, 6, 4),
    ("base_rare", rare_frame, 8, 8),
    ("base_epic", epic_frame, 12, 8),
    ("base_legendary", legendary_frame, 12, 10),
]

RARITY_BASE = {"common": "base_common", "uncommon": "base_uncommon", "rare": "base_rare",
               "epic": "base_epic", "legendary": "base_legendary"}


def build_bases():
    """Returns {name: (list of 56 x 30 frames, fps)}."""
    out = {}
    for (name, fn, frames, fps) in BASES:
        out[name] = ([fn(i) for i in range(frames)], fps)
    return out
