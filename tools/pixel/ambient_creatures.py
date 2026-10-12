"""Ambient creatures and living toys: each function returns (frames, fps).

Frames are PIL RGBA images of the contract size. Loops are built from the frame
index only (sin / tables over the loop length), so they close exactly.
"""
import math

from ambient_lib import (BLUE, CREAM, CREAM_SH, Cv, DRED, DSTEEL, GREEN, GREEN_HI, GREEN_SH, INK, MUSTARD,
                         MUSTARD_HI, MUSTARD_SH, ORANGE, ORANGE_HI, ORANGE_SH, PAPER, PINK, PINK_SH, RED,
                         RED_HI, SKY, SKY_HI, SKY_SH, STEEL, STEEL_HI, TAU, WHITE, WHITE_SH, box, disc,
                         ell, frames, line, poly, rnd, stroke, wave)
from ambient_lib import DSTEEL_SH, NAVY, WOOD, WOOD_HI, WOOD_SH


# ---------------------------------------------------------------- lucky cat
def maneki_neko():
    n = 8
    paw = [0, 1, 2, 2, 1, 0, 0, 1]          # 0 = raised, 2 = beckoning down

    def fr(i):
        c = Cv(26, 32, "amb_maneki_neko")
        w = paw[i]
        bob = 1 if w == 2 else 0
        # cushion
        c.part(ell(12.5, 28, 11, 3), RED)
        c.rect(5, 28, 19, 28, DRED)
        c.dots([(2, 28), (22, 28)], MUSTARD)
        # body
        c.part(ell(11.5, 21 + bob * 0.5, 7.5, 6.5), WHITE)
        c.part(ell(11.5, 22.5, 4, 3.5), CREAM, outline=False, hi=False, sh=False)
        # feet
        c.part(ell(7, 26.5, 2.5, 1.5), WHITE, hi=False)
        c.part(ell(16, 26.5, 2.5, 1.5), WHITE, hi=False)
        # ears
        hy = bob
        for pts, inner in (([(3, 8 + hy), (3, 1 + hy), (9, 4 + hy)], [(4, 3 + hy), (5, 4 + hy), (4, 4 + hy)]),
                           ([(20, 8 + hy), (20, 1 + hy), (14, 4 + hy)], [(18, 3 + hy), (17, 4 + hy), (18, 4 + hy)])):
            c.part(poly(pts), WHITE, hi=False, sh=False)
            c.dots(inner, PINK)
        # head
        c.part(ell(11.5, 10.5 + hy, 8.5, 6.5), WHITE)
        c.eyes(7, 7 + hy, 3, 5, look=1, blink=(i == 6), lid=WHITE)
        c.dots([(10, 13 + hy), (11, 13 + hy)], PINK_SH)
        c.dots([(9, 14 + hy), (10, 15 + hy), (11, 15 + hy), (12, 14 + hy)], INK)
        c.dots([(5, 13 + hy), (16, 13 + hy)], PINK)
        c.dots([(3, 11 + hy), (4, 12 + hy), (18, 12 + hy), (19, 11 + hy)], INK)
        # collar and bell
        c.rect(6, 17 + hy, 16, 17 + hy, RED)
        c.part(box(10, 17 + hy, 11, 18 + hy), MUSTARD, hi=False, sh=False)
        # koban coin held by the left paw
        c.part(ell(6.5, 22.5, 2.5, 3.5), MUSTARD)
        c.dots([(6, 21), (6, 23)], MUSTARD_SH)
        c.glove(4, 20, 1.6)
        # waving arm: a noodle from the shoulder to the glove
        gx, gy = ((22, 6), (22, 9), (21, 12))[w]
        c.noodle([(17, 19 + bob), (21, 18), (gx, gy + 3)], 2)
        c.glove(gx, gy, 2.5)
        c.dots([(gx - 1, gy + 1), (gx + 1, gy + 1)], WHITE_SH)
        return c

    return frames(fr, n), 6


