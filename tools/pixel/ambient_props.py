"""Ambient objects of the toy store: each function returns (frames, fps).

Loops are built from the frame index only, so they close exactly. Things with
a fixed point (cords, strings, poles) keep that pixel identical in all frames.
"""
import math
import random

from ambient_lib import (BLUE, CREAM, HI, SH, CREAM_SH, Cv, DRED, DSTEEL, DSTEEL_SH, GREEN, GREEN_HI, GREEN_SH, INK,
                         MUSTARD, MUSTARD_HI, MUSTARD_SH, NAVY, NAVY_SH, ORANGE, ORANGE_HI, ORANGE_SH, PAPER,
                         PINK, PINK_HI, PINK_SH, RED, RED_HI, SKY, SKY_HI, SKY_SH, STEEL, STEEL_HI, TAU, WHITE,
                         WHITE_SH, WOOD, WOOD_HI, WOOD_SH, box, dilate, disc, ell, frames, line, poly, rnd,
                         stroke, wave)
from ambient_lib import plant_pixels
from pixlib import TINY


# ---------------------------------------------------------------- wall clock
def wall_clock():
    n = 12

    def fr(i):
        c = Cv(24, 36, "amb_wall_clock")
        s = wave(i, n)
        look = 1 if i < 6 else -1
        # pendulum case with a window
        c.panel(5, 17, 18, 34, WOOD, r=1)
        c.rect(7, 20, 16, 32, DSTEEL_SH)
        c.ring(box(7, 20, 16, 32), WOOD_SH)
        c.rect(7, 20, 16, 32, DSTEEL_SH)
        bx = 11.5 + 3.4 * s
        c.fill(stroke([(11.5, 19), (bx, 29)], 1, smooth=False), STEEL_HI)
        c.fill(disc(rnd(bx - 0.5), 29, 1.6), MUSTARD)
        c.dot(rnd(bx - 0.5), 28, MUSTARD_HI)
        # bells on top, then the head: red rim, cream dial
        c.part(disc(5, 2, 1.5), MUSTARD, hi=False)
        c.part(disc(17, 2, 1.5), MUSTARD, hi=False)
        c.part(disc(11.5, 10, 9.6), RED)
        c.part(disc(11.5, 10, 7.2), PAPER, hi=False)
        c.dots([(11, 3), (12, 3), (11, 17), (12, 17), (4, 10), (19, 10)], DRED)
        c.eyes(8, 5, 3, 6, look=look, gap=2)
        # a small mouth that says tick ... tock
        if i in (0, 1, 6, 7):
            c.rect(11, 13, 12, 15, INK)
            c.dots([(11, 15), (12, 15)], RED)
        else:
            c.dots([(9, 13), (10, 14), (11, 14), (12, 14), (13, 14), (14, 13)], INK)
        return c

    return frames(fr, n), 6


# ---------------------------------------------------------------- ceiling fan
def ceiling_fan():
    n = 6
    cx, cy, rx, ry = 28.0, 10.5, 26.0, 7.0

    def blade(a):
        pts = []
        for r, da in ((0.16, -0.5), (0.7, -0.3), (1.0, -0.2), (1.0, 0.2), (0.7, 0.3), (0.16, 0.5)):
            pts.append((cx + rx * r * math.cos(a + da), cy + ry * r * math.sin(a + da)))
        return poly(pts)

    def fr(i):
        c = Cv(56, 24, "amb_ceiling_fan")
        base = TAU / 3 * i / n + 0.2
        angs = [base + k * TAU / 3 for k in range(3)]
        for a in angs:                          # far blades first
            if math.sin(a) < 0:
                c.part(blade(a), WOOD, hi=False)
        c.rect(26, 0, 29, 6, INK)
        c.erase({(26, 0), (29, 0)})
        c.rect(27, 0, 28, 6, STEEL)
        c.rect(26, 0, 29, 0, INK)
        c.rect(27, 0, 28, 0, STEEL)
        c.part(ell(28, 9, 6, 3.5), MUSTARD)
        for a in angs:
            if math.sin(a) >= 0:
                c.part(blade(a), WOOD, hc=WOOD_HI)
        c.part(ell(28, 12, 4, 2), DSTEEL, hi=False)
        c.part(ell(28, 15.5, 3.5, 3), PAPER, hi=False)
        c.dot(26, 14, WHITE)
        # pull chain, swinging a little
        sw = (0, 1, 1, 0, -1, -1)[i]
        c.fill(line(28, 19, 28 + sw, 21), INK)
        c.dot(28 + sw, 22, MUSTARD)
        return c

    return frames(fr, n), 10


