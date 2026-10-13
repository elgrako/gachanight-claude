"""Machines of GachaNight in the old-cartoon sepia look (art contract v3).

Six rubber-hose machine characters after the owner's reference drawings in
`diseños/`: two gumball-style capsule machines (001-002, 72 x 126), the crane
catcher with its top hat (005, 108 x 156) and the waving plinko (006,
108 x 156), plus the loose sprites the game moves itself (capsules, claw,
plinko ball).

Every machine is drawn from posable parts by one function that takes a pose
dictionary, so animation frames are re-poses with stable volumes. Colours come
from `sepia.py`; IRON and CHROME below only re-order existing swatches.

Entry point: `tools/pixel/build_machines.py`.
"""
import math
import random

from PIL import Image, ImageChops, ImageDraw

import sepia as S

INK = S.INK
INK_SOFT = S.INK_SOFT
CLEAR = S.CLEAR
PAPER, SEPIA, GREY, BLACK = S.PAPER, S.SEPIA, S.GREY, S.BLACK
BRASS, COPPER, GOLD = S.BRASS, S.COPPER, S.GOLD
RED, MUSTARD, OLIVE, TEAL, BLUE, ROSE, PLUM, GLASS = (
    S.RED, S.MUSTARD, S.OLIVE, S.TEAL, S.BLUE, S.ROSE, S.PLUM, S.GLASS)

# Re-ordered swatches (no new colours): dark cast iron and bright chrome.
IRON = [BLACK[2], GREY[0], GREY[1], GREY[2], GREY[3]]
CHROME = [GREY[1], GREY[2], GREY[3], GREY[4], PAPER[4]]

GACHA = (72, 126)
CAB = (108, 156)

ANCHORS = {
    "machine_001": {"chute": [44, 104]},
    "machine_002": {"chute": [44, 104]},
    "machine_005": {"chute": [29, 137], "claw_rail_y": 57, "claw_min_x": 26, "claw_max_x": 65,
                    "claw_rest_x": 28, "grab_y": 68, "drop_x": 65, "drop_y": 97},
    "machine_006": {"chute": [58, 141], "ball_start": [58, 60], "rows": 6, "row_step": 8,
                    "column_step": 6, "slot_y": 118, "slot_xs": [34, 46, 58, 70, 82]},
}

# Regions that must not change during idle (and react): x0, y0, x1, y1 exclusive.
CRANE_GLASS = (10, 54, 81, 105)
PLINKO_BOARD = (27, 54, 90, 125)


# ----------------------------------------------------------------- helpers

def new(size):
    return Image.new("RGBA", size, CLEAR)


def outline(lay, colour=INK):
    """A 1 px ring (4-neighbour) around everything opaque in `lay`."""
    alpha = lay.getchannel("A")
    grown = Image.new("L", alpha.size, 0)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        shifted = Image.new("L", alpha.size, 0)
        shifted.paste(alpha, (dx, dy))
        grown = ImageChops.lighter(grown, shifted)
    ring = ImageChops.subtract(grown, alpha)
    out = Image.new("RGBA", alpha.size, colour)
    out.putalpha(ring)
    return out


def stamp(img, lay):
    """Composite a part with its ink line."""
    img.alpha_composite(outline(lay))
    img.alpha_composite(lay)


def finish(img):
    """Second ink pixel on the outer contour of a big sprite."""
    out = outline(img)
    out.alpha_composite(img)
    return out


def clip(lay, mask):
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), mask))
    return lay


def tone(ramp, index, on=True):
    """A ramp colour; two steps darker when the machine is powered off."""
    return ramp[index] if on else ramp[max(0, index - 2)]


def circ(d, p, r, fill):
    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def star_points(cx, cy, r_out, r_in, turn=-90.0):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(turn + i * 36)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def quad(p0, c, p1, n=16):
    pts = []
    for i in range(n + 1):
        t = i / float(n)
        a, b, e = (1 - t) * (1 - t), 2 * t * (1 - t), t * t
        pts.append((a * p0[0] + b * c[0] + e * p1[0], a * p0[1] + b * c[1] + e * p1[1]))
    return pts


FONT5 = {
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "N": ["#...#", "##..#", "#.#.#", "#.#.#", "#..##", "#...#", "#...#"],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
}
FONT3 = {
    "2": ["##.", "..#", ".#.", "#..", "###"],
    "5": ["###", "#..", "##.", "..#", "##."],
    "c": ["...", ".##", "#..", "#..", ".##"],
    "W": ["#...#", "#...#", "#.#.#", "##.##", "#...#"],
    "I": ["#", "#", "#", "#", "#"],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "!": ["#", "#", "#", ".", "#"],
}


def text(d, x, y, word, font, colour):
    for ch in word:
        glyph = font[ch]
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "#":
                    d.point((x + gx, y + gy), fill=colour)
        x += len(glyph[0]) + 1
    return x


ICON_COLOURS = {
    "k": INK, "w": PAPER[4], "p": PAPER[2], "r": RED[2], "R": RED[3], "b": BLUE[2], "B": BLUE[3],
    "g": OLIVE[2], "G": OLIVE[3], "m": MUSTARD[3], "y": GOLD[3], "s": GREY[3], "t": TEAL[3],
    "o": ROSE[3], "u": PLUM[3],
}
ICONS = {
    "rocket": ["......kkk", ".....kwwk", "....kwbwk", "...kwwwk.", ".kkwwwk..", "krkwwk...",
               "kRrkk....", "kmRk.....", ".kk......"],
    "planet": ["..kkkkk..", ".kBBBbbk.", "mkBBbbbkm", "kmmmmmmmk", "mkbbbbbkm", ".kbbbbbk.",
               "..kkkkk.."],
    "mushroom": ["..kkkkk..", ".kGwGGGk.", "kGGGGwwGk", "kwGGGGwGk", "kkkkkkkkk", "..kwwwk..",
                 "..kwwwk..", "..kkkkk.."],
    "tag": ["kkkkkkkk", "kwwwwwwk", "kwkkwkwk", "kwwwwwwk", "kkkkkkkk"],
    "star": ["....k....", "...kyk...", "kkkkykkkk", "kyyyyyyyk", ".kyyyyyk.", ".kyykyyk.",
             "kyyk.kyyk", "kkk...kkk"],
    "heart": [".kk.kk.", "kRRkRRk", "kRrrrrk", "krrrrrk", ".krrrk.", "..krk..", "...k..."],
    "moon": ["..kkkk..", ".kwwwkk.", "kwwwk...", "kwwpk...", "kwwpk...", "kwwppkk.", ".kwpppk.",
             "..kkkk.."],
    "fish": ["..kkk..k.", ".ktttkkok", "ktktttook", ".ktttkkok", "..kkk..k."],
    "bolt": ["...kkk", "..kyk.", ".kykk.", "kyyyk.", ".kkyk.", ".kyk..", "kyk...", "kk...."],
    "eye": [".kkkkk.", "kwwkkwk", "kwwkkwk", ".kkkkk."],
}


def icon(d, x, y, name):
    for gy, row in enumerate(ICONS[name]):
        for gx, ch in enumerate(row):
            if ch != ".":
                d.point((x + gx, y + gy), fill=ICON_COLOURS[ch])


def eye(img, cx, cy, rx, ry, state, look=(0, 0), side=1, brow=0, has_brow=True):
    """A rubber-hose eye: tall oval, pie-cut pupil, shaded white, brow line.

    state: open, half, closed, squeeze, happy, wide. side: -1 left, 1 right."""
    if state == "wide":
        ry += 1
    d = ImageDraw.Draw(img)
    d.ellipse([cx - rx - 1, cy - ry - 1, cx + rx + 1, cy + ry + 1], fill=INK)
    lay = new(img.size)
    e = ImageDraw.Draw(lay)
    box = [cx - rx, cy - ry, cx + rx, cy + ry]
    if state == "closed":
        e.ellipse(box, fill=PAPER[2])
        e.arc(box, 20, 160, fill=PAPER[1])
        e.arc(box, 200, 300, fill=PAPER[3])
        e.arc([cx - rx + 1, cy - 4, cx + rx - 1, cy + 4], 15, 165, fill=INK)
        e.point([(cx - rx + 1, cy + 3), (cx + rx - 1, cy + 3)], fill=INK)
    else:
        e.ellipse(box, fill=PAPER[4])
        e.arc(box, 30, 170, fill=PAPER[2])
        e.arc([box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1], 50, 150, fill=PAPER[3])
        if state == "squeeze":
            x0, x1 = (cx - rx + 2, cx + 2) if side < 0 else (cx + rx - 2, cx - 2)
            e.line([(x0, cy - 4), (x1, cy), (x0, cy + 4)], fill=INK, width=2)
        elif state == "happy":
            e.arc([cx - rx + 1, cy - 3, cx + rx - 1, cy + 8], 180, 360, fill=INK, width=2)
        else:
            prx = max(2, rx // 2)
            pry = max(3, int(ry * 0.55)) - (1 if state == "wide" else 0)
            px, py = cx + 1 + look[0], cy + 1 + look[1]
            e.ellipse([px - prx, py - pry, px + prx, py + pry], fill=INK)
            e.polygon([(px, py), (px + prx + 1, py - pry), (px + prx + 1, py - 1)], fill=PAPER[4])
            e.point((px - prx + 1, py + pry - 2), fill=INK_SOFT)
            if state == "half":
                ly = cy - ry // 3
                e.rectangle([cx - rx, cy - ry, cx + rx, ly], fill=PAPER[2])
                e.line([(cx - rx, ly - 1), (cx + rx, ly - 1)], fill=PAPER[1])
                e.line([(cx - rx, ly), (cx + rx, ly)], fill=INK)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse(box, fill=255)
    img.alpha_composite(clip(lay, mask))
    if has_brow and state != "closed":
        by = cy - ry - 4 - brow
        tilt = 1 if state in ("squeeze",) else 0
        d.arc([cx - rx, by + tilt, cx + rx, by + 6 + tilt], 205, 335, fill=INK, width=2)


def bulb(d, x, y, lit):
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=INK)
    d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=GOLD[4] if lit else MUSTARD[0])
    if lit:
        d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=PAPER[4])
        d.point([(x + 2, y + 1), (x + 1, y + 2)], fill=GOLD[2])
    else:
        d.point((x - 1, y - 1), fill=MUSTARD[1])