# ---------------------------------------------------------------- mouse
def mouse_run():
    n = 6

    def fr(i):
        c = Cv(22, 14, "amb_mouse_run")
        ext = math.cos(TAU * i / n)              # 1 = fully stretched, -1 = gathered
        air = 1 if ext > 0.4 else 0              # body is higher while stretched
        by = 8 - air
        # tail: a noodle that whips up and down
        tw = wave(i, n, 0.2)
        c.noodle([(4, by), (2, by - 1 - tw), (0, by - 3 + 2 * tw)], 1, INK)
        # hose legs with white shoes
        for (hip, foot) in ((5, 6 - 3 * ext), (12, 12 + 3 * ext)):
            fy = 12 if abs(ext) < 0.9 else 11
            fx = rnd(foot)
            c.noodle([(hip, by + 2), ((hip + foot) / 2.0, by + 3), (foot, fy)], 1, INK, smooth=False)
            c.part({(fx, fy), (fx + 1, fy)}, WHITE, hi=False, sh=False)
        # body
        c.part(ell(9, by + 0.5, 5.2 + 0.8 * ext, 3.2 - 0.3 * ext), STEEL)
        c.rect(7, by + 2, 11, by + 2, CREAM)
        # big round ear, head with a pointed snout, a tall-oval eye
        hx_ = 14 + air
        head = ell(hx_ + 0.5, by, 3.6, 3.4) | {(hx_ + 4, by), (hx_ + 4, by + 1), (hx_ + 5, by + 1)}
        c.part(head, STEEL)
        c.part(disc(hx_ - 2, by - 3, 2.3), STEEL, hi=False, sh=False)
        c.dots([(hx_ - 2, by - 3), (hx_ - 1, by - 3), (hx_ - 2, by - 2), (hx_ - 1, by - 2)], PINK)
        c.dot(hx_ + 6, by + 1, INK)
        c.dot(hx_ + 5, by, INK)
        c.eyes(hx_ + 1, by - 2, 2, 3, look=1, gap=0, ringed=False)
        c.dot(hx_ + 3, by + 2, INK)
        return c

    return frames(fr, n), 14


# ---------------------------------------------------------------- moth
def moth():
    n = 4
    wings = [((4.0, 5.5, 2.7, 2.6), 0), ((4.5, 4.0, 2.2, 2.7), 1), ((4.0, 5.5, 2.7, 2.6), 0), ((4.2, 7.0, 2.6, 2.2), -1)]

    def fr(i):
        c = Cv(14, 12, "amb_moth")
        (wx, wy, rx, ry), bob = wings[i]
        by = 6 + bob
        for sgn in (-1, 1):
            cx = (14 - wx) if sgn > 0 else wx
            m = ell(cx, wy + bob * 0.5, rx, ry)
            c.part(m, CREAM, hi=False)
            c.dot(rnd(cx - 0.5), rnd(wy + bob * 0.5 - 0.5), ORANGE)
        c.part(box(6, by - 2, 7, by + 2), WOOD_BODY, hi=False, sh=False)
        c.dots([(6, by - 2), (7, by - 2)], WHITE)
        c.dots([(5, by - 4), (8, by - 4)], INK)
        return c

    return frames(fr, n), 14


WOOD_BODY = (181, 118, 58)


# ---------------------------------------------------------------- sleeping cat
def cat_sleep():
    n = 20

    def fr(i):
        c = Cv(36, 22, "amb_cat_sleep")
        br = wave(i, n)
        up = 1 if br > 0.3 else 0
        # tail tip flick near the head
        flick = {12: 1, 13: 2, 14: 1}.get(i, 0)
        # body: a curled loaf
        c.part(ell(19.5, 13 - up * 0.5, 14, 6.5 + up * 0.5), ORANGE)
        for sx in (17, 22, 27):
            c.noodle([(sx, 8 - up), (sx + 1, 10 - up), (sx, 12 - up)], 1, ORANGE_SH, smooth=False)
        # tail wrapped along the front
        tail = [(31, 15), (27, 19), (19, 19), (14, 18 - flick)]
        c.fill(stroke(tail, 4), INK)
        c.fill(stroke(tail, 2), ORANGE)
        tx, ty = 14, 18 - flick
        c.rect(tx - 1, ty, tx, ty + 1, CREAM)
        # head resting on the left
        ear = 1 if i in (5, 6) else 0
        c.part(poly([(3, 12), (3, 5 + ear), (8, 9)]), ORANGE, hi=False, sh=False)
        c.part(poly([(15, 12), (15, 5), (10, 9)]), ORANGE, hi=False, sh=False)
        c.dots([(4, 8 + ear), (14, 8)], PINK)
        c.part(ell(9, 13.5 + (0 if up else 0.5), 6.5, 5), ORANGE)
        hy = 0 if up else 1
        c.part(ell(9, 15.5 + hy * 0.5, 3.5, 2.2), CREAM, outline=False, hi=False, sh=False)
        c.dots([(5, 12 + hy), (6, 13 + hy), (7, 12 + hy)], INK)        # closed eyes, "u u"
        c.dots([(11, 12 + hy), (12, 13 + hy), (13, 12 + hy)], INK)
        c.dot(9, 14 + hy, PINK_SH)
        c.dots([(8, 16 + hy), (9, 15 + hy), (10, 16 + hy)], INK)
        return c

    return frames(fr, n), 5


