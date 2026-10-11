"""The protagonist: a posed-parts rig (head, torso, arms, legs) and its animations.

The figure is drawn facing right in a 24 x 40 frame. Legs use two-bone IK from
an ankle target (so planted feet stay exactly on the ground row), arms use
forward kinematics from shoulder angles (0 = down, positive = forward).
"""
import math

from anim_lib import (Layer, glyph, ipt, polar, rnd, INK, CORAL, CORAL_HI, CORAL_SH, CORAL_DK,
                      CREAM, CREAM_SH, WHITE, SKIN, SKIN_SH, DENIM, DENIM_SH, HAIR, HAIR_HI)

W, H = 24, 40
HX = 11            # hip column
HY = 26            # hip row when standing straight
ANKLE_Y = 36       # ankle row of a planted foot (shoe fills rows 37-38, outline row 39)
THIGH = SHIN = 5.0
UPPER = FORE = 4.0

HEAD = [
    ".HhhHH..",
    "HhHHHHH.",
    "HHHHHHHH",
    "HHHHSSSS",
    "HHHSSSeS",
    "HHsSSSeS",
    ".HSSSSSS",
    "..sSSSS.",
]
HEAD_LEGEND = {"H": HAIR, "h": HAIR_HI, "S": SKIN, "s": SKIN_SH}

# Hair tuft on top of the head; it flips back when the head drops or the body runs.
TUFTS = {"up": [(1, -1), (2, -1), (2, -2)],
         "back": [(1, -1), (2, -1), (1, -2)],
         "flat": [(0, -1), (1, -1), (2, -1)]}

# Shoe shapes relative to the ankle pixel: (dx, dy, part) with part u = upper, s = sole.
SHOES = {
    "flat": [(-1, 1, "u"), (0, 1, "u"), (1, 1, "u"), (2, 1, "u"),
             (-1, 2, "s"), (0, 2, "s"), (1, 2, "s"), (2, 2, "s"), (3, 2, "s")],
    # heel raised, toe on the ground (push-off); toe reaches 3 rows below the ankle
    "toe_down": [(-1, 1, "u"), (0, 1, "u"), (1, 1, "u"),
                 (0, 2, "s"), (1, 2, "u"), (2, 2, "u"),
                 (1, 3, "s"), (2, 3, "s"), (3, 3, "s")],
    # heel on the ground, toe raised (heel strike)
    "toe_up": [(-1, 1, "u"), (0, 1, "u"), (1, 1, "u"), (2, 0, "u"),
               (-1, 2, "s"), (0, 2, "s"), (1, 2, "s"), (2, 1, "s"), (3, 1, "s")],
    # shin pointing backwards: toes down, sole facing back
    "kick": [(-1, -1, "u"), (-1, 0, "u"), (-1, 1, "u"), (-1, 2, "u"),
             (-2, -1, "s"), (-2, 0, "s"), (-2, 1, "s"), (-2, 2, "s"), (-2, 3, "s")],
}


def _knee(hip, ankle):
    """Two-bone IK, knee always bending forward (+x)."""
    dx, dy = ankle[0] - hip[0], ankle[1] - hip[1]
    d = math.hypot(dx, dy)
    if d < 0.001:
        return (hip[0] + THIGH, hip[1])
    dd = min(d, THIGH + SHIN - 0.01)
    off = math.sqrt(max(0.0, THIGH * THIGH - (dd / 2.0) ** 2))
    mx, my = hip[0] + dx / 2.0, hip[1] + dy / 2.0
    return (mx + dy / d * off, my - dx / d * off)


def _leg(hip, target, pants, upper, sole):
    dx, lift, shoe = target
    ankle = (HX + dx, ANKLE_Y - lift)
    knee = _knee(hip, ankle)
    lay = Layer()
    lay.limb(hip, knee, 3, pants)
    lay.limb(knee, ankle, 3, pants)
    ax, ay = ipt(ankle)
    for sx, sy, part in SHOES[shoe]:
        lay.set(ax + sx, ay + sy, upper if part == "u" else sole)
    return lay


def _arm(shoulder, angles, sleeve, cuff, skin):
    a1, a2 = angles
    elbow = polar(shoulder, a1, UPPER)
    wrist = polar(elbow, a2, FORE)
    lay = Layer()
    lay.limb(shoulder, elbow, 3, sleeve)
    lay.limb(elbow, wrist, 3, sleeve)
    lay.limb(wrist, wrist, 3, cuff)
    lay.limb(polar(wrist, a2, 1.0), polar(wrist, a2, 2.0), 3, skin)
    return lay


