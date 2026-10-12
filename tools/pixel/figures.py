"""The 30 toy figures as rubber-hose characters, 40 x 40 each, plus their idle loops.

Contract: .orchestrator/plans/2026-10-11-17-45-forge-rubber-hose/art-contract.md,
section B. Every figure is assembled from the shared part helpers of `Fig`
(tall-oval eyes, black noodle limbs, white gloves with a cuff, big shoes) so the
thirty read as one family; a recipe per figure name adds the body, the prop and
the pose that make the toy what its name says.

Coordinates are continuous inside the 40 x 40 canvas (pixel x covers x..x+1,
the centre line is x = 20). Feet stand on the bottom row, centred on x = 20.
No base is drawn here: bases live in bases.py.

Idle loops: every recipe is a function of the frame index `f.i`. Frame 0 is the
static sprite; the other frames move the body (`f.bob`, a 1 px squash over the
planted shoes), blink (`f.blink`), wave a hand or work the prop. `ANIM` gives
the frame count and fps of each figure (varied on purpose so a shelf of figures
does not pulse in unison).
"""
import math
from contextlib import contextmanager

from pixlib import Spr, hx, shade, ell, box, poly, line, shift, clip

W = 40
OFF = 12

# contract palette
INK = hx("161320")
RED = hx("e2231a")
DRED = hx("9c1420")
ORANGE = hx("f0802a")
MUST = hx("f2b632")
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
WHITE = (255, 255, 255)
# sparing extensions
BROWN = hx("a8683a")
WOOD = hx("c58a4a")
PURPLE = hx("8a5fc8")
LILAC = hx("c9b0f0")
TEAL = hx("2fb3b0")
LIME = hx("9ccf4a")
YEL = hx("ffd84a")
INDIGO = hx("4a4ab8")
SOOT = hx("2c2838")      # "black" fur / lacquer, a step above the ink
GLOVE_SH = hx("e3d5b5")

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))

# figure name -> (frames, fps) of its idle loop
ANIM = {
    "Bubble Bird": (8, 6), "Nap Frog": (8, 4), "Tin Robo": (6, 6), "Moon Bunny": (8, 5),
    "Golden Daruma": (6, 5), "Ramune Bear": (8, 6), "Kite Fox": (6, 6), "Drum Tanuki": (4, 8),
    "Comet Owl": (10, 5), "Star Kaiju": (6, 7), "Mochi Seal": (8, 7), "Dango Chick": (6, 4),
    "Taiyaki Fish": (8, 8), "Melon Turtle": (10, 4), "Royal Pudding": (6, 8), "Rocket Pup": (4, 7),
    "Saturn Snail": (8, 4), "Astro Monkey": (6, 5), "Nebula Jelly": (8, 6), "Galaxy Dragon": (8, 5),
    "Sleepy Panda": (10, 4), "Cloud Sheep": (6, 4), "Tiger Cub": (6, 8), "Thunder Oni": (4, 6),
    "Lucky Whale": (10, 6), "Bell Mouse": (6, 6), "Coin Toad": (8, 5), "Koi Kite": (8, 8),
    "Lantern Ghost": (8, 5), "Treasure Kappa": (10, 5),
}
GENERIC_ANIM = (6, 6)

WAVE4 = [(0, 0), (1, -1), (2, 0), (1, -1)]


def dk(c, k=1.15):
    return shade(c, -k)


def lt(c, k=1.0):
    return shade(c, k)


def M(m):
    """Mirror a mask around the centre line of the canvas."""
    return {(W - 1 - x, y) for (x, y) in m}


def bez(p0, c, p1, n=64):
    out = []
    for i in range(n + 1):
        t = i / float(n)
        a, b, d = (1 - t) * (1 - t), 2 * (1 - t) * t, t * t
        out.append((a * p0[0] + b * c[0] + d * p1[0], a * p0[1] + b * c[1] + d * p1[1]))
    return out


def stroke(pts, w=2):
    out = set()
    for (x, y) in pts:
        if w == 1:
            out.add((int(math.floor(x)), int(math.floor(y))))
        else:
            ix, iy = int(math.floor(x + 0.5)), int(math.floor(y + 0.5))
            for a in (-1, 0):
                for b in (-1, 0):
                    out.add((ix + a, iy + b))
    return out


def star5(cx, cy, r=2):
    """Diamond-ish four-point star centred on a pixel."""
    return {(cx + a, cy + b) for a in range(-r, r + 1) for b in range(-r, r + 1)
            if abs(a) + abs(b) <= r and (a == 0 or b == 0 or abs(a) + abs(b) < r)}


def wedge(px_, py_, a0, a1, r):
    """Pie slice around a pivot; angles in degrees, -90 is straight up.
    Returns {pixel: (t along the arc 0..1, distance from the pivot)}."""
    out = {}
    for y in range(int(py_ - r) - 1, int(py_ + r) + 2):
        for x in range(int(px_ - r) - 1, int(px_ + r) + 2):
            dx, dy = x + 0.5 - px_, y + 0.5 - py_
            d = math.hypot(dx, dy)
            if d > r:
                continue
            a = math.degrees(math.atan2(dy, dx))
            if d < 1.2 or a0 <= a <= a1:
                out[(x, y)] = (min(1.0, max(0.0, (a - a0) / float(a1 - a0))), d)
    return out


FINGERS = {
    "fist": [],
    "open": [(-2, -3), (-2, -4), (0, -3), (0, -4), (0, -5), (2, -3), (2, -4), (3, 0), (3, -1)],
    "peace": [(-1, -3), (-2, -4), (-2, -5), (1, -3), (2, -4), (2, -5)],
    "point": [(0, -3), (0, -4), (0, -5)],
    "droop": [(-2, 3), (-2, 4), (0, 3), (0, 4), (0, 5), (2, 3), (2, 4)],
}
PALM = [(a, b) for a in range(-2, 3) for b in range(-2, 3) if abs(a) + abs(b) < 4]
PALM_SHADOW = [(2, 0), (2, 1), (1, 2), (0, 2)]


