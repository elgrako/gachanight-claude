"""Room props: bathroom, staff room, reception and hall decoration."""
import os
import random

from pixlib import (Spr, INK, DARK, CREAM, WALL, CORAL, MINT, MUSTARD, TEAL, BATH, TAN, WOOD, WHITE, PINK,
                    RED, STEEL, NIGHT, GLASS, GLASS_HI, GLOW, GREEN, FONT, hx, shade, mix, ell, box, poly,
                    path, mir, glyph, sheet)

SIZES = {
    "toilet": (24, 30), "sink": (24, 34),
    "power_switch_off": (16, 24), "power_switch_on": (16, 24),
    "ceiling_lamp_off": (32, 12), "ceiling_lamp_on": (32, 12),
    "sofa": (60, 30), "counter": (76, 30),
    "computer_off": (24, 22), "computer_on": (24, 22),
    "door_closed": (44, 68), "door_open": (44, 68),
    "shelf_a": (44, 64), "shelf_b": (44, 64),
    "locker": (22, 56), "table": (34, 22),
    "poster_a": (24, 32), "poster_b": (24, 32), "poster_c": (24, 32), "poster_d": (24, 32),
    "sign_gacha": (96, 20), "key": (12, 8), "plant": (18, 30),
}

PORC = hx("f4f4ee")
PLUM = hx("8a7fd1")
SKY = hx("bfe6f2")
LOCKER = hx("7f97a8")


def toilet():
    s = Spr(24, 30)
    # tank (left), bowl facing right
    s.part(box(2, 3, 9, 19, r=1), PORC, depth=1)
    s.part(box(1, 1, 10, 3, r=0), PORC, sh=False)
    s.rect(8, 5, 9, 6, STEEL)
    s.put(10, 5, INK)
    # pedestal
    s.part(poly([(9, 22), (18, 22), (17, 29), (16, 30), (9, 30)]), PORC, depth=1)
    # bowl
    s.part(poly([(8, 15), (22, 15), (23, 18), (20, 23), (15, 25), (8, 25)]), PORC, depth=2)
    # seat and lid line
    s.part(box(8, 13, 22, 15, r=1), BATH, sh=False)
    s.hline(10, 20, 14, shade(BATH, -1))
    s.put(4, 6, WHITE)
    s.put(4, 7, WHITE)
    s.hline(3, 8, 16, shade(PORC, -1))
    return s


def sink():
    s = Spr(24, 34)
    # mirror
    s.panel(4, 0, 19, 14, WOOD)
    s.rect(6, 2, 17, 12, INK)
    s.rect(7, 3, 16, 11, GLASS_HI)
    for i in range(5):
        s.put(8 + i, 9 - i, WHITE)
    for i in range(3):
        s.put(11 + i, 10 - i, WHITE)
    s.rect(14, 9, 16, 11, shade(GLASS_HI, -1))
    # faucet
    s.rect(10, 16, 13, 19, INK)
    s.rect(11, 17, 12, 19, STEEL)
    s.rect(11, 16, 15, 17, INK)
    s.rect(12, 16, 14, 16, STEEL)
    s.put(15, 18, INK)
    s.put(7, 19, CORAL)
    s.put(16, 19, TEAL)
    # basin
    s.part(poly([(1, 20), (23, 20), (22, 24), (18, 27), (6, 27), (2, 24)]), PORC, depth=2)
    s.hline(3, 20, 21, BATH)
    s.hline(4, 19, 22, shade(BATH, -1))
    # pedestal
    s.part(box(9, 27, 14, 33), PORC, depth=1)
    s.rect(8, 32, 15, 33, INK)
    s.rect(9, 32, 14, 32, shade(PORC, -1))
    return s


