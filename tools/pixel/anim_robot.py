"""The worker robot: a small tin wind-up toy seen from the front, 20 x 24 frames.

Built from parts (feet, legs, body, head, visor eyes, antenna, ear key, arms)
placed per frame from a pose table.
"""
from anim_lib import (Layer, DARK, CORAL, CORAL_HI, CORAL_SH, MINT, MINT_HI, MINT_SH, TEAL, TEAL_HI,
                      TEAL_SH, CREAM, CREAM_SH, WHITE, MUSTARD, MUSTARD_HI, MUSTARD_SH, GOLD_HI)

W, H = 20, 24


def draw(p):
    fy = p.get("feet", 0)
    by = p.get("body", 0)
    hy = p.get("head", 0)
    spread = p.get("spread", 0)
    adx, ady = p.get("ant", (0, 0))
    eyes = p.get("eyes", "open")
    out = Layer()

    # ear key (left of the head) and bolt (right)
    key = Layer()
    key.set(4, 12 + hy, CREAM_SH)
    if p.get("key", "wide") == "wide":
        for x in (2, 3):
            for y in (10, 11, 13, 14):
                key.set(x, y + hy, MUSTARD)
        key.set(3, 12 + hy, MUSTARD_SH)
        key.set(2, 10 + hy, MUSTARD_HI)
    else:
        key.set(2, 12 + hy, MUSTARD)
        key.set(3, 12 + hy, MUSTARD)
    key.set(15, 12 + hy, CREAM_SH)
    out.stamp(key)

    # antenna stem
    stem = Layer()
    stem.rect(9, 7 + hy, 10, 8 + hy, CREAM_SH)
    out.stamp(stem)

    # legs (only visible when the body is stretched above the feet) and feet
    legs = Layer()
    for y in range(21 + by, 21 + fy):
        legs.rect(7 - spread, y, 8 - spread, y, DARK)
        legs.rect(11 + spread, y, 12 + spread, y, DARK)
    for y in range(16 + hy, 16 + by):
        legs.rect(8, y, 11, y, DARK)
    out.stamp(legs)
    feet = Layer()
    for x0 in (6 - spread, 11 + spread):
        feet.rect(x0, 21 + fy, x0 + 2, 22 + fy, CORAL)
        feet.rect(x0, 22 + fy, x0 + 2, 22 + fy, CORAL_SH)
        feet.set(x0, 21 + fy, CORAL_HI)
    out.stamp(feet)

    # body
    body = Layer()
    body.rect(6, 16 + by, 13, 20 + by, TEAL)
    body.rect(6, 16 + by, 6, 19 + by, TEAL_HI)
    body.rect(13, 16 + by, 13, 20 + by, TEAL_SH)
    body.rect(6, 20 + by, 13, 20 + by, TEAL_SH)
    body.rect(8, 17 + by, 11, 19 + by, CREAM)
    body.rect(8, 19 + by, 11, 19 + by, CREAM_SH)
    body.set(8, 18 + by, GOLD_HI if p.get("lamp", 1) else MUSTARD_SH)
    body.rect(10, 18 + by, 11, 18 + by, CORAL)
    out.stamp(body)

    # head with visor
    head = Layer()
    head.rect(5, 9 + hy, 14, 15 + hy, MINT)
    head.rect(5, 9 + hy, 14, 9 + hy, MINT_HI)
    head.rect(5, 9 + hy, 5, 14 + hy, MINT_HI)
    head.rect(14, 10 + hy, 14, 15 + hy, MINT_SH)
    head.rect(5, 15 + hy, 14, 15 + hy, MINT_SH)
    for c in ((5, 9), (14, 9), (5, 15), (14, 15)):
        del head.px[(c[0], c[1] + hy)]
    head.rect(6, 11 + hy, 13, 13 + hy, DARK)
    ex = 1 if eyes == "right" else 0
    for x0 in (7 + ex, 11 + ex):
        if eyes == "blink":
            head.rect(x0, 12 + hy, x0 + 1, 12 + hy, MUSTARD_SH)
        elif eyes == "happy":
            head.rect(x0, 11 + hy, x0 + 1, 11 + hy, MUSTARD_HI)
        else:
            head.rect(x0, 11 + hy, x0 + 1, 12 + hy, MUSTARD_HI)
            head.set(x0, 11 + hy, WHITE)
    out.stamp(head)

    # arms: shoulder on the body side, hand anywhere
    for sx, key_name, rest in ((5, "l_hand", (5, 20)), (15, "r_hand", (15, 20))):
        hx, hyy = p.get(key_name, (rest[0], rest[1] + by))
        arm = Layer()
        arm.limb((sx, 17 + by), (hx, hyy), 2, CREAM_SH)
        arm.rect(hx - 1, hyy - 1, hx, hyy, CORAL)
        arm.set(hx - 1, hyy - 1, CORAL_HI)
        out.stamp(arm)

    # antenna ball
    ball = Layer()
    bx, byy = 8 + adx, 4 + hy + ady
    ball.rect(bx + 1, byy, bx + 2, byy + 2, CORAL)
    ball.rect(bx, byy + 1, bx + 3, byy + 1, CORAL)
    ball.set(bx + 1, byy, CORAL_HI)
    ball.set(bx + 3, byy + 1, CORAL_SH)
    ball.set(bx + 2, byy + 2, CORAL_SH)
    out.stamp(ball)
    return out


def _frames(poses, name):
    return [draw(p).to_image(W, H, name="%s[%d]" % (name, i)) for i, p in enumerate(poses)]


def idle():
    head = [0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0]
    ant = [(0, 0), (0, 0), (0, 0), (0, 0), (1, 0), (-1, 0), (0, 0), (0, 0), (0, 0), (0, 0), (-1, 0), (1, 0)]
    poses = []
    for f in range(12):
        poses.append({"head": head[f], "ant": ant[f],
                      "eyes": "blink" if f == 7 else "open",
                      "key": "wide" if f < 6 else "thin",
                      "lamp": 0 if head[f] else 1})
    return _frames(poses, "robot_idle"), 6, True


def work():
    #        feet body head spread ant      eyes     key     r_hand    l_hand
    table = [(0, 1, 2, 1, (0, 1), "right", "wide", (16, 19), (4, 21)),    # squash, anticipation
             (0, -1, -2, 0, (0, 1), "right", "thin", (16, 17), (5, 19)),  # launch, stretched
             (-2, -3, -3, 0, (-1, 0), "right", "wide", (17, 14), (4, 16)),  # rising, hand over the crank
             (-3, -3, -3, 0, (0, 0), "right", "thin", (18, 16), (4, 16)),   # apex
             (-2, -2, -3, 0, (1, 0), "right", "wide", (18, 18), (4, 17)),   # falling, head lags
             (0, 1, 2, 1, (1, 1), "blink", "thin", (17, 20), (4, 21)),    # landing squash
             (0, -1, -1, 0, (-1, 0), "open", "wide", (16, 19), (5, 19)),  # rebound
             (0, 0, 0, 0, (0, 0), "right", "thin", (16, 18), (5, 20))]    # settle
    poses = []
    for feet, body, head, spread, ant, eyes, key, rh, lh in table:
        poses.append({"feet": feet, "body": body, "head": head, "spread": spread, "ant": ant,
                      "eyes": eyes, "key": key, "r_hand": rh, "l_hand": lh, "lamp": 1 if feet < 0 else 0})
    return _frames(poses, "robot_work"), 12, True
