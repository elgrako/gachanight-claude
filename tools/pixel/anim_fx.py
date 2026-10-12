"""Effects and small objects in the old-cartoon sepia look (art contract v3,
1.5 px per world pixel): four tones per material, hard speculars, ink outline.

coin_spin, coin_pickup, coin_flip, capsule_open (five colours), sparkle,
rarity_burst, zzz, dust_puff, speech_dots.
"""
import math

from pixlib import box, poly

from anim_lib import (Cv, oval, disc, rect, star_mask, rot_px, rnd, shift, shade_mask,
                      INK, INK_SOFT, PAPER, GOLD, MUSTARD, ROSE, GLASS, CAPSULE, WHITE)

LITE = GOLD[4]                      # warm glint, the second colour of every twinkle
PUFF = (PAPER[1], PAPER[2], PAPER[3], PAPER[4])


def k(v):
    """World pixels -> sprite pixels."""
    return rnd(v * 1.5)


# --- coin ---------------------------------------------------------------------------
def coin_px(x0, y0, w, h, size):
    """Gold coin inside a size x size box at (x0, y0), squeezed to w x h (spin /
    flip): reeded rim, sunken face with a raised numeral, like the peseta."""
    ax = x0 + (size - w) // 2
    ay = y0 + (size - h) // 2
    if min(w, h) <= 3:                                   # edge on: the reeded edge
        px = {}
        for (x, y) in rect(ax, ay, ax + w - 1, ay + h - 1):
            along, across = (y - ay, x - ax) if w <= 3 else (x - ax, y - ay)
            px[(x, y)] = GOLD[4] if across == 0 else (GOLD[3] if along % 2 == 0 else GOLD[1])
        return px
    m = oval(ax, ay, ax + w - 1, ay + h - 1)
    px = shade_mask(m, (GOLD[0], GOLD[1], GOLD[2], GOLD[4]), (2, 2))
    cx, cy = ax + w / 2.0, ay + h / 2.0
    if min(w, h) >= 6:
        inner = oval(ax + 2, ay + 2, ax + w - 3, ay + h - 3) if min(w, h) >= 8 else oval(ax + 1, ay + 1, ax + w - 2, ay + h - 2)
        for (x, y) in m - inner:                         # the rim, lit from the upper left, with reeding
            lit = (x + 0.5 - cx) / w + (y + 0.5 - cy) / h < 0
            ang = math.atan2((y + 0.5 - cy) / h, (x + 0.5 - cx) / w)
            notch = int(math.floor(ang / (math.pi / 10.0))) % 2 == 0
            px[(x, y)] = (GOLD[4] if notch else GOLD[3]) if lit else (GOLD[2] if notch else GOLD[1])
        for q in inner:
            px[q] = GOLD[2]
        for q in inner - shift(inner, 1, 1):             # the face is sunken: shadow under the lit rim
            px[q] = GOLD[1]
        for q in inner - shift(inner, -1, -1):
            px[q] = GOLD[3]
    ix, iy = x0 + size // 2, y0 + size // 2
    if w >= size - 3 and h >= size - 3:                  # the numeral, raised
        if size >= 14:
            one = rect(ix - 1, iy - 4, ix, iy + 2) | {(ix - 2, iy - 3)} | rect(ix - 2, iy + 3, ix + 1, iy + 3)
            sh = rect(ix + 1, iy - 3, ix + 1, iy + 2) | {(ix + 2, iy + 3)}
        else:
            one = rect(ix - 1, iy - 3, ix - 1, iy + 1) | rect(ix - 2, iy + 2, ix, iy + 2) | {(ix - 2, iy - 2)}
            sh = rect(ix, iy - 2, ix, iy + 1)
        for q in sh & m:
            px[q] = GOLD[0]
        for q in one & m:
            px[q] = GOLD[4]
        if size >= 14:
            for q in ((ix - 5, iy + 1), (ix - 4, iy + 3), (ix + 4, iy + 1), (ix + 3, iy + 3)):   # laurel dots
                px[q] = GOLD[0]
        px[(ax + 3, ay + 2)] = WHITE
        px[(ax + 2, ay + 3)] = WHITE
    elif min(w, h) >= 5:                                 # the numeral seen at an angle: a bar
        bar = rect(ix - 1, iy - 3, ix - 1, iy + 2) if w < h else rect(ix - 3, iy - 1, ix + 2, iy - 1)
        for q in bar & m:
            px[q] = GOLD[4]
    return px


