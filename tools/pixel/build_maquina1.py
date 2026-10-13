"""The capsule machines, from the owner's picture `diseños/maquina1.png`.

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
EYE_BOX = (41, 26, 66, 43)
EYE_COLOURS = {(0xed, 0xde, 0xcc), (0xd3, 0xbd, 0xad), (0x2a, 0x19, 0x25)}
PUPIL = (0x2a, 0x19, 0x25)
INK = (0, 0, 0, 255)
# Rows of the eye the lid covers: open, half, shut.
LID_HALF = 34
LID_SHUT = EYE_BOX[3]
# Squash in pixels through one breath, then where the blinks fall.
BREATH = [0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 1, 1]
FRAMES = 36
BLINK = {20: LID_HALF, 21: LID_SHUT, 22: LID_HALF}
FPS = 8
# Capsule Machine No. 2: the body's rust to grey-green and olive.
SWAP = {(0x5e, 0x34, 0x24): (0x4a, 0x55, 0x46), (0x8a, 0x4e, 0x30): (0x74, 0x80, 0x6c), (0xb0, 0x70, 0x4a): (0x97, 0x9a, 0x72)}
LID = (0x8a, 0x4e, 0x30, 255)
LID_SWAPPED = (0x74, 0x80, 0x6c, 255)


def eye_pixels(picture):
    """Pixels that are the inside of an eye: its whites, and the pupil pixels joined to them."""
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
    return sorted(found)


def with_lids(picture, eyes, down_to, lid):
    """The picture with its lids lowered to row `down_to`."""
    out = picture.copy()
    pixels = out.load()
    for x, y in eyes:
        if y < down_to:
            pixels[x, y] = lid
        elif y == down_to:
            pixels[x, y] = INK
    return out


def squashed(picture, by):
    """`picture` `by` pixels shorter, standing on the same floor."""
    if by == 0:
        return picture
    frame = Image.new("RGBA", picture.size, (0, 0, 0, 0))
    frame.alpha_composite(picture.resize((picture.width, picture.height - by), Image.NEAREST), (0, by))
    return frame


def build(name, picture, eyes, lid, manifest):
    with_lids(picture, eyes, LID_SHUT, lid).save(os.path.join(OUT, name + ".png"))
    sheet = Image.new("RGBA", (picture.width * FRAMES, picture.height), (0, 0, 0, 0))
    for index in range(FRAMES):
        frame = with_lids(picture, eyes, BLINK[index], lid) if index in BLINK else picture
        sheet.alpha_composite(squashed(frame, BREATH[index % len(BREATH)]), (index * picture.width, 0))
    sheet.save(os.path.join(OUT, name + "_idle.png"))
    manifest[name + "_idle"] = {"file": name + "_idle.png", "fps": FPS, "frame_h": picture.height, "frame_w": picture.width,
                                "frames": FRAMES, "loop": True}


def main():
    drawn = Image.open(glob.glob(os.path.join("dise*", "maquina1.png"))[0]).convert("RGBA")
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
