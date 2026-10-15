"""Set dressing: small, detailed props for the store's walls and floor, and the
reception counter, all at standard density (1.5 art pixels per world pixel,
the 640 x 360 grid of docs/art/pixel-density.md) and on the palette.

Drawn by script as a first version; none of it is the owner's own drawing.
Each prop is drawn pixel by pixel with an ink outline, two or three tones of
shading and a few lit pixels. No lettering: Japanese text is not to be drawn
without the owner checking it.

    assets/sprites/set/<name>.png

Run from the repository root:

    py -3.13 tools/pixel/build_set.py
"""
import math
import os

from PIL import Image, ImageDraw

from palette import rgb

OUT = os.path.join("assets", "sprites", "set")

INK = "#0e0d0c"
SHADE = "#2a2722"
N2, N3, N4, N5, N6 = "#4c4337", "#716049", "#9a8766", "#c9bb9f", "#e3d9c6"
UMBER = ["#3d2a1e", "#5a3d28", "#7a5534", "#9a7046", "#b98d5c"]
OCHRE = ["#8a7038", "#b09448", "#d0b870", "#e0c890"]
OLIVE = ["#4a4a30", "#6e6e48", "#979a72"]
RED = ["#3e1a1a", "#5e2a26", "#80382f", "#a14d3e", "#bf6d55"]
RUST = ["#5e3424", "#8a4e30", "#b0704a"]
PEACH = "#d4a07a"
GREEN = ["#4a5546", "#74806c", "#9fa68e"]
MAUVE = ["#453a38", "#6e5e5a", "#968683"]


def canvas(w, h):
    image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def px(draw, x, y, colour):
    draw.point((x, y), fill=colour)


def outline(image, colour=INK):
    """One ink line around everything drawn."""
    pixels = image.load()
    w, h = image.size
    edge = []
    for y in range(h):
        for x in range(w):
            if pixels[x, y][3]:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and pixels[nx, ny][3]:
                    edge.append((x, y))
                    break
    for x, y in edge:
        pixels[x, y] = rgb(colour) + (255,)
    return image


def save(name, image):
    image.save(os.path.join(OUT, name + ".png"))


def grain(draw, box, colours, step, seed):
    """Wood grain: broken streaks along the board."""
    x0, y0, x1, y1 = box
    rng = seed
    for x in range(x0, x1 + 1, step):
        for y in range(y0, y1 + 1):
            rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
            if rng % 7 == 0:
                px(draw, x + (rng >> 8) % 2, y, colours[(rng >> 4) % len(colours)])


# --- Walls --------------------------------------------------------------------------

def clock():
    image, draw = canvas(25, 25)
    draw.ellipse([0, 0, 24, 24], fill=UMBER[1])
    draw.ellipse([0, 0, 22, 22], fill=UMBER[2])
    draw.ellipse([3, 3, 21, 21], fill=OCHRE[1])
    draw.ellipse([4, 4, 20, 20], fill=OCHRE[3])
    draw.arc([4, 4, 20, 20], 200, 290, fill=N6)
    for step in range(12):
        angle = step * math.tau / 12
        x, y = 12 + math.sin(angle) * 6.5, 12 - math.cos(angle) * 6.5
        px(draw, round(x), round(y), SHADE if step % 3 else INK)
    # Twenty to midnight.
    draw.line([(12, 12), (11, 7)], fill=INK)
    draw.line([(12, 12), (8, 9)], fill=INK)
    draw.line([(12, 12), (15, 17)], fill=RED[3])
    px(draw, 12, 12, OCHRE[0])
    px(draw, 6, 5, N6)
    save("clock", outline(image))