# ---------------------------------------------------------------- goldfish bowl
def fish_bowl():
    n = 16

    def fr(i):
        c = Cv(26, 26, "amb_fish_bowl")
        glass = ell(13, 14.5, 11, 9.5) - {(x, y) for x in range(26) for y in range(0, 6)}
        c.part(glass, SKY, hi=False)
        water = {q for q in glass if q[1] >= 9}
        c.fill({q for q in water if (q[0] + 1, q[1]) in glass and (q[0], q[1] + 1) in glass}, SKY_SH)
        c.rect(5, 9, 20, 9, SKY_HI)
        # gravel and weed
        for gx in range(7, 20):
            if (gx, 22) in glass:
                c.dot(gx, 22, MUSTARD if gx % 2 else CREAM_SH)
        for gx in range(9, 18):
            c.dot(gx, 23, MUSTARD_SH if gx % 3 else MUSTARD)
        sw = rnd(wave(i, n))
        c.noodle([(8, 22), (8 + sw * 0.5, 18), (8 + sw, 14)], 1, GREEN, smooth=False)
        c.dot(9 + sw, 15, GREEN_HI)
        c.noodle([(18, 22), (18 - sw * 0.5, 19), (18 - sw, 16)], 1, GREEN_SH, smooth=False)
        # fish: right for 7 frames, turn, left for 7, turn
        if i < 7:
            d, fx = 1, 8 + i * 1.5
            turn = False
        elif i == 7:
            d, fx, turn = 1, 18, True
        elif i < 15:
            d, fx = -1, 18 - (i - 8) * 1.5
            turn = False
        else:
            d, fx, turn = -1, 8, True
        fy = 15 + rnd(1.2 * wave(i, n, 0.1))
        fx = rnd(fx)
        if turn:
            c.part(ell(fx + 0.5, fy + 0.5, 2, 2.5), ORANGE, hi=False)
            c.eyes(fx - 1, fy - 1, 1, 2, look=0, gap=1, ringed=False)
        else:
            wag = (i % 2) * 2 - 1
            tx = fx - d * 4
            c.part(poly([(tx + 0.5, fy + 0.5), (tx - d * 3 + 0.5, fy - 2.5 + wag * 0.5), (tx - d * 3 + 0.5, fy + 3.5 + wag * 0.5)]),
                   ORANGE_HI, hi=False, sh=False)
            c.part(ell(fx + 0.5, fy + 0.5, 3.5, 2.5), ORANGE)
            ex = fx + d * 1
            c.rect(ex, fy - 1, ex + 1, fy, WHITE)
            c.rect(ex + (1 if d > 0 else 0), fy - 1, ex + (1 if d > 0 else 0), fy, INK)
        # a bubble now and then
        if 3 <= i <= 6:
            c.dot(fx + d * 5, fy - 2 - (i - 3) * 2, WHITE)
        # glass: rim, glare
        c.part(ell(13, 6, 7.5, 1.8), SKY_HI, hi=False, sh=False)
        c.rect(8, 6, 17, 6, SKY)
        c.noodle([(5, 12), (4, 15), (5, 18)], 1, WHITE, smooth=False)
        c.dot(7, 10, WHITE)
        return c.shifted(0, 1)

    return frames(fr, n), 7


