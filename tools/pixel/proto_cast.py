"""Who is the protagonist? Three candidates, none of them human: a capsule
that got out of its machine, an old coin, and a light bulb. Drawn large
(112 x 140) only to choose a character and a look, with no regard for the
size the game needs; the whole sheet is shown at 0.55 saturation, like the
game's screen.

Nothing here is used by the game. It writes
tools/pixel/previews/proto_cast.png (not shipped). Run from the repository
root:

    python tools/pixel/proto_cast.py

The drawing kit (shapes rasterised four times larger and reduced, cel
colouring with hatched shadows, heavier ink on the shadow side) is the one in
proto_hero.py.
"""
import math
import os

from PIL import Image, ImageDraw

from proto_hero import (Sprite, ramp, pie_eye, fist, cuff, _row, _paper, toward_ink,
                        INK, INK_SOFT, WHITE, CREAM, GLOVE, BLACK, GREY, ROSE, BACKDROP, LABEL)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "previews", "proto_cast.png")
SATURATION = 0.55
W, H = 112, 140
GROUND = 136.5

# Full colour here; the sheet is desaturated as a whole afterwards.
TEAL = ramp("#1c5566", "#3d94aa", "#94d6dc")
SHELL = ramp("#b89f72", "#f2e2ba", "#fffaea")
GOLD = ramp("#9a6410", "#e9ac2c", "#ffe88e")
GOLD_EDGE = ramp("#5e3a0a", "#a8721a", "#dba63a")
BRASS = ramp("#7a5214", "#c8962e", "#f4d77c")
BULB = ramp("#c2a04e", "#f6e19a", "#fffbe0")
SHOE = ramp("#3d2114", "#7c4a24", "#b27a40")
TOE = ramp("#b89f72", "#f2e2ba", "#fffaea")
RED = ramp("#7e1a16", "#c93424", "#f07a40")
FLAME = ramp("#d2521a", "#ff9a2a", "#fff0a0")
PATINA = ramp("#5f8a6a")[0]
PLASTER = ramp("#b88f6a", "#e8c8a0", "#f8e6c8")
GLOW = (255, 226, 140, 110)


# --- limbs ---------------------------------------------------------------------------

def limb(s, points, width=4.4):
    s.part(s.hose(points, width), BLACK, mode="flat", outline=None)


def open_hand(s, cx, cy, up=True, thumb=1):
    """A four-finger glove held open, fingers fanned; `thumb` is its side."""
    d = -1.0 if up else 1.0
    hand = s.oval(cx, cy, 5.8, 5.4)
    for dx in (-4.4, -1.5, 1.5, 4.4):
        hand |= s.hose([(cx + dx * 0.8, cy + d * 3.0), (cx + dx * 1.3, cy + d * (10.0 - abs(dx) * 0.5))], 3.6, 3.0)
    s.part(hand, GLOVE, shade=0.26)
    for dx in (-2.9, 0.0, 2.9):                                                           # between the fingers
        s.dots(s.hose([(cx + dx * 0.95, cy + d * 4.5), (cx + dx * 1.25, cy + d * 8.5)], 1.0), INK_SOFT)
    s.part(s.hose([(cx + thumb * 4.5, cy + 1.0), (cx + thumb * 9.0, cy + d * 2.0)], 3.8, 3.0), GLOVE, shade=0.3)
    for dx in (-1.8, 0.2, 2.2):                                                           # lines on the back
        s.dots([(int(round(cx + dx)), int(round(cy - d * 2.0)) + step) for step in (0, 1, 2)], INK_SOFT)


def big_fist(s, cx, cy, thumb=(-1, -1)):
    fist(s, cx, cy, thumb=thumb, radius=6.2)
    s.dots(s.hose([(cx - 4, cy - 2.5), (cx, cy - 4), (cx + 4, cy - 2.5)], 1.0), INK_SOFT)    # knuckles


