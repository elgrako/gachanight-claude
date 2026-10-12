"""The protagonist as a rubber-hose character: round head with pie eyes, a big
grin and a hair tuft, red hoodie (floppy hood, pocket, strings), blue shorts,
black noodle limbs, white gloves and big mustard shoes. Faces RIGHT in a slight
3/4 from above; 40 x 56 frames, feet on the bottom row, anchored bottom centre.

Every animation is a table of poses; `draw` turns one pose into pixels. The
torso is a bean that tilts around the hips (`tilt`), the head rides on top of
it and stays upright, and the tuft, the hood tip and the hoodie strings are
loose ends that lag behind (follow-through).
"""
import math

from anim_lib import (Cv, oval, disc, rect, stroke, bezier, bend_ctrl, hose, noodle, rot_px, rot_pt, glove,
                      rnd, lerp, ease, shift,
                      INK, RED, DRED, RED_HI, MUSTARD, MUSTARD_SH, MUSTARD_HI, CREAM, CREAM_SH, PAPER,
                      NAVY, BLUE, SKY, GLOVE, PINK, DSTEEL, STEEL, STEEL_HI, WHITE)

W, H = 40, 56
GROUND = 55          # bottom row: the outline of a planted near shoe
CX = 20
HIP = (19, 38)
LEG_LEN = 13.5
SLEEP_W, SLEEP_H = 56, 32

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


# --- parts ----------------------------------------------------------------------
def shoe_fn(u, v):
    if v < 0:
        return None
    toe = ((u - 2.1) / 3.6) ** 2 + ((v - 2.3) / 3.2) ** 2 <= 1.0
    heel = ((u + 2.4) / 3.1) ** 2 + ((v - 1.8) / 2.5) ** 2 <= 1.0
    if not (toe or heel):
        return None
    if v < 1.0:
        return MUSTARD_SH
    if toe and ((u - 2.6) / 2.0) ** 2 + ((v - 4.2) / 1.0) ** 2 <= 1.0:
        return MUSTARD_HI
    return MUSTARD


def shoe(foot, ground):
    """-> (pixels, ankle point). A planted shoe is dropped onto the ground row."""
    fx, lift, pitch = foot
    ox, oy = CX + rnd(fx), ground - rnd(lift)
    px = rot_px(shoe_fn, ox, oy, pitch, 9)
    ankle = rot_pt(-2.0, 3.6, ox, oy, pitch)
    spec = rot_pt(3.4, 4.4, ox, oy, pitch)
    low = max(q[1] for q in px)
    dy = 0
    if rnd(lift) == 0 or low > ground - 1:
        dy = (ground - 1) - low
        px = {(x, y + dy): c for (x, y), c in px.items()}
        ankle = (ankle[0], ankle[1] + dy)
    q = (int(math.floor(spec[0])), int(math.floor(spec[1])) + dy)
    if px.get(q) == MUSTARD_HI:
        px[q] = WHITE                       # specular dot on the toe cap
    return px, ankle


def round_box(x0, y0, x1, y1, n=2.5):
    """Superellipse filling the inclusive pixel box: rounder cheeks than an oval."""
    cx, cy = (x0 + x1 + 1) / 2.0, (y0 + y1 + 1) / 2.0
    rx, ry = (x1 - x0 + 1) / 2.0, (y1 - y0 + 1) / 2.0
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
            if abs((x + 0.5 - cx) / rx) ** n + abs((y + 0.5 - cy) / ry) ** n <= 1.0}


