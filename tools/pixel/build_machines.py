"""Builds and verifies the machine sprites (art contract v3, sepia cartoon).

    python tools/pixel/build_machines.py

Writes assets/sprites/machines/*.png, anims.json and anchors.json, writes
contact sheets to tools/pixel/previews/sp_*.png, then checks everything
against the contract (sizes, manifest, timing limits, start and end frames,
stable regions, anchors) and exits non-zero on problems.
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import machines as M  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "assets", "sprites", "machines")
PREV = os.path.join(HERE, "previews")

STATIC_SIZES = {
    "machine_001": M.GACHA, "machine_002": M.GACHA,
    "machine_005": M.CAB, "machine_006": M.CAB,
    "capsule_red": (18, 18), "capsule_blue": (18, 18), "capsule_green": (18, 18),
    "capsule_mustard": (18, 18), "capsule_gold": (18, 18),
    "claw_open": (30, 30), "claw_closed": (30, 30), "plinko_ball": (9, 9),
}
# name -> (frame size, loop, max seconds or None)
ANIM_SPECS = {}
for _n in (1, 2, 5, 6):
    _size = M.GACHA if _n < 5 else M.CAB
    ANIM_SPECS["machine_%03d_wake" % _n] = (_size, False, 0.6)
    ANIM_SPECS["machine_%03d_idle" % _n] = (_size, True, None)
    if _n < 5:
        ANIM_SPECS["machine_%03d_play" % _n] = (_size, False, 0.7)
    else:
        ANIM_SPECS["machine_%03d_react" % _n] = (_size, False, 0.5)

MAX_STRIP_W = 16384
MIN_IDLE_POSES = 8
BACK = (126, 112, 92, 255)


def strip(frames):
    w, h = frames[0].size
    out = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        out.paste(frame, (i * w, 0))
    return out


def sheet(images, path, cols, scale):
    w = max(im.width for im in images) + 4
    h = max(im.height for im in images) + 4
    rows = (len(images) + cols - 1) // cols
    out = Image.new("RGBA", (w * min(cols, len(images)), h * rows), BACK)
    for i, im in enumerate(images):
        out.alpha_composite(im, ((i % cols) * w + 2, (i // cols) * h + 2 + (h - 4 - im.height)))
    out = out.resize((out.width * scale, out.height * scale), Image.NEAREST)
    out.save(path)


def composite(base, items):
    out = base.copy()
    for im, (x, y) in items:
        out.alpha_composite(im, (int(x), int(y)))
    return out


def centred(im, cx, cy):
    return im, (cx - im.width // 2, cy - im.height // 2)


def hung(im, x, y):
    return im, (x - im.width // 2, y)


def build():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    stat = M.stills()
    anims = M.animations()
    for name, im in stat.items():
        im.save(os.path.join(OUT, name + ".png"))
    manifest = {}
    for name, (frames, fps, loop) in anims.items():
        strip(frames).save(os.path.join(OUT, name + ".png"))
        manifest[name] = {"file": name + ".png", "frame_w": frames[0].width, "frame_h": frames[0].height,
                          "frames": len(frames), "fps": fps, "loop": loop}
    with open(os.path.join(OUT, "anims.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")
    with open(os.path.join(OUT, "anchors.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(M.ANCHORS, f, indent=2, sort_keys=True)
        f.write("\n")
    return stat, anims


def previews(stat, anims):
    keys = ["machine_%03d" % n for n in (1, 2, 5, 6)]
    loose = [stat[k] for k in ("capsule_red", "capsule_blue", "capsule_green", "capsule_mustard",
                               "capsule_gold", "claw_open", "claw_closed", "plinko_ball")]
    sheet([stat[k] for k in keys] + [anims[k + "_idle"][0][0] for k in keys],
          os.path.join(PREV, "sp_machines.png"), cols=6, scale=3)
    sheet(loose, os.path.join(PREV, "sp_machine_parts.png"), cols=8, scale=6)
    for name, (frames, _fps, _loop) in anims.items():
        distinct = []
        for frame in frames:
            if not distinct or frame is not distinct[-1]:
                distinct.append(frame)
        sheet(distinct if "idle" in name else frames, os.path.join(PREV, "sp_%s.png" % name),
              cols=8 if frames[0].width > 80 else 10, scale=2)
    # Anchor proofs: the loose sprites placed exactly as the game places them.
    proofs = []
    for n in (1, 2):
        key = "machine_%03d" % n
        cx, cy = M.ANCHORS[key]["chute"]
        colour = ("red", "blue", "green", "gold")[n - 1]
        proofs.append(composite(anims[key + "_idle"][0][0], [centred(stat["capsule_" + colour], cx, cy)]))
    a = M.ANCHORS["machine_005"]
    idle = anims["machine_005_idle"][0][0]
    mid = (a["claw_min_x"] + a["claw_max_x"]) // 2
    proofs.append(composite(idle, [hung(stat["claw_open"], a["claw_rest_x"], a["claw_rail_y"])]))
    proofs.append(composite(idle, [hung(stat["claw_open"], mid, a["grab_y"])]))
    proofs.append(composite(idle, [centred(stat["capsule_mustard"], a["drop_x"], a["drop_y"]),
                                   hung(stat["claw_closed"], a["drop_x"], a["claw_rail_y"]),
                                   centred(stat["capsule_mustard"], *a["chute"])]))
    a = M.ANCHORS["machine_006"]
    idle = anims["machine_006_idle"][0][0]
    ball = stat["plinko_ball"]
    path, x = [], a["ball_start"][0]
    for row, step in enumerate((0, -1, 1, 1, -1, -1, 1)):
        x += step * a["column_step"]
        path.append(centred(ball, x, a["ball_start"][1] + row * a["row_step"]))
    proofs.append(composite(idle, path))
    proofs.append(composite(idle, [centred(ball, sx, a["slot_y"]) for sx in a["slot_xs"]]
                            + [centred(stat["capsule_blue"], *a["chute"])]))
    sheet(proofs, os.path.join(PREV, "sp_machine_anchors.png"), cols=9, scale=3)


def alpha_ok(im):
    return set(im.getchannel("A").tobytes()) <= {0, 255}


def same(a, b, rect):
    return a.crop(rect).tobytes() == b.crop(rect).tobytes()


def box18(point):
    return (point[0] - 9, point[1] - 9, point[0] + 9, point[1] + 9)


def inside(rect, size):
    return rect[0] >= 0 and rect[1] >= 0 and rect[2] <= size[0] and rect[3] <= size[1]


def verify(stat, anims):
    problems = []
    with open(os.path.join(OUT, "anims.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    with open(os.path.join(OUT, "anchors.json"), encoding="utf-8") as f:
        anchors = json.load(f)

    for name, size in STATIC_SIZES.items():
        path = os.path.join(OUT, name + ".png")
        if not os.path.exists(path):
            problems.append("missing %s.png" % name)
            continue
        im = Image.open(path).convert("RGBA")
        if im.size != size:
            problems.append("%s.png is %s, expected %s" % (name, im.size, size))
        if not alpha_ok(im):
            problems.append("%s.png has partial alpha" % name)
        if name.startswith("machine_") and im.getchannel("A").crop((0, size[1] - 1, size[0], size[1])).getbbox() is None:
            problems.append("%s.png does not stand on the bottom row" % name)

    if set(manifest) != set(ANIM_SPECS):
        problems.append("anims.json names differ: %s" % sorted(set(manifest) ^ set(ANIM_SPECS)))
    loaded = {}
    for name, (size, loop, limit) in ANIM_SPECS.items():
        entry = manifest.get(name)
        if entry is None:
            continue
        path = os.path.join(OUT, entry["file"])
        if not os.path.exists(path):
            problems.append("missing %s" % entry["file"])
            continue
        im = Image.open(path).convert("RGBA")
        if (entry["frame_w"], entry["frame_h"]) != size:
            problems.append("%s: frame size %sx%s, expected %s" % (name, entry["frame_w"], entry["frame_h"], size))
        if im.size != (size[0] * entry["frames"], size[1]):
            problems.append("%s: strip is %s for %d frames" % (name, im.size, entry["frames"]))
            continue
        if im.width > MAX_STRIP_W:
            problems.append("%s: strip wider than %d" % (name, MAX_STRIP_W))
        if entry["loop"] != loop:
            problems.append("%s: loop must be %s" % (name, loop))
        seconds = entry["frames"] / float(entry["fps"])
        if limit is not None and seconds > limit + 1e-6:
            problems.append("%s lasts %.3f s, over %.1f s" % (name, seconds, limit))
        if not alpha_ok(im):
            problems.append("%s has partial alpha" % name)
        loaded[name] = [im.crop((i * size[0], 0, (i + 1) * size[0], size[1])) for i in range(entry["frames"])]

    for n in (1, 2, 5, 6):
        key = "machine_%03d" % n
        size = STATIC_SIZES[key]
        need = [key + "_wake", key + "_idle", key + ("_play" if n < 5 else "_react")]
        if any(name not in loaded for name in need):
            continue
        wake, idle, act = (loaded[name] for name in need)
        off = Image.open(os.path.join(OUT, key + ".png")).convert("RGBA")
        if wake[0].tobytes() != off.tobytes():
            problems.append("%s must start on the powered-off still" % need[0])
        for name, frames in ((need[0], wake), (need[2], act)):
            if frames[-1].tobytes() != idle[0].tobytes():
                problems.append("%s must end on idle frame 0" % name)
        if len({f.tobytes() for f in idle}) < MIN_IDLE_POSES:
            problems.append("%s has fewer than %d distinct poses" % (need[1], MIN_IDLE_POSES))
        a = anchors.get(key)
        if a is None or "chute" not in a:
            problems.append("anchors.json lacks %s.chute" % key)
            continue
        if not inside(box18(a["chute"]), size):
            problems.append("%s: the capsule on the chute leaves the canvas" % key)
        regions = {"chute tray": box18(a["chute"])}
        stable = list(idle)
        if n == 5:
            regions["glass interior"] = M.CRANE_GLASS
            stable += act
        if n == 6:
            regions["peg board"] = M.PLINKO_BOARD
            stable += act
        for label, rect in regions.items():
            if any(not same(frame, stable[0], rect) for frame in stable):
                problems.append("%s: the %s changes during idle/react" % (key, label))
        if n == 5:
            gx0, gy0, gx1, gy1 = M.CRANE_GLASS
            for field in ("claw_rail_y", "claw_min_x", "claw_max_x", "claw_rest_x", "grab_y", "drop_x", "drop_y"):
                if field not in a:
                    problems.append("anchors.json lacks machine_005.%s" % field)
                    break
            else:
                if not (gx0 <= a["claw_min_x"] - 15 and a["claw_max_x"] + 15 <= gx1):
                    problems.append("machine_005: the claw leaves the glass sideways")
                if not (a["claw_min_x"] <= a["claw_rest_x"] <= a["claw_max_x"]
                        and a["claw_min_x"] <= a["drop_x"] <= a["claw_max_x"]):
                    problems.append("machine_005: claw_rest_x / drop_x outside the claw range")
                if not (gy0 <= a["claw_rail_y"] < a["grab_y"] and a["grab_y"] + 30 <= gy1):
                    problems.append("machine_005: the claw leaves the glass vertically")
                if not (gy0 < a["drop_y"] < gy1):
                    problems.append("machine_005: drop_y outside the glass")
        if n == 6:
            for field in ("ball_start", "rows", "row_step", "column_step", "slot_y", "slot_xs"):
                if field not in a:
                    problems.append("anchors.json lacks machine_006.%s" % field)
                    break
            else:
                bx0, by0, bx1, by1 = M.PLINKO_BOARD
                xs = a["slot_xs"]
                if any(xs[i + 1] - xs[i] != 2 * a["column_step"] for i in range(len(xs) - 1)):
                    problems.append("machine_006: slot_xs are not spaced 2 x column_step")
                if len(xs) != 5 or xs[2] != a["ball_start"][0]:
                    problems.append("machine_006: slot_xs are not five slots centred on ball_start")
                last_y = a["ball_start"][1] + a["rows"] * a["row_step"]
                if not (by0 <= a["ball_start"][1] - 4 and last_y < a["slot_y"] and a["slot_y"] + 5 <= by1):
                    problems.append("machine_006: the ball path leaves the board vertically")
                if not (bx0 <= xs[0] - 4 and xs[-1] + 5 <= bx1):
                    problems.append("machine_006: the slots leave the board sideways")
    return problems, len(manifest)


def main():
    stat, anims = build()
    previews(stat, anims)
    problems, count = verify(stat, anims)
    if problems:
        print("PROBLEMS:")
        for problem in problems:
            print("  - " + problem)
        return 1
    print("OK: machines match the contract (%d stills and sprites, %d animations)" % (len(STATIC_SIZES), count))
    for name in sorted(anims):
        frames, fps, loop = anims[name]
        print("  %-18s %2d frames @ %2d fps = %.3f s%s" % (name, len(frames), fps, len(frames) / float(fps), " loop" if loop else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
