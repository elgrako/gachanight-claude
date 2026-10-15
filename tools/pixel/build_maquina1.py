"""The capsule machines, from the owner's picture `diseños/maquina bolas/maquina bolas 2.0.png`
(version 2.0; 1.0 is kept beside it, and the x2 and x4 files are the same
picture scaled up, which this game does not need: the machine is standard
density, 81 x 128, see docs/art/pixel-density.md).

Its drawing is kept pixel for pixel; its colours are moved to the game's
palette (`palette.py`), which is browner than the picture. From it:

    machine_001.png        asleep: the same machine with its eyes shut (no power)
    machine_001_idle.png   awake: it breathes (a pixel or two of squash on a
                           slow beat) and blinks now and then
    machine_002.png / _idle.png   the same machine with its red body turned
                           grey-green, for Capsule Machine No. 2, until the
                           owner draws that one

and the two idle entries of `assets/sprites/machines/anims.json`.

Run from the repository root:

    py -3.13 tools/pixel/build_maquina1.py
"""
import glob
import json
import os

from PIL import Image

from palette import remap

OUT = os.path.join("assets", "sprites", "machines")
# Inside of the two eyes: whites and pupils, in the picture's own colours.
EYE_BOX = (37, 22, 63, 42)
EYE_COLOURS = {(0xed, 0xde, 0xcc), (0xd3, 0xbd, 0xad), (0xdc, 0xc1, 0xb2), (0x2a, 0x19, 0x25)}
PUPIL = (0x2a, 0x19, 0x25)
INK = (0, 0, 0, 255)
# Rows of the eye the lid covers: open, half, shut.
LID_HALF = 32
LID_SHUT = EYE_BOX[3]
# Squash in pixels through one breath, then where the blinks fall.
# The idle, blocked out as key poses with holds and one in-between each way
# (docs/art/animation-techniques.md): rest, breathe out (squash, held), rest,
# breathe in (stretch, held), rest; the blink falls in the long rest. Rows of
# squash (+) or stretch (-); the width changes the other way, so the machine
# keeps its volume.
BREATH = [0] * 8 + [1, 2, 2, 2, 1] + [0] * 3 + [-1, -2, -2, -2, -2, -1] + [0] * 14
FRAMES = len(BREATH)
BLINK = {27: LID_HALF, 28: LID_SHUT, 29: LID_HALF}
# Rows of room left above the picture for the stretch.
HEADROOM = 3
FPS = 8
# Capsule Machine No. 2: the body's reds (as the palette leaves them) turned
# grey-green and olive, step for step.
SWAP = {(0x3e, 0x1a, 0x1a): (0x2a, 0x27, 0x22), (0x5e, 0x2a, 0x26): (0x4a, 0x55, 0x46), (0x80, 0x38, 0x2f): (0x74, 0x80, 0x6c),
        (0xa1, 0x4d, 0x3e): (0x9f, 0xa6, 0x8e), (0xbf, 0x6d, 0x55): (0xc9, 0xbb, 0x9f)}
LID = (0xa1, 0x4d, 0x3e, 255)
LID_SWAPPED = (0x74, 0x80, 0x6c, 255)


