"""Machines and their animated parts.

Each machine is drawn twice by the same function (power off / power on); the
`_lit` overlay is exactly the set of pixels that differ, so off + overlay == on.

Anchor coordinates used by the game code are collected in ANCHORS.
"""
import os
import random

from pixlib import (Spr, INK, DARK, CREAM, CORAL, MINT, MUSTARD, TEAL, STEEL, WHITE, PINK, RED, NIGHT,
                    GLASS, GLASS_HI, GLOW, GREEN, WOOD, hx, shade, mix, ell, box, poly, path, mir,
                    glyph, TINY, sheet)

VIOLET = hx("5b5fb0")
PLUM = hx("8a7fd1")

SIZES = {
    "machine_001": (36, 60), "machine_002": (36, 60), "machine_003": (36, 60), "machine_004": (36, 60),
    "machine_005": (56, 76), "machine_006": (56, 76),
    "machine_001_lit": (36, 60), "machine_002_lit": (36, 60), "machine_003_lit": (36, 60),
    "machine_004_lit": (36, 60), "machine_005_lit": (56, 76), "machine_006_lit": (56, 76),
    "gacha_knob": (12, 12),
    "capsule_coral": (10, 10), "capsule_mint": (10, 10), "capsule_mustard": (10, 10),
    "capsule_teal": (10, 10), "capsule_gold": (10, 10),
    "claw_open": (16, 16), "claw_closed": (16, 16),
    "plinko_ball": (6, 6),
}

GACHA_COLOURS = {1: CORAL, 2: MINT, 3: MUSTARD, 4: TEAL}

# Plinko layout (shared with the report / game code)
PEG_X0, PEG_Y0, PEG_DX, PEG_DY, PEG_ROWS = 12, 15, 8, 5, 6
SLOT_X = [12, 20, 28, 36, 44]
SLOT_TOP, SLOT_BOTTOM = 44, 50

ANCHORS = {
    "gacha": {"knob_centre": (18, 38), "knob_recess_px": "x 13..22, y 33..42", "coin_slot": (29, 36),
              "chute_mouth_centre": (18, 52), "chute_opening_px": "x 11..24, y 49..54",
              "dome_inner_px": "x 4..31, y 8..26"},
    "crane": {"glass_px": "x 6..49, y 8..44", "rail_y": 9, "claw_hang_y": 10, "claw_x_range": (14, 44),
              "prize_pile_top_y": 34, "cabinet_floor_y": 44, "drop_hole_px": "x 40..49, y 37..44",
              "joystick": (14, 48), "chute_centre": (44, 64), "chute_opening_px": "x 39..48, y 60..68"},
    "plinko": {"board_px": "x 8..47, y 10..50", "ball_drop": (28, 11), "peg_origin": (PEG_X0, PEG_Y0),
               "peg_dx": PEG_DX, "peg_dy": PEG_DY, "peg_rows": PEG_ROWS,
               "even_rows": "5 pegs at x 12,20,28,36,44", "odd_rows": "4 pegs at x 16,24,32,40",
               "slot_x": SLOT_X, "slot_y": (SLOT_TOP, SLOT_BOTTOM), "slot_floor_y": 50,
               "button": (28, 56), "chute_centre": (28, 66), "chute_opening_px": "x 22..33, y 63..69"},
}


def dim(c, lit, k=0.38):
    return c if lit else mix(c, NIGHT, k)


def mini_capsule(s, cx, cy, col, rng, lit, inside):
    """6 px capsule inside a dome; only pixels of `inside` are touched."""
    m = ell(cx, cy, 3, 3)
    tmp = {}
    for (x, y) in m:
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + a, y + b) not in m:
                tmp[(x + a, y + b)] = INK
    mode = rng.randrange(3)
    clear = dim(CREAM, lit, 0.3)
    c = dim(col, lit, 0.25)
    for (x, y) in m:
        if mode == 0:
            top = y + 0.5 < cy
        elif mode == 1:
            top = x + 0.5 < cx
        else:
            top = (x + 0.5 - cx) + (y + 0.5 - cy) < 0
        tmp[(x, y)] = c if top else clear
    tmp[(int(cx) - 2, int(cy) - 2)] = shade(c, 1) if lit else c
    for q, v in tmp.items():
        if q in inside:
            s.put(q[0], q[1], v)