def lamp_lit(lamps, index):
    if lamps is None:
        return False
    if lamps == "all":
        return True
    return (index + lamps) % 2 == 0


def mini_capsule(d, cx, cy, ramp, ang, on=True):
    """A toy capsule inside a globe: coloured half, clear half with a toy."""
    box = [cx - 5, cy - 5, cx + 5, cy + 5]
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=INK)
    d.ellipse(box, fill=PAPER[4] if on else GLASS[1])
    d.arc(box, ang + 200, ang + 330, fill=PAPER[2] if on else GLASS[0])
    d.pieslice(box, ang, ang + 180, fill=tone(ramp, 2, on))
    d.arc(box, ang + 10, ang + 80, fill=tone(ramp, 1, on))
    d.arc(box, ang + 100, ang + 165, fill=tone(ramp, 4, on))
    dx, dy = math.cos(math.radians(ang)) * 5, math.sin(math.radians(ang)) * 5
    d.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=INK)
    nx, ny = math.cos(math.radians(ang + 90)), math.sin(math.radians(ang + 90))
    tx, ty = int(round(cx - nx * 3)), int(round(cy - ny * 3))
    d.rectangle([tx - 1, ty - 1, tx + 1, ty + 1], fill=INK_SOFT if on else BLACK[2])
    d.point((tx, ty), fill=tone(ramp, 3, on))
    hx, hy = int(round(cx + nx * 3 - 1)), int(round(cy + ny * 3 - 1))
    d.point((hx, hy), fill=PAPER[4] if on else tone(ramp, 3, on))


# ------------------------------------------------- capsule machines 001-002

GUMBALLS = {
    1: {"body": BRASS, "trim": BRASS, "plate": GREY, "cap": "dish", "shape": "flare",
        "edges": (19, 53, 9, 62), "seed": 11,
        "stickers": [("rocket", 18, 75), ("planet", 16, 87), ("mushroom", 14, 98), ("tag", 20, 108)]},
    2: {"body": BLUE, "trim": CHROME, "plate": GREY, "cap": "cone", "shape": "step",
        "edges": (20, 52, 9, 62), "seed": 51, "enamel": True,
        "stickers": [("heart", 19, 77), ("planet", 16, 88), ("star", 14, 100)]},
}

GLOBE_C = (36, 42)
GLOBE_R = 26
# dx, dy, colour ramp, angle of the coloured half: back of the pile first.
GLOBE_CAPSULES = [
    (-12, -7, MUSTARD, 200), (-1, -4, PLUM, 150), (-18, 3, TEAL, 250), (10, 1, OLIVE, 180),
    (-7, 5, ROSE, 170), (4, 8, BLUE, 215), (19, 6, COPPER, 180), (15, 13, MUSTARD, 140),
    (-14, 13, RED, 190), (-3, 16, OLIVE, 230), (8, 18, ROSE, 160), (-8, 22, BLUE, 180),
    (2, 24, MUSTARD, 200),
]
G_EYES = ((42, 39), (54, 39))
G_PIVOT = (44, 84)
G_BODY_TOP, G_BODY_BOT = 71, 114


def _shape(kind, t):
    if kind == "bell":
        return t * t
    if kind == "barrel":
        return 1 - (1 - t) * (1 - t)
    if kind == "step":
        return 0.5 * t if t < 0.72 else 0.36 + (t - 0.72) / 0.28 * 0.64
    return t


def _edges(spec, y, top, squash):
    t = (y - top) / float(G_BODY_BOT - top)
    f = _shape(spec["shape"], t)
    tl, tr, bl, br = spec["edges"]
    xl = int(round(tl + (bl - tl) * f - squash * t))
    xr = int(round(tr + (br - tr) * f + squash * t))
    xe = int(round(30 - 2 * t))
    return xl, xe, xr


def _cap(lay, style, T, cy):
    d = ImageDraw.Draw(lay)
    if style == "dish":
        d.ellipse([30, cy - 10, 42, cy - 3], fill=T[2])
        d.ellipse([14, cy - 5, 58, cy + 5], fill=T[1])
        d.ellipse([14, cy - 5, 58, cy + 3], fill=T[2])
        d.ellipse([18, cy - 5, 54, cy], fill=T[3])
    elif style == "dome":
        d.ellipse([33, cy - 11, 39, cy - 5], fill=T[2])
        d.pieslice([16, cy - 8, 56, cy + 10], 180, 360, fill=T[2])
        d.rounded_rectangle([12, cy + 1, 60, cy + 5], radius=2, fill=T[2])
    elif style == "flat":
        d.polygon([(36, cy - 11), (32, cy - 5), (40, cy - 5)], fill=T[3])
        d.rounded_rectangle([19, cy - 6, 53, cy + 3], radius=3, fill=IRON[2])
        d.rounded_rectangle([14, cy + 1, 58, cy + 5], radius=2, fill=T[2])
    else:
        d.ellipse([33, cy - 11, 39, cy - 5], fill=T[3])
        d.polygon([(34, cy - 7), (38, cy - 7), (59, cy + 2), (13, cy + 2)], fill=T[2])
        d.rounded_rectangle([12, cy + 1, 60, cy + 5], radius=2, fill=T[2])