def coin_spin():
    """Upright coin spinning on the floor, resting on the bottom row."""
    frames = []
    for i, w in enumerate((16, 13, 7, 3, 7, 13)):
        cv = Cv()
        cv.blob_px(coin_px(1, 1, w, 16, 16))
        frames.append(cv.image(18, 18, name="coin_spin[%d]" % i))
    return frames, 10, True


def twinkle(cv, cx, cy, r, rot=0.0, col=WHITE, inner=0.3):
    if r < 1.5:
        cv.blob({(rnd(cx), rnd(cy))}, col)
        return
    m = star_mask(cx + 0.5, cy + 0.5, r, max(1.0, r * inner), 4, rot)
    cv.blob(m, col)
    if r >= 5 and col == WHITE:
        cv.fill(m - shift(m, -1, -1), PAPER[3])


def coin_pickup():
    """The coin pops up spinning and turns into a twinkle."""
    frames = []
    seq = [(25, 16), (15, 7), (8, 16), (3, 3), (1, 16)]
    for i, (y0, w) in enumerate(seq):
        cv = Cv()
        cv.blob_px(coin_px(7, y0, w, 16, 16))
        if i == 1:                                       # dust kicked up where it left the floor
            cv.shaded(oval(4, 37, 8, 40), PUFF, (1, 1), False)
            cv.shaded(oval(20, 37, 24, 40), PUFF, (1, 1), False)
        if i == 2:
            cv.blob(rect(3, 35, 4, 36), PAPER[3])
            cv.blob(rect(25, 35, 26, 36), PAPER[3])
        frames.append(cv)
    for r, rot, extra in ((11.5, 0, False), (9, 45, True), (5.5, 0, True), (0, 0, True)):
        cv = Cv()
        if r:
            twinkle(cv, 14.5, 12, min(r, 11), rot, LITE if rot else WHITE)
        if extra:
            d = 9 if r > 6 else (12 if r else 13)
            for (ax, ay) in ((-1, -0.7), (1, -0.6), (-0.9, 0.9), (1, 0.8)):
                x, y = rnd(14.5 + ax * d), rnd(13 + ay * d * 0.7)
                if r:
                    cv.blob(rect(x, y, x + 1, y + 1) if r > 6 else {(x, y)}, WHITE)
                else:
                    cv.px[(x, y)] = INK
                    cv.px[(x + 1, y)] = INK_SOFT
        frames.append(cv)
    return [cv.image(30, 42, name="coin_pickup[%d]" % i) for i, cv in enumerate(frames)], 16, False


def coin_flip():
    """A coin tossed up, flipping, then dropping edge-on into a slot at the bottom."""
    seq = [  # (top y of the 12 px box, w, h)
        (27, 12, 12), (16, 12, 6), (9, 12, 3), (4, 12, 9), (1, 12, 12), (3, 12, 6),
        (7, 12, 3), (13, 9, 12), (21, 3, 12), (28, 3, 12), (34, 3, 12),
    ]
    slot = rect(4, 40, 13, 41)
    frames = []
    for i, (y0, w, h) in enumerate(seq):
        cv = Cv()
        cv.blob_px(coin_px(3, y0, w, h, 12))
        if i == 0:
            cv.dots([(2, 41), (3, 41), (14, 41), (15, 41)], INK)
        if y0 > 27:                                    # sinking into the slot
            cv.erase({q for q in list(cv.px) if q[1] > 39})
            cv.fill(slot, INK)
            cv.fill(rect(5, 41, 12, 41), INK_SOFT)
        frames.append(cv)
    cv = Cv()                                          # clink
    cv.fill(slot, INK)
    cv.fill(rect(5, 41, 12, 41), INK_SOFT)
    twinkle(cv, 8.5, 32, 5.5, 0, WHITE)
    cv.dots([(1, 36), (2, 36), (15, 36), (16, 36), (3, 27), (3, 28), (14, 27), (14, 28)], INK)
    frames.append(cv)
    return [cv.image(18, 42, name="coin_flip[%d]" % i) for i, cv in enumerate(frames)], 16, False


