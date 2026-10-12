"""The helper robot: a small rubber-hose tin toy seen from the front, slightly
from above. Square steel head with pie eyes, blue body with a gauge, long
noodle arms with white gloves, red boots and a mustard butterfly wind-up key
turning on top of its head. 28 x 34 frames, anchored bottom centre.

`work` reaches to the robot's RIGHT (screen right) and cranks in a circle.
"""
import math

from pixlib import box

from anim_lib import (Cv, oval, disc, rect, hose, glove, rnd, shift,
                      INK, RED, DRED, RED_HI, MUSTARD, MUSTARD_SH, MUSTARD_HI, BLUE, NAVY, SKY,
                      STEEL, STEEL_HI, DSTEEL, GLOVE, PINK, WHITE)

W, H = 28, 34
CX = 14
GROUND = 33

# The crank hand of `work` circles around this point (frame pixels).
WORK_CENTRE = (22, 21)
WORK_RADIUS = 2

DEFAULT = dict(x=0, y=0, head=(0, 0), key=0, eyes="open", look=(0, 0), mouth="smile",
               hl=(-5, 8), hr=(5, 8), bl=-2.0, br=2.0, sq=0, lamp=False, puff=0)


def P(**kw):
    d = dict(DEFAULT)
    d.update(kw)
    return d


def boot(cv, x0):
    m = {q for q in oval(x0, 28, x0 + 6, 35) if q[1] <= 32}
    cv.blob(m, RED)
    cv.fill({q for q in m if q[1] == 32}, DRED)
    cv.px[(x0 + 2, 29)] = RED_HI


def key(cv, kx, base_y, phase):
    """Butterfly wind-up key on a collar: two looped wings on a stem. Four
    phases make half a turn (flat on, three-quarter, edge on, three-quarter)."""
    ph = phase % 4
    top = base_y - 6
    cv.blob(rect(kx - 2, base_y, kx + 1, base_y), STEEL_HI)          # collar on the head
    stem = rect(kx - 1, top + 2, kx, base_y - 1)
    if ph == 0:
        wings = oval(kx - 5, top, kx - 2, top + 4) | oval(kx + 1, top, kx + 4, top + 4)
        holes = rect(kx - 4, top + 1, kx - 3, top + 2) | rect(kx + 2, top + 1, kx + 3, top + 2)
    elif ph == 2:
        wings = rect(kx - 1, top, kx, top + 4)
        holes = set()
    else:
        wings = oval(kx - 4, top, kx - 2, top + 4) | oval(kx + 1, top, kx + 3, top + 4)
        holes = rect(kx - 3, top + 1, kx - 3, top + 2) | rect(kx + 2, top + 1, kx + 2, top + 2)
    shape = wings | stem
    cv.blob(shape, MUSTARD)
    cv.fill({q for q in shape - shift(shape, -1, -1) if q in wings}, MUSTARD_SH)
    cv.fill(holes, INK)
    if ph == 0:
        cv.px[(kx - 4, top)] = MUSTARD_HI
        cv.px[(kx + 2, top)] = MUSTARD_HI
    elif ph == 1:
        cv.px[(kx - 3, top)] = MUSTARD_HI
    elif ph == 3:
        cv.px[(kx + 2, top)] = MUSTARD_HI
    else:
        cv.fill(rect(kx - 1, top, kx - 1, top + 3), MUSTARD_HI)