# ---------------------------------------------------------------- CRT TV
def tv():
    n = 14
    rng = random.Random(7)
    noise = [[rng.random() for _ in range(400)] for _ in range(4)]

    def fr(i):
        c = Cv(38, 44, "amb_tv")
        # stand
        c.part(poly([(5, 33), (33, 33), (36, 37), (2, 37)]), WOOD, sh=False)
        c.rect(3, 37, 34, 38, WOOD_SH)
        for lx in (5, 31):
            c.rect(lx, 39, lx + 1, 42, WOOD_SH)
            c.ring(box(lx, 39, lx + 1, 42))
            c.rect(lx, 39, lx + 1, 42, WOOD_SH)
        # antenna
        wob = 1 if i in (10, 12) else 0
        c.noodle([(18, 8), (11 - wob, 1)], 1, INK, smooth=False)
        c.noodle([(20, 8), (27 + wob, 1)], 1, INK, smooth=False)
        c.dot(11 - wob, 0, RED)
        c.dot(27 + wob, 0, RED)
        # cabinet: top face, front
        c.part(poly([(5, 6), (33, 6), (36, 10), (2, 10)]), ORANGE_HI, hi=False, sh=False)
        c.panel(2, 10, 35, 33, ORANGE, r=2)
        # control column
        c.rect(28, 13, 33, 30, CREAM)
        c.part(disc(30.5, 16, 1.8), DSTEEL, hi=False)
        c.dot(30, 15, STEEL_HI)
        c.part(disc(30.5, 21, 1.8), DSTEEL, hi=False)
        c.dot(31, 20, STEEL_HI)
        for yy in (25, 27, 29):
            c.rect(29, yy, 32, yy, CREAM_SH)
        # screen
        scr = box(5, 13, 25, 30, 2)
        c.ring(scr)
        if i < 10:
            c.fill(scr, PAPER)
            c.rect(6, 27, 24, 27, MUSTARD)
            c.fill({q for q in scr if q[1] >= 28}, MUSTARD)
            # sun rays behind
            c.dots([(8, 15), (10, 17), (22, 15), (20, 17)], PINK)
            # a bouncing ball with eyes: two hops across the screen
            t = i / 10.0
            hop = abs(math.sin(TAU * t))
            bx = 8 + rnd(14 * t)
            byc = 24 - rnd(8 * hop)
            if hop < 0.2:
                c.part(ell(bx + 0.5, byc + 1.5, 3.6, 2.4) & scr, RED)
                c.eyes(bx - 1, byc, 1, 2, look=1, gap=1, ringed=False)
            else:
                c.part(ell(bx + 0.5, byc + 0.5, 3, 3.2) & scr, RED)
                c.eyes(bx - 1, byc - 1, 1, 3, look=1, gap=1, ringed=False)
                c.dot(bx - 1, byc - 2, WHITE)
            c.dots([(bx - 4, 26), (bx - 6, 25)], CREAM_SH) if hop < 0.2 else None
        else:
            k = i - 10
            for j, (x, y) in enumerate(sorted(scr)):
                v = noise[k][j % 400]
                c.dot(x, y, WHITE if v > 0.62 else (STEEL if v > 0.3 else DSTEEL))
            yb = 14 + k * 4
            c.fill({q for q in scr if yb <= q[1] <= yb + 1}, INK)
        c.dots([(6, 15), (7, 14)], WHITE)             # glass glare
        return c

    return frames(fr, n), 8


# ---------------------------------------------------------------- neon sign
KANA = {
    "ga": [[(1, 5), (12, 5), (12, 10), (10, 15), (8, 14)], [(6, 1), (6, 6), (5, 11), (2, 15)],
           [(11, 0), (12, 2)], [(14, 0), (15, 2)]],
    "chi": [[(11, 1), (7, 2), (3, 3)], [(1, 7), (14, 7)], [(8, 3), (8, 10), (7, 13), (4, 15)]],
    "ya": [[(2, 9), (12, 7), (10, 11)], [(5, 5), (6, 10), (8, 15)]],
}


def kana_mask(name, ox, oy):
    m = set()
    for pts in KANA[name]:
        m |= stroke([(x + ox, y + oy) for x, y in pts], 1, smooth=False)
    return m


def neon_sign():
    n = 18
    letters = [kana_mask("ga", 8, 6), kana_mask("chi", 28, 6), kana_mask("ya", 47, 6)]
    # the border tube, as an ordered loop of pixels
    border = ([(x, 5) for x in range(5, 67)] + [(66, y) for y in range(6, 23)]
              + [(x, 23) for x in range(65, 4, -1)] + [(5, y) for y in range(22, 5, -1)])
    state = {5: "dim", 11: "off3", 12: "off3", 14: "off3"}

    def fr(i):
        c = Cv(72, 28, "amb_neon_sign")
        for hx_ in (14, 57):
            c.rect(hx_, 0, hx_, 2, DSTEEL)
        c.panel(2, 2, 69, 26, NAVY, r=2, hi=False)
        st = state.get(i, "on")
        tube = SKY_SH if st != "dim" else NAVY_SH
        c.dots(border, tube)
        if st != "dim":
            L = len(border)
            head = (i * L) // n
            for k in range(7):
                c.dot(border[(head + k) % L][0], border[(head + k) % L][1], WHITE)
        for k, m in enumerate(letters):
            if st == "off3" and k == 2:
                c.fill(m, DSTEEL)
            elif st == "dim":
                c.fill(dilate(m), DRED)
                c.fill(m, PINK_SH)
            else:
                c.fill(dilate(m), RED)
                c.fill(m, PINK_HI if (i + k) % 2 else PAPER)
        # a little star tube on the right
        star = {(63, 11), (62, 12), (63, 12), (64, 12), (63, 13)}
        c.fill(star, MUSTARD if (st != "dim" and i % 6 < 4) else MUSTARD_SH)
        return c

    return frames(fr, n), 6


# ---------------------------------------------------------------- string lights
def string_lights():
    n = 4
    cols = (RED, MUSTARD, GREEN, BLUE)

    def wire_y(x):
        return 1 + rnd(3 * math.sin(math.pi * (x % 48) / 48.0))

    def fr(i):
        c = Cv(96, 14, "amb_string_lights")
        for x in range(96):
            c.dot(x, wire_y(x), INK)
        c.dots([(0, 0), (48, 0), (47, 0), (95, 0)], DSTEEL)      # the pegs
        for k in range(8):
            x = 6 + 12 * k
            y = wire_y(x)
            col = cols[k % 4]
            lit = (k - i) % 4 == 0
            warm = (k - i) % 4 == 1                              # the bulb that was just lit
            c.rect(x, y + 1, x + 1, y + 2, DSTEEL)
            m = ell(x + 1, y + 6, 2.5, 3)
            if lit:
                c.part(m, col, sh=False, hc=WHITE)
                c.dot(x, y + 4, WHITE)
                for q in ((x - 3, y + 6), (x + 4, y + 6), (x - 2, y + 9), (x + 3, y + 9)):
                    c.dot(q[0], q[1], HI[col])
            elif warm:
                c.part(m, col, hi=False)
            else:
                c.part(m, SH[col], hi=False, sh=False)
                c.dot(x, y + 4, col)
        return c

    return frames(fr, n), 5