def frame_landscape():
    image, draw = canvas(33, 25)
    draw.rectangle([0, 0, 32, 24], fill=OCHRE[0])
    draw.rectangle([0, 0, 31, 23], fill=OCHRE[1])
    draw.line([(1, 1), (30, 1)], fill=OCHRE[2])
    draw.rectangle([3, 3, 29, 21], fill=SHADE)
    draw.rectangle([4, 4, 28, 20], fill=PEACH)                                      # an evening sky
    draw.rectangle([4, 4, 28, 8], fill=OCHRE[3])
    draw.ellipse([20, 7, 25, 12], fill=N6)                                          # the moon
    draw.polygon([(4, 16), (11, 10), (17, 15), (22, 11), (28, 15), (28, 20), (4, 20)], fill=GREEN[1])
    draw.polygon([(4, 18), (9, 15), (15, 18), (21, 16), (28, 19), (28, 20), (4, 20)], fill=OLIVE[1])
    draw.rectangle([12, 15, 15, 18], fill=RED[2])                                   # a small house
    draw.polygon([(11, 15), (13, 13), (16, 15)], fill=UMBER[1])
    px(draw, 13, 17, OCHRE[3])
    save("frame_landscape", outline(image))


def frame_employee():
    image, draw = canvas(21, 27)
    draw.rectangle([0, 0, 20, 26], fill=UMBER[0])
    draw.rectangle([0, 0, 19, 25], fill=UMBER[2])
    draw.line([(1, 1), (18, 1)], fill=UMBER[3])
    draw.rectangle([3, 3, 17, 19], fill=N5)
    coin = Image.open(os.path.join("assets", "sprites", "ui", "coin_face.png")).convert("RGBA")
    coin = coin.resize((12, 14), Image.LANCZOS)
    coin.putalpha(coin.getchannel("A").point(lambda a: 255 if a > 120 else 0))
    image.alpha_composite(coin, (4, 5))
    draw.rectangle([4, 21, 16, 23], fill=OCHRE[1])                                  # the brass name plate
    draw.line([(5, 22), (15, 22)], fill=OCHRE[0])
    save("frame_employee", outline(image))


def bunting():
    image, draw = canvas(96, 16)
    sag = lambda x: 2 + round(3 * math.sin(math.pi * x / 95))
    colours = [(RED[3], RED[2]), (OCHRE[2], OCHRE[1]), (N6, N5), (GREEN[1], GREEN[0])]
    for index, x in enumerate(range(4, 92, 15)):
        top = sag(x + 5) + 1
        light, dark = colours[index % 4]
        draw.polygon([(x, top), (x + 11, top), (x + 5, top + 10)], fill=light)
        draw.polygon([(x + 6, top), (x + 11, top), (x + 5, top + 10)], fill=dark)
        px(draw, x + 3, top + 2, N6 if light != N6 else OCHRE[2])
    for x in range(96):
        px(draw, x, sag(x), N3)
    save("bunting", outline(image))


def toy_shelf():
    image, draw = canvas(57, 33)
    draw.rectangle([0, 23, 56, 26], fill=UMBER[2])                                  # the plank
    draw.line([(0, 23), (56, 23)], fill=UMBER[3])
    draw.line([(0, 26), (56, 26)], fill=UMBER[0])
    for x in (6, 48):                                                               # brackets
        draw.polygon([(x, 27), (x + 3, 27), (x + 3, 32), (x, 29)], fill=N3)
    # A daruma: round, red, with a cream face.
    draw.ellipse([2, 9, 15, 23], fill=RED[2])
    draw.ellipse([2, 9, 13, 21], fill=RED[3])
    draw.ellipse([5, 12, 12, 18], fill=N6)
    px(draw, 7, 14, INK); px(draw, 10, 14, INK)
    draw.line([(7, 17), (10, 17)], fill=RED[1])
    px(draw, 4, 11, RED[4])
    # A beckoning cat, one paw up, red collar.
    draw.ellipse([19, 12, 30, 23], fill=N6)
    draw.ellipse([20, 4, 30, 13], fill=N6)
    draw.polygon([(20, 6), (21, 2), (23, 5)], fill=N6)
    draw.polygon([(27, 5), (29, 2), (30, 6)], fill=N6)
    px(draw, 22, 3, RED[4]); px(draw, 29, 3, RED[4])
    draw.ellipse([30, 6, 33, 11], fill=N6)                                          # the raised paw
    px(draw, 23, 8, INK); px(draw, 27, 8, INK)
    px(draw, 25, 10, RED[3])
    draw.line([(21, 13), (29, 13)], fill=RED[3])
    px(draw, 25, 14, OCHRE[2])
    draw.ellipse([22, 16, 27, 20], fill=N5)
    # Three capsules.
    for x, top_colour in ((36, GREEN[1]), (44, OCHRE[1]), (40, RED[3])):
        y = 17 if x != 40 else 12
        draw.ellipse([x, y, x + 6, y + 6], fill=N6)
        draw.pieslice([x, y, x + 6, y + 6], 180, 360, fill=top_colour)
        px(draw, x + 1, y + 1, N6)
    # A little tin robot.
    draw.rectangle([50, 12, 55, 22], fill=N4)
    draw.rectangle([51, 8, 54, 11], fill=N4)
    px(draw, 52, 9, RED[4]); px(draw, 53, 9, RED[4])
    draw.line([(52, 6), (52, 7)], fill=N3)
    draw.line([(51, 15), (54, 15)], fill=N3)
    px(draw, 52, 18, OCHRE[2])
    save("toy_shelf", outline(image))