def eye_pixels(picture):
    """What the lids cover, found on the owner's own colours: {(row, eye):
    (first x, last x)}. The inside of an eye is its whites and the pupil
    pixels joined to them; on each row a pupil that sits against the eye's
    edge, past its last white pixel, is taken in up to the outline (the last
    dark pixel before whatever lies outside the eye)."""
    pixels = picture.load()
    inside = lambda x, y: EYE_BOX[0] <= x <= EYE_BOX[2] and EYE_BOX[1] <= y <= EYE_BOX[3]
    stack = [(x, y) for y in range(EYE_BOX[1], EYE_BOX[3] + 1) for x in range(EYE_BOX[0], EYE_BOX[2] + 1)
             if pixels[x, y][:3] in EYE_COLOURS and pixels[x, y][:3] != PUPIL]
    found = set(stack)
    while stack:
        x, y = stack.pop()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if inside(nx, ny) and (nx, ny) not in found and pixels[nx, ny][:3] in EYE_COLOURS:
                found.add((nx, ny))
                stack.append((nx, ny))
    middle = (EYE_BOX[0] + EYE_BOX[2]) / 2.0
    rows = {}
    for x, y in found:
        side = 0 if x < middle else 1
        low, high = rows.get((y, side), (x, x))
        rows[(y, side)] = (min(low, x), max(high, x))
    dark = {(0, 0, 0), PUPIL}
    eye = EYE_COLOURS | {(0, 0, 0)}
    solid = lambda x, y, wanted: pixels[x, y][3] > 0 and pixels[x, y][:3] in wanted
    for (y, side), (low, high) in list(rows.items()):
        start_high, start_low = high, low
        while high - start_high < 8 and solid(high + 1, y, dark) and solid(high + 2, y, eye):
            high += 1
        while start_low - low < 8 and solid(low - 1, y, dark) and solid(low - 2, y, eye):
            low -= 1
        rows[(y, side)] = (low, high)
    return rows


def with_lids(picture, rows, down_to, lid):
    """The picture with its lids lowered to row `down_to`: each row of each eye
    filled from its first inside pixel to its last, the bottom row in ink."""
    out = picture.copy()
    pixels = out.load()
    for (y, _side), (low, high) in rows.items():
        if y > down_to:
            continue
        for x in range(low, high + 1):
            pixels[x, y] = lid if y < down_to else INK
    return out


def squashed(picture, by):
    """`picture` `by` art pixels shorter (or taller, if `by` < 0) and as many
    wider (or narrower), standing on the same floor and centred: squash and
    stretch at constant volume, in whole art pixels."""
    if by == 0:
        return picture
    box = picture.getbbox()
    body = picture.crop(box)
    body = body.resize((body.width + by, body.height - by), Image.NEAREST)
    frame = Image.new("RGBA", picture.size, (0, 0, 0, 0))
    frame.alpha_composite(body, (box[0] - by // 2, box[3] - body.height))
    return frame


def build(name, picture, eyes, lid, manifest):
    room = Image.new("RGBA", (picture.width, picture.height + HEADROOM), (0, 0, 0, 0))
    room.alpha_composite(picture, (0, HEADROOM))
    picture = room
    eyes = {(y + HEADROOM, side): span for (y, side), span in eyes.items()}
    with_lids(picture, eyes, LID_SHUT + HEADROOM, lid).save(os.path.join(OUT, name + ".png"))
    sheet = Image.new("RGBA", (picture.width * FRAMES, picture.height), (0, 0, 0, 0))
    for index in range(FRAMES):
        frame = with_lids(picture, eyes, BLINK[index] + HEADROOM, lid) if index in BLINK else picture
        sheet.alpha_composite(squashed(frame, BREATH[index % len(BREATH)]), (index * picture.width, 0))
    sheet.save(os.path.join(OUT, name + "_idle.png"))
    manifest[name + "_idle"] = {"file": name + "_idle.png", "fps": FPS, "frame_h": picture.height, "frame_w": picture.width,
                                "frames": FRAMES, "loop": True}


def main():
    drawn = Image.open(glob.glob(os.path.join("dise*", "maquina bolas", "maquina bolas 2.0.png"))[0]).convert("RGBA")
    eyes = eye_pixels(drawn)                                  # found on the owner's own colours
    picture = remap(drawn)
    swapped = picture.copy()
    pixels = swapped.load()
    for y in range(swapped.height):
        for x in range(swapped.width):
            colour = pixels[x, y]
            if colour[3] and colour[:3] in SWAP:
                pixels[x, y] = SWAP[colour[:3]] + (colour[3],)
    path = os.path.join(OUT, "anims.json")
    with open(path, encoding="utf-8") as handle:
        manifest = json.load(handle)
    build("machine_001", picture, eyes, LID, manifest)
    build("machine_002", swapped, eyes, LID_SWAPPED, manifest)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("wrote machine_001 and machine_002 from the owner's picture", picture.size)


if __name__ == "__main__":
    main()
