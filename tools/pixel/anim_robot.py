"""The helper robot: a little cleaning machine in the old-cartoon look, seen
from the front and slightly from above. Dark glossy dome head with two bright
pie-cut eyes and a lamp on a springy antenna, a brass collar, a squat grey body
with a maroon stripe and a gauge, two rubber wheels, a copper tank on its back
and one ribbed hose arm that ends in a white glove. 42 x 51 frames, anchored
bottom centre.

`work` reaches to the robot's RIGHT (screen right) and cranks in a circle.
"""
import math

from pixlib import box

from anim_lib import (Cv, oval, disc, rect, hose, glove, rnd, shift, ribbed_hose, bend_ctrl, shade_px,
                      INK, INK_SOFT, PAPER, GREY, BLACK, BRASS, COPPER, RED, WHITE)

W, H = 42, 51
CX = 21
GROUND = 50

# The crank hand of `work` circles around this point (frame pixels).
WORK_CENTRE = (33, 31)
WORK_RADIUS = 3

DOME = (BLACK[0], BLACK[2], GREY[0], GREY[1])
SHELL = (GREY[1], GREY[2], GREY[3], GREY[4])
SKIRT = (GREY[0], GREY[1], GREY[2], GREY[3])
TANK = (COPPER[0], COPPER[1], COPPER[2], COPPER[3])
COLLAR = (BRASS[0], BRASS[1], BRASS[2], BRASS[3])

DEFAULT = dict(x=0, y=0, head=(0, 0), ant=0, eyes="open", look=(0, 0), mouth="smile",
               hr=(5, 11), br=3.0, lamp=False, puff=0, roll=0)


def P(**kw):
    d = dict(DEFAULT)
    d.update(kw)
    return d


def wheel(cv, x0, roll):
    m = oval(x0, 42, x0 + 7, 49)
    cv.blob(m, BLACK[2])
    cv.fill(m - shift(m, 1, 1), BLACK[3])
    cv.fill(m - shift(m, -1, -1), BLACK[0])
    cx, cy = x0 + 3, 45
    cv.fill(rect(cx, cy, cx + 1, cy + 1), GREY[3])
    ox, oy = ((0, 0), (1, 0), (1, 1), (0, 1))[roll % 4]          # the hub bolt goes round
    cv.px[(cx + ox, cy + oy)] = GREY[1]