def power_switch(on):
    s = Spr(16, 24)
    s.panel(1, 0, 14, 23, STEEL, r=1)
    s.rect(3, 2, 12, 5, INK)
    s.rect(4, 3, 11, 4, DARK)
    lamp = GREEN if on else hx("3d5a48")
    s.rect(9, 3, 10, 4, lamp)
    if on:
        s.put(9, 3, WHITE)
    s.put(5, 3, RED if not on else hx("6a3238"))
    s.put(5, 4, RED if not on else hx("6a3238"))
    # lever slot
    s.rect(6, 7, 9, 18, INK)
    s.rect(7, 8, 8, 17, DARK)
    if on:
        s.rect(7, 9, 8, 13, STEEL)
        s.part(box(5, 6, 10, 10, r=1), CORAL)
    else:
        s.rect(7, 12, 8, 16, STEEL)
        s.part(box(5, 15, 10, 19, r=1), CORAL)
    # hazard strip
    for x in range(3, 13):
        s.put(x, 21, MUSTARD if (x // 2) % 2 == 0 else INK)
    s.put(2, 1, WHITE)
    return s


def ceiling_lamp(on):
    s = Spr(32, 12)
    for x in (8, 23):
        s.vline(x, 0, 3, INK)
    s.rect(2, 3, 29, 7, INK)
    s.rect(3, 4, 28, 6, STEEL)
    s.hline(3, 28, 4, shade(STEEL, 1))
    s.hline(3, 28, 6, shade(STEEL, -1))
    s.rect(3, 7, 28, 10, INK)
    tube = GLOW if on else hx("8d99a6")
    s.rect(4, 8, 27, 9, tube)
    if on:
        s.hline(5, 26, 8, WHITE)
    else:
        s.hline(4, 27, 9, shade(tube, -1))
    s.rect(4, 8, 4, 9, shade(STEEL, -1))
    s.rect(27, 8, 27, 9, shade(STEEL, -1))
    return s


def sofa():
    s = Spr(60, 30)
    c = hx("5f9a8f")
    # legs
    for x in (5, 52):
        s.rect(x, 26, x + 3, 29, INK)
        s.rect(x + 1, 26, x + 2, 28, WOOD)
    s.part(box(4, 1, 55, 20, r=3), c, depth=2)
    for x in (20, 39):
        s.put(x, 6, shade(c, -1))
        s.put(x, 11, shade(c, -1))
    s.vline(29, 3, 14, shade(c, -1))
    s.vline(30, 3, 14, shade(c, 0.6))
    # seat cushions
    s.part(box(8, 14, 29, 23, r=2), shade(c, 0.35), depth=1)
    s.part(box(30, 14, 51, 23, r=2), shade(c, 0.35), depth=1)
    # front skirt
    s.part(box(7, 23, 52, 26), shade(c, -0.5))
    # arm rests
    s.part(box(0, 9, 8, 26, r=2), c, depth=2)
    s.part(box(51, 9, 59, 26, r=2), c, depth=2)
    # patch and cushion
    s.rect(36, 16, 41, 20, INK)
    s.rect(37, 17, 40, 19, MUSTARD)
    s.put(37, 17, shade(MUSTARD, 1))
    s.part(box(11, 7, 21, 15, r=2), CORAL)
    s.rect(15, 10, 17, 12, CREAM)
    return s


def counter():
    s = Spr(76, 30)
    s.panel(2, 4, 73, 29, CREAM)
    s.rect(3, 9, 72, 11, CORAL)
    s.hline(3, 72, 9, shade(CORAL, 1))
    s.hline(3, 72, 11, shade(CORAL, -1))
    for x0 in (6, 30, 54):
        s.rect(x0, 14, x0 + 16, 26, INK)
        s.rect(x0 + 1, 15, x0 + 15, 25, WALL)
        s.hline(x0 + 1, x0 + 15, 15, WHITE)
        s.rect(x0 + 1, 25, x0 + 15, 25, shade(WALL, -1))
        s.rect(x0 + 7, 19, x0 + 9, 20, MUSTARD)
    s.rect(3, 28, 72, 28, shade(CREAM, -2))
    # top slab
    s.panel(0, 0, 75, 5, WOOD)
    return s


def computer(on):
    s = Spr(24, 22)
    beige = hx("d9cfb6")
    s.panel(0, 0, 23, 17, beige, r=1)
    s.rect(2, 1, 21, 15, INK)
    scr = hx("2f6b4a") if on else hx("26323c")
    s.rect(3, 2, 20, 14, scr)
    if on:
        s.rect(4, 3, 19, 13, hx("3f9a5c"))
        for y, w in ((4, 9), (6, 12), (8, 6), (10, 11)):
            s.hline(5, 5 + w, y, GREEN)
        s.rect(5, 12, 6, 12, WHITE)
    else:
        for i in range(4):
            s.put(5 + i, 7 - i, hx("3c4c58"))
        s.put(5, 4, hx("3c4c58"))
    s.put(20, 16, GREEN if on else RED)
    s.hline(3, 8, 16, shade(beige, -1))
    # base and keyboard
    s.rect(6, 17, 17, 19, INK)
    s.rect(7, 18, 16, 18, shade(beige, -1))
    s.rect(1, 19, 22, 21, INK)
    s.rect(2, 20, 21, 20, beige)
    for x in range(3, 21, 2):
        s.put(x, 20, shade(beige, -1.5))
    return s


def door(open_):
    s = Spr(44, 68)
    frame = hx("8c6a4c")
    s.panel(0, 0, 43, 67, frame)
    s.rect(3, 3, 40, 67, INK)
    if not open_:
        # night outside seen through the glass leaf
        s.rect(4, 4, 39, 67, TEAL)
        s.vline(4, 4, 67, shade(TEAL, 1))
        s.vline(39, 4, 67, shade(TEAL, -1))
        s.hline(4, 39, 4, shade(TEAL, 1))
        s.rect(7, 7, 36, 58, INK)
        s.rect(8, 8, 35, 57, NIGHT)
        for (x, y) in ((12, 12), (20, 16), (30, 11), (26, 22), (15, 25), (33, 28), (10, 33)):
            s.put(x, y, GLASS_HI)
        s.puts(ell(29, 16, 3, 3) - ell(30.5, 15, 2.6, 2.6), GLOW)
        # skyline
        sk = hx("1a2440")
        for (x0, x1, y0) in ((8, 14, 44), (15, 21, 38), (22, 27, 47), (28, 35, 41)):
            s.rect(x0, y0, x1, 57, sk)
        for (x, y) in ((10, 47), (12, 51), (17, 41), (19, 45), (17, 50), (24, 50), (30, 44), (33, 48), (31, 53)):
            s.put(x, y, MUSTARD)
        # reflections and bars
        for i in range(8):
            s.put(10 + i, 34 - i, GLASS)
            s.put(13 + i, 36 - i, GLASS)
        s.rect(8, 31, 35, 32, TEAL)
        s.hline(8, 35, 31, shade(TEAL, 1))
        s.rect(7, 61, 36, 64, INK)
        s.rect(8, 62, 35, 63, shade(TEAL, -1))
        # push bar and small hanging plate
        s.rect(30, 34, 36, 37, INK)
        s.rect(31, 35, 35, 36, STEEL)
        s.rect(17, 3, 26, 6, INK)
        s.rect(18, 4, 25, 5, CORAL)
    else:
        day = hx("fff6cf")
        s.rect(4, 4, 39, 67, day)
        s.rect(4, 4, 39, 30, SKY)
        s.rect(4, 31, 39, 36, hx("e3f4ef"))
        for (cx, cy, r) in ((16, 14, 4), (21, 15, 5), (26, 14, 3.5), (31, 24, 3), (34, 25, 2.5)):
            s.puts({q for q in ell(cx, cy, r, r * 0.7) if 4 <= q[0] <= 39}, WHITE)
        # bright street
        s.rect(4, 50, 39, 67, hx("f1e2b8"))
        s.rect(4, 37, 39, 49, hx("fbeec5"))
        for (x0, x1, y0) in ((10, 17, 40), (18, 24, 36), (25, 33, 42), (34, 39, 39)):
            s.rect(x0, y0, x1, 49, hx("f0d7a8"))
        s.hline(4, 39, 50, hx("e3c98f"))
        for i in range(6):
            s.hline(8 + i * 5, 10 + i * 5, 58, hx("fff6cf"))
        # door leaf swung inwards, seen edge-on on the left
        s.rect(4, 4, 10, 67, INK)
        s.rect(5, 5, 9, 67, TEAL)
        s.vline(5, 5, 67, shade(TEAL, 1))
        s.vline(9, 5, 67, shade(TEAL, -1))
        s.rect(6, 8, 8, 57, GLASS_HI)
        s.vline(6, 8, 57, WHITE)
        s.rect(6, 31, 8, 32, TEAL)
        s.rect(10, 34, 12, 37, INK)
        s.put(11, 35, STEEL)
        s.put(11, 36, STEEL)
    return s


def toy_box(s, x, y, w, h, c, rng):
    s.rect(x, y, x + w - 1, y + h - 1, INK)
    s.rect(x + 1, y + 1, x + w - 2, y + h - 2, c)
    s.hline(x + 1, x + w - 2, y + 1, shade(c, 1))
    s.vline(x + w - 2, y + 1, y + h - 2, shade(c, -1))
    if w >= 7 and h >= 7:
        s.rect(x + 2, y + 3, x + w - 3, y + h - 4, CREAM)
        tc = rng.choice([CORAL, MINT, MUSTARD, TEAL, PLUM, PINK])
        s.rect(x + 3, y + 4, x + w - 4, y + h - 4, tc)
        s.put(x + 3, y + 4, INK)
        s.put(x + w - 4, y + 4, INK)
    else:
        s.hline(x + 2, x + w - 3, y + h // 2, CREAM)


def toy_plush(s, cx, by, c, kind):
    m = ell(cx, by - 3, 3.5, 3.5) | box(int(cx) - 3, by - 1, int(cx) + 2, by)
    if kind == 0:
        m |= ell(cx - 2.5, by - 6.5, 1.5, 1.5) | ell(cx + 2.5, by - 6.5, 1.5, 1.5)
    elif kind == 1:
        m |= poly([(cx - 3.5, by - 4), (cx - 3, by - 9), (cx - 0.5, by - 6)]) | poly([(cx + 3.5, by - 4), (cx + 3, by - 9), (cx + 0.5, by - 6)])
    else:
        m |= ell(cx - 1.5, by - 8, 1.1, 2.5) | ell(cx + 1.5, by - 8, 1.1, 2.5)
    s.part(m, c, depth=1)
    s.put(int(cx) - 2, by - 3, INK)
    s.put(int(cx) + 1, by - 3, INK)
    s.put(int(cx) - 1, by - 1, CREAM)
    s.put(int(cx), by - 1, CREAM)


def shelf(seed, variant):
    s = Spr(44, 64)
    rng = random.Random(seed)
    wood = WOOD
    back = shade(WOOD, -1.3)
    s.panel(0, 0, 43, 63, wood)
    s.rect(2, 2, 41, 60, INK)
    s.rect(3, 3, 40, 59, back)
    boards = [16, 31, 46]
    floors = boards + [59]
    for y in boards:
        s.rect(3, y, 40, y + 2, INK)
        s.hline(3, 40, y + 1, shade(wood, 0.6))
    cols = [CORAL, MINT, MUSTARD, TEAL, PLUM, PINK, CREAM]
    for row, fy in enumerate(floors):
        base = fy - 1 if fy != 59 else 59
        x = 4
        top = (boards[row - 1] + 3) if row > 0 else 3
        room = base - top + 1
        while x < 38:
            kind = rng.randrange(4)
            plush_row = (row + variant) % 2 == 0
            if plush_row and kind < 2 and x + 8 <= 41:
                toy_plush(s, x + 4, base, rng.choice(cols[:6]), rng.randrange(3))
                x += 9
            else:
                w = rng.choice((6, 7, 8, 9))
                h = rng.choice((7, 9, 10, room - 1))
                h = min(h, room - 1)
                if x + w > 41:
                    w = 41 - x
                if w < 4:
                    break
                toy_box(s, x, base - h + 1, w, h, rng.choice(cols[:6]), rng)
                x += w
    # shadow under each board
    for y in boards:
        for x in range(3, 41):
            if s.get(x, y + 3) == back:
                s.put(x, y + 3, shade(back, -0.7))
    # feet
    s.rect(1, 61, 42, 62, shade(wood, -1))
    if variant == 1:
        s.rect(14, 1, 29, 1, shade(wood, 1))
    return s


def locker():
    s = Spr(22, 56)
    c = LOCKER
    s.panel(1, 0, 20, 53, c)
    s.rect(3, 2, 18, 51, INK)
    s.rect(4, 3, 17, 50, c)
    s.vline(4, 3, 50, shade(c, 1))
    s.hline(4, 17, 3, shade(c, 1))
    s.vline(17, 3, 50, shade(c, -1))
    for y in (6, 8, 10):
        s.hline(7, 14, y, INK)
        s.hline(7, 14, y + 1, shade(c, 1))
    s.rect(6, 15, 15, 19, INK)
    s.rect(7, 16, 14, 18, CREAM)
    s.hline(8, 12, 17, shade(CREAM, -2))
    s.rect(14, 26, 16, 31, INK)
    s.put(15, 27, STEEL)
    s.put(15, 28, STEEL)
    s.put(15, 30, DARK)
    # sticker and dent
    s.rect(6, 36, 9, 39, MUSTARD)
    s.put(7, 37, RED)
    s.put(8, 38, RED)
    s.hline(6, 12, 45, shade(c, -1))
    for x in (2, 16):
        s.rect(x, 53, x + 3, 55, INK)
        s.put(x + 1, 54, DARK)
        s.put(x + 2, 54, DARK)
    return s


def table():
    s = Spr(34, 22)
    for x in (3, 28):
        s.rect(x, 12, x + 2, 21, INK)
        s.vline(x + 1, 12, 20, shade(WOOD, -1))
    s.rect(5, 16, 28, 17, INK)
    s.hline(6, 27, 16, shade(WOOD, -1))
    s.panel(0, 8, 33, 12, WOOD, r=0)
    # mug
    s.part(box(20, 2, 25, 7), CORAL)
    s.rect(21, 2, 24, 2, hx("6b4a3a"))
    s.rect(26, 3, 27, 6, INK)
    s.put(26, 4, CORAL)
    s.put(26, 5, CORAL)
    s.rect(21, 4, 21, 5, CREAM)
    # magazine
    s.rect(6, 6, 15, 7, INK)
    s.hline(7, 14, 6, MINT)
    s.put(8, 6, CREAM)
    s.put(9, 6, CREAM)
    return s


def poster_base(bg):
    s = Spr(24, 32)
    s.rect(0, 0, 23, 31, INK)
    s.rect(1, 1, 22, 30, bg)
    s.vline(22, 1, 30, shade(bg, -1))
    s.hline(1, 22, 30, shade(bg, -1))
    # tape
    for x in (2, 19):
        s.rect(x, 0, x + 2, 1, GLOW)
    return s


def fake_text(s, y, c, widths, x=4):
    for w in widths:
        s.hline(x, x + w - 1, y, c)
        x += w + 1


def poster_a():
    s = poster_base(CREAM)
    for i in range(12):
        import math
        a = i * math.pi / 6
        s.puts(path([(12, 13), (int(12 + 12 * math.cos(a)), int(13 + 12 * math.sin(a)))]) & box(1, 1, 22, 23), MUSTARD if i % 2 else hx("f6d86b"))
    s.part(ell(12, 13, 6, 6), CORAL, depth=2)
    low = {q for q in ell(12, 13, 6, 6) if q[1] >= 13}
    s.puts(low, WHITE)
    s.puts({q for q in low if q[1] == 13}, shade(CORAL, -1.5))
    s.puts({q for q in low if (q[0] + 1, q[1]) not in low or (q[0], q[1] + 1) not in low}, BATH)
    s.put(9, 9, WHITE)
    s.put(10, 8, WHITE)
    s.rect(1, 24, 22, 30, TEAL)
    fake_text(s, 26, CREAM, (4, 3, 5))
    fake_text(s, 28, MUSTARD, (3, 6, 2))
    return s


def poster_b():
    s = poster_base(MINT)
    s.rect(1, 1, 22, 6, TEAL)
    fake_text(s, 3, CREAM, (5, 2, 6))
    # tin robot
    s.rect(11, 7, 12, 9, INK)
    s.part(ell(12, 8, 1.5, 1.5), CORAL, sh=False)
    s.part(box(6, 11, 17, 20, r=1), MUSTARD, depth=1)
    s.rect(8, 13, 10, 15, CREAM)
    s.rect(13, 13, 15, 15, CREAM)
    s.put(9, 14, INK)
    s.put(14, 14, INK)
    s.rect(9, 17, 14, 18, DARK)
    for x in (10, 12, 14):
        s.put(x, 17, CREAM)
    s.part(box(8, 22, 15, 27), CORAL)
    s.rect(4, 22, 6, 26, INK)
    s.rect(17, 22, 19, 26, INK)
    s.put(5, 23, STEEL)
    s.put(18, 23, STEEL)
    s.put(5, 24, STEEL)
    s.put(18, 24, STEEL)
    for (x, y) in ((3, 9), (20, 10), (20, 28), (3, 28)):
        s.put(x, y, WHITE)
    return s


def poster_c():
    s = poster_base(hx("33457a"))
    for (x, y) in ((4, 4), (19, 6), (6, 12), (20, 15), (3, 19), (16, 3), (10, 7)):
        s.put(x, y, GLOW)
    s.puts(ell(17, 9, 4, 4) - ell(19, 7.5, 3.5, 3.5), GLOW)
    # bunny silhouette toy
    m = ell(11, 20, 5.5, 4.5) | ell(8.5, 13, 1.5, 4) | ell(13.5, 13, 1.5, 4)
    s.part(m, hx("f1d9e0"), depth=1)
    s.put(9, 19, INK)
    s.put(13, 19, INK)
    s.put(11, 21, CORAL)
    s.rect(1, 26, 22, 30, CORAL)
    fake_text(s, 28, CREAM, (3, 5, 4))
    return s


def poster_d():
    s = poster_base(hx("f6d86b"))
    s.rect(1, 1, 22, 4, CORAL)
    fake_text(s, 2, CREAM, (6, 3, 4))
    # claw
    s.rect(11, 5, 12, 9, INK)
    s.rect(9, 9, 14, 11, INK)
    s.rect(10, 10, 13, 10, STEEL)
    s.puts(path([(9, 11), (6, 13), (6, 16), (8, 18)]), INK)
    s.puts(path([(14, 11), (17, 13), (17, 16), (15, 18)]), INK)
    # plush
    m = ell(12, 23, 5, 4.5) | ell(8, 18.5, 2, 2) | ell(16, 18.5, 2, 2)
    s.part(m, TEAL, depth=1)
    s.put(10, 22, INK)
    s.put(14, 22, INK)
    s.rect(11, 24, 12, 24, CREAM)
    fake_text(s, 29, RED, (4, 6, 3))
    return s


def sign_gacha():
    s = Spr(96, 20)
    for x in (14, 81):
        s.vline(x, 0, 2, INK)
        s.vline(x + 1, 0, 2, STEEL)
        s.vline(x + 2, 0, 2, INK)
    m = box(0, 2, 95, 19, r=2)
    inner = {q for q in m if all((q[0] + a, q[1] + b) in m for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    s.puts(m, INK)
    s.puts(inner, CORAL)
    s.hline(2, 93, 3, shade(CORAL, 1))
    s.hline(2, 93, 18, shade(CORAL, -1))
    s.rect(17, 3, 78, 18, INK)
    s.rect(18, 3, 77, 18, CREAM)
    s.hline(18, 77, 18, shade(CREAM, -1))
    # letters, 10 x 14 each, 2 px apart
    x = 19
    for ch in "GACHA":
        glyph(s, FONT[ch], x, 4, INK, scale=2)
        x += 12
    for lx in range(19, 79, 12):
        for yy in (4, 5):
            for xx in range(lx, lx + 10):
                if s.get(xx, yy) == INK:
                    s.put(xx, yy, RED)
    # capsule emblems
    for cx, col in ((10, MUSTARD), (86, MINT)):
        mm = ell(cx, 11, 4.5, 4.5)
        s.part(mm, col, depth=1)
        low = {q for q in mm if q[1] >= 11}
        s.puts(low, WHITE)
        s.puts({q for q in low if q[1] == 11}, INK)
        s.put(cx - 2, 8, WHITE)
    # bulbs
    for bx in list(range(5, 17, 4)) + list(range(80, 92, 4)):
        pass
    return s


def key():
    s = Spr(12, 8)
    ring = ell(3.5, 4, 2.5, 3) - {(3, 3), (3, 4)}
    s.part(ring | box(6, 3, 10, 4) | {(8, 5), (10, 5), (10, 6)}, MUSTARD, sh=False)
    s.put(3, 3, INK)
    s.put(3, 4, INK)
    s.put(2, 2, WHITE)
    return s


def plant():
    s = Spr(18, 30)
    leaf = hx("5fae7c")
    for pts in ([(9, 21), (4, 12), (1, 7), (5, 8), (8, 14)], [(9, 21), (14, 12), (17, 5), (13, 7), (10, 14)],
                [(8, 21), (2, 17), (0, 13), (5, 15), (9, 19)], [(10, 21), (16, 18), (18, 14), (13, 15), (9, 19)],
                [(7, 20), (7, 8), (9, 1), (11, 8), (11, 20)]):
        s.part(poly(pts), leaf, depth=1)
    for y in range(5, 19, 2):
        s.put(9, y, shade(leaf, -1))
    s.part(poly([(3, 20), (15, 20), (14, 29), (13, 30), (4, 30)]), hx("c9745a"), depth=1)
    s.part(box(2, 19, 15, 21), hx("c9745a"), sh=False)
    return s


def build_all():
    return {
        "toilet": toilet(), "sink": sink(),
        "power_switch_off": power_switch(False), "power_switch_on": power_switch(True),
        "ceiling_lamp_off": ceiling_lamp(False), "ceiling_lamp_on": ceiling_lamp(True),
        "sofa": sofa(), "counter": counter(),
        "computer_off": computer(False), "computer_on": computer(True),
        "door_closed": door(False), "door_open": door(True),
        "shelf_a": shelf(11, 0), "shelf_b": shelf(29, 1),
        "locker": locker(), "table": table(),
        "poster_a": poster_a(), "poster_b": poster_b(), "poster_c": poster_c(), "poster_d": poster_d(),
        "sign_gacha": sign_gacha(), "key": key(), "plant": plant(),
    }


def previews(out, prev):
    order = ["door_closed", "door_open", "shelf_a", "shelf_b", "locker", "sink", "toilet", "plant",
             "sofa", "counter", "table", "computer_off", "computer_on",
             "sign_gacha", "poster_a", "poster_b", "poster_c", "poster_d",
             "power_switch_off", "power_switch_on", "ceiling_lamp_off", "ceiling_lamp_on", "key"]
    sheet([out[n] for n in order], os.path.join(prev, "props.png"), cols=8, scale=4)