# --- capsule ------------------------------------------------------------------------
CAP_R = 13.5
CAP_C = (30, 34)


def capsule_fn(ramp, part="both", sx=1.0, sy=1.0, emblem=False):
    """Local shape of the toy capsule: coloured top, clear bottom with a tiny toy inside."""
    R = CAP_R

    def fn(u, v):
        u, v = u / sx, v / sy
        d2 = u * u + v * v
        if d2 > R * R:
            return None
        seam = -0.24 * math.sqrt(max(0.0, R * R - u * u))
        top = v > seam
        if part == "top" and not top:
            return None
        if part == "bottom" and top:
            # the open mouth of the cup: the back half of the rim ellipse
            if v < -seam and abs(u) < R - 0.9:
                return GLASS[0] if v < -seam - 1.5 else INK
            return None
        if part == "both" and abs(v - seam) < 0.6:
            return INK
        dd = (u + 3.6) ** 2 + (v - 3.6) ** 2            # distance from a centre pushed towards the light
        band = 0 if dd <= (R - 7.5) ** 2 else (1 if dd <= (R - 2.2) ** 2 else (2 if dd <= (R + 1.6) ** 2 else 3))
        if band == 3 and d2 > (R - 1.3) ** 2:
            band = 2                                     # rim light
        if top:
            if ((u + 5.6) / 3.4) ** 2 + ((v - 7.4) / 1.9) ** 2 <= 1.0:
                return WHITE
            if (u + 9.4) ** 2 + (v - 3.4) ** 2 <= 1.2:
                return WHITE
            if emblem and abs(u - 3.5) + abs(v - 4.5) <= 2.6:
                return WHITE
            if v < seam + 1.5:
                return ramp[1] if part == "top" else ramp[4 if band < 2 else 2]      # the lip of the lid
            return (ramp[3], ramp[2], ramp[1], ramp[0])[band]
        if part == "bottom" and v > seam - 1.5:
            return GLASS[4]
        # the tiny toy: a round bear head sitting in the cup
        if (u + 2.6) ** 2 + (v + 3.6) ** 2 <= 2.4 or (u - 3.6) ** 2 + (v + 3.6) ** 2 <= 2.4:
            return PAPER[2]
        if (u - 0.5) ** 2 + (v + 7.0) ** 2 <= 3.7 ** 2:
            if (abs(u + 1.0) < 0.6 or abs(u - 2.0) < 0.6) and abs(v + 6.4) < 0.7:
                return INK
            if abs(u - 0.5) < 1.1 and abs(v + 8.4) < 0.6:
                return ROSE[2]
            return PAPER[3] if (u + 0.4) ** 2 + (v + 6.2) ** 2 <= 9.5 else PAPER[1]
        if ((u + 8.6) / 1.2) ** 2 + ((v + 4.0) / 3.0) ** 2 <= 1.0:
            return GLASS[4]
        return (GLASS[3], GLASS[2], GLASS[1], GLASS[0])[band]

    return fn


def rays(cv, cx, cy, r0, r1, count, rot, col=WHITE, width=2.2):
    for n in range(count):
        a = math.radians(rot + 360.0 * n / count)
        ca, sa = math.cos(a), math.sin(a)
        nx, ny = -sa, ca
        pts = [(cx + ca * r0 + nx * width, cy + sa * r0 + ny * width),
               (cx + ca * r1, cy + sa * r1),
               (cx + ca * r0 - nx * width, cy + sa * r0 - ny * width)]
        m = set(poly(pts))
        if m:
            cv.blob(m, col)


CAPSULE_FLASH_FRAME = 7

# Confetti thrown out by the capsule: (angle deg, speed world px/frame, colour slot, shape).
CONFETTI = [(-100, 5.2, 0, 0), (-62, 5.8, 1, 1), (-28, 5.0, 2, 2), (-140, 5.6, 3, 1), (-170, 4.6, 1, 0),
            (-8, 4.4, 0, 1), (-80, 6.6, 4, 2), (-122, 6.4, 2, 0), (-45, 6.8, 3, 0), (-155, 6.0, 0, 2),
            (15, 3.8, 4, 0), (-195, 3.8, 2, 1)]
CONFETTI_SHAPES = (rect(0, 0, 2, 1), rect(0, 0, 1, 2), rect(0, 0, 2, 2))


