"""The protagonist as a 1930s rubber-hose lead: round head with pie-cut eyes,
brows, a wide grin and a hair tuft, a maroon hooded top (floppy hood, pocket,
strings) over charcoal shorts, black noodle limbs, puffy white gloves with
three back lines and big two-tone shoes. Faces RIGHT in a slight 3/4 from
above; 60 x 84 frames (1.5 px per world pixel), feet on the bottom row,
anchored bottom centre, 2 px outer contour.

Every animation is a table of poses written in WORLD pixels (the units of the
previous 40 x 56 rig); `draw` scales a pose by 1.5 and turns it into pixels.
The torso is a bean that tilts around the hips (`tilt`), the head rides on top
of it and stays upright, and the tuft, the hood tip and the strings are loose
ends that lag behind (follow-through).
"""
import math

from anim_lib import (Cv, oval, disc, rect, stroke, bezier, bend_ctrl, hose, noodle, rot_px, rot_pt, glove,
                      rnd, lerp, ease, shift, shade_px, S,
                      INK, INK_SOFT, PAPER, SEPIA, GREY, BLACK, BRASS, RED, ROSE, GLASS, WHITE)

W, H = 60, 84
GROUND = 83          # bottom row: the outline of a planted near shoe
CX = 30
HIP = (29, 57)
LEG_LEN = 20.0
LIMB = 3             # brush of the noodle limbs (the outer contour adds 2 px)
SLEEP_W, SLEEP_H = 84, 48

SKIN = (PAPER[1], PAPER[2], PAPER[3], PAPER[4])
HOODIE = (RED[0], RED[1], RED[2], RED[3])
HEM = (RED[0], RED[0], RED[1], RED[2])
SHORTS = (GREY[0], GREY[1], GREY[2], GREY[3])
LEATHER = (SEPIA[1], SEPIA[2], SEPIA[3], SEPIA[4])
TOECAP = (PAPER[1], PAPER[2], PAPER[3], PAPER[4])
HAIR = BLACK[1]

DEFAULT = dict(
    x=0, y=0,                 # hip offset (y < 0 is up)
    tilt=0,                   # torso lean around the hips in degrees (+ = forward)
    sq=0,                     # squash (+) / stretch (-) of the torso, in px
    head=(0, 0), tuft=(0, 0), hood=(0, 0), strings=0,
    eyes="open", look=(0, 0), mouth="grin",
    fn=(-5, 0, 0), ff=(5, 0, 0),      # near / far foot: x from the frame centre, lift, pitch (deg, + = toe down)
    ln=1, lf=1,               # side the slack legs bow to (+1 forward)
    hn=(-5, 9), hf=(6, 8),    # near / far hand relative to its shoulder
    bn=-2.0, bf=2.0,          # bow of each arm
    gn="fist", gf="fist",     # glove kind
    gdn=None, gdf=None,       # glove direction override
    watch=False,              # wrist watch on the near arm
    sweat=0,                  # 1..3: a drop flying off the brow
)


def P(**kw):
    d = dict(DEFAULT)
    d.update(kw)
    return d


def scaled(p):
    """A pose in world pixels -> the same pose in sprite pixels."""
    q = dict(p)
    for k in ("x", "y", "sq", "strings", "bn", "bf"):
        q[k] = p[k] * S
    for k in ("head", "tuft", "hood", "look", "hn", "hf"):
        q[k] = tuple(v * S for v in p[k])
    for k in ("fn", "ff"):
        q[k] = (p[k][0] * S, p[k][1] * S, p[k][2])
    return q


def mix(a, b, t):
    """Blend the numeric fields of two poses; discrete fields come from b once t >= 0.5."""
    out = {}
    for k in a:
        va, vb = a[k], b[k]
        if isinstance(va, bool) or isinstance(vb, bool):
            out[k] = vb if t >= 0.5 else va
        elif isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            out[k] = lerp(va, vb, t)
        elif isinstance(va, tuple) and isinstance(vb, tuple):
            out[k] = tuple(lerp(q, r, t) for q, r in zip(va, vb))
        else:
            out[k] = vb if t >= 0.5 else va
    return out


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# --- parts (sprite pixels from here on) --------------------------------------------
def shoe_fn(u, v):
    """Big two-tone shoe: leather body, pale toe cap, dark sole."""
    if v < 0:
        return None
    toe = ((u - 3.2) / 5.4) ** 2 + ((v - 3.4) / 4.8) ** 2 <= 1.0
    heel = ((u + 3.6) / 4.7) ** 2 + ((v - 2.7) / 3.8) ** 2 <= 1.0
    if not (toe or heel):
        return None
    if v < 1.3:
        return "sole"
    seam = u - 0.35 * (v - 3.0)
    if seam > 3.4:
        return "cap"
    if seam > 2.5:
        return "seam"
    return "leather"


SHOE_RAMPS = {"sole": SEPIA[0], "cap": TOECAP, "seam": INK_SOFT, "leather": LEATHER}


def shoe_px(ox, oy, pitch):
    px = shade_px(rot_px(shoe_fn, ox, oy, pitch, 13), SHOE_RAMPS, (2, 1))
    for u, v in ((5.6, 6.3), (6.6, 5.6), (-4.2, 5.2)):          # hard speculars on the cap and the heel
        s = rot_pt(u, v, ox, oy, pitch)
        q = (int(math.floor(s[0])), int(math.floor(s[1])))
        if q in px and px[q] not in (SEPIA[0], INK_SOFT):
            px[q] = WHITE if u > 0 else SEPIA[4]
    return px


def shoe(foot, ground):
    """-> (pixels, ankle point). A planted shoe is dropped onto the ground row."""
    fx, lift, pitch = foot
    ox, oy = CX + rnd(fx), ground - rnd(lift)
    px = shoe_px(ox, oy, pitch)
    ankle = rot_pt(-3.0, 5.2, ox, oy, pitch)
    low = max(q[1] for q in px)
    if rnd(lift) == 0 or low > ground - 1:
        dy = (ground - 1) - low
        px = {(x, y + dy): c for (x, y), c in px.items()}
        ankle = (ankle[0], ankle[1] + dy)
    return px, ankle


