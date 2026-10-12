"""Build every character / effect animation sheet of GachaNight (art contract
v2, section C) plus assets/sprites/anim/anims.json.

Run: python tools/pixel/build_anims.py
Outputs: assets/sprites/anim/<name>.png, assets/sprites/anim/anims.json and,
for review, tools/pixel/previews/anim_<name>.png (x4 contact sheet, all frames
side by side) and tools/pixel/previews/anim_<name>.gif (x6, real fps).
Sheets and previews of animations that no longer exist are removed.
Deterministic. Exits non-zero when the outputs do not match the contract.
"""
import glob
import json
import os
import sys
import time

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

# Animation name -> (frame size, loop) required by the art contract, section C.
# loop None = the author's choice.
REQUIRED = {
    "player_idle": ((40, 56), True), "player_walk": ((40, 56), True), "player_run": ((40, 56), True),
    "player_use": ((40, 56), False), "player_cheer": ((40, 56), False), "player_sleep": ((56, 32), True),
    "robot_idle": ((28, 34), True), "robot_work": ((28, 34), True),
    "coin_spin": ((12, 12), True), "coin_pickup": ((20, 28), False),
    "capsule_open": ((40, 40), False), "capsule_open_blue": ((40, 40), False),
    "capsule_open_green": ((40, 40), False), "capsule_open_mustard": ((40, 40), False),
    "capsule_open_gold": ((40, 40), False),
    "sparkle": ((16, 16), False), "rarity_burst": ((64, 64), False), "zzz": ((16, 16), None),
    "dust_puff": ((16, 12), False), "coin_flip": ((12, 28), False), "speech_dots": ((20, 14), True),
}
# Animations whose feet must touch the bottom row in at least one frame.
GROUNDED = ("player_stretch", "player_shrug", "player_watch", "player_wave", "player_idle", "player_walk", "player_run", "player_use", "player_cheer", "player_sleep",
            "robot_idle", "robot_work")


