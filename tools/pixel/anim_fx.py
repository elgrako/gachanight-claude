"""Effects and small objects in the same chunky rubber-hose look: flat fills,
one shadow and one highlight shade, bold ink outline.

coin_spin, coin_pickup, coin_flip, capsule_open (five colours), sparkle,
rarity_burst, zzz, dust_puff, speech_dots.
"""
import math

from pixlib import box

from anim_lib import (Cv, oval, disc, rect, stroke, star_mask, rot_px, rnd, shift,
                      INK, RED, DRED, RED_HI, MUSTARD, MUSTARD_SH, MUSTARD_HI, CREAM, CREAM_SH, PAPER,
                      NAVY, BLUE, SKY, GREEN, GREEN_SH, GLOVE, PINK, WHITE, rgb)

GREEN_HI = rgb("#7fd68e")
GOLD = rgb("#ffcf2e")
GOLD_HI = rgb("#fff3a8")
GOLD_SH = rgb("#d9901a")


# --- coin ---------------------------------------------------------------------------
def coin_px(x0, y0, w, h, size):
    """Coin inside a size x size box at (x0, y0), squeezed to w x h (spin / flip)."""
    ax = x0 + (size - w) // 2
    ay = y0 + (size - h) // 2
    m = oval(ax, ay, ax + w - 1, ay + h - 1) if min(w, h) > 2 else rect(ax, ay, ax + w - 1, ay + h - 1)
    px = {q: MUSTARD for q in m}
    if min(w, h) <= 2:
        for (x, y) in m:
            if (w <= 2 and x == ax) or (h <= 2 and y == ay):
                px[(x, y)] = MUSTARD_HI
            else:
                px[(x, y)] = MUSTARD_SH
        return px
    for q in m - shift(m, -1, -1):
        px[q] = MUSTARD_SH
    for q in m - shift(m, 1, 1):
        if q[0] + q[1] < ax + ay + (w + h) // 2:
            px[q] = MUSTARD_HI
    if w >= size - 2 and h >= size - 2:
        cx, cy = x0 + size // 2, y0 + size // 2
        for q in rect(cx - 1, cy - 1, cx, cy):          # square hole, like an old 50 yen coin
            px[q] = INK
        px[(cx - 2, cy - 3)] = WHITE
    elif w >= 4 and h >= 4:
        cx, cy = x0 + size // 2, y0 + size // 2
        if w < h:
            px[(cx - 1, cy - 1)] = INK
            px[(cx - 1, cy)] = INK
        else:
            px[(cx - 1, cy - 1)] = INK
            px[(cx, cy - 1)] = INK
    return px


def coin_spin():
    """Upright coin spinning on the floor, resting on the bottom row."""
    frames = []
    for i, w in enumerate((10, 8, 4, 2, 4, 8)):
        cv = Cv()
        cv.blob_px(coin_px(1, 1, w, 10, 10))
        frames.append(cv.image(12, 12, name="coin_spin[%d]" % i))
    return frames, 10, True


def twinkle(cv, cx, cy, r, rot=0.0, col=WHITE, inner=0.32):
    if r < 1.2:
        cv.blob({(rnd(cx), rnd(cy))}, col)
        return
    cv.blob(star_mask(cx + 0.5, cy + 0.5, r, max(0.8, r * inner), 4, rot), col)


def coin_pickup():
    """The coin pops up spinning and turns into a twinkle."""
    frames = []
    seq = [(17, 10), (10, 4), (5, 10), (2, 4), (1, 10)]
    for i, (y0, w) in enumerate(seq):
        cv = Cv()
        cv.blob_px(coin_px(5, y0, w, 10, 10))
        if i == 1:
            cv.blob(rect(4, 25, 5, 26), CREAM)
            cv.blob(rect(14, 25, 15, 26), CREAM)
        frames.append(cv)
    for r, rot, extra in ((7.5, 0, False), (6, 45, True), (3.5, 0, True), (0, 0, True)):
        cv = Cv()
        if r:
            twinkle(cv, 9.5, 6, r, rot, MUSTARD_HI if rot else WHITE)
        if extra:
            d = 6 if r > 4 else (8 if r else 9)
            for (ax, ay) in ((-1, -0.7), (1, -0.6), (-0.9, 0.9), (1, 0.8)):
                x, y = rnd(9.5 + ax * d), rnd(6.5 + ay * d * 0.7)
                if r:
                    cv.blob({(x, y)}, WHITE)
                else:
                    cv.px[(x, y)] = INK
        frames.append(cv)
    return [cv.image(20, 28, name="coin_pickup[%d]" % i) for i, cv in enumerate(frames)], 16, False