def draw_head(cv, hx, hy, p):
    head = round_box(hx - 10, hy - 9, hx + 9, hy + 8)
    cv.blob(head, CREAM)
    # one shadow shade under the jaw
    jaw = head - shift(head, -1, -2)
    cv.fill({q for q in jaw if q[0] < hx + 3}, CREAM_SH)
    # hair: a black cap over the top and the back of the head
    face = oval(hx - 8, hy - 6, hx + 14, hy + 14)
    hair = head - face
    cv.fill(hair, INK)
    cv.dots([(hx - 6, hy - 6), (hx - 5, hy - 7), (hx - 4, hy - 7), (hx - 7, hy - 4)], DSTEEL)
    # ear
    cv.blob(rect(hx - 7, hy + 1, hx - 6, hy + 2), CREAM)
    # tuft: three licks that lag behind the head, the long one in front
    tx, ty = p["tuft"]
    tip = (hx + 4 + tx, hy - 13 + ty)
    cv.fill(stroke(bezier((hx - 3, hy - 9), (hx - 3 + tx * 0.3, hy - 14 + ty), tip), 2), INK)
    cv.fill(stroke(bezier((hx - 5, hy - 8), (hx - 7 + tx * 0.5, hy - 11 + ty), (hx - 8 + tx, hy - 11 + ty)), 2), INK)

    eyes = p["eyes"]
    lx, ly = rnd(p["look"][0]), rnd(p["look"][1])
    e_top, e_bot = hy - 5, hy + 1
    near = oval(hx + 0, e_top, hx + 3, e_bot)
    far = oval(hx + 5, e_top, hx + 7, e_bot)
    if eyes in ("open", "half", "wide"):
        if eyes == "wide":
            near = oval(hx + 0, e_top - 1, hx + 3, e_bot)
            far = oval(hx + 5, e_top - 1, hx + 7, e_bot)
        if eyes == "half":                             # heavy lids: only the lower half shows
            near = {q for q in near if q[1] >= hy - 2}
            far = {q for q in far if q[1] >= hy - 2}
        cv.blob(near, GLOVE)
        cv.blob(far, GLOVE)
        top = hy - 3 if eyes != "half" else hy - 2
        bot = hy if eyes != "wide" else hy - 1
        cv.fill(rect(hx + 2 + lx, top + ly, hx + 3 + lx, bot + ly), INK, near)
        cv.fill(rect(hx + 6 + lx, top + ly, hx + 7 + lx, bot + ly), INK, far)
        if eyes == "half":
            cv.dots([(0, -3), (1, -3), (2, -3), (3, -3), (5, -3), (6, -3), (7, -3)], INK, hx, hy)
    elif eyes == "blink":
        cv.dots([(0, -1), (1, 0), (2, 0), (3, -1), (5, -1), (6, 0), (7, -1)], INK, hx, hy)
    elif eyes == "happy":
        cv.dots([(0, -1), (1, -2), (2, -2), (3, -1), (5, -1), (6, -2), (7, -1), (0, 0), (3, 0), (5, 0), (7, 0)], INK, hx, hy - 1)
    elif eyes == "sleep":
        cv.dots([(-1, -1), (0, 0), (1, 0), (2, 0), (3, -1), (5, -1), (6, 0), (7, 0), (8, -1)], INK, hx, hy)

    # nose, cheek, mouth
    cv.fill(rect(hx + 9, hy + 1, hx + 10, hy + 2), INK)
    cv.fill(rect(hx - 4, hy + 2, hx - 3, hy + 3), PINK)
    mouth = p["mouth"]
    if mouth == "grin":                                # wide open smile: teeth above, tongue below
        cv.dots([(x, 3) for x in range(0, 8)] + [(-1, 2), (0, 4), (7, 4), (1, 5), (6, 5)]
                + [(x, 6) for x in range(2, 6)], INK, hx, hy)
        cv.dots([(x, 4) for x in range(1, 7)], GLOVE, hx, hy)
        cv.dots([(2, 5), (5, 5)], DRED, hx, hy)
        cv.dots([(3, 5), (4, 5)], PINK, hx, hy)
    elif mouth == "smile":                             # closed, from cheek to cheek
        cv.dots([(-1, 2), (0, 3), (1, 4), (2, 5), (3, 5), (4, 5), (5, 5), (6, 4), (7, 3), (8, 2)], INK, hx, hy)
    elif mouth == "open":
        m = oval(hx + 1, hy + 3, hx + 7, hy + 7) & head
        cv.fill(m, INK)
        inner = oval(hx + 2, hy + 4, hx + 6, hy + 6)
        cv.fill(inner, DRED, m)
        cv.fill(rect(hx + 3, hy + 6, hx + 5, hy + 6), PINK, m)
        cv.dots([(0, 3), (8, 3)], INK, hx, hy)
    elif mouth == "o":
        cv.fill(rect(hx + 4, hy + 4, hx + 5, hy + 5), INK)
    elif mouth == "flat":
        cv.dots([(2, 5), (3, 5), (4, 5), (5, 5), (6, 5)], INK, hx, hy)
    elif mouth == "snore":
        cv.fill(oval(hx + 3, hy + 3, hx + 6, hy + 6), INK)
        cv.fill(rect(hx + 4, hy + 4, hx + 5, hy + 5), DRED)
    sweat = p.get("sweat", 0)
    if sweat:
        sx, sy = hx - 9 - 2 * sweat, hy - 9 - sweat
        cv.blob({(sx, sy), (sx, sy + 1), (sx - 1, sy + 1)}, SKY)