def big_shoe(s, cx, cy, facing=1, long=11.5, high=6.2):
    """A big two-tone shoe with a welt, a heel, laces and a shine on the toe."""
    upper = s.rows(s.oval(cx, cy, long, high) | s.oval(cx + facing * long * 0.45, cy - 0.8, long * 0.58, high), 0, int(cy + high - 2))
    s.part(upper, SHOE, shade=0.3)
    toe = {(x, y) for x, y in upper if (x - cx) * facing > long * 0.22}
    s.part(toe, TOE, shade=0.3, outline=None, form=upper)
    seam = [(x, y) for x, y in upper if (x, y) not in toe and (x + facing, y) in toe]
    s.dots(seam, INK_SOFT)
    s.dots([(x + facing * 2, y) for x, y in seam if y % 2 == 0 and (x + facing * 2, y) in toe], TOE[0])   # stitching
    sole = s.rows(upper, int(cy + high - 3), int(cy + high - 2))
    s.dots(sole, BLACK[1])
    s.dots(s.rows(upper, int(cy + high - 4), int(cy + high - 4)), SHOE[2])                   # welt
    heel = {(x, y) for x, y in sole if (x - cx) * facing < -long * 0.45}
    s.dots(heel | {(x, y + 1) for x, y in heel}, INK)
    for step in range(3):                                                                 # laces
        lx = cx - facing * (1.0 + step * 2.6)
        s.dots(s.hose([(lx - 1, cy - high + 1.6 + step * 0.4), (lx + 1, cy - high + 3.2 + step * 0.4)], 1.0), CREAM[1])
    s.dots(s.hose([(cx + facing * long * 0.55, cy - high + 2.4), (cx + facing * long * 0.9, cy - high + 3.0), (cx + facing * long * 1.08, cy - 1.0)], 1.0) & toe, WHITE)


def legs(s, hip_y, left_x=46.0, right_x=66.0):
    limb(s, [(left_x, hip_y), (left_x - 5, hip_y + 12), (left_x - 5.5, 124)], 4.8)
    limb(s, [(right_x, hip_y), (right_x + 6, hip_y + 12), (right_x + 4.5, 124)], 4.8)
    cuff(s, left_x - 5.5, 122.5, 4.4, 2.4)
    cuff(s, right_x + 4.5, 122.5, 4.4, 2.4)
    big_shoe(s, left_x - 10.0, 128.5, -1)
    big_shoe(s, right_x + 9.0, 128.5, 1)


def tired_face(s, cx, cy, clip, scale=1.0, lid_colors=None, smirk=True):
    """Half-shut pie-cut eyes, heavy brows (one cocked), a button nose and a
    dry half smile: grown-up, unimpressed, a little secretive."""
    ex, ry = 8.6 * scale, 9.0 * scale
    pie_eye(s, cx - ex, cy, 6.0 * scale, ry, -5, clip=clip, lid=0.36, lid_colors=lid_colors)
    pie_eye(s, cx + ex, cy - 1.5, 6.0 * scale, ry, -5, clip=clip, lid=0.36, lid_colors=lid_colors)
    s.dots(s.hose([(cx - ex - 5, cy + ry + 0.5), (cx - ex, cy + ry + 2.0), (cx - ex + 5, cy + ry + 0.5)], 1.0) & clip, INK_SOFT)   # bags
    s.dots(s.hose([(cx + ex - 5, cy + ry - 1.0), (cx + ex, cy + ry + 0.5), (cx + ex + 5, cy + ry - 1.0)], 1.0) & clip, INK_SOFT)
    s.dots(s.hose([(cx - ex - 7, cy - ry - 2.0), (cx - ex, cy - ry - 3.5), (cx - ex + 7, cy - ry + 1.0)], 2.8) & clip, INK)        # brows
    s.dots(s.hose([(cx + ex - 7, cy - ry - 2.0), (cx + ex + 1, cy - ry - 7.5), (cx + ex + 8, cy - ry - 4.0)], 2.8) & clip, INK)
    s.part(s.oval(cx + 0.5, cy + ry + 1.5, 3.4, 2.6) & clip, BLACK, mode="flat")           # button nose
    s.dots(s.oval(cx - 0.6, cy + ry + 0.6, 1.0, 0.7), WHITE)
    if smirk:
        mouth = s.hose([(cx - 9, cy + ry + 9.0), (cx - 1, cy + ry + 11.5), (cx + 10, cy + ry + 6.0)], 2.0) & clip
        s.dots(mouth, INK)
        s.dots(s.hose([(cx + 10, cy + ry + 6.0), (cx + 12.5, cy + ry + 4.0)], 1.0) & clip, INK)   # the corner that lifts
        s.dots(s.hose([(cx - 3, cy + ry + 14.0), (cx + 2, cy + ry + 14.5)], 1.0) & clip, INK_SOFT)  # lower lip


# --- A: a capsule that got out of its machine ---------------------------------------------