def coin_flip():
    """A coin tossed up, flipping, then dropping edge-on into a slot at the bottom."""
    seq = [  # (top y of the 8 px box, w, h)
        (18, 8, 8), (11, 8, 4), (6, 8, 2), (3, 8, 6), (1, 8, 8), (2, 8, 4),
        (5, 8, 2), (9, 6, 8), (14, 2, 8), (19, 2, 8), (23, 2, 8),
    ]
    frames = []
    for i, (y0, w, h) in enumerate(seq):
        cv = Cv()
        px = coin_px(2, y0, w, h, 8)
        cv.blob_px(px)
        if i == 0:
            cv.dots([(2, 27), (9, 27)], INK)
        if y0 > 18:                                   # sinking into the slot
            cv.erase({q for q in list(cv.px) if q[1] > 26})
            cv.fill(rect(3, 27, 8, 27), INK)
        frames.append(cv)
    cv = Cv()                                         # clink
    cv.fill(rect(3, 27, 8, 27), INK)
    twinkle(cv, 5.5, 22, 3.2, 0, WHITE)
    cv.dots([(1, 24), (10, 24), (2, 19), (9, 19)], INK)
    frames.append(cv)
    return [cv.image(12, 28, name="coin_flip[%d]" % i) for i, cv in enumerate(frames)], 16, False


# --- capsule ------------------------------------------------------------------------
CAPSULE_COLOURS = {
    "red": (RED, RED_HI, DRED),
    "blue": (BLUE, SKY, NAVY),
    "green": (GREEN, GREEN_HI, GREEN_SH),
    "mustard": (MUSTARD, MUSTARD_HI, MUSTARD_SH),
    "gold": (GOLD, GOLD_HI, GOLD_SH),
}
CAP_R = 9.0
CAP_C = (20, 23)


def capsule_fn(colours, part="both", sx=1.0, sy=1.0, emblem=False):
    """Local shape of the reference capsule: coloured top, cream bottom, seen from above-front."""
    col, hi, sh = colours

    def fn(u, v):
        u, v = u / sx, v / sy
        d2 = u * u + v * v
        if d2 > CAP_R * CAP_R:
            return None
        seam = -0.24 * math.sqrt(max(0.0, CAP_R * CAP_R - u * u))
        top = v > seam
        if part == "top" and not top:
            return None
        if part == "bottom" and top:
            # the open mouth of the cup: the back half of the rim ellipse
            if v < -seam and abs(u) < CAP_R - 0.6:
                return CREAM_SH if v < -seam - 1.0 else INK
            return None
        if part == "both" and abs(v - seam) < 0.55:
            return INK
        shadow = (u + 2.4) ** 2 + (v - 2.4) ** 2 > (CAP_R - 0.9) ** 2
        if top:
            if ((u + 3.6) / 2.4) ** 2 + ((v - 4.6) / 1.4) ** 2 <= 1.0:
                return WHITE
            if emblem and abs(u - 2.0) + abs(v - 3.0) <= 1.6:
                return WHITE
            if part == "top" and v < seam + 1.2:
                return sh
            return sh if shadow else col
        if part == "bottom" and v > seam - 1.2:
            return PAPER
        return CREAM_SH if shadow else CREAM

    return fn


def rays(cv, cx, cy, r0, r1, count, rot, col=WHITE, width=2.2):
    for k in range(count):
        a = math.radians(rot + 360.0 * k / count)
        ca, sa = math.cos(a), math.sin(a)
        nx, ny = -sa, ca
        pts = [(cx + ca * r0 + nx * width, cy + sa * r0 + ny * width),
               (cx + ca * r1, cy + sa * r1),
               (cx + ca * r0 - nx * width, cy + sa * r0 - ny * width)]
        from pixlib import poly
        m = {q for q in poly(pts)}
        if m:
            cv.blob(m, col)


