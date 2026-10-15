"""The capsule machine seen from right in front of it, almost in first person.

Everything here is on one 320 x 180 pixel grid, which the game shows at four
screen pixels per pixel: the dome fills the background, and below it are the
coin slot, the crank and, at the bottom, the mouth the prize comes out of.
Drawn by script on the game's palette as a first version; none of it is the
owner's own drawing.

    assets/sprites/pov/dome.png             the dome with its capsules (320 x 86)
    assets/sprites/pov/body_<machine>.png   the front of the machine (320 x 180)
    assets/sprites/pov/eyes.png             open, half shut, shut (3 frames)
    assets/sprites/pov/crank.png            the handle through half a turn (8 frames)
    assets/sprites/pov/capsule.png          a capsule in three colours (3 frames)
    assets/sprites/pov/coin.png             a coin
    assets/sprites/pov/font.png             a 5 x 7 pixel alphabet, white

Run from the repository root:

    py -3.13 tools/pixel/build_pov.py
"""
import math
import os
import random

from PIL import Image, ImageDraw

from palette import rgb

OUT = os.path.join("assets", "sprites", "pov")
W, H = 320, 180
DOME_H = 86
INK = "#0e0d0c"
SHADE = "#2a2722"
STEEL = ["#4c4337", "#716049", "#9a8766", "#c9bb9f"]
CREAM = "#e3d9c6"
GLASS = ["#453a38", "#6e5e5a"]
# Capsule colours as (dark, base, light).
BALLS = [("#5e2a26", "#80382f", "#bf6d55"), ("#8a7038", "#b09448", "#d0b870"), ("#4a4a30", "#6e6e48", "#979a72"),
         ("#4a5546", "#74806c", "#979a72"), ("#9a8766", "#c9bb9f", "#e3d9c6"), ("#5a3d28", "#7a5534", "#9a7046")]
# The body of each machine as (dark, base, light).
BODIES = {"machine_001": ("#3e1a1a", "#5e2a26", "#80382f"), "machine_002": ("#2a2722", "#4a5546", "#74806c")}
# Where things are on the body, shared with scripts/ui/gacha_pov.gd.
SLOT = (160, 99)
CRANK = (160, 128)
MOUTH = (132, 150, 188, 179)

FONT_ORDER = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?:+-%/[]'=*><"
FONT = {
    " ": ".....|.....|.....|.....|.....|.....|.....", "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#",
    "B": "####.|#...#|#...#|####.|#...#|#...#|####.", "C": ".###.|#...#|#....|#....|#....|#...#|.###.",
    "D": "####.|#...#|#...#|#...#|#...#|#...#|####.", "E": "#####|#....|#....|####.|#....|#....|#####",
    "F": "#####|#....|#....|####.|#....|#....|#....", "G": ".###.|#...#|#....|#.###|#...#|#...#|.###.",
    "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#", "I": ".###.|..#..|..#..|..#..|..#..|..#..|.###.",
    "J": "..###|...#.|...#.|...#.|...#.|#..#.|.##..", "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#",
    "L": "#....|#....|#....|#....|#....|#....|#####", "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#",
    "N": "#...#|##..#|#.#.#|#..##|#...#|#...#|#...#", "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.",
    "P": "####.|#...#|#...#|####.|#....|#....|#....", "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#",
    "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#", "S": ".####|#....|#....|.###.|....#|....#|####.",
    "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..", "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.",
    "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..", "W": "#...#|#...#|#...#|#.#.#|#.#.#|##.##|#...#",
    "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#", "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..",
    "Z": "#####|....#|...#.|..#..|.#...|#....|#####", "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.",
    "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.", "2": ".###.|#...#|....#|...#.|..#..|.#...|#####",
    "3": "####.|....#|....#|.###.|....#|....#|####.", "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.",
    "5": "#####|#....|####.|....#|....#|#...#|.###.", "6": ".###.|#....|#....|####.|#...#|#...#|.###.",
    "7": "#####|....#|...#.|..#..|.#...|.#...|.#...", "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.",
    "9": ".###.|#...#|#...#|.####|....#|....#|.###.", ".": ".....|.....|.....|.....|.....|.##..|.##..",
    ",": ".....|.....|.....|.....|.##..|..#..|.#...", "!": "..#..|..#..|..#..|..#..|..#..|.....|..#..",
    "?": ".###.|#...#|....#|...#.|..#..|.....|..#..", ":": ".....|.##..|.##..|.....|.##..|.##..|.....",
    "+": ".....|..#..|..#..|#####|..#..|..#..|.....", "-": ".....|.....|.....|#####|.....|.....|.....",
    "%": "##..#|##.#.|...#.|..#..|.#...|.#.##|#..##", "/": "....#|...#.|...#.|..#..|.#...|.#...|#....",
    "[": ".###.|.#...|.#...|.#...|.#...|.#...|.###.", "]": ".###.|...#.|...#.|...#.|...#.|...#.|.###.",
    "'": "..#..|..#..|.....|.....|.....|.....|.....", "=": ".....|.....|#####|.....|#####|.....|.....",
    "*": ".....|.....|..#..|.###.|..#..|.....|.....", ">": ".#...|..#..|...#.|....#|...#.|..#..|.#...",
    "<": "...#.|..#..|.#...|#....|.#...|..#..|...#.",
}