def confetti(cv, cx, cy, age, palette, w=60, h=60):
    """Paper bits flying out from (cx, cy): fast at first, slowing, then falling and tumbling."""
    for n, (ang, speed, slot, shape) in enumerate(CONFETTI):
        if age > 3 + n % 3:                              # they wink out one after the other
            continue
        a = math.radians(ang)
        dist = 1.5 * speed * (1.0 - 0.72 ** age) / 0.28  # geometric slow-down
        x = cx + math.cos(a) * dist
        y = cy + math.sin(a) * dist + 0.68 * age * age   # gravity
        cells = CONFETTI_SHAPES[(shape + age) % 2 if shape < 2 else 2]
        m = {(rnd(x) + ax, rnd(y) + ay) for (ax, ay) in cells}
        if all(1 <= qx < w - 1 and 1 <= qy < h - 1 for (qx, qy) in m):
            col = palette[slot % len(palette)]
            cv.blob(m, col[2])
            cv.px[(rnd(x), rnd(y))] = col[4]


def capsule_open(colour):
    """14 frames: shakes harder and harder, squashes, cracks with light, bursts
    (frame 7), the two halves fly apart tumbling and pop, confetti rains down."""
    ramp = CAPSULE[colour]
    gold = colour == "gold"
    cx, cy = CAP_C
    frames = []
    palette = [ramp, MUSTARD, PAPER, ROSE, GOLD]
    lite = LITE if gold else WHITE
    glow = GOLD[4] if gold else PAPER[3]

    def whole(dx=0, dy=0, rot=0.0, sx=1.0, sy=1.0):
        cv = Cv()
        cv.blob_px(rot_px(capsule_fn(ramp, "both", sx, sy, gold), cx + dx, cy + dy, rot, 21))
        return cv

    def half(cv, part, dx, dy, rot, sx, sy=None):
        sy = sx if sy is None else sy
        cv.blob_px(rot_px(capsule_fn(ramp, part, sx, sy, gold and part == "top"), cx + dx, cy + dy, rot, 21))

    # 0 rest, 1-4 shaking harder and harder with little hops
    frames.append(whole())
    for (dx, dy, rot, sx, sy) in ((-3, 0, -10, 1.0, 1.0), (3, -2, 12, 0.97, 1.04), (-4, 0, -20, 1.04, 0.96),
                                  (4, -3, 22, 0.95, 1.06)):
        cv = whole(dx, dy, rot, sx, sy)
        if abs(dx) == 4:                                 # speed lines
            s_ = 1 if dx > 0 else -1
            for (ax, ay, n) in ((-20, -9, 2), (-21, -4, 3), (-20, 2, 2)):
                cv.fill({(cx + s_ * ax - s_ * j, cy + ay) for j in range(n)}, INK)
            for (ax, ay) in ((21, -12), (22, -7)):
                cv.fill({(cx + s_ * ax + s_ * j, cy + ay) for j in range(2)}, INK)
        frames.append(cv)
    # 5 squash down (anticipation)
    cv = whole(0, 4, 0, 1.18, 0.8)
    cv.fill(rect(cx - 21, cy + 12, cx - 19, cy + 12) | rect(cx + 18, cy + 12, cx + 20, cy + 12), INK)
    frames.append(cv)
    # 6 stretch up, the seam cracks with light
    cv = Cv()
    half(cv, "bottom", 0, 2, 0, 0.96, 1.06)
    rays(cv, cx, cy - 2, 14, 22, 2, 0, WHITE, 3.0)
    rays(cv, cx, cy - 2, 14, 19, 4, 45, lite, 2.0)
    cv.blob(oval(cx - 13, cy - 5, cx + 12, cy + 1), WHITE)
    half(cv, "top", 0, -8, 0, 0.96, 1.06)
    frames.append(cv)
    # 7 the big flash
    cv = Cv()
    half(cv, "top", -6, -15, -18, 0.92)
    half(cv, "bottom", 4, 7, 12, 1.0)
    rays(cv, cx, cy - 3, 15, 28, 8, 22.5, glow, 4.8)
    star = star_mask(cx, cy - 3, 25, 12, 8, 0)
    cv.blob(star, WHITE)
    cv.fill(star - shift(star, -2, -2), PAPER[3])
    cv.fill(disc(cx, cy - 3, 7.5), glow)
    cv.fill(disc(cx - 1, cy - 4, 4), WHITE)
    frames.append(cv)
    # 8-10 the halves tumble apart on arcs, rays thin out, confetti flies
    cv = Cv()
    rays(cv, cx, cy - 3, 16, 27, 8, 0, WHITE, 2.4)
    cv.blob(star_mask(cx, cy - 3, 13, 6, 4, 0), WHITE)
    half(cv, "top", -12, -18, -48, 0.82)
    half(cv, "bottom", 10, 6, 38, 0.86)
    confetti(cv, cx, cy - 3, 1, palette)
    frames.append(cv)
    cv = Cv()
    twinkle(cv, cx, cy - 4, 7.5, 45, WHITE)
    half(cv, "top", -16, -16, -95, 0.64)
    half(cv, "bottom", 15, 9, 80, 0.68)
    twinkle(cv, 48, 10, 4.5, 0, lite)
    confetti(cv, cx, cy - 3, 2, palette)
    frames.append(cv)
    cv = Cv()
    half(cv, "top", -19, -10, -150, 0.46)
    half(cv, "bottom", 18, 15, 130, 0.5)
    twinkle(cv, cx, cy - 6, 4.5, 0, WHITE)
    twinkle(cv, 10, 40, 3, 45, lite)
    confetti(cv, cx, cy - 3, 3, palette)
    frames.append(cv)
    # 11 the halves pop into twinkles
    cv = Cv()
    twinkle(cv, cx - 19, cy - 4, 6, 0, WHITE)
    twinkle(cv, cx + 18, cy + 18, 6, 45, WHITE)
    twinkle(cv, 49, 9, 3, 45, lite)
    confetti(cv, cx, cy - 3, 4, palette)
    frames.append(cv)
    # 12-13 the last confetti and glitter
    cv = Cv()
    for (x, y, r, rot) in ((cx - 19, cy - 4, 3, 45), (cx + 18, cy + 18, 3, 0), (30, 8, 3, 0)):
        twinkle(cv, x, y, r, rot, lite)
    confetti(cv, cx, cy - 3, 5, palette)
    frames.append(cv)
    cv = Cv()
    for (x, y) in ((10, 13), (51, 9), (7, 45), (49, 49), (30, 6)):
        twinkle(cv, x, y, 1.6, 0, lite)
    frames.append(cv)
    if gold:                                           # extra glitter while it shakes
        for i, pts in ((1, ((7, 12, 3),)), (2, ((51, 15, 3),)), (3, ((9, 45, 3), (49, 9, 4.5))), (4, ((7, 13, 4.5), (51, 45, 3))),
                       (5, ((6, 21, 3), (52, 21, 3)))):
            for (x, y, r) in pts:
                twinkle(frames[i], x, y, r, 0, LITE)
    name = "capsule_open" if colour == "red" else "capsule_open_" + colour
    return [cv.image(60, 60, name="%s[%d]" % (name, i)) for i, cv in enumerate(frames)], 14, False