CAPSULE_FLASH_FRAME = 7

# Confetti thrown out by the capsule: (angle deg, speed px/frame, colour slot, shape).
CONFETTI = [(-100, 5.2, 0, 0), (-62, 5.8, 1, 1), (-28, 5.0, 2, 2), (-140, 5.6, 3, 1), (-170, 4.6, 1, 0),
            (-8, 4.4, 0, 1), (-80, 6.6, 4, 2), (-122, 6.4, 2, 0), (-45, 6.8, 3, 0), (-155, 6.0, 0, 2),
            (15, 3.8, 4, 0), (-195, 3.8, 2, 1)]
CONFETTI_SHAPES = (((0, 0), (1, 0)), ((0, 0), (0, 1)), ((0, 0), (1, 0), (0, 1), (1, 1)))


def confetti(cv, cx, cy, age, palette, w=40, h=40):
    """Paper bits flying out from (cx, cy): fast at first, slowing, then falling and tumbling."""
    for k, (ang, speed, slot, shape) in enumerate(CONFETTI):
        if age > 3 + k % 3:                              # they wink out one after the other
            continue
        a = math.radians(ang)
        dist = speed * (1.0 - 0.72 ** age) / 0.28        # geometric slow-down
        x = cx + math.cos(a) * dist
        y = cy + math.sin(a) * dist + 0.45 * age * age   # gravity
        cells = CONFETTI_SHAPES[(shape + age) % 2 if shape < 2 else 2]
        m = {(rnd(x) + ax, rnd(y) + ay) for (ax, ay) in cells}
        if all(1 <= qx < w - 1 and 1 <= qy < h - 1 for (qx, qy) in m):
            cv.blob(m, palette[slot % len(palette)])