def round_box(x0, y0, x1, y1, n=2.5):
    """Superellipse filling the inclusive pixel box: rounder cheeks than an oval."""
    cx, cy = (x0 + x1 + 1) / 2.0, (y0 + y1 + 1) / 2.0
    rx, ry = (x1 - x0 + 1) / 2.0, (y1 - y0 + 1) / 2.0
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
            if abs((x + 0.5 - cx) / rx) ** n + abs((y + 0.5 - cy) / ry) ** n <= 1.0}


def pie_eye(cv, eye, x0, x1, top, bot):
    """Tall black pupil with the pie cut (a wedge of white) on its upper right."""
    pupil = oval(x0, top, x1, bot) if x1 - x0 >= 2 else rect(x0, top, x1, bot)
    cv.fill(pupil, INK, eye)
    cut = [(x1, top + 1), (x1, top + 2), (x1 - 1, top + 1)]
    if x1 - x0 >= 3:
        cut += [(x1 - 1, top + 2), (x1, top + 3)]
    cv.fill(set(cut), WHITE, eye)


def draw_head(cv, hx, hy, p):
    head = round_box(hx - 15, hy - 14, hx + 14, hy + 12)
    cv.shaded(head, SKIN, (3, 3))
    # hair: a black cap over the crown and the back of the head, with a sheen
    face = oval(hx - 11, hy - 12, hx + 22, hy + 22)
    hair = head - face
    cv.fill(hair, HAIR)
    cv.fill(stroke(bezier((hx - 12, hy - 4), (hx - 12, hy - 11), (hx - 6, hy - 12)), 1), BLACK[3], hair)
    cv.fill(stroke(bezier((hx - 13, hy + 2), (hx - 13, hy + 5), (hx - 11, hy + 8)), 1), BLACK[2], hair)
    cv.fill((face & head) - shift(face, 1, 0), PAPER[2])          # the hairline casts a soft shadow
    # ear
    ear = oval(hx - 11, hy + 1, hx - 8, hy + 5)
    cv.blob(ear, PAPER[3])
    cv.dots([(hx - 10, hy + 3), (hx - 10, hy + 4)], PAPER[1])
    # tuft: two licks curling forward that lag behind the head
    tx, ty = p["tuft"]
    licks = (((hx - 3, hy - 13), (hx - 2 + tx * 0.3, hy - 24 + ty), (hx + 8 + tx, hy - 19 + ty), 3),
             ((hx - 8, hy - 12), (hx - 10 + tx * 0.4, hy - 20 + ty), (hx - 3 + tx * 0.8, hy - 21 + ty), 2))
    for a, c, b, w in licks:
        cv.fill(stroke(bezier(a, c, b), w), HAIR)
    cv.dots([(rnd(hx - 3 + tx * 0.3), rnd(hy - 17 + ty * 0.6)), (rnd(hx - 3 + tx * 0.3), rnd(hy - 16 + ty * 0.6))], BLACK[3])

    eyes = p["eyes"]
    lx, ly = rnd(p["look"][0]), rnd(p["look"][1])
    e_top, e_bot = hy - 7, hy + 1
    brow = hy - 11
    if eyes == "wide":
        e_top -= 1
        brow -= 1
    near = oval(hx + 0, e_top, hx + 5, e_bot)
    far = oval(hx + 8, e_top, hx + 12, e_bot)
    if eyes in ("open", "half", "wide"):
        if eyes == "half":                             # heavy lids: only the lower half shows
            near = {q for q in near if q[1] >= hy - 4}
            far = {q for q in far if q[1] >= hy - 4}
            brow = hy - 9
        cv.blob(near, WHITE)
        cv.blob(far, WHITE)
        for eye in (near, far):                        # shade under the lid, and on the lower right
            cv.fill({q for q in eye if (q[0], q[1] - 1) not in eye}, PAPER[3])
            cv.fill(eye - shift(eye, -1, -1), PAPER[2])
        top = hy - 5 if eyes != "half" else hy - 3
        bot = hy if eyes != "wide" else hy - 1
        pie_eye(cv, near, hx + 2 + lx, hx + 5 + lx, top + ly, bot + ly)
        pie_eye(cv, far, hx + 10 + lx, hx + 12 + lx, top + ly, bot + ly)
        if eyes == "half":
            cv.fill(rect(hx + 0, hy - 5, hx + 5, hy - 5) | rect(hx + 8, hy - 5, hx + 12, hy - 5), INK)
    elif eyes == "blink":
        cv.dots([(0, -2), (1, -1), (2, -1), (3, -1), (4, -1), (5, -2), (-1, -3),
                 (8, -2), (9, -1), (10, -1), (11, -1), (12, -2), (13, -3)], INK, hx, hy)
        brow = hy - 9
    elif eyes == "happy":
        cv.dots([(0, -2), (0, -3), (1, -4), (2, -5), (3, -5), (4, -4), (5, -3), (5, -2),
                 (8, -2), (8, -3), (9, -4), (10, -5), (11, -4), (12, -3), (12, -2)], INK, hx, hy)
        brow = hy - 10
    elif eyes == "sleep":
        cv.dots([(-1, -3), (0, -2), (1, -1), (2, -1), (3, -1), (4, -1), (5, -2), (6, -3),
                 (8, -3), (9, -2), (10, -1), (11, -1), (12, -2), (13, -3)], INK, hx, hy)
        brow = None
    # brows: a short arc over each eye
    bl = 0 if eyes in ("open", "wide", "happy") else 1
    if brow is not None:
        cv.fill({(hx + 0, brow + 1 - bl), (hx + 1, brow), (hx + 2, brow), (hx + 3, brow), (hx + 4, brow), (hx + 5, brow + bl),
                 (hx + 8, brow + bl), (hx + 9, brow), (hx + 10, brow), (hx + 11, brow), (hx + 12, brow + 1 - bl)}, INK, head)

    # nose: a shiny black bean sticking out of the face
    nose = oval(hx + 13, hy + 0, hx + 16, hy + 3)
    cv.fill(nose, INK)
    cv.px[(hx + 14, hy + 1)] = BLACK[3]
    # cheek
    cv.fill(rect(hx - 6, hy + 4, hx - 4, hy + 5) | rect(hx - 5, hy + 3, hx - 4, hy + 6), ROSE[3])
    mouth = p["mouth"]
    if mouth == "grin":                                # wide open smile: teeth above, tongue below
        m = {(x, y) for y in range(hy + 5, hy + 10) for x in range(hx - 2, hx + 13)
             if ((x + 0.5 - (hx + 5.5)) / 6.6) ** 2 + ((y + 0.5 - (hy + 4.6)) / 5.2) ** 2 <= 1.0}
        cv.blob(m, RED[0])
        cv.fill({q for q in m if q[1] <= hy + 6}, WHITE)
        cv.fill({q for q in m if q[1] == hy + 6 and (q[0] - hx) % 3 == 1}, PAPER[2])      # tooth gaps
        cv.fill(oval(hx + 3, hy + 8, hx + 8, hy + 11) & m, ROSE[2])
        cv.fill(rect(hx + 5, hy + 8, hx + 6, hy + 8) & m, ROSE[3])
        cv.dots([(-2, 3), (-1, 4), (12, 4), (13, 3)], INK, hx, hy)                       # cheek ticks
    elif mouth == "smile":                             # closed, from cheek to cheek
        cv.fill(stroke(bezier((hx - 1, hy + 4), (hx + 5, hy + 11), (hx + 12, hy + 4)), 1), INK)
        cv.dots([(-2, 3), (13, 3)], INK, hx, hy)
    elif mouth == "open":
        m = oval(hx + 1, hy + 4, hx + 10, hy + 11) & head
        cv.fill(m, INK)
        inner = oval(hx + 2, hy + 5, hx + 9, hy + 10)
        cv.fill(inner, RED[0], m)
        cv.fill(rect(hx + 3, hy + 5, hx + 8, hy + 5), WHITE, m)
        cv.fill(oval(hx + 3, hy + 8, hx + 8, hy + 11) & inner, ROSE[2], m)
        cv.dots([(0, 4), (11, 4)], INK, hx, hy)
    elif mouth == "o":
        cv.fill(oval(hx + 5, hy + 5, hx + 8, hy + 8), INK)
        cv.fill(rect(hx + 6, hy + 6, hx + 7, hy + 7), RED[0])
    elif mouth == "flat":
        cv.fill(rect(hx + 2, hy + 7, hx + 9, hy + 7), INK)
        cv.dots([(1, 6), (10, 8)], INK, hx, hy)
    elif mouth == "snore":
        cv.fill(oval(hx + 4, hy + 4, hx + 9, hy + 9), INK)
        cv.fill(oval(hx + 5, hy + 5, hx + 8, hy + 8), RED[0])
        cv.fill(rect(hx + 6, hy + 7, hx + 7, hy + 8), ROSE[2])
    sweat = p.get("sweat", 0)
    if sweat:
        sx, sy = hx - 14 - 3 * sweat, hy - 13 - 2 * sweat
        cv.blob({(sx, sy), (sx, sy + 1), (sx - 1, sy + 1), (sx - 1, sy + 2), (sx, sy + 2), (sx + 1, sy + 1)}, GLASS[3])
        cv.px[(sx, sy + 1)] = GLASS[4]