def draw_hood(cv, hx, hy, p):
    """Floppy hood hanging at the nape; its tip lags behind the head."""
    dx, dy = p["hood"]
    dx, dy = rnd(dx), rnd(dy)
    body = oval(hx - 12, hy + 2, hx - 5, hy + 10)
    tip = disc(hx - 11 + dx, hy + 8 + dy, 2.6)
    link = disc(hx - 10 + rnd(dx * 0.5), hy + 7 + rnd(dy * 0.5), 2.6)
    hood = body | tip | link
    cv.blob(hood, RED)
    cv.fill(hood - shift(hood, 1, -2), DRED)
    # the fold of the opening
    cv.dots([(hx - 9, hy + 3), (hx - 10, hy + 4), (hx - 10, hy + 5)], RED_HI)


def draw_arm(cv, shoulder, hand_rel, bend, kind, gdir=None, watch=False):
    hand = (shoulder[0] + hand_rel[0], shoulder[1] + hand_rel[1])
    ctrl = bend_ctrl(shoulder, hand, bend)
    pts = bezier(shoulder, ctrl, hand)
    arm = stroke(pts, 3)
    cv.fill(arm, INK)
    d = gdir or (hand[0] - ctrl[0], hand[1] - ctrl[1])
    if abs(d[0]) + abs(d[1]) < 0.01:
        d = (0, 1)
    glove(cv, hand, d, kind)
    if watch:                                          # a chunky wrist watch over the cuff
        n = math.hypot(d[0], d[1])
        wx, wy = rnd(hand[0] - d[0] / n * 5.0), rnd(hand[1] - d[1] / n * 5.0)
        cv.blob(rect(wx - 1, wy - 1, wx + 1, wy + 1), MUSTARD)
        cv.px[(wx, wy)] = PAPER
        cv.px[(wx + 1, wy + 1)] = MUSTARD_SH
    return hand


def geo(p):
    """Skeleton of a pose: hips, the torso frame, head centre, shoulders."""
    hipx, hipy = HIP[0] + rnd(p["x"]), HIP[1] + rnd(p["y"])
    sq = p["sq"]
    tilt = p["tilt"]

    def loc(u, v):
        v2 = v - sq * clamp(v, 0.0, 14.0) / 14.0
        return rot_pt(u, v2, hipx, hipy, tilt)

    hc = loc(1.0, 19.0)
    hx = rnd(hc[0] + p["head"][0])
    hy = rnd(hc[1] + p["head"][1])
    sn = loc(-5.0, 7.5)
    sf = loc(4.5, 7.5)
    return hipx, hipy, loc, hx, hy, (rnd(sn[0]), rnd(sn[1])), (rnd(sf[0]), rnd(sf[1]))


def torso_px(hipx, hipy, tilt, sq):
    sy = (14.0 - sq) / 14.0
    sx = 1.0 + 0.045 * sq

    def fn(u, v):
        uu, vv = u / sx, v / sy
        w = vv - 5.0
        ru = 7.0 - (0.9 * w / 7.0 if w > 0 else 0.0)
        if (uu / ru) ** 2 + (w / 7.0) ** 2 > 1.0:
            return None
        if vv < 2.0:
            return BLUE
        if vv < 3.0:
            return INK
        return RED

    px = rot_px(fn, hipx, hipy, tilt, 18)
    mask = set(px)
    for q in mask - shift(mask, -2, -1):
        if px[q] == RED:
            px[q] = DRED
        elif px[q] == BLUE:
            px[q] = NAVY
    return px