def notice_board():
    image, draw = canvas(45, 33)
    draw.rectangle([0, 0, 44, 32], fill=UMBER[1])
    draw.line([(1, 1), (43, 1)], fill=UMBER[3])
    draw.rectangle([3, 3, 41, 29], fill=UMBER[3])                                   # cork
    seed = 7
    for y in range(3, 30):
        for x in range(3, 42):
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            if seed % 9 == 0:
                px(draw, x, y, UMBER[4] if seed % 2 else UMBER[2])
    for box, lines in (((6, 6, 18, 20), 5), ((22, 5, 37, 14), 3), ((24, 17, 38, 27), 3)):
        draw.rectangle(box, fill=N6)
        draw.line([(box[0], box[3]), (box[2], box[3])], fill=N5)
        for line in range(lines):
            y = box[1] + 3 + line * 2
            draw.line([(box[0] + 2, y), (box[2] - 2 - (line * 3) % 5, y)], fill=N4)
    draw.rectangle([8, 22, 17, 28], fill=N5)                                        # a photo
    draw.rectangle([9, 23, 16, 27], fill=GREEN[1])
    draw.ellipse([11, 23, 14, 26], fill=N6)
    for x, y in ((12, 6), (29, 5), (31, 17), (12, 22)):                             # pins
        px(draw, x, y, RED[3]); px(draw, x, y - 1, RED[4])
    save("notice_board", outline(image))


def key_cabinet():
    image, draw = canvas(31, 37)
    draw.rectangle([0, 0, 30, 36], fill=UMBER[1])
    draw.line([(1, 1), (29, 1)], fill=UMBER[3])
    draw.rectangle([3, 3, 27, 33], fill=UMBER[0])
    for row, y in enumerate((8, 19, 30)):
        draw.line([(4, y - 3), (26, y - 3)], fill=UMBER[2])
        for column, x in enumerate((7, 13, 19, 24)):
            px(draw, x, y - 2, OCHRE[2])                                            # the hook
            if row == 0 and column == 2:
                # The manager's key: its hook is empty, its shape still on the board.
                draw.rectangle([x - 1, y, x + 1, y + 5], outline=UMBER[2])
                continue
            draw.ellipse([x - 2, y - 1, x + 2, y + 3], fill=OCHRE[1])
            px(draw, x, y + 1, UMBER[0])
            draw.line([(x, y + 3), (x, y + 6)], fill=OCHRE[1])
            px(draw, x + 1, y + 5, OCHRE[1])
            px(draw, x - 1, y, OCHRE[3])
    save("key_cabinet", outline(image))


def calendar():
    image, draw = canvas(19, 25)
    draw.rectangle([0, 2, 18, 24], fill=N6)
    draw.rectangle([0, 2, 18, 7], fill=RED[2])
    draw.line([(0, 2), (18, 2)], fill=RED[3])
    for x in (5, 13):
        draw.line([(x, 0), (x, 3)], fill=N3)
    for row in range(4):
        for column in range(5):
            x, y = 2 + column * 3, 10 + row * 3
            draw.rectangle([x, y, x + 1, y + 1], fill=N4 if (row * 5 + column) % 6 else RED[3])
    draw.ellipse([7, 15, 11, 19], outline=RED[3])                                   # tonight, circled
    draw.line([(1, 23), (17, 23)], fill=N5)
    save("calendar", outline(image))


