"""Builds every static sprite of GachaNight (figures, machines, props, tiles).

Run:  python tools/pixel/build_sprites.py [figures|machines|props|tiles ...]
Deterministic and re-runnable. Writes contact sheets (x4) to tools/pixel/previews/
and verifies that every file of the art contract exists with its exact size.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

from PIL import Image  # noqa: E402

import pixlib  # noqa: E402
from pixlib import Spr, sheet  # noqa: E402

SPR = os.path.join(ROOT, "assets", "sprites")
PREV = os.path.join(HERE, "previews")


def load_figures():
    with open(os.path.join(ROOT, "data", "figures.json"), encoding="utf-8") as fh:
        return json.load(fh)["figures"]


def silhouette(img):
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    src, dst = img.load(), out.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if src[x, y][3]:
                dst[x, y] = pixlib.INK + (255,)
    return out


def build_figures():
    import figures
    imgs = []
    for fig in load_figures():
        s = figures.build_figure(fig)
        s.save(os.path.join(SPR, "figures", fig["id"] + ".png"))
        imgs.append(s.img)
    if figures.OVERFLOW:
        print('FIGURES TOO BIG: ' + '; '.join(figures.OVERFLOW))
    sheet(imgs, os.path.join(PREV, "figures.png"), cols=10, scale=4)
    sheet([silhouette(i) for i in imgs], os.path.join(PREV, "figures_silhouettes.png"), cols=10, scale=4)
    return {"figures/%s.png" % f["id"]: (32, 32) for f in load_figures()}


def build_machines():
    import machines
    out = machines.build_all()
    for name, s in out.items():
        s.save(os.path.join(SPR, "machines", name + ".png"))
    machines.previews(out, PREV)
    return {"machines/%s.png" % n: machines.SIZES[n] for n in machines.SIZES}


def build_props():
    import props
    out = props.build_all()
    for name, s in out.items():
        s.save(os.path.join(SPR, "props", name + ".png"))
    props.previews(out, PREV)
    return {"props/%s.png" % n: props.SIZES[n] for n in props.SIZES}


def build_tiles():
    import tiles
    out = tiles.build_all()
    for name, s in out.items():
        s.save(os.path.join(SPR, "tiles", name + ".png"))
    tiles.previews(out, PREV)
    return {"tiles/%s.png" % n: tiles.SIZES[n] for n in tiles.SIZES}


def expected():
    import machines
    import props
    import tiles
    exp = {"figures/%s.png" % f["id"]: (32, 32) for f in load_figures()}
    exp.update({"machines/%s.png" % n: v for n, v in machines.SIZES.items()})
    exp.update({"props/%s.png" % n: v for n, v in props.SIZES.items()})
    exp.update({"tiles/%s.png" % n: v for n, v in tiles.SIZES.items()})
    return exp


def verify():
    problems = []
    exp = expected()
    for rel, size in sorted(exp.items()):
        p = os.path.join(SPR, rel.replace("/", os.sep))
        if not os.path.isfile(p):
            problems.append("MISSING  %s" % rel)
            continue
        im = Image.open(p)
        if im.size != size:
            problems.append("SIZE     %s is %dx%d, expected %dx%d" % (rel, im.size[0], im.size[1], size[0], size[1]))
        if im.mode != "RGBA":
            problems.append("MODE     %s is %s, expected RGBA" % (rel, im.mode))
            continue
        alphas = set(im.getchannel("A").tobytes())
        if not alphas <= {0, 255}:
            problems.append("ALPHA    %s has partial alpha" % rel)
        if rel.startswith("tiles/") and alphas != {255}:
            problems.append("OPAQUE   %s must be fully opaque" % rel)
        if not rel.startswith("tiles/") and 255 not in alphas:
            problems.append("EMPTY    %s has no opaque pixel" % rel)
        if rel.startswith("figures/"):
            bb = im.getbbox()
            if bb[3] != 32:
                problems.append("GROUND   %s does not touch the bottom row" % rel)
            if abs((bb[0] + bb[2]) - 32) > 1:
                problems.append("CENTRE   %s is not horizontally centred" % rel)
    # figures must have distinct silhouettes
    sil = {}
    for rel in exp:
        if rel.startswith("figures/"):
            p = os.path.join(SPR, rel.replace("/", os.sep))
            if os.path.isfile(p):
                key = Image.open(p).getchannel("A").tobytes()
                if key in sil:
                    problems.append("SILHOUETTE %s equals %s" % (rel, sil[key]))
                sil[key] = rel
    if problems:
        print("VERIFY FAILED (%d problems)" % len(problems))
        for line in problems:
            print("  " + line)
        return 1
    print("VERIFY OK: %d files present with exact sizes" % len(exp))
    return 0


def main():
    todo = sys.argv[1:] or ["figures", "machines", "props", "tiles", "mockup"]
    if "figures" in todo:
        build_figures()
    if "machines" in todo:
        build_machines()
    if "props" in todo:
        build_props()
    if "tiles" in todo:
        build_tiles()
    if "mockup" in todo:
        import mockup
        mockup.build(SPR, PREV)
    if "noverify" in todo:
        return 0
    return verify()


if __name__ == "__main__":
    sys.exit(main())