def hand_tip(pose):
    """Furthest forward x of the near hand (used to report the reach frame)."""
    lean = pose.get("lean", 0)
    sh = (HX + rnd(lean * 0.8), 0)
    a1, a2 = pose["near_arm"]
    return polar(polar(sh, a1, UPPER), a2, FORE + 2.0)[0]


def draw(pose):
    dy = pose.get("dy", 0)
    lean = pose.get("lean", 0)
    breath = pose.get("breath", 0)
    belly = pose.get("belly", 0)
    hy = HY + dy
    hip = (HX, hy)

    def sh(y):
        return rnd(lean * (hy - 1 - y) / 10.0)

    top = hy - 11 - breath
    shoulder = (HX + sh(hy - 10), hy - 10 - breath)

    out = Layer()
    # far arm and far leg, in shadow colours
    out.stamp(_arm((shoulder[0] + 1, shoulder[1]), pose["far_arm"], CORAL_SH, CORAL_DK, SKIN_SH))
    out.stamp(_leg(hip, pose["far_leg"], DENIM_SH, CREAM_SH, CORAL_SH))

    # torso: hoodie, hood lump behind the neck, pelvis
    torso = Layer()
    for y in range(top, hy):
        s = sh(y)
        front = HX + 3 + s + (1 if belly and hy - 8 <= y <= hy - 3 else 0)
        for x in range(HX - 3 + s, front + 1):
            torso.set(x, y, CORAL)
        if y == hy - 1:
            for x in range(HX - 3 + s, front + 1):
                torso.set(x, y, CORAL_SH)
    for y in range(hy - 10 - breath, hy - 5):
        torso.set(HX - 3 + sh(y), y, CORAL_HI)
    for y in range(hy - 13 - breath, hy - 8 - breath):
        torso.set(HX - 4 + sh(y), y, CORAL_SH)
    torso.rect(HX - 2, hy, HX + 2, hy + 1, DENIM)
    out.stamp(torso)

    out.stamp(_leg(hip, pose["near_leg"], DENIM, WHITE, CORAL))

    # head
    hdx, hdy = pose.get("head", (0, 0))
    ox = HX - 3 + sh(hy - 11) + hdx
    oy = hy - 19 - breath + hdy
    legend = dict(HEAD_LEGEND)
    eye = pose.get("eye", "open")
    legend["e"] = INK if eye == "open" else SKIN
    head = glyph(HEAD, legend, ox, oy)
    if eye == "closed":
        head.set(ox + 5, oy + 5, INK)
        head.set(ox + 6, oy + 5, INK)
    elif eye == "sleep":
        head.set(ox + 6, oy + 4, INK)
        head.set(ox + 6, oy + 5, INK)
        head.set(ox + 5, oy + 5, SKIN_SH)
    for tx, ty in TUFTS[pose.get("tuft", "up")]:
        head.set(ox + tx, oy + ty, HAIR)
    out.stamp(head)

    # near arm on top
    adx = pose.get("arm_dx", 0)
    out.stamp(_arm((shoulder[0] + adx, shoulder[1]), pose["near_arm"], CORAL, CORAL_SH, SKIN))
    return out


def _frames(poses, name):
    return [draw(p).shifted(p.get("shift", 0), 0).to_image(W, H, name="%s[%d]" % (name, i)) for i, p in enumerate(poses)]


# --- idle --------------------------------------------------------------------
STAND = {"near_leg": (-1, 0, "flat"), "far_leg": (2, 0, "flat"),
         "near_arm": (-4, 8), "far_arm": (6, 14)}


def idle():
    poses = []
    #            breath, head dy, near arm,  eye
    table = [(0, 0, (-4, 8), "open"),
             (0, 0, (-4, 8), "open"),
             (1, 1, (-4, 8), "open"),     # chest fills first, head follows a frame later
             (1, 0, (-6, 6), "open"),
             (1, 0, (-6, 6), "open"),
             (1, 0, (-6, 6), "closed"),   # blink at the top of the breath
             (0, -1, (-6, 6), "open"),    # chest drops first, head follows
             (0, 0, (-4, 8), "open")]
    for breath, hdy, arm, eye in table:
        p = dict(STAND)
        p.update(breath=breath, head=(0, hdy), near_arm=arm, eye=eye)
        poses.append(p)
    return _frames(poses, "player_idle"), 6, True


