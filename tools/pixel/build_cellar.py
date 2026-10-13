"""The cellar's poker table: two mice playing cards by a candle.

A rough first pass drawn straight in world pixels (one sprite pixel per world
pixel), to try the scene. The flame is not in the picture: the store draws it,
so it can flicker. Run from the repository root:

    py -3.13 tools/pixel/build_cellar.py
"""
import os

from PIL import Image, ImageDraw

OUT = os.path.join("assets", "sprites", "props", "poker_table.png")
SIZE = (92, 50)
INK = (20, 12, 10, 255)
FUR = (34, 24, 22, 255)
FUR_LIGHT = (62, 46, 40, 255)
MUZZLE = (232, 210, 168, 255)
GLOVE = (241, 232, 208, 255)
CARD = (241, 230, 200, 255)
CARD_RED = (176, 52, 38, 255)
WOOD = (138, 90, 52, 255)
WOOD_LIGHT = (185, 130, 74, 255)
WOOD_DARK = (88, 54, 32, 255)
SHOE = (120, 62, 34, 255)
BRASS = (201, 152, 46, 255)
WAX = (236, 224, 196, 255)
VISOR = (58, 122, 88, 255)
CHIP_BLUE = (56, 130, 140, 255)


def mouse(draw):
    """The left player, facing right, sitting on a stool."""
    draw.rectangle([8, 37, 16, 38], fill=WOOD_LIGHT)                      # stool
    draw.rectangle([11, 39, 13, 48], fill=WOOD_DARK)
    draw.line([(5, 35), (2, 31), (3, 27)], fill=FUR, width=1)             # tail
    draw.ellipse([5, 21, 19, 37], fill=FUR)                               # body
    draw.ellipse([7, 23, 12, 30], fill=FUR_LIGHT)
    draw.line([(14, 36), (21, 40), (21, 45)], fill=FUR, width=2)          # leg
    draw.ellipse([19, 44, 26, 48], fill=SHOE)
    draw.ellipse([6, 3, 14, 11], fill=FUR)                                # ears
    draw.ellipse([15, 1, 23, 9], fill=FUR)
    draw.ellipse([9, 6, 23, 20], fill=FUR)                                # head
    draw.ellipse([15, 11, 25, 20], fill=MUZZLE)
    draw.rectangle([19, 13, 20, 15], fill=INK)                            # eye
    draw.rectangle([25, 14, 26, 15], fill=INK)                            # nose
    draw.line([(19, 18), (23, 17)], fill=INK, width=1)                    # mouth
    draw.line([(16, 26), (24, 27), (28, 24)], fill=FUR, width=2)          # arm
    for index, x in enumerate((27, 30, 33)):                              # a fan of cards
        draw.rectangle([x, 15 + index % 2, x + 4, 22 + index % 2], fill=CARD, outline=INK)
    draw.point((29, 18), fill=CARD_RED)
    draw.point((35, 18), fill=CARD_RED)
    draw.ellipse([27, 22, 31, 26], fill=GLOVE)                            # glove


def build():
    half = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    mouse(ImageDraw.Draw(half))
    image = Image.alpha_composite(half, half.transpose(Image.FLIP_LEFT_RIGHT))
    draw = ImageDraw.Draw(image)
    draw.rectangle([64, 5, 74, 6], fill=VISOR)                            # the right one wears a dealer's visor
    draw.rectangle([62, 7, 66, 8], fill=VISOR)
    draw.rectangle([24, 28, 67, 31], fill=WOOD)                           # table top
    draw.rectangle([24, 28, 67, 28], fill=WOOD_LIGHT)
    draw.rectangle([44, 32, 47, 45], fill=WOOD_DARK)                      # pedestal
    draw.rectangle([38, 46, 53, 48], fill=WOOD_DARK)
    draw.rectangle([43, 26, 48, 27], fill=BRASS)                          # candle holder
    draw.rectangle([45, 19, 46, 25], fill=WAX)                            # candle
    draw.rectangle([37, 25, 39, 27], fill=CARD_RED)                       # chips
    draw.rectangle([40, 26, 42, 27], fill=CHIP_BLUE)
    draw.rectangle([52, 24, 54, 27], fill=BRASS)
    draw.rectangle([56, 26, 61, 27], fill=CARD)                           # a card face down
    # One ink line around everything.
    pixels = image.load()
    edge = []
    for y in range(SIZE[1]):
        for x in range(SIZE[0]):
            if pixels[x, y][3] != 0:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < SIZE[0] and 0 <= ny < SIZE[1] and pixels[nx, ny][3] != 0:
                    edge.append((x, y))
                    break
    for x, y in edge:
        pixels[x, y] = INK
    image.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