def draw_hood(cv, hx, hy, p):
    """Floppy hood hanging at the nape; its tip lags behind the head."""
    dx, dy = p["hood"]
    body = oval(hx - 18, hy + 3, hx - 8, hy + 15)
    tip = disc(hx - 17 + rnd(dx), hy + 12 + rnd(dy), 3.9)
    link = disc(hx - 15 + rnd(dx * 0.5), hy + 10 + rnd(dy * 0.5), 3.9)
    hood = body | tip | link
    cv.shaded(hood, HOODIE, (3, 3))
    # the fold of the opening
    cv.fill(stroke(bezier((hx - 12, hy + 4), (hx - 16, hy + 6), (hx - 15, hy + 10)), 1), RED[4], hood)
    cv.fill(stroke(bezier((hx - 11, hy + 6), (hx - 14, hy + 8), (hx - 13, hy + 12)), 1), RED[0], hood)


def draw_arm(cv, shoulder, hand_rel, bend, kind, gdir=None, watch=False):
    hand = (shoulder[0] + hand_rel[0], shoulder[1] + hand_rel[1])
    ctrl = bend_ctrl(shoulder, hand, bend)
    pts = bezier(shoulder, ctrl, hand)
    cv.fill(stroke(pts, LIMB), BLACK[1])
    d = gdir or (hand[0] - ctrl[0], hand[1] - ctrl[1])
    if abs(d[0]) + abs(d[1]) < 0.01:
        d = (0, 1)
    glove(cv, hand, d, kind)
    if watch:                                          # a chunky brass wrist watch over the cuff
        n = math.hypot(d[0], d[1])
        wx, wy = rnd(hand[0] - d[0] / n * 8.0), rnd(hand[1] - d[1] / n * 8.0)
        cv.blob(rect(wx - 2, wy - 2, wx + 2, wy + 2), BRASS[2])
        cv.fill(rect(wx - 1, wy - 1, wx + 1, wy + 1), PAPER[4])
        cv.dots([(wx, wy), (wx, wy - 1), (wx + 1, wy)], INK)
        cv.dots([(wx - 2, wy - 2), (wx - 1, wy - 2)], BRASS[4])
        cv.dots([(wx + 2, wy + 2), (wx + 1, wy + 2)], BRASS[0])
    return hand


