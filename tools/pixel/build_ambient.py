"""Build the ambient-life animation sheets of GachaNight and their manifest.

Run: python tools/pixel/build_ambient.py
Outputs: assets/sprites/ambient/<name>.png and assets/sprites/ambient/anims.json,
plus review material in tools/pixel/previews/: amb_<name>.png (x4 contact
sheet, frames side by side), amb_<name>.gif (x4, real fps) and
amb_overview.png (first frame of everything). Deterministic. Exits non-zero
when the outputs do not match the art contract (section E).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from PIL import Image  # noqa: E402

import ambient_creatures as cr  # noqa: E402
import ambient_props as pr  # noqa: E402
from ambient_lib import contact_sheet, overview, save_gif, strip  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "assets", "sprites", "ambient")
PREVIEWS = os.path.join(HERE, "previews")

# name -> (generator, contract frame size). The first 26 are section E of the contract.
REQUIRED = [
    ("amb_maneki_neko", cr.maneki_neko, (26, 32)),
    ("amb_wall_clock", pr.wall_clock, (24, 36)),
    ("amb_ceiling_fan", pr.ceiling_fan, (56, 24)),
    ("amb_tv", pr.tv, (38, 44)),
    ("amb_neon_sign", pr.neon_sign, (72, 28)),
    ("amb_string_lights", pr.string_lights, (96, 14)),
    ("amb_lantern", pr.lantern, (20, 34)),
    ("amb_fish_bowl", cr.fish_bowl, (26, 26)),
    ("amb_tap_drip", pr.tap_drip, (10, 26)),
    ("amb_moth", cr.moth, (14, 12)),
    ("amb_mouse_run", cr.mouse_run, (22, 14)),
    ("amb_cat_sleep", cr.cat_sleep, (36, 22)),
    ("amb_plant_sway", pr.plant_sway, (24, 40)),
    ("amb_mug_steam", pr.mug_steam, (14, 24)),
    ("amb_radio", pr.radio, (30, 30)),
    ("amb_balloon", cr.balloon, (18, 44)),
    ("amb_windup_toy", cr.windup_toy, (18, 18)),
    ("amb_dust_motes", pr.dust_motes, (48, 48)),
    ("amb_exit_sign", pr.exit_sign, (30, 14)),
    ("amb_vending", pr.vending, (46, 86)),
    ("amb_koinobori", pr.koinobori, (64, 24)),
    ("amb_capsule_roll", pr.capsule_roll, (12, 12)),
    ("amb_spider", cr.spider, (12, 30)),
    ("amb_pinwheel", pr.pinwheel, (18, 30)),
    ("amb_arcade_cab", pr.arcade_cab, (40, 78)),
    ("amb_bubbles", pr.bubbles, (16, 32)),
]
EXTRAS = [
    ("amb_cuckoo_clock", cr.cuckoo_clock, (26, 40)),
    ("amb_toy_train", cr.toy_train, (36, 18)),
    ("amb_daruma", cr.daruma, (22, 24)),
    ("amb_robot_display", cr.robot_display, (22, 28)),
    ("amb_candle", pr.candle, (10, 20)),
    ("amb_music_notes", pr.music_notes, (16, 24)),
    ("amb_claw_mobile", pr.claw_mobile, (34, 30)),
    ("amb_furin", pr.furin, (12, 30)),
    ("amb_spinning_top", pr.spinning_top, (14, 14)),
    ("amb_calendar", pr.calendar, (18, 26)),
    ("amb_noren", pr.noren, (48, 22)),
    ("amb_teru_bozu", cr.teru_bozu, (14, 28)),
    ("amb_akabeko", cr.akabeko, (26, 20)),
    ("amb_jack_in_box", cr.jack_in_box, (20, 34)),
    ("amb_cymbal_monkey", cr.cymbal_monkey, (24, 26)),
    ("amb_rubber_duck", cr.rubber_duck, (18, 14)),
]
# Pixels that must be opaque and identical in every frame (the point the game pins).
FIXED = {
    "amb_ceiling_fan": [(27, 0), (28, 0)], "amb_lantern": [(10, 0)], "amb_balloon": [(9, 43)],
    "amb_spider": [(6, 0)], "amb_string_lights": [(0, 1), (95, 1)], "amb_claw_mobile": [(17, 0)],
    "amb_furin": [(6, 0)], "amb_koinobori": [(2, 23)], "amb_pinwheel": [(9, 29)],
    "amb_teru_bozu": [(7, 0)], "amb_noren": [(0, 1), (47, 1)], "amb_calendar": [(8, 0)],
}
# Floor-standing things: the bottom row must be touched in every frame.
GROUNDED = ["amb_maneki_neko", "amb_tv", "amb_cat_sleep", "amb_plant_sway", "amb_mug_steam", "amb_vending",
            "amb_arcade_cab", "amb_pinwheel", "amb_fish_bowl", "amb_daruma", "amb_robot_display", "amb_candle",
            "amb_akabeko", "amb_jack_in_box", "amb_cymbal_monkey", "amb_rubber_duck"]


def build():
    anims = {}
    errors = []
    for name, fn, size in REQUIRED + EXTRAS:
        try:
            frames, fps = fn()
        except ValueError as err:
            errors.append(str(err))
            continue
        anims[name] = (frames, fps)
    if errors:
        raise ValueError("\n  - " + "\n  - ".join(errors))
    return anims


def write(anims):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREVIEWS, exist_ok=True)
    manifest = {}
    for name, (frames, fps) in anims.items():
        w, h = frames[0].size
        strip(frames).save(os.path.join(OUT, name + ".png"))
        manifest[name] = {"file": name + ".png", "frame_w": w, "frame_h": h,
                          "frames": len(frames), "fps": fps, "loop": True}
        contact_sheet(frames).save(os.path.join(PREVIEWS, name + ".png"))
        save_gif(frames, os.path.join(PREVIEWS, name + ".gif"), fps)
    with open(os.path.join(OUT, "anims.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    overview([(n, f[0]) for n, (f, _) in anims.items()], os.path.join(PREVIEWS, "amb_overview.png"))
    return manifest


def verify():
    """Check the files on disk against the contract and the manifest."""
    problems = []
    path = os.path.join(OUT, "anims.json")
    if not os.path.exists(path):
        return ["anims.json is missing"], {}
    with open(path, encoding="utf-8") as fh:
        manifest = json.load(fh)
    sizes = {name: size for name, _, size in REQUIRED + EXTRAS}
    for name, _, (fw, fh_) in REQUIRED:
        if name not in manifest:
            problems.append("%s: required by the contract but missing from anims.json" % name)
    for name, e in manifest.items():
        missing = [k for k in ("file", "frame_w", "frame_h", "frames", "fps", "loop") if k not in e]
        if missing:
            problems.append("%s: manifest keys missing: %s" % (name, ", ".join(missing)))
            continue
        if not name.startswith("amb_"):
            problems.append("%s: ambient animation names must start with amb_" % name)
        if name in sizes and (e["frame_w"], e["frame_h"]) != sizes[name]:
            problems.append("%s: frame %dx%d, contract says %dx%d"
                            % (name, e["frame_w"], e["frame_h"], sizes[name][0], sizes[name][1]))
        if e["frames"] < 1 or e["fps"] <= 0:
            problems.append("%s: frames and fps must be positive" % name)
            continue
        sheet_path = os.path.join(OUT, e["file"])
        if not os.path.exists(sheet_path):
            problems.append("%s: sheet %s missing" % (name, e["file"]))
            continue
        img = Image.open(sheet_path)
        if img.mode != "RGBA":
            problems.append("%s: sheet is %s, expected RGBA" % (name, img.mode))
            continue
        if img.width != e["frame_w"] * e["frames"]:
            problems.append("%s: sheet width %d != frame_w %d * frames %d"
                            % (name, img.width, e["frame_w"], e["frames"]))
            continue
        if img.height != e["frame_h"]:
            problems.append("%s: sheet height %d != frame_h %d" % (name, img.height, e["frame_h"]))
            continue
        if sum(img.getchannel("A").histogram()[1:255]):
            problems.append("%s: alpha values other than 0/255" % name)
        cells = [img.crop((i * e["frame_w"], 0, (i + 1) * e["frame_w"], e["frame_h"])) for i in range(e["frames"])]
        for i, cell in enumerate(cells):
            if cell.getchannel("A").getextrema()[1] == 0:
                problems.append("%s: frame %d is empty" % (name, i))
        if e["frames"] > 1 and len({cell.tobytes() for cell in cells}) < 2:
            problems.append("%s: every frame is identical" % name)
        for (x, y) in FIXED.get(name, []):
            vals = {cell.getpixel((x, y)) for cell in cells}
            if len(vals) != 1 or next(iter(vals))[3] != 255:
                problems.append("%s: fixed point (%d, %d) is not pixel-stable" % (name, x, y))
        if name in GROUNDED:
            for i, cell in enumerate(cells):
                row = cell.crop((0, e["frame_h"] - 1, e["frame_w"], e["frame_h"]))
                if row.getchannel("A").getextrema()[1] == 0:
                    problems.append("%s: frame %d does not touch the bottom row" % (name, i))
                    break
    return problems, manifest


def main():
    try:
        anims = build()
    except ValueError as err:
        print("PROBLEM while drawing: %s" % err)
        return 1
    write(anims)
    problems, manifest = verify()
    required = {n for n, _, _ in REQUIRED}
    for name, e in manifest.items():
        print("%-20s %2dx%-2d  %2d frames  %2d fps  %.2f s%s" % (
            name, e["frame_w"], e["frame_h"], e["frames"], e["fps"], e["frames"] / float(e["fps"]),
            "" if name in required else "  (extra)"))
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    print("OK: %d ambient animations, all %d required by the contract present and consistent"
          % (len(manifest), len(required)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
