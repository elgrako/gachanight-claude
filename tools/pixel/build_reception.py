"""The reception: the owner's computer and an old wooden counter.

Computer: `diseños/ordenador.png` and `diseños/ordenador_kawai.png` are the
owner's own pictures. They are copied as they are (trimmed), and a third one
with the screen dark is made from the first for when the store has no power.

    assets/sprites/props/pc_on.png      the computer, awake
    assets/sprites/props/pc_kawai.png   the same, delighted
    assets/sprites/props/pc_off.png     the same, screen dark

Counter: drawn here in world pixels, old dark wood with recessed panels and a
brass coin set in the middle one: an old cartoon's shop counter. No lettering:
Japanese text is not to be drawn without the owner checking it.

    assets/sprites/props/counter_wood.png

Run from the repository root:

    py -3.13 tools/pixel/build_reception.py
"""
import glob
import os

from PIL import Image, ImageDraw

OUT = os.path.join("assets", "sprites", "props")
INK = (20, 12, 10, 255)
TOP = (150, 100, 58, 255)
TOP_LIGHT = (188, 134, 80, 255)
TOP_DARK = (112, 72, 42, 255)
WOOD = (104, 64, 38, 255)
WOOD_LIGHT = (136, 88, 52, 255)
WOOD_DARK = (70, 42, 26, 255)
PANEL = (84, 50, 30, 255)
SKIRT = (48, 28, 18, 255)
PLAQUE = (232, 214, 172, 255)
BRASS = (201, 152, 46, 255)
BRASS_LIGHT = (240, 206, 110, 255)
BRASS_DARK = (140, 96, 30, 255)
COUNTER_SIZE = (100, 50)


def computer():
    awake = Image.open(glob.glob(os.path.join("dise*", "ordenador.png"))[0]).convert("RGBA")
    kawai = Image.open(glob.glob(os.path.join("dise*", "ordenador_kawai.png"))[0]).convert("RGBA")
    # Dark screen: the eyes are the light shapes wholly inside the glass.
    pixels = awake.load()
    counts = {}
    for y in range(awake.height):
        for x in range(awake.width):
            p = pixels[x, y]
            if p[3] and sum(p[:3]) < 150:
                counts[p] = counts.get(p, 0) + 1
    glass = max(counts, key=counts.get)
    off = awake.copy()
    out = off.load()
    seen = set()
    for y in range(awake.height):
        for x in range(awake.width):
            if (x, y) in seen or pixels[x, y] == glass or pixels[x, y][3] == 0:
                continue
            # One patch of non-glass pixels; it is an eye if only glass surrounds it.
            patch, stack, enclosed = [], [(x, y)], True
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop()
                patch.append((cx, cy))
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if not (0 <= nx < awake.width and 0 <= ny < awake.height) or pixels[nx, ny][3] == 0:
                        enclosed = False
                        continue
                    if pixels[nx, ny] != glass and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            if enclosed and len(patch) < 600:
                for cx, cy in patch:
                    out[cx, cy] = glass
    box = awake.getbbox()
    for name, picture in (("pc_on", awake), ("pc_kawai", kawai), ("pc_off", off)):
        # The same crop for all three, so they swap without moving.
        picture.crop((box[0], 0, box[2], box[3])).save(os.path.join(OUT, name + ".png"))
    print("wrote pc_on, pc_kawai, pc_off", (box[2] - box[0], box[3]))


def counter():
    width, height = COUNTER_SIZE
    image = Image.new("RGBA", COUNTER_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # The top, seen a little from above: worn boards with a lit front edge.
    draw.rectangle([0, 6, width - 1, 16], fill=INK)
    draw.rectangle([1, 7, width - 2, 13], fill=TOP)
    draw.rectangle([1, 7, width - 2, 7], fill=TOP_LIGHT)
    draw.rectangle([1, 14, width - 2, 15], fill=TOP_DARK)
    for x, y, length in ((6, 9, 22), (34, 11, 16), (58, 9, 12), (74, 12, 18), (16, 12, 9)):
        draw.line([(x, y), (x + length, y)], fill=TOP_DARK)
    for x, y in ((30, 9), (66, 11), (90, 9)):
        draw.point((x, y), fill=TOP_LIGHT)
    # The front: planks, three recessed panels, a skirting board.
    draw.rectangle([2, 16, width - 3, height - 1], fill=INK)
    draw.rectangle([3, 17, width - 4, height - 6], fill=WOOD)
    draw.rectangle([3, 17, width - 4, 17], fill=WOOD_DARK)
    for x in range(3, width - 3, 12):
        draw.line([(x, 18), (x, height - 6)], fill=WOOD_DARK)
    for left in (7, 37, 67):
        draw.rectangle([left, 21, left + 25, 40], fill=WOOD_LIGHT)
        draw.rectangle([left + 1, 22, left + 25, 40], fill=WOOD_DARK)
        draw.rectangle([left + 2, 23, left + 24, 39], fill=PANEL)
        draw.line([(left + 4, 27), (left + 12, 27)], fill=WOOD_DARK)
        draw.line([(left + 10, 34), (left + 21, 34)], fill=WOOD_DARK)
    draw.rectangle([2, height - 5, width - 3, height - 2], fill=SKIRT)
    draw.rectangle([2, height - 5, width - 3, height - 5], fill=WOOD_DARK)
    # A brass coin set into the middle panel.
    draw.ellipse([42, 23, 57, 38], fill=INK)
    draw.ellipse([43, 24, 56, 37], fill=BRASS)
    draw.ellipse([45, 26, 54, 35], fill=BRASS_DARK)
    draw.ellipse([45, 26, 53, 34], fill=BRASS)
    draw.arc([44, 25, 55, 36], 200, 290, fill=BRASS_LIGHT)
    draw.rectangle([49, 28, 50, 33], fill=INK)
    draw.point((48, 29), fill=INK)
    draw.rectangle([48, 33, 51, 33], fill=INK)
    # A brass bell on the top.
    draw.ellipse([82, 2, 92, 12], fill=INK)
    draw.pieslice([83, 3, 91, 13], 180, 360, fill=BRASS)
    draw.rectangle([83, 8, 91, 9], fill=BRASS_DARK)
    draw.point((85, 5), fill=BRASS_LIGHT)
    draw.point((86, 4), fill=BRASS_LIGHT)
    draw.rectangle([86, 1, 88, 2], fill=INK)
    draw.rectangle([81, 10, 93, 11], fill=INK)
    image.save(os.path.join(OUT, "counter_wood.png"))
    print("wrote counter_wood", COUNTER_SIZE)


if __name__ == "__main__":
    computer()
    counter()
