"""Opaque, seamless room tiles."""
import os

from PIL import Image

from pixlib import (Spr, INK, CREAM, WALL, BATH, TAN, WOOD, WHITE, DARK, hx, shade, mix, sheet)

SIZES = {
    "wall_bath": (16, 16), "wall_corridor": (16, 16), "wall_hall": (16, 16), "wall_reception": (16, 16),
    "wall_staff": (16, 16), "floor_bath": (16, 16), "floor_hall": (16, 16), "floor_staff": (16, 16),
    "trim": (16, 6), "pillar": (12, 16), "ceiling": (16, 8),
}

LINO_A = hx("d8c39a")
LINO_B = hx("b98f6f")
CEIL = hx("3a4668")


def wall_bath():
    s = Spr(16, 16, BATH)
    grout = shade(BATH, -1)
    for y in range(16):
        for x in range(16):
            if x % 8 == 7 or y % 8 == 7:
                s.put(x, y, grout)
            elif x % 8 == 0 or y % 8 == 0:
                s.put(x, y, shade(BATH, 0.7))
    s.put(1, 1, WHITE)
    s.put(9, 9, WHITE)
    return s


def wall_corridor():
    s = Spr(16, 16, WALL)
    for (x, y) in ((3, 4), (11, 12), (13, 2), (6, 10)):
        s.put(x, y, shade(WALL, -0.35))
    return s


def wall_hall():
    s = Spr(16, 16, WALL)
    d = shade(WALL, -0.45)
    lgt = shade(WALL, 0.6)
    for (cx, cy) in ((4, 4), (12, 12)):
        for (a, b) in ((0, -2), (-1, -1), (1, -1), (-2, 0), (2, 0), (-1, 1), (1, 1), (0, 2)):
            s.put((cx + a) % 16, (cy + b) % 16, d)
        s.put(cx, cy, lgt)
    for (cx, cy) in ((12, 4), (4, 12)):
        s.put(cx, cy, d)
    return s


def wall_reception():
    s = Spr(16, 16, WALL)
    for x in (3, 11):
        s.vline(x, 0, 15, shade(WALL, -0.5))
        s.vline(x + 1, 0, 15, shade(WALL, 0.5))
    s.vline(7, 0, 15, mix(WALL, hx("ef7a6d"), 0.28))
    s.vline(15, 0, 15, mix(WALL, hx("ef7a6d"), 0.28))
    return s


def wall_staff():
    s = Spr(16, 16, TAN)
    d = shade(TAN, -0.6)
    lgt = shade(TAN, 0.5)
    for (cx, cy) in ((4, 3), (12, 11)):
        s.put(cx, cy - 1, d)
        s.put(cx - 1, cy, d)
        s.put(cx + 1, cy, d)
        s.put(cx, cy + 1, d)
        s.put(cx, cy, lgt)
    for x in (0, 8):
        s.vline(x, 0, 15, shade(TAN, -0.25))
    return s


def floor_bath():
    a = hx("e6f2ec")
    b = shade(BATH, -1)
    s = Spr(16, 16, a)
    for y in range(16):
        for x in range(16):
            if ((x // 4) + (y // 4)) % 2:
                s.put(x, y, b)
            if x % 4 == 3 or y % 4 == 3:
                s.put(x, y, shade(b, -0.6) if ((x // 4) + (y // 4)) % 2 else shade(a, -0.6))
    return s


def floor_hall():
    s = Spr(16, 16, LINO_A)
    for y in range(16):
        for x in range(16):
            dark = ((x // 8) + (y // 8)) % 2 == 1
            c = LINO_B if dark else LINO_A
            if x % 8 == 0 or y % 8 == 0:
                c = shade(c, 0.25)
            elif x % 8 == 7 or y % 8 == 7:
                c = shade(c, -0.25)
            s.put(x, y, c)
    for (x, y) in ((3, 5), (12, 10), (5, 13), (10, 2)):
        s.put(x, y, shade(s.get(x, y), -0.4))
    return s


def floor_staff():
    s = Spr(16, 16, WOOD)
    for y in range(16):
        row = y // 4
        for x in range(16):
            c = WOOD if row % 2 == 0 else shade(WOOD, -0.35)
            if y % 4 == 0:
                c = shade(WOOD, 0.5)
            if y % 4 == 3:
                c = shade(WOOD, -1)
            s.put(x, y, c)
    for row, jx in enumerate((5, 13, 1, 9)):
        s.vline(jx, row * 4 + 1, row * 4 + 3, shade(WOOD, -1))
    for (x, y) in ((9, 1), (10, 1), (2, 6), (3, 6), (12, 9), (5, 14), (6, 14)):
        s.put(x, y, shade(WOOD, -0.6))
    return s


def trim():
    s = Spr(16, 6, WOOD)
    base = shade(WOOD, -0.6)
    s.rect(0, 0, 15, 5, base)
    s.hline(0, 15, 0, INK)
    s.hline(0, 15, 1, shade(WOOD, 0.6))
    s.hline(0, 15, 4, shade(base, -1))
    s.hline(0, 15, 5, INK)
    return s


def pillar():
    c = hx("8c6a4c")
    s = Spr(12, 16, c)
    s.vline(0, 0, 15, INK)
    s.vline(11, 0, 15, INK)
    s.vline(1, 0, 15, shade(c, 0.7))
    s.vline(2, 0, 15, shade(c, 0.3))
    s.vline(9, 0, 15, shade(c, -0.7))
    s.vline(10, 0, 15, shade(c, -1.2))
    s.vline(5, 0, 15, shade(c, -0.4))
    s.vline(6, 0, 15, shade(c, 0.3))
    return s


def ceiling():
    s = Spr(16, 8, CEIL)
    s.hline(0, 15, 0, shade(CEIL, -0.8))
    s.hline(0, 15, 5, shade(CEIL, 0.6))
    s.hline(0, 15, 6, shade(CEIL, -1))
    s.hline(0, 15, 7, INK)
    s.put(7, 2, shade(CEIL, -0.8))
    s.put(8, 2, shade(CEIL, 0.5))
    s.put(15, 3, shade(CEIL, -0.8))
    s.put(0, 3, shade(CEIL, 0.5))
    return s


def build_all():
    return {"wall_bath": wall_bath(), "wall_corridor": wall_corridor(), "wall_hall": wall_hall(),
            "wall_reception": wall_reception(), "wall_staff": wall_staff(), "floor_bath": floor_bath(),
            "floor_hall": floor_hall(), "floor_staff": floor_staff(), "trim": trim(), "pillar": pillar(),
            "ceiling": ceiling()}


def previews(out, prev):
    tiled = []
    for name in SIZES:
        t = out[name].img
        nx = 1 if name == "pillar" else 4
        ny = 1 if name in ("trim", "ceiling") else 4
        big = Image.new("RGBA", (t.size[0] * nx, t.size[1] * ny))
        for j in range(ny):
            for i in range(nx):
                big.paste(t, (i * t.size[0], j * t.size[1]))
        tiled.append(big)
    sheet(tiled, os.path.join(prev, "tiles.png"), cols=4, scale=4)