def build():
    anims = {}      # name -> (frames, fps, loop)
    notes = []

    anims["player_idle"] = anim_player.idle()
    anims["player_walk"] = anim_player.walk()
    anims["player_run"] = anim_player.run()
    frames, fps, loop, reach, hand = anim_player.use()
    anims["player_use"] = (frames, fps, loop)
    notes.append("player_use: hand reaches furthest at frame index %d (glove centre at pixel %d, %d of the frame)"
                 % (reach, hand[0], hand[1]))
    for name, stride in (("player_walk", anim_player.WALK_STRIDE_PX), ("player_run", anim_player.RUN_STRIDE_PX)):
        f, fps_, _ = anims[name]
        notes.append("%s: %d px per cycle, %d frames at %d fps -> natural ground speed %.1f px/s"
                     % (name, stride, len(f), fps_, stride * fps_ / float(len(f))))
    anims["player_cheer"] = anim_player.cheer()
    anims["player_sleep"] = anim_player.sleep()
    anims["player_stretch"] = anim_player.stretch()      # extra
    anims["player_shrug"] = anim_player.shrug()          # extra
    anims["player_watch"] = anim_player.watch()          # extra
    anims["player_wave"] = anim_player.wave()            # extra
    anims["robot_idle"] = anim_robot.idle()
    anims["robot_work"] = anim_robot.work()
    c = anim_robot.WORK_CENTRE
    notes.append("robot_work: crank hand circles (radius %d) around pixel %d, %d of the frame = %+d px from the "
                 "centre line, %d px above the bottom edge" % (anim_robot.WORK_RADIUS, c[0], c[1],
                                                               c[0] - anim_robot.W // 2, anim_robot.H - c[1]))
    anims["coin_spin"] = anim_fx.coin_spin()
    anims["coin_pickup"] = anim_fx.coin_pickup()
    anims["coin_flip"] = anim_fx.coin_flip()
    anims["capsule_open"] = anim_fx.capsule_open("red")
    for colour in ("blue", "green", "mustard", "gold"):
        anims["capsule_open_" + colour] = anim_fx.capsule_open(colour)
    notes.append("capsule_open*: biggest flash at frame index %d" % anim_fx.CAPSULE_FLASH_FRAME)
    anims["sparkle"] = anim_fx.sparkle()
    anims["rarity_burst"] = anim_fx.rarity_burst()
    anims["zzz"] = anim_fx.zzz()
    anims["dust_puff"] = anim_fx.dust_puff()
    anims["speech_dots"] = anim_fx.speech_dots()
    return anims, notes


def save_image(img, path):
    """Save, retrying while another process (an editor re-importing) holds the file."""
    for attempt in range(8):
        try:
            img.save(path)
            return
        except OSError:
            if attempt == 7:
                raise
            time.sleep(0.25)


def remove(path):
    for p in (path, path + ".import"):
        if os.path.exists(p):
            os.remove(p)


def write(anims):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREVIEWS, exist_ok=True)
    manifest = {}
    for name, (frames, fps, loop) in anims.items():
        w, h = frames[0].size
        save_image(strip(frames), os.path.join(OUT, name + ".png"))
        manifest[name] = {"file": name + ".png", "frame_w": w, "frame_h": h,
                          "frames": len(frames), "fps": fps, "loop": bool(loop)}
        save_image(contact_sheet(frames), os.path.join(PREVIEWS, "anim_" + name + ".png"))
        save_gif(frames, os.path.join(PREVIEWS, "anim_" + name + ".gif"), fps, loop)
    with open(os.path.join(OUT, "anims.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    # drop sheets and previews of animations that are gone
    removed = []
    for path in glob.glob(os.path.join(OUT, "*.png")):
        if os.path.splitext(os.path.basename(path))[0] not in manifest:
            remove(path)
            removed.append(os.path.basename(path))
    for path in glob.glob(os.path.join(PREVIEWS, "anim_*.png")) + glob.glob(os.path.join(PREVIEWS, "anim_*.gif")):
        if os.path.splitext(os.path.basename(path))[0][len("anim_"):] not in manifest:
            remove(path)
    for path in glob.glob(os.path.join(OUT, "*.png.import")) + glob.glob(os.path.join(PREVIEWS, "anim_*.import")):
        if not os.path.exists(path[:-len(".import")]):
            os.remove(path)
    return manifest, removed


def verify():
    """Check the files on disk against the contract and the manifest."""
    problems = []
    path = os.path.join(OUT, "anims.json")
    if not os.path.exists(path):
        return ["anims.json is missing"], {}
    with open(path, encoding="utf-8") as fh:
        manifest = json.load(fh)
    for name, ((fw, fh_), loop) in REQUIRED.items():
        if name not in manifest:
            problems.append("%s: required by the contract but missing from anims.json" % name)
            continue
        e = manifest[name]
        if (e.get("frame_w"), e.get("frame_h")) != (fw, fh_):
            problems.append("%s: frame %sx%s, contract says %dx%d" % (name, e.get("frame_w"), e.get("frame_h"), fw, fh_))
        if loop is not None and e.get("loop") != loop:
            problems.append("%s: loop is %s, contract says %s" % (name, e.get("loop"), loop))
    for name, e in manifest.items():
        missing = [k for k in ("file", "frame_w", "frame_h", "frames", "fps", "loop") if k not in e]
        for key in missing:
            problems.append("%s: manifest key '%s' missing" % (name, key))
        if missing:
            continue
        sheet_path = os.path.join(OUT, e["file"])
        if not os.path.exists(sheet_path):
            problems.append("%s: sheet %s missing" % (name, e["file"]))
            continue
        img = Image.open(sheet_path)
        if img.mode != "RGBA":
            problems.append("%s: sheet is %s, expected RGBA" % (name, img.mode))
            continue
        if e["frames"] < 1 or e["fps"] <= 0:
            problems.append("%s: frames and fps must be positive" % name)
        if img.width != e["frame_w"] * e["frames"]:
            problems.append("%s: sheet width %d != frame_w %d * frames %d" % (name, img.width, e["frame_w"], e["frames"]))
            continue
        if img.height != e["frame_h"]:
            problems.append("%s: sheet height %d != frame_h %d" % (name, img.height, e["frame_h"]))
            continue
        alpha = img.getchannel("A")
        if sum(alpha.histogram()[1:255]):
            problems.append("%s: alpha values other than 0/255" % name)
        grounded = False
        for i in range(e["frames"]):
            cell = alpha.crop((i * e["frame_w"], 0, (i + 1) * e["frame_w"], e["frame_h"]))
            if cell.getextrema()[1] == 0:
                problems.append("%s: frame %d is empty" % (name, i))
            if cell.crop((0, e["frame_h"] - 1, e["frame_w"], e["frame_h"])).getextrema()[1]:
                grounded = True
        if name in GROUNDED and not grounded:
            problems.append("%s: nothing ever touches the bottom row" % name)
    for path in glob.glob(os.path.join(OUT, "*.png")):
        if os.path.basename(path) not in [e.get("file") for e in manifest.values()]:
            problems.append("%s: sheet on disk is not in anims.json" % os.path.basename(path))
    return problems, manifest


def main():
    anims, notes = build()
    _, removed = write(anims)
    problems, manifest = verify()
    for name, e in manifest.items():
        print("%-22s %2dx%-2d  %2d frames  %2d fps  %-4s %.2f s%s" % (
            name, e["frame_w"], e["frame_h"], e["frames"], e["fps"],
            "loop" if e["loop"] else "once", e["frames"] / float(e["fps"]), "" if name in REQUIRED else "  (extra)"))
    for n in notes:
        print("note: " + n)
    if removed:
        print("removed obsolete sheets: " + ", ".join(sorted(removed)))
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    print("OK: %d animations, all %d required by the contract present and consistent" % (len(manifest), len(REQUIRED)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