# ---------------------------------------------------------------- paper lantern
def lantern():
    n = 10

    def fr(i):
        c = Cv(20, 34, "amb_lantern")
        s = wave(i, n)
        lag = wave(i, n, -0.15)
        c.rect(10, 0, 10, 5, INK)
        c.panel(7, 5, 13, 7, INK, outline=False)
        body = ell(10.5, 17.5, 6.5, 9.5)
        c.part(body, RED)
        for yy in (11, 14, 17, 20, 23):                 # bamboo ribs
            c.fill({q for q in body if q[1] == yy and (q[0] - 1, q[1]) in body and (q[0] + 1, q[1]) in body}, DRED)
        glow = ell(10.5, 18, 4, 5.5 if i % 2 else 5)     # the candle inside
        c.fill({q for q in glow if q[1] not in (11, 14, 17, 20, 23)}, ORANGE)
        c.fill({q for q in ell(10.5, 19, 2.5, 3.5) if q[1] not in (17, 20, 23)}, MUSTARD)
        c.eyes(8, 13, 2, 4, look=(1 if s > 0 else -1), gap=1)
        c.dots([(6, 12), (6, 13)], RED_HI)
        c.panel(7, 27, 13, 29, INK, outline=False)
        out = c.sheared(0, 33, 2.6 * s)
        # tassel trails behind the swing
        tx = 10 + rnd(2.6 * s * 30 / 33.0)
        tip = 10 + rnd(2.6 * lag)
        out.rect(tx, 30, tx, 31, MUSTARD)
        out.rect(tip, 32, tip, 33, MUSTARD_SH)
        out.ring({(tx, 30), (tx, 31)} | {(tip, 32)})
        out.rect(tx, 30, tx, 31, MUSTARD)
        out.rect(tip, 32, tip, 33, MUSTARD_SH)
        out.dot(10, 0, INK)
        return out

    return frames(fr, n), 7


# ---------------------------------------------------------------- dripping tap
def tap_drip():
    n = 14

    def drop(c, x, y, h):
        m = box(x, y, x + 1, y + h - 1)
        if h >= 3:
            m |= {(x - 1, y + h - 2), (x + 2, y + h - 2)}
        if h >= 4:
            m |= {(x - 1, y + h - 3), (x + 2, y + h - 3)}
            m -= {(x - 1, y + h - 3), (x + 2, y + h - 3)} if h == 4 else set()
        c.part(m, SKY, hi=False, sc=BLUE)
        c.dot(x, y + max(0, h - 2), WHITE)

    def fr(i):
        c = Cv(10, 26, "amb_tap_drip")
        # tap: a pipe out of the wall, a spout and a red cross handle
        c.rect(3, 1, 4, 2, INK)
        c.part(box(1, 1, 6, 1), RED, hi=False, sh=False)
        c.panel(1, 3, 7, 5, STEEL)
        c.panel(4, 5, 7, 8, STEEL, hi=False)
        c.rect(2, 4, 6, 4, STEEL)
        c.rect(2, 3, 6, 3, STEEL_HI)
        c.rect(5, 5, 6, 7, STEEL)
        c.rect(5, 9, 6, 9, DSTEEL_SH)
        x = 5
        if i == 1:
            c.rect(x, 10, x + 1, 10, SKY)
        elif i == 2:
            c.part(box(x, 10, x + 1, 11), SKY, hi=False, sc=BLUE)
        elif i == 3:
            drop(c, x, 10, 3)
        elif i == 4:
            drop(c, x, 11, 4)
        elif i == 5:
            drop(c, x, 14, 4)
        elif i == 6:
            drop(c, x, 18, 4)
        elif i == 7:
            c.part(box(x, 21, x + 1, 23), SKY, hi=False, sc=BLUE)
        elif i == 8:
            c.part(box(x - 2, 24, x + 3, 24), SKY, hi=False, sc=BLUE)
            c.dots([(x - 3, 21), (x + 4, 21)], WHITE)
        elif i == 9:
            c.dots([(x - 4, 24), (x - 2, 22), (x + 3, 22), (x + 4, 24), (x, 24), (x + 1, 24)], SKY)
            c.dots([(x - 3, 20), (x + 3, 20)], WHITE)
        elif i == 10:
            c.dots([(x - 3, 24), (x + 3, 24)], SKY_SH)
        return c

    return frames(fr, n), 9


# ---------------------------------------------------------------- potted plant
def plant_sway():
    """The plant prop, breathing: every leaf sways with its own phase and reach."""
    n = 12
    amps = (0.9, 1.5, 1.5, 1.2, 1.2, 1.0)
    phases = (0.0, 0.1, 0.24, 0.36, 0.5, 0.62)

    def fr(i):
        c = Cv(24, 40, "amb_plant_sway")
        sway = [amps[k] * wave(i, n, -phases[k]) for k in range(6)]
        c.px.update(plant_pixels(sway))
        return c

    return frames(fr, n), 7


# ---------------------------------------------------------------- mug with steam
def mug_steam():
    n = 9

    def fr(i):
        c = Cv(14, 24, "amb_mug_steam")
        # two curly ribbons of steam: the wave travels upwards, the tips thin out
        for k, (cx, y0, y1, ph) in enumerate(((4, 3, 12, 0.0), (9, 1, 11, 0.5))):
            m = set()
            for y in range(y0, y1 + 1):
                x = cx + rnd(1.4 * math.sin(TAU * (y / 9.0 + i / float(n) + ph)))
                m.add((x, y))
                if y > y0 + 2:
                    m.add((x + 1, y))
            c.part(m, WHITE, hi=False, sh=False)
        c.part(box(10, 16, 12, 21, 1) - box(10, 18, 10, 19), CREAM)     # handle
        c.erase({(10, 18), (10, 19)})
        c.dots([(10, 17), (10, 20)], INK)
        c.part(box(1, 14, 9, 22, 1), RED)
        c.part(ell(5.5, 14.5, 4, 1.6), WOOD_SH, hi=False, sh=False)
        c.dot(4, 14, WOOD)
        c.rect(2, 18, 8, 19, CREAM)
        c.dots([(4, 18), (6, 19)], RED)
        return c

    return frames(fr, n), 7