def fire_extinguisher():
    image, draw = canvas(12, 27)
    draw.rectangle([2, 9, 9, 24], fill=RED[2])
    draw.ellipse([2, 6, 9, 12], fill=RED[2])
    draw.rectangle([2, 9, 4, 24], fill=RED[3])
    px(draw, 3, 8, RED[4])
    draw.rectangle([3, 14, 8, 18], fill=N6)
    draw.line([(4, 16), (7, 16)], fill=N4)
    draw.rectangle([4, 3, 7, 6], fill=N4)
    draw.line([(7, 3), (10, 1)], fill=N2)
    draw.line([(8, 5), (10, 9)], fill=SHADE)
    draw.rectangle([1, 24, 10, 26], fill=N3)                                        # the bracket
    save("fire_extinguisher", outline(image))


def mirror():
    image, draw = canvas(27, 36)
    draw.ellipse([0, 0, 26, 35], fill=OCHRE[0])
    draw.ellipse([0, 0, 25, 34], fill=OCHRE[1])
    draw.ellipse([3, 3, 23, 32], fill=MAUVE[1])
    draw.ellipse([4, 4, 22, 31], fill=MAUVE[2])
    draw.line([(8, 9), (12, 5)], fill=N6)
    draw.line([(8, 13), (15, 6)], fill=N5)
    draw.line([(16, 27), (19, 24)], fill=N5)
    save("mirror", outline(image))


def towel_rail():
    image, draw = canvas(30, 25)
    draw.line([(1, 2), (28, 2)], fill=N4)
    for x in (1, 28):
        draw.rectangle([x - 1, 0, x + 1, 4], fill=N3)
    draw.rectangle([6, 3, 22, 23], fill=N6)
    draw.rectangle([6, 3, 8, 23], fill=N5)
    for y in (15, 18):
        draw.line([(6, y), (22, y)], fill=RED[3])
    draw.line([(6, 22), (22, 22)], fill=N5)
    save("towel_rail", outline(image))


# --- Floor ----------------------------------------------------------------------------

def coat_rack():
    image, draw = canvas(30, 105)
    draw.rectangle([13, 8, 16, 98], fill=UMBER[2])
    draw.line([(13, 8), (13, 98)], fill=UMBER[3])
    for x0, x1 in ((4, 13), (16, 25)):                                              # the feet
        draw.polygon([(x0, 104), (x1, 96), (x1, 99), (x0 + 2, 104)], fill=UMBER[1])
    draw.ellipse([11, 2, 18, 9], fill=UMBER[3])
    for side in (-1, 1):                                                            # hooks
        draw.line([(15, 14), (15 + side * 8, 10)], fill=N4)
    # A bowler hat on one hook, a long olive coat on the other.
    draw.ellipse([0, 6, 12, 10], fill=SHADE)
    draw.ellipse([2, 0, 10, 8], fill=SHADE)
    draw.line([(3, 5), (9, 5)], fill=N3)
    draw.polygon([(17, 12), (25, 12), (28, 60), (16, 62)], fill=OLIVE[1])
    draw.polygon([(17, 12), (20, 12), (19, 61), (16, 62)], fill=OLIVE[2])
    draw.line([(22, 14), (23, 58)], fill=OLIVE[0])
    for y in (24, 34, 44):
        px(draw, 24, y, OCHRE[1])
    save("coat_rack", outline(image))


def umbrella_stand():
    image, draw = canvas(18, 39)
    draw.rectangle([2, 17, 15, 38], fill=OCHRE[0])
    draw.rectangle([2, 17, 6, 38], fill=OCHRE[1])
    draw.line([(2, 21), (15, 21)], fill=OCHRE[2])
    draw.line([(2, 34), (15, 34)], fill=OCHRE[2])
    draw.line([(10, 17), (11, 3)], fill=SHADE)                                      # the umbrella
    draw.arc([7, 0, 14, 7], 180, 360, fill=SHADE)
    draw.polygon([(7, 17), (14, 17), (12, 9), (9, 9)], fill=RED[2])
    draw.line([(10, 9), (10, 17)], fill=RED[1])
    save("umbrella_stand", outline(image))