def draw(p):
    cv = Cv()
    bx = CX + rnd(p["x"])
    by = rnd(p["y"])
    sq = rnd(p["sq"])
    hx = bx + rnd(p["head"][0])
    hy = by + rnd(p["head"][1]) + sq
    # legs and boots
    cv.fill(hose((bx - 3, 25 + by), (10, 29), 0.0, 2), INK)
    cv.fill(hose((bx + 2, 25 + by), (17, 29), 0.0, 2), INK)
    boot(cv, 6)
    boot(cv, 15)
    # arms: long thin hoses from the shoulders, behind the body
    sh_l = (bx - 5, 19 + by + sq)
    sh_r = (bx + 3, 19 + by + sq)
    hands = []
    for sh, rel, bend in ((sh_l, p["hl"], p["bl"]), (sh_r, p["hr"], p["br"])):
        hand = (sh[0] + rel[0], sh[1] + rel[1])
        cv.fill(hose(sh, hand, bend, 2), INK)
        hands.append((sh, hand))
    # body
    body = box(bx - 5, 18 + by + sq, bx + 4, 26 + by, 2)
    cv.blob(body, BLUE)
    cv.fill(body - shift(body, -2, -1), NAVY)
    cv.fill({q for q in body if q[1] == 19 + by + sq and bx - 4 < q[0] < bx + 2}, SKY)
    gy = 22 + by + (sq + 1) // 2
    gauge = disc(bx - 2, gy, 1.6)
    cv.blob(gauge, MUSTARD)
    cv.px[(bx - 2, gy)] = INK
    cv.px[(bx - 1, gy - 1)] = INK
    cv.fill(rect(bx + 2, gy - 1, bx + 3, gy), RED if not p["lamp"] else RED_HI)
    cv.dots([(bx + 1, 25 + by), (bx - 1, 25 + by), (bx - 3, 25 + by)], NAVY)
    # head
    head = box(hx - 8, 8 + hy, hx + 7, 17 + hy, 3)
    for ex in (hx - 10, hx + 8):                      # ear bolts
        cv.blob(rect(ex, 11 + hy, ex + 1, 13 + hy), RED)
    cv.blob(head, STEEL)
    cv.fill({q for q in head if q[1] <= 9 + hy}, STEEL_HI)
    cv.fill(head - shift(head, -1, -1), DSTEEL)
    cv.dots([(hx - 6, 15 + hy), (hx + 5, 10 + hy)], DSTEEL)          # rivets
    # eyes: tall ovals touching each other
    le = oval(hx - 4, 10 + hy, hx - 1, 15 + hy)
    re = oval(hx + 1, 10 + hy, hx + 4, 15 + hy)
    lx, ly = rnd(p["look"][0]), rnd(p["look"][1])
    if p["eyes"] == "open":
        cv.blob(le, GLOVE)
        cv.blob(re, GLOVE)
        cv.fill(rect(hx - 3 + lx, 12 + hy + ly, hx - 2 + lx, 14 + hy + ly), INK, le)
        cv.fill(rect(hx + 2 + lx, 12 + hy + ly, hx + 3 + lx, 14 + hy + ly), INK, re)
    elif p["eyes"] == "blink":
        cv.dots([(-4, 13), (-3, 14), (-2, 14), (-1, 13), (1, 13), (2, 14), (3, 14), (4, 13)], INK, hx, hy)
    elif p["eyes"] == "happy":
        cv.dots([(-4, 13), (-3, 12), (-2, 12), (-1, 13), (1, 13), (2, 12), (3, 12), (4, 13)], INK, hx, hy)
    if p["mouth"] == "smile":
        cv.dots([(-2, 16), (-1, 17), (0, 17), (1, 16)], INK, hx, hy)
    else:
        cv.dots([(-1, 16), (0, 16), (-1, 17), (0, 17)], INK, hx, hy)
    key(cv, hx, 7 + hy, p["key"])
    # gloves on top
    for sh, hand in hands:
        d = (hand[0] - sh[0], hand[1] - sh[1])
        glove(cv, hand, d, "fist", r=2.4, thumb=0)
    # a puff of steam from the ear bolt while it works hard
    if p["puff"]:
        k = p["puff"]
        cv.blob(disc(hx - 9 - k // 2, 8 + hy - 2 * k, 1.2 if k < 3 else 0.6), WHITE)
    return cv


def render(poses, name):
    return [draw(p).image(W, H, name="%s[%d]" % (name, i)) for i, p in enumerate(poses)]


def idle():
    """16 frames: tin-toy tick bob, long arms swaying, the key winding down, a blink, glances."""
    bob = [0, 0, 1, 1, 0, 0, 0, 0]
    poses = []
    for i in range(16):
        b = bob[i % 8]
        prev = bob[(i - 1) % 8]
        sway = (0, 1, 1, 0, 0, -1, -1, 0)[i % 8]
        p = P(y=b, key=i // 4, hl=(-5 - b + min(sway, 0), 8 - (b - prev)), hr=(5 + b + max(sway, 0), 8 - (b - prev)),
              bl=-2.0 - b * 0.8, br=2.0 + b * 0.8)
        if i == 9:
            p["eyes"] = "blink"
        if i in (3, 4, 5, 6):
            p["look"] = (1, 0)
        if i in (12, 13, 14):
            p["look"] = (-1, 0)
        if i in (4, 5):
            p["head"] = (1, 0)
        if i == 13:
            p["head"] = (-1, 0)
        poses.append(p)
    return render(poses, "robot_idle"), 8, True


def work_hand(i, n=8):
    a = 2 * math.pi * i / n
    return (WORK_CENTRE[0] + rnd(WORK_RADIUS * math.cos(a)), WORK_CENTRE[1] + rnd(WORK_RADIUS * math.sin(a)))


def work():
    """8 frames: leans right, the right hand turns a crank in a circle, the body
    pumps with it, the free arm swings as a counterweight, the key spins."""
    poses = []
    for i in range(8):
        a = 2 * math.pi * i / 8
        down = 1 if math.sin(a) > 0.3 else 0
        hand = work_hand(i)
        x = -2
        sh_r = (CX + x + 3, 19 + down)
        p = P(x=x, y=down, head=(1 if math.cos(a) > -0.3 else 0, 0), key=i, look=(1, 1 if down else 0),
              hr=(hand[0] - sh_r[0], hand[1] - sh_r[1]), br=-2.0 * math.sin(a) - 1.5,
              hl=(-3 - rnd(1.4 * math.cos(a)), 6 - rnd(2.2 * math.sin(a))), bl=-2.5 + math.sin(a),
              lamp=(i % 4 < 2), eyes="open", mouth="o" if down else "smile",
              puff=(i - 4) if i in (5, 6, 7) else 0)
        poses.append(p)
    return render(poses, "robot_work"), 12, True