def new(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def ball(draw, cx, cy, r, colours):
    dark, base, light = colours
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=INK)
    draw.ellipse([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], fill=dark)
    draw.ellipse([cx - r + 1, cy - r + 1, cx + r - 3, cy + r - 3], fill=base)
    draw.ellipse([cx - r + 3, cy - r + 3, cx - r + 3 + r // 2, cy - r + 3 + r // 3], fill=light)
    draw.line([(cx - r + 2, cy + 1), (cx + r - 3, cy + 1)], fill=dark)               # the seam of the capsule


def dome():
    image = new((W, DOME_H))
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, W, DOME_H], fill=GLASS[0])
    draw.ellipse([-60, -70, W + 60, 150], fill=GLASS[1])                              # the lit inside of the glass
    rng = random.Random(1987)
    spots = []
    for row, y in enumerate((30, 46, 62, 76)):                                       # capsules piled towards us
        x = -10 + (row % 2) * 13
        while x < W + 16:
            spots.append((x + rng.randint(-3, 3), y + rng.randint(-3, 3), 13 + row + rng.randint(0, 2)))
            x += 27 + rng.randint(-2, 3)
    for x, y, r in spots:
        ball(draw, x, y, r, BALLS[rng.randrange(len(BALLS))])
    for offset in (0, 7):                                                            # a streak of light on the glass
        draw.line([(116 + offset, 4), (104 + offset, 24)], fill=CREAM, width=2 if offset == 0 else 1)
    draw.line([(206, 6), (212, 16)], fill=STEEL[3])
    # The collar the dome sits in.
    draw.rectangle([0, DOME_H - 9, W, DOME_H], fill=INK)
    draw.rectangle([0, DOME_H - 8, W, DOME_H - 2], fill=STEEL[2])
    draw.rectangle([0, DOME_H - 8, W, DOME_H - 8], fill=STEEL[3])
    draw.rectangle([0, DOME_H - 4, W, DOME_H - 2], fill=STEEL[1])
    for x in range(8, W, 24):
        draw.rectangle([x, DOME_H - 6, x + 1, DOME_H - 5], fill=STEEL[0])
    image.save(os.path.join(OUT, "dome.png"))


def body(name, colours):
    dark, base, light = colours
    image = new((W, H))
    draw = ImageDraw.Draw(image)
    top = DOME_H
    draw.rectangle([0, top, W, H], fill=base)
    draw.rectangle([0, top, W, top + 1], fill=light)
    draw.rectangle([0, H - 14, W, H], fill=dark)
    for x in (58, 104, 216, 262):                                                    # seams of the casing
        draw.line([(x, top + 2), (x, H)], fill=dark)
        draw.line([(x + 1, top + 2), (x + 1, H - 15)], fill=light)
    for x, y in ((110, top + 6), (209, top + 6), (110, H - 20), (209, H - 20)):
        draw.rectangle([x, y, x + 1, y + 1], fill=INK)
        draw.point((x, y), fill=STEEL[3])
    # Coin slot: a steel plate with the slot in it.
    sx, sy = SLOT
    draw.rectangle([sx - 15, sy - 8, sx + 15, sy + 8], fill=INK)
    draw.rectangle([sx - 14, sy - 7, sx + 14, sy + 7], fill=STEEL[2])
    draw.rectangle([sx - 14, sy - 7, sx + 14, sy - 7], fill=STEEL[3])
    draw.rectangle([sx - 14, sy + 6, sx + 14, sy + 7], fill=STEEL[1])
    draw.rectangle([sx - 7, sy - 2, sx + 7, sy + 1], fill=INK)
    draw.rectangle([sx - 6, sy - 1, sx + 6, sy - 1], fill=STEEL[0])
    for x in (sx - 12, sx + 11):
        draw.rectangle([x, sy - 5, x + 1, sy - 4], fill=STEEL[0])
        draw.rectangle([x, sy + 3, x + 1, sy + 4], fill=STEEL[0])
    # The crank's housing: a round plate with marks around it.
    cx, cy = CRANK
    draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=INK)
    draw.ellipse([cx - 21, cy - 21, cx + 21, cy + 21], fill=STEEL[1])
    draw.ellipse([cx - 21, cy - 21, cx + 19, cy + 19], fill=STEEL[2])
    draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=STEEL[0])
    for step in range(12):
        angle = step * math.tau / 12
        draw.point((round(cx + math.cos(angle) * 19), round(cy + math.sin(angle) * 19)), fill=INK)
    # The mouth the prize comes out of, with its tray.
    x0, y0, x1, y1 = MOUTH
    draw.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 1], fill=INK)
    draw.rectangle([x0 - 2, y0 - 2, x1 + 2, y1], fill=STEEL[1])
    draw.rectangle([x0 - 2, y0 - 2, x1 + 2, y0 - 2], fill=STEEL[3])
    draw.rectangle([x0, y0, x1, y1], fill=INK)
    draw.rectangle([x0 + 1, y0 + 1, x1 - 1, y0 + 4], fill=SHADE)
    draw.rectangle([x0, y1 - 5, x1, y1], fill=STEEL[0])
    draw.rectangle([x0, y1 - 5, x1, y1 - 5], fill=STEEL[2])
    image.save(os.path.join(OUT, "body_%s.png" % name))