# --- sparkle / burst ----------------------------------------------------------------
def sparkle():
    frames = []
    for i, (r, rot, dots) in enumerate(((3, 0, 0), (7.5, 0, 0), (10.5, 0, 7), (7.5, 45, 9), (4.5, 0, 10), (0, 0, 10))):
        cv = Cv()
        if r:
            twinkle(cv, 11.5, 11.5, r, rot, WHITE if i != 3 else LITE)
        if dots:
            for (ax, ay) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                q = (rnd(11.5 + ax * dots * 0.8), rnd(11.5 + ay * dots * 0.8))
                if r and 1 <= q[0] <= 21 and 1 <= q[1] <= 21:
                    cv.blob({q, (q[0] + 1, q[1])} if i == 2 else {q}, WHITE)
                elif not r:
                    cv.px[q] = WHITE
                    cv.px[(q[0], q[1] + 1)] = INK
        frames.append(cv.image(24, 24, name="sparkle[%d]" % i))
    return frames, 14, False


BURST = 96


def burst_confetti(cv, c, age):
    """Pale paper bits (the game tints them): thrown out past the ring,
    slowing down, then tumbling to the ground one after the other."""
    for n in range(16):
        ang = math.radians(n * 137.5 + 20)               # golden angle: an even, irregular scatter
        speed = 1.5 * (5.0 + (n * 5 % 7) * 0.8)
        if age > 5 + n % 4:
            continue
        dist = 18.0 + speed * (1.0 - 0.7 ** age) / 0.3
        x = rnd(c + math.cos(ang) * dist + (2.2 * math.sin(age * 1.7 + n) if age > 3 else 0.0))
        y = rnd(c + math.sin(ang) * dist * 0.9 + 0.33 * age * age)
        kind = n % 3
        flip = (age + n) % 2
        if kind == 0:                                    # a tumbling strip
            m = rect(x, y, x + 3, y + 1) if flip else rect(x, y, x + 1, y + 3)
        elif kind == 1:                                  # a square seen flat, then edge on
            m = rect(x, y, x + 2, y + 2) if flip else rect(x, y, x + 3, y)
        else:                                            # a little diamond
            m = (rect(x - 1, y, x + 1, y) | rect(x, y - 1, x, y + 1) | {(x + 2, y), (x, y + 2), (x + 1, y + 1), (x + 1, y - 1)}
                 if flip else rect(x, y, x + 1, y + 2))
        if all(1 <= qx < BURST - 1 and 1 <= qy < BURST - 1 for (qx, qy) in m):
            cv.blob(m, WHITE)
            if len(m) >= 8:
                cv.px[(x + 1, y + 1)] = PAPER[3]


