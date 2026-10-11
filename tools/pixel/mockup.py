"""Composed 320 x 180 hall mock-up (x4) to check that everything fits at game scale.

Layout used by the game: 8 px ceiling strip, 140 px back wall, 32 px floor.
"""
import os

from PIL import Image


def build(spr_dir, prev_dir):
    def load(rel):
        return Image.open(os.path.join(spr_dir, rel.replace("/", os.sep))).convert("RGBA")

    W, H = 320, 180
    floor_y = 148
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    wall, floor, trim, ceil, pillar = (load("tiles/wall_hall.png"), load("tiles/floor_hall.png"),
                                       load("tiles/trim.png"), load("tiles/ceiling.png"), load("tiles/pillar.png"))
    for y in range(8, floor_y, 16):
        for x in range(0, W, 16):
            img.paste(wall, (x, y))
    for y in range(floor_y, H, 16):
        for x in range(0, W, 16):
            img.paste(floor, (x, y))
    for x in range(0, W, 16):
        img.paste(ceil, (x, 0))
        img.paste(trim, (x, floor_y - 6))
    for y in range(8, floor_y, 16):
        img.paste(pillar, (0, y))

    def stand(rel, cx, lift=0):
        im = load(rel)
        img.alpha_composite(im, (cx - im.size[0] // 2, floor_y + 6 - im.size[1] - lift))
        return cx - im.size[0] // 2, floor_y + 6 - im.size[1] - lift

    def hang(rel, x, y):
        img.alpha_composite(load(rel), (x, y))

    hang("props/ceiling_lamp_on.png", 60, 8)
    hang("props/ceiling_lamp_off.png", 200, 8)
    hang("props/sign_gacha.png", 112, 18)
    hang("props/poster_a.png", 18, 50)
    hang("props/poster_c.png", 286, 46)
    hang("props/power_switch_off.png", 262, 84)
    stand("props/shelf_a.png", 40)
    stand("props/plant.png", 300)
    for i, cx in enumerate((84, 124, 164)):
        n = i + 1
        ox, oy = stand("machines/machine_00%d.png" % n, cx)
        if n != 3:
            hang_im = load("machines/machine_00%d_lit.png" % n)
            img.alpha_composite(hang_im, (ox, oy))
        img.alpha_composite(load("machines/gacha_knob.png"), (ox + 12, oy + 32))
    ox, oy = stand("machines/machine_005.png", 214)
    img.alpha_composite(load("machines/machine_005_lit.png"), (ox, oy))
    img.alpha_composite(load("machines/claw_open.png"), (ox + 18, oy + 10))
    ox, oy = stand("machines/machine_006.png", 272)
    img.alpha_composite(load("machines/plinko_ball.png"), (ox + 25, oy + 23))
    # a few figures on the floor for scale
    figs = sorted(f for f in os.listdir(os.path.join(spr_dir, "figures")) if f.endswith(".png"))
    for k, cx in ((0, 104), (9, 144), (19, 190), (24, 244)):
        im = load("figures/" + figs[k])
        img.alpha_composite(im, (cx - 16, floor_y + 24 - 32))
    out = img.resize((W * 4, H * 4), Image.NEAREST)
    os.makedirs(prev_dir, exist_ok=True)
    out.save(os.path.join(prev_dir, "mockup_hall.png"))