def chute(s, x0, y0, x1, y1, lit):
    s.rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1, INK)
    s.rect(x0, y0, x1, y1, DARK)
    s.rect(x0, y0, x1, y0 + 1, STEEL)           # flap
    s.hline(x0, x1, y0 + 1, shade(STEEL, -1))
    s.hline(x0 + 1, x1 - 1, y1, shade(DARK, 1))  # tray lip
    s.put(x0, y0, WHITE)


def feet(s, x0, x1, y):
    s.rect(x0, y, x1, y + 1, INK)
    s.rect(x0 + 1, y, x1 - 1, y, DARK)
    for fx in (x0 + 1, x1 - 6):
        s.rect(fx, y + 1, fx + 5, y + 2, INK)
        s.rect(fx + 1, y + 1, fx + 4, y + 1, DARK)


def gacha(n, lit):
    col = GACHA_COLOURS[n]
    s = Spr(36, 60)
    rng = random.Random(100 + n)
    hi, lo = shade(col, 1), shade(col, -1)
    # top cap with sign plate
    s.panel(6, 0, 29, 7, col, r=2)
    s.rect(9, 2, 26, 5, INK)
    plate = GLOW if lit else dim(CREAM, False, 0.25)
    s.rect(10, 3, 25, 4, plate)
    mark = RED if lit else dim(RED, False)
    for x in (11, 12, 14, 16, 17, 19, 21, 22, 24):
        s.put(x, 3 + (x % 2), mark)
    # dome
    dome = box(3, 7, 32, 27, r=4)
    inside = {q for q in dome if all((q[0] + a, q[1] + b) in dome for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    s.puts(dome, INK)
    glass = GLASS_HI if lit else GLASS
    s.puts(inside, glass)
    s.puts({q for q in inside if q[1] <= 9 or q[0] <= 5}, shade(glass, 0.5) if lit else shade(glass, -0.6))
    palette = [CORAL, MINT, MUSTARD, TEAL, PINK, PLUM, col, col]
    spots = [(7, 23.5), (13.5, 24), (20, 23.5), (26.5, 24), (30, 22.5), (10, 18.5), (16.5, 19), (23, 18.5),
             (28.5, 18), (6.5, 16.5), (13, 13.5), (19.5, 14), (25.5, 13), (8, 11.5), (30, 13)]
    order = list(range(len(spots)))
    rng.shuffle(order)
    for k in sorted(order[:14], key=lambda i: spots[i][1]):
        x, y = spots[k]
        mini_capsule(s, x + rng.choice((-0.5, 0, 0.5)), y, palette[rng.randrange(len(palette))], rng, lit, inside)
    # glass reflections
    refl = WHITE if lit else GLASS_HI
    for (x, y) in ((6, 12), (6, 11), (7, 10), (8, 9), (6, 14), (9, 9)):
        s.put(x, y, refl)
    if lit:
        for (x, y) in ((28, 9), (29, 10), (29, 11), (7, 12), (8, 10)):
            s.put(x, y, WHITE)
    # collar
    s.rect(2, 27, 33, 29, INK)
    s.hline(3, 32, 28, STEEL)
    s.put(3, 28, WHITE)
    s.hline(28, 32, 28, shade(STEEL, -1))
    # body
    s.panel(2, 29, 33, 57, col)
    s.rect(3, 45, 32, 45, lo)
    s.rect(3, 46, 32, 46, hi)
    # crank plate, hole left empty for the knob
    plate_m = ell(18, 38, 7, 7)
    s.part(plate_m, CREAM, depth=1)
    s.puts(ell(18, 38, 5, 5), DARK)
    s.puts({q for q in ell(18, 38, 5, 5) if q not in ell(18.6, 38.6, 4.6, 4.6)}, INK)
    s.rect(17, 37, 18, 38, STEEL)
    # price label with the machine number
    s.rect(4, 33, 8, 41, INK)
    s.rect(5, 34, 7, 40, CREAM)
    glyph(s, TINY[str(n)], 5, 35, INK)
    # coin slot
    s.rect(27, 33, 31, 41, INK)
    s.rect(28, 34, 30, 40, STEEL)
    s.vline(28, 34, 40, shade(STEEL, 1))
    s.vline(29, 35, 38, INK)
    lamp = GREEN if lit else dim(RED, False, 0.5)
    s.put(29, 40, lamp)
    # chute
    chute(s, 11, 48, 24, 54, lit)
    s.rect(5, 49, 7, 53, lo)
    s.rect(28, 49, 30, 53, lo)
    for y in (50, 52):
        s.hline(5, 7, y, INK)
        s.hline(28, 30, y, INK)
    feet(s, 3, 32, 57)
    return s


def plush(s, cx, by, col, kind, lit):
    """Small plush prize sitting on the cabinet floor (by = bottom row)."""
    c = dim(col, lit, 0.3)
    m = ell(cx, by - 3.5, 4, 4)
    if kind == 0:
        m |= ell(cx - 3, by - 7.5, 1.5, 1.5) | ell(cx + 3, by - 7.5, 1.5, 1.5)
    elif kind == 1:
        m |= poly([(cx - 4, by - 5), (cx - 3.5, by - 10), (cx - 0.5, by - 7)]) | poly([(cx + 4, by - 5), (cx + 3.5, by - 10), (cx + 0.5, by - 7)])
    elif kind == 2:
        m |= ell(cx - 2, by - 9, 1.2, 3) | ell(cx + 2, by - 9, 1.2, 3)
    s.part(m, c, depth=1)
    s.put(int(cx) - 2, by - 4, INK)
    s.put(int(cx) + 1, by - 4, INK)
    s.put(int(cx) - 1, by - 2, dim(CREAM, lit, 0.3))
    s.put(int(cx), by - 2, dim(CREAM, lit, 0.3))


def crane(lit):
    s = Spr(56, 76)
    col = PINK
    hi, lo = shade(col, 1), shade(col, -1)
    # marquee
    s.panel(3, 0, 52, 7, col, r=1)
    s.rect(6, 1, 49, 6, INK)
    s.rect(7, 2, 48, 5, GLOW if lit else dim(CREAM, False, 0.3))
    star_c = CORAL if lit else dim(CORAL, False)
    for x0 in (13, 21, 29, 37):
        s.rect(x0, 3, x0 + 4, 4, star_c)
        s.put(x0 + 2, 2, star_c)
        s.put(x0 + 2, 5, star_c)
    for x in (8, 10, 45, 47):
        s.put(x, 3 + (x % 4) // 2, MUSTARD if lit else dim(MUSTARD, False))
    # cabinet frame
    s.rect(3, 7, 52, 46, INK)
    s.rect(4, 8, 5, 45, col)
    s.rect(50, 8, 51, 45, lo)
    s.vline(4, 8, 45, hi)
    # glass interior x 6..49, y 8..44
    glass = GLASS_HI if lit else GLASS
    back = shade(glass, -0.5) if lit else shade(glass, -0.7)
    s.rect(6, 8, 49, 44, back)
    s.rect(6, 8, 49, 8, GLOW if lit else shade(STEEL, -1.5))     # light strip
    s.rect(6, 9, 49, 9, STEEL if lit else shade(STEEL, -1))        # claw rail
    for x in range(8, 49, 6):
        s.put(x, 9, INK)
    # back wall pattern
    for y in range(13, 34, 5):
        for x in range(9 + (y % 2) * 3, 48, 7):
            s.put(x, y, shade(back, 0.6))
    # prize pile
    kinds = [(10, 44, CORAL, 0), (19, 44, MINT, 1), (28, 44, MUSTARD, 2), (36, 44, PLUM, 0),
             (14.5, 41, TEAL, 2), (24, 40, CREAM, 0), (32.5, 41, CORAL, 1)]
    for (cx, by, c, k) in kinds[4:] + kinds[:4]:
        plush(s, cx, by, c, k, lit)
    # drop hole wall
    wall = GLASS_HI if lit else shade(GLASS, 0.6)
    s.vline(40, 36, 44, wall)
    s.hline(40, 49, 36, wall)
    s.rect(41, 37, 49, 44, shade(back, -0.6))
    # reflections
    refl = WHITE if lit else GLASS_HI
    for i in range(7):
        s.put(9 + i, 19 - i, refl)
    for i in range(4):
        s.put(12 + i, 20 - i, refl)
    if lit:
        for i in range(5):
            s.put(41 + i, 27 - i, WHITE)
    # control panel
    s.rect(2, 45, 53, 55, INK)
    s.rect(3, 46, 52, 54, CREAM)
    s.hline(3, 52, 46, WHITE)
    s.rect(3, 53, 52, 54, shade(CREAM, -1))
    s.rect(11, 51, 17, 52, INK)
    s.rect(13, 50, 14, 51, STEEL)
    s.part(ell(14, 48, 2, 2), CORAL)
    for (x, c) in ((24, MUSTARD), (30, MINT)):
        s.rect(x - 1, 49, x + 2, 52, INK)
        s.rect(x, 50, x + 1, 51, c if lit else dim(c, False, 0.3))
        s.put(x, 50, shade(c, 1) if lit else c)
    s.rect(38, 48, 46, 52, INK)
    s.rect(39, 49, 45, 51, STEEL)
    s.hline(41, 43, 50, INK)
    s.put(45, 49, GREEN if lit else dim(RED, False, 0.5))
    # lower body
    s.panel(3, 55, 52, 73, col)
    s.rect(4, 58, 34, 59, CREAM)
    s.rect(4, 61, 34, 61, CREAM)
    # decal: star badge and speaker grille
    badge = ell(12, 67, 4, 4)
    s.part(badge, MUSTARD)
    s.rect(11, 66, 12, 67, CREAM)
    for y in (64, 66, 68, 70):
        s.hline(21, 31, y, lo)
    chute(s, 39, 60, 48, 68, lit)
    feet(s, 3, 52, 73)
    return s


def plinko(lit):
    s = Spr(56, 76)
    col = VIOLET
    hi, lo = shade(col, 1), shade(col, -1)
    # arched marquee
    m = box(6, 0, 49, 9, r=3)
    s.puts(m, INK)
    s.puts({q for q in m if all((q[0] + a, q[1] + b) in m for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}, col)
    s.rect(10, 2, 45, 7, INK)
    s.rect(11, 3, 44, 6, GLOW if lit else dim(CREAM, False, 0.3))
    gold = MUSTARD if lit else dim(MUSTARD, False)
    for x0 in (14, 22, 30, 38):
        s.rect(x0, 4, x0 + 3, 5, RED if lit else dim(RED, False))
    s.rect(26, 3, 29, 6, gold)
    # frame
    s.rect(3, 8, 52, 52, INK)
    s.rect(4, 9, 51, 51, col)
    s.vline(4, 9, 51, hi)
    s.vline(51, 9, 51, lo)
    s.hline(4, 51, 9, hi)
    # lamps down both pillars
    for y in range(13, 50, 6):
        for x in (5, 49):
            s.rect(x, y, x + 1, y + 1, GLOW if lit else dim(MUSTARD, False, 0.45))
    # board x 8..47, y 10..50
    s.rect(7, 9, 48, 51, INK)
    board = hx("33457a") if lit else NIGHT
    s.rect(8, 10, 47, 50, board)
    for y in range(10, 44):
        for x in range(8, 48):
            if (x + y) % 8 == 0 and y % 2 == 0:
                s.put(x, y, shade(board, 0.5))
    # drop gate marks
    s.rect(24, 10, 31, 10, shade(board, 1))
    s.put(27, 11, gold)
    s.put(28, 11, gold)
    # pegs
    for r in range(PEG_ROWS):
        xs = [PEG_X0 + PEG_DX * i for i in range(5)] if r % 2 == 0 else [PEG_X0 + PEG_DX // 2 + PEG_DX * i for i in range(4)]
        y = PEG_Y0 + PEG_DY * r
        for x in xs:
            s.rect(x - 1, y - 1, x, y, STEEL if not lit else CREAM)
            s.put(x - 1, y - 1, WHITE)
            s.put(x, y, shade(STEEL, -1))
    # slots
    slot_cols = [CORAL, MINT, MUSTARD, MINT, CORAL]
    bounds = [(8, 14), (17, 22), (25, 30), (33, 38), (41, 47)]
    for (x0, x1), c in zip(bounds, slot_cols):
        s.rect(x0, 49, x1, 50, c if lit else dim(c, False, 0.3))
        s.hline(x0, x1, 49, shade(c, 1) if lit else dim(c, False, 0.15))
    for dx in (15, 23, 31, 39):
        s.rect(dx, SLOT_TOP, dx + 1, 50, STEEL)
        s.vline(dx + 1, SLOT_TOP, 50, shade(STEEL, -1))
        s.put(dx, SLOT_TOP, WHITE)
    # control panel
    s.rect(2, 52, 53, 60, INK)
    s.rect(3, 53, 52, 59, CREAM)
    s.hline(3, 52, 53, WHITE)
    s.rect(3, 58, 52, 59, shade(CREAM, -1))
    s.part(ell(28, 56, 3, 2.5), CORAL if lit else dim(CORAL, False, 0.2))
    s.rect(38, 54, 46, 58, INK)
    s.rect(39, 55, 45, 57, STEEL)
    s.hline(41, 43, 56, INK)
    s.put(45, 55, GREEN if lit else dim(RED, False, 0.5))
    for x in (8, 12, 16):
        s.rect(x, 55, x + 2, 57, INK)
        s.put(x + 1, 56, gold)
    # lower body
    s.panel(3, 60, 52, 73, col)
    chute(s, 22, 63, 33, 69, lit)
    for side in (0, 1):
        x0 = 7 if side == 0 else 39
        s.part(poly([(x0 + 5, 62.5), (x0 + 9.5, 67), (x0 + 5, 71.5), (x0 + 0.5, 67)]), MUSTARD)
        s.rect(x0 + 4, 66, x0 + 5, 67, RED)
    feet(s, 3, 52, 73)
    return s


def overlay(off, on):
    out = Spr(off.w, off.h)
    for y in range(off.h):
        for x in range(off.w):
            if on.p[x, y] != off.p[x, y]:
                out.p[x, y] = on.p[x, y]
    return out


def knob():
    s = Spr(12, 12)
    s.part(ell(6, 6, 5, 5), CREAM, depth=1)
    s.rect(4, 1, 7, 10, INK)
    s.rect(5, 1, 6, 10, STEEL)
    s.vline(5, 1, 10, shade(STEEL, 1))
    s.rect(5, 1, 6, 2, CORAL)
    s.put(5, 1, shade(CORAL, 1))
    s.put(4, 0, INK)
    s.put(7, 0, INK)
    s.put(4, 11, INK)
    s.put(7, 11, INK)
    return s


def capsule(col):
    s = Spr(10, 10)
    m = ell(5, 5, 4, 4)
    s.part(m, col, depth=1)
    clear = hx("d8eef0")
    low = {q for q in m if q[1] >= 5}
    s.puts(low, clear)
    s.puts({q for q in low if (q[0] + 1, q[1]) not in m or (q[0], q[1] + 1) not in m}, shade(clear, -1))
    s.puts({q for q in m if q[1] == 5}, shade(col, -1.5))
    s.put(3, 2, WHITE)
    s.put(2, 3, WHITE)
    s.put(3, 7, WHITE)
    return s


def claw(closed):
    s = Spr(16, 16)
    if closed:
        left = path([(6, 5), (4, 7), (4, 11), (6, 14)])
    else:
        left = path([(5, 5), (2, 7), (1, 11), (3, 14)])
    left |= {(x + 1, y) for (x, y) in left}
    for m in (left, mir(left, 16)):
        s.part(m, STEEL, hl=False, sh=False)
    for m in (left, mir(left, 16)):
        s.puts({q for q in m if (q[0] - 1, q[1]) not in m}, shade(STEEL, 1) if m is left else STEEL)
    s.rect(6, 0, 9, 2, INK)
    s.rect(7, 0, 8, 2, STEEL)
    s.part(box(5, 3, 10, 5), CORAL)
    s.put(7, 4, CREAM)
    s.put(8, 4, CREAM)
    return s


def ball():
    s = Spr(6, 6)
    s.part(ell(3, 3, 2, 2), MUSTARD, depth=1)
    s.put(2, 2, WHITE)
    return s


def build_all():
    out = {}
    for n in (1, 2, 3, 4):
        off, on = gacha(n, False), gacha(n, True)
        out["machine_00%d" % n] = off
        out["machine_00%d_lit" % n] = overlay(off, on)
    for n, fn in ((5, crane), (6, plinko)):
        off, on = fn(False), fn(True)
        out["machine_00%d" % n] = off
        out["machine_00%d_lit" % n] = overlay(off, on)
    out["gacha_knob"] = knob()
    for name, c in (("coral", CORAL), ("mint", MINT), ("mustard", MUSTARD), ("teal", TEAL), ("gold", hx("f6d86b"))):
        out["capsule_" + name] = capsule(c)
    gold = out["capsule_gold"]
    gold.put(6, 3, WHITE)
    gold.put(5, 2, WHITE)
    out["claw_open"] = claw(False)
    out["claw_closed"] = claw(True)
    out["plinko_ball"] = ball()
    return out


def composed(out, n, parts=True):
    """Machine with its lit overlay and its animated parts placed (for previews)."""
    base = Spr(*SIZES["machine_00%d" % n])
    base.blit(out["machine_00%d" % n], 0, 0)
    base.blit(out["machine_00%d_lit" % n], 0, 0)
    if not parts:
        return base
    if n <= 4:
        base.blit(out["gacha_knob"], 12, 32)
        base.blit(out["capsule_" + ("coral", "mint", "mustard", "teal")[n - 1]], 13, 46)
    elif n == 5:
        base.vline(27, 10, 17, INK)
        base.vline(28, 10, 17, STEEL)
        base.blit(out["claw_open"], 20, 18)
    else:
        base.blit(out["plinko_ball"], 21, 22)
        base.blit(out["plinko_ball"], 25, 44)
    return base


def previews(out, prev):
    names = ["machine_00%d" % n for n in range(1, 7)]
    row1 = [out[n] for n in names]
    row2 = [composed(out, n, parts=False) for n in range(1, 7)]
    row3 = [composed(out, n) for n in range(1, 7)]
    row4 = [out[n + "_lit"] for n in names]
    sheet(row1 + row2 + row3 + row4, os.path.join(prev, "machines.png"), cols=6, scale=4)
    parts = [out[k] for k in SIZES if not k.startswith("machine_")]
    sheet(parts, os.path.join(prev, "machine_parts.png"), cols=9, scale=4)