# ---------------------------------------------------------------- radio
def radio():
    n = 8

    def note(c, x, y, col=INK):
        c.rect(x, y + 3, x + 1, y + 4, col)
        c.rect(x + 2, y, x + 2, y + 3, col)
        c.dot(x + 3, y + 1, col)
        c.dot(x + 3, y, col)

    def fr(i):
        c = Cv(30, 30, "amb_radio")
        beat = i % 4                       # 0 = squash, 2 = stretch
        sq = (1, 0, -1, 0)[beat]
        top = 12 + sq
        wide = 1 if sq > 0 else 0
        # antenna
        c.noodle([(23, top), (25 + (1 if beat == 2 else 0), 5 + sq), (26 - sq, 3)], 1, INK)
        c.dot(26 - sq, 2, RED)
        c.dot(26 - sq, 3, RED)
        # noodle legs and big shoes
        for lx in (7, 18):
            c.rect(lx + 1, 25, lx + 2, 27, INK)
            c.part(box(lx - 1 - wide, 27, lx + 4 + wide, 28, 0) | {(lx, 26), (lx + 3, 26)}, WHITE, hi=False)
        x0, x1 = 3 - wide, 26 + wide
        c.part(poly([(x0 + 2, top - 3), (x1 - 1, top - 3), (x1 + 1, top), (x0, top)]), ORANGE_HI, hi=False, sh=False)
        c.panel(x0, top, x1, 25, ORANGE, r=2)
        # speaker (a mouth that booms on the beat) on the left
        c.part(disc(9, 19, 4.2), CREAM, hi=False)
        for yy in (17, 19, 21):
            c.rect(7, yy, 11, yy, DSTEEL)
        if beat in (0, 1):
            c.fill(disc(9, 19, 2.4), INK)
            c.dots([(9, 20), (10, 20), (9, 21)], RED)
        # dial with the eyes on the right
        c.rect(15, top + 2, 24, top + 8, MUSTARD)
        c.ring(box(15, top + 2, 24, top + 8))
        c.rect(15, top + 2, 24, top + 8, MUSTARD)
        c.rect(15, top + 2, 24, top + 2, MUSTARD_HI)
        c.eyes(16, top + 3, 3, 5, look=(1 if i < 4 else -1), gap=2)
        c.rect(17, 23, 18, 23, DSTEEL)
        c.rect(22, 23, 23, 23, DSTEEL)
        c.rect(20, 23, 20, 23, RED)
        # notes popping out of the top, one per half loop
        a = i % 4
        if i < 4:
            note(c, 7 - a, 6 - a * 2 + (2 if a == 0 else 0), INK)
        else:
            note(c, 12 + a, 6 - a * 2 + (2 if a == 0 else 0), RED if a < 3 else DRED)
        if i in (3, 7):
            px_ = 4 if i == 3 else 15
            c.dots([(px_ - 2, 1), (px_ + 5, 0), (px_ + 5, 4)], MUSTARD)
        return c

    return frames(fr, n), 9


# ---------------------------------------------------------------- dust motes
def dust_motes():
    """Motes in a light beam. Each one is a white fleck with a mustard underside,
    so it reads on cream walls as well as on dark ones; a few twinkle."""
    n = 26
    rng = random.Random(11)
    motes = [(rng.uniform(6, 40), rng.uniform(4, 30), rng.randrange(n), rng.uniform(0.25, 0.55),
              rng.uniform(0.6, 1.6), rng.random()) for _ in range(11)]

    def fr(i):
        c = Cv(48, 48, "amb_dust_motes")
        for k, (x0, y0, born, vy, amp, ph) in enumerate(motes):
            age = (i - born) % n
            life = 18
            if age >= life:
                continue
            x = rnd(x0 + amp * math.sin(TAU * (age / 13.0 + ph)) + age * 0.15)
            y = rnd(y0 + vy * age)
            if age in (0, life - 1):
                c.dot(x, y, MUSTARD_SH)
            elif age in (1, life - 2):
                c.dot(x, y, MUSTARD)
            else:
                c.dot(x, y + 1, MUSTARD)
                c.dot(x, y, WHITE)
                if k % 4 == 0 and age in (7, 8):          # a twinkle as it catches the light
                    c.dots([(x - 1, y), (x + 1, y), (x, y - 1)], MUSTARD_HI)
                    c.dot(x, y + 1, MUSTARD_HI)
                    c.dot(x, y + 2, MUSTARD)
        return c

    return frames(fr, n), 6


# ---------------------------------------------------------------- exit sign
RUNNER = ["..##...", "..##.#.", ".####..", "#.##...", "..###..", ".#..##.", "#.....#"]
DEGUCHI = ["..#....#####", "#.#.#..#...#", "#####..#...#", "..#....#...#", "#.#.#..#...#", "#.#.#..#...#",
           "#####..#####"]


def exit_sign():
    n = 22
    dim = {14, 16}

    def fr(i):
        c = Cv(30, 14, "amb_exit_sign")
        c.rect(6, 0, 6, 1, DSTEEL)
        c.rect(23, 0, 23, 1, DSTEEL)
        off = i in dim
        bg = GREEN_SH if off else GREEN
        fg = STEEL if off else WHITE
        c.panel(1, 3, 28, 12, bg, hi=not off, sh=not off)
        c.rect(1, 2, 28, 2, INK)
        c.rect(2, 2, 27, 2, DSTEEL if off else GREEN_HI)
        c.ring(box(1, 2, 28, 12))
        for j, row in enumerate(RUNNER):
            for k, ch in enumerate(row):
                if ch == "#":
                    c.dot(3 + k, 4 + j, fg)
        c.rect(11, 4, 12, 10, fg)                           # the door
        c.dot(11, 7, bg)
        for j, row in enumerate(DEGUCHI):
            for k, ch in enumerate(row):
                if ch == "#":
                    c.dot(15 + k, 4 + j, fg)
        if not off and i in (13, 15, 17):
            c.dots([(0, 5), (29, 9)], GREEN_HI)             # a stray spark of glow
        return c

    return frames(fr, n), 8