def geo(p):
    """Skeleton of a (scaled) pose: hips, the torso frame, head centre, shoulders."""
    hipx, hipy = HIP[0] + rnd(p["x"]), HIP[1] + rnd(p["y"])
    sq = p["sq"]
    tilt = p["tilt"]

    def loc(u, v):
        v2 = v - sq * clamp(v, 0.0, 21.0) / 21.0
        return rot_pt(u, v2, hipx, hipy, tilt)

    hc = loc(1.5, 28.5)
    hx = rnd(hc[0] + p["head"][0])
    hy = rnd(hc[1] + p["head"][1])
    sn = loc(-7.5, 11.0)
    sf = loc(6.8, 11.0)
    return hipx, hipy, loc, hx, hy, (rnd(sn[0]), rnd(sn[1])), (rnd(sf[0]), rnd(sf[1]))


TORSO_RAMPS = {"shorts": SHORTS, "line": INK, "hem": HEM, "hood": HOODIE}


def torso_keys(hipx, hipy, tilt, sq):
    sy = (21.0 - sq) / 21.0
    sx = 1.0 + 0.03 * sq

    def fn(u, v):
        uu, vv = u / sx / S, v / sy / S
        w = vv - 5.0
        ru = 7.0 - (0.9 * w / 7.0 if w > 0 else 0.0)
        if (uu / ru) ** 2 + (w / 7.0) ** 2 > 1.0:
            return None
        if vv < 1.7:
            return "shorts"
        if vv < 2.3:
            return "line"
        if vv < 3.5:
            return "hem"
        return "hood"

    return rot_px(fn, hipx, hipy, tilt, 27)