def capsule_open(colour):
    """14 frames: shakes harder and harder, squashes, cracks with light, bursts
    (frame 7), the two halves fly apart tumbling and pop, confetti rains down."""
    colours = CAPSULE_COLOURS[colour]
    gold = colour == "gold"
    cx, cy = CAP_C
    frames = []
    palette = [colours[0], MUSTARD, PAPER, colours[1], GOLD_HI if gold else PINK]
    lite = GOLD_HI if gold else WHITE

    def whole(dx=0, dy=0, rot=0.0, sx=1.0, sy=1.0):
        cv = Cv()
        cv.blob_px(rot_px(capsule_fn(colours, "both", sx, sy, gold), cx + dx, cy + dy, rot, 14))
        return cv

    def half(cv, part, dx, dy, rot, sx, sy=None):
        sy = sx if sy is None else sy
        cv.blob_px(rot_px(capsule_fn(colours, part, sx, sy, gold and part == "top"), cx + dx, cy + dy, rot, 14))

    # 0 rest, 1-4 shaking harder and harder with little hops
    frames.append(whole())
    for (dx, dy, rot, sx, sy) in ((-2, 0, -10, 1.0, 1.0), (2, -1, 12, 0.97, 1.04), (-3, 0, -20, 1.04, 0.96),
                                  (3, -2, 22, 0.95, 1.06)):
        cv = whole(dx, dy, rot, sx, sy)
        if abs(dx) == 3:
            s_ = 1 if dx > 0 else -1
            cv.dots([(cx - s_ * 13, cy - 6), (cx - s_ * 14, cy - 3), (cx - s_ * 13, cy + 1)], INK)
            cv.dots([(cx + s_ * 14, cy - 8), (cx + s_ * 15, cy - 5)], INK)
        frames.append(cv)
    # 5 squash down (anticipation)
    cv = whole(0, 3, 0, 1.18, 0.8)
    cv.dots([(cx - 13, cy + 8), (cx + 12, cy + 8)], INK)
    frames.append(cv)
    # 6 stretch up, the seam cracks with light
    cv = Cv()
    half(cv, "bottom", 0, 1, 0, 0.96, 1.06)
    rays(cv, cx, cy - 1, 9.5, 15.0, 2, 0, WHITE, 2.0)
    rays(cv, cx, cy - 1, 9.5, 13.0, 4, 45, lite, 1.4)
    cv.blob(oval(cx - 9, cy - 3, cx + 8, cy + 1), WHITE)
    half(cv, "top", 0, -5, 0, 0.96, 1.06)
    frames.append(cv)
    # 7 the big flash
    cv = Cv()
    half(cv, "top", -4, -10, -18, 0.92)
    half(cv, "bottom", 3, 5, 12, 1.0)
    rays(cv, cx, cy - 2, 10, 19, 8, 22.5, GOLD_HI if gold else PAPER, 3.2)
    cv.blob(star_mask(cx, cy - 2, 17, 8, 8, 0), WHITE)
    cv.fill(disc(cx, cy - 2, 5), GOLD_HI if gold else PAPER)
    frames.append(cv)
    # 8-10 the halves tumble apart on arcs, rays thin out, confetti flies
    cv = Cv()
    rays(cv, cx, cy - 2, 11, 18, 8, 0, WHITE, 1.6)
    cv.blob(star_mask(cx, cy - 2, 9, 4, 4, 0), WHITE)
    half(cv, "top", -8, -12, -48, 0.82)
    half(cv, "bottom", 7, 4, 38, 0.86)
    confetti(cv, cx, cy - 2, 1, palette)
    frames.append(cv)
    cv = Cv()
    twinkle(cv, cx, cy - 3, 5, 45, WHITE)
    half(cv, "top", -11, -11, -95, 0.64)
    half(cv, "bottom", 10, 6, 80, 0.68)
    twinkle(cv, 32, 7, 3, 0, lite)
    confetti(cv, cx, cy - 2, 2, palette)
    frames.append(cv)
    cv = Cv()
    half(cv, "top", -13, -7, -150, 0.46)
    half(cv, "bottom", 12, 10, 130, 0.5)
    twinkle(cv, cx, cy - 4, 3, 0, WHITE)
    twinkle(cv, 7, 27, 2, 45, lite)
    confetti(cv, cx, cy - 2, 3, palette)
    frames.append(cv)
    # 11 the halves pop into twinkles
    cv = Cv()
    twinkle(cv, cx - 13, cy - 3, 4, 0, WHITE)
    twinkle(cv, cx + 12, cy + 12, 4, 45, WHITE)
    twinkle(cv, 33, 6, 2, 45, lite)
    confetti(cv, cx, cy - 2, 4, palette)
    frames.append(cv)
    # 12-13 the last confetti and glitter
    cv = Cv()
    for (x, y, r, rot) in ((cx - 13, cy - 3, 2, 45), (cx + 12, cy + 12, 2, 0), (20, 5, 2, 0)):
        twinkle(cv, x, y, r, rot, lite)
    confetti(cv, cx, cy - 2, 5, palette)
    frames.append(cv)
    cv = Cv()
    for (x, y) in ((7, 9), (34, 6), (5, 30), (33, 33), (20, 4)):
        twinkle(cv, x, y, 1, 0, lite)
    frames.append(cv)
    if gold:                                           # extra glitter while it shakes
        for i, pts in ((1, ((5, 8, 2),)), (2, ((34, 10, 2),)), (3, ((6, 30, 2), (33, 6, 3))), (4, ((5, 9, 3), (34, 30, 2))),
                       (5, ((4, 14, 2), (35, 14, 2)))):
            for (x, y, r) in pts:
                twinkle(frames[i], x, y, r, 0, GOLD_HI)
    name = "capsule_open" if colour == "red" else "capsule_open_" + colour
    return [cv.image(40, 40, name="%s[%d]" % (name, i)) for i, cv in enumerate(frames)], 14, False