def plant():
    image, draw = canvas(30, 51)
    draw.polygon([(7, 36), (22, 36), (20, 50), (9, 50)], fill=RUST[1])              # terracotta pot
    draw.polygon([(7, 36), (11, 36), (11, 50), (9, 50)], fill=RUST[2])
    draw.rectangle([6, 34, 23, 37], fill=RUST[2])
    draw.line([(6, 34), (23, 34)], fill=PEACH)
    leaves = [((14, 34), -1.2, 18), ((15, 34), -0.6, 26), ((15, 34), 0.05, 31), ((15, 34), 0.6, 25), ((16, 34), 1.15, 17),
              ((14, 34), -0.25, 22), ((16, 34), 0.35, 21)]
    for index, ((x, y), lean, length) in enumerate(leaves):
        tip = (x + math.sin(lean) * length, y - math.cos(lean) * length)
        side = (math.cos(lean) * 3, math.sin(lean) * 3)
        middle = (x + (tip[0] - x) * 0.55, y + (tip[1] - y) * 0.55)
        colour = [GREEN[1], OLIVE[1], GREEN[0], OLIVE[2], GREEN[1], OLIVE[1], GREEN[2]][index]
        draw.polygon([(x, y), (middle[0] - side[0], middle[1] - side[1]), tip, (middle[0] + side[0], middle[1] + side[1])], fill=colour)
        draw.line([(x, y), tip], fill=GREEN[0] if colour != GREEN[0] else OLIVE[0])
    save("plant", outline(image))


def side_table_radio():
    image, draw = canvas(36, 45)
    draw.rectangle([2, 22, 33, 25], fill=UMBER[2])                                  # table top
    draw.line([(2, 22), (33, 22)], fill=UMBER[3])
    for x in (5, 29):
        draw.rectangle([x, 26, x + 2, 44], fill=UMBER[1])
    draw.line([(7, 38), (29, 38)], fill=UMBER[1])
    # A cathedral radio.
    draw.rectangle([8, 6, 25, 21], fill=UMBER[2])
    draw.ellipse([8, 0, 25, 14], fill=UMBER[2])
    draw.ellipse([10, 3, 23, 14], fill=OCHRE[2])
    for x in range(12, 22, 3):                                                       # the cloth grille
        draw.line([(x, 5), (x, 14)], fill=OCHRE[0])
    draw.rectangle([10, 16, 23, 19], fill=UMBER[0])
    px(draw, 12, 17, OCHRE[3]); px(draw, 21, 17, OCHRE[3])
    draw.line([(15, 17), (18, 17)], fill=PEACH)
    # A mug, steam drawn as two light pixels.
    draw.rectangle([27, 15, 31, 21], fill=N6)
    draw.arc([30, 16, 33, 19], 270, 90, fill=N6)
    draw.line([(27, 16), (31, 16)], fill=RED[3])
    px(draw, 28, 12, N5); px(draw, 30, 10, N5)
    save("side_table_radio", outline(image))


# --- Reception ---------------------------------------------------------------------