# ---------------------------------------------------------------- vending machine
def vending():
    n = 10
    cans = (RED, GREEN, BLUE, MUSTARD, ORANGE)

    def fr(i):
        c = Cv(46, 86, "amb_vending")
        c.part(poly([(5, 1), (41, 1), (44, 6), (2, 6)]), RED_HI, hi=False, sh=False)
        c.panel(2, 6, 43, 82, RED, r=1)
        c.rect(40, 8, 42, 80, DRED)
        for fx in (4, 36):
            c.panel(fx, 82, fx + 5, 84, DSTEEL, hi=False)
        # marquee with chasing lamps
        c.rect(5, 8, 40, 12, CREAM)
        c.ring(box(5, 8, 40, 12))
        c.rect(5, 8, 40, 12, CREAM)
        for k in range(9):
            lit = (k - i) % 5 == 0
            c.rect(7 + k * 4, 10, 8 + k * 4, 10, RED if lit else CREAM_SH)
            if lit:
                c.dots([(7 + k * 4, 9), (8 + k * 4, 11)], MUSTARD)
        # lit display window with two shelves of cans and their buttons
        c.rect(5, 15, 40, 45, PAPER)
        c.ring(box(5, 15, 40, 45))
        c.rect(5, 15, 40, 45, PAPER)
        c.rect(5, 15, 40, 15, WHITE)
        for row in range(2):
            y = 18 + row * 14
            c.rect(6, y + 9, 39, y + 9, CREAM_SH)
            for k in range(5):
                x = 8 + k * 7
                col = cans[(k + row * 2) % 5]
                c.part(box(x, y, x + 3, y + 8, 0), col, hi=False)
                c.rect(x, y, x + 3, y, STEEL_HI)
                c.rect(x, y + 3, x + 3, y + 4, PAPER)
                c.dot(x, y + 2, WHITE)
                idx = row * 5 + k
                on = idx == i
                was = idx == (i - 1) % n
                c.rect(x + 1, y + 11, x + 2, y + 11, RED if on else (MUSTARD if was else GREEN))
                if on:
                    c.dots([(x, y + 11), (x + 3, y + 11)], MUSTARD_HI)
        # a sleepy face: eyes on the middle band, the tray is the mouth
        c.rect(3, 47, 39, 48, CREAM)
        blink = i == 7
        c.eyes(9, 51, 5, 9, look=(1 if i < 5 else -1), gap=2, blink=blink, lid=RED)
        # coin panel
        c.panel(27, 51, 38, 64, STEEL, r=1)
        c.rect(32, 53, 33, 57, INK)
        c.rect(29, 53, 30, 54, RED if i % 2 else DRED)
        c.part(disc(32, 61, 1.3), DSTEEL, hi=False, sh=False)
        c.rect(35, 59, 36, 62, INK)
        # tray
        c.panel(8, 68, 37, 78, INK, r=1, outline=False)
        c.rect(10, 70, 35, 73, DSTEEL)
        c.rect(10, 70, 35, 70, STEEL)
        c.rect(10, 76, 35, 76, DSTEEL_SH)
        c.rect(6, 4, 30, 4, PAPER)
        return c

    return frames(fr, n), 6


# ---------------------------------------------------------------- carp streamer
def koinobori():
    n = 7

    def fr(i):
        c = Cv(64, 24, "amb_koinobori")
        # pole and its ball
        c.rect(2, 3, 3, 23, WOOD)
        c.ring(box(2, 3, 3, 23))
        c.rect(2, 3, 3, 23, WOOD)
        c.rect(3, 3, 3, 23, WOOD_SH)
        c.erase({(2, 24), (3, 24)})
        c.part(disc(2.5, 2, 1.8), MUSTARD, hi=False)
        c.rect(4, 8, 6, 8, INK)
        cols = {}
        for x in range(7, 62):
            u = (x - 7) / 54.0
            amp = 0.4 + 3.2 * u
            yc = 11.5 + amp * math.sin(TAU * (u * 1.35 - i / float(n)))
            half = 5.5 - 1.8 * u if u < 0.82 else 4.0 + (u - 0.82) * 12
            for y in range(rnd(yc - half), rnd(yc + half)):
                v = (y + 0.5 - yc) / half
                if u > 0.86 and abs(v) < (u - 0.86) * 5:      # notch of the tail fin
                    continue
                if x < 10:
                    col = PAPER
                elif x < 12:
                    col = MUSTARD
                elif v > 0.45:
                    col = CREAM
                elif u > 0.82:
                    col = RED_HI if (rnd(v * 4) % 2 == 0) else RED
                else:
                    sc_ = (x + (2 if rnd((v + 1) * 2.2) % 2 else 0)) % 5
                    col = DRED if (sc_ == 0 and v > -0.75) else RED
                    if v < -0.7:
                        col = RED_HI
                cols[(x, y)] = col
        c.ring(set(cols))
        for q, col in cols.items():
            c.px[q] = col
        # eye
        ey = rnd(11.5 + 0.6 * math.sin(TAU * (0.16 - i / float(n))))
        c.part(disc(16, ey - 2, 2.5), WHITE, hi=False, sh=False)
        c.rect(16, ey - 3, 17, ey - 1, INK)
        return c

    return frames(fr, n), 8


# ---------------------------------------------------------------- rolling capsule
def capsule_roll():
    n = 8

    def fr(i):
        c = Cv(12, 12, "amb_capsule_roll")
        a = TAU * i / n
        nx, ny = math.sin(a), -math.cos(a)              # the red half points along this vector
        m = disc(5.5, 5.5, 4.6)
        c.ring(m)
        for (x, y) in m:
            d = (x + 0.5 - 6) * nx + (y + 0.5 - 6) * ny
            lower = (x + 1, y) not in m or (x, y + 1) not in m
            if abs(d) < 0.55:
                col = DRED
            elif d > 0:
                col = DRED if (lower and x + y > 11) else RED
            else:
                col = CREAM_SH if (lower and x + y > 11) else CREAM
            c.px[(x, y)] = col
        c.dots([(3, 3), (4, 3), (3, 4)], WHITE)
        return c

    return frames(fr, n), 10