def draw(p, name="player", w=W, h=H):
    p = scaled(p)
    cv = Cv()
    hipx, hipy, loc, hx, hy, sh_n, sh_f = geo(p)

    # far arm, behind everything
    draw_arm(cv, sh_f, p["hf"], p["bf"], p["gf"], p["gdf"])
    # legs: far then near
    for foot, hip, ground, side in ((p["ff"], (hipx + 3, hipy - 2), GROUND - 2, p["lf"]),
                                    (p["fn"], (hipx - 3, hipy - 2), GROUND, p["ln"])):
        px, ankle = shoe(foot, ground)
        cv.fill(noodle(hip, ankle, LEG_LEN, side, LIMB), BLACK[1])
        cv.blob_px(px)
    draw_hood(cv, hx, hy, p)
    # torso: hooded top and shorts
    keys = torso_keys(hipx, hipy, p["tilt"], p["sq"])
    cv.blob_px(shade_px(keys, TORSO_RAMPS, (4, 3)))

    def mark(pt, col, only="hood"):
        q = (int(math.floor(pt[0])), int(math.floor(pt[1])))
        if keys.get(q) == only:
            cv.px[q] = col

    for u, v in ((-7.2, 15.0), (-7.2, 14.0), (-6.2, 16.0), (-5.2, 16.6)):          # hard light on the shoulder
        mark(loc(u, v), RED[4])
    for k in range(17):                                                           # pocket: a dark arc on the belly
        t = k / 16.0
        a, c, b = (0.5, 6.6), (4.4, 10.6), (8.6, 6.8)
        u = (1 - t) ** 2 * a[0] + 2 * t * (1 - t) * c[0] + t * t * b[0]
        v = (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * c[1] + t * t * b[1]
        mark(loc(u, v), RED[0])
        mark(loc(u, v + 1.0), RED[3])
    for u in (-6.0, -3.0, 0.0, 3.0, 6.0):                                         # ribbing of the hem
        mark(loc(u, 4.2), RED[0], "hem")
    for u in (-5.0, 5.5):                                                         # shorts: a crease on each leg
        mark(loc(u, 0.4), GREY[0], "shorts")
        mark(loc(u, -0.6), GREY[0], "shorts")
    # strings hang straight down and sway
    sway = p["strings"]
    for u in (4.0, 8.0):
        s = loc(u, 14.5)
        x, y = rnd(s[0]), rnd(s[1])
        for k in range(5):
            q = (x + rnd(sway * k / 4.0), y + k)
            if q in keys:
                cv.px[q] = PAPER[4] if k >= 3 else PAPER[2]
    draw_head(cv, hx, hy, p)
    # near arm in front
    draw_arm(cv, sh_n, p["hn"], p["bn"], p["gn"], p["gdn"], watch=p["watch"])
    cv.px = {q: c for q, c in cv.px.items() if q[1] >= 0}      # a fingertip may graze the top edge at the apex of a jump
    cv.thicken(w, h, GROUND)
    return cv


def render(poses, name):
    return [draw(p).image(W, H, name="%s[%d]" % (name, i)) for i, p in enumerate(poses)]


def hand_pos(p, near=True):
    """Glove centre in frame (sprite) pixels."""
    p = scaled(p)
    g = geo(p)
    s = g[5] if near else g[6]
    h = p["hn"] if near else p["hf"]
    return (rnd(s[0] + h[0]), rnd(s[1] + h[1]))


# --- idle ---------------------------------------------------------------------------
IDLE_FPS = 8


def breathing(n):
    """Bouncy breath: the base every idle-like animation is laid over."""
    breath = [0, 1, 1, 0, -1, -1, 0, 0]
    frames = []
    for i in range(n):
        b = breath[i % 8]
        prev = breath[(i - 1) % 8]
        lag = prev - b
        # hands, tuft and hood drag one frame behind the shoulders
        frames.append(P(sq=b, tuft=(0, lag), hood=(0, -lag),
                        hn=(-6 - (1 if b > 0 else 0), 9 + lag), hf=(6 + (1 if b > 0 else 0), 8 + lag)))
    return frames


def idle():
    """64 frames (8 s): bouncy breathing with blinks, glances back and up, a
    foot tap, a shift of weight and, late in the loop, a head scratch."""
    frames = breathing(64)

    def put(i, **kw):
        frames[i].update(kw)

    for i in (5, 29, 59):                              # blinks
        put(i, eyes="blink")
        put(i + 1, eyes="half")
    for i in (11, 12, 13, 14, 15):                     # glance back over the shoulder
        put(i, look=(-1, 0))
    for i in (12, 13, 14):
        put(i, head=(-1, 0), tuft=(1, 0), mouth="smile")
    for i in (18, 19, 21, 22, 24, 25):                 # impatient foot tap
        put(i, ff=(5, 0, -28))
    for i in (19, 20, 21, 22, 23, 24, 25):
        put(i, look=(0, 1))
    for i in (33, 34, 35, 36):                         # look up at the machines
        put(i, look=(0, -1), head=(0, -1), mouth="smile")
    # scratch the back of the head: anticipation, up, four scratches, down, settle
    put(40, hn=(-8, 6), bn=-3.5, look=(0, -1))
    put(41, hn=(-7, -4), bn=4.0, gn="open", gdn=(-0.3, -1), look=(0, -1), mouth="smile")
    put(42, hn=(-5, -15), bn=4.5, gn="open", gdn=(0.6, -1), look=(0, -1), mouth="o", head=(1, 0), tuft=(-1, 1))
    for k, i in enumerate(range(43, 51)):
        a = k % 2
        put(i, hn=(-4 + 2 * a, -16 + a), bn=4.5 - a, gn="open", gdn=(0.8, -1 + 0.6 * a), look=(0, -1),
            mouth="o" if k < 6 else "smile", head=(1, 0), tuft=(1 - 2 * a, a), eyes="open" if k not in (3, 4) else "half")
    put(51, hn=(-7, -6), bn=4.0, gn="open", gdn=(-0.5, -1), mouth="smile", tuft=(1, -1))
    put(52, hn=(-8, 7), bn=-3.5, mouth="smile", tuft=(0, 1))
    put(53, hn=(-6, 10), bn=-1.0)
    return render(frames, "player_idle"), IDLE_FPS, True


# --- walk ---------------------------------------------------------------------------
WALK_FRAMES = 12
WALK_FPS = 15
WALK_STEP = 3                       # WORLD px a planted foot slides back per frame (4.5 sprite px)
WALK_STRIDE_PX = WALK_STEP * WALK_FRAMES


def walk_leg(ph):
    s = WALK_STEP * WALK_FRAMES / 2.0          # length of one step
    if ph < 0.5:
        u = ph / 0.5
        x = s / 2.0 - s * u
        pitch = -24 if u < 0.1 else (20 if u > 0.8 else 0)
        return (x, 0, pitch)
    u = (ph - 0.5) / 0.5
    if u < 0.01:
        return (-s / 2.0, 0, 38)               # toe-off: heel peeled, toe planted
    x = -s / 2.0 + s * (0.25 * u + 0.75 * ease(u))
    return (x, 5.5 * math.sin(math.pi * u) ** 0.8, lerp(46, -28, u))


def walk():
    """Rubber-hose strut: chest out, a double bounce, arms swinging in wide arcs."""
    n = WALK_FRAMES
    half = n // 2
    bob = [0, 1, 0, -1, -2, -1]
    squash = [0, 1, 0, 0, -1, 0]
    frames = []
    for i in range(n):
        t = i / float(n)
        y = bob[i % half]
        y1 = bob[(i - 1) % half]
        y2 = bob[(i - 2) % half]
        swing = math.cos(2 * math.pi * t)       # +1: near foot forward, near arm back
        vel = math.sin(2 * math.pi * t)
        an = math.radians(-52 * swing + 6)
        af = math.radians(52 * swing + 6)
        rn = 11.5
        up_n = max(0.0, math.sin(an))
        up_f = max(0.0, math.sin(af))
        p = P(y=y, sq=squash[i % half], tilt=-4,
              head=(1, y1 - y), tuft=(-1 if y2 - y1 < 0 else 0, y2 - y1),
              hood=(-1, clamp(y2 - y, -1, 2)), strings=rnd(-swing * 0.8),
              fn=walk_leg(t), ff=walk_leg((t + 0.5) % 1.0),
              hn=(rn * math.sin(an), rn * math.cos(an) - 4.0 * up_n ** 1.5),
              hf=(rn * math.sin(af) + 2, rn * math.cos(af) - 4.0 * up_f ** 1.5 - 1),
              bn=-1.0 - 2.5 * abs(math.sin(an)) + 1.2 * vel, bf=-1.0 - 2.5 * abs(math.sin(af)) - 1.2 * vel)
        frames.append(p)
    return render(frames, "player_walk"), WALK_FPS, True


# --- run ----------------------------------------------------------------------------
RUN_FRAMES = 8
RUN_FPS = 16
RUN_STEP = 6                        # WORLD px per frame (9 sprite px)
RUN_STRIDE_PX = RUN_STEP * RUN_FRAMES

RUN_LEG = [(9, 0, -24), (3, 0, 0), (-3, 0, 14), (-9, 2, 48),
           (-12, 8, 80), (-6, 10, 44), (3, 9, 6), (10, 5, -28)]


def run():
    """Leaning sprint: the torso tilts forward, arms pump, hood and tuft stream behind."""
    bob = [1, 2, 0, -2]
    squash = [0, 2, 0, -2]
    tilt = [18, 21, 17, 14]
    frames = []
    for i in range(RUN_FRAMES):
        t = i / float(RUN_FRAMES)
        y = bob[i % 4]
        y1 = bob[(i - 1) % 4]
        swing = math.cos(2 * math.pi * (t + 0.06))
        vel = math.sin(2 * math.pi * (t + 0.06))
        an = -swing
        af = swing
        dy = clamp(y1 - y, -1, 1)
        p = P(y=y, sq=squash[i % 4], tilt=tilt[i % 4], x=-4,
              head=(0, dy), tuft=(-3, 2 + dy), hood=(-3, -2 - dy), strings=-1,
              fn=RUN_LEG[i], ff=RUN_LEG[(i + 4) % 8], ln=1, lf=1,
              hn=(9.0 * an + 1, 5.0 - 4.5 * max(an, 0.0) - 1.0 * max(-an, 0.0)),
              hf=(8.0 * af + 3, 4.5 - 4.5 * max(af, 0.0) - 1.0 * max(-af, 0.0)),
              bn=-4.0 - 1.5 * vel, bf=-4.0 + 1.5 * vel,
              mouth="grin", eyes="open", sweat=i if i in (1, 2, 3) else 0)
        frames.append(p)
    return render(frames, "player_run"), RUN_FPS, True


# --- use ----------------------------------------------------------------------------
USE_REACH_FRAME = 4


def use():
    """Anticipation, a long rubber reach, press, hold, settle. Returns the reach frame too."""
    rest = P()
    ant1 = P(x=-1, tilt=-5, sq=1, hn=(-7, 5), bn=-3.5, hf=(6, 7), tuft=(1, 0), hood=(1, 0), mouth="smile", strings=1)
    ant2 = P(x=-2, tilt=-12, sq=2, hn=(-7, -1), bn=-5.0, hf=(8, 4), bf=3.0, head=(0, 1), tuft=(2, 1), hood=(1, 1),
             eyes="half", mouth="flat", ff=(5, 0, -22), gn="point", gdn=(-0.2, -1), strings=1)
    go = P(x=-3, tilt=3, sq=-1, hn=(9, 2), bn=4.5, hf=(-1, 9), bf=-2.0, tuft=(-3, 1), hood=(-2, -1),
           gn="point", gdn=(1, 0.1), fn=(-6, 0, 16), mouth="open", strings=-1)
    reach = P(x=-4, tilt=12, sq=-2, hn=(19, 1), bn=-0.8, hf=(-8, 6), bf=-4.0, head=(-1, 0), tuft=(-3, 1),
              hood=(-3, -2), gn="point", gdn=(1, 0), fn=(-7, 0, 30), ff=(6, 0, 0), eyes="wide", mouth="grin",
              strings=-1)
    press = P(x=-3, tilt=10, sq=1, hn=(17, 1), bn=2.0, hf=(-6, 8), bf=-3.0, head=(-1, 0), tuft=(1, 0), hood=(1, 1),
              gn="point", gdn=(1, 0), fn=(-7, 0, 18), ff=(6, 0, 0), eyes="open", mouth="grin", strings=1)
    hold = P(x=-3, tilt=10, sq=0, hn=(18, 1), bn=1.0, hf=(-5, 8), bf=-2.5, head=(-1, 0), tuft=(0, 0),
             gn="point", gdn=(1, 0), fn=(-6, 0, 8), ff=(6, 0, 0), eyes="happy", mouth="grin")
    back = P(x=-1, tilt=3, sq=0, hn=(8, 6), bn=4.0, hf=(2, 9), bf=0.0, tuft=(2, 0), hood=(2, 0),
             eyes="happy", strings=1)
    over = P(tilt=-4, sq=1, hn=(-6, 9), bn=-3.0, hf=(7, 8), bf=3.0, tuft=(1, 1), hood=(0, 1))
    poses = [rest, ant1, ant2, go, reach, press, hold, back, over, rest]
    return render(poses, "player_use"), 12, False, USE_REACH_FRAME, hand_pos(reach)


# --- cheer --------------------------------------------------------------------------
def cheer():
    """A full jump for joy: crouch, launch, hang with both arms up, land, settle."""
    up = dict(gn="open", gf="open", eyes="happy", mouth="open")
    poses = [
        P(),
        P(y=2, sq=2, tilt=4, hn=(-8, 7), hf=(8, 6), bn=-3.5, bf=3.5, head=(0, 1), tuft=(0, -1), hood=(0, -1),
          eyes="half", mouth="smile"),
        P(y=3, sq=3, tilt=8, hn=(-10, 4), hf=(7, 5), bn=-4.5, bf=4.5, head=(0, 1), tuft=(1, 1), hood=(0, 1),
          eyes="blink", mouth="flat"),
        P(y=-2, sq=-2, tilt=-2, hn=(-7, -3), hf=(8, -4), bn=3.0, bf=-3.0, fn=(-5, 0, 32), ff=(5, 0, 32),
          tuft=(0, 2), hood=(0, 2), eyes="wide", mouth="open", gn="open", gf="open", gdn=(-1, -0.6), gdf=(1, -0.6)),
        P(y=-4, sq=-2, tilt=-5, hn=(-6, -13), hf=(8, -14), bn=2.5, bf=-2.5, fn=(-5, 4, 40), ff=(5, 4, 40),
          tuft=(0, 3), hood=(0, 3), gdn=(-0.4, -1), gdf=(0.4, -1), strings=0, **up),
        P(y=-6, sq=0, tilt=-6, hn=(-6, -13), hf=(8, -14), bn=-2.0, bf=2.0, fn=(-9, 9, 20), ff=(9, 9, -20), ln=-1, lf=1,
          tuft=(0, 1), hood=(0, 1), gdn=(-0.5, -1), gdf=(0.5, -1), **up),
        P(y=-7, sq=1, tilt=-4, hn=(-7, -11), hf=(8, -12), bn=-3.5, bf=3.5, fn=(-10, 11, 10), ff=(10, 11, -10),
          ln=-1, lf=1, tuft=(0, 0), hood=(0, -1), gdn=(-0.8, -1), gdf=(0.8, -1), **up),
        P(y=-4, sq=-2, tilt=0, hn=(-6, -13), hf=(7, -14), bn=1.5, bf=-1.5, fn=(-6, 5, 26), ff=(6, 5, 26),
          tuft=(0, 0), hood=(0, -3), gdn=(-0.3, -1), gdf=(0.3, -1), **up),
        P(y=3, sq=3, tilt=5, hn=(-7, 1), hf=(8, 0), bn=4.0, bf=-4.0, fn=(-7, 0, 0), ff=(7, 0, 0),
          head=(0, 1), tuft=(0, 2), hood=(0, 2), eyes="blink", mouth="open", gn="open", gf="open",
          gdn=(-1, 0.2), gdf=(1, 0.2)),
        P(y=-1, sq=-1, tilt=-2, hn=(-8, 6), hf=(8, 5), bn=-3.5, bf=3.5, fn=(-6, 0, 0), ff=(6, 0, 0),
          tuft=(0, -2), hood=(0, -1), eyes="happy", mouth="grin"),
        P(y=1, sq=1, hn=(-7, 9), hf=(7, 8), bn=-2.5, bf=2.5, tuft=(0, 1), hood=(0, 1), eyes="happy"),
        P(),
    ]
    return render(poses, "player_cheer"), 12, False


# --- sleep --------------------------------------------------------------------------
def lying_head(p):
    """The head turned a quarter: face up, crown to the left, chin to the right."""
    tmp = Cv()
    draw_head(tmp, 0, 0, scaled(p))
    return {(y, -x - 1): c for (x, y), c in tmp.px.items()}


def sleep():
    """Lying on the back on the sofa, head on its side at the left, breathing
    slowly; a snot bubble grows and pops, the foot twitches."""
    breath = [0, 0, 1, 1, 1, 1, 0, 0]
    bubble = [0, 2, 3, 5, 5, 6, -1, 0]
    frames = []
    for i in range(8):
        b = breath[i]
        cv = Cv()
        base = SLEEP_H - 1
        top = base - 18 - 2 * b
        # far leg stretched out, shoe toe-up (it twitches when the bubble pops)
        px = shoe_px(75, base - 3, -68 if i != 6 else -54)
        dy = (base - 3) - max(q[1] for q in px)
        px = {(x, y + dy): c for (x, y), c in px.items()}
        cv.fill(hose((61, base - 8), (72, base - 6), 1.2, LIMB), BLACK[1])
        cv.blob_px(px)
        # near leg with the knee up, shoe flat on the cushion
        px = shoe_px(69, base, 0)
        cv.fill(hose((58, base - 8), (66, base - 7), 6.0 + 0.8 * b, LIMB), BLACK[1])
        cv.blob_px(px)
        # hood squashed under the neck
        hx, hy = 21, base - 17
        hood = oval(hx + 6, hy + 6, hx + 20, hy + 15)
        cv.shaded(hood, HOODIE, (3, 3))
        # torso lying down
        torso = oval(33, top, 63, base - 2)
        keys = {q: ("shorts" if q[0] >= 56 else "line" if q[0] == 55 else "hem" if q[0] >= 52 else "hood") for q in torso}
        cv.blob_px(shade_px(keys, TORSO_RAMPS, (4, 3)))
        cv.fill({(x, top + 3) for x in range(41, 46)} | {(46, top + 2), (40, top + 4)}, RED[4], torso)
        cv.fill({q for q in torso if 44 <= q[0] <= 50 and q[1] == base - 8}, RED[0])          # pocket
        cv.fill({q for q in torso if q[0] in (45, 49) and base - 7 <= q[1] <= base - 5}, RED[0])
        # head lying on its side
        p = P(eyes="sleep", mouth="snore" if b else "o", tuft=(1, 3 if b else 2))
        cv.px.update({(x + hx, y + hy): c for (x, y), c in lying_head(p).items()})
        # near arm resting on the belly, rising with the breath
        sh = (40, top + 6)
        hand = (50, top + 2)
        cv.fill(stroke(bezier(sh, (40, top - 6), hand), LIMB), BLACK[1])
        glove(cv, hand, (1, 0.6))
        # snot bubble from the nose (which now points up)
        r = bubble[i]
        nx, ny = hx + 2, hy - 18
        if r > 0:
            m = disc(nx, ny - r + 1, r + 0.4)
            cv.blob(m, GLASS[3])
            cv.fill(m - shift(m, -1, -1), GLASS[2])
            cv.dots([(nx - r // 2, ny - r - r // 2 + 1), (nx - r // 2 + 1, ny - r - r // 2 + 1)], GLASS[4])
        elif r < 0:
            cv.dots([(nx - 5, ny - 8), (nx + 7, ny - 8), (nx - 7, ny - 2), (nx + 9, ny - 2), (nx + 1, ny - 11),
                     (nx - 4, ny - 7), (nx + 6, ny - 7), (nx + 1, ny - 10)], INK)
        cv.thicken(SLEEP_W, SLEEP_H)
        frames.append(cv.image(SLEEP_W, SLEEP_H, name="player_sleep[%d]" % i))
    return frames, 4, True


# --- extras -------------------------------------------------------------------------
def stretch():
    """Extra: a big yawn and stretch with both arms up (after waking up). Not looping."""
    yawn = dict(eyes="blink", mouth="open", gn="open", gf="open")
    poses = [
        P(mouth="smile"),
        P(sq=1, hn=(-3, 3), hf=(3, 2), bn=-4.0, bf=4.0, eyes="half", mouth="o", tuft=(0, -1)),
        P(y=-1, sq=-1, tilt=-3, hn=(-7, -4), hf=(8, -5), bn=3.0, bf=-3.0, gdn=(-0.7, -1), gdf=(0.7, -1),
          tuft=(0, 1), hood=(0, 1), **yawn),
        P(y=-1, sq=-2, tilt=-7, hn=(-6, -13), hf=(6, -14), bn=2.0, bf=-2.0, gdn=(-0.3, -1), gdf=(0.3, -1),
          fn=(-5, 0, 22), ff=(5, 0, 22), head=(0, -1), tuft=(0, 2), hood=(0, 2), **yawn),
        P(y=-1, sq=-2, tilt=-10, hn=(-6, -12), hf=(8, -13), bn=-1.0, bf=1.0, gdn=(-0.6, -1), gdf=(0.6, -1),
          fn=(-5, 0, 26), ff=(5, 0, 26), head=(0, -1), tuft=(1, 0), hood=(1, 0), **yawn),
        P(y=-1, sq=-2, tilt=-7, hn=(-6, -13), hf=(6, -14), bn=2.0, bf=-2.0, gdn=(-0.3, -1), gdf=(0.3, -1),
          fn=(-5, 0, 22), ff=(5, 0, 22), head=(0, -1), tuft=(-1, 0), **yawn),
        P(sq=0, tilt=-2, hn=(-7, -1), hf=(8, -2), bn=-3.5, bf=3.5, gn="open", gf="open", gdn=(-1, -0.2), gdf=(1, -0.2),
          eyes="half", mouth="o", tuft=(0, -2), hood=(0, -1)),
        P(sq=1, hn=(-7, 8), hf=(7, 7), bn=-3.0, bf=3.0, eyes="blink", mouth="smile", tuft=(0, 1), hood=(0, 1)),
        P(eyes="happy"),
        P(),
    ]
    return render(poses, "player_stretch"), 10, False


def shrug():
    """Extra: palms up and a head shake ("can't" / not enough coins). Not looping."""
    palms = dict(gn="open", gf="open", gdn=(-1, -0.5), gdf=(1, -0.5), eyes="half", mouth="flat")
    poses = [
        P(mouth="smile"),
        P(sq=1, hn=(-6, 8), hf=(6, 7), bn=-3.0, bf=3.0, mouth="flat", tuft=(0, -1)),
        P(sq=-1, hn=(-7, 2), hf=(8, 1), bn=3.5, bf=-3.5, head=(-1, 0), look=(-1, 0), tuft=(1, 1), hood=(1, 0), **palms),
        P(sq=-1, hn=(-7, 1), hf=(8, 0), bn=3.5, bf=-3.5, head=(1, 0), look=(0, 0), tuft=(-2, 0), hood=(-1, 0), **palms),
        P(sq=-1, hn=(-7, 2), hf=(8, 1), bn=3.5, bf=-3.5, head=(-1, 0), look=(-1, 0), tuft=(2, 0), hood=(1, 0), **palms),
        P(sq=-1, hn=(-7, 1), hf=(8, 0), bn=3.5, bf=-3.5, head=(1, 0), look=(0, 0), tuft=(-2, 0), hood=(-1, 0), **palms),
        P(sq=1, hn=(-7, 8), hf=(7, 7), bn=-3.0, bf=3.0, mouth="flat", tuft=(1, 1)),
        P(mouth="smile"),
    ]
    return render(poses, "player_shrug"), 10, False


def watch():
    """Extra idle fidget: lifts the wrist, checks the watch, taps a foot, drops the arm. Not looping."""
    look = dict(hn=(12, 0), bn=-4.0, gn="fist", gdn=(0.6, -1), watch=True, look=(0, 1), head=(0, 1), mouth="flat")
    poses = [
        P(mouth="smile"),
        P(sq=1, hn=(-8, 7), bn=-3.5, mouth="smile", tuft=(0, -1)),
        P(sq=-1, hn=(4, 7), bn=-4.5, gdn=(1, -0.4), watch=True, mouth="smile", tuft=(0, 1)),
        P(tuft=(0, 1), hood=(0, 1), **look),
        P(sq=1, **look),
        P(sq=1, ff=(5, 0, -28), **look),
        P(ff=(5, 0, -28), **look),
        P(**look),
        P(ff=(5, 0, -28), eyes="half", **look),
        P(sq=1, ff=(5, 0, -28), eyes="half", **look),
        P(sq=1, **look),
        P(hn=(12, 0), bn=-4.0, gdn=(0.6, -1), watch=True, eyes="wide", mouth="o", head=(0, 0), tuft=(0, -2)),
        P(sq=-1, hn=(12, -1), bn=-4.0, gdn=(0.6, -1), watch=True, eyes="wide", mouth="open", tuft=(0, -1)),
        P(hn=(3, 8), bn=-4.0, watch=True, mouth="smile", tuft=(0, 1)),
        P(sq=1, hn=(-7, 10), bn=-3.0, mouth="smile", tuft=(0, 1)),
        P(),
    ]
    return render(poses, "player_watch"), 8, False


def wave():
    """Extra: a big friendly wave with the far hand (greeting the salesman, a new robot). Not looping."""
    poses = [P(mouth="smile"),
             P(sq=1, hf=(8, 5), bf=3.5, tuft=(0, -1)),
             P(sq=-1, tilt=-3, hf=(9, -8), bf=-3.5, gf="open", gdf=(0.5, -1), tuft=(0, 1), hood=(0, 1), eyes="happy")]
    for k in range(6):
        a = k % 2
        poses.append(P(sq=-1, tilt=-3, hf=(6 + 3 * a, -13 + 2 * a), bf=-3.0 + 5.0 * a, gf="open",
                       gdf=(-0.4 + 1.0 * a, -1), eyes="happy", tuft=(1 - 2 * a, 0), hood=(0, a),
                       hn=(-7, 9 - a)))
    poses += [P(sq=1, hf=(8, 0), bf=3.5, gf="open", gdf=(1, -0.2), eyes="happy", tuft=(0, 1)),
              P(hf=(7, 8), bf=2.5, tuft=(0, 1)),
              P()]
    return render(poses, "player_wave"), 10, False