def capsule_man():
    s = Sprite(W, H)
    legs(s, 96.0)
    limb(s, [(84, 68), (104, 74), (93, 90)])                                              # far arm: fist on the hip
    ball = s.oval(56.0, 62.0, 32.0, 32.0)
    s.part(ball, SHELL, shade=0.25)
    slope = -0.17                                                                         # the seam tilts up to the right
    top = {(x, y) for x, y in ball if y - 60.0 < slope * (x - 56.0)}
    s.part(top, TEAL, shade=0.25, gloss=True, outline=None, form=ball)
    # What it carries inside: the shadow of a key behind the tinted half.
    key = s.oval(44.0, 40.0, 6.0, 6.0) - s.oval(44.0, 40.0, 2.8, 2.8)
    key |= s.hose([(49, 42), (66, 47)], 2.6) | s.hose([(60, 45.5), (59, 50)], 2.2) | s.hose([(65, 47), (64, 51.5)], 2.2)
    s.dots(key & top, toward_ink(TEAL[0], 0.25))
    # The seam: a ridged band with a latch.
    band = {(x, y) for x, y in ball if abs((y - 60.0) - slope * (x - 56.0)) <= 2.0}
    s.dots(band, SHELL[0])
    s.dots([(x, y) for x, y in band if abs((y - 60.0) - slope * (x - 56.0)) > 1.4], INK)
    s.dots([(x, y) for x, y in band if x % 4 == 0 and abs((y - 60.0) - slope * (x - 56.0)) <= 1.4], INK_SOFT)
    s.part(s.poly([(80, 52), (87, 51), (87.5, 59), (80.5, 60)]), SHELL, shade=0.3)           # latch
    s.dots([(83, 55), (84, 55), (83, 56), (84, 56)], INK_SOFT)
    # Gloss, wear and a mended crack.
    s.dots(s.hose([(30, 50), (33, 38), (45, 31)], 2.8) & top, WHITE)
    s.dots(s.hose([(49.5, 29.5), (53, 28.8)], 2.4) & top, WHITE)
    for px, py in ((70, 33), (74, 33), (70, 37), (74, 37)):                                 # a window, reflected
        s.dots(s.poly([(px, py), (px + 3, py), (px + 3, py + 3), (px, py + 3)]) & top, TEAL[2])
    s.dots(s.hose([(31, 76), (36, 84), (35, 88)], 1.0) | s.hose([(36, 84), (41, 86)], 1.0), INK_SOFT)      # crack
    s.part(s.poly([(30, 79), (38, 77), (39.5, 81.5), (31.5, 83.5)]), PLASTER, shade=0.3)                    # sticking plaster
    s.dots([(33, 80), (35, 80), (34, 81), (36, 81)], PLASTER[0])
    s.dots(s.hose([(66, 86), (72, 83)], 1.0) | s.hose([(68, 89), (75, 85)], 1.0) | s.hose([(52, 90), (57, 89)], 1.0), SHELL[0])   # scuffs
    tired_face(s, 55.0, 60.0, ball, lid_colors=TEAL)
    s.dots(s.oval(34.0, 73.0, 3.2, 1.8), ROSE)
    s.dots(s.oval(78.0, 69.0, 3.2, 1.8), ROSE)
    cuff(s, 97.0, 86.0, 3.0, 4.4, -30)
    big_fist(s, 92.0, 91.5)
    limb(s, [(27, 68), (6, 70), (12, 44)])                                                # near arm: scratching its head
    cuff(s, 12.5, 44.0, 4.4, 2.6, 10)
    open_hand(s, 15.0, 37.0, up=True, thumb=1)
    s.finish(GROUND, 34.0, 56.0)
    return s


# --- B: an old coin -----------------------------------------------------------------------