# ---------------------------------------------------------------- pinwheel
def pinwheel():
    """Four curled sails drawn per pixel as spiral sectors (colour front, paper
    back fold) under one outline, so the wheel stays clean at every angle."""
    n = 8

    def fr(i):
        c = Cv(18, 30, "amb_pinwheel")
        # pot and stick
        c.rect(9, 9, 9, 23, WOOD)
        c.ring(box(9, 9, 9, 23))
        c.rect(9, 9, 9, 23, WOOD)
        c.part(poly([(5, 24), (14, 24), (12.5, 29), (6.5, 29)]), BLUE)
        c.panel(4, 22, 13, 24, BLUE)
        c.rect(6, 23, 11, 23, GREEN_SH)
        c.dots([(7, 22), (10, 21), (11, 22)], GREEN)
        gr = (0, 0, 1, 1, 0, 0, -1, -1)[i]                 # a blade of grass in the draught
        c.dots([(6 + gr, 20), (6, 21), (12 - gr, 20)], GREEN_HI)
        cx, cy, big = 9.5, 8.5, 7.4
        base = math.pi * i / n
        cols = {}
        for y in range(0, 18):
            for x in range(0, 18):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                r = math.hypot(dx, dy)
                ang = (math.atan2(dy, dx) - base) % TAU
                k = int(ang / (math.pi / 2)) % 4
                a = (ang % (math.pi / 2)) / (math.pi / 2)
                if r > big * (1.0 - 0.62 * a):
                    continue
                if a < 0.5:
                    col = (RED, MUSTARD)[k % 2]
                    if a > 0.36:
                        col = (DRED, MUSTARD_SH)[k % 2]
                else:
                    col = PAPER if a < 0.8 else CREAM
                cols[(x, y)] = col
        c.ring(set(cols))
        for q, col in cols.items():
            c.px[q] = col
        c.part({(9, 8)}, WHITE, hi=False, sh=False)
        return c

    return frames(fr, n), 12


# ---------------------------------------------------------------- arcade cabinet
INVADER = ["..#...#..", "...#.#...", "..#####..", ".##.#.##.", "#########", "#.#####.#", "#.#...#.#", "...#.#..."]