class Fig:
    def __init__(self, look=None, i=0):
        self.look = look or {}
        self.s = Spr(W + 2 * OFF, W + 2 * OFF)
        self.flip = False
        self.pending = []
        self.problems = []
        self.i = i            # idle frame index; 0 is the static sprite
        self.ox = 0           # offset applied to everything painted (the bob)
        self.oy = 0
        self.blink = False
        self.lid = CREAM      # eyelid colour while blinking

    # ------------------------------------------------------------ animation
    def q(self, seq):
        return seq[self.i % len(seq)]

    def on(self, *frames):
        return self.i in frames

    def bob(self, seq):
        self.oy = self.q(seq)

    @contextmanager
    def fixed(self):
        """Paint without the bob (things planted on the ground or floating free)."""
        old = (self.ox, self.oy)
        self.ox, self.oy = 0, 0
        yield
        self.ox, self.oy = old

    @contextmanager
    def off(self, dx=0, dy=0):
        """Paint with an extra offset on top of the bob."""
        old = (self.ox, self.oy)
        self.ox, self.oy = old[0] + dx, old[1] + dy
        yield
        self.ox, self.oy = old

    # ------------------------------------------------------------ painting
    def _put(self, x, y, c):
        self.s.put(x + OFF + self.ox, y + OFF + self.oy, c)

    def _m(self, m):
        return M(m) if self.flip else set(m)

    def P(self, m, c, sh=1, gloss=False, sc=None, ink=INK):
        """Outlined part: flat colour, a hard crescent of shadow bottom-right,
        optional white specular streak top-left. Returns the painted mask."""
        m = self._m(m)
        if not m:
            return m
        for (x, y) in m:
            for a, b in N4:
                if (x + a, y + b) not in m:
                    self._put(x + a, y + b, ink)
        sc = sc or dk(c)
        for (x, y) in m:
            col = c
            if sh and ((x + 1, y + 1) not in m or (x + sh, y + sh) not in m):
                col = sc
            self._put(x, y, col)
        if gloss:
            xs = [q[0] for q in m]
            ys = [q[1] for q in m]
            gx = min(xs) + int((max(xs) - min(xs)) * 0.22)
            gy = min(ys) + int((max(ys) - min(ys)) * 0.2)
            # vinyl-toy specular: a short streak and a dot under it
            for q in ((gx + 1, gy), (gx, gy + 1), (gx, gy + 2), (gx, gy + 4)):
                if q in m and (q[0] - 1, q[1]) in m and (q[0], q[1] - 1) in m:
                    self._put(q[0], q[1], WHITE)
        return m

    def PM(self, m, c, **kw):
        old = self.flip
        self.flip = False
        self.P(m, c, **kw)
        self.flip = True
        self.P(m, c, **kw)
        self.flip = old

    def F(self, m, c):
        m = self._m(m)
        for (x, y) in m:
            self._put(x, y, c)
        return m

    def FM(self, m, c):
        self.F(m, c)
        self.F(M(m), c)

    def px(self, x, y, c):
        if self.flip:
            x = W - 1 - x
        self._put(x, y, c)

    def pts(self, coords, c):
        for (x, y) in coords:
            self.px(x, y, c)

    def sym(self, coords, c):
        for (x, y) in coords:
            self._put(x, y, c)
            self._put(W - 1 - x, y, c)

    # ------------------------------------------------------------ limbs
    def noodle(self, p0, c, p1, w=2, col=INK):
        m = stroke(bez(p0, c, p1), w)
        if col == INK:
            self.F(m, INK)
        else:
            self.P(m, col, sh=0)
        return m

    def arm(self, side, p0, c, hand, kind="fist", cuff=True):
        """Black noodle arm ending in a white glove. Coordinates are given for
        the LEFT side of the picture; side = +1 mirrors the arm to the right.
        The glove itself is painted last (see hands), over body and props."""
        old = self.flip
        self.flip = side > 0
        self.noodle(p0, c, hand, 2)
        gx, gy = int(math.floor(hand[0])), int(math.floor(hand[1]))
        dx, dy = hand[0] - c[0], hand[1] - c[1]
        n = math.hypot(dx, dy) or 1.0
        ux, uy = dx / n, dy / n
        if cuff:
            cx_, cy_ = gx - int(round(4 * ux)), gy - int(round(4 * uy))
            qx, qy = int(round(-uy)), int(round(ux))
            self.P({(cx_, cy_), (cx_ + qx, cy_ + qy), (cx_ - qx, cy_ - qy)}, GLOVE, sh=0)
        self.pending.append((self.flip, gx, gy, kind, self.ox, self.oy))
        self.flip = old

    def hands(self):
        old = (self.flip, self.ox, self.oy)
        self.flip = False
        for (flip, gx, gy, kind, ox, oy) in self.pending:
            self.ox, self.oy = ox, oy
            sgn = -1 if flip else 1
            ax = W - 1 - gx if flip else gx
            palm = {(ax + a, gy + b) for (a, b) in PALM}
            fingers = {(ax + sgn * a, gy + b) for (a, b) in FINGERS[kind]}
            self.P(palm | fingers, GLOVE, sh=0)
            self.F({(ax + a, gy + b) for (a, b) in PALM_SHADOW}, GLOVE_SH)
            if kind == "fist":
                # knuckle creases
                self.F({(ax - 1, gy - 2), (ax - 1, gy - 1), (ax + 1, gy - 2), (ax + 1, gy - 1)}, GLOVE_SH)
            elif kind in ("open", "peace", "point"):
                # crease where the fingers meet the palm
                self.F({(ax - sgn, gy - 2), (ax + sgn, gy - 2)}, GLOVE_SH)
        self.pending = []
        self.flip, self.ox, self.oy = old

    def shoe(self, cx, c, toe=1.5):
        m = clip(ell(cx, 36.6, 4, 2.4) | ell(cx - toe, 37.2, 4, 1.9), y1=38)
        m = self.P(m, c, sh=1)
        for (x, y) in m:
            if y == 38:
                self._put(x, y, dk(c))
        # glossy toe cap: a white streak with a soft highlight under it
        self.px(int(cx - toe - 1), 35, WHITE)
        self.px(int(cx - toe), 35, WHITE)
        self.px(int(cx - toe - 2), 36, lt(c, 0.9))
        self.px(int(cx - toe + 1), 35, lt(c, 0.9))

    def legs(self, hip_y=29, hip_dx=3, foot_dx=6.5, shoe=RED, toe=1.5):
        """Noodle legs: the hips follow the bob, the shoes stay planted."""
        old = (self.flip, self.ox, self.oy)
        ox, oy = self.ox, self.oy
        self.ox, self.oy = 0, 0
        for flip in (False, True):
            self.flip = flip
            sx = -ox if flip else ox
            self.noodle((20 - hip_dx + sx, hip_y + oy), (20 - hip_dx - 1.5 + sx * 0.5, hip_y + 3 + oy * 0.5),
                        (20 - foot_dx + 1, 35), 2)
            self.shoe(20 - foot_dx, shoe, toe)
        self.flip, self.ox, self.oy = old

    # ------------------------------------------------------------ faces
    def eye(self, x, y, w=3, h=5, gaze=1):
        """Tall-oval eye: white oval, black pupil pushed to the gaze side.
        While blinking the lid (body colour) comes down over it."""
        m = box(x, y, x + w - 1, y + h - 1, r=1 if (w >= 3 and h >= 4) else 0)
        if self.blink:
            self.P(m, self.lid, sh=0)
            self.F({(a, y + h - 2) for a in range(x, x + w)} & m, INK)
            return
        self.P(m, GLOVE, sh=0)
        pw = 2 if w <= 4 else w // 2
        if w <= 2:
            pw = 1
        if gaze > 0:
            cols = range(x + w - pw, x + w)
        elif gaze < 0:
            cols = range(x, x + pw)
        else:
            cols = range(x + (w - pw) // 2, x + (w - pw) // 2 + pw)
        self.F({(a, b) for a in cols for b in range(y + 1, y + h)} & m, INK)

    def eyes(self, x, y, w=3, h=5, gaze=1, gap=1):
        """Two touching tall-oval eyes; x is the first white column."""
        self.eye(x, y, w, h, gaze)
        self.eye(x + w + gap, y, w, h, gaze)

    def pie(self, x, y, w=3, h=4):
        """Pie eye: black oval with a little white slice."""
        if self.blink:
            self.pts([(x, y + 2), (x + 1, y + 3), (x + 2, y + 2)], INK)
            return
        self.F(box(x, y, x + w - 1, y + h - 1, r=1), INK)
        self.px(x + w - 1, y + 1, WHITE)

    def sleepy(self, x, y, w=5, c=INK):
        self.pts([(x, y)] + [(a, y + 1) for a in range(x + 1, x + w - 1)] + [(x + w - 1, y)], c)

    def smile(self, x0, x1, y, c=INK):
        self.pts([(a, y) for a in range(x0, x1 + 1)] + [(x0 - 1, y - 1), (x1 + 1, y - 1)], c)

    def blush(self, x, y, c=PINK):
        self.sym([(x, y), (x + 1, y)], c)

    def spark(self, x, y, level, c=WHITE):
        """Tiny twinkle: 0 nothing, 1 a dot, 2 a plus."""
        if level >= 1:
            self._put(x, y, c)
        if level >= 2:
            for a, b in N4:
                self._put(x + a, y + b, c)

    # ------------------------------------------------------------ output
    def done(self, name):
        self.hands()
        bb = self.s.img.getbbox()
        if bb is None:
            self.problems.append("%s: empty" % name)
            return Spr(W, W)
        x0, y0, x1, y1 = bb[0] - OFF, bb[1] - OFF, bb[2] - OFF, bb[3] - OFF
        if x0 < 0 or y0 < 0 or x1 > W or y1 > W:
            self.problems.append("%s frame %d: content spills out of 40x40 (x %d..%d, y %d..%d)"
                                 % (name, self.i, x0, x1 - 1, y0, y1 - 1))
        out = Spr(W, W)
        out.img.paste(self.s.img.crop((OFF, OFF, OFF + W, OFF + W)), (0, 0))
        out.p = out.img.load()
        return out


def torso(f, c, belly=None, cy=25, rx=5.5, ry=5):
    t = f.P(ell(20, cy, rx, ry), c, sh=1)
    if belly:
        f.F(ell(20, cy + 1, rx - 2, ry - 1.5) & t, belly)
    return t


def hand(p, d):
    return (p[0] + d[0], p[1] + d[1])


# ------------------------------------------------------------------ machine 1: Pocket Pals

def bubble_bird(f):
    c = TEAL
    f.lid = c
    f.bob([0, 0, 1, 1, 0, 0, 0, 0])
    f.blink = f.on(5)
    wv = f.q(WAVE4)
    f.legs(28, shoe=ORANGE)
    # tail feathers
    f.P(poly([(27, 21), (36, 18), (34.5, 22.5), (36.5, 26), (28, 28)]), dk(c), sh=0)
    f.pts([(32, 21), (33, 21), (32, 24), (33, 25)], c)
    f.P(poly([(16.5, 9), (15.5, 3.5), (19, 6.5), (20.5, 1.5), (22, 6.5), (25.5, 4), (24, 9)]), c, sh=0)
    b = f.P(ell(20, 18.5, 10, 10.5), c, sh=2, gloss=True)
    f.F(ell(20, 24.5, 6, 4.5) & b, CREAM)
    f.pts([(17, 24), (18, 25), (19, 24), (21, 26), (22, 27), (23, 26)], dk(CREAM, 0.8))
    f.arm(-1, (10.5, 20), (4, 25), hand((5.5, 13.5), wv), "open")
    f.arm(1, (10.5, 19), (-2, 24), (10.5, 27.5))
    f.eyes(16, 12)
    f.P(box(17, 19, 22, 20) | box(18, 21, 21, 21), ORANGE, sh=1)
    f.pts([(18, 19), (19, 19)], lt(ORANGE, 0.9))
    f.blush(13, 18)
    with f.fixed():
        by = f.q([0, 0, -1, -1, -2, -1, -1, 0])
        f.P(ell(33.5, 7.5 + by, 3, 3), SKY, sh=0)
        f.pts([(32, 6 + by), (32, 7 + by), (33, 5 + by)], WHITE)
        f.px(35, 9 + by, lt(SKY, 0.8))
        f.P(ell(29, 13 + f.q([0, 0, 0, -1, -1, -1, 0, 0]), 1.2, 1.2), SKY, sh=0)


def nap_frog(f):
    c = hx("5cbf5a")
    br = f.q([0, 0, 0, 1, 1, 1, 1, 0])           # breathing in lifts the back
    body = ell(20, 23.5 - br * 0.5, 12, 9.5 + br * 0.5) | ell(13, 13.5 - br, 5, 5) | ell(27, 13.5 - br, 5, 5)
    b = f.P(body, c, sh=2, gloss=True)
    f.F(ell(20, 28, 7.5, 5) & b, CREAM)
    f.pts([(18, 27), (19, 28), (20, 28), (21, 27)], dk(CREAM, 0.8))
    with f.off(0, -br):
        for ex in (10, 24):
            f.F(ell(ex + 3, 13, 3.6, 3.4), lt(c, 0.9))
            # heavy closed lid with lashes
            f.pts([(ex, 13), (ex, 14), (ex + 1, 15), (ex + 2, 15), (ex + 3, 15), (ex + 4, 15), (ex + 5, 15),
                   (ex + 6, 14), (ex + 6, 13), (ex + 1, 14), (ex + 5, 14)], INK)
            f.pts([(ex - 1, 15), (ex + 3, 17), (ex + 7, 15)], INK)
        f.smile(16, 23, 21)
        f.pts([(18, 18), (21, 18)], dk(c))
        f.blush(11, 20)
    # snot bubble that swells with every breath
    r = f.q([2.2, 2.2, 2.6, 3.0, 3.4, 3.4, 3.0, 2.6])
    f.P(ell(27.5 + r, 19.5, r, r), SKY, sh=0)
    f.pts([(27 + int(r * 0.5), 18)], WHITE)
    # soles facing the viewer: it sits with its legs stretched out
    for flip in (False, True):
        f.flip = flip
        f.P(clip(ell(11.5, 35.3, 4, 3.4), y1=38), ORANGE, sh=1)
        f.F(ell(11.5, 35.5, 2, 1.5), lt(ORANGE, 0.8))
        f.pts([(9, 33), (11, 32), (13, 33)], dk(ORANGE, 0.8))
    f.flip = False
    f.arm(-1, (8.5, 22), (3, 30), (14.5, 28.5 - br))
    f.arm(1, (8.5, 22), (2, 27), (5.5, 30.5))
    # Z z drifting up
    zy = f.q([0, 0, 0, -1, -1, -1, -2, -2])
    f.pts([(31, 7 + zy), (32, 7 + zy), (33, 7 + zy), (32, 8 + zy), (31, 9 + zy), (32, 9 + zy), (33, 9 + zy)], INK)
    f.pts([(35, 3 + zy), (36, 3 + zy), (36, 4 + zy), (35, 5 + zy), (36, 5 + zy)], INK)


def tin_robo(f):
    c = MUST
    f.lid = CREAM
    f.bob([0, 0, 1, 0, 0, 1])
    f.blink = f.on(4)
    turn = f.q([0, 0, 0, 1, 1, 1])
    wv = f.q([(0, 0), (1, -1), (2, 0), (1, -1), (0, 0), (0, 0)])
    f.legs(30, shoe=RED)
    # wind-up key, turning
    f.P(box(9, 25, 13, 26), STEEL, sh=0)
    if turn:
        f.P(box(6, 24, 7, 27), STEEL, sh=1)
    else:
        f.P(box(5, 22, 8, 29, r=1), STEEL, sh=1)
        f.F(box(6, 24, 7, 27), INK)
    f.arm(-1, (14, 22), (8, 23), hand((7.5, 14.5), wv), "open")
    f.arm(1, (14, 23), (7, 23), (7.5, 29.5))
    f.P(box(14, 21, 25, 30, r=1), c, sh=1)
    f.P(box(17, 24, 22, 28), CREAM, sh=0)
    f.pts([(18, 25), (19, 25), (18, 26), (19, 26)], f.q([RED, RED, RED, YEL, YEL, RED]))
    f.pts([(21, 25), (21, 27), (18, 28), (19, 28), (20, 28), (21, 28)], DSTEEL)
    f.pts([(15, 22), (24, 22), (15, 29)], dk(c, 1.6))           # rivets
    f.F(box(19, 3, 20, 6), INK)
    lamp = f.q([RED, RED, YEL, RED, RED, YEL])
    f.P(ell(20, 2.5, 2, 2), lamp, sh=1)
    f.px(19, 2, WHITE)
    f.PM(box(8, 11, 9, 16), STEEL)
    f.P(box(10, 6, 29, 20, r=2), c, sh=2)
    f.F(box(12, 7, 27, 8), lt(c, 0.9))
    f.pts([(12, 10), (27, 10), (12, 18)], dk(c, 1.6))           # rivets
    f.P(box(13, 10, 26, 18, r=1), CREAM, sh=0)
    f.eyes(16, 11, 3, 4)
    f.F(box(16, 16, 23, 17), INK)
    f.pts([(17, 16), (19, 16), (21, 16)], PAPER)
    f.sym([(14, 15), (14, 16)], PINK)


def moon_bunny(f):
    c, sc = hx("fbe6ee"), hx("e2b0c8")
    f.lid = c
    f.bob([0, 0, 1, 1, 0, 0, 0, 0])
    f.blink = f.on(6)
    e = f.q([0, 0, 1, 1, 1, 0, 0, 0])            # the flopped ear dips
    f.legs(30, shoe=BLUE)
    f.P(ell(27, 28.5, 2.2, 2.2), PAPER, sh=0)
    f.arm(1, (15, 24), (5, 26), (6.5, 15.5 + f.q([0, 0, 0, -1, -1, 0, 0, 0])))
    f.arm(-1, (15, 22.5), (2, 26), (13.5, 28.5))
    f.P(ell(20, 26.5, 5, 4.5), c, sh=1, sc=sc)
    f.pts([(19, 26), (20, 27), (21, 26)], sc)
    ears = ell(24.5, 7.5, 2.6, 6.5) | ell(15.5, 9, 2.6, 4) | poly(
        [(17.5, 7), (14, 2.5 + e), (7, 3 + 2 * e), (6.5, 6.5 + 2 * e), (13, 9.5)])
    f.P(ell(20, 15.5, 8.5, 7) | ears, c, sh=2, sc=sc, gloss=False)
    f.F(box(24, 4, 25, 10), PINK)
    f.pts([(9, 5 + 2 * e), (10, 5 + 2 * e), (11, 5 + e), (12, 5 + e), (13, 5 + e), (14, 6)], PINK)
    f.pts([(14, 12), (14, 13), (15, 11)], WHITE)
    f.eyes(16, 13)
    f.pts([(19, 19), (20, 19)], PINK)
    f.pts([(18, 20), (19, 21), (20, 21), (21, 20)], INK)
    f.blush(13, 19)
    with f.fixed():
        cres = ell(33.5, 7.5, 4.5, 4.5) - ell(35.5, 6, 3.8, 3.8)
        f.P(cres, MUST, sh=1)
        f.pts([(30, 6), (30, 7)], PAPER)
        f.spark(36, 3, f.q([0, 1, 2, 1, 0, 0, 0, 0]), PAPER)
        f.spark(37, 12, f.q([1, 0, 0, 0, 0, 1, 2, 1]), PAPER)


def golden_daruma(f):
    c = MUST
    f.lid = CREAM
    f.bob([0, 0, 1, 1, 0, 0])
    f.blink = f.on(4)
    rot = f.q([0, -7, -14, -7, 0, 0])
    f.legs(30, hip_dx=4, shoe=RED)
    b = f.P(clip(ell(20, 18, 13, 12.5), y1=30), c, sh=2, gloss=True)
    f.pts([(20, 6), (19, 7), (21, 7)], RED)                       # top-knot mark
    # folding fan (sensu): a red and paper pleated wedge opening from the glove
    wd = wedge(34.5, 12.5, -168 + rot, -62 + rot, 8.6)
    f.P(set(wd), PAPER, sh=0)
    for q_, (t, d) in wd.items():
        if d < 2.6:
            col = dk(WOOD, 1.2)
        elif d > 7.2:
            col = MUST
        else:
            col = RED if int(t * 6.999) % 2 == 0 else PAPER
        f.F({q_}, col)
    f.arm(1, (7.5, 20), (1, 20), (5.5, 13.5))
    f.arm(-1, (8.5, 18), (-3, 23), (9.5, 26.5))
    f.P(ell(20, 15, 8.5, 6.5), CREAM, sh=0)
    f.sym([(13, 9), (14, 9), (15, 10), (16, 10), (17, 11), (13, 10), (14, 10), (15, 11), (16, 11)], INK)
    f.eyes(15, 12, 4, 5)
    f.sym([(15, 18), (16, 19), (17, 19), (18, 18), (14, 17)], INK)           # moustache
    f.sym([(12, 16), (13, 16)], RED)
    f.F(box(19, 23, 20, 28), RED)
    f.sym([(13, 23), (14, 24), (15, 25), (16, 26), (15, 22), (16, 23), (17, 24), (11, 26), (12, 27)], RED)
    f.pts([(19, 29), (20, 29)], dk(c, 1.4))


# ------------------------------------------------------------------ machine 2: Festival Friends

def ramune_bear(f):
    c = BLUE
    f.lid = c
    f.bob([0, 0, 1, 1, 0, 0, 1, 1])
    f.blink = f.on(5)
    wv = f.q([(0, 0), (1, -1), (2, 0), (1, -1), (0, 0), (0, 0), (0, 0), (0, 0)])
    f.legs(29, shoe=RED)
    f.arm(-1, (15, 22.5), (6, 26), hand((6.5, 16.5), wv), "open")
    f.arm(1, (15, 23), (6, 27), (6.5, 17.5))
    torso(f, c, CREAM)
    head = ell(20, 13, 9, 7.5) | ell(12.5, 6.5, 3.3, 3.3) | ell(27.5, 6.5, 3.3, 3.3)
    f.P(head, c, sh=2, gloss=True)
    f.FM(ell(12.5, 6.5, 1.5, 1.5), PINK)
    f.F(ell(20, 16.5, 4, 3), CREAM)
    f.eyes(16, 9)
    f.pts([(19, 15), (20, 15)], INK)
    f.pts([(18, 17), (19, 18), (20, 18), (21, 17)], INK)
    f.blush(12, 15)
    # the soda bottle, with its marble and a rising bubble
    f.P(box(31, 6, 35, 15, r=1) | box(32, 3, 34, 5), SKY, sh=1)
    f.P(box(32, 1, 34, 2), RED, sh=0)
    f.F(box(31, 10, 35, 12), PAPER)
    f.pts([(32, 11), (33, 11), (34, 11)], RED)
    f.pts([(32, 7), (32, 8)], WHITE)
    f.px(33, 4, BLUE)
    f.px(34, f.q([14, 13, 9, 8, 7, 14, 13, 9]), WHITE)


def kite_fox(f):
    c = ORANGE
    f.lid = c
    f.bob([0, 0, 1, 1, 0, 0])
    f.blink = f.on(3)
    kx = f.q([0, 1, 2, 2, 1, 0])
    tw = f.q([0, 0, 1, 1, 1, 0])
    with f.off(tw, 0):
        t = f.P(ell(32, 22.5, 4.5, 8), c, sh=1)
        f.F(clip(t, y1=18), PAPER)
        f.pts([(30, 19), (31, 20), (33, 19), (34, 20)], PAPER)
    f.legs(29, shoe=NAVY)
    f.arm(-1, (15, 22.5), (6, 26), (5.5 + kx * 0.5, 18.5))
    f.arm(1, (15, 21.5), (2, 25), (13.5, 27.5))
    torso(f, c, PAPER)
    ear = poly([(11.5, 11), (11, 1.5), (18, 7.5)])
    cheek = poly([(12, 14), (8, 18), (14, 19.5)])
    h = f.P(ell(20, 14, 8.5, 7) | ear | M(ear) | cheek | M(cheek), c, sh=2, gloss=True)
    f.F(ell(20, 20.5, 10, 4.5) & h, PAPER)
    f.FM(clip(ear, y1=4), SOOT)
    f.eyes(16, 11, gaze=-1)
    f.pts([(19, 17), (20, 17)], INK)
    f.pts([(18, 19), (19, 19), (20, 19), (21, 19)], INK)
    f.blush(12, 17)
    # the paper kite tugging on its string
    with f.fixed():
        k = f.P(poly([(5.5 + kx, 1), (10 + kx, 7), (5.5 + kx, 14), (1 + kx, 7)]), MUST, sh=0)
        f.pts([(5 + kx, y) for y in range(2, 13)] + [(x + kx, 6) for x in range(2, 9)], RED)
        f.pts([(3 + kx, 5), (7 + kx, 5), (3 + kx, 8), (7 + kx, 8)], PAPER)
        f.F(line(5 + kx, 14, 5 + (kx + 1) // 2, 16), INK)


def drum_tanuki(f):
    c, d = BROWN, hx("5b3520")
    f.lid = d
    beat_l = f.q([0, 3, 0, 0])
    beat_r = f.q([0, 0, 0, 3])
    f.bob([0, 1, 0, 1])
    t = f.P(ell(32.5, 27.5, 3.5, 5.5), c, sh=1)
    f.F({q for q in t if q[1] in (24, 25, 28, 29)}, d)
    f.legs(31, hip_dx=4, shoe=RED)
    f.PM(ell(12.5, 6.5, 2.8, 2.8), c, sh=0)
    f.FM(ell(12.5, 6.8, 1.2, 1.2), d)
    b = f.P(ell(20, 13, 9, 7) | ell(20, 24, 10.5, 8), c, sh=2, gloss=True)
    # the belly is the drum
    f.P(ell(20, 25, 6.5, 5.5), CREAM, sh=1)
    hit = beat_l or beat_r
    f.F(ell(20, 25, 3.2 if hit else 2.2, 3.2 if hit else 2.2), RED)
    f.pts([(19, 24), (20, 25)], CREAM)
    if hit:
        f.sym([(11, 21), (10, 23), (11, 28)], PAPER)
    f.F(ell(15.5, 13.5, 3.6, 3) | ell(24.5, 13.5, 3.6, 3), d)
    f.eye(14, 11, 3, 4)
    f.eye(23, 11, 3, 4)
    f.F(ell(20, 16.5, 3, 2), CREAM)
    f.pts([(19, 15), (20, 15)], INK)
    f.pts([(19, 17), (20, 17)], dk(CREAM, 1.5))
    f.P(ell(21, 5.5, 3.5, 1.8), GREEN, sh=0)
    f.pts([(20, 5), (21, 5), (22, 5)], lt(GREEN, 0.8))
    for flip, dy in ((False, beat_l), (True, beat_r)):
        f.flip = flip
        with f.off(0, dy):
            f.P(line(5, 11, 3 + (1 if dy else 0), 5), WOOD, sh=0)
            f.P(ell(3 + (1 if dy else 0), 4, 1.2, 1.2), RED, sh=0)
    f.flip = False
    f.arm(-1, (10, 21), (3, 22), (5.5, 14.5 + beat_l))
    f.arm(1, (10, 21), (3, 22), (5.5, 14.5 + beat_r))


def comet_owl(f):
    c = PURPLE
    f.bob([0, 0, 0, 1, 1, 0, 0, 0, 1, 1])
    blink = f.on(6)
    look = f.q([0, 0, -2, -2, 0, 0, 0, 0, 0, 0])
    f.legs(30, shoe=MUST)
    tuft = poly([(11.5, 14), (9.5, 1.5), (17.5, 9)])
    f.arm(1, (12, 20), (4, 21), (6.5, 13.5), "point")
    b = f.P(box(11, 9, 28, 30, r=5) | tuft | M(tuft), c, sh=2, gloss=True)
    f.arm(-1, (11.5, 19), (-1, 23), (11.5, 26.5))
    f.F(ell(20, 25, 6, 5.5) & b, LILAC)
    for (x, y) in ((16, 23), (20, 23), (14, 26), (18, 26), (22, 26)):
        f.pts([(x, y), (x + 1, y + 1), (x + 2, y)], c)
    f.sym([(12, 4), (12, 5), (13, 6)], LILAC)
    if blink:
        f.P(ell(15.5, 15, 4, 4), LILAC, sh=0)
        f.P(ell(24.5, 15, 4, 4), LILAC, sh=0)
        f.F(box(13, 16, 18, 16) | box(22, 16, 27, 16), INK)
    else:
        f.P(ell(15.5, 15, 4, 4), GLOVE, sh=0)
        f.P(ell(24.5, 15, 4, 4), GLOVE, sh=0)
        f.F(box(17 + look, 13, 18 + look, 17) | box(22 + look, 13, 23 + look, 17), INK)
        f.pts([(17 + look, 13), (22 + look, 13)], WHITE)
    f.P({(18, 19), (19, 19), (20, 19), (21, 19), (19, 20), (20, 20)}, MUST, sh=0)
    # the comet it points at
    with f.fixed():
        r = f.q([2, 2, 3, 2, 2, 2, 1, 2, 2, 3])
        f.P(star5(34, 5, r), MUST, sh=0)
        f.px(34, 5, PAPER)
        tail = f.q([2, 3, 3, 2, 2, 1, 1, 2, 3, 3])
        f.pts([(37, 2), (38, 1)][:max(0, tail - 1)], PAPER)


def star_kaiju(f):
    c = hx("22a394")
    f.lid = c
    f.bob([0, 1, 0, 0, 1, 0])
    f.blink = f.on(5)
    up = f.q([0, -1, -2, -2, -1, 0])
    roar = f.on(2, 3)
    tl = f.q([0, 0, 1, 1, 0, 0])
    f.P(poly([(23, 26), (31, 25), (34.5, 19 - tl), (37.5, 20.5 - tl), (36.5, 28), (31, 32.5), (23, 32.5)]), c, sh=1)
    f.P(poly([(32.5, 20 - tl), (37, 14.5 - tl), (37.5, 21 - tl)]), MUST, sh=0)
    f.pts([(30, 27), (33, 26), (27, 28)], dk(c, 0.8))
    f.legs(29, shoe=ORANGE)
    f.arm(-1, (15, 22.5), (7, 27), (6.5, 17.5 + up), "open")
    f.arm(1, (15, 22.5), (7, 27), (6.5, 17.5 + up), "open")
    torso(f, c, CREAM)
    # star badge on the belly
    f.F(star5(19, 25, 2) | star5(20, 25, 2), RED)
    f.pts([(19, 25), (20, 25)], YEL)
    f.P(poly([(17.5, 6.5), (20, 0.8), (22.5, 6.5)]), MUST, sh=0)
    sp = poly([(11.5, 9.5), (11.5, 3), (16.5, 7)])
    f.PM(sp, MUST, sh=0)
    head = ell(20, 12.5, 9, 7.5)
    h = f.P(head, c, sh=2, gloss=True)
    f.F(ell(20, 16.5, 6, 3.5) & h, lt(c, 0.8))
    f.eyes(16, 8)
    f.pts([(18, 14), (21, 14)], INK)
    if roar:
        f.F(box(14, 16, 25, 19, r=1), INK)
        f.pts([(15, 16), (17, 16), (19, 16), (21, 16), (23, 16), (16, 19), (22, 19)], WHITE)
        f.pts([(18, 18), (19, 18), (20, 18), (21, 18)], RED)
    else:
        f.F(box(14, 17, 25, 17), INK)
        f.pts([(15, 18), (17, 18), (22, 18), (24, 18)], WHITE)
    f.blush(12, 15, lt(c, 1.2))


# ------------------------------------------------------------------ machine 3: Snack Squad

def mochi_seal(f):
    c = PAPER
    f.lid = c
    f.blink = f.on(5)
    clap = f.q([0, 0, 1, 2, 1, 0, 1, 2])
    fl = f.q([0, 0, -1, -2, -1, 0, 1, 0])
    spin = f.q([0, 0, 1, 1, 2, 2, 3, 3])
    f.arm(1, (18, 24), (12, 22), (11.5 + clap, 16.5), "open")
    tail = poly([(30, 31), (34, 23), (31.5, 18.5 + fl), (35.5, 20.5 + fl), (38, 17.5 + fl), (38.6, 23.5 + fl),
                 (36.5, 27), (34.5, 35)])
    body = ell(13, 13.5, 6.5, 6.5) | ell(15.5, 25, 8, 10) | clip(ell(22.5, 32.2, 11, 6.8), y1=38)
    f.P(poly([(27, 35), (34, 36), (35, 38.9), (26, 38.9)]), dk(c, 0.7), sh=1)
    f.P(body | tail, c, sh=2)
    f.P(poly([(11, 34), (6, 36), (6, 38.9), (14, 38.9)]), dk(c, 0.7), sh=1)
    f.pie(9, 11)
    f.pie(14, 11)
    f.pts([(11, 15), (12, 15), (13, 15)], INK)
    f.pts([(10, 16), (11, 17), (12, 16), (13, 17), (14, 16)], INK)
    f.pts([(7, 15), (8, 15), (16, 15), (17, 15)], PINK)
    f.pts([(8, 17), (16, 17), (9, 18), (15, 18)], dk(c))
    f.pts([(35, 21 + fl), (36, 22 + fl), (33, 25)], dk(c))
    f.pts([(12, 27), (13, 28), (14, 28), (20, 33), (21, 34)], dk(c, 0.5))
    # the mochi ball spinning on its nose
    f.P(ell(13, 3.8, 3.5, 3), PINK, sh=1)
    hl = [(11, 2), (13, 1), (15, 3), (13, 5)][spin]
    f.pts([hl, (hl[0], hl[1] + 1)], WHITE)
    f.pts([(11, 6), (12, 6), (13, 6), (14, 6)], GREEN)
    f.arm(-1, (9, 24), (3, 25), (3.5 + clap, 18.5), "open")


def dango_chick(f):
    c = YEL
    f.lid = c
    f.bob([0, 0, 1, 1, 0, 0])
    f.blink = f.on(4)
    wv = f.q([(0, 0), (1, -1), (2, 0), (1, -1), (0, 0), (0, 0)])
    f.legs(31, shoe=ORANGE)
    f.P(box(33, 3, 33, 30), WOOD, sh=0)
    for (y, col) in ((4.5, PINK), (10.5, PAPER), (16.5, LIME)):
        f.P(ell(33.5, y, 2.5, 2.5), col, sh=1)
        f.px(32, int(y - 1), WHITE)
    f.arm(1, (11.5, 23), (7, 28), (6.5, 22.5))
    f.arm(-1, (12, 22), (5, 25), hand((5.5, 14.5), wv), "open")
    f.P(poly([(18, 9), (17, 4.5), (20, 7), (22.5, 3.5), (23, 9)]), c, sh=0)
    b = f.P(ell(20, 15, 8, 7.5) | ell(20, 24, 9, 7.5), c, sh=2, gloss=True)
    f.pts([(12, 24), (13, 25), (12, 26), (27, 24), (26, 25), (27, 26)], dk(c, 0.9))     # wing marks
    f.eyes(16, 12)
    f.P({(18, 19), (19, 19), (20, 19), (21, 19), (19, 20), (20, 20)}, ORANGE, sh=0)
    f.blush(13, 18)


def taiyaki_fish(f):
    c, d = hx("e09a3e"), hx("a85f1e")
    f.lid = c
    f.blink = f.on(6)
    tw = f.q([0, 1, 2, 1, 0, -1, -2, -1])
    wv = f.q([(0, 0), (0, -1), (1, -1), (0, -1), (0, 0), (0, 0), (0, 0), (0, 0)])
    f.legs(27, hip_dx=3.5, foot_dx=7, shoe=PAPER)
    f.arm(1, (15, 24), (9, 27), (9.5, 31.5))
    tail = poly([(27, 19), (33.5, 11 + tw), (38, 12 + tw), (36, 19 + tw), (38, 26 + tw), (33.5, 27 + tw), (27, 20)])
    fin = poly([(13, 12), (19, 6), (25, 12)])
    body = ell(18.5, 19, 12, 8.5)
    f.P(body | tail | fin, c, sh=2, gloss=True)
    for y in (15, 18, 21):
        for x in range(17 + ((y // 3) % 2) * 2, 28, 4):
            if (x + 3, y + 2) in body:
                f.pts([(x, y), (x + 1, y + 1), (x + 2, y + 1), (x + 3, y)], d)
    f.pts([(33, 15 + tw), (34, 14 + tw), (33, 19 + tw), (34, 19 + tw), (33, 23 + tw), (34, 24 + tw), (18, 9), (20, 9)], d)
    f.pts([(15, 13), (16, 14), (16, 15), (16, 16), (16, 17), (16, 18), (16, 19), (16, 20), (16, 21), (16, 22), (15, 23)], d)
    f.eyes(8, 14, 3, 5, gaze=-1)
    f.pts([(8, 22), (9, 23), (10, 23), (11, 23), (12, 22)], INK)
    f.pts([(13, 21), (14, 21)], PINK)
    # a peek of red-bean filling at the bite mark
    f.pts([(22, 11), (23, 12)], DRED)
    f.arm(-1, (9, 23), (2, 22), hand((4.5, 13.5), wv), "peace")


def melon_turtle(f):
    c, shell, net = LIME, hx("f3e58f"), hx("b3a445")
    f.lid = c
    f.blink = f.on(7)
    nod = f.q([0, 0, 0, 1, 2, 2, 1, 0, 0, 0])
    wv = f.q([(0, 0), (1, -1), (2, 0), (1, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)])
    f.P(poly([(29, 28), (34.5, 30.5), (29, 32.5)]), c, sh=0)
    f.legs(31, hip_dx=4, shoe=MUST)
    f.arm(-1, (10.5, 21), (4, 24), hand((4.5, 14.5), wv), "open")
    f.arm(1, (10.5, 22), (4, 22), (5.5, 28.5))
    f.P(ell(20, 23.5, 11, 9.5), GREEN, sh=1)
    s = f.P(ell(20, 23.5, 9, 7.8), shell, sh=1)
    f.F({q for q in s if ((q[0] + q[1]) % 5 == 0 or (q[0] - q[1]) % 5 == 0)
         and (q[0] + 1, q[1]) in s and (q[0] - 1, q[1]) in s}, net)
    f.pts([(14, 19), (15, 18), (14, 20)], WHITE)
    with f.off(0, nod):
        f.P({(19, 3), (20, 3), (19, 2), (20, 2), (20, 1), (21, 1), (22, 1)}, BROWN, sh=0)
        f.P(ell(20, 9.5, 6.5, 6), c, sh=2, gloss=True)
        f.eyes(16, 7, 3, 4)
        f.smile(18, 21, 13)
        f.blush(15, 12)


def royal_pudding(f):
    c, car = hx("ffd070"), hx("8a4a22")
    f.lid = c
    f.blink = f.on(4)
    sx = f.q([0, 1, 0, -1, 0, 0])                 # the jiggle
    sp = f.q([0, -1, -1, 0, 1, 0])
    f.legs(30, hip_dx=4, shoe=RED)
    with f.off(0, sp):
        f.P(line(5, 8, 5, 24), STEEL, sh=0)
        f.P(ell(5.5, 5.5, 2.5, 3.5), STEEL, sh=1)
        f.pts([(4, 4), (4, 5)], WHITE)
    body = poly([(12.5 + sx, 10), (27.5 + sx, 10), (31.5, 28), (29.5, 30.9), (10.5, 30.9), (8.5, 28)])
    f.P(body, c, sh=2)
    f.arm(-1, (10, 22), (5, 27), (5.5, 20.5 + sp))
    f.arm(1, (9.5, 20), (-3, 24), (9.5, 26.5))
    with f.off(sx, 0):
        f.P(ell(20, 10, 8, 3.2), car, sh=0)
        f.F(ell(20, 9.5, 6, 1.8), lt(car, 0.7))
        f.pts([(13, 13), (13, 14), (17, 13), (18, 13), (18, 14), (18, 15), (23, 13), (26, 13), (26, 14), (27, 15),
               (12, 12), (27, 12)], car)
        crown = box(15, 5, 24, 7) | {(15, y) for y in range(2, 5)} | {(24, y) for y in range(2, 5)}
        crown |= {(x, y) for x in (19, 20) for y in range(1, 5)} | {(16, 4), (18, 4), (21, 4), (23, 4)}
        f.P(crown, MUST, sh=1)
        f.pts([(17, 6), (22, 6)], RED)
        f.pts([(19, 6), (20, 6)], BLUE)
        f.pts([(15, 2), (24, 2), (19, 1)], PAPER)
        f.eyes(16, 16)
        f.smile(18, 21, 23)
        f.blush(13, 22)
        f.pts([(13, 16), (13, 17), (12, 19), (12, 21)], WHITE)


# ------------------------------------------------------------------ machine 4: Space Patrol

def rocket_pup(f):
    c = PAPER
    f.lid = c
    f.bob([0, 1, 0, 1])
    flap = f.q([0, 1, 2, 1])
    pump = f.q([0, -1, 0, 1])
    f.legs(30, shoe=BLUE)
    f.PM(poly([(14.5, 23), (8, 31.5), (14.5, 31.5)]), DRED, sh=0)
    f.arm(-1, (14, 22), (3, 24), (4.5, 9.5 + pump))
    f.arm(1, (14, 22), (2, 25), (12.5, 27.5))
    f.P(box(14, 20, 25, 30, r=2), RED, sh=1)
    f.F(box(15, 20, 24, 21), STEEL)
    f.pts([(16, 20), (19, 20), (22, 20)], lt(STEEL, 0.9))
    f.P(ell(20, 26, 2.2, 2.2), SKY, sh=0)
    f.px(19 + (flap == 2), 25, WHITE)
    f.pts([(15, 23), (15, 28), (24, 23)], lt(RED, 0.9))
    h = f.P(ell(20, 12, 8.5, 7.5), c, sh=2)
    f.F(ell(24.5, 10, 3.5, 3.8) & h, hx("d79a55"))
    f.PM(poly([(12.5, 6.5), (8 - flap * 0.5, 9), (6.5 - flap, 17.5 - flap * 0.5), (9 - flap, 20 - flap * 0.5),
               (12.5, 16.5), (13.5, 10)]), BROWN, sh=1)
    f.eyes(16, 8)
    f.F({(18, 14), (19, 14), (20, 14), (21, 14), (19, 15), (20, 15)}, INK)
    f.px(19, 14, DSTEEL)
    f.pts([(17, 16), (18, 17), (21, 17), (22, 16)], INK)
    f.pts([(19, 17), (20, 17), (19, 18), (20, 18)], PINK)
    f.blush(13, 14)


def saturn_snail(f):
    c, pl = LILAC, ORANGE
    f.lid = GLOVE_SH
    f.blink = f.on(3)
    sw = f.q([0, 0, 1, 1, 0, 0, -1, -1])
    back, front = set(), set()
    order = []
    for i in range(400):
        t = i * math.pi * 2 / 400
        x = 25 + 12.3 * math.cos(t)
        y = 19.5 + 3.3 * math.sin(t) + 0.3 * (x - 25)
        q = (int(math.floor(x)), int(math.floor(y)))
        (front if math.sin(t) > 0.05 else back).add(q)
        (front if math.sin(t) > 0.05 else back).add((q[0], q[1] + 1))
        if math.sin(t) > 0.05 and q not in order:
            order.append(q)
    f.P(back, CREAM, sh=0)
    foot = poly([(3, 34), (7, 30.5), (31, 30.5), (37.5, 36), (37.5, 38.9), (3, 38.9)])
    f.noodle((7, 18), (4.5, 13), (4.5 + sw, 9), 2)
    f.noodle((11, 18), (12.5, 14), (12.5 + sw, 8), 2)
    f.P(foot | ell(9, 25, 4.5, 8.5), c, sh=2)
    p = f.P(ell(25, 19.5, 9, 9), pl, sh=2, gloss=True)
    f.F({q for q in p if q[1] in (16, 23, 24) and (q[0] + 2, q[1] + 2) in p}, dk(pl, 0.7))
    f.F({q for q in p if q[1] == 20 and (q[0] + 2, q[1] + 2) in p}, lt(pl, 0.8))
    f.P(front, CREAM, sh=0)
    # a glint travelling along the ring
    g = order[(len(order) - 1 - f.i * len(order) // 8 - 3) % len(order)]
    f.pts([g, (g[0] + 1, g[1])], WHITE)
    with f.off(sw, 0):
        f.eye(2, 3, 4, 6)
        f.eye(10, 2, 4, 6)
    f.pts([(5, 23), (6, 24), (7, 25), (8, 25), (9, 25), (10, 24), (11, 23)], INK)
    f.pts([(5, 26), (6, 26), (11, 26), (12, 26)], PINK)
    f.pts([(x, 37) for x in range(6, 36, 4)], dk(c))
    f.pts([(6, 32), (7, 31)], WHITE)


def astro_monkey(f):
    c, skin = BROWN, hx("f6d9b0")
    f.lid = skin
    f.bob([0, 0, 1, 1, 0, 0])
    f.blink = f.on(4)
    wv = f.q([(0, 0), (0, -1), (0, -2), (0, -1), (0, 0), (0, 0)])
    tl = f.q([0, 1, 2, 1, 0, 0])
    with f.fixed():
        f.noodle((24, 28), (35, 34), (34.5, 24 + tl), 2, col=c)
    f.legs(30, shoe=MUST)
    f.arm(1, (15, 24), (7, 28), hand((6.5, 20.5), wv), "peace")
    f.arm(-1, (15, 23.5), (2, 27), (13.5, 28.5))
    f.P(ell(20, 26.5, 5.5, 4.5), BLUE, sh=1)
    f.pts([(19, 27), (20, 27)], MUST)
    f.pts([(17, 25), (22, 25)], PAPER)
    f.P(ell(20, 13, 11.5, 11), hx("cdeafc"), sh=0)
    f.P(box(15, 23, 24, 24), STEEL, sh=0)
    hd = ell(20, 13.5, 7.5, 6.5)
    f.P(hd | ell(12, 13.5, 2.8, 3) | ell(28, 13.5, 2.8, 3), c, sh=1)
    f.FM(ell(12, 13.5, 1.3, 1.6), skin)
    f.F((ell(17.3, 12.5, 3.2, 3.2) | ell(22.7, 12.5, 3.2, 3.2) | ell(20, 16, 5, 3.3)) & hd, skin)
    f.eyes(16, 10, 3, 4)
    f.pts([(19, 15), (20, 15)], dk(skin, 1.6))
    f.smile(17, 22, 17)
    f.blush(14, 16)
    # glass glint sliding over the helmet
    gl = f.q([0, 0, 1, 2, 1, 0])
    f.pts([(12 + gl, 6 - gl), (13 + gl, 5 - gl), (14 + gl, 4 - gl), (11, 8 + gl), (11, 9 + gl)], WHITE)
    f.pts([(29, 19), (28, 20)], WHITE)
    f.pts([(27, 3), (28, 2)], INK)
    f.P(ell(29.5, 1.9, 1.2, 1.2), f.q([RED, RED, YEL, YEL, RED, RED]), sh=0)


def nebula_jelly(f):
    c, t = hx("5cc8ee"), hx("b07ae0")
    f.lid = c
    f.blink = f.on(5)
    ph = -f.i * 2 * math.pi / 8.0
    with f.fixed():
        for i, x in enumerate((13, 18, 23, 28)):
            pts = [(x + 1.6 * math.sin((y - 18) / 3.0 + i * math.pi + ph) * min(1.0, (y - 16) / 6.0), y)
                   for y in [18 + k * 0.25 for k in range(84)]]
            f.P(clip(stroke(pts, 2), y1=38), t if i % 2 == 0 else PINK, sh=0)
    f.bob([0, 0, 1, 2, 2, 1, 0, 0])
    wv = f.q([(0, 0), (0, 0), (1, -1), (2, 0), (1, -1), (0, 0), (0, 0), (0, 0)])
    f.arm(-1, (10, 17), (2, 22), hand((4.5, 12.5), wv), "open")
    f.arm(1, (10, 18), (3, 19), (4.5, 25.5), "open")
    bell = clip(ell(20, 14, 12, 11.5), y1=16)
    for x in (10.4, 15.2, 20, 24.8, 29.6):
        bell |= ell(x, 17, 2.6, 2.2)
    f.P(bell, c, sh=2, gloss=True)
    tw = f.i % 4
    stars = [(12, 9), (27, 7), (26, 13), (13, 14), (20, 5)]
    f.pts(stars, t)
    f.pts([stars[tw], stars[(tw + 2) % 5]], WHITE)
    f.pts([(24, 5), (11, 12), (28, 10)], WHITE if tw < 2 else lt(c, 1.2))
    f.eyes(16, 8)
    f.smile(18, 21, 15)
    f.blush(13, 14)


def galaxy_dragon(f):
    c, wc = INDIGO, PURPLE
    f.lid = c
    f.bob([0, 0, 1, 1, 0, 0, 1, 1])
    f.blink = f.on(6)
    wf = f.q([0, 0, 1, 2, 3, 2, 1, 0])
    # bat wings in a lighter purple so the body stays readable
    wing = poly([(15, 25), (8, 22), (6, 24), (3.5, 19 + wf * 0.5), (1.5, 20 + wf * 0.5), (1.5, 7 + wf), (7, 11 + wf * 0.6),
                 (13, 15)])
    f.PM(wing, wc, sh=0)
    f.sym([(3, 10 + wf), (4, 12 + wf), (5, 14 + wf), (6, 16), (7, 18), (8, 20)], LILAC)
    f.sym([(4, 17 + wf // 2)], YEL)
    with f.fixed():
        tl = f.q([0, 0, -1, -1, 0, 0, 1, 1])
        f.noodle((24, 29), (33, 35), (36, 28 + tl), 2, col=c)
        f.P(poly([(34, 28 + tl), (36.5, 24 + tl), (38, 28.5 + tl)]), MUST, sh=0)
    f.legs(29, shoe=RED)
    f.arm(1, (15, 23), (6, 25), (7.5, 15.5))
    f.arm(-1, (15, 21.5), (2, 25), (13.5, 27.5))
    torso(f, c, MUST)
    f.pts([(18, 25), (19, 25), (20, 25), (21, 25)], dk(MUST))
    f.PM(poly([(13.5, 9), (11.5, 1.5), (17, 6.5)]), MUST, sh=0)
    h = f.P(ell(20, 13, 8.5, 7), c, sh=2, gloss=True)
    f.F(ell(20, 17, 5.5, 3) & h, lt(c, 0.9))
    f.eyes(16, 9)
    f.pts([(18, 16), (21, 16)], INK)
    f.pts([(17, 19), (22, 19)], WHITE)
    # the star orb it holds up
    pulse = f.q([0, 0, 1, 2, 1, 0, 1, 2])
    f.P(ell(32.5, 9.5, 3, 3), YEL, sh=1)
    f.pts([(31, 8), (31, 9)], WHITE)
    if pulse:
        f.spark(36, 5, pulse, PAPER)
        f.spark(28, 6, pulse - 1, PAPER)


# ------------------------------------------------------------------ machine 5: Plush Parade

def sleepy_panda(f):
    c, k = PAPER, SOOT
    nod = f.q([0, 0, 0, 1, 1, 2, 2, 2, 1, 0])
    sw = f.q([0, 0, 0, 0, 1, 1, 1, 0, -1, 0])
    f.legs(30, shoe=BLUE)
    f.P(box(31, 23, 37, 32, r=1), PINK, sh=1)
    f.pts([(33, y) for y in range(24, 32)] + [(35, y) for y in range(24, 31)], PAPER)
    f.arm(1, (15, 24), (10, 28), (7.5, 22.5))
    f.arm(-1, (15, 24), (7, 27), (15.5, 21.5 + (nod > 0)))
    t = f.P(ell(20, 26, 5.5, 5), c, sh=1)
    f.F(clip(t, y1=24), k)
    with f.off(0, nod):
        f.PM(ell(11.5, 9.5, 3, 3), k, sh=0)
        f.P(ell(20, 14.5, 9, 7.5), c, sh=2)
        f.F(ell(15.5, 15.5, 3, 3.3) | ell(24.5, 15.5, 3, 3.3), k)
        f.sleepy(13, 15, 5, PAPER)
        f.sleepy(22, 15, 5, PAPER)
        f.pts([(19, 17), (20, 17)], INK)
        if nod == 2:                                   # a yawn
            f.F(box(18, 19, 21, 21, r=1), INK)
            f.pts([(19, 21), (20, 21)], RED)
        else:
            f.F(box(19, 19, 20, 20), INK)
            f.px(19, 20, RED)
        f.blush(11, 18)
        cap = poly([(11, 10), (14.5, 3.5), (21, 1.5), (28, 4), (33, 9.5), (30, 10), (27, 8.5)])
        f.P(cap, BLUE, sh=1)
        f.pts([(16, 5), (20, 4), (24, 5), (27, 7), (18, 7), (22, 7)], PAPER)
        f.P(poly([(10.5, 9), (27.5, 7.5), (28, 9.5), (11, 11.5)]), PAPER, sh=0)
        f.P(ell(33.5 + sw, 12, 2.5, 2.5), PAPER, sh=1)


def cloud_sheep(f):
    c, face = PAPER, hx("3b3550")
    f.lid = face
    f.bob([0, 0, 1, 1, 0, 0])
    f.blink = f.on(3)
    puff = f.q([0, 0, 0.5, 0.5, 0, 0])
    sw = f.q([0, 0, 1, 2, 1, 0])
    f.legs(29, hip_dx=3.5, shoe=PINK)
    f.arm(-1, (8, 22), (3, 23), (3.5, 28.5))
    f.arm(1, (8, 22), (3, 23), (3.5 + sw, 28.5 - sw))
    wool = ell(20, 19, 11, 8)
    for (x, y, r) in ((9.5, 17, 4), (11, 23, 4), (14, 11.5, 4.2), (20, 9.5, 4.5), (26, 11.5, 4.2),
                      (30.5, 17, 4), (29, 23, 4), (23.5, 26, 4), (16.5, 26, 4)):
        wool |= ell(x, y, r + (puff if y > 12 else 0), r)
    f.P(wool, c, sh=2)
    for (x, y) in ((8, 15), (27, 12), (29, 21), (12, 25), (22, 27), (13, 10)):
        f.pts([(x, y + 1), (x + 1, y), (x + 2, y), (x + 3, y + 1)], dk(c))
    f.PM(ell(12.5, 16.5, 2.6, 2.6), MUST, sh=1)
    f.sym([(12, 16), (13, 17)], dk(MUST, 1.6))
    f.sym([(11, 15)], WHITE)
    f.P(ell(20, 19.5, 5.5, 5.5), face, sh=0)
    f.P(ell(20, 13.5, 4, 2.3) | ell(16.5, 14.5, 2, 1.6) | ell(23.5, 14.5, 2, 1.6), c, sh=0)
    f.eyes(16, 17, 3, 4)
    f.pts([(19, 22), (20, 22)], PINK)
    f.sym([(15, 21)], PINK)


def tiger_cub(f):
    c = ORANGE
    f.lid = c
    f.bob([0, 0, 1, 0, 0, 0])
    f.blink = f.on(4)
    pump = f.q([0, -1, -2, -1, 0, 0])
    tw = f.q([0, 1, 2, 1, 0, -1])
    with f.fixed():
        tb = bez((16, 29), (4, 35), (5 + tw, 22))
        f.P(stroke(tb, 2), c, sh=0)
        for i in (20, 32, 44, 56):
            x, y = tb[i]
            f.F(stroke([(x, y)], 2), INK)
    f.legs(29, shoe=BLUE)
    f.arm(1, (15, 23), (5, 23), (7.5, 10.5 + pump))
    f.arm(-1, (15, 21.5), (2, 25), (13.5, 27.5))
    torso(f, c, CREAM)
    f.sym([(15, 24), (16, 24), (15, 27), (16, 27)], INK)
    f.PM(ell(12.5, 6.5, 3.2, 3.2), c, sh=0)
    f.FM(ell(12.5, 6.5, 1.4, 1.4), CREAM)
    h = f.P(ell(20, 13, 9, 7.5), c, sh=2, gloss=True)
    f.F(box(19, 6, 20, 8), INK)
    f.sym([(16, 6), (16, 7), (11, 12), (12, 12), (11, 14), (12, 14), (13, 14)], INK)
    f.F(ell(20, 17, 4.5, 3) & h, CREAM)
    f.eyes(16, 9)
    f.pts([(19, 15), (20, 15)], PINK)
    f.pts([(17, 17), (18, 18), (19, 17), (20, 17), (21, 18), (22, 17)], INK)
    f.blush(13, 16)


def thunder_oni(f):
    c, k = RED, SOOT
    f.lid = c
    f.bob([0, 1, 0, 0])
    shake = f.q([0, -1, 0, 1])
    with f.fixed():
        arc = set()
        for i in range(200):
            a = math.radians(195 + 150 * i / 199.0)
            arc.add((int(math.floor(20 + 16.5 * math.cos(a))), int(math.floor(16.5 + 13 * math.sin(a)))))
        f.P(arc, DSTEEL, sh=0)
        for n, deg in enumerate((197, 224, 316, 343)):
            a = math.radians(deg)
            x, y = 20 + 16.5 * math.cos(a), 16.5 + 13 * math.sin(a)
            lit = (n + f.i) % 4 == 0
            f.P(ell(int(x) + 0.5, int(y) + 0.5, 2.5, 2.5), YEL if lit else MUST, sh=0 if lit else 1)
            # tomoe comma on every little drum
            f.px(int(x), int(y), WHITE if lit else RED)
            f.px(int(x) - 1, int(y) + 1, RED)
    f.legs(30, shoe=NAVY)
    f.arm(-1, (14, 23), (6, 28), (5.5, 21.5 + shake))
    f.arm(1, (14, 23), (6, 28), (5.5, 21.5 - shake))
    t = f.P(box(14, 21, 25, 30, r=2), c, sh=1)
    f.F(clip(t, y0=26), MUST)
    f.pts([(16, 27), (16, 28), (19, 28), (19, 29), (22, 27), (22, 28), (24, 29)], INK)
    f.PM(poly([(12, 9.5), (12, 2.5), (16.5, 8.5)]), PAPER, sh=0)
    f.sym([(13, 6), (13, 7)], dk(CREAM, 0.9))
    f.P(ell(20, 7.5, 3.5, 2), k, sh=0)
    f.P(box(10, 8, 29, 21, r=3), c, sh=2, gloss=True)
    f.sym([(13, 9), (14, 9), (15, 10), (16, 10), (17, 10), (14, 10)], INK)
    f.eyes(16, 13, 3, 4)
    f.F(box(15, 18, 24, 19), INK)
    f.pts([(16, 18), (23, 18)], WHITE)
    f.blush(12, 17, dk(c, 0.8))


def lucky_whale(f):
    c = BLUE
    f.lid = c
    f.blink = f.on(7)
    sp = f.q([0, 0, 1, 2, 3, 3, 2, 1, 0, 0])
    fl = f.q([0, 0, -1, -1, 0, 0, 1, 1, 0, 0])
    wv = f.q([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (1, -1), (2, 0), (1, -1), (0, 0), (0, 0)])
    tail = poly([(28, 22), (31.5, 14), (28.5, 8 + fl), (33.5, 10.5 + fl), (38, 8 + fl), (37.5, 14 + fl), (34.5, 17.5),
                 (33.5, 26)])
    body = clip(ell(19, 23.5, 13, 9.5), y1=33)
    f.legs(32, hip_dx=4, foot_dx=7, shoe=RED)
    crown = box(9, 12, 16, 14) | {(9, 10), (9, 11), (16, 10), (16, 11), (12, 9), (13, 9), (12, 10), (13, 10),
                                  (12, 11), (13, 11), (10, 11), (15, 11), (11, 11), (14, 11)}
    f.P(crown, MUST, sh=0)
    f.pts([(12, 13), (13, 13)], RED)
    f.pts([(10, 12), (15, 12)], PAPER)
    # the spout
    if sp:
        top = 13 - sp * 3
        m = box(22, top, 23, 14)
        if sp >= 2:
            m |= {(20, top), (21, top - 1), (24, top - 1), (25, top), (19, top + 1), (26, top + 1)}
        if sp >= 3:
            m |= {(18, top + 2), (27, top + 2), (18, top + 3), (27, top + 3)}
        f.P(m, SKY, sh=0)
        f.px(22, top + 1, WHITE)
    f.P(body | tail, c, sh=2, gloss=True)
    belly = {q for q in body if q[1] >= 28 and q[0] <= 27}
    f.F(belly, CREAM)
    f.F({q for q in belly if q[0] % 3 == 0 and q[1] >= 29}, dk(CREAM, 0.8))
    f.pts([(22, 15), (23, 15)], INK)                               # blowhole
    f.eyes(8, 19, 3, 5, gaze=-1)
    f.pts([(7, 26), (16, 26)] + [(x, 27) for x in range(8, 16)], INK)
    f.pts([(16, 23), (17, 23)], PINK)
    f.pts([(33, 12 + fl), (35, 11 + fl)], lt(c, 0.9))
    f.arm(-1, (9, 27), (2, 29), hand((3.5, 22.5), wv), "open")
    f.arm(1, (16, 27), (10, 32), (11.5, 24.5))


# ------------------------------------------------------------------ machine 6: Fortune Parade

def bell_mouse(f):
    c = hx("c9c5d2")
    f.lid = c
    f.bob([0, 0, 1, 1, 0, 0])
    f.blink = f.on(3)
    ring = f.q([0, 1, 1, 0, -1, -1])
    pt = f.q([0, -1, -1, 0, 0, 0])
    with f.fixed():
        f.P(stroke(bez((24, 29), (36, 34), (35 + ring, 25)), 1), PINK, sh=0)
    f.legs(29, shoe=RED)
    f.arm(1, (15, 23), (7, 27), (6.5, 21.5 + pt), "point")
    f.arm(-1, (15, 22.5), (7, 24), (6.5, 28.5))
    torso(f, c)
    f.PM(ell(11, 7.5, 5, 5), c, sh=1)
    f.FM(ell(11, 7.5, 3, 3), PINK)
    f.sym([(9, 6)], lt(PINK, 0.9))
    f.P(ell(20, 14.5, 8, 7), c, sh=2, gloss=True)
    f.F(ell(20, 18, 3.5, 2.5), PAPER)
    f.eyes(16, 11)
    f.pts([(19, 17), (20, 17)], PINK)
    f.pts([(19, 19), (20, 19)], INK)
    f.sym([(12, 17), (13, 17), (12, 19), (13, 19)], INK)
    # red collar and the swinging bell
    f.F(box(16, 21, 23, 21), RED)
    with f.off(ring, 0):
        f.P(ell(20, 24, 3, 3), MUST, sh=1)
        f.pts([(18, 25), (19, 25), (20, 25), (21, 25)], INK)
        f.pts([(19, 26), (20, 26)], INK)
        f.pts([(18, 22), (18, 23)], WHITE)
    if ring:
        f.pts([(20 + ring * 5, 22), (20 + ring * 6, 24), (20 + ring * 5, 26)], PAPER)


def coin_toad(f):
    c = GREEN
    f.lid = c
    f.blink = f.on(6)
    rx = f.q([6.5, 5, 2.6, 1, 2.6, 5, 6.5, 6.5])           # the coin spins
    puff = f.q([0, 0, 0, 0, 0, 0.6, 0.6, 0])
    f.legs(32, hip_dx=6, foot_dx=9, shoe=MUST)
    coin = f.P(ell(20, 7, rx, 6), MUST, sh=2 if rx > 3 else 0, gloss=rx > 5)
    if rx > 4:
        f.F(box(19, 6, 20, 8), INK)                          # square hole of an old coin
        f.pts([(20 - int(rx) + 2, 7), (19 + int(rx) - 2, 7), (19, 3), (20, 11)], dk(MUST, 0.9))
    elif rx > 2:
        f.F(box(19, 6, 20, 8), dk(MUST, 1.4))
    b = f.P(ell(20, 25.5, 13 + puff, 8) | ell(13, 18, 4, 4) | ell(27, 18, 4, 4), c, sh=2, gloss=True)
    f.F(ell(20, 30, 8 + puff, 3.5) & b, hx("e9e2a0"))
    f.eye(12, 16, 3, 4)
    f.eye(25, 16, 3, 4)
    f.smile(11, 28, 25)
    f.pts([(8, 23), (31, 22), (10, 28), (29, 28), (20, 21), (17, 22), (23, 23)], dk(c))
    f.sym([(9, 25), (10, 25)], lt(c, 1.1))
    f.arm(-1, (8.5, 22), (1, 14), (11.5, 9.5), "open")
    f.arm(1, (8.5, 22), (1, 14), (11.5, 9.5), "open")


def koi_kite(f):
    """Koinobori: a carp streamer curling in the wind, hoop mouth up, forked tail out."""
    c = RED
    f.lid = c
    f.bob([0, 0, 1, 1, 0, 0, 0, 0])
    f.blink = f.on(5)
    tw = f.q([0, 1, 2, 1, 0, -1, -2, -1])
    spin = f.i % 2
    wv = f.q([(0, 0), (0, 0), (-1, -1), (-2, 0), (-1, -1), (0, 0), (0, 0), (0, 0)])
    f.legs(30, shoe=PAPER)
    # pole with its pinwheel
    f.P(line(5, 10, 5, 29), WOOD, sh=0)
    tris = (([(5.5, 7.5), (1, 7.5), (1, 3.5)], MUST), ([(5.5, 7.5), (5.5, 3), (9.5, 3)], BLUE),
            ([(5.5, 7.5), (10, 7.5), (10, 11.5)], MUST), ([(5.5, 7.5), (5.5, 12), (1.5, 12)], BLUE))
    for (tri, col) in tris:
        if spin:
            tri = [(11 - x, y) for (x, y) in tri]
        f.P(poly(tri), col, sh=0)
    f.px(5, 7, PAPER)
    f.arm(-1, (13, 20), (8, 25), (5.5, 21.5))
    f.arm(1, (15, 18), (7, 19), hand((8.5, 10.5), wv), "open")
    spine = bez((19, 9.5), (17.5, 31), (32, 24.5 + tw * 0.4), 40)
    body = set()
    for k, (x, y) in enumerate(spine):
        r = 7.2 - 3.4 * k / 40.0
        body |= ell(x, y, r, r)
    tail = poly([(31, 21.5 + tw * 0.4), (35, 14 + tw), (36.5, 19 + tw), (38.8, 17.5 + tw), (38.5, 27 + tw * 0.6),
                 (32, 28.5 + tw * 0.4)])
    b = f.P(body | tail, c, sh=2)
    # white belly band and scales
    for y in (17, 20, 23, 26):
        for x in range(11 + ((y // 3) % 2) * 2, 32, 4):
            arc = [(x, y), (x + 1, y + 1), (x + 2, y + 1), (x + 3, y)]
            if all(q in body and (q[0], q[1] + 2) in body and (q[0] + 2, q[1]) in body and (q[0] - 2, q[1]) in body
                   for q in arc):
                f.pts(arc, PAPER)
    f.F({q for q in tail - body if (q[0] + q[1]) % 3 == 0 and (q[0] + 1, q[1] + 1) in b and (q[0] - 1, q[1]) in b}, MUST)
    # hoop mouth
    f.P(ell(19, 4.2, 6, 2.4), MUST, sh=0)
    f.F(ell(19, 4.2, 4, 1.2), INK)
    f.eyes(15, 8, 3, 5, gaze=-1)
    f.pts([(13, 15), (14, 16), (15, 16), (22, 16), (23, 16), (24, 15)], PAPER)       # gill line
    f.pts([(13, 9), (13, 10), (14, 8)], WHITE)
    f.pts([(22, 13), (23, 13)], PINK)


def lantern_ghost(f):
    """Chochin-obake: a paper lantern ghost with its tongue out, floating over two spirit flames."""
    c, k, rib = hx("fff0c4"), SOOT, hx("e6c27c")
    f.lid = c
    f.bob([0, 0, 1, 2, 2, 1, 0, 0])
    f.blink = f.on(6)
    oy = f.oy
    fk = f.i % 2
    lick = f.q([0, 0, 0, 1, 1, 0, -1, -1])
    with f.fixed():
        wisp = poly([(16, 27 + oy), (24, 27 + oy), (24.5, 31), (22, 34), (23.5, 36.5), (21.5, 38.9), (18.5, 38.9),
                     (19.5, 36), (17, 33.5)])
        f.P(wisp, c, sh=1)
        # hitodama flames
        for (fx, fy, d) in ((7, 33, fk), (33, 30, 1 - fk)):
            fl = ell(fx, fy, 2.4, 2.4) | {(fx - 1 + d, fy - 3), (fx - 1 + d, fy - 4), (fx + d, fy - 3), (fx - 2 + 2 * d, fy - 5)}
            f.P(fl, BLUE, sh=0)
            f.F(ell(fx, fy + 0.3, 1.3, 1.3), SKY)
            f.px(fx - 1, fy, WHITE)
    f.P(clip(ell(20, 5, 5, 4.5) - ell(20, 5, 4, 3.5), y1=4), k, sh=0)
    f.arm(-1, (11, 17), (2, 13), (5.5, 22.5), "droop")
    f.arm(1, (11, 17), (2, 13), (5.5, 22.5), "droop")
    b = f.P(clip(ell(20, 17.5, 10, 11.5), y0=8, y1=27), c, sh=2, gloss=True)
    f.F({q for q in b if q[1] in (10, 19, 25) and (q[0] - 1, q[1]) in b and (q[0] + 1, q[1]) in b}, rib)
    f.P(box(14, 6, 25, 8), k, sh=0)
    f.F(box(15, 6, 24, 6), lt(k, 1.4))
    f.P(box(15, 27, 24, 28), k, sh=0)
    f.eyes(15, 11, 4, 5)
    f.sym([(13, 16), (14, 16)], PINK)
    f.F(ell(20, 21.5, 5.5, 2.3), INK)
    f.pts([(16, 20), (23, 20)], WHITE)                               # two little fangs
    f.P(box(18 + lick, 22, 21 + lick, 28, r=1), RED, sh=1)
    f.pts([(19 + lick, y) for y in range(23, 27)], lt(RED, 0.9))


def treasure_kappa(f):
    c, k, wood = hx("35b587"), SOOT, hx("b5722f")
    f.lid = c
    f.bob([0, 0, 1, 1, 0, 0, 0, 1, 1, 0])
    f.blink = f.on(6)
    tw = f.q([0, 1, 2, 1, 0, 0, 1, 2, 1, 0])
    up = f.q([0, 0, 0, -1, -1, -1, 0, 0, 0, 0])
    f.legs(31, hip_dx=4, shoe=ORANGE)
    # shell on its back, belly plates in front
    f.P(ell(19, 24.5, 9.5, 7.5), BROWN, sh=1)
    f.pts([(11, 22), (11, 26), (12, 29)], dk(BROWN, 1.4))
    t = torso(f, c, CREAM, cy=25, rx=6.5, ry=5.5)
    f.pts([(17, 25), (18, 25), (19, 25), (20, 25), (21, 25), (22, 25), (19, 27), (20, 27)], dk(CREAM, 0.9))
    f.arm(-1, (13, 22), (5, 22), (5.5, 13.5 + up))
    # the gem it shows off
    with f.off(0, up):
        gem = poly([(2, 6.5), (5.5, 2.5), (9, 6.5), (5.5, 11)])
        g = f.P(gem, SKY, sh=1, sc=BLUE)
        f.pts([(4, 5), (5, 4), (4, 6)], WHITE)
        f.pts([(3, 7), (4, 7), (5, 7), (6, 7), (7, 7)], lt(SKY, 0.9))
    f.spark(9, 3 + up, tw)
    f.P(ell(20, 13, 9, 7.5), c, sh=2, gloss=True)
    # spiky hair fringe around the water dish
    fringe = ell(20, 7.2, 8.5, 2.8)
    for x0 in (10.5, 13.5, 16.5, 20.5, 23.5, 26.5):
        fringe |= poly([(x0, 8), (x0 + 3, 8), (x0 + 1.5, 11.6)])
    f.P(fringe, k, sh=0)
    f.P(ell(20, 6.2, 5.5, 1.9), SKY, sh=0)
    gx = f.q([17, 17, 18, 19, 20, 21, 22, 22, 20, 18])
    f.pts([(gx, 6), (gx + 1, 6)], WHITE)
    f.eyes(16, 12, 3, 4)
    f.P(box(16, 17, 23, 19, r=1), MUST, sh=1)
    f.pts([(18, 17), (21, 17)], dk(MUST, 1.5))
    f.blush(12, 17)
    # little treasure chest tucked under the other arm
    f.P(box(27, 21, 37, 24, r=1), dk(wood), sh=0)
    f.P(box(27, 25, 37, 31), wood, sh=1)
    f.F(box(27, 27, 37, 27), MUST)
    f.F(box(31, 27, 33, 29), MUST)
    f.px(32, 28, INK)
    f.P(ell(32, 24.2, 4.2, 1.6), YEL, sh=0)
    coins = [(30, 24), (32, 23), (34, 24)]
    f.pts([coins[f.i % 3]], WHITE)
    f.arm(1, (13, 23), (8, 30), (10.5, 29.5))


RECIPES = {
    "Bubble Bird": bubble_bird, "Nap Frog": nap_frog, "Tin Robo": tin_robo, "Moon Bunny": moon_bunny,
    "Golden Daruma": golden_daruma, "Ramune Bear": ramune_bear, "Kite Fox": kite_fox,
    "Drum Tanuki": drum_tanuki, "Comet Owl": comet_owl, "Star Kaiju": star_kaiju,
    "Mochi Seal": mochi_seal, "Dango Chick": dango_chick, "Taiyaki Fish": taiyaki_fish,
    "Melon Turtle": melon_turtle, "Royal Pudding": royal_pudding, "Rocket Pup": rocket_pup,
    "Saturn Snail": saturn_snail, "Astro Monkey": astro_monkey, "Nebula Jelly": nebula_jelly,
    "Galaxy Dragon": galaxy_dragon, "Sleepy Panda": sleepy_panda, "Cloud Sheep": cloud_sheep,
    "Tiger Cub": tiger_cub, "Thunder Oni": thunder_oni, "Lucky Whale": lucky_whale,
    "Bell Mouse": bell_mouse, "Coin Toad": coin_toad, "Koi Kite": koi_kite,
    "Lantern Ghost": lantern_ghost, "Treasure Kappa": treasure_kappa,
}


def generic(f):
    """Fallback for a figure without a recipe: a plain rubber-hose blob in its look colour."""
    c = hx(f.look.get("color", "#f2b632"))
    f.lid = c
    f.bob([0, 0, 1, 1, 0, 0])
    f.blink = f.on(4)
    f.legs(29)
    f.arm(-1, (11, 20), (4, 25), hand((5.5, 13.5), f.q(WAVE4)), "open")
    f.arm(1, (11, 20), (4, 22), (5.5, 27.5))
    f.P(ell(20, 18.5, 10, 10.5), c, sh=2, gloss=True)
    f.eyes(16, 13)
    f.smile(18, 21, 21)


def build_figure(fig, i=0):
    """Frame i of the figure's idle loop (0 = the static sprite).
    Returns (Spr 40 x 40, list of problems)."""
    f = Fig(fig.get("look"), i)
    RECIPES.get(fig["name_en"], generic)(f)
    spr = f.done(fig["id"])
    return spr, f.problems


def idle_spec(fig):
    """(frames, fps) of the figure's idle loop."""
    return ANIM.get(fig["name_en"], GENERIC_ANIM)


def build_idle(fig):
    """Returns (list of 40 x 40 frames, fps, problems). Frame 0 is the static sprite."""
    n, fps = idle_spec(fig)
    frames, problems = [], []
    for i in range(n):
        spr, probs = build_figure(fig, i)
        frames.append(spr)
        problems += probs
    return frames, fps, problems