def eyes():
    size = (62, 40)
    sheet = new((size[0] * 3, size[1]))
    for frame, lid in enumerate((0, 20, 38)):                                        # rows covered by the lid
        image = new(size)
        draw = ImageDraw.Draw(image)
        for x in (0, 32):
            draw.ellipse([x, 0, x + 29, 39], fill=INK)
            draw.ellipse([x + 2, 2, x + 27, 37], fill=CREAM)
            draw.ellipse([x + 9, 12, x + 21, 36], fill=SHADE)                         # looking down at the player
            draw.rectangle([x + 12, 16, x + 14, 19], fill=CREAM)
            if lid:
                mask = new(size)
                ImageDraw.Draw(mask).ellipse([x + 2, 2, x + 27, 37], fill=(255, 255, 255, 255))
                closed = new(size)
                ImageDraw.Draw(closed).rectangle([x, 0, x + 29, lid], fill=rgb(GLASS[1]) + (255,))
                ImageDraw.Draw(closed).rectangle([x, lid - 1, x + 29, lid], fill=rgb(INK) + (255,))
                image.paste(closed, (0, 0), Image.composite(mask, new(size), closed).getchannel("A"))
        sheet.alpha_composite(image, (frame * size[0], 0))
    sheet.save(os.path.join(OUT, "eyes.png"))


def crank():
    size = 46
    sheet = new((size * 8, size))
    for frame in range(8):
        image = new((size, size))
        draw = ImageDraw.Draw(image)
        centre = size / 2
        angle = frame * math.pi / 8
        along = (math.cos(angle), math.sin(angle))
        across = (-along[1], along[0])

        def bar(length, width):
            return [(centre + along[0] * a * length + across[0] * b * width, centre + along[1] * a * length + across[1] * b * width)
                    for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        draw.polygon(bar(20, 6), fill=INK)
        draw.polygon(bar(19, 5), fill=STEEL[2])
        draw.polygon(bar(19, 2), fill=STEEL[3])
        draw.ellipse([centre - 8, centre - 8, centre + 8, centre + 8], fill=INK)
        draw.ellipse([centre - 7, centre - 7, centre + 7, centre + 7], fill=STEEL[1])
        draw.ellipse([centre - 7, centre - 7, centre + 5, centre + 5], fill=STEEL[2])
        draw.rectangle([centre - 1, centre - 1, centre, centre], fill=INK)
        sheet.alpha_composite(image, (frame * size, 0))
    sheet.save(os.path.join(OUT, "crank.png"))


def capsule():
    size = 22
    sheet = new((size * 3, size))
    for frame, colours in enumerate((BALLS[0], BALLS[1], BALLS[3])):
        image = new((size, size))
        draw = ImageDraw.Draw(image)
        draw.ellipse([0, 0, 21, 21], fill=INK)
        draw.ellipse([2, 2, 19, 19], fill=STEEL[3])
        draw.pieslice([2, 2, 19, 19], 180, 360, fill=colours[1])
        draw.pieslice([2, 2, 17, 17], 180, 360, fill=colours[2])
        draw.pieslice([4, 4, 19, 19], 180, 360, fill=colours[1])
        draw.rectangle([1, 10, 20, 11], fill=INK)
        draw.rectangle([6, 5, 8, 6], fill=CREAM)
        draw.arc([3, 3, 18, 18], 20, 80, fill=STEEL[1])
        sheet.alpha_composite(image, (frame * size, 0))
    sheet.save(os.path.join(OUT, "capsule.png"))


def coin():
    image = new((9, 9))
    draw = ImageDraw.Draw(image)
    draw.ellipse([0, 0, 8, 8], fill=INK)
    draw.ellipse([1, 1, 7, 7], fill="#b09448")
    draw.ellipse([1, 1, 6, 6], fill="#d0b870")
    draw.rectangle([4, 3, 4, 5], fill="#8a7038")
    image.save(os.path.join(OUT, "coin.png"))


def font():
    image = new((len(FONT_ORDER) * 6, 7))
    for index, letter in enumerate(FONT_ORDER):
        for y, row in enumerate(FONT[letter].split("|")):
            for x, mark in enumerate(row):
                if mark == "#":
                    image.putpixel((index * 6 + x, y), (255, 255, 255, 255))
    image.save(os.path.join(OUT, "font.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    dome()
    for machine, colours in BODIES.items():
        body(machine, colours)
    eyes()
    crank()
    capsule()
    coin()
    font()
    print("wrote", OUT)