def arcade_cab():
    n = 16

    def tri(i, period, span):
        t = (i % period) / float(period)
        return span * (2 * t if t < 0.5 else 2 - 2 * t)

    def fr(i):
        c = Cv(40, 78, "amb_arcade_cab")
        # side panels and top face
        c.part(poly([(5, 1), (34, 1), (37, 5), (2, 5)]), RED_HI, hi=False, sh=False)
        c.panel(2, 5, 37, 76, DRED, r=1, hi=False, sh=False)
        c.panel(5, 5, 34, 76, RED, hi=False)
        # marquee
        c.rect(6, 6, 33, 13, MUSTARD)
        c.ring(box(6, 6, 33, 13))
        c.rect(6, 6, 33, 13, MUSTARD if i % 8 < 6 else MUSTARD_HI)
        star = [(19, 7), (20, 7), (18, 8), (19, 8), (20, 8), (21, 8), (16, 9), (17, 9), (18, 9), (19, 9), (20, 9),
                (21, 9), (22, 9), (23, 9), (18, 10), (19, 10), (20, 10), (21, 10), (17, 11), (18, 11), (21, 11),
                (22, 11), (17, 12), (22, 12)]
        c.dots(star, RED)
        for k in range(4):
            lit = (k + i) % 4 < 2
            for x in (8 + k * 2, 31 - k * 2):
                c.dot(x, 9 + (k % 2), WHITE if lit else MUSTARD_SH)
        # screen
        c.rect(6, 15, 33, 41, INK)
        scr = box(8, 17, 31, 39, 1)
        c.fill(scr, NAVY_SH)
        for k, (sx, sy) in enumerate(((10, 19), (27, 21), (14, 30), (29, 33), (21, 18), (11, 36), (24, 27))):
            if (i + k * 3) % 8 < 5:
                c.dot(sx, sy, PAPER if (i + k) % 3 else SKY)
        ix = 9 + rnd(tri(i, 16, 12))
        iy = 19 + rnd(tri(i, 8, 5))
        legs = i % 2
        for j, row in enumerate(INVADER):
            if j == 7 and legs:
                row = "..#...#.."
            for k, ch in enumerate(row):
                if ch == "#":
                    c.dot(ix + k, iy + j, GREEN_HI if j < 4 else GREEN)
        c.eyes(ix + 3, iy + 3, 1, 2, look=0, gap=1, ringed=False)
        # "insert coin": a blinking coin and dashes
        if i % 4 < 2:
            c.rect(11, 35, 12, 36, MUSTARD)
            for k in range(5):
                c.rect(15 + k * 3, 36, 16 + k * 3, 36, PAPER)
        base_y = 33
        c.rect(9, base_y, 30, base_y, BLUE) if i % 4 >= 2 else None
        c.dots([(9, 18), (10, 18), (9, 19)], SKY)
        # control panel: sloped top face with a joystick and buttons
        c.part(poly([(4, 43), (36, 43), (38, 50), (2, 50)]), CREAM, hi=False)
        c.rect(3, 51, 36, 52, CREAM_SH)
        c.ring(box(2, 50, 37, 52))
        c.rect(3, 51, 36, 52, CREAM_SH)
        tilt = {4: -1, 5: -1, 12: 1, 13: 1}.get(i, 0)
        c.fill(line(11, 47, 11 + tilt, 44), INK)
        c.part(disc(11 + tilt * 2, 42, 1.8), RED, sh=False)
        c.part(ell(11.5, 47.5, 2.5, 1.2), DSTEEL, hi=False, sh=False)
        press = i in (6, 14)
        c.part(ell(22, 46.5 + (0.5 if press else 0), 2, 1.3), MUSTARD, hi=False)
        c.part(ell(29, 46.5, 2, 1.3), BLUE, hi=False)
        # lower body: stripes and the coin door
        c.rect(6, 56, 33, 57, CREAM)
        c.rect(6, 59, 33, 59, MUSTARD)
        c.panel(13, 62, 26, 73, DSTEEL, r=1)
        for sx in (15, 21):
            c.rect(sx, 64, sx + 3, 68, INK)
            c.rect(sx + 1, 65, sx + 2, 66, RED if (i // 2 + sx) % 2 else DRED)
        c.rect(16, 71, 23, 71, STEEL)
        c.rect(3, 77, 36, 77, INK)
        return c

    return frames(fr, n), 6


# ---------------------------------------------------------------- soap bubbles
def bubbles():
    n = 15
    specs = [(5, 0, 2.6, 0.0), (10, 5, 2.0, 0.4), (7, 10, 3.0, 0.7)]

    def fr(i):
        c = Cv(16, 32, "amb_bubbles")
        for (x0, born, rmax, ph) in specs:
            age = (i - born) % n
            if age > 11:
                continue
            y = 28 - age * 2.0
            x = x0 + 1.2 * math.sin(TAU * (age / 9.0 + ph))
            xi, yi = rnd(x), rnd(y)
            if age == 11:                                # pop: a ring of ticks
                r = int(rmax) + 1
                for dx, dy in ((-r, -r), (r, -r), (-r, r), (r, r)):
                    c.dot(xi + dx, yi + dy, INK)
                for dx, dy in ((-r, 0), (r, 0), (0, -r)):
                    c.dot(xi + dx, yi + dy, SKY_HI)
                continue
            r = min(rmax, 1.0 + age * 0.5)
            m = disc(xi, yi, r)
            c.part(m, SKY_HI, hi=False, sc=SKY)
            if r >= 2:
                c.dot(xi - 1, yi - 1, WHITE)
                c.dot(xi + 1, yi + 1, PINK_HI)
        return c

    return frames(fr, n), 8


# ================================================================ extras

def candle():
    n = 5
    shapes = [(0, 5), (1, 6), (0, 4), (-1, 6), (0, 5)]

    def fr(i):
        c = Cv(10, 20, "amb_candle")
        lean, h = shapes[i]
        # flame: teardrop
        base_y = 9
        pts = [(5 + lean, base_y - h - 0.5), (7.2, base_y - 1.5), (5, base_y + 0.5), (2.8, base_y - 1.5)]
        c.part(poly(pts) | ell(5, base_y - 1.5, 2.2, 1.8), ORANGE, hi=False, sh=False)
        c.fill(ell(5, base_y - 1.2, 1.1, 1.5), MUSTARD_HI)
        c.rect(4, 10, 5, 10, INK)
        # wax and holder
        c.panel(3, 11, 6, 16, PAPER)
        c.dot(3, 12 + (i % 3), CREAM_SH)
        c.part(ell(5, 17.5, 4, 1.5), MUSTARD, hi=False)
        return c

    return frames(fr, n), 9


def music_notes():
    n = 10

    def note(c, x, y, col, double=False):
        c.fill(dilate({(x, y + 4), (x + 1, y + 4), (x, y + 5), (x + 1, y + 5)} | {(x + 2, yy) for yy in range(y, y + 5)}
                      | {(x + 3, y), (x + 4, y + 1)}), INK)
        c.rect(x, y + 4, x + 1, y + 5, col)
        c.rect(x + 2, y, x + 2, y + 4, col)
        c.dots([(x + 3, y), (x + 4, y + 1)], col)

    def fr(i):
        c = Cv(16, 24, "amb_music_notes")
        for k, (x0, born, col) in enumerate(((2, 0, RED), (8, 5, BLUE))):
            age = (i - born) % n
            if age > 7:
                continue
            y = 16 - age * 2
            x = x0 + rnd(1.5 * math.sin(TAU * age / 8.0 + k))
            if age == 7:
                c.dots([(x + 1, y + 2), (x + 3, y + 4), (x, y + 5), (x + 4, y + 1)], col)
            else:
                note(c, x, y, col)
        return c

    return frames(fr, n), 8


def claw_mobile():
    n = 12

    def fr(i):
        c = Cv(34, 30, "amb_claw_mobile")
        s = wave(i, n)
        tilt = rnd(1.6 * s)
        c.rect(17, 0, 17, 4, INK)
        # crossbar tilting around its middle
        bar = stroke([(6, 5 + tilt), (17, 5), (28, 5 - tilt)], 2, smooth=False)
        c.part(bar, STEEL, hi=False, sh=False)
        # left: a capsule; middle: the claw; right: a star
        sw = rnd(1.2 * wave(i, n, -0.2))
        ly = 6 + tilt
        c.fill(line(7, ly, 7 + sw, ly + 7), INK)
        m = disc(7 + sw, ly + 12, 3.6)
        c.part(m, CREAM)
        c.fill({q for q in m if q[1] <= ly + 12}, RED)
        c.dot(6 + sw, ly + 10, WHITE)
        # claw: a mustard hub and three hose prongs that open and close
        op = (0, 1, 2, 2, 1, 0)[i % 6]
        c.rect(17, 7, 17, 13, INK)
        for sgn in (-1, 1):
            c.noodle([(17 + sgn * 2, 16), (17 + sgn * (4 + op), 20), (17 + sgn * (2 + op), 25)], 2, INK)
            c.dot(17 + sgn * (2 + op) + (0 if sgn < 0 else 1), 26, STEEL_HI)
        c.rect(17, 16, 18, 22, INK)
        c.part(box(14, 13, 21, 16, 1), MUSTARD, hi=False)
        c.dots([(16, 14), (19, 14)], WHITE)
        # star
        ry = 6 - tilt
        c.fill(line(27, ry, 27 - sw, ry + 5), INK)
        sx, sy = 27 - sw, ry + 10
        star = {(sx, sy - 3), (sx, sy - 2), (sx - 1, sy - 2), (sx + 1, sy - 2)}
        star |= {(sx + d, sy - 1) for d in range(-3, 4)} | {(sx + d, sy) for d in range(-2, 3)}
        star |= {(sx + d, sy + 1) for d in range(-2, 3)} | {(sx - 2, sy + 2), (sx - 1, sy + 2), (sx + 1, sy + 2), (sx + 2, sy + 2)}
        c.part(star, MUSTARD, hi=False)
        c.dot(sx - 1, sy - 1, WHITE)
        c.rect(17, 0, 17, 3, INK)
        return c

    return frames(fr, n), 5


def furin():
    n = 9

    def fr(i):
        c = Cv(12, 30, "amb_furin")
        s = wave(i, n)
        c.rect(6, 0, 6, 3, INK)
        bell = ell(6.5, 8, 4, 4.5) - {(x, y) for x in range(12) for y in range(11, 16)}
        c.part(bell, SKY, hi=False)
        c.dots([(4, 6), (4, 7)], WHITE)
        c.dots([(7, 8), (8, 7), (8, 9)], RED)            # painted goldfish dabs
        c.rect(3, 10, 9, 10, SKY_SH)
        # clapper and paper strip, swinging from the bell
        k = 2.5 * s
        cx = lambda y: 6 + rnd(k * (y - 10) / 18.0)
        for y in range(11, 17):
            c.dot(cx(y), y, INK)
        c.dot(cx(13), 13, STEEL_HI)
        strip_ = set()
        for y in range(17, 28):
            for x in (-1, 0, 1):
                strip_.add((cx(y) + x, y))
        c.part(strip_, PAPER, hi=False)
        c.dots([(cx(20), 20), (cx(22), 22), (cx(24), 24)], RED)
        if i in (2, 6):                                   # ting!
            c.dots([(1, 5), (0, 8)] if i == 2 else [(11, 5), (11, 8)], MUSTARD_HI)
        c.dot(6, 0, INK)
        return c

    return frames(fr, n), 6


def spinning_top():
    n = 4

    def fr(i):
        c = Cv(14, 14, "amb_spinning_top")
        lean = (0, 1, 0, -1)[i]
        c.fill(line(7 + lean, 0, 7, 3), INK)
        c.fill(line(6 + lean, 0, 6, 3), WOOD)
        body = ell(7, 6.5, 5.5, 3)
        cone = poly([(2.5, 8), (11.5, 8), (7, 13)])
        c.part(body | cone, RED, hi=False)
        for (x, y) in body:
            band = (x + i * 3) % 12
            if y in (5, 6) and band < 5:
                c.px[(x, y)] = MUSTARD
            elif y in (5, 6) and band < 7:
                c.px[(x, y)] = PAPER
        c.rect(4, 4, 6, 4, RED_HI)
        c.dot(7, 12, STEEL_HI)
        if i % 2:
            c.dots([(0, 12), (13, 12)], CREAM_SH)
        return c

    return frames(fr, n), 12


# ---------------------------------------------------------------- tear-off calendar (extra)
def calendar():
    """Himekuri day calendar on the wall; the corner of the top page lifts in the draught."""
    n = 14
    curl = [0, 0, 1, 2, 3, 2, 1, 0, 0, 1, 2, 1, 0, 0]

    def fr(i):
        c = Cv(18, 26, "amb_calendar")
        c.panel(1, 2, 16, 24, PAPER, hi=False, sh=False)
        c.rect(1, 23, 16, 23, CREAM)
        c.rect(1, 24, 16, 24, CREAM_SH)
        c.rect(1, 2, 16, 6, RED)
        c.rect(1, 6, 16, 6, DRED)
        c.rect(1, 2, 16, 2, RED_HI)
        for x in (4, 8, 12):
            c.rect(x, 4, x + 1, 4, PAPER)
        c.rect(1, 7, 16, 7, INK)
        c.rect(8, 0, 9, 1, DSTEEL)                       # the nail and its loop
        c.dot(8, 0, STEEL_HI)
        for d, ch in enumerate("15"):
            for j, row in enumerate(TINY[ch]):
                for k, bit in enumerate(row):
                    if bit == "1":
                        c.rect(3 + d * 7 + k * 2, 9 + j * 2, 4 + d * 7 + k * 2, 10 + j * 2, RED)
        c.rect(4, 20, 8, 20, DSTEEL)
        c.rect(10, 20, 13, 20, NAVY)
        s = curl[i]
        if s:
            sz = 1 + s * 2
            for d in range(sz):
                for e in range(sz - d):
                    c.dot(16 - d, 22 - e, CREAM)
            for d in range(sz):
                c.dot(16 - d, 22 - (sz - 1 - d), INK)
                if d + 1 < sz:
                    c.dot(16 - d - 1, 22 - (sz - 1 - d), CREAM_SH)
        return c

    return frames(fr, n), 6


# ---------------------------------------------------------------- noren curtain (extra)
NOREN_KANA = [
    ["0010101", "0010000", "1111110", "0010010", "0010010", "0100010", "1001100"],
    ["0000110", "0111000", "0001000", "1111111", "0001000", "0001000", "0110000"],
    ["0000000", "0010000", "0011110", "1110010", "0010100", "0010000", "0001000"],
]


def noren():
    """Short split shop curtain on a rod; a ripple runs along the hems of the three panels."""
    n = 10

    def fr(i):
        c = Cv(48, 22, "amb_noren")
        for k in range(3):
            x0 = 2 + 15 * k
            m = set()
            hem = {}
            for q in range(14):
                ph = TAU * (i / float(n) - 0.17 * k) - q * 0.5
                hem[q] = 18 + rnd(1.3 * math.sin(ph))
                for y in range(3, hem[q] + 1):
                    m.add((x0 + q, y))
            c.part(m, NAVY, hi=False, sh=False)
            for q in range(14):
                ph = TAU * (i / float(n) - 0.17 * k) - q * 0.5
                if math.cos(ph) > 0.55:                       # the fold catching the light
                    c.rect(x0 + q, 4, x0 + q, hem[q] - 3, BLUE)
                elif math.cos(ph) < -0.75:
                    c.rect(x0 + q, 4, x0 + q, hem[q] - 3, NAVY_SH)
                c.dot(x0 + q, hem[q] - 2, PAPER)
                c.rect(x0 + q, hem[q] - 1, x0 + q, hem[q], RED)
            for j, row in enumerate(NOREN_KANA[k]):
                for q, bit in enumerate(row):
                    if bit == "1":
                        c.dot(x0 + 3 + q, 6 + j, PAPER)
        c.rect(0, 0, 47, 3, INK)
        c.rect(0, 1, 47, 1, WOOD_HI)
        c.rect(0, 2, 47, 2, WOOD)
        c.dot(0, 1, MUSTARD)
        c.dot(47, 1, MUSTARD)
        return c

    return frames(fr, n), 7
