"""Entry point: rubber-hose figures and rarity bases (art-contract.md, section B).

Writes
  assets/sprites/figures/<figure_id>.png   20 figures, 40 x 40
  assets/sprites/figures/<figure_id>_idle.png   idle loop strip, 40 x 40 frames
  assets/sprites/figures/anims.json        manifest of the idle loops (fig_<figure_id>_idle)
  assets/sprites/bases/base_<rarity>.png   five animation strips, 56 x 30 frames
  assets/sprites/bases/anims.json          manifest of the five base animations
  tools/pixel/previews/rh_figures.png, rh_figures_silhouettes.png,
  rh_bases.png, rh_bases_review.png, figures_on_bases.png, rh_base_ladder.png,
  rh_figures_idle_a.png, rh_figures_idle_b.png (all idle frames side by side)

then verifies everything against the contract and exits non-zero on problems.
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import bases  # noqa: E402
import figures  # noqa: E402
from pixlib import sheet  # noqa: E402

FIG_DIR = os.path.join(ROOT, "assets", "sprites", "figures")
BASE_DIR = os.path.join(ROOT, "assets", "sprites", "bases")
PREV = os.path.join(HERE, "previews")
FIG = 40
BW, BH = 56, 30
FEET = (28, 12)
MAX_IOU = 0.80


def alpha_set(img):
    px = img.load()
    return {(x, y) for y in range(img.size[1]) for x in range(img.size[0]) if px[x, y][3]}


def silhouette(img, col=(22, 19, 32)):
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    o = out.load()
    for (x, y) in alpha_set(img):
        o[x, y] = col + (255,)
    return out


def on_base(fig_img, base_frame):
    """Figure standing on a base exactly as the game stacks them."""
    out = Image.new("RGBA", (BW, BH + FIG - FEET[1] - 1), (0, 0, 0, 0))
    oy = FIG - FEET[1] - 1
    out.alpha_composite(base_frame, (0, oy))
    out.alpha_composite(fig_img, (FEET[0] - FIG // 2, 0))
    return out


def strip(frames):
    out = Image.new("RGBA", (BW * len(frames), BH), (0, 0, 0, 0))
    for i, fr in enumerate(frames):
        out.paste(fr.img, (i * BW, 0))
    return out


def main():
    problems = []
    with open(os.path.join(ROOT, "data", "figures.json"), encoding="utf-8") as fh:
        figs = json.load(fh)["figures"]

    # ------------------------------------------------------------ figures
    os.makedirs(FIG_DIR, exist_ok=True)
    imgs = {}
    for fig in figs:
        spr, probs = figures.build_figure(fig)
        problems += probs
        if fig["name_en"] not in figures.RECIPES:
            problems.append("%s (%s): no recipe, generic fallback used" % (fig["id"], fig["name_en"]))
        spr.save(os.path.join(FIG_DIR, fig["id"] + ".png"))
        imgs[fig["id"]] = spr.img

    # ------------------------------------------------------------ idle loops
    idle = {}
    fig_manifest = {}
    for fig in figs:
        frames, fps, probs = figures.build_idle(fig)
        problems += probs
        st = Image.new("RGBA", (FIG * len(frames), FIG), (0, 0, 0, 0))
        for k, fr in enumerate(frames):
            st.paste(fr.img, (k * FIG, 0))
        st.save(os.path.join(FIG_DIR, fig["id"] + "_idle.png"))
        idle[fig["id"]] = [fr.img for fr in frames]
        fig_manifest["fig_%s_idle" % fig["id"]] = {"file": fig["id"] + "_idle.png", "frame_w": FIG, "frame_h": FIG,
                                                   "frames": len(frames), "fps": fps, "loop": True}
    with open(os.path.join(FIG_DIR, "anims.json"), "w", encoding="utf-8") as fh:
        json.dump(fig_manifest, fh, indent=2)
        fh.write("\n")

    # ------------------------------------------------------------ bases
    os.makedirs(BASE_DIR, exist_ok=True)
    built = bases.build_bases()
    manifest = {}
    for name, (frames, fps) in built.items():
        strip(frames).save(os.path.join(BASE_DIR, name + ".png"))
        manifest[name] = {"file": name + ".png", "frame_w": BW, "frame_h": BH,
                          "frames": len(frames), "fps": fps, "loop": True}
    with open(os.path.join(BASE_DIR, "anims.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    # ------------------------------------------------------------ previews
    order = [f["id"] for f in figs]
    sheet([imgs[i] for i in order], os.path.join(PREV, "rh_figures.png"), cols=5, scale=5)
    sheet([silhouette(imgs[i]) for i in order], os.path.join(PREV, "rh_figures_silhouettes.png"), cols=10, scale=3)
    half = (len(order) + 1) // 2
    for tag, part in (("a", order[:half]), ("b", order[half:])):
        nmax = max(len(idle[i]) for i in part)
        sh = Image.new("RGBA", (nmax * (FIG + 2) + 2, len(part) * (FIG + 2) + 2), (120, 124, 132, 255))
        for r, fid in enumerate(part):
            for k, im in enumerate(idle[fid]):
                sh.alpha_composite(im, (2 + k * (FIG + 2), 2 + r * (FIG + 2)))
        sh.resize((sh.size[0] * 3, sh.size[1] * 3), Image.NEAREST).save(os.path.join(PREV, "rh_figures_idle_%s.png" % tag))
    rows = []
    wmax = max(len(fr) for fr, _ in built.values()) * (BW + 4) + 4
    for name, (frames, fps) in built.items():
        row = Image.new("RGBA", (wmax, BH + 8), (120, 124, 132, 255))
        for i, fr in enumerate(frames):
            row.alpha_composite(fr.img, (4 + i * (BW + 4), 4))
        rows.append(row)
    allb = Image.new("RGBA", (wmax, sum(r.size[1] for r in rows)), (120, 124, 132, 255))
    y = 0
    for r in rows:
        allb.paste(r, (0, y))
        y += r.size[1]
    allb.resize((allb.size[0] * 4, allb.size[1] * 4), Image.NEAREST).save(os.path.join(PREV, "rh_bases.png"))
    review = []
    for name, (frames, fps) in built.items():
        review += [frames[k * len(frames) // 3].img for k in range(3)]
    sheet(review, os.path.join(PREV, "rh_bases_review.png"), cols=3, scale=6)
    stacked = []
    for fig in figs:
        frames, _ = built[bases.RARITY_BASE[fig["rarity_id"]]]
        stacked.append(on_base(imgs[fig["id"]], frames[0].img))
    sheet(stacked, os.path.join(PREV, "figures_on_bases.png"), cols=5, scale=4)
    # the ladder at game size (x1 and x2) to judge it at a glance
    ladder = []
    by_rarity = {}
    for fig in figs:
        by_rarity.setdefault(fig["rarity_id"], fig)
    for rid in ("common", "uncommon", "rare", "epic", "legendary"):
        fig = by_rarity[rid]
        ladder.append(on_base(imgs[fig["id"]], built[bases.RARITY_BASE[rid]][0][0].img))
    sheet(ladder, os.path.join(PREV, "rh_base_ladder.png"), cols=5, scale=2)

    # ------------------------------------------------------------ verification
    if len(figs) != 20:
        problems.append("expected 20 figures in data/figures.json, found %d" % len(figs))
    sil = {}
    for fig in figs:
        path = os.path.join(FIG_DIR, fig["id"] + ".png")
        if not os.path.isfile(path):
            problems.append("missing " + path)
            continue
        im = Image.open(path).convert("RGBA")
        if im.size != (FIG, FIG):
            problems.append("%s: size %s, expected 40x40" % (fig["id"], im.size))
            continue
        px = im.load()
        if any(px[x, y][3] not in (0, 255) for y in range(FIG) for x in range(FIG)):
            problems.append("%s: alpha other than 0/255" % fig["id"])
        a = alpha_set(im)
        sil[fig["id"]] = a
        bottom = [x for (x, y) in a if y == FIG - 1]
        if not bottom:
            problems.append("%s: does not touch the bottom row" % fig["id"])
        else:
            cx = (min(bottom) + max(bottom) + 1) / 2.0
            if abs(cx - FIG / 2.0) > 2.5:
                problems.append("%s: feet centred on x=%.1f, expected 20" % (fig["id"], cx))
        xs = [q[0] for q in a]
        bx = (min(xs) + max(xs) + 1) / 2.0
        if abs(bx - FIG / 2.0) > 4.0:
            problems.append("%s: silhouette centred on x=%.1f, expected about 20" % (fig["id"], bx))
    pairs = []
    ids = [f["id"] for f in figs if f["id"] in sil]
    names = {f["id"]: f["name_en"] for f in figs}
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = sil[ids[i]], sil[ids[j]]
            iou = len(a & b) / float(len(a | b))
            pairs.append((iou, ids[i], ids[j]))
            if a == b:
                problems.append("%s and %s: identical silhouettes" % (ids[i], ids[j]))
            elif iou > MAX_IOU:
                problems.append("%s and %s: silhouettes too alike (IoU %.2f)" % (ids[i], ids[j], iou))
    pairs.sort(reverse=True)
    extra = sorted(set(os.path.splitext(n)[0] for n in os.listdir(FIG_DIR) if n.endswith(".png"))
                   - set(order) - set(i + "_idle" for i in order))
    if extra:
        problems.append("stray figure sprites not in data/figures.json: " + ", ".join(extra))

    # idle loops: manifest consistency, frame 0 = static sprite, planted feet,
    # every frame inside the canvas, and real motion
    with open(os.path.join(FIG_DIR, "anims.json"), encoding="utf-8") as fh:
        fman = json.load(fh)
    timings = set()
    for fig in figs:
        fid = fig["id"]
        name = "fig_%s_idle" % fid
        e = fman.get(name)
        if e is None:
            problems.append("figures/anims.json: missing " + name)
            continue
        if (e.get("frame_w"), e.get("frame_h")) != (FIG, FIG):
            problems.append("%s: frame size %sx%s, expected 40x40" % (name, e.get("frame_w"), e.get("frame_h")))
        if e.get("loop") is not True:
            problems.append("%s: must loop" % name)
        n, fps = e.get("frames", 0), e.get("fps", 0)
        if not 4 <= n <= 10:
            problems.append("%s: %s frames, expected 4..10" % (name, n))
        if not 4 <= fps <= 8:
            problems.append("%s: %s fps, expected 4..8" % (name, fps))
        timings.add((n, fps))
        path = os.path.join(FIG_DIR, e.get("file", ""))
        if not os.path.isfile(path):
            problems.append("%s: file %s missing" % (name, e.get("file")))
            continue
        im = Image.open(path).convert("RGBA")
        if im.size != (FIG * n, FIG):
            problems.append("%s: strip is %s, manifest says %s frames of 40x40" % (name, im.size, n))
            continue
        static = Image.open(os.path.join(FIG_DIR, fid + ".png")).convert("RGBA")
        frames = [im.crop((k * FIG, 0, (k + 1) * FIG, FIG)) for k in range(n)]
        if frames[0].tobytes() != static.tobytes():
            problems.append("%s: frame 0 differs from the static sprite" % name)
        if len(set(fr.tobytes() for fr in frames)) < min(n, 3):
            problems.append("%s: fewer than 3 distinct frames" % name)
        a0 = alpha_set(frames[0])
        feet0 = sorted(x for (x, y) in a0 if y == FIG - 1)
        for k, fr in enumerate(frames):
            px = fr.load()
            a = alpha_set(fr)
            if any(px[x, y][3] not in (0, 255) for (x, y) in a):
                problems.append("%s frame %d: alpha other than 0/255" % (name, k))
            feet = sorted(x for (x, y) in a if y == FIG - 1)
            if not feet:
                problems.append("%s frame %d: does not touch the bottom row" % (name, k))
            elif abs((feet[0] + feet[-1]) - (feet0[0] + feet0[-1])) > 2:
                problems.append("%s frame %d: feet slide on the bottom row" % (name, k))
            # the silhouette may breathe but not jump
            diff = len(a ^ a0) / float(len(a0))
            if diff > 0.45:
                problems.append("%s frame %d: silhouette changes by %d%%" % (name, k, int(diff * 100)))
    if len(timings) < 8:
        problems.append("idle loops: only %d different (frames, fps) timings, figures would pulse in unison" % len(timings))
    for name in fman:
        if not any(name == "fig_%s_idle" % f["id"] for f in figs):
            problems.append("figures/anims.json: unexpected animation " + name)

    mpath = os.path.join(BASE_DIR, "anims.json")
    with open(mpath, encoding="utf-8") as fh:
        man = json.load(fh)
    for name in ("base_common", "base_uncommon", "base_rare", "base_epic", "base_legendary"):
        e = man.get(name)
        if e is None:
            problems.append("anims.json: missing " + name)
            continue
        if (e.get("frame_w"), e.get("frame_h")) != (BW, BH):
            problems.append("%s: frame size %sx%s, expected 56x30" % (name, e.get("frame_w"), e.get("frame_h")))
        path = os.path.join(BASE_DIR, e.get("file", ""))
        if not os.path.isfile(path):
            problems.append("%s: file %s missing" % (name, e.get("file")))
            continue
        im = Image.open(path).convert("RGBA")
        if e.get("frames", 0) < 1 or e.get("fps", 0) <= 0 or im.size != (BW * e["frames"], BH):
            problems.append("%s: strip is %s, manifest says %s frames of 56x30" % (name, im.size, e.get("frames")))
            continue
        allowed = bases.SURFACE.get(name, set())
        for k in range(e["frames"]):
            fr = im.crop((k * BW, 0, (k + 1) * BW, BH))
            px = fr.load()
            a = alpha_set(fr)
            if any(px[x, y][3] not in (0, 255) for (x, y) in a):
                problems.append("%s frame %d: alpha other than 0/255" % (name, k))
            if not any(y == BH - 1 for (x, y) in a):
                problems.append("%s frame %d: does not touch the bottom row" % (name, k))
            bottom = [x for (x, y) in a if y == BH - 1]
            if bottom and abs((min(bottom) + max(bottom) + 1) / 2.0 - FEET[0]) > 1.0:
                problems.append("%s frame %d: not centred" % (name, k))
            if (FEET[0], FEET[1]) not in a or (FEET[0] - 1, FEET[1]) not in a:
                problems.append("%s frame %d: no surface under the feet point" % (name, k))
            bad = [(x, y) for (x, y) in a if 14 <= x <= 41 and y < FEET[1] and (x, y) not in allowed]
            if bad:
                problems.append("%s frame %d: %d ornament pixels inside the figure zone, e.g. %s" % (name, k, len(bad), bad[0]))
    for name in man:
        if name not in built:
            problems.append("anims.json: unexpected animation " + name)

    print("figures: %d written to %s" % (len(imgs), os.path.relpath(FIG_DIR, ROOT)))
    for name, e in man.items():
        print("  %-15s %2d frames @ %2d fps" % (name, e["frames"], e["fps"]))
    print("idle loops: %d, %d different timings" % (len(fman), len(timings)))
    print("most alike silhouettes:")
    for (iou, a, b) in pairs[:6]:
        print("  %.2f  %s / %s" % (iou, names[a], names[b]))
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
