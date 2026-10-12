"""Build and verify the environment art (section D of the rubber-hose contract).

Run from anywhere:  python tools/pixel/build_environment.py
Writes assets/sprites/tiles/*.png, assets/sprites/props/*.png and the contact
sheets tools/pixel/previews/rh_*.png. Exits non-zero if the contract is broken.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import props  # noqa: E402
import tiles  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
TILE_DIR = os.path.join(ROOT, "assets", "sprites", "tiles")
PROP_DIR = os.path.join(ROOT, "assets", "sprites", "props")
PREV = os.path.join(HERE, "previews")

# Files of the previous (flat side-view) contract that no longer exist.
OBSOLETE = [
    os.path.join(PROP_DIR, "ceiling_lamp_off.png"), os.path.join(PROP_DIR, "ceiling_lamp_on.png"),
    os.path.join(TILE_DIR, "ceiling.png"),
    os.path.join(PREV, "props.png"), os.path.join(PREV, "tiles.png"), os.path.join(PREV, "mockup_hall.png"),
]

# Props that stand on the floor: their bottom row must touch the ground.
GROUNDED = ["toilet", "sink", "sofa", "counter", "door_closed", "door_open", "shelf_a", "shelf_b", "locker",
            "table", "plant", "rug", "crate"]


def tile_fill(dst, tile, x0, y0, x1, y1):
    """Repeat a tile over the half-open rectangle, phase-locked to (x0, y0)."""
    tw, th = tile.size
    for y in range(y0, y1, th):
        for x in range(x0, x1, tw):
            piece = tile.crop((0, 0, min(tw, x1 - x), min(th, y1 - y)))
            dst.paste(piece, (x, y))


def room(t, wall, floor, w=427):
    """Empty room at camera size: 112 px of wall, 120 px of floor, front ledge."""
    h, fl = 240, 112
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    tile_fill(im, t[wall].img, 0, 8, w, fl)
    tile_fill(im, t["wall_top"].img, 0, 0, w, 8)
    tile_fill(im, t["trim"].img, 0, fl - 6, w, fl)
    tile_fill(im, t[floor].img, 0, fl, w, h - 8)
    tile_fill(im, t["front_ledge"].img, 0, h - 8, w, h)
    for x in (0, w - 14):
        tile_fill(im, t["pillar"].img, x, 8, x + 14, fl)
    return im


class _Ext:
    def __init__(self, img):
        self.img = img


def _first(folder, name, fw=None, fh=None, frame=0):
    """First (or given) frame of a sprite of another artist, for the mock-ups only."""
    path = os.path.join(ROOT, "assets", "sprites", folder, name + ".png")
    if not os.path.isfile(path):
        return None
    im = Image.open(path).convert("RGBA")
    if fw:
        im = im.crop((frame * fw, 0, frame * fw + fw, fh or im.size[1]))
    return im


def _amb_sizes():
    import json
    path = os.path.join(ROOT, "assets", "sprites", "ambient", "anims.json")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def externals(p):
    """Props plus machines, the player, figures and ambient frames."""
    q = dict(p)
    for n in range(1, 7):
        im = _first("machines", "machine_00%d_idle" % n, 48 if n < 5 else 72, None)
        if im is not None:
            q["m%d" % n] = _Ext(im)
    im = _first("anim", "player_idle", 40, 56)
    if im is not None:
        q["player"] = _Ext(im)
    for name, e in _amb_sizes().items():
        im = _first("ambient", name, e["frame_w"], e["frame_h"], min(2, e["frames"] - 1))
        if im is not None:
            q[name] = _Ext(im)
    fig_dir = os.path.join(ROOT, "assets", "sprites", "figures")
    figs = sorted(f[:-4] for f in os.listdir(fig_dir) if f.endswith(".png")) if os.path.isdir(fig_dir) else []
    bases = ["base_common", "base_uncommon", "base_rare", "base_epic", "base_legendary"]
    for i, f in enumerate(figs):
        im = _first("figures", f)
        dark = Image.new("RGBA", im.size, (14, 12, 22, 255))
        dark.putalpha(im.getchannel("A"))
        q["sil%d" % i] = _Ext(dark)
        base = _first("bases", bases[i % 5], 56, 30)
        if base is not None:
            both = Image.new("RGBA", (56, 58), (0, 0, 0, 0))
            both.alpha_composite(base, (0, 28))
            both.alpha_composite(im, (8, 0))
            q["fig%d" % i] = _Ext(both)
    return q


def stage(im, p, wall_items, floor_items):
    """wall_items: (name, x, top). floor_items: (name, x, bottom), depth-sorted
    (the rug is always drawn first). Unknown names are skipped."""
    for (name, x, top) in wall_items:
        if name in p:
            im.alpha_composite(p[name].img, (x, top))
    draw = [(b, n, x) for (n, x, b) in floor_items if n in p]
    for (b, n, x) in [d for d in draw if d[1] == "rug"] + sorted([d for d in draw if d[1] != "rug"],
                                                                key=lambda d: d[0]):
        im.alpha_composite(p[n].img, (x, b - p[n].img.size[1]))
    return im


def _join(strips, path, scale=3):
    total = Image.new("RGBA", (sum(s.size[0] for s in strips) + 4 * (len(strips) - 1), 240), (0, 0, 0, 255))
    x = 0
    for s in strips:
        total.paste(s, (x, 0))
        x += s.size[0] + 4
    total.resize((total.size[0] * scale, 240 * scale), Image.NEAREST).save(path)


def mockups(t, p):
    """Rooms composed like the game does, with the real machines, player,
    figures (dark silhouettes and discovered ones) and ambient sprites."""
    fl = 112
    p = externals(p)
    bath = stage(room(t, "wall_bath", "floor_bath", 180), p,
                 [("lamp_on", 30, 8), ("amb_wall_clock", 96, 24), ("poster_c", 126, 26),
                  ("gallery_shelf", 96, 82), ("gallery_shelf", 130, 82), ("amb_spider", 80, 8),
                  ("amb_tap_drip", 66, 60), ("amb_calendar", 156, 58)],
                 [("toilet", 14, fl + 18), ("sink", 56, fl + 10), ("player", 80, 176), ("amb_rubber_duck", 110, 90),
                  ("amb_bubbles", 76, 96)])
    hall = stage(room(t, "wall_hall", "floor_hall"), p,
                 [("sign_gacha", 190, 6), ("poster_a", 14, 42), ("power_switch_on", 48, 54), ("poster_d", 396, 40),
                  ("poster_b", 366, 40), ("lamp_on", 110, 8), ("lamp_off", 300, 8), ("amb_lantern", 96, 12),
                  ("amb_dust_motes", 100, 50), ("amb_teru_bozu", 172, 8)],
                 [("amb_vending", 70, fl + 14), ("plant", 22, fl + 14), ("m1", 136, fl + 14), ("m2", 206, fl + 14),
                  ("m3", 276, fl + 14), ("m4", 346, fl + 14), ("rug", 240, 204), ("player", 196, 178),
                  ("crate", 392, 150), ("key", 150, 215), ("amb_pinwheel", 120, fl + 16),
                  ("amb_toy_train", 60, 200), ("amb_jack_in_box", 20, 190)])
    _join([bath, hall], os.path.join(PREV, "rh_mockup_hall.png"), 3)

    shelves = [("gallery_shelf", x, y) for y in (51, 107) for x in range(14, 290, 34)]
    figs = []
    for i in range(8):
        figs.append((("fig%d" if i in (0, 5) else "sil%d") % i, 16 + i * 34 - (8 if i in (0, 5) else 0), 56))
        figs.append((("fig%d" if i == 3 else "sil%d") % (i + 12), 16 + i * 34 - (8 if i == 3 else 0), 112))
    gal = room(t, "wall_gallery", "floor_gallery", 300)
    stage(gal, p, shelves + [("lamp_on", 250, 8), ("amb_spider", 40, 8)], [])
    for (name, x, bottom) in figs:
        if name in p:
            gal.alpha_composite(p[name].img, (x, bottom - p[name].img.size[1] + (20 if name.startswith("fig") else 0)))
    stage(gal, p, [], [("rug", 190, 190), ("amb_cat_sleep", 220, 180), ("plant", 4, fl + 14), ("player", 110, 180),
                       ("amb_toy_train", 150, 215), ("amb_spinning_top", 60, 200), ("amb_akabeko", 30, 160)])
    rec = stage(room(t, "wall_reception", "floor_hall", 260), p,
                [("poster_b", 222, 40), ("amb_exit_sign", 150, 9), ("lamp_on", 110, 8), ("amb_calendar", 204, 44),
                 ("amb_noren", 2, 22)],
                [("amb_arcade_cab", 16, fl + 14), ("shelf_b", 66, fl + 8), ("door_closed", 140, fl),
                 ("counter", 50, 176), ("plant", 226, fl + 14), ("player", 90, 204)])
    for (name, x, bottom) in (("computer_on", 58, 138), ("amb_radio", 96, 138), ("amb_maneki_neko", 124, 137),
                              ("amb_mini_gacha", 28, 150)):
        if name in p:
            rec.alpha_composite(p[name].img, (x, bottom - p[name].img.size[1]))
    _join([gal, rec], os.path.join(PREV, "rh_mockup_rooms.png"), 3)

    staff = stage(room(t, "wall_staff", "floor_staff", 300), p,
                  [("poster_c", 76, 40), ("power_switch_off", 110, 56), ("lamp_on", 60, 8),
                   ("amb_string_lights", 100, 9), ("amb_koinobori", 130, 26), ("amb_wall_clock", 2, 30)],
                  [("locker", 18, fl + 6), ("locker", 48, fl + 6), ("sofa", 100, fl + 22), ("shelf_a", 226, fl + 8),
                   ("table", 180, 196), ("crate", 30, 190), ("player", 110, 190), ("amb_tv", 70, 200),
                   ("amb_cymbal_monkey", 250, 180)])
    for (name, x, bottom) in (("amb_fish_bowl", 184, 180), ("amb_mug_steam", 208, 181)):
        if name in p:
            staff.alpha_composite(p[name].img, (x, bottom - p[name].img.size[1]))
    cor = stage(room(t, "wall_corridor", "floor_hall", 110), p,
                [("poster_d", 16, 40), ("amb_furin", 80, 8), ("amb_calendar", 60, 44)],
                [("player", 30, 170), ("amb_balloon", 80, 140)])
    dark = Image.alpha_composite(bath, Image.new("RGBA", bath.size, (20, 26, 60, 150)))
    _join([staff, cor, dark], os.path.join(PREV, "rh_mockup_staff.png"), 3)


def verify(folder, sizes, opaque):
    problems = []
    for name, size in sizes.items():
        path = os.path.join(folder, name + ".png")
        if not os.path.isfile(path):
            problems.append("missing " + path)
            continue
        im = Image.open(path)
        if im.mode != "RGBA":
            problems.append("%s: mode %s, expected RGBA" % (name, im.mode))
            continue
        if im.size != size:
            problems.append("%s: size %s, expected %s" % (name, im.size, size))
        alphas = {i for i, n in enumerate(im.getchannel("A").histogram()) if n}
        if not alphas <= {0, 255}:
            problems.append("%s: partial alpha" % name)
        if opaque and alphas != {255}:
            problems.append("%s: tile is not fully opaque" % name)
        if not opaque and 255 not in alphas:
            problems.append("%s: empty sprite" % name)
    return problems


def verify_extra():
    problems = []
    for name in GROUNDED:
        im = Image.open(os.path.join(PROP_DIR, name + ".png"))
        w, h = im.size
        if not any(im.getpixel((x, h - 1))[3] for x in range(w)):
            problems.append("%s: bottom row is empty (must touch the floor)" % name)
    # the computer may only differ inside the screen rectangle (and its power led)
    a = Image.open(os.path.join(PROP_DIR, "computer_off.png"))
    b = Image.open(os.path.join(PROP_DIR, "computer_on.png"))
    sx, sy, sw, sh = props.COMPUTER_SCREEN
    for y in range(a.size[1]):
        for x in range(a.size[0]):
            inside = sx <= x < sx + sw and sy <= y < sy + sh
            if not inside and (x, y) != props.COMPUTER_LED and a.getpixel((x, y)) != b.getpixel((x, y)):
                problems.append("computer: on/off differ outside the screen at %d,%d" % (x, y))
    # lamps: the cord starts at the top centre
    for name in ("lamp_off", "lamp_on"):
        im = Image.open(os.path.join(PROP_DIR, name + ".png"))
        if not (im.getpixel((14, 0))[3] and im.getpixel((15, 0))[3]):
            problems.append("%s: cord does not start at the top centre" % name)
    return problems


def main():
    os.makedirs(PREV, exist_ok=True)
    t = tiles.build_all()
    p = props.build_all()
    problems = []
    for name, spr in t.items():
        if spr.img.size != tiles.SIZES[name]:
            problems.append("tile %s drawn at %s" % (name, spr.img.size))
        spr.save(os.path.join(TILE_DIR, name + ".png"))
    for name, spr in p.items():
        if spr.img.size != props.SIZES[name]:
            problems.append("prop %s drawn at %s" % (name, spr.img.size))
        spr.save(os.path.join(PROP_DIR, name + ".png"))
    for path in OBSOLETE:
        for f in (path, path + ".import"):
            if os.path.isfile(f):
                os.remove(f)
    tiles.previews(t, PREV)
    props.previews(p, PREV)
    mockups(t, p)
    problems += verify(TILE_DIR, tiles.SIZES, True)
    problems += verify(PROP_DIR, props.SIZES, False)
    if not problems:
        problems += verify_extra()
    # stray PNGs that the contract does not list
    for folder, sizes in ((TILE_DIR, tiles.SIZES), (PROP_DIR, props.SIZES)):
        for f in sorted(os.listdir(folder)):
            if f.endswith(".png") and f[:-4] not in sizes:
                problems.append("unlisted file %s" % os.path.join(folder, f))
    print("tiles: %d, props: %d" % (len(t), len(p)))
    print("computer screen (x, y, w, h):", props.COMPUTER_SCREEN)
    print("door opening (x, y, w, h):", props.DOOR_OPENING, "clear passage when open:", props.DOOR_PASSAGE)
    print("lamp light source (x, y):", props.LAMP_LIGHT)
    print("footprint depths:", props.FOOTPRINT_DEPTH)
    if problems:
        print("PROBLEMS:")
        for q in problems:
            print("  - " + q)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