def draw(p):
    cv = Cv()
    bx = CX + rnd(p["x"])
    by = rnd(p["y"])
    hx = bx + rnd(p["head"][0])
    hy = by + rnd(p["head"][1])
    # copper tank on the back, with its pipe into the dome
    tank = box(bx - 17, 26 + by, bx - 12, 40 + by, 2)
    cv.fill(hose((bx - 15, 25 + by), (hx - 9, 20 + hy), -2.0, 2), INK)
    cv.blob(rect(bx - 16, 24 + by, bx - 13, 25 + by), BRASS[3])
    cv.shaded(tank, TANK, (2, 2))
    cv.fill({q for q in tank if q[1] in (30 + by, 36 + by)}, COPPER[0])          # straps
    cv.px[(bx - 16, 28 + by)] = COPPER[4]
    cv.px[(bx - 16, 32 + by)] = COPPER[4]
    # wheels
    wheel(cv, bx - 13, p["roll"])
    wheel(cv, bx + 3, p["roll"])
    # body: a squat shell that pumps on its wheels
    body = box(bx - 13, 29 + by, bx + 11, 46, 4)
    keys = {q: ("skirt" if q[1] >= 42 else "shell") for q in body}
    cv.blob_px(shade_px(keys, {"skirt": SKIRT, "shell": SHELL}, (3, 2)))
    cv.fill({q for q in body if q[1] == 41}, INK_SOFT)
    cv.fill({q for q in body if q[1] == 35 + by}, RED[2])                        # the maroon stripe
    cv.fill({q for q in body if q[1] == 36 + by}, RED[1])
    gy = 38 + by
    cv.blob(disc(bx - 7, gy + 1, 1.6), BRASS[3])                                 # gauge
    cv.px[(bx - 7, gy + 1)] = INK
    cv.px[(bx - 6, gy)] = INK
    cv.fill(rect(bx - 2, gy, bx, gy + 1), PAPER[3])                              # sticker
    cv.px[(bx - 1, gy + 1)] = RED[2]
    lamp = rect(bx + 3, gy, bx + 5, gy + 1)
    cv.fill(lamp, RED[4] if p["lamp"] else RED[1])
    cv.px[(bx + 3, gy)] = WHITE if p["lamp"] else RED[2]
    cv.dots([(bx - 10, 44), (bx - 3, 44), (bx + 1, 44), (bx + 8, 44)], GREY[0])   # rivets of the skirt
    cv.dots([(bx - 10, 43), (bx - 3, 43), (bx + 1, 43), (bx + 8, 43)], GREY[4])
    # collar and dome
    collar = box(hx - 13, 28 + hy, hx + 11, 31 + hy, 1)
    cv.shaded(collar, COLLAR, (2, 1))
    cv.fill({q for q in collar if q[1] == 28 + hy and hx - 9 < q[0] < hx - 2}, BRASS[4])
    dome = {q for q in oval(hx - 12, 10 + hy, hx + 10, 44 + hy) if q[1] <= 27 + hy}
    cv.shaded(dome, DOME, (3, 2))
    for q in ((hx - 9, 17 + hy), (hx - 8, 15 + hy), (hx - 7, 14 + hy), (hx - 6, 13 + hy), (hx - 9, 18 + hy)):
        cv.px[q] = GREY[2]                                                       # gloss on the glass
    cv.px[(hx - 8, 16 + hy)] = WHITE
    cv.px[(hx - 5, 12 + hy)] = GREY[3]
    # eyes: two tall bright ovals
    le = oval(hx - 7, 16 + hy, hx - 3, 24 + hy)
    re = oval(hx + 0, 16 + hy, hx + 4, 24 + hy)
    lx, ly = rnd(p["look"][0]), rnd(p["look"][1])
    if p["eyes"] == "open":
        for eye, ex in ((le, hx - 5), (re, hx + 2)):
            cv.blob(eye, WHITE)
            cv.fill(eye - shift(eye, -1, -1), PAPER[2])
            cv.fill(rect(ex + lx, 19 + hy + ly, ex + 1 + lx, 22 + hy + ly), INK, eye)
            cv.fill({(ex + 1 + lx, 19 + hy + ly)}, WHITE, eye)                   # pie cut
    elif p["eyes"] == "blink":
        cv.dots([(-7, 20), (-6, 21), (-5, 21), (-4, 21), (-3, 20), (0, 20), (1, 21), (2, 21), (3, 21), (4, 20)], PAPER[2], hx, hy)
    elif p["eyes"] == "happy":
        cv.dots([(-7, 21), (-6, 20), (-5, 19), (-4, 20), (-3, 21), (0, 21), (1, 20), (2, 19), (3, 20), (4, 21)], WHITE, hx, hy)
    if p["mouth"] == "smile":
        cv.dots([(-3, 25), (-2, 26), (-1, 26), (0, 25)], PAPER[2], hx, hy)
    else:
        cv.dots([(-2, 25), (-1, 25), (-2, 26), (-1, 26)], PAPER[2], hx, hy)
    # antenna with a lamp that wobbles behind the head
    a = rnd(p["ant"])
    cv.fill(hose((hx - 1, 10 + hy), (hx - 1 + a, 5 + hy), 0.0, 1), INK)
    bulb = disc(hx - 1 + a, 3 + hy, 1.9)
    cv.blob(bulb, RED[4] if p["lamp"] else RED[2])
    cv.px[(hx - 2 + a, 2 + hy)] = WHITE if p["lamp"] else RED[4]
    # the ribbed hose arm, from a brass socket on the right shoulder
    sh = (bx + 8, 34 + by)
    hand = (sh[0] + p["hr"][0], sh[1] + p["hr"][1])
    ctrl = bend_ctrl(sh, hand, p["br"])
    ribbed_hose(cv, sh, hand, p["br"], 3)
    cv.blob(disc(sh[0], sh[1], 2.2), BRASS[2])
    cv.px[(sh[0] - 1, sh[1] - 1)] = BRASS[4]
    d = (hand[0] - ctrl[0], hand[1] - ctrl[1])
    if abs(d[0]) + abs(d[1]) < 0.01:
        d = (1, 0)
    glove(cv, hand, d, "fist", r=3.6, thumb=0)
    # a puff of steam from the tank while it works hard
    if p["puff"]:
        k = p["puff"]
        cv.blob(disc(max(3, bx - 15 - k), 22 + by - 3 * k, 2.2 - 0.5 * k), WHITE)
    return cv


def render(poses, name):
    return [draw(p).image(W, H, name="%s[%d]" % (name, i)) for i, p in enumerate(poses)]


def idle():
    """16 frames: a soft engine bob, the hose arm swaying, the antenna wobbling,
    the lamp pulsing, a blink and glances to both sides."""
    bob = [0, 0, 1, 1, 0, 0, 0, 0]
    wob = [0, 0, 1, 1, 0, -1, -1, 0]
    poses = []
    for i in range(16):
        b = bob[i % 8]
        prev = bob[(i - 1) % 8]
        sway = (0, 1, 1, 0, 0, -1, -1, 0)[i % 8]
        p = P(y=b, ant=wob[(i - 1) % 8], hr=(5 + sway, 11 - (b - prev)), br=3.0 + sway, lamp=(i % 8) in (2, 3, 4))
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
    """8 frames: leans right, the gloved hose turns a crank in a circle, the body
    pumps with it, the antenna whips, the lamp flashes and the tank puffs."""
    poses = []
    for i in range(8):
        a = 2 * math.pi * i / 8
        down = 1 if math.sin(a) > 0.3 else 0
        hand = work_hand(i)
        x = -3
        sh = (CX + x + 8, 34 + down)
        p = P(x=x, y=down, head=(1 if math.cos(a) > -0.3 else 0, 0), ant=-rnd(1.6 * math.cos(a)), roll=i,
              look=(1, 1 if down else 0), hr=(hand[0] - sh[0], hand[1] - sh[1]), br=4.0 + 1.5 * math.sin(a),
              lamp=(i % 4 < 2), eyes="open", mouth="o" if down else "smile",
              puff=(i - 4) if i in (5, 6, 7) else 0)
        poses.append(p)
    return render(poses, "robot_work"), 12, True