# --- sparkle / burst ----------------------------------------------------------------
def sparkle():
    frames = []
    for i, (r, rot, dots) in enumerate(((2, 0, 0), (5, 0, 0), (7, 0, 5), (5, 45, 6), (3, 0, 7), (0, 0, 7))):
        cv = Cv()
        if r:
            twinkle(cv, 7.5, 7.5, r, rot, WHITE if i != 3 else MUSTARD_HI)
        if dots:
            for (ax, ay) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                q = (rnd(7.5 + ax * dots * 0.75), rnd(7.5 + ay * dots * 0.75))
                if r:
                    cv.blob({q}, WHITE) if 1 <= q[0] <= 14 and 1 <= q[1] <= 14 else None
                else:
                    cv.px[q] = WHITE
        frames.append(cv.image(16, 16, name="sparkle[%d]" % i))
    return frames, 14, False


def burst_confetti(cv, c, age):
    """White paper bits (the game tints them): thrown out past the ring,
    slowing down, then tumbling to the ground one after the other."""
    for k in range(16):
        ang = math.radians(k * 137.5 + 20)               # golden angle: an even, irregular scatter
        speed = 5.0 + (k * 5 % 7) * 0.8
        if age > 5 + k % 4:
            continue
        dist = 12.0 + speed * (1.0 - 0.7 ** age) / 0.3
        x = rnd(c + math.cos(ang) * dist + (1.5 * math.sin(age * 1.7 + k) if age > 3 else 0.0))
        y = rnd(c + math.sin(ang) * dist * 0.9 + 0.22 * age * age)
        kind = k % 3
        flip = (age + k) % 2
        if kind == 0:                                    # a tumbling strip
            m = rect(x, y, x + 2, y + 1) if flip else rect(x, y, x + 1, y + 2)
        elif kind == 1:                                  # a square seen flat, then edge on
            m = rect(x, y, x + 1, y + 1) if flip else rect(x, y, x + 2, y)
        else:                                            # a little diamond
            m = {(x, y), (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)} if flip else rect(x, y, x, y + 1)
        if all(1 <= qx < 63 and 1 <= qy < 63 for (qx, qy) in m):
            cv.blob(m, WHITE)


def rarity_burst():
    """White cartoon burst the game tints: pop, starburst, ring of rays, stars, a shower of confetti."""
    c = 32
    frames = []
    spec = [
        dict(star=(8, 4, 8, 0)),
        dict(star=(18, 9, 8, 0), rays=(12, 24, 8, 22.5, 3.0)),
        dict(star=(25, 13, 10, 18), rays=(18, 30, 10, 0, 3.4)),
        dict(star=(20, 14, 10, 0), rays=(22, 31, 10, 18, 3.0), hole=7),
        dict(ring=(19, 5), rays=(24, 31, 10, 0, 2.4), stars=(27, 4, 0)),
        dict(ring=(23, 3), rays=(27, 31, 10, 18, 1.6), stars=(28, 3.5, 45), conf=1),
        dict(ring=(26, 2, 8), stars=(29, 3, 0), conf=2),
        dict(stars=(30, 2, 45), conf=3),
        dict(conf=4),
        dict(conf=5),
        dict(conf=6),
        dict(conf=7),
        dict(conf=8),
    ]
    for i, s in enumerate(spec):
        cv = Cv()
        if "conf" in s:
            burst_confetti(cv, c, s["conf"])
        if "rays" in s:
            r0, r1, n, rot, w = s["rays"]
            rays(cv, c, c, r0, r1, n, rot, WHITE, w)
        if "star" in s:
            ro, ri, n, rot = s["star"]
            m = star_mask(c, c, ro, ri, n, rot)
            if "hole" in s:
                m -= disc(c, c, s["hole"])
            cv.blob(m, WHITE)
        if "ring" in s:
            r, th = s["ring"][0], s["ring"][1]
            m = set()
            for y in range(64):
                for x in range(64):
                    d = math.hypot(x + 0.5 - c, y + 0.5 - c)
                    if abs(d - r) <= th / 2.0:
                        if len(s["ring"]) > 2:
                            a = (math.degrees(math.atan2(y + 0.5 - c, x + 0.5 - c)) + 360) % (360.0 / s["ring"][2])
                            if a > 360.0 / s["ring"][2] * 0.55:
                                continue
                        m.add((x, y))
            cv.blob(m, WHITE)
        if "stars" in s:
            d, r, rot = s["stars"]
            for k in range(6):
                a = math.radians(60 * k + 30)
                twinkle(cv, c + math.cos(a) * d * 0.95, c + math.sin(a) * d * 0.95, r, rot, WHITE)
        cv.px = {q: col for q, col in cv.px.items() if 0 <= q[0] < 64 and 0 <= q[1] < 64}
        frames.append(cv.image(64, 64, name="rarity_burst[%d]" % i))
    return frames, 16, False


