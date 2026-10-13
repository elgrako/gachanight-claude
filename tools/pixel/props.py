"""Room props in the raised oblique view: every object shows its front AND its top.

Rubber-hose / Showa toy-shop look: bold ink outline, flat colour + one shadow +
one highlight. Floor-standing props touch the bottom row of their canvas.
"""
import math
import os

from pixlib import FONT, TINY, hx, mix, ell, box, poly, path, clip, shift, sheet
from tiles import (Cv, rim, INK, WHITE, RED, ORANGE, MUSTARD, CREAM, NAVY, BLUE, SKY, GREEN, STEEL, DSTEEL,
                   PINK, PORC, WOOD, CARD, LOCK)

SIZES = {
    "toilet": (30, 40), "sink": (30, 50),
    "power_switch_off": (20, 28), "power_switch_on": (20, 28),
    "lamp_off": (30, 34), "lamp_on": (30, 34),
    "sofa": (80, 46), "counter": (100, 50),
    "computer_off": (30, 30), "computer_on": (30, 30),
    "door_closed": (58, 88), "door_open": (58, 88),
    "shelf_a": (58, 84), "shelf_b": (58, 84),
    "locker": (30, 74), "table": (46, 32),
    "poster_a": (28, 36), "poster_b": (28, 36), "poster_c": (28, 36), "poster_d": (28, 36),
    "sign_gacha": (110, 28), "key": (14, 10),
    "gallery_shelf": (34, 12), "rug": (96, 34), "crate": (28, 30),
}

# Facts the game needs (also printed by build_environment.py).
COMPUTER_SCREEN = (6, 7, 18, 12)        # x, y, w, h (same in computer_off / computer_on)
COMPUTER_LED = (23, 20)                 # power led pixel, the only other on/off difference
DOOR_OPENING =(5, 14, 48, 71)          # x, y, w, h of the glass / doorway inside the frame
DOOR_PASSAGE = (14, 14, 30, 71)         # clear walk-through part when open (leaves slid aside)
LAMP_LIGHT = (15, 28)                   # centre of the bulb
FOOTPRINT_DEPTH = {"table": 12, "crate": 8, "rug": 34, "sofa": 20, "counter": 12,
                   "toilet": 18, "sink": 10, "locker": 5, "shelf_a": 6, "shelf_b": 6}

KANA = {
    "ga": ["0010101", "0010000", "1111110", "0010010", "0010010", "0100010", "1001100"],
    "chi": ["0000110", "0111000", "0001000", "1111111", "0001000", "0001000", "0110000"],
    "ya": ["0000000", "0010000", "0011110", "1110010", "0010100", "0010000", "0001000"],
}
GACHA = ("ga", "chi", "ya")


def kana_row(s, x, y, c, scale=1, gap=1, shadow=None):
    for i, k in enumerate(GACHA):
        gx = x + i * (7 * scale + gap)
        if shadow is not None:
            s.stamp(KANA[k], gx + 1, y + 1, shadow, scale)
        s.stamp(KANA[k], gx, y, c, scale)


def kana_col(s, x, y, c, gap=1, shadow=None):
    for i, k in enumerate(GACHA):
        if shadow is not None:
            s.stamp(KANA[k], x + 1, y + i * (7 + gap) + 1, shadow)
        s.stamp(KANA[k], x, y + i * (7 + gap), c)


