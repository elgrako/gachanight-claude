"""Build every animated sprite sheet of GachaNight plus the anims.json manifest.

Run: python tools/pixel/build_anims.py
Outputs: assets/sprites/anim/<name>.png, assets/sprites/anim/anims.json and,
for review, tools/pixel/previews/anim_<name>.png (x4 contact sheet) and
tools/pixel/previews/anim_<name>.gif (x6, real fps). Deterministic.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from PIL import Image  # noqa: E402

import anim_fx  # noqa: E402
import anim_player  # noqa: E402
import anim_robot  # noqa: E402
from anim_lib import contact_sheet, save_gif, strip  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "assets", "sprites", "anim")
PREVIEWS = os.path.join(HERE, "previews")
PROPS = os.path.join(ROOT, "assets", "sprites", "props")

# Animation name -> frame size required by the art contract.
REQUIRED = {
    "player_idle": (24, 40), "player_walk": (24, 40), "player_run": (24, 40), "player_use": (24, 40),
    "player_sleep": (40, 24), "robot_idle": (20, 24), "robot_work": (20, 24),
    "coin_spin": (10, 10), "coin_pickup": (16, 24), "capsule_open": (32, 32), "sparkle": (16, 16),
    "rarity_burst": (48, 48), "zzz": (16, 16), "lamp_flicker": (32, 12), "screen_glow": (24, 22),
}


def build():
    anims = {}      # name -> (frames, fps, loop)
    notes = []

    anims["player_idle"] = anim_player.idle()
    anims["player_walk"] = anim_player.walk()
    anims["player_run"] = anim_player.run()
    frames, fps, loop, reach = anim_player.use()
    anims["player_use"] = (frames, fps, loop)
    notes.append("player_use: hand reaches furthest at frame index %d" % reach)
    notes.append("player_walk covers %d px per cycle, player_run %d px per cycle"
                 % (anim_player.WALK_STRIDE_PX, anim_player.RUN_STRIDE_PX))
    anims["player_sleep"] = anim_player.sleep()
    anims["robot_idle"] = anim_robot.idle()
    anims["robot_work"] = anim_robot.work()
    anims["coin_spin"] = anim_fx.coin_spin()
    anims["coin_pickup"] = anim_fx.coin_pickup()
    anims["capsule_open"] = anim_fx.capsule_open("coral")
    for colour in ("mint", "mustard", "teal", "gold"):          # extras, same timing
        anims["capsule_open_" + colour] = anim_fx.capsule_open(colour)
    anims["sparkle"] = anim_fx.sparkle()
    anims["rarity_burst"] = anim_fx.rarity_burst()
    anims["zzz"] = anim_fx.zzz()
    frames, fps, loop, source = anim_fx.lamp_flicker(PROPS)
    anims["lamp_flicker"] = (frames, fps, loop)
    notes.append("lamp_flicker: lamp shape taken from %s" % source)
    anims["screen_glow"] = anim_fx.screen_glow()
    return anims, notes


def write(anims):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREVIEWS, exist_ok=True)
    manifest = {}
    for name, (frames, fps, loop) in anims.items():
        w, h = frames[0].size
        strip(frames).save(os.path.join(OUT, name + ".png"))
        manifest[name] = {"file": name + ".png", "frame_w": w, "frame_h": h,
                          "frames": len(frames), "fps": fps, "loop": bool(loop)}
        contact_sheet(frames).save(os.path.join(PREVIEWS, "anim_" + name + ".png"))
        save_gif(frames, os.path.join(PREVIEWS, "anim_" + name + ".gif"), fps, loop)
    with open(os.path.join(OUT, "anims.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    return manifest


def verify():
    """Check the files on disk against the contract and the manifest."""
    problems = []
    path = os.path.join(OUT, "anims.json")
    if not os.path.exists(path):
        return ["anims.json is missing"]
    with open(path, encoding="utf-8") as fh:
        manifest = json.load(fh)
    for name, (fw, fh_) in REQUIRED.items():
        if name not in manifest:
            problems.append("%s: required by the contract but missing from anims.json" % name)
        elif (manifest[name].get("frame_w"), manifest[name].get("frame_h")) != (fw, fh_):
            problems.append("%s: frame %sx%s, contract says %dx%d"
                            % (name, manifest[name].get("frame_w"), manifest[name].get("frame_h"), fw, fh_))
    for name, e in manifest.items():
        for key in ("file", "frame_w", "frame_h", "frames", "fps", "loop"):
            if key not in e:
                problems.append("%s: manifest key '%s' missing" % (name, key))
        if any(k not in e for k in ("file", "frame_w", "frame_h", "frames")):
            continue
        sheet_path = os.path.join(OUT, e["file"])
        if not os.path.exists(sheet_path):
            problems.append("%s: sheet %s missing" % (name, e["file"]))
            continue
        img = Image.open(sheet_path)
        if img.mode != "RGBA":
            problems.append("%s: sheet is %s, expected RGBA" % (name, img.mode))
            continue
        if e["frames"] < 1 or e.get("fps", 0) <= 0:
            problems.append("%s: frames and fps must be positive" % name)
        if img.width != e["frame_w"] * e["frames"]:
            problems.append("%s: sheet width %d != frame_w %d * frames %d"
                            % (name, img.width, e["frame_w"], e["frames"]))
        if img.height != e["frame_h"]:
            problems.append("%s: sheet height %d != frame_h %d" % (name, img.height, e["frame_h"]))
        hist = img.getchannel("A").histogram()
        if sum(hist[1:255]):
            problems.append("%s: alpha values other than 0/255" % name)
        for i in range(e["frames"]):
            box = (i * e["frame_w"], 0, (i + 1) * e["frame_w"], e["frame_h"])
            if img.width >= box[2] and img.crop(box).getchannel("A").getextrema()[1] == 0:
                problems.append("%s: frame %d is empty" % (name, i))
    return problems, manifest


def main():
    anims, notes = build()
    write(anims)
    result = verify()
    if isinstance(result, list):
        problems, manifest = result, {}
    else:
        problems, manifest = result
    for name, e in manifest.items():
        print("%-22s %2dx%-2d  %2d frames  %2d fps  %s%s" % (
            name, e["frame_w"], e["frame_h"], e["frames"], e["fps"],
            "loop" if e["loop"] else "once", "" if name in REQUIRED else "  (extra)"))
    for n in notes:
        print("note: " + n)
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    print("OK: %d animations, all %d required by the contract present and consistent"
          % (len(manifest), len(REQUIRED)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