def _cap_details(img, style, T, cy):
    d = ImageDraw.Draw(img)
    if style == "dish":
        d.line([(32, cy - 9), (36, cy - 9)], fill=T[4])
        d.line([(31, cy - 8), (31, cy - 6)], fill=T[4])
        d.line([(40, cy - 8), (41, cy - 5)], fill=T[1])
        d.arc([18, cy - 5, 54, cy], 190, 260, fill=T[4])
        d.line([(22, cy - 2), (30, cy - 3)], fill=T[4])
        d.arc([14, cy - 5, 58, cy + 3], 10, 170, fill=T[1])
        d.arc([14, cy - 5, 58, cy + 5], 20, 160, fill=T[0])
        for x in (20, 28, 36, 44, 52):
            d.point((x, cy + 2), fill=T[4])
    elif style == "dome":
        d.point([(34, cy - 9), (35, cy - 10)], fill=T[4])
        d.arc([16, cy - 8, 56, cy + 10], 190, 250, fill=T[4], width=2)
        d.arc([16, cy - 8, 56, cy + 10], 290, 350, fill=T[1], width=2)
        for x in (26, 36, 46):
            d.line([(x, cy - 6 + abs(x - 36) // 4), (x + (x - 36) // 5, cy)], fill=T[1])
        d.line([(13, cy + 1), (59, cy + 1)], fill=T[4])
        d.line([(13, cy + 5), (59, cy + 5)], fill=T[0])
        d.line([(13, cy + 4), (59, cy + 4)], fill=T[1])
        for x in range(15, 59, 4):
            d.point((x, cy + 3), fill=OLIVE[3])
    elif style == "flat":
        d.line([(36, cy - 10), (34, cy - 6)], fill=T[4])
        d.line([(21, cy - 5), (50, cy - 5)], fill=IRON[4])
        d.line([(20, cy - 4), (20, cy)], fill=IRON[3])
        d.line([(51, cy - 4), (52, cy)], fill=IRON[0])
        d.line([(20, cy - 2), (52, cy - 2)], fill=T[3])
        d.line([(20, cy - 1), (52, cy - 1)], fill=T[1])
        d.line([(15, cy + 1), (57, cy + 1)], fill=T[4])
        d.line([(15, cy + 2), (57, cy + 2)], fill=T[3])
        d.line([(15, cy + 5), (57, cy + 5)], fill=T[0])
        for x in range(17, 57, 5):
            d.point((x, cy + 3), fill=T[0])
    else:
        d.point([(34, cy - 9), (35, cy - 10)], fill=PAPER[4])
        d.line([(33, cy - 5), (18, cy + 1)], fill=T[4])
        d.line([(34, cy - 4), (24, cy)], fill=T[3])
        d.line([(40, cy - 5), (55, cy + 1)], fill=T[0])
        d.line([(39, cy - 4), (48, cy)], fill=T[1])
        d.line([(36, cy - 6), (36, cy)], fill=T[1])
        d.line([(13, cy + 1), (59, cy + 1)], fill=T[4])
        d.line([(13, cy + 5), (59, cy + 5)], fill=T[0])
        d.line([(13, cy + 4), (59, cy + 4)], fill=T[1])
        d.line([(13, cy + 3), (59, cy + 3)], fill=BLUE[2])


def gumball(number, pose):
    """One frame of a capsule machine. Pose keys: on, bob (globe, collar and
    cap shift down), sink (body top compresses), squash (body flares), cap,
    rattle, lever (radians), lamp, eyes, look, wink."""
    spec = GUMBALLS[number]
    B, T, P = spec["body"], spec["trim"], spec["plate"]
    on = pose.get("on", True)
    bob = pose.get("bob", 0)
    sink = pose.get("sink", 0)
    squash = pose.get("squash", 0)
    rattle = pose.get("rattle", 0)
    img = new(GACHA)

    # --- flared body in three quarters: shaded side on the left, lit front ---
    top = G_BODY_TOP + sink
    lay = new(GACHA)
    d = ImageDraw.Draw(lay)
    rows = {}
    for y in range(top, G_BODY_BOT + 1):
        xl, xe, xr = rows[y] = _edges(spec, y, top, squash)
        d.line([(xl, y), (xe - 1, y)], fill=B[1])
        d.line([(xl, y), (xl + 1, y)], fill=B[0])
        d.line([(xe, y), (xr, y)], fill=B[2])
        d.point((xe, y), fill=B[4])
        d.line([(xe + 1, y), (xe + 2, y)], fill=B[3])
        for x in range(xr - 6, xr - 1):
            if (x + y) % 2 == 0:
                d.point((x, y), fill=B[1])
        d.line([(xr - 1, y), (xr, y)], fill=B[1])
        if y - top < 3:
            d.line([(xe + 1, y), (xr, y)], fill=B[1])
            d.line([(xl, y), (xe - 1, y)], fill=B[0])
    rng = random.Random(spec["seed"])
    for _ in range(46):
        x, y = rng.randint(8, 62), rng.randint(G_BODY_TOP + 4, G_BODY_BOT - 1)
        kind = rng.random()
        if y not in rows:
            continue
        xl, xe, xr = rows[y]
        if xl + 2 < x < xe - 1:
            d.point((x, y), fill=B[0] if kind < 0.7 else B[2])
        elif xe + 3 < x < xr - 2:
            d.point((x, y), fill=B[1] if kind < 0.6 else B[3])
    if spec.get("patina"):
        for _ in range(14):
            x, y0, n = rng.randint(10, 60), rng.randint(G_BODY_TOP, G_BODY_TOP + 16), rng.randint(4, 15)
            for y in range(y0, y0 + n):
                if y in rows and rows[y][0] + 1 < x < rows[y][2] - 1 and (x + y) % 2 == 0:
                    side = x < rows[y][1]
                    d.point((x, y), fill=OLIVE[2] if side else OLIVE[3])
                    if n > 9 and y < y0 + n - 3:
                        d.point((x + 1, y + 1), fill=TEAL[2] if side else TEAL[3])
    if spec.get("enamel"):
        for y in (top + 6, top + 7, top + 8):
            if y in rows:
                xl, xe, xr = rows[y]
                d.line([(xl + 2, y), (xe - 1, y)], fill=PAPER[1])
                d.line([(xe + 1, y), (xr - 2, y)], fill=PAPER[3] if y < top + 8 else PAPER[2])
        for x, y in ((57, 108), (58, 109), (57, 109), (33, 111), (11, 106), (12, 107)):
            if y in rows and rows[y][0] < x < rows[y][2]:
                d.point((x, y), fill=GREY[1])
    if spec.get("pinstripe"):
        for y in range(top + 4, G_BODY_BOT - 2):
            xl, xe, xr = rows[y]
            d.point((xr - 3, y), fill=GOLD[2])
            d.point((xl + 3, y), fill=GOLD[0])
    y = G_BODY_BOT - 3
    d.line([(rows[y][1] + 1, y), (rows[y][2] - 2, y)], fill=B[1])
    d.line([(rows[y][0] + 2, y), (rows[y][1] - 1, y)], fill=B[0])
    d.line([(rows[y][1] + 1, y + 1), (rows[y][2] - 2, y + 1)], fill=B[3])
    # Foot slab.
    Sl = T if spec.get("pinstripe") else B
    sl, sr = rows[G_BODY_BOT][0] - 5, rows[G_BODY_BOT][2] + 4
    d.rectangle([sl, 115, sr, 123], fill=Sl[2])
    d.rectangle([sl, 115, 27, 123], fill=Sl[1])
    d.line([(28, 115), (sr, 115)], fill=Sl[4])
    d.line([(28, 116), (sr, 116)], fill=Sl[3])
    d.line([(sl, 115), (27, 115)], fill=Sl[2])
    d.rectangle([28, 122, sr, 123], fill=Sl[1])
    d.rectangle([sl, 122, 27, 123], fill=Sl[0])
    d.line([(sr - 1, 117), (sr - 1, 123)], fill=Sl[1])
    d.line([(sr, 116), (sr, 123)], fill=Sl[0])
    d.line([(sl, 116), (sl, 123)], fill=Sl[0])
    d.point((28, 116), fill=Sl[4])
    for x in range(33, sr - 2, 8):
        d.point((x, 119), fill=Sl[4])
        d.point((x + 1, 120), fill=Sl[0])
    for x in range(sl + 4, 26, 7):
        d.point((x, 119), fill=Sl[0])
    if spec.get("patina"):
        for x in range(sl + 1, sr, 3):
            d.point((x, 117 + (x * 7) % 3), fill=OLIVE[3] if x > 27 else OLIVE[2])
    d.rectangle([sl + 4, 124, sl + 11, 124], fill=BLACK[2])
    d.rectangle([sr - 11, 124, sr - 4, 124], fill=BLACK[2])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    # Rivets at the front corners.
    for x, y in ((33, 72 + sink), (rows[G_BODY_BOT - 8][2] - 4, G_BODY_BOT - 8)):
        d.point((x, y), fill=B[4])
        d.point((x + 1, y + 1), fill=B[0])
    # Stickers on the shaded side.
    for name, x, y in spec["stickers"]:
        icon(d, x, y, name)

    # --- coin plate, lever, chute ---------------------------------------------
    d.rectangle([32, 73, 55, 93], fill=INK)
    d.rectangle([33, 74, 54, 92], fill=P[3])
    d.line([(33, 74), (54, 74)], fill=P[4])
    d.line([(33, 74), (33, 91)], fill=P[4])
    d.line([(34, 92), (54, 92)], fill=P[1])
    d.line([(54, 75), (54, 92)], fill=P[2])
    d.line([(34, 91), (53, 91)], fill=P[2])
    for x, y in ((34, 75), (53, 75), (34, 91), (53, 91)):
        d.point((x, y), fill=P[0])
    text(d, 36, 76, "25c", FONT3, INK)
    d.rectangle([50, 79, 51, 86], fill=INK)
    d.point((51, 79), fill=P[1])
    lamp = pose.get("lamp", on)
    d.rectangle([49, 75, 52, 77], fill=INK)
    d.rectangle([50, 76, 51, 76], fill=GOLD[4] if lamp else P[0])
    circ(d, G_PIVOT, 5, INK)
    circ(d, G_PIVOT, 4, P[2])
    d.arc([G_PIVOT[0] - 4, G_PIVOT[1] - 4, G_PIVOT[0] + 4, G_PIVOT[1] + 4], 180, 280, fill=P[4])
    d.arc([G_PIVOT[0] - 4, G_PIVOT[1] - 4, G_PIVOT[0] + 4, G_PIVOT[1] + 4], 10, 100, fill=P[0])
    angle = pose.get("lever", 0.0)
    hx = G_PIVOT[0] + int(round(math.cos(angle) * 8))
    hy = G_PIVOT[1] + int(round(math.sin(angle) * 8))
    lev = new(GACHA)
    ld = ImageDraw.Draw(lev)
    ld.line([G_PIVOT, (hx, hy)], fill=GREY[3], width=3)
    circ(ld, G_PIVOT, 2, GREY[3])
    circ(ld, (hx, hy), 2.5, RED[2])
    stamp(img, lev)
    d = ImageDraw.Draw(img)
    d.line([G_PIVOT, (hx, hy)], fill=GREY[4])
    d.point(G_PIVOT, fill=GREY[1])
    circ(d, (hx, hy), 1.5, RED[3])
    d.point((hx - 1, hy - 1), fill=RED[4])
    d.point((hx + 1, hy + 2), fill=RED[1])
    # Chute: a dark mouth with a lip; the game rests the capsule here.
    d.rectangle([33, 94, 54, 114], fill=INK)
    d.rectangle([34, 95, 53, 113], fill=BLACK[1])
    d.rectangle([34, 95, 53, 96], fill=BLACK[0])
    d.line([(34, 97), (34, 110)], fill=BLACK[0])
    d.line([(53, 97), (53, 110)], fill=BLACK[2])
    d.rectangle([34, 109, 53, 111], fill=BLACK[3])
    d.line([(36, 109), (51, 109)], fill=BLACK[2])
    d.rectangle([34, 112, 53, 113], fill=B[3])
    d.line([(34, 112), (53, 112)], fill=B[4])
    d.line([(34, 114), (53, 114)], fill=B[1])

    # --- collar ------------------------------------------------------------------
    lay = new(GACHA)
    d = ImageDraw.Draw(lay)
    d.rectangle([21, 66 + bob, 51, 72 + bob], fill=T[2])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.rectangle([21, 66 + bob, 29, 72 + bob], fill=T[1])
    d.line([(30, 66 + bob), (51, 66 + bob)], fill=T[4])
    d.line([(30, 67 + bob), (51, 67 + bob)], fill=T[3])
    d.line([(21, 72 + bob), (51, 72 + bob)], fill=T[0])
    d.line([(30, 71 + bob), (51, 71 + bob)], fill=T[1])
    for x in range(23, 51, 4):
        d.line([(x, 68 + bob), (x, 70 + bob)], fill=T[0] if x < 30 else T[1])
    d.line([(50, 67 + bob), (51, 71 + bob)], fill=T[1])

    # --- glass globe -------------------------------------------------------------
    gx, gy = GLOBE_C[0], GLOBE_C[1] + bob
    rx = GLOBE_R + (1 if bob > 1 else 0)
    ry = GLOBE_R - (1 if bob > 1 else 0) + (1 if bob < -1 else 0)
    box = [gx - rx, gy - ry, gx + rx, gy + ry]
    lay = new(GACHA)
    g = ImageDraw.Draw(lay)
    g.ellipse(box, fill=GLASS[2] if on else GLASS[0])
    if on:
        g.ellipse([gx - rx - 1, gy - ry - 2, gx + rx - 5, gy + ry - 7], fill=GLASS[3])
        for y in range(gy + 6, gy + ry, 2):
            for x in range(gx + 8 + (y % 4) // 2 * 1, gx + rx, 2):
                g.point((x, y), fill=GLASS[1] if (x + y) % 4 == 0 else GLASS[2])
    g.rectangle([gx - 1, gy - ry, gx, gy + 2], fill=GREY[3] if on else GREY[0])
    g.line([(gx - 1, gy - ry), (gx - 1, gy + 2)], fill=GREY[1] if on else BLACK[2])
    for index, (dx, dy, ramp, ang) in enumerate(GLOBE_CAPSULES):
        jx = rattle * (1 if index % 2 == 0 else -1)
        jy = -abs(rattle) if index % 3 == 0 else (abs(rattle) // 2 if index % 3 == 1 else 0)
        mini_capsule(g, gx + dx + jx, gy + dy + jy, ramp, ang + rattle * 12 * (1 if index % 2 else -1), on)
    mask = Image.new("L", GACHA, 0)
    ImageDraw.Draw(mask).ellipse(box, fill=255)
    stamp(img, clip(lay, mask))
    d = ImageDraw.Draw(img)
    if on:
        d.arc([box[0] + 3, box[1] + 3, box[2] - 3, box[3] - 3], 196, 246, fill=GLASS[4], width=3)
        d.arc([box[0] + 3, box[1] + 3, box[2] - 3, box[3] - 3], 252, 262, fill=GLASS[4], width=2)
        d.arc([box[0] + 2, box[1] + 2, box[2] - 2, box[3] - 2], 20, 70, fill=GLASS[4])
        d.arc([box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1], 95, 170, fill=GLASS[1])
    else:
        d.arc([box[0] + 3, box[1] + 3, box[2] - 3, box[3] - 3], 200, 240, fill=GLASS[1], width=2)
    # The machine's own eyes, big, on the globe.
    state = pose.get("eyes", "open")
    look = pose.get("look", (0, 0))
    left = "closed" if pose.get("wink") else state
    eye(img, G_EYES[0][0], G_EYES[0][1] + bob, 6, 11, left, look, side=-1, brow=-1, has_brow=on)
    eye(img, G_EYES[1][0], G_EYES[1][1] + bob, 6, 11, state, look, side=1, brow=-1, has_brow=on)

    # --- cap ---------------------------------------------------------------------
    cy = 16 + bob + pose.get("cap", 0)
    lay = new(GACHA)
    _cap(lay, spec["cap"], T, cy)
    stamp(img, lay)
    _cap_details(img, spec["cap"], T, cy)
    return finish(img)


G_OFF = {"on": False, "eyes": "closed", "lamp": False}
G_REST = {"eyes": "open", "look": (0, 0), "lamp": True}


def gumball_idle():
    """Four seconds at 8 fps: breathing, glances, two blinks, a rattle, a wink."""
    poses = []
    for i in range(32):
        pose = dict(G_REST)
        pose["bob"] = 1 if (i // 4) % 2 == 1 else 0
        if 6 <= i < 11:
            pose["look"] = (-2, 0)
        elif 14 <= i < 18:
            pose["look"] = (2, 1)
        elif 23 <= i < 26:
            pose["look"] = (0, -2)
        if i in (3, 19):
            pose["eyes"] = "half"
        if i in (4, 20):
            pose["eyes"] = "closed"
        if i in (28, 29):
            pose["wink"] = True
        if i in (12, 13):
            pose["rattle"] = 1 if i == 12 else -1
        pose["lamp"] = (i // 3) % 2 == 0
        poses.append(pose)
    return poses


def gumball_wake():
    return [
        dict(G_OFF),
        dict(G_OFF, lamp=True),
        {"eyes": "half", "bob": 1, "sink": 1},
        {"eyes": "half", "bob": 3, "sink": 3, "squash": 2},
        {"eyes": "wide", "bob": -2, "cap": -1, "rattle": 1},
        {"eyes": "wide", "bob": -2, "look": (-2, 0)},
        {"eyes": "open", "bob": 2, "sink": 2, "squash": 1, "look": (2, 0)},
        {"eyes": "happy", "bob": 0},
        dict(G_REST),
    ]


def gumball_play():
    """Anticipation, one full turn of the lever with the globe rattling, pop."""
    return [
        {"eyes": "open", "look": (2, 2), "bob": 2, "sink": 2, "squash": 1, "lever": -0.5},
        {"eyes": "squeeze", "bob": 3, "sink": 3, "squash": 2, "lever": 0.9, "rattle": 2},
        {"eyes": "squeeze", "bob": 1, "sink": 1, "lever": 1.9, "rattle": -2},
        {"eyes": "squeeze", "bob": 3, "sink": 3, "squash": 2, "lever": 3.0, "rattle": 2},
        {"eyes": "squeeze", "bob": 1, "sink": 1, "lever": 4.1, "rattle": -2},
        {"eyes": "squeeze", "bob": 3, "sink": 3, "squash": 2, "lever": 5.3, "rattle": 2},
        {"eyes": "wide", "bob": -2, "cap": -1, "lever": 0.0, "rattle": 1},
        {"eyes": "wide", "bob": -2, "look": (0, 2)},
        {"eyes": "happy", "bob": 1, "sink": 1},
        dict(G_REST),
    ]


# -------------------------------------------------------------- crane 005

_CACHE = {}


def _plush_bear(img, cx, cy, ramp, on):
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    circ(d, (cx - 5, cy - 4), 2.5, tone(ramp, 2, on))
    circ(d, (cx + 5, cy - 4), 2.5, tone(ramp, 2, on))
    d.ellipse([cx - 7, cy - 5, cx + 7, cy + 6], fill=tone(ramp, 3, on))
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.arc([cx - 7, cy - 5, cx + 7, cy + 6], 10, 120, fill=tone(ramp, 2, on), width=2)
    d.point([(cx - 5, cy - 4), (cx + 5, cy - 4)], fill=tone(ramp, 4, on))
    d.ellipse([cx - 3, cy, cx + 3, cy + 4], fill=tone(PAPER, 3, on))
    d.point([(cx - 3, cy - 1), (cx + 3, cy - 1), (cx, cy + 1), (cx - 1, cy + 1)], fill=INK)
    d.point((cx, cy + 3), fill=INK_SOFT)
    d.point((cx - 4, cy - 3), fill=tone(ramp, 4, on))


def _plush_bunny(img, cx, cy, ramp, on):
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    d.ellipse([cx - 5, cy - 14, cx - 1, cy - 2], fill=tone(ramp, 3, on))
    d.ellipse([cx + 1, cy - 13, cx + 5, cy - 2], fill=tone(ramp, 3, on))
    d.ellipse([cx - 6, cy - 5, cx + 6, cy + 6], fill=tone(ramp, 4, on))
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.line([(cx - 3, cy - 11), (cx - 3, cy - 6)], fill=tone(ramp, 1, on))
    d.line([(cx + 3, cy - 10), (cx + 3, cy - 6)], fill=tone(ramp, 1, on))
    d.arc([cx - 6, cy - 5, cx + 6, cy + 6], 10, 120, fill=tone(ramp, 3, on), width=2)
    d.point([(cx - 2, cy - 1), (cx + 2, cy - 1)], fill=INK)
    d.point((cx, cy + 1), fill=tone(RED, 2, on))
    d.point([(cx - 1, cy + 3), (cx, cy + 3), (cx + 1, cy + 3)], fill=INK_SOFT)


def _plush_star(img, cx, cy, on):
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    d.polygon(star_points(cx, cy, 8.5, 4.2), fill=tone(MUSTARD, 3, on))
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.polygon(star_points(cx - 1, cy - 1, 4.5, 2.4), fill=tone(MUSTARD, 4, on))
    d.point([(cx - 2, cy), (cx + 2, cy)], fill=INK)
    d.line([(cx - 1, cy + 2), (cx + 1, cy + 2)], fill=INK_SOFT)


def _plush_die(img, x, y, on):
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([x, y, x + 10, y + 10], radius=2, fill=tone(PAPER, 4, on))
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.line([(x + 1, y + 10), (x + 9, y + 10)], fill=tone(PAPER, 2, on))
    d.line([(x + 10, y + 2), (x + 10, y + 9)], fill=tone(PAPER, 2, on))
    d.line([(x + 2, y + 9), (x + 9, y + 9)], fill=tone(PAPER, 3, on))
    for px, py in ((2, 2), (7, 2), (2, 7), (7, 7)):
        d.rectangle([x + px, y + py, x + px + 1, y + py + 1], fill=INK)
    d.rectangle([x + 4, y + 4, x + 5, y + 5], fill=tone(RED, 2, on))


def _plush_ball(img, cx, cy, ramp, on):
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    circ(d, (cx, cy), 6, tone(ramp, 2, on))
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.arc([cx - 6, cy - 6, cx + 6, cy + 6], 10, 110, fill=tone(ramp, 1, on), width=2)
    d.line([(cx - 5, cy - 1), (cx + 5, cy - 1)], fill=tone(PAPER, 3, on))
    d.line([(cx - 6, cy), (cx + 6, cy)], fill=tone(PAPER, 4, on))
    d.line([(cx - 5, cy + 1), (cx + 5, cy + 1)], fill=tone(PAPER, 2, on))
    d.rectangle([cx - 3, cy - 4, cx - 2, cy - 3], fill=tone(ramp, 4, on))


def crane_interior(on):
    """The glass box: static, cached, pasted identically into every frame."""
    key = ("crane", on)
    if key in _CACHE:
        return _CACHE[key]
    x0, y0, x1, y1 = CRANE_GLASS
    img = new(CAB)
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=GLASS[2] if on else GLASS[0])
    if on:
        d.rectangle([x0, y0, x1 - 1, y0 + 20], fill=GLASS[3])
        for y in range(y0 + 21, y0 + 27):
            for x in range(x0, x1):
                if (x + y) % 2 == 0 and (y - y0 - 21) < 3 + (x % 3):
                    d.point((x, y), fill=GLASS[3])
        # Back corner of the box and its floor line.
        d.line([(66, y0), (66, 86)], fill=GLASS[1])
        d.line([(x0, 86), (66, 86)], fill=GLASS[1])
        d.line([(66, 86), (x1 - 1, 92)], fill=GLASS[1])
        for x in range(67, x1, 2):
            for y in range(y0 + 3, 90, 2):
                if (x + y) % 4 == 0:
                    d.point((x, y), fill=GLASS[1])
    else:
        d.line([(66, y0), (66, 86)], fill=BLACK[2])
        d.line([(x0, 86), (66, 86)], fill=BLACK[2])
    # Rail the claw travels on.
    d.rectangle([x0, y0, x1 - 1, y0 + 2], fill=tone(GREY, 3, on))
    d.line([(x0, y0), (x1 - 1, y0)], fill=tone(GREY, 4, on))
    d.line([(x0, y0 + 2), (x1 - 1, y0 + 2)], fill=tone(GREY, 1, on) if on else BLACK[1])
    d.line([(x0, y0 + 3), (x1 - 1, y0 + 3)], fill=INK)
    for x in range(x0 + 3, x1, 6):
        d.point((x, y0 + 1), fill=tone(GREY, 1, on) if on else BLACK[1])
    # Drop hole in the right corner.
    d.rectangle([53, 90, 78, 104], fill=INK)
    d.rectangle([54, 91, 77, 93], fill=tone(GREY, 3, on))
    d.line([(54, 91), (77, 91)], fill=tone(GREY, 4, on))
    d.rectangle([54, 94, 77, 104], fill=BLACK[1])
    d.rectangle([54, 94, 77, 95], fill=BLACK[0])
    d.line([(77, 96), (77, 104)], fill=BLACK[2])
    for x in range(56, 77, 5):
        d.point((x, 92), fill=tone(GREY, 1, on) if on else BLACK[0])
    # The prize pile: back row, then front row.
    _plush_bunny(img, 30, 91, ROSE, on)
    _plush_bear(img, 17, 92, SEPIA, on)
    _plush_star(img, 44, 93, on)
    lay = new(CAB)
    mini_capsule(ImageDraw.Draw(lay), 13, 100, BLUE, 200, on)
    img.alpha_composite(lay)
    _plush_ball(img, 25, 100, RED, on)
    _plush_bear(img, 38, 100, TEAL, on)
    _plush_die(img, 44, 96, on)
    d = ImageDraw.Draw(img)
    # Hard reflections on the front pane.
    if on:
        d.line([(14, 76), (28, 60)], fill=GLASS[4], width=2)
        d.line([(19, 79), (27, 70)], fill=GLASS[4])
        d.line([(58, 66), (64, 59)], fill=GLASS[4])
    else:
        d.line([(14, 76), (28, 60)], fill=GLASS[1])
    mask = Image.new("L", CAB, 0)
    ImageDraw.Draw(mask).rectangle([x0, y0, x1 - 1, y1 - 1], fill=255)
    _CACHE[key] = clip(img, mask)
    return _CACHE[key]


def crane(pose):
    """One frame of the crane. Pose keys: on, eyes, look, wink, s (dome
    stretch, negative squashes), hat (extra hat lift), lamps (None, 'all' or a
    chase phase), mouth (smile, open, flat)."""
    on = pose.get("on", True)
    s = pose.get("s", 0)
    lamps = pose.get("lamps", 0 if on else None)
    R = RED
    img = new(CAB)

    # --- cream dome with the face (drawn first: the cabinet overlaps its base) --
    ry = 26 + s
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    d.pieslice([22, 36 - ry, 96, 36 + ry], 180, 360, fill=PAPER[2])
    d.polygon([(8, 41), (82, 41), (96, 36), (22, 36)], fill=PAPER[2])
    d.pieslice([8, 41 - ry, 82, 41 + ry], 180, 360, fill=PAPER[3])
    d.pieslice([11, 43 - ry, 70, 39 + ry - 4], 180, 360, fill=PAPER[4])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.arc([8, 41 - ry, 82, 41 + ry], 318, 360, fill=PAPER[1], width=2)
    for y in range(41 - ry + 6, 40, 2):
        for x in range(74, 96, 2):
            if img.getpixel((x, y)) == PAPER[2] and (x + y) % 4 == 0:
                d.point((x, y), fill=PAPER[1])
    d.arc([22, 36 - ry, 96, 36 + ry], 300, 360, fill=PAPER[0], width=2)
    d.arc([14, 44 - ry, 60, 80], 200, 250, fill=PAPER[4])
    fy = -(s // 2) if s >= 0 else -((s - 1) // 2)
    state = pose.get("eyes", "open")
    look = pose.get("look", (0, 0))
    left = "closed" if pose.get("wink") else state
    eye(img, 35, 26 + fy, 6, 7, left, look, side=-1, brow=-1, has_brow=on)
    eye(img, 51, 26 + fy, 6, 7, state, look, side=1, brow=-1, has_brow=on)
    mouth = pose.get("mouth", "smile" if on else "flat")
    if mouth == "open":
        d.chord([37, 30 + fy, 49, 39 + fy], 0, 180, fill=INK)
        d.rectangle([41, 37 + fy, 45, 37 + fy], fill=RED[3])
    elif mouth == "smile":
        d.arc([36, 30 + fy, 50, 38 + fy], 15, 165, fill=INK, width=2)
        d.point([(35, 34 + fy), (51, 34 + fy)], fill=INK)
    else:
        d.line([(39, 37 + fy), (47, 37 + fy)], fill=INK)

    # --- little top hat, tipped to the side ------------------------------------
    hy = -s + pose.get("hat", 0) + 1
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    d.ellipse([64, 11 + hy, 90, 17 + hy], fill=BLACK[1])
    d.polygon([(69, 14 + hy), (70, 4 + hy), (85, 5 + hy), (85, 14 + hy)], fill=BLACK[1])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.polygon([(69, 10 + hy), (85, 11 + hy), (85, 13 + hy), (69, 12 + hy)], fill=RED[2])
    d.line([(69, 10 + hy), (85, 11 + hy)], fill=RED[3])
    d.line([(71, 5 + hy), (84, 6 + hy)], fill=BLACK[3])
    d.line([(71, 6 + hy), (71, 9 + hy)], fill=BLACK[3])
    d.line([(72, 6 + hy), (72, 8 + hy)], fill=BLACK[2])
    d.arc([64, 11 + hy, 90, 17 + hy], 100, 200, fill=BLACK[3])
    d.arc([64, 11 + hy, 90, 17 + hy], 200, 250, fill=BLACK[2])

    # --- maroon cabinet: lit front, shaded side on the right --------------------
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    d.rectangle([6, 40, 82, 151], fill=R[2])
    d.polygon([(83, 40), (101, 34), (101, 145), (83, 151)], fill=R[1])
    d.rectangle([8, 152, 18, 154], fill=BLACK[2])
    d.rectangle([70, 152, 80, 154], fill=BLACK[2])
    d.polygon([(91, 149), (99, 146), (99, 148), (91, 151)], fill=BLACK[2])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.line([(6, 40), (82, 40)], fill=R[4])
    d.line([(6, 41), (82, 41)], fill=R[3])
    d.line([(6, 42), (6, 150)], fill=R[3])
    d.line([(82, 41), (82, 150)], fill=R[4])
    d.line([(100, 36), (100, 145)], fill=R[0])
    d.line([(101, 35), (101, 145)], fill=R[0])
    d.line([(83, 41), (101, 35)], fill=R[2])
    for y, col in ((52, R[0]), (106, R[0]), (122, R[0]), (146, R[0])):
        d.line([(6, y), (82, y)], fill=R[1] if y != 146 else R[0])
        d.line([(83, y), (101, y - 6)], fill=col)
    # Sloped control shelf and its fascia.
    d.rectangle([7, 107, 81, 113], fill=R[3])
    d.line([(7, 107), (81, 107)], fill=R[4])
    d.line([(7, 114), (81, 114)], fill=R[1])
    d.polygon([(83, 107), (101, 101), (101, 107), (83, 113)], fill=R[2])
    # Gold stripe, plinth.
    d.line([(7, 123), (81, 123)], fill=MUSTARD[3])
    d.line([(7, 124), (81, 124)], fill=MUSTARD[1])
    d.line([(83, 123), (101, 117)], fill=MUSTARD[1])
    d.rectangle([7, 147, 81, 151], fill=R[1])
    d.line([(7, 151), (81, 151)], fill=R[0])
    d.line([(7, 147), (81, 147)], fill=R[3])
    d.polygon([(83, 147), (100, 141), (100, 145), (83, 151)], fill=R[0])
    rng = random.Random(5)
    for _ in range(60):
        x, y = rng.randint(8, 80), rng.randint(116, 145)
        d.point((x, y), fill=R[1] if rng.random() < 0.65 else R[3])
    for _ in range(26):
        x, y = rng.randint(85, 99), rng.randint(108, 140)
        d.point((x, y), fill=R[0])
    for x, y in ((8, 148), (9, 148), (8, 149), (80, 126), (79, 125), (7, 53), (8, 54)):
        d.point((x, y), fill=SEPIA[3])
    for x, y in ((9, 127), (79, 127), (9, 143), (79, 143)):
        d.point((x, y), fill=MUSTARD[4])
        d.point((x + 1, y + 1), fill=R[0])
    # PRIZE sign with chasing bulbs.
    d.rectangle([23, 41, 65, 51], fill=INK)
    d.rectangle([24, 42, 64, 50], fill=PAPER[3] if on else PAPER[1])
    d.line([(24, 42), (64, 42)], fill=PAPER[4] if on else PAPER[2])
    d.line([(24, 50), (64, 50)], fill=PAPER[1] if on else PAPER[0])
    text(d, 31, 43, "PRIZE", FONT5, INK)
    for index, x in enumerate((11, 18, 70, 77)):
        bulb(d, x, 46, lamp_lit(lamps, index))
    for index, y in enumerate((42, 48)):
        d.point((88 + index * 6, y - 3 - index * 2), fill=GOLD[4] if lamp_lit(lamps, index) else MUSTARD[0])
    # Glass box.
    x0, y0, x1, y1 = CRANE_GLASS
    d.rectangle([x0 - 1, y0 - 1, x1, y1], fill=INK)
    d.line([(7, 54), (7, 104)], fill=R[1])
    img.alpha_composite(crane_interior(on))
    d = ImageDraw.Draw(img)
    side = [(85, 55), (98, 51), (98, 100), (85, 104)]
    d.polygon(side, fill=GLASS[1] if on else GLASS[0], outline=INK)
    if on:
        d.line([(87, 72), (94, 60)], fill=GLASS[3])
        d.line([(88, 75), (92, 68)], fill=GLASS[2])
    d.polygon([(88, 80), (95, 78), (95, 89), (88, 91)], fill=PAPER[3] if on else PAPER[1], outline=INK_SOFT)
    d.line([(90, 83), (93, 82)], fill=RED[2])
    d.line([(90, 86), (93, 85)], fill=INK_SOFT)
    d.line([(90, 88), (92, 87)], fill=INK_SOFT)
    # Controls: joystick, buttons, coin plate.
    d.ellipse([24, 109, 36, 114], fill=INK)
    d.ellipse([25, 110, 35, 113], fill=GREY[1])
    d.line([(26, 110), (33, 110)], fill=GREY[3])
    d.rectangle([29, 106, 31, 111], fill=INK)
    d.line([(30, 106), (30, 111)], fill=GREY[4])
    d.ellipse([26, 100, 34, 108], fill=INK)
    d.ellipse([27, 101, 33, 107], fill=RED[2])
    d.ellipse([28, 102, 31, 105], fill=RED[3])
    d.point((29, 102), fill=RED[4])
    d.point([(32, 106), (33, 105)], fill=RED[1])
    for cx, ramp in ((45, MUSTARD), (53, TEAL)):
        d.ellipse([cx - 3, 108, cx + 3, 113], fill=INK)
        d.ellipse([cx - 2, 109, cx + 2, 111], fill=ramp[3] if on else ramp[1])
        d.line([(cx - 2, 112), (cx + 2, 112)], fill=ramp[1])
        d.point((cx - 1, 109), fill=ramp[4] if on else ramp[2])
    d.rectangle([60, 108, 79, 120], fill=INK)
    d.rectangle([61, 109, 78, 119], fill=GREY[3])
    d.line([(61, 109), (78, 109)], fill=GREY[4])
    d.line([(61, 119), (78, 119)], fill=GREY[1])
    d.line([(78, 110), (78, 119)], fill=GREY[2])
    text(d, 63, 112, "25c", FONT3, INK)
    d.rectangle([75, 111, 76, 117], fill=INK)
    d.point([(62, 110), (62, 118)], fill=GREY[1])
    # Chute door.
    d.rectangle([13, 126, 45, 147], fill=INK)
    d.rectangle([14, 127, 44, 146], fill=GREY[2])
    d.line([(14, 127), (44, 127)], fill=GREY[4])
    d.line([(14, 128), (14, 146)], fill=GREY[3])
    d.line([(44, 128), (44, 146)], fill=GREY[1])
    d.rectangle([16, 129, 42, 146], fill=INK)
    d.rectangle([17, 130, 41, 146], fill=BLACK[1])
    d.rectangle([17, 130, 41, 131], fill=BLACK[0])
    d.rectangle([17, 143, 41, 146], fill=BLACK[3])
    d.line([(19, 143), (39, 143)], fill=BLACK[2])
    d.point([(15, 128), (43, 128), (15, 145), (43, 145)], fill=GREY[0])
    # WIN! sticker and vents.
    d.rectangle([52, 128, 76, 140], fill=INK_SOFT)
    d.rectangle([53, 129, 75, 139], fill=PAPER[3])
    d.line([(53, 129), (75, 129)], fill=PAPER[4])
    d.line([(53, 139), (75, 139)], fill=PAPER[2])
    text(d, 57, 132, "WIN!", FONT3, RED[1])
    d.point([(54, 130), (74, 130), (54, 138), (74, 138)], fill=RED[2])
    d.point([(75, 139), (74, 139), (75, 138)], fill=R[2])
    for y in (142, 144):
        d.line([(55, y), (73, y)], fill=R[0])
        d.line([(55, y + 1), (73, y + 1)], fill=R[3])
    d.line([(9, 153), (17, 153)], fill=BLACK[3])
    d.line([(71, 153), (79, 153)], fill=BLACK[3])
    return finish(img)


C_OFF = {"on": False, "eyes": "closed", "lamps": None, "mouth": "flat"}
C_REST = {"eyes": "open", "look": (0, 0), "lamps": 0}


def crane_idle():
    poses = []
    for i in range(32):
        pose = dict(C_REST)
        pose["s"] = -1 if (i // 4) % 2 == 1 else 0
        pose["hat"] = -1 if i % 8 == 4 else 0
        pose["lamps"] = (i // 2) % 2
        if 5 <= i < 10:
            pose["look"] = (-2, 1)
        elif 13 <= i < 17:
            pose["look"] = (2, 1)
        elif 24 <= i < 27:
            pose["look"] = (1, -2)
            pose["hat"] = -1
        if i in (2, 20):
            pose["eyes"] = "half"
        if i in (3, 21):
            pose["eyes"] = "closed"
        if i in (29, 30):
            pose["wink"] = True
        poses.append(pose)
    return poses


def crane_wake():
    return [
        dict(C_OFF),
        dict(C_OFF, lamps="all"),
        {"eyes": "half", "s": -1, "lamps": "all", "mouth": "flat"},
        {"eyes": "half", "s": -3, "lamps": 1, "mouth": "flat"},
        {"eyes": "wide", "s": 2, "lamps": "all", "mouth": "open"},
        {"eyes": "wide", "s": 1, "hat": -2, "look": (-2, 0), "lamps": 1, "mouth": "open"},
        {"eyes": "open", "s": -2, "look": (2, 0), "lamps": 0},
        {"eyes": "happy", "s": 0, "lamps": 1},
        dict(C_REST),
    ]


def crane_react():
    return [
        {"eyes": "wide", "s": -2, "lamps": "all", "look": (-2, 2), "mouth": "open"},
        {"eyes": "squeeze", "s": -3, "lamps": 1},
        {"eyes": "happy", "s": 2, "lamps": "all", "mouth": "open"},
        {"eyes": "happy", "s": 1, "hat": -2, "lamps": 1, "mouth": "open"},
        {"eyes": "happy", "s": -2, "lamps": "all"},
        {"eyes": "open", "s": 1, "lamps": 1},
        dict(C_REST),
    ]


# -------------------------------------------------------------- plinko 006

PEG_ROWS = 6


def plinko_board(on):
    """The upright peg board and its five slots: static, cached."""
    key = ("plinko", on)
    if key in _CACHE:
        return _CACHE[key]
    a = ANCHORS["machine_006"]
    x0, y0, x1, y1 = PLINKO_BOARD
    img = new(CAB)
    d = ImageDraw.Draw(img)
    base, shade, deep = (PAPER[3], PAPER[2], PAPER[1]) if on else (SEPIA[2], SEPIA[1], SEPIA[0])
    d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=base)
    d.rectangle([x0, y0, x1 - 1, y0 + 2], fill=deep)
    d.line([(x0, y0 + 3), (x1 - 1, y0 + 3)], fill=shade)
    d.rectangle([x0, y0, x0 + 1, y1 - 1], fill=shade)
    for y in range(y0 + 5, 108, 2):
        for x in range(x0 + 2, x1 - 1):
            if (x + y) % 4 == 0 and (x * 3 + y * 5) % 7 < 3:
                d.point((x, y), fill=shade)
    if on:
        d.line([(x1 - 2, y0 + 4), (x1 - 2, 107)], fill=PAPER[4])
    # Pegs.
    sx, sy = a["ball_start"]
    for j in range(PEG_ROWS):
        py = sy + 6 + j * a["row_step"]
        xs = [sx + k * 2 * a["column_step"] + (a["column_step"] if j % 2 else 0) for k in range(-3, 3)]
        for px in xs:
            if px - 2 < x0 + 2 or px + 2 > x1 - 3:
                continue
            d.rectangle([px, py + 1, px + 2, py + 3], fill=deep)
            d.rectangle([px - 1, py - 2, px + 1, py + 2], fill=INK)
            d.rectangle([px - 2, py - 1, px + 2, py + 1], fill=INK)
            d.rectangle([px - 1, py - 1, px + 1, py + 1], fill=tone(BLUE, 2, on))
            d.point((px - 1, py - 1), fill=tone(BLUE, 4, on))
            d.point((px, py - 1), fill=tone(BLUE, 3, on))
            d.point((px + 1, py + 1), fill=tone(BLUE, 1, on) if on else BLACK[1])
    # Slots: dark pockets between dividers.
    d.rectangle([x0, 109, x1 - 1, y1 - 1], fill=BLUE[0] if on else BLACK[1])
    d.line([(x0, 108), (x1 - 1, 108)], fill=deep)
    for index, cx in enumerate(a["slot_xs"]):
        d.rectangle([cx - 4, 109, cx + 4, 110], fill=BLACK[1] if on else BLACK[0])
        d.line([(cx - 4, y1 - 1), (cx + 4, y1 - 1)], fill=tone(BLUE, 2, on))
        mark = GOLD[3] if index == 2 else (PAPER[2] if index in (1, 3) else PAPER[0])
        d.line([(cx - 1 - (index == 2), y1 - 1), (cx + 1 + (index == 2), y1 - 1)],
               fill=mark if on else BLUE[1])
    for cx in [a["slot_xs"][0] - a["column_step"] + i * 2 * a["column_step"] for i in range(6)]:
        d.rectangle([cx - 1, 107, cx + 1, y1 - 1], fill=INK)
        d.line([(cx, 108), (cx, y1 - 1)], fill=tone(BLUE, 3, on))
        d.point((cx, 108), fill=tone(BLUE, 4, on))
    if on:
        d.line([(31, 72), (40, 59)], fill=PAPER[4])
        d.line([(33, 75), (38, 68)], fill=PAPER[4])
    mask = Image.new("L", CAB, 0)
    ImageDraw.Draw(mask).rectangle([x0, y0, x1 - 1, y1 - 1], fill=255)
    _CACHE[key] = clip(img, mask)
    return _CACHE[key]


ARM_UP = {"w": (92, 37), "a": 0.1, "c": (108, 60)}
ARM_LIMP = {"w": (97, 104), "a": math.pi, "c": (106, 92), "t": 1}
SHOULDER = (96, 86)
GLOVE = 1.35


def _arm(img, arm):
    wx, wy = arm["w"]
    ang = arm["a"]
    thumb = arm.get("t", -1)
    u = (math.sin(ang), -math.cos(ang))
    v = (math.cos(ang), math.sin(ang))

    def at(du, dv):
        du, dv = du * GLOVE, dv * GLOVE
        return (wx + u[0] * du + v[0] * dv, wy + u[1] * du + v[1] * dv)

    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    for p in quad(SHOULDER, arm["c"], (wx, wy), 60):
        d.rectangle([int(round(p[0])) - 1, int(round(p[1])) - 1, int(round(p[0])), int(round(p[1]))], fill=BLACK[1])
    circ(d, SHOULDER, 2, BLUE[1])
    stamp(img, lay)
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    circ(d, at(0.5, 0), 3.2 * GLOVE, PAPER[3])
    stamp(img, lay)
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    circ(d, at(6, 0), 5.4 * GLOVE, PAPER[4])
    for du, dv in ((10.5, -4.2), (12.5, 0), (10.5, 4.2)):
        circ(d, at(du, dv), 2.5 * GLOVE, PAPER[4])
    circ(d, at(5.5, 6.5 * thumb), 2.6 * GLOVE, PAPER[4])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    for k in (-2.2, 0, 2.2):
        d.line([at(3.5, k), at(7.5, k)], fill=INK_SOFT)
    for dv in (-2.1, 2.1):
        d.line([at(10, dv), at(12.5, dv)], fill=INK_SOFT)
    d.line([at(0.5, -2.5), at(0.5, 2.5)], fill=PAPER[1])
    d.line([at(8, -4.5 * thumb), at(4, -5 * thumb)], fill=PAPER[2])


def plinko(pose):
    """One frame of the plinko. Pose keys: on, eyes, look, wink, s (glass dome
    stretch), lamps, arm (dict with wrist w, angle a, bend c)."""
    on = pose.get("on", True)
    s = pose.get("s", 0)
    lamps = pose.get("lamps", 0 if on else None)
    B = BLUE
    img = new(CAB)

    # --- steel-blue cabinet: lit front, shaded side on the left, top visible ---
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    d.rectangle([23, 38, 93, 151], fill=B[2])
    d.polygon([(4, 32), (22, 38), (22, 151), (4, 145)], fill=B[1])
    d.polygon([(23, 37), (93, 37), (76, 32), (5, 32)], fill=B[3])
    d.ellipse([24, 150, 33, 154], fill=B[0])
    d.ellipse([83, 150, 92, 154], fill=B[0])
    d.ellipse([5, 144, 12, 148], fill=B[0])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.line([(23, 38), (93, 38)], fill=B[4])
    d.line([(23, 39), (93, 39)], fill=B[3])
    d.line([(23, 40), (23, 150)], fill=B[4])
    d.line([(24, 40), (24, 150)], fill=B[3])
    d.rectangle([92, 40, 93, 150], fill=B[1])
    d.line([(6, 33), (75, 33)], fill=B[4])
    d.line([(8, 34), (22, 37)], fill=B[2])
    d.rectangle([4, 34, 5, 144], fill=B[0])
    d.line([(4, 33), (22, 39)], fill=B[2])
    for y in (52, 126):
        d.line([(25, y), (91, y)], fill=B[1])
        d.line([(25, y + 1), (91, y + 1)], fill=B[3])
        d.line([(4, y - 6), (22, y)], fill=B[0])
    d.rectangle([25, 147, 91, 151], fill=B[1])
    d.line([(25, 151), (91, 151)], fill=B[0])
    d.polygon([(6, 141), (21, 146), (21, 150), (6, 145)], fill=B[0])
    rng = random.Random(6)
    for _ in range(40):
        x, y = rng.randint(26, 90), rng.randint(128, 146)
        d.point((x, y), fill=B[1] if rng.random() < 0.6 else B[3])
    for _ in range(40):
        x, y = rng.randint(7, 20), rng.randint(44, 138)
        d.point((x, y), fill=B[0] if rng.random() < 0.8 else B[2])
    for y in range(58, 124, 13):
        for x in (24, 92):
            d.point((x, y), fill=B[4])
            d.point((x, y + 1), fill=B[0])
    for x, y in ((7, 40), (19, 44), (7, 136), (19, 140), (7, 62), (19, 66), (7, 110), (19, 114)):
        d.point((x, y), fill=B[3])
        d.point((x + 1, y + 1), fill=B[0])
    # Star badge on the side panel.
    d.ellipse([5, 78, 21, 94], fill=INK)
    d.ellipse([6, 79, 20, 93], fill=B[0])
    d.arc([6, 79, 20, 93], 0, 360, fill=PAPER[1])
    d.arc([6, 79, 20, 93], 180, 300, fill=PAPER[3])
    d.polygon(star_points(13, 86, 5.6, 2.3), fill=PAPER[3] if on else PAPER[1])
    d.point((13, 82), fill=PAPER[4] if on else PAPER[2])
    for y in (100, 103):
        d.line([(8, y), (18, y + 3)], fill=B[0])
    for y in (70, 73):
        d.line([(8, y - 4), (18, y - 1)], fill=B[0])
    # PLINKO sign with chasing bulbs.
    d.rectangle([37, 40, 79, 50], fill=INK)
    d.rectangle([38, 41, 78, 49], fill=PAPER[3] if on else PAPER[1])
    d.line([(38, 41), (78, 41)], fill=PAPER[4] if on else PAPER[2])
    text(d, 42, 42, "PLINKO", FONT5, INK)
    bulb(d, 30, 45, lamp_lit(lamps, 0))
    bulb(d, 86, 45, lamp_lit(lamps, 1))
    # Board.
    x0, y0, x1, y1 = PLINKO_BOARD
    d.rectangle([x0 - 1, y0 - 1, x1, y1], fill=INK)
    img.alpha_composite(plinko_board(on))
    d = ImageDraw.Draw(img)
    # Tray under the board.
    d.rectangle([45, 129, 71, 151], fill=INK)
    d.rectangle([46, 130, 70, 150], fill=GREY[2])
    d.line([(46, 130), (70, 130)], fill=GREY[4])
    d.line([(46, 131), (46, 150)], fill=GREY[3])
    d.line([(70, 131), (70, 150)], fill=GREY[1])
    d.rectangle([47, 131, 69, 150], fill=INK)
    d.rectangle([48, 132, 68, 150], fill=BLACK[1])
    d.rectangle([48, 132, 68, 133], fill=BLACK[0])
    d.rectangle([48, 147, 68, 150], fill=BLACK[3])
    d.line([(50, 147), (66, 147)], fill=BLACK[2])
    for cx in (34, 82):
        d.polygon(star_points(cx, 138, 5.5, 2.4), fill=MUSTARD[3], outline=INK)
        d.point((cx - 1, 137), fill=MUSTARD[4])
    for cx in (29, 39, 77, 87):
        d.point((cx, 131), fill=B[4])
        d.point((cx + 1, 132), fill=B[0])

    # --- glass dome with the eyes, sitting on the top face -----------------------
    ry = 23 + s
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    d.ellipse([25, 31, 73, 39], fill=B[1])
    stamp(img, lay)
    lay = new(CAB)
    d = ImageDraw.Draw(lay)
    d.pieslice([28, 35 - ry, 70, 35 + ry], 180, 360, fill=GLASS[2] if on else GLASS[0])
    d.ellipse([28, 32, 70, 38], fill=GLASS[2] if on else GLASS[0])
    d.ellipse([46, 6 - s, 52, 12 - s], fill=B[2])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    if on:
        mask = Image.new("L", CAB, 0)
        ImageDraw.Draw(mask).pieslice([28, 35 - ry, 70, 35 + ry], 180, 360, fill=255)
        lit = new(CAB)
        ImageDraw.Draw(lit).ellipse([27, 34 - ry, 64, 30 + ry], fill=GLASS[3])
        img.alpha_composite(clip(lit, mask))
        d = ImageDraw.Draw(img)
        d.arc([31, 38 - ry, 67, 32 + ry], 195, 245, fill=GLASS[4], width=3)
        d.arc([30, 37 - ry, 68, 33 + ry], 300, 340, fill=GLASS[4])
    else:
        d.arc([31, 38 - ry, 67, 32 + ry], 200, 240, fill=GLASS[1], width=2)
    d.point([(47, 8 - s), (48, 7 - s)], fill=B[4])
    d.point([(51, 10 - s), (50, 11 - s)], fill=B[0])
    d.arc([25, 31, 73, 39], 10, 170, fill=B[3], width=1)
    d.arc([25, 30, 73, 38], 20, 160, fill=B[0])
    fy = -(s // 2) if s >= 0 else -((s - 1) // 2)
    state = pose.get("eyes", "open")
    look = pose.get("look", (0, 0))
    left = "closed" if pose.get("wink") else state
    eye(img, 43, 24 + fy, 5, 7, left, look, side=-1, brow=-1, has_brow=on)
    eye(img, 55, 24 + fy, 5, 7, state, look, side=1, brow=-1, has_brow=on)

    # --- the waving arm ----------------------------------------------------------
    _arm(img, pose.get("arm", ARM_UP if on else ARM_LIMP))
    return finish(img)


P_OFF = {"on": False, "eyes": "closed", "lamps": None, "arm": ARM_LIMP}
P_REST = {"eyes": "open", "look": (0, 0), "lamps": 0, "arm": ARM_UP}


def _wave(angle, dy=0):
    return {"w": (92, 37 + dy), "a": angle, "c": (108, 60 + dy)}


def plinko_idle():
    poses = []
    swing = [0.1, -0.1, -0.3, -0.1, 0.1, 0.3, 0.1, -0.1, -0.3, -0.1, 0.1, 0.3]
    for i in range(32):
        pose = dict(P_REST)
        pose["s"] = -1 if (i // 4) % 2 == 1 else 0
        pose["lamps"] = (i // 2) % 2
        if 8 <= i < 20:
            pose["arm"] = _wave(swing[i - 8])
            pose["look"] = (2, 0)
        if 22 <= i < 26:
            pose["look"] = (-2, 1)
        if i in (3, 27):
            pose["eyes"] = "half"
        if i in (4, 28):
            pose["eyes"] = "closed"
        if 12 <= i < 16:
            pose["eyes"] = "happy"
        poses.append(pose)
    return poses


def plinko_wake():
    return [
        dict(P_OFF),
        dict(P_OFF, lamps="all"),
        {"eyes": "half", "s": -1, "lamps": "all", "arm": ARM_LIMP},
        {"eyes": "half", "s": -3, "lamps": 1, "arm": {"w": (97, 100), "a": math.pi, "c": (107, 90), "t": 1}},
        {"eyes": "wide", "s": 3, "lamps": "all", "arm": {"w": (95, 58), "a": 0.0, "c": (108, 76)}},
        {"eyes": "wide", "s": 2, "look": (2, 0), "lamps": 1, "arm": _wave(-0.3, -3)},
        {"eyes": "open", "s": -2, "look": (2, 0), "lamps": 0, "arm": _wave(0.3, 1)},
        {"eyes": "happy", "s": 0, "lamps": 1, "arm": _wave(-0.1)},
        dict(P_REST),
    ]


def plinko_react():
    return [
        {"eyes": "wide", "s": -2, "lamps": "all", "look": (0, 2), "arm": _wave(0.1, 2)},
        {"eyes": "squeeze", "s": -3, "lamps": 1, "arm": _wave(0.1, 4)},
        {"eyes": "happy", "s": 3, "lamps": "all", "arm": _wave(-0.3, -4)},
        {"eyes": "happy", "s": 2, "lamps": 1, "arm": _wave(0.3, -3)},
        {"eyes": "happy", "s": -2, "lamps": "all", "arm": _wave(-0.3, 1)},
        {"eyes": "open", "s": 1, "lamps": 1, "arm": _wave(0.2)},
        dict(P_REST),
    ]


# ------------------------------------------------------------ loose sprites

def capsule(ramp):
    """18 x 18 toy capsule: coloured top, clear bottom with a tiny toy."""
    img = new((18, 18))
    lay = new((18, 18))
    d = ImageDraw.Draw(lay)
    box = [1, 1, 16, 16]
    d.ellipse(box, fill=PAPER[4])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.arc(box, 10, 100, fill=GLASS[2], width=2)
    d.arc(box, 100, 170, fill=GLASS[3])
    d.pieslice(box, 180, 360, fill=ramp[2])
    d.arc(box, 290, 360, fill=ramp[1], width=2)
    d.arc([2, 2, 15, 15], 190, 260, fill=ramp[3], width=2)
    d.rectangle([4, 4, 6, 5], fill=ramp[4])
    d.point((4, 4), fill=PAPER[4])
    d.point((4, 6), fill=ramp[4])
    d.line([(1, 8), (16, 8)], fill=ramp[0])
    d.line([(1, 9), (16, 9)], fill=INK)
    d.line([(2, 10), (15, 10)], fill=PAPER[3])
    # The toy: a tiny robot head.
    toy = TEAL if ramp in (RED, MUSTARD, GOLD) else ROSE
    d.rectangle([6, 11, 11, 15], fill=INK_SOFT)
    d.rectangle([7, 12, 10, 14], fill=toy[3])
    d.point([(7, 13), (10, 13)], fill=INK)
    d.point((8, 11), fill=toy[2])
    d.point((3, 12), fill=GLASS[4])
    if ramp is GOLD:
        d.point([(12, 3), (11, 4), (13, 4), (12, 5), (12, 4)], fill=PAPER[4])
    return img


def claw(is_open):
    """30 x 30 crane claw hanging from its top centre (15, 0)."""
    img = new((30, 30))
    if is_open:
        left = [(10, 9), (4, 14), (3, 21), (7, 27)]
        mid = [(15, 11), (15, 19)]
    else:
        left = [(10, 9), (6, 15), (7, 22), (13, 27)]
        mid = [(15, 11), (15, 16)]
    right = [(29 - x, y) for x, y in left]
    lay = new((30, 30))
    d = ImageDraw.Draw(lay)
    for pts in (left, right, mid):
        d.line(pts, fill=GREY[3], width=2)
        circ(d, pts[-1], 1.5, RED[2])
        for p in pts[1:-1]:
            circ(d, p, 1.5, GREY[2])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    for pts in (left, right):
        d.line(pts[:3], fill=GREY[4])
        for p in pts[1:-1]:
            d.point(p, fill=GREY[1])
        d.point(pts[-1], fill=RED[3])
    d.point(mid[-1], fill=RED[3])
    lay = new((30, 30))
    d = ImageDraw.Draw(lay)
    d.rectangle([14, 0, 15, 4], fill=GREY[2])
    d.ellipse([8, 4, 21, 12], fill=BRASS[2])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.line([(14, 0), (14, 3)], fill=GREY[4])
    d.arc([8, 4, 21, 12], 180, 290, fill=BRASS[4])
    d.line([(11, 6), (14, 5)], fill=BRASS[4])
    d.arc([8, 4, 21, 12], 0, 150, fill=BRASS[0])
    d.line([(11, 10), (18, 10)], fill=BRASS[1])
    # A tiny face on the hub: the claw is a character too.
    d.rectangle([12, 7, 12, 8], fill=INK)
    d.rectangle([17, 7, 17, 8], fill=INK)
    return img


def plinko_ball():
    img = new((9, 9))
    lay = new((9, 9))
    d = ImageDraw.Draw(lay)
    d.ellipse([1, 1, 7, 7], fill=GOLD[2])
    stamp(img, lay)
    d = ImageDraw.Draw(img)
    d.arc([1, 1, 7, 7], 0, 110, fill=GOLD[0])
    d.point([(5, 5), (4, 6), (6, 4)], fill=GOLD[1])
    d.rectangle([2, 2, 3, 3], fill=GOLD[4])
    d.point((4, 2), fill=GOLD[3])
    d.point((2, 4), fill=GOLD[3])
    d.point((2, 2), fill=PAPER[4])
    return img


# ------------------------------------------------------------ public tables

def _frames(draw, poses):
    cache, out = {}, []
    for pose in poses:
        key = repr(sorted(pose.items(), key=lambda kv: kv[0]))
        if key not in cache:
            cache[key] = draw(pose)
        out.append(cache[key])
    return out


def stills():
    """name -> image, powered off (and the loose sprites)."""
    out = {}
    for n in sorted(GUMBALLS):
        out["machine_%03d" % n] = gumball(n, G_OFF)
    out["machine_005"] = crane(C_OFF)
    out["machine_006"] = plinko(P_OFF)
    for name, ramp in S.CAPSULE.items():
        out["capsule_" + name] = capsule(ramp)
    out["claw_open"] = claw(True)
    out["claw_closed"] = claw(False)
    out["plinko_ball"] = plinko_ball()
    return out


def animations():
    """name -> (frames, fps, loop)."""
    out = {}
    for n in sorted(GUMBALLS):
        def draw(pose, n=n):
            return gumball(n, pose)
        key = "machine_%03d_" % n
        out[key + "wake"] = (_frames(draw, gumball_wake()), 15, False)
        out[key + "idle"] = (_frames(draw, gumball_idle()), 8, True)
        out[key + "play"] = (_frames(draw, gumball_play()), 15, False)
    out["machine_005_wake"] = (_frames(crane, crane_wake()), 15, False)
    out["machine_005_idle"] = (_frames(crane, crane_idle()), 8, True)
    out["machine_005_react"] = (_frames(crane, crane_react()), 15, False)
    out["machine_006_wake"] = (_frames(plinko, plinko_wake()), 15, False)
    out["machine_006_idle"] = (_frames(plinko, plinko_idle()), 8, True)
    out["machine_006_react"] = (_frames(plinko, plinko_react()), 15, False)
    return out