def pie_eye(s, x, y, w=3, h=5, look=1, closed=False):
    """Tall-oval eye whose white interior has its top-left at (x, y)."""
    if closed:
        s.hline(x, x + w - 1, y + h // 2 + 1, INK)
        s.put(x - 1, y + h // 2, INK)
        s.put(x + w, y + h // 2, INK)
        return
    m = box(x, y, x + w - 1, y + h - 1, r=1 if w >= 3 else 0)
    s.ol(m)
    s.puts(m, WHITE)
    px = x + w - 1 if look > 0 else x
    s.rect(px, y + 1, px, y + h - 1 if w < 3 else y + h - 2, INK)


def starburst(cx, cy, r_out, r_in, n, rot=0.0, squash=1.0):
    pts = []
    for i in range(n * 2):
        a = rot + math.pi * i / n
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r * squash))
    return poly(pts)


def sunburst(s, m, cx, cy, n, ca, cb, rot=0.0):
    for (x, y) in m:
        a = math.atan2(y + 0.5 - cy, x + 0.5 - cx) + rot
        k = int(math.floor(a / (math.pi / n)))
        s.put(x, y, ca if k % 2 else cb)


# ---------------------------------------------------------------- bathroom

def toilet():
    s = Cv(30, 40)
    # tank at the back: lid top + front
    s.block(5, 0, 24, 20, 4, PORC, r=1)
    s.hline(6, 23, 5, PORC[1])
    # flush lever, maker sticker, glaze streak
    s.shape(box(8, 8, 11, 9), STEEL, sh=0)
    s.put(8, 8, STEEL[2])
    s.put(12, 9, STEEL[1])
    s.rect(15, 9, 18, 12, BLUE[0])
    s.hline(16, 17, 10, WHITE)
    s.put(16, 11, SKY[0])
    s.vline(21, 8, 15, PORC[2])
    s.hline(7, 9, 17, PORC[1])
    # spare paper roll lying on the lid
    roll = box(14, 1, 21, 3, r=1)
    s.shape(roll, CREAM, sh=1)
    s.hline(15, 20, 1, CREAM[2])
    s.vline(15, 1, 2, CREAM[1])
    s.put(14, 1, DSTEEL[0])
    s.put(14, 2, DSTEEL[0])
    # bowl body and foot
    body = poly([(4, 25), (26, 25), (23, 36), (7, 36)])
    s.shape(body, PORC, sh=2)
    s.shape(box(8, 35, 21, 38, r=1), PORC, sh=1)
    s.put(10, 37, STEEL[0])
    s.put(19, 37, STEEL[0])
    # seat ring + closed lid in a fluffy pink cover, seen from above
    seat = ell(15, 24.5, 12.5, 6.5)
    s.shape(seat, PORC, sh=1)
    s.rect(13, 18, 16, 18, STEEL[0])
    lid = ell(15, 24, 9.5, 4.3)
    s.shape(lid, PINK, sh=1)
    s.pts([(9, 23), (11, 21), (19, 21), (21, 23), (11, 26), (19, 26)], PINK[2])
    s.pts([(15, 22), (14, 23), (16, 23), (15, 24)], WHITE)
    s.put(15, 23, MUSTARD[0])
    return s


def sink():
    s = Cv(30, 50)
    # round mirror on the wall
    s.shape(ell(15, 11, 11, 11), MUSTARD, sh=1, hi=1)
    glass = ell(15, 11, 8, 8)
    s.shape(glass, SKY, sh=0)
    s.puts(glass & poly([(15, 19), (24, 9), (24, 20)]), SKY[1])
    for i in range(6):
        s.put(10 + i, 12 - i, WHITE)
    for i in range(4):
        s.put(13 + i, 13 - i, WHITE)
    s.put(19, 15, WHITE)
    # hanger knob of the mirror
    s.put(15, 0, STEEL[0])
    # basin: top surface + front, pedestal
    s.shape(box(11, 42, 18, 48, r=0), PORC, sh=1)
    front = poly([(2, 33), (28, 33), (28, 39), (23, 44), (7, 44), (2, 39)])
    top = box(2, 28, 27, 37, r=2)
    s.shape(front | top, PORC, sh=2)
    s.puts(top, PORC[2])
    s.hline(3, 26, 38, PORC[1])
    s.hline(7, 22, 41, SKY[0])
    bowl = ell(15, 33.5, 9.5, 3.4)
    s.shape(bowl, SKY, sh=0)
    s.puts(rim(bowl, 0, -1, 1), SKY[1])
    s.put(15, 34, INK)
    s.hline(11, 13, 35, WHITE)
    # faucet and taps on the back edge
    s.shape(box(14, 24, 15, 29), STEEL, sh=0)
    s.shape(box(13, 24, 16, 25), STEEL, sh=0)
    s.put(13, 24, STEEL[2])
    s.shape(box(7, 28, 9, 29), RED, sh=0)
    s.shape(box(20, 28, 22, 29), BLUE, sh=0)
    # a bar of soap on the corner
    s.rect(3, 35, 5, 36, PINK[0])
    s.put(3, 35, PINK[2])
    s.put(5, 36, PINK[1])
    return s


# ---------------------------------------------------------------- power switch

def power_switch(on):
    s = Cv(20, 28)
    s.block(1, 0, 18, 27, 2, STEEL, r=1)
    # pilot lamp
    lamp = box(8, 4, 11, 5, r=0)
    s.shape(lamp, GREEN if on else (hx("27503a"), hx("1a3a2a"), hx("27503a")), sh=0)
    if on:
        s.put(8, 4, WHITE)
        s.hline(9, 11, 5, GREEN[2])
    # two wide-set rubber-hose pie eyes
    for x0 in (3, 13):
        if on:
            m = box(x0, 8, x0 + 3, 13, r=1)
            s.ol(m)
            s.puts(m, WHITE)
            s.rect(x0 + 2, 9, x0 + 3, 12, INK)
            s.put(x0 + 3, 9, WHITE)
        else:
            s.hline(x0, x0 + 3, 11, INK)
            s.put(x0 - 1, 10, INK)
            s.put(x0 + 4, 10, INK)
            s.hline(x0, x0 + 3, 12, STEEL[2])
    # lever slot
    s.rect(7, 16, 12, 25, INK)
    s.rect(8, 17, 11, 24, DSTEEL[1])
    s.rect(9, 19, 10, 22, STEEL[2])
    knob = box(6, 16, 13, 19, r=1) if on else box(6, 22, 13, 25, r=1)
    s.shape(knob, RED, sh=1)
    ky = min(q[1] for q in knob)
    s.hline(8, 10, ky, RED[2])
    # position marks and screws
    s.put(15, 17, GREEN[0] if on else DSTEEL[0])
    s.put(15, 24, DSTEEL[0] if on else RED[0])
    for (x, y) in ((3, 3), (16, 3), (3, 24), (16, 25)):
        s.put(x, y, DSTEEL[0])
    return s


# ---------------------------------------------------------------- pendant lamp

def lamp(on):
    s = Cv(30, 34)
    s.rect(14, 0, 15, 9, INK)
    # bulb pokes out below the shade
    bulb = ell(15, 27.5, 4.5, 4.5)
    bp = (hx("fff3a8"), MUSTARD[0], WHITE) if on else (hx("9aa3b5"), DSTEEL[0], STEEL[2])
    s.shape(bulb, bp, sh=1)
    s.put(13, 28, bp[2])
    s.put(13, 29, bp[2])
    if on:
        for (x0, y0, x1, y1) in ((15, 33, 15, 33), (14, 33, 14, 33), (8, 30, 7, 31), (21, 30, 22, 31)):
            s.puts(path([(x0, y0), (x1, y1)]), MUSTARD[0])
    # enamel shade seen from slightly above: cone + front arc of the rim
    cone = poly([(11, 12), (19, 12), (28, 23), (2, 23)])
    lip = clip(ell(15, 23, 13.5, 3.6), y0=23)
    shade_m = cone | lip
    s.shape(shade_m, GREEN, sh=0)
    s.puts(shade_m & poly([(18, 12), (20, 12), (29, 23), (29, 28), (22, 28)]), GREEN[1])
    s.puts(shade_m & poly([(11, 14), (13, 14), (8, 23), (5, 23)]), GREEN[2])
    s.puts(rim(lip, 0, 1, 1) | shift(rim(lip, 0, 1, 1), 0, -1) & shade_m, CREAM[0])
    s.shape(box(12, 9, 17, 11, r=0), DSTEEL, sh=1)
    s.hline(12, 14, 9, DSTEEL[2])
    return s


# ---------------------------------------------------------------- staff room

def sofa():
    s = Cv(80, 46)
    P = GREEN
    # wooden feet
    for x in (3, 72):
        s.shape(box(x, 41, x + 4, 44), WOOD, sh=1)
    # backrest: top + front
    s.block(6, 0, 73, 26, 4, P, r=2)
    s.hline(8, 71, 5, P[0])
    for x in (20, 33, 46, 59):
        s.put(x, 12, P[1])
        s.put(x, 13, INK)
    # seat: cushion tops + front
    s.block(9, 19, 70, 42, 12, P)
    s.vline(39, 20, 41, INK)
    s.vline(40, 20, 41, INK)
    for (a, b) in ((10, 38), (41, 69)):
        s.hline(a, b, 31, P[0])
        s.hline(a + 1, b - 1, 21, WHITE)
        s.hline(a + 1, b - 1, 21, mix(P[2], WHITE, 0.55))
        s.vline(b, 33, 41, P[1])
    s.hline(10, 38, 33, P[0])
    # worn, flattened spots where people sit
    s.hline(18, 27, 26, P[0])
    s.hline(20, 25, 27, P[0])
    s.hline(49, 58, 25, P[0])
    # mustard patch with stitches
    s.rect(56, 34, 62, 39, MUSTARD[0])
    s.frame(56, 34, 62, 39, MUSTARD[1])
    for (x, y) in ((55, 35), (63, 37), (58, 33), (60, 40)):
        s.put(x, y, INK)
    # lace antimacassar over the backrest
    s.rect(31, 1, 48, 9, CREAM[2])
    for x in range(31, 49, 3):
        s.put(x + 1, 10, CREAM[2])
        s.put(x, 9, CREAM[1])
    s.vline(30, 1, 9, INK)
    s.vline(49, 1, 9, INK)
    for (x, y) in ((34, 3), (39, 5), (44, 3), (36, 7), (42, 7)):
        s.pts([(x, y), (x + 1, y + 1), (x - 1, y + 1), (x, y + 2)], CREAM[1])
    s.rect(31, 4, 48, 4, CREAM[2])
    s.rect(24, 36, 28, 39, PINK[0])
    s.frame(24, 36, 28, 39, PINK[1])
    s.put(26, 37, WHITE)
    # arms: rounded tops + fronts
    for x in (0, 69):
        s.block(x, 13, x + 10, 43, 6, P, r=2)
        s.hline(x + 2, x + 8, 20, P[0])
        s.hline(x + 2, x + 6, 15, mix(P[2], WHITE, 0.55))
    # striped throw pillow
    pm = ell(20, 19.5, 7.5, 6)
    s.shape(pm, CREAM, sh=2)
    for y in (17, 20):
        s.puts(pm & box(13, y, 27, y), RED[0])
    return s


def counter():
    s = Cv(100, 50)
    s.block(0, 0, 99, 49, 11, WOOD)
    s.hline(1, 98, 11, mix(WOOD[2], WOOD[0], 0.5))
    s.hline(1, 98, 14, INK)
    # glossy streaks on the top
    s.hline(6, 30, 3, CREAM[2])
    s.hline(34, 38, 3, CREAM[2])
    # front panel
    s.rect(1, 15, 98, 44, RED[0])
    s.hline(1, 98, 15, RED[2])
    s.hline(1, 98, 44, RED[1])
    s.vline(98, 15, 44, RED[1])
    s.hline(1, 98, 45, INK)
    s.rect(1, 46, 98, 48, DSTEEL[0])
    s.hline(1, 98, 48, DSTEEL[1])
    # cream band with kana and diamonds
    s.hline(1, 98, 23, INK)
    s.hline(1, 98, 35, INK)
    s.rect(1, 24, 98, 34, CREAM[0])
    s.hline(1, 98, 34, CREAM[1])
    kana_row(s, 38, 26, RED[0])
    for cx in (8, 19, 30, 69, 80, 91):
        for d in range(-2, 3):
            s.hline(cx - (2 - abs(d)), cx + (2 - abs(d)), 29 + d, NAVY[0])
    # a taped price card, scuffs on the kick plate, a chipped corner
    s.rect(5, 37, 22, 43, INK)
    s.rect(6, 38, 21, 42, CREAM[2])
    coin = ell(9, 40.5, 2.1, 2.1)
    s.puts(coin, MUSTARD[0])
    s.puts(rim(coin, 1, 0, 1) | rim(coin, 0, 1, 1), MUSTARD[1])
    s.put(8, 39, MUSTARD[2])
    s.rect(13, 39, 19, 40, RED[0])
    s.hline(13, 17, 42, DSTEEL[0])
    s.rect(12, 36, 15, 37, MUSTARD[2])
    s.pts([(30, 47), (31, 47), (32, 46), (60, 47), (61, 46), (62, 47), (88, 47)], STEEL[0])
    s.pts([(2, 12), (3, 12), (2, 13), (70, 12), (71, 12)], WOOD[1])
    s.hline(44, 58, 6, mix(WOOD[2], WOOD[0], 0.5))
    s.hline(48, 62, 8, mix(WOOD[2], WOOD[0], 0.5))
    # desk bell
    s.shape(clip(ell(86, 8, 4, 4), y1=7), MUSTARD, sh=1)
    s.shape(box(82, 8, 89, 8), DSTEEL, sh=0)
    s.put(84, 5, WHITE)
    s.shape(box(85, 2, 86, 2), DSTEEL, sh=0)
    return s


SCREEN_BG = hx("164a2c")
PHOS = hx("9ff59a")


def computer(on):
    s = Cv(30, 30)
    # keyboard slab seen from above
    kb = poly([(2, 23), (28, 23), (30, 29), (0, 29)])
    s.shape(kb, CREAM, sh=1)
    for y in (25, 27):
        for x in range(4 if y == 25 else 3, 27, 2):
            s.put(x, y, DSTEEL[0])
    # chunky CRT body: top + front
    s.block(2, 0, 27, 22, 3, CREAM, r=1)
    s.hline(3, 26, 4, CREAM[0])
    sx, sy, sw, sh = COMPUTER_SCREEN
    s.rect(sx - 1, sy - 1, sx + sw, sy + sh, INK)
    s.put(sx - 1, sy - 1, CREAM[1])
    s.put(sx + sw, sy - 1, CREAM[1])
    s.put(sx - 1, sy + sh, CREAM[1])
    s.put(sx + sw, sy + sh, CREAM[1])
    # vents and power led under the screen
    for x in (5, 7, 9):
        s.put(x, 20, CREAM[1])
    s.put(23, 20, GREEN[2] if on else DSTEEL[0])
    if on:
        s.rect(sx, sy, sx + sw - 1, sy + sh - 1, SCREEN_BG)
        for y in range(sy + 1, sy + sh, 2):
            s.hline(sx, sx + sw - 1, y, hx("1c5a36"))
        # rubber-hose salesman: round head, pie eyes, grin, bow tie
        head = ell(sx + 9, sy + 5, 5, 4.6)
        s.puts(head, PHOS)
        s.rect(sx + 7, sy + 3, sx + 7, sy + 5, INK)
        s.rect(sx + 10, sy + 3, sx + 10, sy + 5, INK)
        s.put(sx + 6, sy + 3, WHITE)
        s.put(sx + 6, sy + 4, WHITE)
        s.put(sx + 9, sy + 3, WHITE)
        s.put(sx + 9, sy + 4, WHITE)
        s.pts([(sx + 6, sy + 7), (sx + 7, sy + 8), (sx + 8, sy + 8), (sx + 9, sy + 8), (sx + 10, sy + 8),
               (sx + 11, sy + 7)], INK)
        s.pts([(sx + 6, sy + 10), (sx + 6, sy + 11), (sx + 7, sy + 11), (sx + 10, sy + 11), (sx + 11, sy + 11),
               (sx + 11, sy + 10), (sx + 7, sy + 10), (sx + 10, sy + 10)], PHOS)
        s.rect(sx + 8, sy + 10, sx + 9, sy + 11, WHITE)
        # hat brim and a little sparkle
        s.hline(sx + 4, sx + 13, sy + 1, WHITE)
        s.rect(sx + 6, sy, sx + 11, sy, PHOS)
        s.pts([(sx + 15, sy + 3), (sx + 14, sy + 4), (sx + 15, sy + 4), (sx + 16, sy + 4), (sx + 15, sy + 5),
               (sx + 2, sy + 8)], PHOS)
    else:
        s.rect(sx, sy, sx + sw - 1, sy + sh - 1, hx("1f2a36"))
        for i in range(5):
            s.put(sx + 2 + i, sy + 6 - i, DSTEEL[0])
        for i in range(3):
            s.put(sx + 5 + i, sy + 7 - i, DSTEEL[0])
    return s


def locker():
    s = Cv(30, 74)
    for x in (3, 22):
        s.shape(box(x, 70, x + 4, 72), DSTEEL, sh=1)
    s.block(1, 0, 28, 70, 3, LOCK, r=1)
    s.hline(2, 27, 4, LOCK[0])
    # a board-game box left on top
    s.rect(17, 1, 25, 3, MUSTARD[0])
    s.hline(17, 25, 3, MUSTARD[1])
    s.hline(18, 21, 1, MUSTARD[2])
    s.vline(16, 1, 3, INK)
    s.vline(26, 1, 3, INK)
    s.rect(14, 5, 15, 69, INK)
    for k, x0 in enumerate((2, 16)):
        s.vline(x0, 5, 68, LOCK[2])
        s.vline(x0 + 11, 5, 68, LOCK[1])
        for y in (8, 10, 12, 62, 64):
            s.hline(x0 + 3, x0 + 8, y, INK)
            s.hline(x0 + 3, x0 + 8, y + 1, LOCK[2])
        # name plate with a scribbled name
        s.rect(x0 + 2, 16, x0 + 9, 21, INK)
        s.rect(x0 + 3, 17, x0 + 8, 20, CREAM[2])
        if k == 0:
            s.pts([(x0 + 4, 18), (x0 + 5, 19), (x0 + 6, 18), (x0 + 7, 19)], NAVY[0])
        else:
            s.hline(x0 + 4, x0 + 7, 18, RED[0])
            s.hline(x0 + 4, x0 + 6, 19, NAVY[0])
    # handles next to the middle, a padlock on the right door
    s.shape(box(11, 36, 12, 40), STEEL, sh=0)
    s.put(11, 36, STEEL[2])
    s.shape(box(17, 36, 18, 40), STEEL, sh=0)
    s.put(17, 36, STEEL[2])
    s.pts([(18, 42), (20, 42), (18, 43), (20, 43)], STEEL[1])
    s.put(19, 42, STEEL[2])
    s.shape(box(18, 44, 20, 46), MUSTARD, sh=0)
    s.put(19, 45, INK)
    # left door: star and capsule stickers, a taped note
    st = starburst(7.5, 28.5, 3.8, 1.7, 5, rot=-math.pi / 2)
    s.puts(st, MUSTARD[0])
    s.put(7, 28, MUSTARD[2])
    cap = ell(6.5, 45.5, 2.6, 2.6)
    s.shape(cap, CREAM, sh=0)
    s.puts(clip(cap, y1=44), RED[0])
    s.put(5, 44, WHITE)
    s.rect(4, 50, 10, 57, CREAM[2])
    s.vline(10, 50, 57, CREAM[1])
    s.hline(4, 10, 57, CREAM[1])
    s.rect(6, 49, 8, 50, MUSTARD[2])
    for y in (52, 54):
        s.hline(5, 8, y, DSTEEL[0])
    s.put(9, 55, RED[0])
    s.put(8, 55, RED[0])
    # right door: smiley, kana sticker
    face = ell(22, 28, 3.5, 3.5)
    s.shape(face, PINK, sh=0)
    s.put(20, 27, INK)
    s.put(23, 27, INK)
    s.pts([(20, 29), (21, 30), (22, 30), (23, 29)], INK)
    s.rect(17, 49, 26, 58, INK)
    s.rect(18, 50, 25, 57, CREAM[0])
    s.stamp(KANA["ga"], 18, 50, RED[0])
    # wear: scratches, a dent, rust near the floor
    s.pts([(5, 33), (6, 34), (7, 34), (8, 35)], LOCK[1])
    s.pts([(22, 34), (23, 35), (24, 35)], LOCK[2])
    s.pts([(24, 42), (25, 43), (25, 44)], LOCK[1])
    s.pts([(3, 68), (4, 68), (4, 67), (25, 68), (26, 68), (26, 67), (9, 68)], ORANGE[1])
    return s


def table():
    s = Cv(46, 32)
    dark = (WOOD[1], hx("5a3418"), WOOD[0])
    for x in (13, 30):
        s.shape(box(x, 20, x + 2, 26), dark, sh=1)
    for x in (7, 35):
        s.shape(box(x, 18, x + 3, 30), WOOD, sh=1)
        s.vline(x, 21, 29, WOOD[2])
    top = ell(23, 9.5, 22, 9)
    side = shift(top, 0, 4)
    s.shape(top | side, WOOD, sh=0)
    # side of the slab: mid wood with a dark groove under the top and a shadow at the bottom
    s.puts(side - top, WOOD[0])
    s.puts(rim(side, 0, 1, 1) - top, WOOD[1])
    s.puts(shift(rim(top, 0, 1, 1), 0, 1) - top, hx("5a3418"))
    # top surface: light, with a catch-light along its near edge
    s.puts(top, WOOD[2])
    s.puts(rim(top, 0, 1, 1), hx("f2c98a"))
    grain = mix(WOOD[2], WOOD[0], 0.55)
    ring = ell(23, 9.5, 15, 5.4)
    s.puts((rim(ring, 0, 1, 1) | rim(ring, 1, 0, 1) | rim(ring, -1, 0, 1) | rim(ring, 0, -1, 1)) - box(18, 0, 30, 5),
           grain)
    ring2 = ell(22, 9.5, 7, 2.4)
    s.puts(rim(ring2, 0, 1, 1) | rim(ring2, -1, 0, 1), grain)
    s.hline(9, 17, 5, CREAM[2])
    s.hline(7, 9, 6, CREAM[2])
    # a mug ring and a forgotten capsule sticker
    stain = ell(35, 11, 3, 1.5)
    s.puts(rim(stain, 0, 1, 1) | rim(stain, 0, -1, 1), WOOD[0])
    s.rect(9, 11, 11, 12, RED[0])
    s.put(9, 11, RED[2])
    return s


# ---------------------------------------------------------------- door

def _night(s, x0, y0, x1, y1):
    s.rect(x0, y0, x1, y1, NAVY[1])
    for (x, y) in ((9, 20), (17, 27), (24, 18), (33, 22), (46, 40), (12, 38), (29, 34), (48, 19), (21, 45)):
        s.put(x, y, CREAM[0])
    s.pts([(36, 44), (35, 45), (36, 45), (37, 45), (36, 46)], CREAM[0])
    moon = ell(42, 28, 5.2, 5.2)
    s.puts(moon, CREAM[0])
    s.puts(moon & ell(44.5, 26.5, 4.2, 4.2), NAVY[1])
    # skyline
    for (x, w, h) in ((6, 7, 14), (13, 5, 22), (18, 8, 10), (26, 6, 18), (32, 9, 12), (41, 5, 24), (46, 7, 15)):
        s.rect(x, 74 - h, x + w - 1, 74, NAVY[0])
        for wy in range(74 - h + 2, 73, 4):
            for wx in range(x + 1, x + w - 1, 3):
                if (wx + wy) % 5 != 0:
                    s.put(wx, wy, MUSTARD[0])
    s.vline(15, 48, 52, NAVY[0])


def _day(s, x0, y0, x1, y1):
    s.rect(x0, y0, x1, y1, SKY[0])
    sun = ell(37, 30, 6, 6)
    sunburst(s, ell(37, 30, 13, 13) & box(x0, y0, x1, 60), 37, 30, 8, SKY[2], SKY[0])
    s.puts(sun, hx("fff3a8"))
    s.puts(rim(sun, -1, 0, 1) | rim(sun, 0, -1, 1), WHITE)
    for (cx, cy, w) in ((18, 24, 9), (30, 44, 7)):
        s.puts(ell(cx, cy, w / 2.0, 2) | ell(cx + 3, cy - 1.5, 3, 2.2), WHITE)
    for (x, w, h) in ((14, 6, 12), (20, 7, 18), (27, 5, 9), (32, 6, 15), (38, 7, 11)):
        s.rect(x, 62 - h, x + w - 1, 62, SKY[1])
        for wy in range(62 - h + 2, 61, 4):
            for wx in range(x + 1, x + w - 1, 2):
                s.put(wx, wy, SKY[2])
    s.rect(x0, 63, x1, y1, CREAM[0])
    s.hline(x0, x1, 63, CREAM[1])
    for i in range(4):
        s.rect(18 + i * 6, 70 + i * 0, 21 + i * 6, 71, CREAM[2])
        s.rect(17 + i * 6, 76, 21 + i * 6, 78, CREAM[2])
    bush = ell(41, 62, 4, 3.5) | ell(45, 63, 3, 2.5)
    s.puts(clip(bush, y1=63), GREEN[0])
    s.puts(clip(rim(bush, 0, -1, 1), y1=63), GREEN[2])


def _leaf(s, a, b, y0, y1, streak):
    """Sliding glass leaf frame over whatever is already drawn in x a..b."""
    s.rect(a, y0, a + 1, y1, STEEL[0])
    s.rect(b - 1, y0, b, y1, STEEL[0])
    s.rect(a, y0, b, y0 + 1, STEEL[0])
    s.vline(a, y0, y1, STEEL[2])
    s.vline(b, y0, y1, STEEL[1])
    s.hline(a + 2, b - 2, y0 + 2, INK)
    s.vline(a + 2, y0 + 2, y1 - 9, INK)
    s.vline(b - 2, y0 + 2, y1 - 9, INK)
    s.hline(a + 2, b - 2, y1 - 9, INK)
    s.rect(a + 2, y1 - 8, b - 2, y1, STEEL[0])
    s.hline(a + 2, b - 2, y1 - 8, STEEL[2])
    s.hline(a, b, y1, STEEL[1])
    if b - a > 12:
        for i in range(7):
            s.put(a + 5 + i, y0 + 14 - i, streak)
        for i in range(4):
            s.put(a + 9 + i, y0 + 16 - i, streak)


def door(opened):
    s = Cv(58, 88)
    ox, oy, ow, oh = DOOR_OPENING
    x1, y1 = ox + ow - 1, oy + oh - 1
    # frame posts and threshold
    s.rect(0, 6, 57, 87, INK)
    for a in (1, 54):
        s.rect(a, 7, a + 2, 86, WOOD[0])
        s.vline(a, 7, 86, WOOD[2])
        s.vline(a + 2, 7, 86, WOOD[1])
    s.rect(5, 86, 52, 86, STEEL[0])
    s.rect(ox, 7, x1, y1, NAVY[1])
    if opened:
        _day(s, ox, 7, x1, y1)
        px, _, pw, _ = DOOR_PASSAGE
        _leaf(s, ox, px - 2, 7, y1, WHITE)
        s.vline(px - 1, 7, y1, INK)
        _leaf(s, px + pw + 1, x1, 7, y1, WHITE)
        s.vline(px + pw, 7, y1, INK)
        # light spilling on the threshold
        s.rect(px, 86, px + pw - 1, 86, CREAM[2])
    else:
        _night(s, ox, 7, x1, y1)
        _leaf(s, ox, 27, 7, y1, BLUE[0])
        _leaf(s, 30, x1, 7, y1, BLUE[0])
        s.rect(28, 7, 29, y1, INK)
        for a in (23, 33):
            s.shape(box(a, 46, a + 1, 57), STEEL, sh=0)
            s.vline(a, 46, 57, STEEL[2])
        # "closed" tag hanging on the glass
        s.shape(box(9, 58, 19, 63), CREAM, sh=1)
        s.hline(11, 17, 60, RED[0])
        s.hline(11, 17, 61, RED[0])
        s.put(14, 56, INK)
    # striped awning with scallops, seen from above-front
    aw = set()
    for k in range(7):
        a = 1 + k * 8
        m = box(a, 1, a + 7, 9) | clip(ell(a + 4, 9.5, 4, 3.6), y0=9)
        aw |= m
    s.ol(aw)
    for k in range(7):
        a = 1 + k * 8
        m = box(a, 1, a + 7, 9) | clip(ell(a + 4, 9.5, 4, 3.6), y0=9)
        p = RED if k % 2 == 0 else CREAM
        s.puts(m, p[0])
        s.puts(clip(m, y1=3), p[2])
        s.puts(rim(m, 0, 1, 1) & clip(m, y0=9), p[1])
    return s


# ---------------------------------------------------------------- shelves and toys

TEAL = (hx("2aa7a0"), hx("1b7774"), hx("7fdccf"))
PURPLE = (hx("8a63c9"), hx("5e3f96"), hx("b79be6"))


def toy_box(s, x, yb, w, h, p, motif="dot"):
    s.block(x, yb - h, x + w - 1, yb + 1, 2, p)
    cx = x + w // 2
    cy = yb - (h - 3) // 2
    if motif == "dot":
        s.puts(ell(cx, cy + 0.5, min(w, h) / 2.0 - 2.2, min(w, h) / 2.0 - 2.6), CREAM[0])
    elif motif == "stripe":
        s.rect(x + 1, cy - 1, x + w - 2, cy, CREAM[0])
    elif motif == "star":
        s.puts(starburst(cx, cy + 0.5, 3.2, 1.4, 5, rot=-math.pi / 2), MUSTARD[2])
    elif motif == "face":
        s.rect(cx - 2, cy - 1, cx - 2, cy, INK)
        s.rect(cx + 1, cy - 1, cx + 1, cy, INK)
        s.put(cx - 3, cy - 1, WHITE)
        s.put(cx, cy - 1, WHITE)
        s.hline(cx - 2, cx + 1, cy + 2, WHITE)
    elif motif == "window":
        s.rect(x + 2, cy - 2, x + w - 3, cy + 1, INK)
        s.rect(x + 3, cy - 1, x + w - 4, cy, SKY[0])
        s.put(x + 3, cy - 1, WHITE)
    elif motif == "capsule":
        m = ell(cx, cy + 0.5, 2.6, 2.6)
        s.puts(m, CREAM[2])
        s.puts(clip(m, y1=cy - 1), MUSTARD[2] if p is RED else RED[0])
        s.put(cx - 2, cy - 1, WHITE)


def _eyes2(s, cx, y):
    """Two tiny pie eyes (white + pupil), symmetric about cx - 0.5."""
    for x in (cx - 3, cx):
        s.rect(x, y, x, y + 1, WHITE)
        s.rect(x + 1, y, x + 1, y + 1, INK)


MINI = {"penguin": TEAL, "frog": GREEN, "bunny": PINK, "fox": ORANGE, "owl": PURPLE, "mouse": STEEL,
        "bear": BLUE, "tanuki": WOOD, "plush": MUSTARD}


def mini(s, cx, yb, kind, p=None):
    """Shelf toy echoing one of the game's figures; about 9 x 12, feet on yb."""
    p = p or MINI[kind]
    body = ell(cx, yb - 2.2, 3.6, 3.2)
    head = ell(cx, yb - 7, 4.2, 3.6)
    ears = set()
    if kind == "bunny":
        ears = box(cx - 3, yb - 13, cx - 2, yb - 10) | box(cx + 1, yb - 13, cx + 2, yb - 10)
    elif kind in ("fox", "owl"):
        ears = {(cx - 4, yb - 10), (cx - 3, yb - 10), (cx - 4, yb - 11), (cx + 3, yb - 10), (cx + 2, yb - 10),
                (cx + 3, yb - 11)}
    elif kind in ("mouse", "bear", "tanuki", "plush"):
        r = 2.1 if kind == "mouse" else 1.6
        ears = ell(cx - 3.5, yb - 10.5, r, r) | ell(cx + 2.5, yb - 10.5, r, r)
    elif kind == "frog":
        ears = ell(cx - 2.5, yb - 10.5, 1.6, 1.6) | ell(cx + 1.5, yb - 10.5, 1.6, 1.6)
    s.shape(body, p, sh=1)
    if ears:
        s.shape(ears, p, sh=0)
    s.shape(head, p, sh=1)
    if kind in ("penguin", "fox", "tanuki", "bear", "frog", "owl"):
        s.rect(cx - 1, yb - 3, cx, yb - 1, GREEN[2] if kind == "frog" else CREAM[2])
    if kind == "tanuki":
        s.rect(cx - 4, yb - 8, cx + 3, yb - 7, WOOD[1])
        s.put(cx - 1, yb - 11, GREEN[0])
        s.put(cx, yb - 11, GREEN[2])
    if kind == "frog":
        _eyes2(s, cx, yb - 11)
        s.hline(cx - 2, cx + 1, yb - 6, INK)
        s.put(cx - 3, yb - 7, PINK[0])
        s.put(cx + 2, yb - 7, PINK[0])
    else:
        _eyes2(s, cx, yb - 8)
    if kind == "penguin":
        s.rect(cx - 1, yb - 6, cx, yb - 6, ORANGE[0])
        s.rect(cx - 3, yb, cx - 2, yb, ORANGE[0])
        s.rect(cx + 1, yb, cx + 2, yb, ORANGE[0])
        s.put(cx - 1, yb - 11, TEAL[0])
        s.put(cx - 1, yb - 12, INK)
    elif kind == "fox":
        s.rect(cx - 1, yb - 6, cx, yb - 5, WHITE)
        s.put(cx - 1, yb - 6, INK)
    elif kind == "owl":
        s.rect(cx - 1, yb - 6, cx, yb - 6, MUSTARD[0])
        s.pts([(cx - 2, yb - 2), (cx + 1, yb - 2)], PURPLE[2])
    elif kind == "bunny":
        s.put(cx - 1, yb - 6, PINK[1])
        s.vline(cx - 3, yb - 12, yb - 11, PINK[2])
        s.vline(cx + 1, yb - 12, yb - 11, PINK[2])
        s.rect(cx - 1, yb - 2, cx, yb - 1, WHITE)
    elif kind == "mouse":
        s.put(cx - 4, yb - 11, PINK[0])
        s.put(cx + 2, yb - 11, PINK[0])
        s.rect(cx - 1, yb - 6, cx, yb - 6, INK)
        s.rect(cx - 1, yb - 3, cx, yb - 2, MUSTARD[0])
    elif kind in ("bear", "plush"):
        s.rect(cx - 1, yb - 6, cx, yb - 6, CREAM[2])
        s.put(cx - 1, yb - 2, CREAM[2])
        s.put(cx, yb - 2, CREAM[2])


def daruma(s, cx, yb, p=RED):
    m = ell(cx, yb - 4.5, 4.6, 5)
    s.shape(m, p, sh=1)
    s.puts(ell(cx, yb - 6, 3, 2.6), CREAM[0])
    s.put(cx - 2, yb - 7, INK)
    s.put(cx + 1, yb - 7, INK)
    s.hline(cx - 1, cx, yb - 5, INK)
    s.hline(cx - 2, cx + 1, yb - 2, MUSTARD[0] if p is RED else RED[0])


def ball(s, cx, yb, p):
    m = ell(cx, yb - 3, 3.5, 3.5)
    s.shape(m, CREAM, sh=1)
    s.puts(clip(m, y1=yb - 4), p[0])
    s.put(cx - 2, yb - 5, WHITE)


def robot(s, x, yb):
    """The TV-headed tin robot: orange head with a cream screen, blue body."""
    s.rect(x + 1, yb, x + 2, yb, RED[0])
    s.rect(x + 4, yb, x + 5, yb, RED[0])
    s.shape(box(x, yb - 5, x + 6, yb - 1), BLUE, sh=1)
    s.rect(x + 2, yb - 4, x + 4, yb - 3, MUSTARD[0])
    s.put(x + 3, yb - 3, RED[0])
    s.shape(box(x - 1, yb - 12, x + 7, yb - 7, r=1), ORANGE, sh=1)
    s.rect(x + 1, yb - 11, x + 5, yb - 8, CREAM[2])
    s.rect(x + 2, yb - 10, x + 2, yb - 9, INK)
    s.rect(x + 4, yb - 10, x + 4, yb - 9, INK)
    s.put(x + 3, yb - 14, RED[0])
    s.put(x + 3, yb - 13, INK)


def kokeshi(s, cx, yb, p):
    s.shape(box(cx - 2, yb - 5, cx + 2, yb), p, sh=1)
    s.hline(cx - 2, cx + 2, yb - 3, MUSTARD[0])
    head = ell(cx + 0.5, yb - 8.5, 3.5, 3.3)
    s.shape(head, CREAM, sh=0)
    s.puts(clip(head, y1=yb - 11), INK)
    s.put(cx - 1, yb - 8, INK)
    s.put(cx + 2, yb - 8, INK)
    s.put(cx, yb - 6, RED[0])
    s.put(cx + 1, yb - 6, RED[0])


def whale(s, cx, yb):
    body = ell(cx, yb - 3, 5.6, 3.6)
    fluke = {(cx + 5, yb - 6), (cx + 6, yb - 7), (cx + 6, yb - 8), (cx + 5, yb - 8), (cx + 7, yb - 6)}
    s.shape(fluke, BLUE, sh=0)
    s.shape(body, BLUE, sh=1)
    s.puts(clip(body, y0=yb - 1), CREAM[2])
    s.rect(cx - 4, yb - 4, cx - 4, yb - 3, WHITE)
    s.rect(cx - 3, yb - 4, cx - 3, yb - 3, INK)
    s.put(cx - 5, yb - 2, PINK[0])
    s.pts([(cx - 2, yb - 8), (cx, yb - 8), (cx + 2, yb - 8)], MUSTARD[0])
    s.hline(cx - 2, cx + 2, yb - 7, MUSTARD[0])
    s.hline(cx - 3, cx + 3, yb - 6, INK)
    s.hline(cx - 2, cx + 2, yb - 7, MUSTARD[0])


def jelly(s, cx, yb):
    dome = clip(ell(cx, yb - 7, 4.4, 4.2), y1=yb - 6)
    for k, x in enumerate((cx - 3, cx - 1, cx + 1)):
        s.shape(box(x, yb - 5, x, yb - (0 if k != 1 else 1)), PINK, sh=0)
    s.shape(dome, SKY, sh=1)
    s.put(cx - 3, yb - 10, WHITE)
    _eyes2(s, cx, yb - 8)


def shelf(rows):
    s = Cv(58, 84)
    back = hx("5a3418")
    s.block(0, 0, 57, 83, 4, WOOD)
    s.hline(1, 56, 5, WOOD[0])
    s.rect(3, 6, 54, 78, INK)
    s.rect(4, 7, 53, 78, back)
    s.vline(1, 6, 82, WOOD[2])
    s.rect(1, 79, 56, 82, WOOD[1])
    s.hline(1, 56, 79, INK)
    # worn plinth
    s.pts([(6, 81), (7, 81), (30, 80), (31, 80), (32, 81), (49, 81)], WOOD[0])
    for k in range(4):
        y0 = 7 + k * 18
        # shadow under the board above, board top (seen from above), board edge
        s.hline(4, 53, y0, hx("3f240f"))
        s.rect(4, y0 + 12, 53, y0 + 14, WOOD[2])
        s.hline(4, 53, y0 + 12, mix(WOOD[2], WOOD[0], 0.6))
        s.rect(4, y0 + 15, 53, y0 + 16, WOOD[0])
        s.hline(4, 53, y0 + 16, WOOD[1])
        s.hline(3, 54, y0 + 17, INK)
        yb = y0 + 13
        for it in rows[k]:
            kind = it[0]
            if kind == "box":
                toy_box(s, it[1], yb, it[2], it[3], it[4], it[5])
            elif kind == "daruma":
                daruma(s, it[1], yb, it[2] if len(it) > 2 else RED)
            elif kind == "ball":
                ball(s, it[1], yb, it[2])
            elif kind == "robot":
                robot(s, it[1], yb)
            elif kind == "kokeshi":
                kokeshi(s, it[1], yb, it[2])
            elif kind == "whale":
                whale(s, it[1], yb)
            elif kind == "jelly":
                jelly(s, it[1], yb)
            else:
                mini(s, it[1], yb, kind, it[2] if len(it) > 2 else None)
        # price tags clipped to the board edge
        for j, x in enumerate((9 + (k * 5) % 7, 26 + (k * 3) % 8, 44 + (k * 4) % 6)):
            s.rect(x, y0 + 15, x + 3, y0 + 16, CREAM[2])
            s.put(x + 1 + (j + k) % 2, y0 + 15 + (j % 2), RED[0])
            s.put(x + 3, y0 + 16, CREAM[1])
    return s


SHELF_A = [
    [("box", 5, 12, 10, RED, "capsule"), ("penguin", 23), ("frog", 34), ("ball", 43, RED), ("ball", 50, BLUE)],
    [("daruma", 9, MUSTARD), ("box", 16, 14, 9, MUSTARD, "stripe"), ("robot", 33), ("fox", 48)],
    [("bunny", 9), ("box", 15, 10, 11, BLUE, "window"), ("box", 26, 11, 8, RED, "stripe"),
     ("kokeshi", 42, RED), ("kokeshi", 49, GREEN)],
    [("box", 5, 15, 10, ORANGE, "star"), ("whale", 28), ("owl", 41), ("ball", 50, MUSTARD)],
]
SHELF_B = [
    [("kokeshi", 7, NAVY), ("kokeshi", 14, RED), ("box", 20, 13, 11, GREEN, "window"), ("daruma", 40),
     ("daruma", 49, MUSTARD)],
    [("box", 5, 10, 11, BLUE, "face"), ("mouse", 22), ("jelly", 33), ("box", 40, 13, 10, RED, "star")],
    [("ball", 8, BLUE), ("ball", 15, RED), ("robot", 21), ("box", 31, 12, 11, ORANGE, "stripe"),
     ("tanuki", 49)],
    [("box", 5, 12, 9, NAVY, "capsule"), ("bear", 23), ("frog", 34), ("box", 41, 12, 8, MUSTARD, "window")],
]


def gallery_shelf():
    s = Cv(34, 12)
    s.hline(0, 33, 0, INK)
    s.rect(0, 1, 33, 6, WOOD[2])
    s.hline(0, 33, 6, mix(WOOD[2], WOOD[0], 0.6))
    s.hline(0, 33, 7, WOOD[0])
    s.hline(0, 33, 8, WOOD[1])
    s.hline(0, 33, 9, INK)
    s.vline(33, 1, 8, WOOD[1])
    s.rect(14, 10, 19, 10, INK)
    s.rect(15, 10, 18, 10, DSTEEL[0])
    s.rect(15, 11, 18, 11, INK)
    return s


# ---------------------------------------------------------------- posters and sign

def mini_machine(s, cx, top, arms=True):
    if arms:
        s.puts(path([(cx - 4, top + 14), (cx - 6, top + 15), (cx - 7, top + 17)]), INK)
        s.puts(path([(cx + 3, top + 14), (cx + 6, top + 13), (cx + 7, top + 10)]), INK)
        s.shape(box(cx - 8, top + 18, cx - 7, top + 19), PORC, sh=0)
        s.shape(box(cx + 7, top + 7, cx + 8, top + 9), PORC, sh=0)
    base = poly([(cx - 3, top + 11), (cx + 3, top + 11), (cx + 5, top + 21), (cx - 5, top + 21)])
    s.shape(base, RED, sh=1)
    s.vline(cx - 3, top + 13, top + 19, RED[2])
    s.rect(cx - 1, top + 13, cx, top + 14, STEEL[2])
    s.rect(cx - 1, top + 16, cx, top + 18, INK)
    globe = ell(cx, top + 6.5, 5.2, 5.2)
    s.shape(globe, SKY, sh=0)
    for (dx, dy, p) in ((-3, 2, RED), (0, 3, GREEN), (-1, 0, BLUE), (2, 1, MUSTARD), (2, -2, PORC)):
        s.rect(cx + dx - 1, top + 6 + dy - 1, cx + dx + 1, top + 6 + dy + 1, p[0])
    s.put(cx - 1, top + 6, WHITE)
    s.put(cx - 1, top + 5, INK)
    s.put(cx + 2, top + 7, WHITE)
    s.put(cx + 2, top + 6, INK)
    s.put(cx - 3, top + 3, WHITE)
    s.shape(box(cx - 3, top, cx + 2, top + 1), RED, sh=0)
    s.hline(cx - 3, cx + 1, top, RED[2])


def _skyline(s, x0, x1, yb, heights, c, win=None):
    x = x0
    i = 0
    while x <= x1:
        w = 3 + (i * 7) % 3
        h = heights[i % len(heights)]
        s.rect(x, yb - h, min(x + w - 1, x1), yb, c)
        if win is not None:
            for wy in range(yb - h + 1, yb, 2):
                s.put(x + 1, wy, win)
        x += w
        i += 1


def _paper(s, c):
    s.rect(0, 0, 27, 35, INK)
    s.rect(1, 1, 26, 34, c)


def poster_a():
    """The reference poster, pared down: title, red sun, living machine, skyline."""
    s = Cv(28, 36)
    _paper(s, CREAM[0])
    # title strip
    s.rect(1, 1, 26, 9, CREAM[2])
    kana_row(s, 3, 2, RED[0])
    s.hline(1, 26, 10, INK)
    # navy sky wedge behind the sun, like the reference
    s.puts(poly([(14, 11), (27, 11), (27, 22)]), NAVY[0])
    for (x, y) in ((22, 13), (24, 15), (25, 13)):
        s.put(x, y, CREAM[2])
    sun = ell(14, 21, 9.4, 9.4) & box(1, 11, 26, 32)
    s.puts(sun, MUSTARD[0])
    _skyline(s, 1, 26, 32, (3, 5, 4, 7, 5, 3, 6, 4), NAVY[0], MUSTARD[0])
    s.rect(1, 33, 26, 34, RED[0])
    s.hline(1, 26, 33, INK)
    s.rect(1, 34, 26, 34, RED[0])
    mini_machine(s, 14, 11)
    return s


def poster_b():
    """Capsule mascot flashing a peace sign on a full sunburst."""
    s = Cv(28, 36)
    _paper(s, CREAM[0])
    sunburst(s, box(1, 1, 26, 28), 14, 17, 8, MUSTARD[0], CREAM[2], rot=0.2)
    s.rect(1, 29, 26, 34, RED[0])
    s.hline(1, 26, 29, INK)
    for x in (5, 14, 23):
        s.pts([(x, 31), (x - 1, 32), (x, 32), (x + 1, 32), (x, 33)], CREAM[2])
    for x in (9, 18):
        s.put(x, 32, MUSTARD[0])
    # noodle arms up, gloves (the right one makes a V), legs and shoes
    s.puts(path([(8, 18), (4, 15), (4, 10)]), INK)
    s.puts(path([(20, 18), (23, 15), (23, 10)]), INK)
    s.shape(box(3, 6, 5, 9, r=1) | {(3, 6), (5, 6)}, PORC, sh=0)
    s.shape(box(22, 7, 24, 9) | {(22, 5), (22, 6), (24, 5), (24, 6)}, PORC, sh=0)
    s.vline(11, 23, 27, INK)
    s.vline(16, 23, 27, INK)
    s.shape(box(8, 27, 11, 28, r=0), PORC, sh=0)
    s.shape(box(16, 27, 19, 28, r=0), PORC, sh=0)
    body = ell(14, 17, 7, 7)
    s.shape(body, CREAM, sh=1)
    s.puts(clip(body, y1=16), RED[0])
    s.puts(clip(rim(body, 1, 0, 1), y1=16), RED[1])
    s.hline(7, 20, 17, INK)
    s.pts([(9, 13), (10, 12), (11, 11)], RED[2])
    pie_eye(s, 10, 12, 3, 5, look=1)
    pie_eye(s, 15, 12, 3, 5, look=1)
    s.pts([(11, 20), (12, 21), (13, 21), (14, 21), (15, 21), (16, 20)], INK)
    s.put(9, 19, PINK[0])
    s.put(18, 19, PINK[0])
    return s


def poster_c():
    """Mount Fuji, red sun and cloud bands."""
    s = Cv(28, 36)
    _paper(s, CREAM[0])
    for y in range(1, 8):
        for x in range(1, 27):
            if (x + y) % 2 == 0 and y < 7 - abs(x - 4) // 2:
                s.put(x, y, MUSTARD[0])
    s.puts(ell(15, 13, 8.5, 8.5), RED[0])
    for (x0, x1, y) in ((2, 11, 12), (4, 14, 14), (17, 26, 9), (19, 25, 11), (1, 7, 20), (20, 26, 21)):
        s.rect(x0, y, x1, y + 1, MUSTARD[0])
        s.hline(x0, x1, y, MUSTARD[2])
    mt = poly([(1, 31), (11, 17), (17, 17), (27, 31)]) & box(1, 1, 26, 30)
    s.shape(mt, NAVY, sh=0)
    cap = mt & (poly([(9, 22), (11, 17), (17, 17), (20, 22), (18, 21), (16, 23), (14, 21), (12, 23), (10, 21)]))
    s.puts(cap, PORC[0])
    s.puts(mt & poly([(17, 17), (27, 31), (20, 31), (16, 23)]) - cap, NAVY[1])
    s.rect(1, 30, 26, 34, RED[0])
    s.hline(1, 26, 29, INK)
    for x in range(2, 26, 3):
        s.put(x, 31, CREAM[0])
        s.put(x + 1, 33, MUSTARD[0])
    # red seal
    s.rect(22, 2, 25, 6, RED[0])
    s.rect(23, 3, 24, 5, CREAM[2])
    s.put(23, 4, RED[0])
    return s


def poster_d():
    """Sale poster: kana title over a big starburst price seal."""
    s = Cv(28, 36)
    _paper(s, NAVY[0])
    for y in range(11, 35):
        for x in range(1, 27):
            if (x + y) % 2 == 0 and (x - y < -17 or x - y > 4 and y < 20):
                s.put(x, y, BLUE[0])
    kana_row(s, 3, 2, MUSTARD[0], shadow=NAVY[1])
    seal = starburst(13.5, 22, 12.6, 10.4, 12, rot=0.13) & box(1, 10, 26, 34)
    s.shape(seal, MUSTARD, sh=0)
    s.puts(seal & ell(13.5, 22, 9.6, 8.6), MUSTARD[2])
    for i, ch in enumerate("100"):
        s.stamp(TINY[ch], 5 + i * 7 + 1, 18 + 1, MUSTARD[1], 2)
    for i, ch in enumerate("100"):
        s.stamp(TINY[ch], 5 + i * 7, 18, RED[0], 2)
    for (x, y) in ((3, 12), (24, 13)):
        s.pts([(x, y - 1), (x - 1, y), (x, y), (x + 1, y), (x, y + 1)], CREAM[0])
    return s


def sign_gacha():
    s = Cv(110, 28)
    for x in (16, 92):
        s.rect(x, 0, x + 1, 4, INK)
        s.put(x, 1, STEEL[0])
        s.put(x + 1, 3, STEEL[0])
    board = box(0, 4, 109, 27, r=2)
    s.puts(board, INK)
    inner = box(1, 5, 108, 26, r=1)
    s.puts(inner, RED[0])
    s.hline(2, 107, 5, RED[2])
    s.hline(2, 107, 26, RED[1])
    # marquee bulbs on the frame
    for x in range(5, 106, 6):
        for y in (6, 25):
            s.put(x, y, MUSTARD[2])
            s.put(x + 1, y, MUSTARD[0])
    s.rect(3, 7, 106, 24, INK)
    s.rect(4, 8, 105, 23, CREAM[0])
    s.hline(4, 105, 8, CREAM[2])
    # capsule mascot
    cap = ell(13, 16, 6, 6)
    s.shape(cap, PORC, sh=1)
    s.puts(clip(cap, y1=15), RED[0])
    s.hline(7, 18, 16, INK)
    s.put(9, 12, WHITE)
    s.put(10, 11, WHITE)
    pie_eye(s, 11, 13, 2, 3, look=1)
    pie_eye(s, 15, 13, 2, 3, look=1)
    # big kana with a navy drop shadow
    kana_row(s, 24, 9, RED[0], scale=2, gap=2, shadow=NAVY[0])
    # GACHA pill
    pill = box(73, 10, 103, 21, r=3)
    s.shape(pill, NAVY, sh=1)
    for i, ch in enumerate("GACHA"):
        s.stamp(FONT[ch], 74 + i * 6, 12, MUSTARD[0])
    return s


# ---------------------------------------------------------------- small and free-standing

def key():
    s = Cv(14, 10)
    bow = ell(4, 5, 3.2, 3.2)
    m = bow | box(6, 4, 12, 5) | box(9, 6, 9, 7) | box(11, 6, 12, 7)
    s.puts(m, MUSTARD[0])
    s.puts(rim(m, 0, 1, 1), MUSTARD[1])
    s.puts(rim(bow, 0, -1, 1), MUSTARD[2])
    s.hline(7, 11, 4, MUSTARD[2])
    s.outline_all(INK)
    s.rect(3, 4, 4, 5, INK)
    return s





def rug():
    s = Cv(96, 34)
    field = box(3, 1, 92, 32, r=3)
    s.puts(field, NAVY[0])
    for y in range(3, 31, 2):
        s.hline(1, 2, y, CREAM[0])
        s.hline(93, 94, y, CREAM[0])
    s.outline_all(INK)
    band = box(7, 3, 88, 30, r=2) - box(9, 4, 86, 29, r=2)
    s.puts(band, CREAM[0])
    med = ell(48, 16.5, 20, 8.2)
    s.puts(med, MUSTARD[0])
    sunburst(s, med & ell(48, 16.5, 18, 7.2), 48, 16.5, 8, MUSTARD[0], MUSTARD[2])
    s.puts(ell(48, 16.5, 9, 3.8), RED[0])
    s.puts(ell(48, 16.5, 9, 3.8) - ell(48, 16.5, 7, 2.9), CREAM[0])
    for (cx, cy) in ((16, 9), (79, 9), (16, 24), (79, 24)):
        for d in range(-1, 2):
            s.hline(cx - 2 * (1 - abs(d)) - 1, cx + 2 * (1 - abs(d)) + 1, cy + d, RED[0])
    s.hline(4, 91, 32, NAVY[1])
    return s


def crate():
    s = Cv(28, 30)
    # back flap standing up, side flaps folded out
    s.shape(box(4, 5, 23, 9), (CARD[2], CARD[0], CARD[2]), sh=0)
    s.shape(poly([(4, 9), (0, 12), (0, 15), (4, 14)]), CARD, sh=0)
    s.shape(poly([(24, 9), (28, 12), (28, 15), (24, 14)]), (CARD[1], CARD[1], CARD[1]), sh=0)
    # opening seen from above (dark inside) and the front face
    s.block(3, 9, 24, 29, 5, CARD, tp=(None, None, hx("5a3418")))
    s.vline(13, 15, 28, CREAM[0])
    s.vline(14, 15, 28, CREAM[1])
    s.shape(ell(19.5, 22, 2.6, 2.6), RED, sh=0)
    s.rect(19, 21, 19, 22, CREAM[2])
    s.stamp(KANA["ga"], 5, 20, CARD[1])
    # toys peeking out
    ball(s, 20, 13, BLUE)
    s.puts(path([(15, 12), (16, 5)]), INK)
    s.puts(starburst(16.5, 3.5, 3.4, 1.5, 5, rot=-math.pi / 2), MUSTARD[0])
    s.ol(starburst(16.5, 3.5, 3.4, 1.5, 5, rot=-math.pi / 2))
    ears = ell(6, 2.5, 1.8, 1.8) | ell(12, 2.5, 1.8, 1.8)
    head = ell(9, 7.5, 4.8, 4.6)
    s.shape(ears, PINK, sh=0)
    s.shape(head, PINK, sh=1)
    for x in (7, 10):
        s.put(x, 6, INK)
        s.put(x, 7, INK)
        s.put(x - 1, 6, WHITE)
    s.hline(8, 9, 9, CREAM[2])
    s.put(6, 9, PINK[1])
    s.put(11, 9, PINK[1])
    # front lip of the box over the toys
    s.hline(3, 24, 14, INK)
    s.hline(4, 23, 15, CARD[2])
    return s


def build_all():
    return {
        "toilet": toilet(), "sink": sink(),
        "power_switch_off": power_switch(False), "power_switch_on": power_switch(True),
        "lamp_off": lamp(False), "lamp_on": lamp(True),
        "sofa": sofa(), "counter": counter(),
        "computer_off": computer(False), "computer_on": computer(True),
        "door_closed": door(False), "door_open": door(True),
        "shelf_a": shelf(SHELF_A), "shelf_b": shelf(SHELF_B),
        "locker": locker(), "table": table(),
        "poster_a": poster_a(), "poster_b": poster_b(), "poster_c": poster_c(), "poster_d": poster_d(),
        "sign_gacha": sign_gacha(), "key": key(),
        "gallery_shelf": gallery_shelf(), "rug": rug(), "crate": crate(),
    }


def previews(out, prev):
    order = ["door_closed", "door_open", "shelf_a", "shelf_b", "locker", "counter",
             "sofa", "table", "rug", "crate", "toilet", "sink",
             "computer_off", "computer_on", "power_switch_off", "power_switch_on", "lamp_off", "lamp_on",
             "poster_a", "poster_b", "poster_c", "poster_d", "key", "gallery_shelf", "sign_gacha"]
    sheet([out[n] for n in order[:6]], os.path.join(prev, "rh_props_1.png"), cols=6, scale=4)
    sheet([out[n] for n in order[6:13]], os.path.join(prev, "rh_props_2.png"), cols=4, scale=4)
    sheet([out[n] for n in order[13:]], os.path.join(prev, "rh_props_3.png"), cols=7, scale=4)
    sheet([out[n] for n in order], os.path.join(prev, "rh_props.png"), cols=7, scale=4)