def counter():
    """The counter, sized for the computer: 150 x 75 art pixels (100 x 50 world).
    Things stand on it at art row 10."""
    image, draw = canvas(150, 75)
    # The top: thick, worn boards, a lit front edge, a brass strip.
    draw.rectangle([0, 4, 149, 13], fill=UMBER[2])
    grain(draw, (1, 5, 147, 10), [UMBER[3], UMBER[1]], 3, 11)
    draw.line([(0, 4), (149, 4)], fill=UMBER[4])
    draw.rectangle([0, 11, 149, 13], fill=OCHRE[1])
    draw.line([(0, 11), (149, 11)], fill=OCHRE[3])
    # The front: dark wood, three raised panels with bevels.
    draw.rectangle([3, 14, 146, 68], fill=UMBER[1])
    for x in range(3, 147, 9):
        draw.line([(x, 14), (x, 68)], fill=UMBER[0])
    for left in (9, 57, 105):
        right = left + 36
        draw.rectangle([left, 19, right, 61], fill=UMBER[0])
        draw.rectangle([left + 1, 20, right, 61], fill=UMBER[2])
        draw.rectangle([left + 4, 23, right - 3, 58], fill=UMBER[1])
        draw.line([(left + 4, 23), (right - 3, 23)], fill=UMBER[0])
        draw.line([(left + 4, 23), (left + 4, 58)], fill=UMBER[0])
        draw.line([(left + 5, 58), (right - 3, 58)], fill=UMBER[3])
        grain(draw, (left + 6, 25, right - 5, 56), [UMBER[2], UMBER[0]], 4, left)
    # A brass coin set in the middle panel, with its laurel.
    cx, cy = 75, 40
    draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=OCHRE[0])
    draw.ellipse([cx - 10, cy - 10, cx + 9, cy + 9], fill=OCHRE[1])
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=OCHRE[2])
    draw.arc([cx - 9, cy - 9, cx + 8, cy + 8], 200, 280, fill=OCHRE[3])
    draw.line([(cx, cy - 4), (cx, cy + 4)], fill=OCHRE[0])
    px(draw, cx - 1, cy - 3, OCHRE[0])
    draw.line([(cx - 2, cy + 4), (cx + 2, cy + 4)], fill=OCHRE[0])
    for side in (-1, 1):
        for step in range(4):
            px(draw, cx + side * (14 + step % 2), cy + 6 - step * 4, GREEN[1])
            px(draw, cx + side * (15 + step % 2), cy + 5 - step * 4, GREEN[2])
    # Brass kick plate and skirting.
    draw.rectangle([3, 66, 146, 74], fill=UMBER[0])
    draw.rectangle([3, 66, 146, 68], fill=OCHRE[0])
    draw.line([(3, 66), (146, 66)], fill=OCHRE[2])
    for x in range(10, 146, 22):
        px(draw, x, 67, OCHRE[3])
    save("counter", outline(image))


def banker_lamp():
    image, draw = canvas(24, 24)
    draw.rectangle([5, 20, 18, 23], fill=OCHRE[0])
    draw.line([(5, 20), (18, 20)], fill=OCHRE[2])
    draw.line([(11, 19), (11, 12)], fill=OCHRE[1])
    draw.line([(11, 13), (8, 11)], fill=OCHRE[1])
    draw.polygon([(0, 10), (2, 5), (20, 5), (22, 10)], fill=GREEN[0])                # the shade
    draw.polygon([(2, 5), (20, 5), (19, 7), (3, 7)], fill=GREEN[1])
    draw.line([(3, 6), (18, 6)], fill=GREEN[2])
    draw.line([(1, 10), (21, 10)], fill=OCHRE[3])                                   # light under it
    px(draw, 15, 22, OCHRE[3])
    save("banker_lamp", outline(image))


def cash_register():
    image, draw = canvas(30, 27)
    draw.polygon([(2, 9), (27, 9), (29, 26), (0, 26)], fill=OCHRE[1])
    draw.polygon([(2, 9), (8, 9), (6, 26), (0, 26)], fill=OCHRE[2])
    draw.rectangle([6, 1, 23, 9], fill=OCHRE[0])                                    # the sign at the top
    draw.rectangle([8, 3, 21, 7], fill=SHADE)
    draw.rectangle([10, 4, 19, 6], fill=OCHRE[3])
    for row in range(3):
        for column in range(5):
            x, y = 6 + column * 4, 12 + row * 3
            draw.rectangle([x, y, x + 2, y + 1], fill=N6 if (row + column) % 3 else RED[4])
    draw.rectangle([1, 22, 28, 26], fill=OCHRE[0])                                  # the drawer
    draw.line([(12, 24), (17, 24)], fill=OCHRE[3])
    draw.line([(28, 13), (29, 9)], fill=N4)
    save("cash_register", outline(image))


def lucky_cat():
    image, draw = canvas(15, 19)
    draw.ellipse([1, 8, 13, 18], fill=N6)
    draw.ellipse([2, 1, 12, 10], fill=N6)
    draw.polygon([(2, 3), (3, 0), (5, 2)], fill=N6)
    draw.polygon([(9, 2), (11, 0), (12, 3)], fill=N6)
    px(draw, 3, 1, RED[4]); px(draw, 10, 1, RED[4])
    draw.ellipse([11, 3, 14, 8], fill=N6)
    px(draw, 5, 5, INK); px(draw, 9, 5, INK)
    px(draw, 7, 7, RED[3])
    draw.line([(3, 10), (11, 10)], fill=RED[3])
    px(draw, 7, 11, OCHRE[2])
    draw.ellipse([4, 12, 10, 16], fill=OCHRE[2])                                    # the coin it holds
    px(draw, 6, 13, OCHRE[3])
    save("lucky_cat", outline(image))


