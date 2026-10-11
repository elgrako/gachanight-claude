"""The 30 vinyl-toy figures, 32 x 32 each.

Every figure is assembled from the shared part helpers of `Fig` and takes its
colours and eye style from the `look` dictionary of data/figures.json. A recipe
per figure name adds the touches that make the toy what its name says; any
figure without a recipe falls back to `generic`, which is driven by `look` alone.
"""
from pixlib import (Spr, INK, DARK, CREAM, CORAL, MINT, MUSTARD, TEAL, BATH, TAN, WOOD, WHITE,
                    PINK, RED, STEEL, GLASS_HI, hx, shade, mix, ell, box, poly, line, path,
                    shift, mir, clip)

OFF = 8
OVERFLOW = []


class Fig:
    def __init__(self, look):
        self.look = look
        self.s = Spr(48, 48)
        self.c = hx(look["color"])
        self.a = hx(look["accent"])
        self.eyek = look.get("eyes", "dot")

    def P(self, m, c, **kw):
        self.s.part(shift(m, OFF, OFF), c, **kw)
        return m

    def PM(self, m, c, **kw):
        """Paint a part and its mirror image."""
        self.P(m, c, **kw)
        self.P(mir(m), c, **kw)

    def F(self, m, c):
        self.s.puts(shift(m, OFF, OFF), c)

    def px(self, x, y, c):
        self.s.put(x + OFF, y + OFF, c)

    def pts(self, coords, c):
        for (x, y) in coords:
            self.px(x, y, c)

    def sym(self, coords, c):
        for (x, y) in coords:
            self.px(x, y, c)
            self.px(31 - x, y, c)

    def eye(self, x, y, kind=None, c=INK, glint=WHITE):
        kind = kind or self.eyek
        if kind == "sleepy":
            self.pts([(x - 1, y + 1), (x, y + 2), (x + 1, y + 2), (x + 2, y + 1)], c)
        elif kind == "small":
            self.pts([(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)], c)
            self.px(x, y, glint)
        elif kind == "big":
            for a in range(3):
                for b in range(3):
                    self.px(x + a, y + b, c)
            self.px(x, y, glint)
        else:
            for b in range(3):
                self.px(x, y + b, c)
                self.px(x + 1, y + b, c)
            self.px(x, y, glint)

    def face(self, y, sep=4, kind=None, mouth="smile", blush=PINK, cx=16):
        lx = cx - sep - 2
        rx = cx + sep
        self.eye(lx, y, kind)
        self.eye(rx, y, kind)
        my = y + 3
        if mouth == "smile":
            self.pts([(cx - 2, my), (cx - 1, my + 1), (cx, my + 1), (cx + 1, my)], INK)
        elif mouth == "dot":
            self.pts([(cx - 1, my), (cx, my)], INK)
        elif mouth == "cat":
            self.pts([(cx - 1, my), (cx, my), (cx - 2, my + 2), (cx - 1, my + 1), (cx, my + 1), (cx + 1, my + 2)], INK)
        if blush:
            self.pts([(lx - 2, my), (lx - 1, my), (rx + 2, my), (rx + 3, my)], blush)

    def feet(self, c, xl=10, w=4, y=29, **kw):
        m = box(xl, y, xl + w - 1, y + 1)
        self.PM(m, c, **kw)

    def done(self, name):
        bb = self.s.img.getbbox()
        if bb[2] - bb[0] > 32 or bb[3] - bb[1] > 32:
            OVERFLOW.append('%s: content %dx%d' % (name, bb[2] - bb[0], bb[3] - bb[1]))
            x0 = max(0, (bb[0] + bb[2]) // 2 - 16)
            crop = Spr(32, 32)
            crop.img.paste(self.s.img.crop((x0, bb[3] - 32, x0 + 32, bb[3])), (0, 0))
            crop.p = crop.img.load()
            return crop
        return self.s.fitted(32, 32, name)


def star(cx, cy):
    return {(cx, cy - 1), (cx - 1, cy), (cx, cy), (cx + 1, cy), (cx, cy + 1)}


def crown_mask(x0, x1, ytop, h=5):
    """Three-point crown: band at the bottom, three teeth."""
    yb = ytop + h - 1
    m = box(x0, yb - 1, x1, yb)
    xm = (x0 + x1) // 2
    for x in (x0, xm, xm + 1, x1):
        for y in range(ytop + (0 if x in (xm, xm + 1) else 1), yb - 1):
            m.add((x, y))
    m |= {(x0 + 1, yb - 2), (x1 - 1, yb - 2), (xm - 1, yb - 2), (xm + 2, yb - 2)}
    return m


# ------------------------------------------------------------------ machine 1: Pocket Pals

def bubble_bird(f):
    c, a = f.c, f.a
    f.PM(box(11, 29, 13, 30) | {(10, 30)}, a, hl=False)
    f.P(poly([(23, 21), (30, 17), (30, 21), (28, 22), (29, 25), (24, 26)]), shade(c, -1))
    f.P({(15, 8), (16, 8), (16, 7), (17, 7), (17, 6), (18, 6), (14, 9), (15, 9), (13, 7), (14, 7), (14, 8)}, c, sh=False)
    body = f.P(ell(16, 19, 10, 10), c, depth=2)
    f.F(ell(16, 25, 6, 3.5) & body, mix(c, CREAM, 0.7))
    f.PM(ell(6.5, 21, 2.5, 3.5), shade(c, -1), hl=False)
    f.face(15, sep=4, mouth=None)
    f.pts([(14, 19), (15, 19), (16, 19), (17, 19)], a)
    f.pts([(15, 20), (16, 20)], shade(a, -1))
    f.pts([(10, 12), (11, 11), (12, 11)], WHITE)


def nap_frog(f):
    c, a = f.c, f.a
    f.PM(box(6, 29, 10, 30), shade(c, -1), hl=False)
    body = ell(16, 21.5, 12, 8.5) | ell(9.5, 13.5, 4, 4) | ell(22.5, 13.5, 4, 4)
    f.P(body, c, depth=2)
    f.F(ell(16, 26, 7, 4) & body, a)
    f.eye(9, 12, "sleepy")
    f.eye(21, 12, "sleepy")
    f.pts([(x, 21) for x in range(11, 21)] + [(10, 20), (21, 20)], INK)
    f.pts([(14, 18), (17, 18)], shade(c, -2))
    f.pts([(7, 20), (8, 20), (23, 20), (24, 20)], PINK)
    # sleep bubble
    f.P(ell(25.5, 9.5, 2.5, 2.5), GLASS_HI, sh=False)
    f.px(24, 8, WHITE)


def tin_robo(f):
    c, a = f.c, f.a
    # wind-up key
    f.P(box(22, 22, 26, 23), STEEL, hl=False, sh=False)
    f.P(box(27, 20, 29, 25) - {(28, 22), (28, 23)}, STEEL, sh=False)
    f.pts([(28, 22), (28, 23)], INK)
    f.PM(box(11, 27, 14, 30), shade(c, -1), hl=False)
    f.PM(box(6, 19, 8, 25), STEEL)
    f.PM(box(5, 25, 9, 26), a, hl=False)
    f.P(box(10, 19, 21, 27), c)
    f.F(box(13, 21, 18, 25), a)
    f.pts([(14, 22), (15, 22)], WHITE)
    f.pts([(17, 22), (17, 24), (14, 24), (15, 24)], INK)
    f.P(box(15, 4, 16, 5), STEEL, hl=False, sh=False)
    f.P(ell(16, 3, 2, 2), a)
    f.PM(box(5, 10, 7, 14), a)
    f.P(box(8, 6, 23, 18, r=1), c, depth=2)
    f.F(box(10, 9, 14, 13), CREAM)
    f.F(box(17, 9, 21, 13), CREAM)
    f.pts([(12, 10), (13, 10), (12, 11), (13, 11), (12, 12), (13, 12)], INK)
    f.pts([(19, 10), (20, 10), (19, 11), (20, 11), (19, 12), (20, 12)], INK)
    f.pts([(12, 10), (19, 10)], WHITE)
    f.F(box(12, 15, 19, 16), DARK)
    f.pts([(13, 15), (15, 15), (17, 15), (13, 16), (15, 16), (17, 16)], CREAM)


def moon_bunny(f):
    c, a = f.c, f.a
    f.PM(box(10, 29, 14, 30), c)
    body = f.P(ell(16, 25.5, 6.5, 5), c)
    f.P(ell(24, 25.5, 2, 2), WHITE, sh=False)
    ear_l = ell(11.5, 8, 2.5, 6)
    ear_r = ell(20.5, 10, 2.5, 4) | poly([(19, 7), (22, 4), (28, 4), (28.5, 7), (23, 9.5)])
    head = ell(16, 17.5, 9.5, 7)
    f.P(head | ear_l | ear_r, c, depth=2)
    f.F(box(11, 5, 11, 11), a)
    f.F(box(20, 8, 20, 11) | {(21, 7), (22, 6), (23, 6), (24, 6), (25, 6)}, a)
    f.face(16, sep=4, mouth=None)
    f.pts([(15, 19), (16, 19)], a)
    f.pts([(15, 20), (16, 20)], INK)
    # crescent moon charm
    f.pts([(15, 12), (16, 12), (14, 13), (15, 14), (16, 14)], MUSTARD)


def golden_daruma(f):
    c, a = f.c, f.a
    body = clip(ell(16, 20.5, 11.5, 10.5), y1=30)
    f.P(body, c, depth=2)
    f.P(crown_mask(11, 20, 3, h=7), a)
    f.pts([(13, 8), (18, 8), (15, 5), (16, 5)], CREAM)
    face = ell(16, 18, 7.5, 5.5)
    f.P(face, CREAM, hl=False, sh=False)
    # one eye painted, one still blank
    f.pts([(10, 14), (11, 14), (12, 15), (13, 15), (14, 16)], INK)
    f.pts([(21, 14), (20, 14), (19, 15), (18, 15), (17, 16)], INK)
    f.F(box(11, 17, 13, 19), INK)
    f.px(11, 17, WHITE)
    f.F(box(18, 17, 20, 19), INK)
    f.F({(19, 18)}, WHITE)
    f.pts([(14, 21), (15, 22), (16, 22), (17, 21)], INK)
    f.pts([(9, 20), (22, 20)], PINK)
    # red belly marks
    f.pts([(15, 25), (16, 25), (15, 26), (16, 26), (15, 27), (16, 27)], a)
    f.sym([(8, 24), (9, 25), (10, 26), (11, 27), (12, 25), (13, 26)], a)


# ------------------------------------------------------------------ machine 2: Festival Friends

def ramune_bear(f):
    c, a = f.c, f.a
    f.PM(box(10, 28, 14, 30, r=0), c)
    body = f.P(ell(16, 23.5, 6.5, 6.5), c)
    f.F(ell(16, 24.5, 4, 4) & body, a)
    f.P(ell(9, 22, 2.5, 3.5), c, hl=False)
    # ramune bottle
    bottle = hx("8fd3e8")
    f.P(box(24, 17, 28, 26, r=1) | box(25, 13, 27, 16), bottle)
    f.pts([(25, 12), (26, 12), (27, 12)], CORAL)
    f.pts([(24, 12), (28, 12), (25, 11), (26, 11), (27, 11)], INK)
    f.pts([(25, 15), (25, 19), (25, 20)], WHITE)
    f.pts([(24, 22), (25, 22), (26, 22), (27, 22), (28, 22), (24, 23), (25, 23), (26, 23), (27, 23), (28, 23)], a)
    f.P(ell(22.5, 22.5, 2.5, 2.5), c, hl=False)
    head = ell(16, 11.5, 8.5, 7) | ell(9.5, 5.5, 3, 3) | ell(22.5, 5.5, 3, 3)
    f.P(head, c, depth=2)
    f.sym([(9, 5), (9, 6), (10, 5)], shade(c, -1))
    f.F(ell(16, 14.5, 3.5, 2.5), a)
    f.pts([(15, 13), (16, 13)], INK)
    f.pts([(15, 15), (16, 15)], shade(a, -2))
    f.eye(10, 10)
    f.eye(20, 10)
    f.pts([(8, 13), (9, 13), (22, 13), (23, 13)], PINK)


def kite_fox(f):
    c, a = f.c, f.a
    tail = ell(25.5, 22.5, 3.5, 6.5)
    f.P(tail, c, depth=2)
    f.F(clip(tail, y1=18), a)
    # kite on a stick
    f.P(path([(5, 19), (8, 23)]), WOOD, hl=False, sh=False)
    kite = poly([(4, 6.5), (7.5, 12.5), (4, 20), (0.5, 12.5)])
    f.P(kite, MUSTARD)
    f.pts([(3, y) for y in range(8, 19)], RED)
    f.pts([(x, 12) for x in range(1, 7)], RED)
    f.PM(box(11, 28, 14, 30), DARK, hl=False)
    body = f.P(ell(16, 24, 5.5, 6), c)
    f.F(ell(16, 25, 3, 4) & body, a)
    f.P(ell(10.5, 23.5, 2, 2.5), c, hl=False)
    ear = poly([(8.5, 10), (9, 1.5), (15, 7)])
    head = ell(16, 12.5, 7.5, 6.5) | ear | mir(ear) | poly([(8, 13), (8.5, 17.5), (12, 18)]) | mir(poly([(8, 13), (8.5, 17.5), (12, 18)]))
    f.P(head, c, depth=2)
    f.F((ell(16, 18, 8, 3.8) & head), a)
    f.sym([(10, 5), (10, 6), (10, 7), (11, 6), (11, 7), (12, 7)], DARK)
    f.pts([(15, 15), (16, 15)], INK)
    f.pts([(15, 17), (16, 17)], shade(a, -2))
    f.eye(11, 11)
    f.eye(19, 11)


def drum_tanuki(f):
    c, a = f.c, f.a
    tail = ell(27, 23.5, 3, 5)
    f.P(tail, c)
    f.F({q for q in tail if q[1] in (20, 21, 24, 25)}, shade(c, -2))
    f.PM(box(9, 29, 13, 30), shade(c, -2), hl=False)
    ear = poly([(5, 15), (6, 8), (12, 12)])
    body = ell(16, 21.5, 11, 8.5) | ear | mir(ear)
    # leaf on the head
    f.P(ell(17, 10, 4, 2.2) | {(13, 12), (14, 11), (14, 12)}, MINT)
    f.pts([(15, 10), (16, 10), (17, 10), (18, 10)], shade(MINT, -1))
    f.P(body, c, depth=2)
    f.sym([(7, 11), (7, 12), (8, 12)], shade(c, -2))
    belly = ell(16, 24.5, 6.5, 5)
    f.F(belly & body, a)
    f.F({q for q in belly & body if (q[0] + 1, q[1]) not in belly or (q[0], q[1] + 1) not in belly}, shade(a, -1))
    f.pts([(15, 25), (16, 25), (14, 24), (17, 24), (14, 26), (17, 26)], shade(a, -2))
    f.F(ell(11, 17.5, 3, 2.5) | ell(21, 17.5, 3, 2.5), mix(c, INK, 0.5))
    f.eye(10, 16, c=INK)
    f.eye(20, 16, c=INK)
    f.F(ell(16, 19.5, 2.5, 1.5), a)
    f.pts([(15, 18), (16, 18)], INK)
    # drumming paws
    f.PM(ell(8.5, 24, 2, 2), c, hl=False)


def comet_owl(f):
    c, a = f.c, f.a
    f.PM(box(11, 29, 13, 30) | {(10, 30)}, a, hl=False)
    tuft = poly([(7, 11), (5.5, 2.5), (12.5, 7.5)])
    body = box(7, 7, 24, 28, r=4) | tuft | mir(tuft)
    f.P(body, c, depth=2)
    f.F(ell(16, 23, 6, 5.5) & body, shade(c, 1))
    for (x, y) in ((12, 21), (16, 21), (14, 24), (18, 24), (12, 26), (16, 26)):
        f.pts([(x, y), (x + 1, y + 1), (x + 2, y)], c)
    f.PM(ell(6.5, 20, 2.5, 6), shade(c, -1), hl=False)
    f.F(ell(11.5, 14, 4, 4) | ell(20.5, 14, 4, 4), CREAM)
    f.F(box(11, 13, 12, 15) | box(19, 13, 20, 15), INK)
    f.pts([(11, 13), (19, 13)], WHITE)
    f.pts([(15, 16), (16, 16), (15, 17), (16, 17)], a)
    f.pts([(15, 18), (16, 18)], shade(a, -1))
    f.F(star(16, 9) | {(15, 9), (17, 9)}, a)
    f.pts([(18, 8), (19, 7), (20, 6)], a)


def star_kaiju(f):
    c, a = f.c, f.a
    f.P(poly([(19, 25), (26, 25), (29, 20), (31, 21), (30, 27), (26, 30.9), (19, 30.9)]), c, depth=2)
    for tri in ([(21, 7), (26.5, 6), (23, 12.5)], [(22, 14), (27.5, 14.5), (23, 19.5)], [(26, 19), (30.5, 16), (30, 21)]):
        f.P(poly(tri), a, sh=False)
    f.PM(box(9, 28, 14, 30, r=0), c)
    f.sym([(9, 30), (11, 30), (13, 30)], WHITE)
    body = f.P(ell(16, 23, 7, 7), c, depth=2)
    belly = ell(16, 24.5, 4.5, 4.5) & body
    f.F(belly, a)
    f.F({q for q in belly if q[1] in (22, 25, 28)}, shade(a, -1))
    f.PM(ell(8.5, 21.5, 2, 2), c, hl=False)
    f.P(star(16, 3) | {(15, 3), (15, 2), (15, 4), (14, 3)} | {(17, 3)}, a, sh=False)
    head = f.P(ell(16, 11.5, 8.5, 6.5), c, depth=2)
    f.eye(10, 9)
    f.eye(20, 9)
    f.pts([(x, 14) for x in range(11, 21)], INK)
    f.pts([(13, 15), (18, 15)], WHITE)
    f.pts([(14, 12), (17, 12)], shade(c, -2))


# ------------------------------------------------------------------ machine 3: Snack Squad

def mochi_seal(f):
    c, a = f.c, f.a
    tail = poly([(21, 24), (25, 15), (24, 11), (27.5, 13.5), (31, 11), (30.5, 17), (28, 20), (27, 26)])
    body = clip(ell(14.5, 23.5, 11.5, 7), y1=30)
    f.P(body | tail, c, depth=2)
    f.P(ell(8, 30, 3, 1.5), shade(c, -1), hl=False)
    f.P(ell(19, 30, 3, 1.5), shade(c, -1), hl=False)
    f.eye(7, 21)
    f.eye(15, 21)
    f.pts([(11, 23), (12, 23)], INK)
    f.pts([(10, 25), (11, 24), (12, 24), (13, 25)], shade(c, -2))
    f.pts([(5, 24), (6, 24), (17, 24), (18, 24)], a)
    # little bow
    f.P({(10, 15), (10, 16), (11, 16), (12, 16), (13, 16), (14, 16), (14, 15), (10, 17), (14, 17)}, a, sh=False)
    f.px(12, 16, shade(a, -1))


def dango_chick(f):
    c, a = f.c, f.a
    for m in (box(10, 29, 12, 30) | {(9, 30)}, box(17, 29, 19, 30) | {(20, 30)}):
        f.P(m, a, hl=False)
    # dango skewer
    f.P(box(27, 8, 27, 28), WOOD, hl=False, sh=False)
    f.P(ell(27.5, 11.5, 2.5, 2.5), PINK)
    f.P(ell(27.5, 16.5, 2.5, 2.5), WHITE)
    f.P(ell(27.5, 21.5, 2.5, 2.5), MINT)
    f.P({(14, 6), (15, 6), (15, 5), (16, 5), (16, 4), (13, 5), (14, 5), (13, 4)}, c, sh=False)
    body = ell(15, 13.5, 6.5, 6.5) | ell(15, 23, 8.5, 7)
    f.P(body, c, depth=2)
    f.P(ell(6.5, 22, 2, 3), shade(c, -0.5), hl=False)
    f.P(ell(24, 22.5, 2.5, 2), shade(c, -0.5), hl=False)
    f.face(11, sep=3, mouth=None, cx=15, blush=a)
    f.pts([(13, 14), (14, 14), (15, 14), (16, 14)], a)
    f.pts([(14, 15), (15, 15)], shade(a, -1))


def taiyaki_fish(f):
    c, a = f.c, f.a
    for m in (box(9, 27, 11, 30) | {(8, 30)}, box(16, 27, 18, 30) | {(15, 30)}):
        f.P(m, a, hl=False)
    tail = poly([(21, 18), (27, 11), (30.5, 11.5), (29, 19), (30.5, 26.5), (27, 27), (21, 20)])
    fin = poly([(10, 13), (15, 7.5), (20, 13)])
    body = ell(14, 19, 10.5, 7.5)
    f.P(body | tail | fin, c, depth=2)
    for y in (15, 18, 21, 24):
        for x in range(11 + (y % 2) * 2, 22, 4):
            if (x + 2, y + 1) in body:
                f.pts([(x, y), (x + 1, y + 1), (x + 2, y + 1), (x + 3, y)], a)
    f.pts([(26, 14), (27, 15), (27, 19), (26, 19), (27, 23), (26, 24), (14, 10), (15, 11), (16, 10)], a)
    f.pts([(10, 14), (10, 15), (9, 16), (9, 17), (9, 18), (9, 19), (10, 20), (10, 21), (10, 22)], a)
    f.eye(6, 16)
    f.pts([(4, 20), (5, 21), (6, 21)], INK)
    f.pts([(6, 22), (7, 22)], PINK)


def melon_turtle(f):
    c, a = f.c, f.a
    f.P({(27, 25), (28, 25), (28, 26), (29, 26)}, c, hl=False)
    for m in (box(9, 27, 12, 30), box(21, 27, 24, 30)):
        f.P(m, c)
    f.P(ell(7.5, 19.5, 5, 5) | box(9, 20, 13, 25), c, depth=2)
    f.P(box(17, 8, 18, 11) | box(15, 7, 20, 8), WOOD, hl=False)
    shell = clip(ell(18.5, 21, 9.5, 9), y1=27)
    f.P(shell, a, depth=1)
    net = shade(c, -1)
    f.F({q for q in shell if ((q[0] + q[1]) % 5 == 0 or (q[0] - q[1]) % 5 == 0) and q[1] < 26
         and (q[0] - 1, q[1]) in shell and (q[0] + 1, q[1]) in shell and (q[0], q[1] - 1) in shell}, net)
    f.F(clip(shell, y0=26), shade(c, -1))
    f.eye(4, 18, "small")
    f.eye(8, 18, "small")
    f.pts([(5, 21), (6, 22), (7, 22), (8, 21)], INK)
    f.pts([(3, 21), (10, 21)], PINK)


def royal_pudding(f):
    c, a = f.c, f.a
    f.PM(ell(5.5, 22, 2, 2), c, hl=False)
    f.P(crown_mask(11, 20, 3, h=7), MUSTARD)
    f.pts([(13, 8), (18, 8)], CORAL)
    f.pts([(15, 5), (16, 5)], RED)
    body = poly([(9.5, 10), (22.5, 10), (27, 28), (25, 31), (7, 31), (5, 28)])
    f.P(body, c, depth=2)
    top = clip(body, y1=13)
    f.F(top, a)
    f.F({q for q in top if q[1] == 10}, shade(a, 1))
    f.pts([(9, 14), (9, 15), (13, 14), (14, 14), (14, 15), (14, 16), (19, 14), (22, 14), (22, 15), (23, 16), (22, 16)], a)
    f.face(19, sep=4)
    f.pts([(8, 16), (8, 17), (9, 18)], WHITE)


# ------------------------------------------------------------------ machine 4: Space Patrol

def rocket_pup(f):
    c, a = f.c, f.a
    boost = box(4, 17, 8, 26) | {(5, 16), (6, 16), (7, 16), (6, 15)}
    for m in (boost, mir(boost)):
        f.P(m, a)
    f.sym([(4, 24), (5, 24), (6, 24), (7, 24), (8, 24)], STEEL)
    for m in ({(5, 28), (6, 28), (7, 28), (6, 29), (6, 30)}, mir({(5, 28), (6, 28), (7, 28), (6, 29), (6, 30)})):
        f.P(m, MUSTARD, sh=False, hl=False)
    f.sym([(6, 28)], WHITE)
    f.PM(box(11, 28, 14, 30), c)
    body = f.P(ell(16, 23.5, 6, 6.5), c)
    f.pts([(x, 21) for x in range(11, 21)], STEEL)
    f.pts([(15, 22), (16, 22), (15, 23), (16, 23)], a)
    head = f.P(ell(16, 11.5, 8.5, 7), c, depth=2)
    f.F(ell(21, 10.5, 3.2, 3.2) & head, TAN)
    f.PM(ell(7, 12.5, 2.5, 5), WOOD)
    f.pts([(x, 18) for x in range(12, 20)], a)
    f.px(16, 19, MUSTARD)
    f.eye(11, 10)
    f.eye(19, 10)
    f.pts([(15, 13), (16, 13), (15, 14), (16, 14)], INK)
    f.pts([(13, 15), (14, 16), (15, 16), (16, 16), (17, 16), (18, 15)], INK)
    f.pts([(15, 17), (16, 17)], CORAL)


def saturn_snail(f):
    c, a = f.c, f.a
    shell_c = shade(c, -1.6)
    ring = set()
    import math
    for i in range(200):
        t = i * math.pi * 2 / 200
        x = 19.5 + 12.2 * math.cos(t)
        y = 15.5 + 3.4 * math.sin(t) - 0.28 * (x - 19.5)
        ring.add((int(x), int(y), math.sin(t) > 0))
    back = {(x, y) for (x, y, fr) in ring if not fr}
    front = {(x, y) for (x, y, fr) in ring if fr}
    back |= shift(back, 0, 1)
    front |= shift(front, 0, 1)
    f.P(back, a, hl=False, sh=False)
    foot = poly([(2, 28), (5, 24), (27, 24), (30.5, 28.5), (29, 31), (3, 31)])
    head = ell(6.5, 22, 4, 5)
    stalks = path([(5, 18), (4, 13)]) | path([(8, 18), (10, 13)]) | box(3, 11, 5, 13) | box(9, 11, 11, 13)
    f.P(foot | head | stalks, c, depth=1)
    f.pts([(4, 12), (10, 12)], INK)
    f.pts([(4, 23), (5, 24), (6, 24), (7, 23)], INK)
    f.pts([(8, 22), (9, 22)], PINK)
    f.F({q for q in foot if q[1] == 29 and q[0] % 3 == 0}, shade(c, -1))
    shell = ell(19.5, 16, 8, 8)
    f.P(shell, shell_c, depth=2)
    f.F(path([(19, 16), (21, 15), (22, 17), (20, 19), (17, 18), (16, 15), (18, 12), (22, 11), (25, 14)]) & shell, shade(shell_c, 1.3))
    f.P(front, a, hl=False, sh=False)
    f.pts([(13, 9), (26, 21)], WHITE)


def astro_monkey(f):
    c, a = f.c, f.a
    skin = hx("f1dcc0")
    f.P(path([(21, 28), (26, 28), (28, 26), (28, 22), (26, 20), (24, 22), (25, 24)]), c, hl=False, sh=False)
    f.PM(box(11, 28, 14, 30), WHITE)
    body = f.P(ell(16, 24, 6, 5.5), a)
    f.pts([(15, 23), (16, 23), (15, 24), (16, 24)], MUSTARD)
    f.pts([(13, 26), (18, 26)], shade(a, -1))
    f.PM(ell(9.5, 22.5, 2, 3), a, hl=False)
    f.sym([(9, 25), (10, 25)], WHITE)
    f.P(box(15, 2, 16, 5), STEEL, hl=False, sh=False)
    f.P(ell(16, 2, 1.5, 1.5), CORAL, sh=False)
    head = ell(16, 12.5, 8, 7) | ell(6.5, 13, 3, 3.5) | ell(25.5, 13, 3, 3.5)
    f.P(head, c, depth=2)
    f.F(ell(6.5, 13, 1.5, 2) | ell(25.5, 13, 1.5, 2), skin)
    f.F(ell(13, 11.5, 3.5, 3.5) | ell(19, 11.5, 3.5, 3.5) | ell(16, 15, 5.5, 3.5), skin)
    f.pts([(x, 19) for x in range(11, 21)], STEEL)
    f.eye(12, 10)
    f.eye(18, 10)
    f.pts([(15, 14), (16, 14)], shade(skin, -2))
    f.pts([(13, 15), (14, 16), (15, 16), (16, 16), (17, 16), (18, 15)], INK)


def nebula_jelly(f):
    c, a = f.c, f.a
    for i, x in enumerate((8, 13, 18, 23)):
        col = a if i % 2 == 0 else shade(c, -1)
        s = 1 if i % 2 == 0 else -1
        f.P(path([(x, 17), (x - s, 20), (x + s, 23), (x - s, 26), (x, 29)], w=2), col, hl=False, sh=False)
    spike = poly([(13.5, 6), (16, 0.5), (18.5, 6)])
    sp2 = poly([(7, 9), (7.5, 3.5), (12, 6)])
    bell = clip(ell(16, 14, 10.5, 9), y1=17)
    for x in (7.5, 12, 16, 20, 24.5):
        bell |= ell(x, 17.5, 2.4, 2)
    f.P(bell | spike, c, depth=2)
    f.F({q for q in bell if q[1] == 17}, shade(c, -1))
    f.pts([(9, 9), (10, 8), (22, 8), (20, 15), (11, 15), (16, 6)], a)
    f.pts([(12, 7), (23, 11), (16, 2)], WHITE)
    f.face(11, sep=3, blush=a)


def galaxy_dragon(f):
    c, a = f.c, f.a
    wing = poly([(11, 23), (8, 19.5), (6, 21.5), (4, 17.5), (1.5, 18.5), (2, 6.5), (6, 9), (12, 14)])
    wc = shade(c, -1)
    for m in (wing, mir(wing)):
        f.P(m, wc, depth=1)
    f.sym([(3, 9), (3, 10), (4, 11), (4, 12), (5, 13), (5, 14), (6, 15), (7, 16), (5, 10), (6, 11), (7, 12), (8, 13)], shade(c, -2))
    f.sym([(4, 15), (7, 18), (3, 13)], a)
    f.P(poly([(19, 26), (25, 27.5), (27.5, 24), (29.5, 25), (28, 30.9), (19, 30.9)]), c)
    f.P(poly([(26.5, 24.5), (29.5, 19.5), (31, 25.5), (28.5, 25.5)]), a, sh=False)
    f.PM(box(10, 28, 14, 30), c)
    f.sym([(10, 30), (12, 30)], a)
    body = f.P(ell(16, 23.5, 6, 6.5), c)
    belly = ell(16, 24.5, 3.5, 4.5) & body
    f.F(belly, a)
    f.F({q for q in belly if q[1] in (22, 25, 28)}, shade(a, -1))
    f.PM(ell(10, 22, 2, 2), c, hl=False)
    horn = {(10, 7), (10, 6), (9, 5), (9, 4), (9, 3), (10, 5), (10, 4), (8, 2), (9, 2), (11, 6), (11, 7)}
    f.PM(horn, a, sh=False)
    head = f.P(ell(16, 12, 8, 6.5), c, depth=2)
    f.F(ell(16, 15.5, 4.5, 2.5) & head, shade(c, 1))
    f.pts([(14, 15), (17, 15)], INK)
    f.pts([(13, 17), (18, 17)], WHITE)
    f.F(box(10, 10, 12, 12) | box(19, 10, 21, 12), CREAM)
    f.pts([(11, 10), (11, 11), (11, 12), (20, 10), (20, 11), (20, 12)], INK)
    f.pts([(15, 7), (16, 7), (15, 8), (16, 8)], a)


# ------------------------------------------------------------------ machine 5: Plush Parade

def sleepy_panda(f):
    c, a = f.c, f.a
    f.PM(ell(8.5, 8.5, 2.8, 2.8), a, hl=False)
    body = f.P(ell(16, 25, 7.5, 5.5), c)
    f.PM(ell(11, 29.5, 3, 2), a)
    f.sym([(10, 29), (11, 29)], shade(a, 1.5))
    f.PM(ell(9, 23.5, 2.5, 3.5), a)
    head = f.P(ell(16, 14.5, 9.5, 7.5), c, depth=2)
    # nightcap
    cap = poly([(8, 9.5), (13, 3.5), (20, 3), (26, 7), (28, 12), (25, 10), (23.5, 9.5)])
    f.P(cap, MINT)
    f.pts([(12, 7), (15, 6), (18, 7), (21, 8), (14, 8), (17, 5)], CREAM)
    f.P(ell(28, 13.5, 2, 2), WHITE)
    f.P(box(8, 9, 23, 10), CREAM, hl=False)
    f.F(ell(11.5, 15.5, 2.8, 2.8) | ell(20.5, 15.5, 2.8, 2.8), a)
    f.eye(11, 14, "sleepy", c=CREAM)
    f.eye(20, 14, "sleepy", c=CREAM)
    f.pts([(15, 17), (16, 17)], INK)
    f.pts([(14, 19), (15, 19), (16, 19), (17, 19)], shade(c, -2))
    f.pts([(8, 18), (9, 18), (22, 18), (23, 18)], PINK)


def cloud_sheep(f):
    c, a = f.c, f.a
    leg = hx("4a4a58")
    for x in (9, 13, 18, 22):
        f.P(box(x, 26, x + 1, 30), leg, hl=False)
    wool = ell(16, 19, 10, 7)
    for (x, y, r) in ((6.5, 17, 3.5), (7.5, 22.5, 3.5), (11.5, 12.5, 3.8), (17, 11, 3.8), (22, 13, 3.8),
                      (25.5, 18, 3.5), (24.5, 23, 3.5), (19.5, 25.5, 3.5), (13, 25.5, 3.5)):
        wool |= ell(x, y, r, r)
    f.P(wool, c, depth=2)
    for (x, y) in ((8, 15), (20, 13), (23, 20), (12, 25), (19, 26), (6, 21)):
        f.pts([(x, y + 1), (x + 1, y), (x + 2, y), (x + 3, y + 1)], shade(c, -1))
    face = ell(16, 20, 5, 4.5)
    f.P(face, hx("f6d9c6"), sh=False, hl=False)
    f.PM(ell(9.5, 18.5, 2.5, 3), TAN)
    f.sym([(9, 18), (10, 19), (9, 20)], shade(TAN, -2))
    f.F(ell(16, 15.5, 4, 2) | ell(13, 16, 2, 1.5) | ell(19, 16, 2, 1.5), c)
    f.eye(13, 18, "small")
    f.eye(17, 18, "small")
    f.pts([(15, 21), (16, 21)], a)
    f.pts([(15, 22), (16, 22)], INK)
    f.pts([(12, 21), (19, 21)], a)


def tiger_cub(f):
    c, a = f.c, f.a
    tail = path([(21, 27), (25, 27), (27, 25), (27, 20), (25, 17)], w=2)
    f.P(tail, c, hl=False, sh=False)
    f.pts([(24, 27), (24, 28), (27, 24), (28, 24), (27, 21), (28, 21), (25, 17), (26, 17), (25, 18), (26, 18)], a)
    f.PM(box(10, 28, 14, 30), c)
    body = f.P(ell(16, 24.5, 6, 5.5), c)
    f.F(ell(16, 25.5, 3, 3.5) & body, CREAM)
    f.sym([(10, 23), (11, 23), (10, 25), (11, 25)], a)
    f.PM(ell(10, 23.5, 2, 2.5), c, hl=False)
    ear = poly([(6, 11), (7, 3), (13.5, 6.5)])
    head = ell(16, 13.5, 9.5, 7.5) | ear | mir(ear)
    f.P(head, c, depth=2)
    f.sym([(8, 6), (8, 7), (9, 7)], CREAM)
    f.F(ell(16, 17, 4.5, 3) & head, CREAM)
    f.pts([(15, 6), (16, 6), (15, 7), (16, 7), (15, 8), (16, 8), (12, 7), (12, 8), (19, 7), (19, 8)], a)
    f.sym([(7, 13), (8, 13), (7, 15), (8, 15), (9, 15)], a)
    f.eye(11, 11)
    f.eye(19, 11)
    f.pts([(15, 15), (16, 15)], PINK)
    f.pts([(14, 17), (15, 18), (16, 18), (17, 17), (15, 16), (16, 16)], INK)
    f.pts([(15, 16), (16, 16)], PINK)


def thunder_oni(f):
    c, a = f.c, f.a
    ring = clip(ell(16, 15, 12, 12.5) - ell(16, 15, 11, 11.5), y1=15)
    f.P(ring, shade(a, -1), hl=False, sh=False)
    for (x, y) in ((4.5, 16), (27.5, 16), (7.5, 6.5), (24.5, 6.5)):
        f.P(ell(x, y, 2.5, 2.5), a)
        f.px(int(x), int(y), RED)
    f.PM(box(11, 28, 14, 30), c)
    f.PM(ell(8.5, 23, 2, 3), c, hl=False)
    body = f.P(box(10, 20, 21, 27, r=1), c)
    f.F(box(10, 24, 21, 27, r=0) & body, a)
    f.pts([(12, 24), (12, 25), (15, 25), (15, 26), (18, 24), (18, 25), (20, 26)], DARK)
    horn = {(11, 7), (11, 6), (11, 5), (10, 4), (10, 3), (12, 7), (12, 6), (11, 4)}
    f.PM(horn, CREAM, sh=False)
    head = f.P(box(8, 8, 23, 19, r=2), c, depth=2)
    f.F(box(13, 7, 18, 9) | {(12, 8), (19, 8), (14, 10), (17, 10)}, DARK)
    f.pts([(10, 11), (11, 12), (12, 12), (13, 13), (21, 11), (20, 12), (19, 12), (18, 13)], INK)
    f.eye(11, 13)
    f.eye(19, 13)
    f.pts([(x, 17) for x in range(12, 20)], INK)
    f.pts([(13, 16), (18, 16), (13, 15), (18, 15)], WHITE)
    f.pts([(9, 16), (22, 16)], shade(c, -1))


def lucky_whale(f):
    c, a = f.c, f.a
    tail = poly([(21, 23), (25, 15), (23, 10), (27, 12.5), (31, 10), (30.5, 16), (28, 19), (27, 26)])
    body = clip(ell(14, 21.5, 12, 9), y1=30)
    f.P(crown_mask(8, 15, 7, h=7), a)
    f.pts([(10, 12), (13, 12)], CORAL)
    f.P(body | tail, c, depth=2)
    belly = {q for q in body if q[1] >= 25 and q[0] <= 21}
    f.F(belly, CREAM)
    f.F({q for q in belly if q[0] % 3 == 0 and q[1] >= 26}, shade(CREAM, -1))
    f.P(poly([(14, 23), (19.5, 24.5), (17, 29), (14, 27)]), shade(c, -1), hl=False)
    f.eye(6, 19)
    f.pts([(3, 23), (4, 24), (5, 24), (6, 24), (7, 24), (8, 23)], INK)
    f.pts([(9, 22), (10, 22)], PINK)
    f.pts([(8, 16), (9, 15), (10, 15)], shade(c, 1))


# ------------------------------------------------------------------ machine 6: Fortune Parade

def bell_mouse(f):
    c, a = f.c, f.a
    f.P(path([(22, 28), (27, 28), (29, 26), (29, 22), (27, 20)]), PINK, hl=False, sh=False)
    f.PM(box(11, 29, 14, 30), PINK, hl=False)
    body = ell(16, 13.5, 7, 6.5) | ell(16, 23.5, 8, 6.5) | ell(8, 8, 4.5, 4.5) | ell(24, 8, 4.5, 4.5)
    f.P(body, c, depth=2)
    f.F(ell(8, 8, 2.5, 2.5) | ell(24, 8, 2.5, 2.5), PINK)
    f.PM(ell(9, 22, 2, 2.5), c, hl=False)
    f.pts([(x, 19) for x in range(10, 22)], RED)
    f.P(ell(16, 22.5, 3, 3), a)
    f.pts([(14, 23), (15, 23), (16, 23), (17, 23), (16, 24)], INK)
    f.face(12, sep=3, mouth=None)
    f.pts([(15, 15), (16, 15)], PINK)
    f.pts([(15, 16), (16, 16)], WHITE)
    f.sym([(8, 15), (9, 14)], shade(c, -2))


def coin_toad(f):
    c, a = f.c, f.a
    f.PM(box(4, 28, 9, 30, r=0) | {(3, 30)}, c)
    f.P(box(12, 7, 19, 13, r=1), a)
    f.pts([(x, 9) for x in range(13, 19)] + [(x, 11) for x in range(13, 19)], shade(a, -2))
    body = ell(16, 22, 12.5, 8) | ell(9, 14.5, 3.8, 3.8) | ell(23, 14.5, 3.8, 3.8)
    f.P(body, c, depth=2)
    f.F(ell(16, 27, 7, 3) & body, shade(c, 1))
    f.F(ell(9, 14.5, 2.2, 2.2) | ell(23, 14.5, 2.2, 2.2), a)
    f.pts([(8, 14), (9, 14), (22, 14), (23, 14)], INK)
    f.pts([(x, 21) for x in range(8, 24)] + [(7, 20), (24, 20)], INK)
    f.P(ell(16, 22.5, 3, 3), a)
    f.pts([(15, 22), (16, 22), (15, 23), (16, 23)], INK)
    f.pts([(6, 23), (7, 25), (25, 23), (24, 26), (12, 17), (19, 17), (5, 21), (26, 21)], shade(c, -1))


def koi_kite(f):
    c, a = f.c, f.a
    tail = poly([(10, 22), (22, 22), (27, 31), (20.5, 28.5), (16, 31), (11.5, 28.5), (5, 31)])
    fin = poly([(10.5, 13), (5, 15.5), (5.5, 21), (10.5, 19)])
    body = box(10, 4, 21, 25, r=2)
    f.P(body | tail | fin | mir(fin), c, depth=2)
    f.sym([(6, 17), (7, 18), (8, 17), (8, 27), (9, 28), (11, 26), (12, 27)], shade(c, -1))
    for y in (15, 18, 21):
        for x in range(11 + ((y // 3) % 2) * 2, 20, 4):
            f.pts([(x, y), (x + 1, y + 1), (x + 2, y + 1), (x + 3, y)], a)
    f.F(box(10, 12, 21, 12), a)
    f.P(ell(16, 4.5, 5.5, 3), a, sh=False)
    f.F(ell(16, 4.5, 3.5, 1.5), INK)
    f.F(ell(13, 9.5, 2, 2) | ell(19, 9.5, 2, 2), WHITE)
    f.pts([(13, 9), (13, 10), (18, 9), (18, 10)], INK)
    f.pts([(14, 24), (17, 24), (15, 26), (16, 26)], a)


def lantern_ghost(f):
    c, a = f.c, f.a
    handle = clip(ell(16, 4.5, 4, 3.5) - ell(16, 4.5, 3, 2.5), y1=4)
    f.P(handle, DARK, hl=False, sh=False)
    # star charm on a string

    tail = poly([(8, 22), (24, 22), (23, 26), (20, 29), (15, 31), (12.5, 31), (14.5, 28), (10.5, 26.5)])
    body = clip(ell(16, 16, 9.5, 10.5), y0=8, y1=25)
    f.P(body | tail, c, depth=2)
    rib = shade(c, -1)
    f.F({q for q in body if q[1] in (10, 13, 16, 19, 22) and (q[0] - 1, q[1]) in body and (q[0] + 1, q[1]) in body}, rib)
    f.P(box(11, 5, 20, 7), DARK, sh=False)
    f.F(star(16, 10) | {(15, 10), (15, 9), (15, 11)}, MUSTARD)
    f.eye(11, 12, "big")
    f.eye(18, 12, "big")
    f.F(ell(16, 18.5, 4, 2), INK)
    f.P(box(15, 19, 17, 24, r=1) - {(15, 19), (17, 19)}, a, hl=False)
    f.px(16, 21, shade(a, -1))
    f.pts([(9, 16), (10, 16), (21, 16), (22, 16)], a)


def treasure_kappa(f):
    c, a = f.c, f.a
    f.P(ell(16, 21.5, 9.5, 7.5), WOOD, depth=2)
    f.PM(box(8, 29, 13, 30) | {(7, 30)}, a, hl=False)
    body = f.P(box(10, 19, 21, 28, r=2), c)
    # treasure chest held in front
    f.PM(ell(9, 22.5, 2, 2.5), c, hl=False)
    f.P(box(12, 21, 19, 27), WOOD)
    f.F(box(12, 21, 19, 22), shade(WOOD, -1))
    f.pts([(x, 23) for x in range(12, 20)], a)
    f.pts([(15, 24), (16, 24), (15, 25), (16, 25)], a)
    f.pts([(13, 21), (15, 20), (16, 21), (18, 20), (17, 21)], a)
    fringe = box(8, 6, 23, 7)
    for x in (7, 10, 13, 18, 21, 24):
        fringe |= {(x, 8), (x, 7)}
    f.P(fringe, DARK, hl=False, sh=False)
    f.P(ell(16, 4.5, 5.5, 2), BATH)
    f.pts([(13, 4), (14, 4)], WHITE)
    head = f.P(box(8, 8, 23, 18, r=3), c, depth=2)
    f.pts([(8, 8), (11, 8), (12, 8), (14, 8), (15, 8), (16, 8), (17, 8), (19, 8), (20, 8), (22, 8), (23, 8), (9, 8), (10, 8), (13, 8), (18, 8), (21, 8)], DARK)
    f.pts([(9, 9), (12, 9), (15, 9), (16, 9), (19, 9), (22, 9)], DARK)
    f.eye(10, 11)
    f.eye(20, 11)
    f.F(box(13, 14, 18, 15), a)
    f.pts([(14, 16), (15, 16), (16, 16), (17, 16)], shade(a, -1))
    f.pts([(8, 15), (9, 15), (22, 15), (23, 15)], PINK)


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


# ------------------------------------------------------------------ look-only fallback

def generic(f):
    """Builds a toy from the look dictionary alone (used for figures without a recipe)."""
    look = f.look
    c, a = f.c, f.a
    extras = [look.get("extra")] + list(look.get("extras", []))
    kind = look.get("body", "round")
    if kind == "wide":
        body = ell(16, 21.5, 11.5, 8.5)
        fy = 19
    elif kind == "square":
        body = box(8, 9, 23, 28, r=3)
        fy = 15
    elif kind == "pear":
        body = ell(16, 14, 6.5, 6.5) | ell(16, 23, 9, 7)
        fy = 12
    elif kind == "tall":
        body = ell(16, 12, 7.5, 7) | ell(16, 23, 6.5, 7)
        fy = 10
    else:
        body = ell(16, 19, 10, 10)
        fy = 16
    top = min(q[1] for q in body)
    ears = look.get("ears", "none")
    if ears == "round":
        body |= ell(9, top + 2, 3, 3) | ell(23, top + 2, 3, 3)
    elif ears == "pointy":
        e = poly([(7, top + 5), (8, top - 4), (14, top + 1)])
        body |= e | mir(e)
    elif ears == "long":
        body |= ell(12, top - 3, 2.5, 6) | ell(20, top - 3, 2.5, 6)
    if "tail" in extras:
        f.P(ell(26, 25, 3, 3), c)
    if "wings" in extras:
        f.PM(ell(5, 20, 3, 5), shade(c, -1))
    if "shell" in extras:
        f.P(ell(16, 21, 12, 9), a, depth=2)
    if "spikes" in extras:
        for y in (10, 16, 22):
            f.P(poly([(22, y), (28, y + 1), (23, y + 5)]), a)
    if look.get("limbs") != "none":
        f.feet(shade(c, -1))
    f.P(body, c, depth=2)
    if ears == "antenna":
        f.P(box(15, top - 4, 16, top - 1), c, hl=False, sh=False)
        f.P(ell(16, top - 5, 2, 2), a)
    elif ears == "horns":
        f.PM(poly([(9, top + 3), (8, top - 3), (12, top + 1)]), a)
    if "crown" in extras:
        f.P(crown_mask(11, 20, top - 5, h=6), a)
    if "belly" in extras or "mask" in extras:
        f.F(ell(16, fy + 6, 5, 3.5) & body, a)
    f.face(fy, sep=4, mouth=None if "beak" in extras else "smile")
    if "beak" in extras:
        f.pts([(14, fy + 3), (15, fy + 3), (16, fy + 3), (17, fy + 3), (15, fy + 4), (16, fy + 4)], a)
    if "drum" in extras:
        f.P(ell(16, 25, 4, 3.5), a)
    if "star" in extras:
        f.F(star(16, fy - 4), a)


def build_figure(fig):
    f = Fig(fig["look"])
    RECIPES.get(fig["name_en"], generic)(f)
    return f.done(fig["id"])