# --- zzz ----------------------------------------------------------------------------
def letter_z(cv, x, y, size, col=PAPER):
    """Z of the given size with its top-left at (x, y), outlined."""
    m = set()
    for i in range(size):
        m.add((x + i, y))
        m.add((x + i, y + size - 1))
        m.add((x + size - 1 - i, y + i))
    cv.blob(m, col)


def zzz():
    """Two Zs drifting up and to the right, growing as they rise; loops."""
    frames = []
    n = 8
    for i in range(n):
        cv = Cv()
        for k in range(2):
            ph = ((i + k * n / 2.0) % n) / n          # 0 just born .. 1 gone
            size = 3 if ph < 0.25 else (4 if ph < 0.6 else 5)
            x = rnd(1 + ph * 9)
            y = rnd(12 - ph * 12)
            letter_z(cv, x, y, size)
        cv.px = {q: c for q, c in cv.px.items() if 0 <= q[0] < 16 and 0 <= q[1] < 16}
        frames.append(cv.image(16, 16, name="zzz[%d]" % i))
    return frames, 6, True


# --- dust ---------------------------------------------------------------------------
def dust_puff():
    """A little cloud kicked up at the feet: pops, billows, splits into three
    round puffs that drift up and out, shrinking to specks."""
    frames = []
    spec = [
        [(6, 7, 10, 10)],
        [(3, 6, 8, 10), (8, 5, 13, 10), (6, 3, 10, 7)],
        [(1, 5, 6, 10), (9, 4, 14, 9), (5, 2, 10, 7), (5, 7, 10, 10)],
        [(1, 4, 5, 8), (10, 3, 14, 7), (6, 1, 9, 4), (7, 8, 8, 9)],
        [(1, 3, 3, 5), (12, 2, 14, 4), (7, 1, 8, 2)],
        [(1, 2, 1, 2), (14, 1, 14, 1), (7, 1, 7, 1)],
    ]
    for i, puffs in enumerate(spec):
        cv = Cv()
        if i < 3:                                      # one billowing cloud
            m = set()
            for (x0, y0, x1, y1) in puffs:
                m |= oval(x0, y0, x1, y1)
            cv.blob(m, PAPER)
            cv.fill(m - shift(m, -1, -1), CREAM_SH)
            cv.fill({q for q in m - shift(m, 1, 1) if q[1] < 5}, WHITE)
        else:                                          # separate puffs
            for (x0, y0, x1, y1) in puffs:
                d = oval(x0, y0, x1, y1) if x1 - x0 >= 2 else rect(x0, y0, x1, y1)
                cv.blob(d, PAPER)
                if x1 - x0 >= 3:
                    cv.fill(d - shift(d, -1, -1), CREAM_SH)
        frames.append(cv.image(16, 12, name="dust_puff[%d]" % i))
    return frames, 14, False


# --- speech dots --------------------------------------------------------------------
def speech_dots():
    """Three dots bouncing one after the other inside a speech bubble; loops."""
    frames = []
    hop = [0, -2, -3, -2, 0, 0, 0, 0]
    for i in range(8):
        cv = Cv()
        bubble = box(1, 1, 18, 9, 2)
        tail = {(4, 10), (5, 10), (4, 11), (3, 12)} - {(3, 12)}
        cv.blob(bubble | tail | {(3, 11)}, PAPER)
        cv.fill({q for q in bubble if q[1] == 9}, CREAM)
        for k in range(3):
            dy = hop[(i - k * 2) % 8]
            x = 5 + k * 4
            cv.fill(rect(x, 5 + dy, x + 1, 6 + dy), INK)
        frames.append(cv.image(20, 14, name="speech_dots[%d]" % i))
    return frames, 10, True