def coin_man():
    s = Sprite(W, H)
    legs(s, 95.0)
    limb(s, [(86, 70), (105, 66), (101, 50)])                                             # far arm: palm up, a shrug
    back = s.oval(61.0, 62.0, 31.0, 32.0)
    front = s.oval(52.0, 62.0, 31.0, 32.0) - s.oval(24.0, 44.0, 3.4, 2.6) - s.oval(30.0, 88.0, 2.6, 2.2)   # nicks in the rim
    s.part(back, GOLD_EDGE, shade=0.3, mode="tube")
    edge = back - front
    s.dots([(x, y) for x, y in edge if y % 3 == 0 and (x - 1, y) in back and (x + 1, y) in back], INK_SOFT)   # reeded edge
    s.part(front, GOLD, shade=0.24, gloss=True)
    ring = s.oval(52.0, 62.0, 27.0, 28.0) - s.oval(52.0, 62.0, 25.4, 26.4)
    s.dots(ring & front, GOLD[0])
    s.dots({(x + 1, y + 1) for x, y in ring} & front - ring, GOLD[2])                       # the rim catches light
    for step in range(0, 360, 12):                                                        # beading inside the rim
        bx = int(round(52.0 + math.cos(math.radians(step)) * 23.0))
        by = int(round(62.0 + math.sin(math.radians(step)) * 24.0))
        if (bx, by) in front:
            s.dots([(bx, by)], GOLD[0])
    star = s.poly([(52, 35), (54, 40.5), (59.5, 40.5), (55, 44), (57, 49.5), (52, 46), (47, 49.5), (49, 44), (44.5, 40.5), (50, 40.5)])
    s.part(star & front, GOLD, mode="flat", outline=INK_SOFT)                               # struck on its brow
    s.dots(star & front, GOLD[2])
    for px, py in ((33, 82), (35, 84), (32, 85), (37, 86), (34, 88), (70, 88), (72, 86), (39, 37), (41, 35)):   # verdigris
        if (px, py) in front:
            s.dots([(px, py)], PATINA)
    s.dots(s.hose([(66, 44), (72, 52)], 1.0) | s.hose([(68, 43), (73, 49)], 1.0) | s.hose([(40, 90), (46, 92)], 1.0), GOLD[0])   # scratches
    tired_face(s, 51.0, 62.0, front, lid_colors=GOLD)
    s.dots(s.oval(30.0, 75.0, 3.2, 1.8) & front, ROSE)
    s.dots(s.oval(73.0, 71.0, 3.2, 1.8) & front, ROSE)
    cuff(s, 101.0, 49.5, 4.4, 2.6)
    open_hand(s, 101.5, 42.0, up=True, thumb=-1)
    limb(s, [(23, 70), (4, 74), (10, 52)])                                                # near arm: a lit match
    cuff(s, 10.5, 52.0, 4.4, 2.6)
    s.part(s.hose([(11, 44), (12, 27)], 2.0), CREAM, mode="flat")                          # the matchstick
    big_fist(s, 11.0, 45.5, thumb=(1, -1))
    flame = s.oval(12.5, 20.0, 4.0, 6.5, 8) | s.hose([(12.5, 16), (14, 10)], 3.6, 1.0)
    s.part(flame, FLAME, shade=0.0, mode="flat")
    s.dots(s.oval(12.5, 21.5, 2.0, 3.6), FLAME[2])
    s.dots(s.oval(12.5, 26.0, 1.6, 1.4), RED[0])
    s.finish(GROUND, 34.0, 56.0)
    for point in s.oval(12.5, 19.0, 13.0, 13.0) - s.oval(12.5, 19.0, 9.5, 9.5):             # the match's glow
        if point not in s.px and (point[0] + point[1]) % 2 == 0:
            s.px[point] = GLOW
    return s


# --- C: a light bulb ----------------------------------------------------------------------

