"""Build and verify the machine sprites (art contract v2, section A).

Run from the repository root:
    python tools/pixel/build_machines.py

Writes assets/sprites/machines/*.png, anims.json and anchors.json, removes the
machine files of the previous art direction, writes contact sheets and GIFs to
tools/pixel/previews/, then checks everything against the contract. Exits
non-zero when a check fails.
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import machines as M  # noqa: E402
from pixlib import sheet, GREY  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "assets", "sprites", "machines")
PREV = os.path.join(HERE, "previews")

GACHA = (48, 84)
CAB = (72, 104)
STATIC_SIZES = {
    "machine_001": GACHA, "machine_002": GACHA, "machine_003": GACHA, "machine_004": GACHA,
    "machine_005": CAB, "machine_006": CAB,
    "capsule_red": (12, 12), "capsule_blue": (12, 12), "capsule_green": (12, 12),
    "capsule_mustard": (12, 12), "capsule_gold": (12, 12),
    "claw_open": (20, 20), "claw_closed": (20, 20), "plinko_ball": (6, 6),
}
ANIM_SPECS = {}   # name -> (frame size, loop, max seconds or None)
for _n in (1, 2, 3, 4, 5, 6):
    _k = "machine_%03d" % _n
    _size = GACHA if _n <= 4 else CAB
    ANIM_SPECS[_k + "_wake"] = (_size, False, 0.6)
    ANIM_SPECS[_k + "_idle"] = (_size, True, None)
    if _n <= 4:
        ANIM_SPECS[_k + "_play"] = (_size, False, 0.7)
    else:
        ANIM_SPECS[_k + "_react"] = (_size, False, 0.5)

# Anchors of the first rubber-hose pass. The game reads anchors.json, so a
# change is legal, but it has to be deliberate: update this table with it.
ANCHORS_FROZEN = {
    "machine_001": {"chute": [24, 72]}, "machine_002": {"chute": [24, 72]},
    "machine_003": {"chute": [24, 72]}, "machine_004": {"chute": [24, 72]},
    "machine_005": {"chute": [49, 89], "claw_rail_y": 28, "claw_min_x": 23, "claw_max_x": 49,
                    "claw_rest_x": 25, "grab_y": 33, "drop_x": 49, "drop_y": 55},
    "machine_006": {"chute": [36, 90], "ball_start": [36, 29], "rows": 6, "row_step": 6,
                    "column_step": 5, "slot_y": 72, "slot_xs": [16, 26, 36, 46, 56]},
}
MAX_STRIP_W = 16384      # largest texture the renderer is guaranteed to take
MIN_IDLE_POSES = 16      # an idle loop must really be alive


def palette():
    """Every colour the machine module declares (module-level RGB constants)."""
    out = set()
    for name in dir(M):
        v = getattr(M, name)
        if name.isupper() and isinstance(v, tuple) and len(v) == 3 and all(isinstance(c, int) for c in v):
            out.add(v)
    return out


def stray_colours(img, allowed):
    return sorted({c[:3] for _n, c in img.convert("RGBA").getcolors(1 << 20) if c[3]} - allowed)


OBSOLETE = ["machine_%03d_lit.png" % n for n in range(1, 7)] + [
    "gacha_knob.png", "capsule_coral.png", "capsule_mint.png", "capsule_teal.png"]


def strip(frames):
    w, h = frames[0].img.size
    out = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        out.paste(f.img, (i * w, 0))
    return out


def on_grey(img, scale):
    bg = Image.new("RGBA", img.size, GREY + (255,))
    bg.alpha_composite(img)
    return bg.resize((img.size[0] * scale, img.size[1] * scale), Image.NEAREST)


def gif(frames, fps, path_, scale=4, loop=True):
    ims = [on_grey(f.img, scale).convert("P", palette=Image.ADAPTIVE, colors=64) for f in frames]
    extra = {} if loop else {}
    ims[0].save(path_, save_all=True, append_images=ims[1:], duration=int(round(1000.0 / fps)),
                loop=0, disposal=2, **extra)


def composite(base, items):
    """Copy of a sprite image with other sprites drawn on it (top-left positions)."""
    out = base.copy()
    for img, x, y in items:
        out.alpha_composite(img, (x, y))
    return out


def build():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for name in OBSOLETE:
        for path_ in (os.path.join(OUT, name), os.path.join(OUT, name + ".import")):
            if os.path.exists(path_):
                os.remove(path_)

    stat = M.statics()
    for name, spr in stat.items():
        spr.img.save(os.path.join(OUT, name + ".png"))

    anims = M.animations()
    manifest = {}
    for name in sorted(anims):
        frames, fps, loop = anims[name]
        w, h = frames[0].img.size
        strip(frames).save(os.path.join(OUT, name + ".png"))
        manifest[name] = {"file": name + ".png", "frame_w": w, "frame_h": h,
                          "frames": len(frames), "fps": fps, "loop": loop}
    with open(os.path.join(OUT, "anims.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    anchors = M.anchors()
    with open(os.path.join(OUT, "anchors.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(anchors, fh, indent=2)
        fh.write("\n")

    previews(stat, anims, anchors)
    return stat, anims, manifest, anchors


def previews(stat, anims, anchors):
    order = ["machine_%03d" % n for n in range(1, 7)]
    small = ["capsule_red", "capsule_blue", "capsule_green", "capsule_mustard", "capsule_gold",
             "claw_open", "claw_closed", "plinko_ball"]
    lit = [anims[k + "_idle"][0][0] for k in order]
    sheet([stat[k] for k in order] + lit + [stat[k] for k in small],
          os.path.join(PREV, "rh_machines.png"), cols=6, scale=4)
    # game scale (x3) on a dark floor-like background, to judge readability
    sheet(lit + [stat[k] for k in order], os.path.join(PREV, "rh_machines_x3.png"), cols=12,
          scale=3, bg=(58, 52, 70))
    for name, (frames, fps, loop) in anims.items():
        sheet(frames, os.path.join(PREV, "rh_" + name + ".png"), cols=12, scale=4)
        gif(frames, fps, os.path.join(PREV, "rh_" + name + ".gif"))

    # anchor proofs
    caps = [stat["capsule_" + c].img for c in ("red", "blue", "green", "mustard")]
    proofs = []
    for i, n in enumerate((1, 2, 3, 4)):
        key = "machine_%03d" % n
        cx, cy = anchors[key]["chute"]
        proofs.append(composite(anims[key + "_idle"][0][0].img, [(caps[i], cx - 6, cy - 6)]))
    sheet(proofs, os.path.join(PREV, "rh_anchor_gacha.png"), cols=4, scale=4)

    a = anchors["machine_005"]
    crane = anims["machine_005_idle"][0][0].img
    op, cl = stat["claw_open"].img, stat["claw_closed"].img
    gold = stat["capsule_gold"].img
    proofs = [
        composite(crane, [(op, a["claw_rest_x"] - 10, a["claw_rail_y"])]),
        composite(crane, [(op, a["claw_min_x"] - 10, a["claw_rail_y"]),
                          (op, a["claw_max_x"] - 10, a["claw_rail_y"])]),
        composite(crane, [(op, a["claw_min_x"] - 10, a["grab_y"])]),
        composite(crane, [(cl, 34 - 10, a["grab_y"])]),
        composite(crane, [(cl, a["drop_x"] - 10, a["claw_rail_y"]),
                          (gold, a["drop_x"] - 6, a["drop_y"] - 6)]),
        composite(crane, [(op, a["drop_x"] - 10, a["claw_rail_y"]),
                          (gold, a["chute"][0] - 6, a["chute"][1] - 6)]),
    ]
    sheet(proofs, os.path.join(PREV, "rh_anchor_crane.png"), cols=6, scale=4)

    a = anchors["machine_006"]
    board = anims["machine_006_idle"][0][0].img
    pb = stat["plinko_ball"].img
    every = []
    for k in range(a["rows"] + 1):
        for o in range(-k, k + 1, 2):
            if abs(o) <= 5:
                every.append((pb, a["ball_start"][0] + o * a["column_step"] - 3,
                              a["ball_start"][1] + k * a["row_step"] - 3))
    slots = [(pb, x - 3, a["slot_y"] - 3) for x in a["slot_xs"]]
    path_r = [(pb, a["ball_start"][0] + o * a["column_step"] - 3,
               a["ball_start"][1] + k * a["row_step"] - 3)
              for k, o in enumerate((0, 1, 2, 1, 2, 3, 4))]
    proofs = [
        composite(board, every[:-7]),
        composite(board, slots),
        composite(board, path_r + [(pb, a["slot_xs"][4] - 3, a["slot_y"] - 3)]),
        composite(board, [(caps[0], a["chute"][0] - 6, a["chute"][1] - 6)]),
    ]
    sheet(proofs, os.path.join(PREV, "rh_anchor_plinko.png"), cols=4, scale=4)


# ------------------------------------------------------------------ verification

def alpha_ok(img):
    hist = img.getchannel("A").histogram()
    return sum(hist[1:255]) == 0


def frame_of(img, w, h, i):
    return img.crop((i * w, 0, (i + 1) * w, h))


def same_region(a, b, rect):
    return a.crop(rect).tobytes() == b.crop(rect).tobytes()


def stable_regions(key, a):
    """Rectangles (x0, y0, x1+1, y1+1) that must not change in idle / react."""
    cx, cy = a["chute"]
    rects = [(cx - 6, cy - 6, cx + 6, cy + 6)]
    if key == "machine_005":
        x0, y0, x1, y1 = M.CR_GLASS
        rects.append((x0, y0, x1 + 1, y1 + 1))
    if key == "machine_006":
        x0, y0, x1, y1 = M.PK_BOARD
        rects.append((x0, y0, x1 + 1, y1 + 1))
    return rects


def verify():
    problems = []

    def bad(msg):
        problems.append(msg)

    imgs = {}
    for name, size in STATIC_SIZES.items():
        path_ = os.path.join(OUT, name + ".png")
        if not os.path.exists(path_):
            bad("missing " + name + ".png")
            continue
        img = Image.open(path_)
        imgs[name] = img
        if img.mode != "RGBA":
            bad("%s: mode %s, expected RGBA" % (name, img.mode))
        elif not alpha_ok(img):
            bad("%s: alpha must be 0 or 255" % name)
        if img.size != size:
            bad("%s: size %s, expected %s" % (name, img.size, size))
        if name.startswith("machine_") and img.mode == "RGBA":
            bb = img.getbbox()
            if bb is None or bb[3] != size[1]:
                bad("%s: does not touch the bottom row" % name)
            elif abs((bb[0] + bb[2]) - size[0]) > 2:
                bad("%s: not horizontally centred (bbox %s)" % (name, bb))

    allowed = palette()
    for name, img in imgs.items():
        extra = stray_colours(img, allowed)
        if extra:
            bad("%s: colours outside the declared palette: %s" % (name, extra[:4]))

    for name in OBSOLETE:
        if os.path.exists(os.path.join(OUT, name)) or os.path.exists(os.path.join(OUT, name + ".import")):
            bad("obsolete file still present: " + name)

    try:
        with open(os.path.join(OUT, "anims.json"), encoding="utf-8") as fh:
            manifest = json.load(fh)
    except (OSError, ValueError) as err:
        bad("anims.json: %s" % err)
        manifest = {}
    try:
        with open(os.path.join(OUT, "anchors.json"), encoding="utf-8") as fh:
            anchors = json.load(fh)
    except (OSError, ValueError) as err:
        bad("anchors.json: %s" % err)
        anchors = {}

    for name in manifest:
        if name not in ANIM_SPECS:
            bad("anims.json: unexpected animation " + name)
    strips = {}
    for name, (size, loop, max_s) in ANIM_SPECS.items():
        e = manifest.get(name)
        if e is None:
            bad("anims.json: missing " + name)
            continue
        if sorted(e) != ["file", "fps", "frame_h", "frame_w", "frames", "loop"]:
            bad("%s: wrong manifest keys %s" % (name, sorted(e)))
            continue
        if (e["frame_w"], e["frame_h"]) != size:
            bad("%s: frame %dx%d, expected %dx%d" % (name, e["frame_w"], e["frame_h"], size[0], size[1]))
        if e["loop"] is not loop:
            bad("%s: loop must be %s" % (name, loop))
        if not (isinstance(e["frames"], int) and e["frames"] >= 1 and e["fps"] > 0):
            bad("%s: bad frames / fps" % name)
            continue
        if max_s is not None and e["frames"] / float(e["fps"]) > max_s + 1e-9:
            bad("%s: lasts %.3f s, limit %.1f s" % (name, e["frames"] / float(e["fps"]), max_s))
        path_ = os.path.join(OUT, e["file"])
        if not os.path.exists(path_):
            bad("%s: file %s missing" % (name, e["file"]))
            continue
        img = Image.open(path_)
        if img.mode != "RGBA" or not alpha_ok(img):
            bad("%s: must be RGBA with alpha 0 or 255" % name)
            continue
        if img.size != (e["frame_w"] * e["frames"], e["frame_h"]):
            bad("%s: strip %s does not match %d frames of %dx%d"
                % (name, img.size, e["frames"], e["frame_w"], e["frame_h"]))
            continue
        if img.size[0] > MAX_STRIP_W:
            bad("%s: strip is %d px wide, limit %d" % (name, img.size[0], MAX_STRIP_W))
        extra = stray_colours(img, allowed)
        if extra:
            bad("%s: colours outside the declared palette: %s" % (name, extra[:4]))
        strips[name] = [frame_of(img, e["frame_w"], e["frame_h"], i) for i in range(e["frames"])]
        raw = [fr.tobytes() for fr in strips[name]]
        if loop:
            if len(set(raw)) < MIN_IDLE_POSES:
                bad("%s: only %d different poses, expected at least %d"
                    % (name, len(set(raw)), MIN_IDLE_POSES))
        else:
            for i in range(1, len(raw)):
                if raw[i] == raw[i - 1]:
                    bad("%s: frame %d repeats frame %d" % (name, i, i - 1))
        for i, fr in enumerate(strips[name]):
            # A pose cut by the canvas shows as a filled (non-outline) pixel on
            # the top row or on a side column: only the ink contour may touch them.
            fw, fh = e["frame_w"], e["frame_h"]
            px = fr.load()
            border = [(x, 0) for x in range(fw)] + [(x, y) for y in range(fh - 1) for x in (0, fw - 1)]
            if any(px[q][3] and px[q][:3] != M.INK for q in border):
                bad("%s: frame %d is cut by the canvas edge" % (name, i))
        for i, fr in enumerate(strips[name]):
            bb = fr.getbbox()
            if bb is None or bb[3] != e["frame_h"]:
                bad("%s: frame %d does not touch the bottom row" % (name, i))

    # pose continuity and pixel-stable anchors
    for n in range(1, 7):
        key = "machine_%03d" % n
        idle = strips.get(key + "_idle")
        if not idle:
            continue
        size = GACHA if n <= 4 else CAB
        a = anchors.get(key)
        if a is None:
            bad("anchors.json: missing " + key)
            continue
        wake = strips.get(key + "_wake")
        if wake:
            if key in imgs and wake[0].tobytes() != imgs[key].convert("RGBA").tobytes():
                bad("%s_wake: first frame is not the powered-off sprite" % key)
            if wake[-1].tobytes() != idle[0].tobytes():
                bad("%s_wake: does not end in the first idle pose" % key)
        other = key + ("_play" if n <= 4 else "_react")
        if other in strips and strips[other][-1].tobytes() != idle[0].tobytes():
            bad("%s: does not end in the first idle pose" % other)
        cx, cy = a["chute"]
        if not (6 <= cx <= size[0] - 6 and 6 <= cy <= size[1] - 6):
            bad("%s: chute capsule does not fit the canvas" % key)
        check = list(idle) + (strips.get(key + "_react") or [] if n >= 5 else [])
        for rect in stable_regions(key, a):
            for i, fr in enumerate(check):
                if not same_region(fr, idle[0], rect):
                    bad("%s: region %s changes in idle/react frame %d" % (key, rect, i))
                    break

    if anchors and anchors != ANCHORS_FROZEN:
        for key in sorted(set(anchors) | set(ANCHORS_FROZEN)):
            if anchors.get(key) != ANCHORS_FROZEN.get(key):
                bad("anchors.json: %s differs from the frozen values (%s); if intended, "
                    "update ANCHORS_FROZEN and report it" % (key, anchors.get(key)))

    a = anchors.get("machine_005")
    if a:
        want = ["chute", "claw_max_x", "claw_min_x", "claw_rail_y", "claw_rest_x", "drop_x", "drop_y", "grab_y"]
        if sorted(a) != want:
            bad("machine_005 anchors: keys %s" % sorted(a))
        else:
            gx0, gy0, gx1, gy1 = M.CR_GLASS
            if not (gx0 <= a["claw_min_x"] - 10 and a["claw_max_x"] + 9 <= gx1):
                bad("machine_005: claw leaves the glass box sideways")
            if not (gy0 <= a["claw_rail_y"] < a["grab_y"] and a["grab_y"] + 19 <= gy1):
                bad("machine_005: claw leaves the glass box vertically")
            if not (a["claw_min_x"] <= a["claw_rest_x"] <= a["claw_max_x"]
                    and a["claw_min_x"] <= a["drop_x"] <= a["claw_max_x"]):
                bad("machine_005: rest / drop x outside the claw range")
            if not (gy0 <= a["drop_y"] <= gy1):
                bad("machine_005: drop_y outside the glass box")
    a = anchors.get("machine_006")
    if a:
        want = ["ball_start", "chute", "column_step", "row_step", "rows", "slot_xs", "slot_y"]
        if sorted(a) != want:
            bad("machine_006 anchors: keys %s" % sorted(a))
        else:
            bx0, by0, bx1, by1 = M.PK_BOARD
            sx, sy = a["ball_start"]
            cs = a["column_step"]
            if a["slot_xs"] != [sx + cs * o for o in (-4, -2, 0, 2, 4)]:
                bad("machine_006: slot_xs must be spaced 2 x column_step around ball_start x")
            if a["rows"] != 6:
                bad("machine_006: rows must be 6")
            if not (by0 <= sy - 3 and a["slot_y"] + 2 <= by1 and sy + a["rows"] * a["row_step"] <= a["slot_y"]):
                bad("machine_006: ball path leaves the board vertically")
            if not (bx0 <= a["slot_xs"][0] - 3 and a["slot_xs"][-1] + 2 <= bx1):
                bad("machine_006: slots leave the board sideways")
            if not (bx0 <= sx - 5 * cs - 3 and sx + 5 * cs + 2 <= bx1):
                bad("machine_006: a ball five columns off centre leaves the board")
    for n in (1, 2, 3, 4):
        a = anchors.get("machine_%03d" % n)
        if a is not None and sorted(a) != ["chute"]:
            bad("machine_%03d anchors: keys %s" % (n, sorted(a)))
    return problems, manifest


def main():
    build()
    problems, manifest = verify()
    for name in sorted(manifest):
        e = manifest[name]
        print("%-22s %2d frames @ %2d fps  %.3f s  %s" % (
            name, e["frames"], e["fps"], e["frames"] / float(e["fps"]), "loop" if e["loop"] else "once"))
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    print("OK: machines match the contract (%d stills, %d animations)" % (len(STATIC_SIZES), len(manifest)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