def draw(p, name="player"):
    cv = Cv()
    hipx, hipy, loc, hx, hy, sh_n, sh_f = geo(p)

    # far arm, behind everything
    draw_arm(cv, sh_f, p["hf"], p["bf"], p["gf"], p["gdf"])
    # legs: far then near
    for foot, hip, ground, side in ((p["ff"], (hipx + 2, hipy - 1), GROUND - 1, p["lf"]),
                                    (p["fn"], (hipx - 2, hipy - 1), GROUND, p["ln"])):
        px, ankle = shoe(foot, ground)
        cv.fill(noodle(hip, ankle, LEG_LEN, side), INK)
        cv.blob_px(px)
    draw_hood(cv, hx, hy, p)
    # torso: hoodie and shorts
    torso = torso_px(hipx, hipy, p["tilt"], p["sq"])
    cv.blob_px(torso)
    hi = loc(-4.6, 9.6)
    cv.dots([(rnd(hi[0]), rnd(hi[1])), (rnd(hi[0]), rnd(hi[1]) + 1), (rnd(hi[0]) + 1, rnd(hi[1]) - 1)], RED_HI)
    # pocket opening: a short dark arc on the belly
    for u, v in ((0.5, 4.6), (1.5, 5.4), (2.5, 5.8), (3.5, 5.8), (4.5, 5.4)):
        q = loc(u, v)
        q = (int(math.floor(q[0])), int(math.floor(q[1])))
        if torso.get(q) == RED:
            cv.px[q] = DRED
    # hoodie strings hang straight down and sway
    sway = rnd(p["strings"])
    for u in (2.6, 5.2):
        s = loc(u, 9.4)
        x, y = rnd(s[0]), rnd(s[1])
        for k, q in enumerate(((x, y), (x, y + 1), (x + sway, y + 2))):
            if q in torso:
                cv.px[q] = PAPER
    draw_head(cv, hx, hy, p)
    # near arm in front
    draw_arm(cv, sh_n, p["hn"], p["bn"], p["gn"], p["gdn"], watch=p["watch"])
    return cv


def render(poses, name):
    return [draw(p).image(W, H, name="%s[%d]" % (name, i)) for i, p in enumerate(poses)]


def hand_pos(p, near=True):
    """Glove centre in frame pixels."""
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
WALK_STEP = 3                       # px a planted foot slides back per frame
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
RUN_STEP = 6
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
    draw_head(tmp, 0, 0, p)
    return {(y, -x - 1): c for (x, y), c in tmp.px.items()}


def sleep():
    """Lying on the back on the sofa, head on its side at the left, breathing
    slowly; a snot bubble grows and pops, the foot twitches."""
    breath = [0, 0, 1, 1, 1, 1, 0, 0]
    bubble = [0, 1, 2, 3, 3, 4, -1, 0]
    frames = []
    for i in range(8):
        b = breath[i]
        cv = Cv()
        base = SLEEP_H - 1
        top = base - 12 - b
        # far leg stretched out, shoe toe-up (it twitches when the bubble pops)
        px = rot_px(shoe_fn, 50, base - 2, -68 if i != 6 else -56, 9)
        dy = (base - 2) - max(q[1] for q in px)
        px = {(x, y + dy): c for (x, y), c in px.items()}
        cv.fill(hose((41, base - 5), (48, base - 4), 0.8), INK)
        cv.blob_px(px)
        # near leg with the knee up, shoe flat on the cushion
        px = rot_px(shoe_fn, 46, base, 0, 9)
        cv.fill(hose((39, base - 5), (44, base - 5), 4.0 + 0.5 * b), INK)
        cv.blob_px(px)
        # hood squashed under the neck
        hx, hy = 14, base - 11
        hood = oval(hx + 4, hy + 4, hx + 13, hy + 10)
        cv.blob(hood, RED)
        cv.fill(hood - shift(hood, 1, -2), DRED)
        # torso lying down
        torso = oval(22, top, 42, base - 1)
        cv.blob(torso, RED)
        cv.fill(torso - shift(torso, -1, -2), DRED)
        cv.dots([(28, top + 2), (29, top + 2), (30, top + 1)], RED_HI)
        shorts = {q for q in torso if q[0] >= 37}
        cv.fill(shorts, BLUE)
        cv.fill(shorts - shift(torso, -1, -2), NAVY)
        cv.fill({q for q in torso if q[0] == 36}, INK)
        cv.fill({q for q in torso if q[0] in (30, 31, 32, 33) and q[1] == base - 5}, DRED)      # pocket
        # head lying on its side
        p = P(eyes="sleep", mouth="snore" if b else "o", tuft=(0, 1 if b else 0))
        cv.px.update({(x + hx, y + hy): c for (x, y), c in lying_head(p).items()})
        # near arm resting on the belly, rising with the breath
        sh = (27, top + 4)
        hand = (33, top + 1)
        cv.fill(stroke(bezier(sh, (27, top - 4), hand), 3), INK)
        glove(cv, hand, (1, 0.6))
        # snot bubble from the nose (which now points up)
        r = bubble[i]
        nx, ny = hx + 2, hy - 12
        if r > 0:
            cv.blob(disc(nx + 1, ny - r + 1, r + 0.4), SKY)
            cv.px[(nx, ny - r)] = WHITE
        elif r < 0:
            cv.dots([(nx - 3, ny - 5), (nx + 5, ny - 5), (nx - 4, ny - 1), (nx + 6, ny - 1), (nx + 1, ny - 7)], INK)
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