def ledger_stack():
    image, draw = canvas(21, 13)
    for index, (y, colour) in enumerate(((9, RED[2]), (5, GREEN[0]), (1, UMBER[2]))):
        x = 1 + index % 2 * 2
        draw.rectangle([x, y, x + 16, y + 3], fill=colour)
        draw.line([(x + 1, y + 1), (x + 15, y + 1)], fill=N6)
        draw.line([(x, y + 3), (x + 16, y + 3)], fill=SHADE)
    save("ledger_stack", outline(image))


# --- Wall textures: laid over a room's wall colour, so mostly see-through ---------------

def wall_grain():
    """Boards: a seam every 12 art pixels, grain, a nail now and then. 36 x 48."""
    image = Image.new("RGBA", (36, 48), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    dark, light = (0, 0, 0, 70), (255, 240, 210, 26)
    for x in (0, 12, 24):
        draw.line([(x, 0), (x, 47)], fill=(0, 0, 0, 110))
        draw.line([(x + 1, 0), (x + 1, 47)], fill=light)
    seed = 3
    for x in range(36):
        if x % 12 in (0, 1):
            continue
        for y in range(48):
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            if seed % 11 == 0:
                draw.line([(x, y), (x, y + 2 + seed % 4)], fill=dark if seed % 3 else light)
    for x, y in ((6, 10), (18, 34), (30, 22)):
        draw.point((x, y), fill=(0, 0, 0, 150))
    draw.ellipse([15, 12, 19, 18], outline=(0, 0, 0, 60))                           # a knot
    image.save(os.path.join(OUT, "wall_grain.png"))


def dado_panels():
    """Raised panels for the lower wall, under its rail. 60 x 66."""
    image = Image.new("RGBA", (60, 66), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, 59, 65], fill=(0, 0, 0, 40))
    draw.rectangle([6, 6, 53, 57], fill=(0, 0, 0, 55))
    draw.line([(6, 6), (53, 6)], fill=(0, 0, 0, 120))
    draw.line([(6, 6), (6, 57)], fill=(0, 0, 0, 120))
    draw.line([(7, 57), (53, 57)], fill=(255, 240, 210, 50))
    draw.line([(53, 7), (53, 57)], fill=(255, 240, 210, 50))
    draw.rectangle([10, 10, 49, 53], fill=(0, 0, 0, 25))
    draw.line([(0, 0), (0, 65)], fill=(0, 0, 0, 90))
    draw.line([(0, 62), (59, 62)], fill=(0, 0, 0, 80))
    image.save(os.path.join(OUT, "dado_panels.png"))


def wall_tiles():
    """Small square tiles for the bathroom, with grout and a lit corner. 24 x 24."""
    image = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for x in (0, 12):
        draw.line([(x, 0), (x, 23)], fill=(0, 0, 0, 90))
    for y in (0, 12):
        draw.line([(0, y), (23, y)], fill=(0, 0, 0, 90))
    for x in (1, 13):
        for y in (1, 13):
            draw.line([(x, y), (x + 4, y)], fill=(255, 245, 225, 60))
            draw.line([(x, y), (x, y + 3)], fill=(255, 245, 225, 60))
            draw.point((x + 9, y + 9), fill=(0, 0, 0, 50))
    image.save(os.path.join(OUT, "wall_tiles.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for build in (clock, frame_landscape, frame_employee, bunting, toy_shelf, notice_board, key_cabinet, calendar,
                  fire_extinguisher, mirror, towel_rail, coat_rack, umbrella_stand, plant, side_table_radio, counter,
                  banker_lamp, cash_register, lucky_cat, ledger_stack, wall_grain, dado_panels, wall_tiles):
        build()
    print("wrote", OUT)