# --- walk --------------------------------------------------------------------
# One leg over the 8-frame cycle, starting at its heel strike: (dx, lift, shoe)
WALK_LEG = [(5, 0, "toe_up"),
            (3, 0, "flat"),
            (0, 0, "flat"),
            (-3, 0, "flat"),
            (-5, 1, "toe_down"),
            (-5, 3, "toe_down"),
            (-1, 3, "flat"),
            (4, 2, "toe_up")]
WALK_DY = [1, 1, 0, 0]            # contact, down, passing, up
WALK_STRIDE_PX = 20               # ground covered by one full cycle


def walk():
    poses = []
    n = 8
    for f in range(n):
        s = math.cos(2 * math.pi * f / n)          # +1 when the near leg is forward
        near_up = -34 * s
        far_up = 34 * s
        poses.append({
            "dy": WALK_DY[f % 4], "lean": 1,
            "near_leg": WALK_LEG[f], "far_leg": WALK_LEG[(f + 4) % n],
            "near_arm": (near_up, near_up + 10 + 22 * max(0.0, -s)),
            "far_arm": (far_up, far_up + 10 + 22 * max(0.0, s)),
            # the hair tuft flips back as the body drops and recovers as it rises
            "tuft": "back" if f % 4 in (0, 1) else "up",
        })
    return _frames(poses, "player_walk"), 12, True


# --- run ---------------------------------------------------------------------
RUN_LEG = [(4, 0, "flat"),        # contact
           (-1, 0, "flat"),       # mid-stance, knee loaded
           (-6, 2, "toe_down"),   # push-off, already airborne
           (-6, 6, "kick"),       # heel kick behind
           (-1, 6, "toe_down"),   # knee drives forward
           (5, 3, "toe_up")]      # reach, airborne
RUN_DY = [0, 1, -1]
RUN_STRIDE_PX = 30


def run():
    poses = []
    n = 6
    for f in range(n):
        s = math.cos(2 * math.pi * (f + 0.5) / n)  # +1 when the near leg is forward
        near_up = -44 * s - 8
        far_up = 44 * s - 8
        poses.append({
            "dy": RUN_DY[f % 3], "lean": 2,
            "near_leg": RUN_LEG[f], "far_leg": RUN_LEG[(f + 3) % n],
            "near_arm": (near_up, near_up + 88),
            "far_arm": (far_up, far_up + 88),
            "tuft": "flat", "shift": -1,
        })
    return _frames(poses, "player_run"), 12, True


# --- use ---------------------------------------------------------------------
def use():
    #        dy lean near arm    far arm    head
    table = [(0, 0, (-18, 30), (8, 16), (0, 0)),      # start pulling the hand back
             (0, -1, (-38, 62), (14, 30), (0, 0)),    # anticipation: lean back, hand drawn
             (0, 1, (42, 78), (-10, 6), (0, 0)),      # thrust
             (0, 1, (82, 90), (-22, -6), (1, 0)),     # full reach (furthest)
             (0, 1, (70, 88), (-16, 0), (0, 0)),      # settle, pressing
             (0, 0, (30, 58), (0, 12), (0, 0)),       # retract
             (0, 0, (2, 14), (6, 14), (0, 0))]        # back to rest
    poses = []
    for dy, lean, near, far, head in table:
        p = dict(STAND)
        p.update(dy=dy, lean=lean, near_arm=near, far_arm=far, head=head)
        poses.append(p)
    tips = [hand_tip(p) for p in poses]
    reach = max(range(len(poses)), key=lambda i: tips[i])
    return _frames(poses, "player_use"), 12, False, reach


# --- sleep -------------------------------------------------------------------
SW, SH_ = 40, 24


def sleep():
    frames = []
    #        belly, arm lifted
    table = [(0, 0), (0, 0), (0, 0), (1, 0), (1, 1), (1, 1), (1, 1), (0, 1)]
    ref = None
    for i, (belly, arm) in enumerate(table):
        pose = {"near_leg": (-2, 5, "kick"), "far_leg": (0, 0, "flat"),
                "near_arm": (22, -8), "far_arm": (0, 4),
                # the chest rises one frame before the resting hand follows it
                "eye": "sleep", "belly": belly, "arm_dx": arm}
        lay = draw(pose).rot_ccw(W)
        if ref is None:
            x0, y0, x1, y1 = lay.bbox()
            ref = ((SW - (x1 - x0 + 1)) // 2 - x0, (SH_ - 1) - y1)
        frames.append(lay.shifted(*ref).to_image(SW, SH_, name="player_sleep[%d]" % i))
    return frames, 4, True
