"""The protagonist's walk, from the owner's frames in `diseños/moneda/walking animation/`.

NOT IN USE (owner, 2026-10-15): tried in the game and turned down, the leg
rises and hangs at a middle point. The walk and run in the game are the rig
strips of build_peseta.py again. Kept for a looping set of frames later;
running it would overwrite those strips.

The owner made the thirteen frames with an animation generator. They are not
a loop: the first three go from the hat-tipping pose into the walk, and the
coin keeps turning a little from frame to frame, so the last frame does not
lead back to any earlier one. Until the owner has a looping set, the walk is
frames 3 to 12 played forward and then back (ping-pong), which never jumps.

The frames are used as drawn, colours untouched, on the same 232 x 222
canvas and anchor as the other `peseta_*` strips. Facing left is the mirror
image with the "1" and "PESETA" of the coin turned back the right way round:
each is placed in every frame by where the coin's face is (matched against
frame 3, as the face is never covered), and only the
coin's own pixels are copied back, so a hand over the word stays a hand.

    assets/sprites/peseta/peseta_walk.png, peseta_walk_left.png
    assets/sprites/peseta/peseta_run.png, peseta_run_left.png   (the same, faster)
    and their entries in assets/sprites/peseta/anims.json

Run from the repository root:

    py -3.13 tools/pixel/build_peseta_walk.py
"""
import glob
import json
import os

from PIL import Image, ImageChops, ImageStat

OUT = os.path.join("assets", "sprites", "peseta")
FRAME = (232, 222)
# Where the owner's 185 x 202 frame sits on that canvas: the same as the
# picture the other strips were built from.
OFFSET = (24, 22)
LOOP = list(range(3, 13)) + list(range(11, 3, -1))
# The game speeds these up with the ground speed (about 2.2 times when walking,
# 1.4 when running: player.gd), so the walk shows about 13 frames a second.
WALK_FPS = 6
RUN_FPS = 12
# The lettering on the coin in frame 3 ("1", then "PESETA"), and how far it
# may have moved in another frame.
LETTERING = [(115, 93, 129, 119), (73, 118, 125, 137)]
# The coin's eyes and nose in frame 3: never covered, so they place the coin.
FACE = (75, 45, 135, 95)
SEARCH = 40


def find(frame, template, box):
    """Top left of `template` in `frame`: the spot near `box` that matches best."""
    best = None
    w, h = template.size
    for y in range(box[1] - SEARCH // 2, box[1] + SEARCH // 2):
        for x in range(box[0] - 8, box[0] + SEARCH + 20):
            if x < 0 or y < 0 or x + w > frame.width or y + h > frame.height:
                continue
            score = sum(ImageStat.Stat(ImageChops.difference(frame.crop((x, y, x + w, y + h)), template)).mean[:3])
            if best is None or score < best[0]:
                best = (score, x, y)
    return best[1], best[2]


def facing_left(frame, found, coin_colours):
    """The frame mirrored, with its lettering put back the right way round.
    `found` is [(x, y, w, h)] per piece of lettering; only pixels that are the
    coin's own colours on both sides are copied, so hands are left alone."""
    mirrored = frame.transpose(Image.FLIP_LEFT_RIGHT)
    source = frame.load()
    target = mirrored.load()
    for x, y, w, h in found:
        for dy in range(h):
            for dx in range(w):
                from_pixel = source[x + dx, y + dy]
                to_x = frame.width - 1 - (x + dx)
                if from_pixel[:3] in coin_colours and target[to_x, y + dy][:3] in coin_colours:
                    target[to_x, y + dy] = from_pixel
    return mirrored


def strip(frames):
    sheet = Image.new("RGBA", (FRAME[0] * len(frames), FRAME[1]), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, (index * FRAME[0], 0))
    return sheet


def main():
    paths = sorted(glob.glob(os.path.join("dise*", "moneda", "walking animation", "*.png")))
    drawn = [Image.open(path).convert("RGBA") for path in paths]
    templates = [drawn[3].crop(box) for box in LETTERING]
    face = drawn[3].crop(FACE)
    # The coin's face and lettering colours: whatever frame 3 has where its
    # lettering is, which no hand covers there.
    coin_colours = set()
    for template in templates:
        coin_colours |= {pixel[:3] for pixel in template.get_flattened_data() if pixel[3] == 255}
    right, left = [], []
    for index in LOOP:
        canvas = Image.new("RGBA", FRAME, (0, 0, 0, 0))
        canvas.alpha_composite(drawn[index], OFFSET)
        right.append(canvas)
        x, y = find(drawn[index], face, FACE)
        shift = (x - FACE[0], y - FACE[1])
        found = [(box[0] + shift[0], box[1] + shift[1], box[2] - box[0], box[3] - box[1]) for box in LETTERING]
        canvas_left = Image.new("RGBA", FRAME, (0, 0, 0, 0))
        mirrored = facing_left(drawn[index], found, coin_colours)
        canvas_left.alpha_composite(mirrored, (FRAME[0] - OFFSET[0] - drawn[index].width, OFFSET[1]))
        left.append(canvas_left)
    path = os.path.join(OUT, "anims.json")
    with open(path, encoding="utf-8") as handle:
        manifest = json.load(handle)
    for name, frames, fps in (("peseta_walk", right, WALK_FPS), ("peseta_walk_left", left, WALK_FPS),
                              ("peseta_run", right, RUN_FPS), ("peseta_run_left", left, RUN_FPS)):
        strip(frames).save(os.path.join(OUT, name + ".png"))
        manifest[name] = {"file": name + ".png", "fps": fps, "frame_h": FRAME[1], "frame_w": FRAME[0],
                          "frames": len(frames), "loop": True}
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("walk and run from %d owner frames, %d in the loop" % (len(drawn), len(LOOP)))


if __name__ == "__main__":
    main()
