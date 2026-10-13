"""Moves the generated art onto the game's palette (`palette.py`), in place.

Run it after any generator that writes into `assets/sprites`. It leaves alone
what is built from the owner's own pictures, which carry their own colours or
are remapped by their own builder: the protagonist (never touched), the HUD
coin, the two capsule machines and the reception computer.

    py -3.13 tools/pixel/apply_palette.py
"""
import glob
import os

from PIL import Image

from palette import remap

ROOT = os.path.join("assets", "sprites")
SKIP = ("peseta" + os.sep, "ui" + os.sep, os.path.join("machines", "machine_001"), os.path.join("machines", "machine_002"),
        os.path.join("props", "pc_"))


def main():
    done = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "**", "*.png"), recursive=True)):
        inside = os.path.relpath(path, ROOT)
        if any(inside.startswith(prefix) for prefix in SKIP):
            continue
        picture = Image.open(path)
        mapped = remap(picture)
        if mapped.tobytes() != picture.convert("RGBA").tobytes():
            mapped.save(path)
            done += 1
    print("remapped", done, "pictures")


if __name__ == "__main__":
    main()