# ---------------------------------------------------------------- spider
def spider():
    """Joro-spider colours (mustard body, ink stripes, red tip) and a grey thread,
    so it reads on light walls and on dark or unlit ones alike."""
    n = 20

    def fr(i):
        c = Cv(12, 30, "amb_spider")
        p = (1 - math.cos(TAU * i / n)) / 2.0
        y = 6 + rnd(17 * p)
        down = i < n // 2
        c.rect(6, 0, 6, y - 4, STEEL)
        # legs: 3 visible per side, reaching up when dropping, tucked when climbing
        k = (i % 2)
        for sgn in (-1, 1):
            x0 = 6 + sgn * 3
            for j, dy in enumerate((-2, 0, 2)):
                if down:
                    tip = (x0 + sgn * 2, y + dy - 2 + (k if j != 1 else 0))
                else:
                    tip = (x0 + sgn * 2, y + dy + 1 - (k if j == 1 else 0))
                c.fill(line(x0, y + dy // 2, tip[0] - sgn, y + dy // 2) | {tip}, INK)
                c.dot(tip[0] - sgn, y + dy // 2, MUSTARD_SH)
        body = disc(6, y, 3.0)
        c.part(body, MUSTARD, hi=False)
        c.fill({q for q in body if q[1] == y + 1}, INK)
        c.fill({q for q in body if q[1] == y + 3}, RED)
        c.dot(4, y - 3, MUSTARD_HI)
        c.eyes(4, y - 2, 2, 3, look=(1 if down else -1), gap=1, ringed=False, blink=(i == 14), lid=MUSTARD)
        c.dot(6, 0, STEEL)
        return c

    return frames(fr, n), 6


# ---------------------------------------------------------------- wind-up chick
def windup_toy():
    n = 6

    def fr(i):
        c = Cv(18, 18, "amb_windup_toy")
        step = i % 6
        rock = (0, 1, 0, 0, 1, 0)[step]
        lift_a = step in (0, 1)
        lift_b = step in (3, 4)
        by = 8 + rock
        # key on the back, turning (seen edge-on, half and full)
        kw = (3, 2, 0, 3, 2, 0)[step]
        c.rect(2, by, 4, by, DSTEEL)
        if kw == 0:
            c.rect(2, by - 2, 2, by + 2, STEEL)
            c.ring({(2, yy) for yy in range(by - 2, by + 3)})
            c.rect(2, by - 2, 2, by + 2, STEEL)
        else:
            m = ell(2.5, by - kw + 1.5, 1.5, kw / 2.0 + 0.5) | ell(2.5, by + kw - 0.5, 1.5, kw / 2.0 + 0.5)
            c.part(m, STEEL, sh=False)
        # feet
        for fx, lift in ((6, lift_a), (11, lift_b)):
            fy = 16 - (2 if lift else 0)
            c.fill(line(fx + 1, by + 4, fx + 1, fy - 1), INK)
            c.part(box(fx, fy - 1, fx + 3, fy), ORANGE, hi=False)
        # body and head
        c.part(ell(9.5, by + 0.5, 5, 5), MUSTARD)
        c.part(poly([(4, by - 1), (1.5, by - 4), (6, by - 3)]), MUSTARD, hi=False)      # tail feather
        c.part(ell(7.5, by + 2.5, 2.5, 1.8), MUSTARD_HI, hi=False, sh=False)            # wing
        c.part(poly([(14, by - 2), (16.8, by - 0.5), (14, by + 1.5)]), ORANGE, hi=False)  # beak
        c.part(box(11, by - 4, 12, by - 1), WHITE, hi=False, sh=False)
        c.rect(12, by - 3, 12, by - 1, INK)
        c.dots([(8, by - 6), (9, by - 7), (10, by - 6)], RED)                            # comb
        c.dot(6, by - 3, WHITE)
        return c

    return frames(fr, n), 9


# ---------------------------------------------------------------- balloon
def balloon():
    n = 11

    def fr(i):
        c = Cv(18, 44, "amb_balloon")
        dx = rnd(2 * wave(i, n))
        dy = rnd(1.4 * math.sin(2 * TAU * i / n + 0.6))
        bx, by = 9 + dx, 11 + dy
        # string: bottom end fixed at (9, 43)
        c.noodle([(bx, by + 10), (9 + dx * 0.2 - 1, 30), (9, 43)], 1, INK)
        c.dot(9, 43, INK)
        c.part(poly([(bx - 1.5, by + 10.5), (bx + 0.5, by + 7.5), (bx + 2.5, by + 10.5)]), RED, hi=False, sh=False)
        c.part(ell(bx + 0.5, by, 5.5, 7.5), RED)
        c.fill(stroke([(bx - 3, by - 4), (bx - 4, by - 2), (bx - 4, by)], 1), WHITE)
        c.dot(bx - 2, by - 5, WHITE)
        c.eyes(bx - 1, by - 1, 2, 4, look=(1 if dx >= 0 else -1), gap=1, blink=(i == 5), lid=RED)
        c.dots([(bx, by + 5), (bx + 1, by + 5)], DRED)
        return c

    return frames(fr, n), 5


# ---------------------------------------------------------------- daruma (extra)
def daruma():
    n = 13

    def fr(i):
        c = Cv(22, 24, "amb_daruma")
        c.part(ell(11, 14, 8, 9), RED)
        c.rect(8, 23, 13, 23, INK)
        c.part(ell(11, 11, 5.5, 5), CREAM, hi=False)
        c.eyes(7, 8, 3, 5, look=(1 if i < 7 else -1), blink=(i == 12), lid=CREAM, gap=2)
        c.rect(6, 6, 9, 6, INK)
        c.rect(12, 6, 15, 6, INK)
        c.dots([(9, 14), (10, 15), (11, 15), (12, 14)], INK)
        c.dots([(6, 13), (15, 13)], PINK)
        c.noodle([(8, 18), (11, 20), (14, 18)], 1, MUSTARD, smooth=False)
        c.dots([(11, 18), (11, 22)], MUSTARD)
        out = c.sheared(23, 3, rnd(2.4 * wave(i, n)))     # roly-poly: the base stays put
        return out

    return frames(fr, n), 6


# ---------------------------------------------------------------- tin robot on display (extra)
def robot_display():
    n = 9

    def fr(i):
        c = Cv(22, 28, "amb_robot_display")
        # antenna
        c.rect(10, 2, 10, 4, INK)
        c.part(disc(10, 2, 1.4), RED if i % 3 == 0 else DRED, hi=False, sh=False)
        # legs and shoes
        for lx in (6, 12):
            c.rect(lx + 1, 21, lx + 2, 24, INK)
            c.part(box(lx, 24, lx + 3, 26, 1), DSTEEL, hi=False)
        # arms: noodles with gloves
        sway = (0, 0, 1, 1, 0, 0, -1, -1, 0)[i]
        c.noodle([(4, 15), (3, 18), (3 + sway, 21)], 2)
        c.glove(3 + sway, 22, 1.8)
        c.noodle([(16, 15), (17, 18), (17 + sway, 21)], 2)
        c.glove(17 + sway, 22, 1.8)
        # body with chest lamps
        c.panel(4, 13, 16, 21, STEEL, r=1)
        cols = (RED, MUSTARD, GREEN)
        for k in range(3):
            c.rect(6 + k * 3, 15, 7 + k * 3, 16, cols[k] if (i + k) % 3 == 0 else DSTEEL)
        c.rect(6, 18, 14, 19, INK)
        c.rect(6 + (i * 2) % 8, 18, 7 + (i * 2) % 8, 19, GREEN_HI)
        # head
        c.panel(3, 4, 17, 12, BLUE, r=2)
        c.eyes(6, 6, 3, 5, look=(1, 1, 1, 0, -1, -1, -1, 0, 1)[i], gap=2)
        c.dots([(2, 8), (18, 8)], MUSTARD)
        return c

    return frames(fr, n), 4


# ---------------------------------------------------------------- toy train (extra)
def toy_train():
    """Tin locomotive facing RIGHT: a long boiler with two big pie eyes, a small
    cab, three wheels with a coupling rod, a chuffing bob and smoke."""
    n = 8

    def fr(i):
        c = Cv(36, 18, "amb_toy_train")
        y0 = 1 if i % 4 == 2 else 0
        # cab with a window and a mustard roof
        c.panel(3, 4 + y0, 11, 12 + y0, RED)
        c.part(box(5, 6 + y0, 9, 9 + y0), SKY, hi=False, sh=False)
        c.dot(5, 6 + y0, WHITE)
        c.part(box(2, 3 + y0, 12, 3 + y0), MUSTARD, hi=False, sh=False)
        # chimney, boiler, buffer
        c.part(box(15, 2 + y0, 17, 5 + y0), DSTEEL, hi=False)
        c.rect(15, 3 + y0, 17, 3 + y0, RED)
        c.part(box(12, 5 + y0, 30, 12 + y0, 2), BLUE)
        c.rect(13, 7 + y0, 13, 11 + y0, MUSTARD)
        c.part(box(31, 9 + y0, 33, 12 + y0), RED, hi=False)
        c.dot(34, 11 + y0, MUSTARD)
        # the face
        c.eyes(20, 6 + y0, 3, 5, look=1, gap=1, blink=(i == 5), lid=BLUE)
        c.dot(29, 10 + y0, PINK)
        # smoke puffs leave the chimney and drift back over the cab
        for k in range(2):
            age = (i + k * 4) % 8
            if age < 5:
                r = (0.9, 1.3, 1.7, 1.5, 1.0)[age]
                c.part(disc(15 - rnd(age * 2.6), 2, r), WHITE, hi=False, sc=WHITE_SH)
        # wheels and the coupling rod
        a = TAU * i / n
        for wx in (7, 18, 26):
            c.part(disc(wx, 14, 2.3), MUSTARD, hi=False)
            c.dot(wx, 14, DRED)
        c.dot(7 + rnd(1.4 * math.cos(a)), 14 + rnd(1.4 * math.sin(a)), INK)
        rx, ry = rnd(1.3 * math.cos(a)), rnd(1.3 * math.sin(a))
        c.rect(18 + rx, 14 + ry, 26 + rx, 14 + ry, STEEL_HI)
        c.dot(18 + rx, 14 + ry, INK)
        c.dot(26 + rx, 14 + ry, INK)
        return c

    return frames(fr, n), 10


# ---------------------------------------------------------------- cuckoo clock (extra)
def cuckoo_clock():
    n = 24

    def fr(i):
        c = Cv(26, 40, "amb_cuckoo_clock")
        # pendulum (3 swings per loop) and weights
        s = math.sin(TAU * 3 * i / n)
        px_ = 13 + rnd(4 * s)
        c.noodle([(13, 24), (px_, 34)], 1, INK, smooth=False)
        c.part(disc(px_, 35, 2.2), MUSTARD)
        for wx, wl in ((7, 33), (19, 30)):
            c.rect(wx, 24, wx, wl - 3, DSTEEL)
            c.part(box(wx - 1, wl - 3, wx + 1, wl, 0), WOOD_BODY, hi=False)
        # house
        c.panel(4, 9, 21, 24, WOOD_BODY, r=1)
        c.part(poly([(1, 11), (13, 1), (25, 11), (22, 11), (13, 4), (4, 11)]), RED, hi=False)
        c.part(poly([(5, 10), (13, 4), (21, 10)]), CREAM, hi=False, sh=False)
        # dial
        c.part(disc(12.5, 18, 4.6), PAPER, hi=False)
        c.dots([(12, 14), (13, 14), (12, 22), (13, 22), (9, 18), (16, 18)], DRED)
        c.noodle([(12, 18), (12, 15)], 1, INK, smooth=False)
        c.noodle([(13, 18), (15, 19)], 1, INK, smooth=False)
        # door and bird: out during frames 9..18, calling twice
        out = 9 <= i <= 18
        c.rect(11, 6, 14, 9, INK)
        if not out:
            c.rect(11, 6, 14, 9, GREEN)
            c.ring(box(11, 6, 14, 9))
            c.rect(11, 6, 14, 9, GREEN)
            c.dot(13, 8, MUSTARD)
        else:
            c.rect(9, 6, 9, 9, GREEN_SH)                      # door swung open, edge-on
            c.ring(box(9, 6, 9, 9))
            c.rect(9, 6, 9, 9, GREEN_SH)
            reach = 2 if i in (9, 18) else (5 if i in (11, 12, 15, 16) else 4)
            by = 8
            c.rect(13, by, 13 + reach - 2, by, DSTEEL)        # the spring arm
            bx = 12 + reach
            c.part(disc(bx, by - 1, 2.3), SKY)
            c.dot(bx, by - 2, WHITE)
            c.dot(bx + 1, by - 2, INK)
            beak_open = i in (11, 12, 15, 16)
            c.part(poly([(bx + 2.5, by - 2), (bx + 5.5, by - 0.5 - (1 if beak_open else 0)), (bx + 2.5, by + 0.5)]),
                   ORANGE, hi=False, sh=False)
            if beak_open:
                c.dot(bx + 3, by + 1, ORANGE)
                c.dot(bx + 4, by + 2, INK)
        return c

    return frames(fr, n), 8


# ---------------------------------------------------------------- teru teru bozu (extra)
def teru_bozu():
    """Paper weather doll hanging from a string (top centre fixed), swaying; the hem lags."""
    n = 12

    def fr(i):
        c = Cv(14, 28, "amb_teru_bozu")
        s = wave(i, n)
        hem = max(-1, min(1, rnd(1.2 * wave(i, n, -0.2)) - rnd(1.2 * s)))
        c.rect(7, 0, 7, 5, STEEL)
        skirt = poly([(5, 12), (9, 12), (11 + hem, 23), (3 + hem, 23)])
        skirt |= disc(4 + hem, 22, 1.2) | disc(7 + hem, 22, 1.2) | disc(9 + hem, 22, 1.2)
        c.part(skirt, WHITE)
        c.rect(6, 15, 6, 21, WHITE_SH)
        c.rect(8, 16, 8, 20, WHITE_SH)
        c.part(disc(7, 8, 3.6), WHITE)
        c.rect(5, 12, 9, 12, RED)
        c.dot(10, 13, RED)
        c.dot(4, 13, RED)
        if i == 9:
            c.dots([(5, 8), (6, 8), (8, 8), (9, 8)], INK)
        else:
            ex = 1 if s > 0.3 else (-1 if s < -0.3 else 0)
            c.rect(6 + min(ex, 0), 7, 6 + min(ex, 0), 8, INK)
            c.rect(9 + min(ex, 0), 7, 9 + min(ex, 0), 8, INK)
        c.dots([(6, 10), (7, 11), (8, 10)], INK)
        c.dots([(4, 9), (10, 9)], PINK)
        out = c.sheared(0, 27, 1.6 * s)
        out.dot(7, 0, STEEL)
        return out

    return frames(fr, n), 7


# ---------------------------------------------------------------- akabeko (extra)
def akabeko():
    """Red papier-mache cow facing RIGHT whose head nods on its neck; the tail flicks."""
    n = 8
    nod = [0, 1, 2, 2, 1, 0, -1, 0]

    def fr(i):
        c = Cv(26, 20, "amb_akabeko")
        d = nod[i]
        tw = 1 if i in (2, 3) else 0
        c.noodle([(3, 9), (1, 7 - tw), (1, 4 - tw)], 1, INK, smooth=False)
        c.dot(1, 3 - tw, RED)
        for lx in (5, 14):
            c.part(box(lx, 15, lx + 2, 18), RED, hi=False)
        c.part(box(3, 6, 17, 15, 3), RED)
        c.rect(6, 7, 14, 7, MUSTARD)
        for (sx, sy) in ((7, 10), (12, 11)):
            c.fill(disc(sx, sy, 1.6), WHITE)
            c.dot(sx, sy, INK)
        c.rect(5, 18, 7, 18, INK)
        c.rect(14, 18, 16, 18, INK)
        hy = 8 + d
        c.rect(16, 9, 17, 12, MUSTARD)
        c.dots([(18, hy - 5), (23, hy - 5)], MUSTARD)
        c.dots([(18, hy - 6), (23, hy - 6)], INK)
        c.part(ell(20.5, hy + 0.5, 4.2, 4.6), RED)
        c.fill(ell(21, hy + 3.2, 2.7, 1.7), WHITE)
        c.dots([(20, hy + 3), (22, hy + 3)], INK)
        c.eyes(18, hy - 2, 2, 3, look=1, gap=2, blink=(i == 6), lid=RED, ringed=False)
        return c

    return frames(fr, n), 8


# ---------------------------------------------------------------- jack-in-the-box (extra)
def jack_in_box():
    """A clown on a spring peeks over the rim, pops up, wobbles and sinks back; the crank turns."""
    n = 14
    height = [-5, -5, -4, 3, 8, 6, 8, 7, 8, 8, 7, 3, -2, -5]
    wob = [0, 0, 0, 0, 1, 0, -1, 0, 1, 0, 0, 0, 0, 0]

    def fr(i):
        c = Cv(20, 34, "amb_jack_in_box")
        h, sway = height[i], wob[i]
        # lid standing open at the back, dark inside of the box
        c.panel(3, 16, 16, 23, MUSTARD, hi=False)
        c.rect(4, 17, 15, 17, MUSTARD_HI)
        c.panel(2, 22, 17, 25, DSTEEL_SH, hi=False, sh=False)
        top = 23 - h
        cx = 9 + sway
        for y in range(max(top, 12), 25):                 # the spring
            x = 9 + (y % 2)
            c.rect(x - 1, y, x + 2, y, INK)
            c.rect(x, y, x + 1, y, STEEL_HI if y % 2 else STEEL)
        hy = top - 4
        if i == 3:
            c.part(ell(cx + 1, hy + 0.5, 5.0, 4.0), PAPER)
        else:
            c.part(ell(cx + 1, hy + 0.5, 4.5, 4.5), PAPER)
        c.part(box(cx - 1, top, cx + 2, top), RED, hi=False, sh=False)
        c.part(poly([(cx - 2.5, hy - 3), (cx + 4.5, hy - 3), (cx + 1 + sway, hy - 8)]), BLUE, hi=False)
        c.part(disc(cx + sway, hy - 8, 1.2), MUSTARD, hi=False, sh=False)
        c.rect(cx - 2, hy - 3, cx + 3, hy - 3, MUSTARD)
        if i in (0, 13):
            c.dots([(cx - 1, hy), (cx, hy), (cx + 2, hy), (cx + 3, hy)], INK)
        else:
            lk = 0 if sway >= 0 else -1
            c.rect(cx + lk, hy - 1, cx + lk, hy + 1, INK)
            c.rect(cx + 3 + lk, hy - 1, cx + 3 + lk, hy + 1, INK)
        c.rect(cx + 1, hy + 2, cx + 1, hy + 3, RED)
        c.dots([(cx - 3, hy + 2), (cx + 4, hy + 2)], PINK)
        # the box front, over the clown
        c.panel(2, 24, 17, 32, RED)
        c.rect(3, 25, 16, 25, RED_HI)
        c.rect(3, 30, 16, 30, MUSTARD)
        st = [(9, 26), (10, 26), (8, 27), (9, 27), (10, 27), (11, 27), (7, 28), (8, 28), (9, 28), (10, 28), (11, 28),
              (12, 28), (8, 29), (11, 29)]
        c.dots(st, MUSTARD_HI)
        ky = (27, 28, 29, 28)[i % 4]
        c.dot(18, 28, INK)
        c.dot(19, ky, MUSTARD)
        c.dot(19, ky + 1, INK)
        return c

    return frames(fr, n), 9


# ---------------------------------------------------------------- cymbal monkey (extra)
def cymbal_monkey():
    """Wind-up monkey clapping its cymbals: wide eyes and a hop on every crash."""
    n = 6
    pose = [0, 0, 1, 2, 1, 0]

    def fr(i):
        c = Cv(24, 26, "amb_cymbal_monkey")
        p = pose[i]
        hop = 1 if p == 2 else 0
        # wind-up key on the back
        c.rect(3, 18, 6, 18, DSTEEL)
        c.part(box(1, 16, 2, 20) if i % 2 else box(1, 17, 2, 19), STEEL, sh=False)
        for fx in (7, 13):
            c.part(box(fx, 22, fx + 3, 24), CREAM, hi=False)
        body = ell(12, 18, 5.5, 5.2)
        c.part(body, WOOD)
        c.fill({q for q in body if 15 <= q[1] <= 21 and (q[0] < 10 or q[0] > 13)}, RED)
        c.fill(ell(12, 19, 2, 2.6), CREAM)
        hy = 8 - hop
        for ex in (6, 17):
            c.part(disc(ex, hy, 1.8), WOOD, hi=False)
            c.dot(ex, hy, PINK)
        c.part(ell(12, hy + 0.5, 5.2, 4.8), WOOD)
        c.fill(ell(12, hy + 1.8, 3.9, 3.0), CREAM)
        c.part(box(10, hy - 6, 13, hy - 5), RED, hi=False, sh=False)
        c.dot(14, hy - 6, MUSTARD)
        for ex in (10, 13):
            c.rect(ex, hy - 1 - (1 if p == 2 else 0), ex, hy + 1, INK)
        c.dots([(8, hy + 1), (15, hy + 1)], PINK)
        if p == 2:
            c.rect(11, hy + 3, 12, hy + 4, INK)
            c.dot(12, hy + 4, RED)
        else:
            c.dots([(10, hy + 3), (11, hy + 4), (12, hy + 4), (13, hy + 3)], INK)
        # arms and cymbals
        lx, rx_ = ((3.5, 20.5), (7.0, 17.0), (11.0, 13.0))[p]
        cy = 12.5 if p < 2 else 15.0
        c.noodle([(7, 15), (lx + 1, cy + 1)], 2, INK, smooth=False)
        c.noodle([(16, 15), (rx_ - 1, cy + 1)], 2, INK, smooth=False)
        c.part(ell(lx, cy, 1.4, 4.0), MUSTARD)
        c.part(ell(rx_, cy, 1.4, 4.0), MUSTARD)
        if p == 2:
            c.dots([(8, 11), (16, 11), (7, 16), (17, 16), (12, 10)], WHITE)
            c.dots([(6, 13), (18, 13)], MUSTARD_HI)
        return c

    return frames(fr, n), 10


# ---------------------------------------------------------------- rubber duck (extra)
def rubber_duck():
    """Bath duck rocking on its round belly, with a blink and a squeaky quack."""
    n = 10
    rock = [0, 1, 1, 0, -1, -1, 0, 0, 0, 0]

    def fr(i):
        c = Cv(18, 14, "amb_rubber_duck")
        c.part(poly([(3, 9), (2, 5), (6, 8)]), MUSTARD, hi=False)
        c.part(ell(8.5, 9.5, 5.5, 3.6), MUSTARD)
        c.fill(ell(7.5, 10, 2.4, 1.4), MUSTARD_SH)
        c.rect(6, 9, 8, 9, MUSTARD_HI)
        c.part(disc(11, 4, 3.2), MUSTARD)
        quack = i in (7, 8)
        if quack:
            c.part(box(14, 3, 15, 4), ORANGE, hi=False)
            c.part(box(14, 6, 15, 6), ORANGE, hi=False, sh=False)
        else:
            c.part(box(14, 4, 15, 5), ORANGE, hi=False)
        if i == 4:
            c.rect(11, 4, 12, 4, INK)
        else:
            c.rect(11, 3, 11, 4, WHITE)
            c.rect(12, 3, 12, 4, INK)
        c.dot(9, 2, MUSTARD_HI)
        out = c.sheared(13, 0, float(rock[i]))
        if quack:
            out.dots([(17, 1), (16, 0)], INK)
        return out

    return frames(fr, n), 6