def rarity_burst():
    """Pale cartoon burst the game tints: pop, starburst, ring of rays, stars, a shower of confetti."""
    c = BURST // 2
    frames = []
    spec = [
        dict(star=(12, 6, 8, 0)),
        dict(star=(27, 13.5, 8, 0), rays=(18, 36, 8, 22.5, 4.5)),
        dict(star=(37.5, 19.5, 10, 18), rays=(27, 45, 10, 0, 5.0)),
        dict(star=(30, 21, 10, 0), rays=(33, 46.5, 10, 18, 4.5), hole=10.5),
        dict(ring=(28.5, 7.5), rays=(36, 46.5, 10, 0, 3.6), stars=(40.5, 6, 0)),
        dict(ring=(34.5, 4.5), rays=(40.5, 46.5, 10, 18, 2.4), stars=(42, 5.2, 45), conf=1),
        dict(ring=(39, 3, 8), stars=(43.5, 4.5, 0), conf=2),
        dict(stars=(45, 3, 45), conf=3),
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
            cv.fill(m - shift(m, -2, -2), PAPER[3])       # one shade so the tinted burst keeps its volume
            cv.fill(m - shift(m, -1, -1), PAPER[2])
        if "ring" in s:
            r, th = s["ring"][0], s["ring"][1]
            m = set()
            for y in range(BURST):
                for x in range(BURST):
                    d = math.hypot(x + 0.5 - c, y + 0.5 - c)
                    if abs(d - r) <= th / 2.0:
                        if len(s["ring"]) > 2:
                            a = (math.degrees(math.atan2(y + 0.5 - c, x + 0.5 - c)) + 360) % (360.0 / s["ring"][2])
                            if a > 360.0 / s["ring"][2] * 0.55:
                                continue
                        m.add((x, y))
            cv.blob(m, WHITE)
            if th >= 4:
                cv.fill(m - shift(m, -1, -1), PAPER[3])
        if "stars" in s:
            d, r, rot = s["stars"]
            for n in range(6):
                a = math.radians(60 * n + 30)
                twinkle(cv, c + math.cos(a) * d * 0.95, c + math.sin(a) * d * 0.95, r, rot, WHITE)
        cv.px = {q: col for q, col in cv.px.items() if 0 <= q[0] < BURST and 0 <= q[1] < BURST}
        frames.append(cv.image(BURST, BURST, name="rarity_burst[%d]" % i))
    return frames, 16, False


# --- zzz ----------------------------------------------------------------------------
def letter_z(cv, x, y, size):
    """Hand-lettered Z of the given size with its top-left at (x, y), outlined."""
    th = 2 if size >= 6 else 1
    m = set()
    for i in range(size):
        for t in range(th):
            m.add((x + i, y + t))
            m.add((x + i, y + size - 1 - t))
            m.add((x + size - 1 - i, min(y + size - 1, y + i + t)))
    cv.blob(m, WHITE)
    if th == 2:
        cv.fill(m - shift(m, -1, -1), PAPER[2])


def zzz():
    """Two Zs drifting up and to the right, growing as they rise; loops."""
    frames = []
    n = 8
    for i in range(n):
        cv = Cv()
        for j in range(2):
            ph = ((i + j * n / 2.0) % n) / n          # 0 just born .. 1 gone
            size = 4 if ph < 0.25 else (6 if ph < 0.6 else 8)
            x = rnd(1 + ph * 13)
            y = rnd(18 - ph * 18)
            letter_z(cv, x, y, size)
        cv.px = {q: c for q, c in cv.px.items() if 0 <= q[0] < 24 and 0 <= q[1] < 24}
        frames.append(cv.image(24, 24, name="zzz[%d]" % i))
    return frames, 6, True


# --- dust ---------------------------------------------------------------------------
def dust_puff():
    """A little cloud kicked up at the feet: pops, billows, splits into three
    round puffs that drift up and out, shrinking to specks."""
    frames = []
    spec = [    # boxes in world pixels
        [(6, 7, 10, 10)],
        [(3, 6, 8, 10), (8, 5, 13, 10), (6, 3, 10, 7)],
        [(1, 5, 6, 10), (9, 4, 14, 9), (5, 2, 10, 7), (5, 7, 10, 10)],
        [(1, 4, 5, 8), (10, 3, 14, 7), (6, 1, 9, 4), (7, 8, 8, 9)],
        [(1, 3, 3, 5), (12, 2, 14, 4), (7, 1, 8, 2)],
        [(1, 2, 1, 2), (14, 1, 14, 1), (7, 1, 7, 1)],
    ]
    for i, puffs in enumerate(spec):
        cv = Cv()
        boxes = [(k(x0), k(y0), k(x1 + 1) - 1, min(16, k(y1 + 1) - 1)) for (x0, y0, x1, y1) in puffs]
        if i < 3:                                      # one billowing cloud
            m = set()
            for (x0, y0, x1, y1) in boxes:
                m |= oval(x0, y0, x1, y1)
            cv.shaded(m, PUFF, (2, 2), False)
            for (x0, y0, x1, y1) in boxes[1:]:         # the curl of each billow
                cv.fill(oval(x0, y0, x1, y1) - shift(oval(x0, y0, x1, y1), -1, -1), PAPER[2], m)
        else:                                          # separate puffs
            for (x0, y0, x1, y1) in boxes:
                d = oval(x0, y0, x1, y1) if x1 - x0 >= 2 else rect(x0, y0, x1, y1)
                if x1 - x0 >= 4:
                    cv.shaded(d, PUFF, (1, 1), False)
                else:
                    cv.blob(d, PAPER[3])
        frames.append(cv.image(24, 18, name="dust_puff[%d]" % i))
    return frames, 14, False


# --- speech dots --------------------------------------------------------------------
def speech_dots():
    """Three dots bouncing one after the other inside a speech bubble; loops."""
    frames = []
    hop = [0, -3, -4, -3, 0, 0, 0, 0]
    for i in range(8):
        cv = Cv()
        bubble = box(1, 1, 28, 14, 4)
        tail = {(6, 15), (7, 15), (8, 15), (9, 15), (6, 16), (7, 16), (8, 16), (5, 17), (6, 17), (5, 18)}
        m = bubble | tail
        cv.blob(m, PAPER[4])
        cv.fill(m - shift(m, -1, -2), PAPER[3])
        cv.fill(m - shift(m, -1, -1), PAPER[2])
        for j in range(3):
            dy = hop[(i - j * 2) % 8]
            x = 7 + j * 6
            dot = rect(x, 8 + dy, x + 2, 10 + dy) | rect(x + 1, 7 + dy, x + 1, 11 + dy) | rect(x - 1, 9 + dy, x + 3, 9 + dy)
            cv.fill(dot & bubble, INK)
            cv.fill({(x, 8 + dy)} & bubble, INK_SOFT)
        frames.append(cv.image(30, 21, name="speech_dots[%d]" % i))
    return frames, 10, True