def bulb_man():
    s = Sprite(W, H)
    legs(s, 108.0, 50.0, 62.0)
    limb(s, [(73, 84), (95, 82), (92, 100)])                                              # far arm: holds its own pull chain
    base = s.poly([(41, 82), (71, 82), (69, 103), (62, 110), (50, 110), (43, 103)])
    s.part(base, BRASS, shade=0.26, mode="tube", gloss=True)
    for ty in (86, 91, 96, 101):                                                          # the thread
        thread = s.hose([(40, ty + 1.5), (56, ty - 0.5), (72, ty + 1.5)], 1.0) & base
        s.dots(thread, INK_SOFT)
        s.dots({(x, y - 1) for x, y in thread} & base, BRASS[2])
    s.part(s.oval(56.0, 110.5, 6.5, 3.0), GREY, shade=0.3)                                 # contact
    glass = s.oval(56.0, 44.0, 32.0, 31.0) | s.poly([(38, 62), (74, 62), (70, 84), (42, 84)])
    s.part(glass, BULB, shade=0.2, gloss=True)
    # The filament: two supports and a coil that burns.
    s.dots((s.hose([(50, 82), (49, 62), (45, 34)], 1.0) | s.hose([(62, 82), (63, 62), (67, 34)], 1.0)) & glass, BULB[0])
    coil = set()
    points = [(45 + step * 2.0, 34 - (5 if step % 2 else 0)) for step in range(12)]
    for index in range(len(points) - 1):
        coil |= s.hose([points[index], points[index + 1]], 1.0)
    s.dots({(x + dx, y + dy) for x, y in coil for dx in (-1, 0, 1) for dy in (-1, 0, 1)} & glass, FLAME[2])
    s.dots(coil & glass, FLAME[1])
    s.dots(s.hose([(31, 46), (34, 30), (46, 20)], 2.8) & glass, WHITE)                     # gloss
    s.dots(s.hose([(50, 17.5), (54, 16.8)], 2.4) & glass, WHITE)
    s.dots(s.hose([(80, 58), (77, 66)], 1.6) & glass, BULB[2])
    s.dots(s.hose([(40, 80), (56, 82), (72, 80)], 1.0) & glass, BULB[0])                   # cement at the neck
    tired_face(s, 55.0, 56.0, glass, scale=0.95, lid_colors=BULB)
    s.dots(s.oval(35.0, 68.0, 3.0, 1.7) & glass, ROSE)
    s.dots(s.oval(76.0, 64.0, 3.0, 1.7) & glass, ROSE)
    # The pull chain: beads from the base to the hand that holds it.
    for step in range(11):
        t = step / 10.0
        bx = 71.0 + 21.0 * t
        by = 90.0 + 11.0 * t + math.sin(t * math.pi) * 9.0
        s.part(s.oval(bx, by, 1.3, 1.3), BRASS, shade=0.3)
    cuff(s, 94.0, 98.0, 3.0, 4.4, 20)
    big_fist(s, 92.5, 103.5)
    s.part(s.oval(93.0, 113.0, 2.6, 3.4), BRASS, shade=0.3, gloss=True)                    # the chain's pull
    limb(s, [(39, 84), (16, 86), (14, 66)])                                               # near arm: a small wave
    cuff(s, 14.5, 66.0, 4.4, 2.6)
    open_hand(s, 15.0, 58.5, up=True, thumb=1)
    s.finish(GROUND, 30.0, 56.0)
    for radius, parity in ((36.0, 0), (40.0, 1), (44.0, 0)):                                # its own light
        for point in s.oval(56.0, 44.0, radius, radius - 1.0) - s.oval(56.0, 44.0, radius - 2.0, radius - 3.0):
            if point not in s.px and point[1] < 84 and (point[0] + point[1]) % 3 == parity:
                s.px[point] = GLOW
    return s


# --- sheet ----------------------------------------------------------------------------------

def desaturate(image, amount):
    """Keeps `amount` of every pixel's colour, like the game's screen grade."""
    data = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = data[x, y]
            grey = 0.299 * r + 0.587 * g + 0.114 * b
            data[x, y] = (int(round(grey + (r - grey) * amount)), int(round(grey + (g - grey) * amount)),
                          int(round(grey + (b - grey) * amount)), a)
    return image


def _tile(sprite_image, zoom, label):
    tile = Image.new("RGBA", (sprite_image.width * zoom + 24, sprite_image.height * zoom + 44), BACKDROP)
    panel = _paper(sprite_image.width, sprite_image.height)
    panel.alpha_composite(sprite_image)
    tile.alpha_composite(panel.resize((sprite_image.width * zoom, sprite_image.height * zoom), Image.NEAREST), (12, 10))
    ImageDraw.Draw(tile).text((12, sprite_image.height * zoom + 18), label, fill=LABEL)
    return tile


def build():
    cast = [("A  LA CAPSULA: se escapo de su maquina; lleva una llave dentro", capsule_man()),
            ("B  LA MONEDA: vieja, mellada, alumbra con una cerilla", coin_man()),
            ("C  LA BOMBILLA: la unica luz de la tienda; sujeta su propio interruptor", bulb_man())]
    rows = [_row([_tile(sprite.image(), 4, name) for name, sprite in cast], "PROTAGONISTA: TRES CANDIDATOS  %d x %d px, saturacion %.2f" % (W, H, SATURATION))]
    line = Image.new("RGBA", (W * 3 + 40, H + 8), (0, 0, 0, 0))
    for index, (_name, sprite) in enumerate(cast):
        line.alpha_composite(sprite.image(), (10 + index * (W + 10), 4))
    rows.append(_row([_tile(line, 2, "los tres juntos (x2)")], "COMPARACION"))
    sheet = Image.new("RGBA", (max(row.width for row in rows), sum(row.height for row in rows)), BACKDROP)
    y = 0
    for row in rows:
        sheet.alpha_composite(row, (0, y))
        y += row.height
    return desaturate(sheet, SATURATION)


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    build().save(OUT)
    print("wrote %s" % os.path.relpath(OUT))
