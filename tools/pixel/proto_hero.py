"""Prototypes for the owner to judge: an adult protagonist and Capsule Machine
No. 1 as an old, slightly dark and mysterious drawing: 1930s rubber-hose
cartooning in sepia ink, the way a worn print of it would look in pixel art.

Nothing here is used by the game. It writes a labelled contact sheet to
tools/pixel/previews/proto_views.png (not shipped). Run from the repository
root:

    python tools/pixel/proto_hero.py

The mood: a tired man in a hat and a long coat, eyes half shut under the
brim, flipping the one coin he has; a machine that is a little too pleased to
see him. Sepia throughout, one muted oxblood accent, shadows hatched like an
engraving, and an aged, vignetted paper behind them.

What that look asks for, and how the pictures get it:
- a pose with a line of action and an attitude, never a symmetric doll: the
  kid shows off a coin with a hand on his hip, the machine tips its cap;
- shapes drawn as curves, not boxes: every part is rasterised four times
  larger and reduced, so tilted ovals, tapering fingers and noodle limbs
  come out as clean pixel curves;
- cel colouring like an animation cel: flat colour, one shadow shape away
  from the light (top left) and white shine marks on whatever is glossy;
- ink: a contour on every part, heavier on the shadow side of the whole
  figure, as a brush line would be;
- the vocabulary: pie-cut eyes, brows, a toothy grin, a black button nose,
  four-finger gloves with a cuff, big two-tone shoes, limbs without joints.
"""
import math
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "previews", "proto_views.png")
SS = 4          # shapes are drawn this many times larger, then reduced


def ramp(*codes):
    out = []
    for code in codes:
        code = code.lstrip("#")
        out.append((int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16), 255))
    return out


# Each ramp: shadow, base, light. Sepia throughout; oxblood is the one accent.
INK = ramp("#140c0a")[0]
INK_SOFT = ramp("#3a2419")[0]
WHITE = ramp("#f3e6c4")[0]
SKIN = ramp("#9a7350", "#d8b98a", "#efdcb0")
HAT = ramp("#17110f", "#2e2420", "#5a4a3e")
COAT = ramp("#3f2e22", "#6e543a", "#9a7c56")
LAPEL = ramp("#2c1f18", "#4a372a", "#6e543a")
RED = ramp("#4a1512", "#7e231c", "#b0412c")
GLOVE = ramp("#a8946c", "#eadfbd", "#f7efd6")
SHOE = ramp("#1c1411", "#3a2a22", "#6a5444")
TOE = ramp("#a8946c", "#ddd0aa", "#f3e6c4")
BRASS = ramp("#5c4216", "#a47a2a", "#d8b45c")
GOLD = ramp("#7a5612", "#c9982e", "#f1d680")
GREY = ramp("#2a2623", "#56504a", "#8c8478")
GLASS = ramp("#2f3a36", "#4f5f58", "#7f9186")
TEAL = ramp("#1e3a40", "#3a6468", "#6f9a96")
GREEN = ramp("#2c3e22", "#52683a", "#869a66")
MUSTARD = ramp("#6e5014", "#b08a2e", "#d8bc6a")
CREAM = ramp("#8f7d5c", "#d9c9a2", "#f3e6c4")
BLACK = ramp("#0f0908", "#1c1110", "#3f2c28")
ROSE = ramp("#b9806a")[0]
MOUTH = ramp("#2a0c0e")[0]
TONGUE = ramp("#8e3a2c")[0]
CLEAR = (0, 0, 0, 0)
FLOOR_SHADOW = (20, 12, 10, 120)


def toward_ink(color, share=0.45):
    return tuple(int(round(color[i] + (INK[i] - color[i]) * share)) for i in range(3)) + (255,)


class Sprite:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.px = {}
        self.tone = {}     # pixel -> (ramp, index), for cast shadows

    # --- shapes: each returns a set of (x, y) --------------------------------

    def _mask(self, paint):
        big = Image.new("L", (self.w * SS, self.h * SS), 0)
        paint(ImageDraw.Draw(big))
        small = big.resize((self.w, self.h), Image.BOX)
        data = small.load()
        return {(x, y) for y in range(self.h) for x in range(self.w) if data[x, y] >= 128}

    def oval(self, cx, cy, rx, ry, turn=0.0):
        """An ellipse turned by `turn` degrees (positive leans to the right)."""
        angle = math.radians(turn)
        points = []
        for step in range(48):
            t = math.tau * step / 48.0
            x, y = math.cos(t) * rx, math.sin(t) * ry
            points.append(((cx + x * math.cos(angle) - y * math.sin(angle) + 0.5) * SS,
                           (cy + x * math.sin(angle) + y * math.cos(angle) + 0.5) * SS))
        return self._mask(lambda d: d.polygon(points, fill=255))

    def poly(self, points):
        scaled = [((x + 0.5) * SS, (y + 0.5) * SS) for x, y in points]
        return self._mask(lambda d: d.polygon(scaled, fill=255))

    def hose(self, points, width=3.4, end_width=None):
        """A noodle: a smooth curve through 2-4 control points, optionally
        tapering to `end_width` (fingers, a cowlick)."""
        end = width if end_width is None else end_width

        def at(t):
            pts = list(points)
            while len(pts) > 1:
                pts = [(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t) for i in range(len(pts) - 1)]
            return pts[0]

        if width < 1.6:
            return {(int(round(at(step / 160.0)[0])), int(round(at(step / 160.0)[1]))) for step in range(161)}

        def paint(d):
            for step in range(81):
                t = step / 80.0
                x, y = at(t)
                r = (width + (end - width) * t) / 2.0
                d.ellipse([(x - r + 0.5) * SS, (y - r + 0.5) * SS, (x + r + 0.5) * SS, (y + r + 0.5) * SS], fill=255)
        return self._mask(paint)

    @staticmethod
    def rows(mask, y0, y1):
        return {(x, y) for x, y in mask if y0 <= y <= y1}

    @staticmethod
    def cols(mask, x0, x1):
        return {(x, y) for x, y in mask if x0 <= x <= x1}

    # --- painting -----------------------------------------------------------

    def _put(self, point, color, tone=None):
        self.px[point] = color
        if tone is None:
            self.tone.pop(point, None)
        else:
            self.tone[point] = tone

    def part(self, mask, colors, shade=0.26, mode="ball", gloss=False, outline=INK, clip=None, form=None):
        """A cel-coloured solid: flat colour with one shadow shape on the side
        away from the light. `mode` "ball" puts the shadow at the lower right,
        "tube" at the right (upright cylinders), "flat" leaves none. `gloss`
        adds a band of light. `form` is the whole solid when `mask` is only a
        region of it."""
        if clip is not None:
            mask = mask & clip
        solid = form if form is not None else mask
        if outline is not None:
            for x, y in mask:
                for near in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if near not in solid and (clip is None or near in clip):
                        self._put(near, outline)
        step = (-1, -1) if mode == "ball" else (-1, 0)
        for point in mask:
            index = 1
            if mode != "flat":
                lit = self._run(point, step, solid)
                dark = self._run(point, (-step[0], -step[1]), solid)
                total = lit + dark
                if total >= 3:
                    t = dark / float(total)
                    if t < shade:
                        index = 0
                    elif gloss and total >= 7 and 0.70 < t < 0.88:
                        index = 2
            color = colors[index]
            if index == 0 and (point[0] + point[1]) % 3 == 0:
                color = toward_ink(color)        # hatched like an engraving
            self._put(point, color, (colors, index))

    @staticmethod
    def _run(point, step, solid):
        x, y = point
        count = 0
        while count < 90 and (x + step[0], y + step[1]) in solid:
            x += step[0]
            y += step[1]
            count += 1
        return count

    def dots(self, points, color):
        for point in points:
            self._put(tuple(point), color)

    def shadow(self, mask):
        """A cast shadow: whatever is drawn there drops to its shadow colour."""
        for point in mask:
            if point in self.tone:
                colors, _index = self.tone[point]
                self.px[point] = colors[0]
                self.tone[point] = (colors, 0)

    def finish(self, ground_y, ground_rx, cx):
        """Brush weight on the shadow side of the whole figure, then the
        figure's shadow on the floor."""
        heavy = [(x + dx, y + dy) for (x, y) in self.px for dx, dy in ((1, 0), (0, 1)) if (x + dx, y + dy) not in self.px]
        self.dots(heavy, INK)
        for point in self.oval(cx, ground_y, ground_rx, 2.6):
            if point not in self.px:
                self.px[point] = FLOOR_SHADOW

    def flipped(self):
        other = Sprite(self.w, self.h)
        other.px = {(self.w - 1 - x, y): c for (x, y), c in self.px.items()}
        return other

    def image(self):
        img = Image.new("RGBA", (self.w, self.h), CLEAR)
        for (x, y), color in self.px.items():
            if 0 <= x < self.w and 0 <= y < self.h:
                img.putpixel((x, y), color)
        return img


# --- shared rubber-hose parts ----------------------------------------------------

def pie_eye(s, cx, cy, rx, ry, turn=0.0, look=(1.0, 1.4), clip=None, lid=0.0, lid_colors=None):
    """A tall eye; the pupil is a black oval low in it with a pie slice cut
    out of its upper right. `lid` is the share of the eye a heavy lid covers."""
    white = s.oval(cx, cy, rx, ry, turn)
    s.part(white, CREAM, mode="flat", clip=clip)
    s.dots(white if clip is None else white & clip, WHITE)
    px, py = cx + look[0], cy + look[1]
    pupil = s.oval(px, py, rx * 0.62, ry * 0.66, turn) & white
    pupil -= s.poly([(px, py - 0.4), (px + rx * 1.2, py - ry * 1.1), (px + rx * 1.3, py - ry * 0.1)])
    if clip is not None:
        pupil &= clip
    s.dots(pupil, INK)
    if lid > 0.0:
        edge = int(round(cy - ry + 2.0 * ry * lid))
        closed = {(x, y) for x, y in white if y < edge}
        line = {(x, y) for x, y in white if y == edge}
        if clip is not None:
            closed &= clip
            line &= clip
        s.dots(closed, (lid_colors or SKIN)[1 if lid_colors is None else 0])
        s.dots(line, INK)


def sleepy_eye(s, cx, cy, rx):
    """A shut eye: a lash line sagging like a smile, with two lashes."""
    s.dots(s.hose([(cx - rx, cy - 1.5), (cx, cy + 3.5), (cx + rx, cy - 1.5)], 2.4), INK)
    s.dots(s.hose([(cx - rx, cy - 1.5), (cx - rx - 1.5, cy + 0.5)], 1.1) | s.hose([(cx + rx, cy - 1.5), (cx + rx + 1.5, cy + 0.5)], 1.1), INK)


def grin(s, cx, cy, width, turn=0.0, clip=None, teeth=False):
    """An open, toothy grin: a crescent with teeth above and the tongue below."""
    mouth = s.oval(cx, cy, width, width * 0.66, turn) - s.oval(cx, cy - width * 0.42, width * 1.15, width * 0.52, turn)
    if clip is not None:
        mouth &= clip
    s.part(mouth, [MOUTH, MOUTH, MOUTH], mode="flat")
    top = {(x, y) for x, y in mouth if (x, y - 1) not in mouth or (x, y - 2) not in mouth}
    s.dots(top, WHITE)
    if teeth:
        s.dots([(x, y) for x, y in top if x % 3 == 0], INK_SOFT)               # every tooth drawn
    s.dots(s.oval(cx, cy + width * 0.48, width * 0.42, width * 0.22, turn) & (mouth - top), TONGUE)


def fist(s, cx, cy, thumb=(-1, -1), radius=4.6):
    """A closed glove: a round fist, a thumb and the knuckle lines."""
    s.part(s.oval(cx, cy, radius, radius * 0.92), GLOVE, shade=0.3)
    s.part(s.oval(cx + thumb[0] * radius * 0.75, cy + thumb[1] * radius * 0.6, radius * 0.42, radius * 0.5), GLOVE, shade=0.3)
    for offset in (-1.5, 0.3, 2.1):
        s.dots([(int(round(cx + offset)), int(round(cy + 1)) + step) for step in (0, 1)], INK_SOFT)


def cuff(s, cx, cy, rx=3.6, ry=2.0, turn=0.0):
    s.part(s.oval(cx, cy, rx, ry, turn), GLOVE, shade=0.4)


def shoe(s, cx, cy, facing=1, long=8.0, turn=0.0):
    """A big two-tone shoe: brown upper, pale toe cap, a sole and a shine."""
    upper = s.rows(s.oval(cx, cy, long, 4.4, turn) | s.oval(cx + facing * long * 0.45, cy - 0.6, long * 0.56, 4.4, turn), 0, int(cy + 3))
    s.part(upper, SHOE, shade=0.3)
    toe = {(x, y) for x, y in upper if (x - cx) * facing > long * 0.2}
    s.part(toe, TOE, shade=0.3, outline=None, form=upper)
    s.dots([(x, y) for x, y in upper if (x, y) not in toe and (x + facing, y) in toe], INK_SOFT)
    s.dots(s.rows(upper, int(cy + 3), int(cy + 3)), BLACK[1])                              # sole
    s.dots(s.hose([(cx + facing * long * 0.55, cy - 2.6), (cx + facing * long * 0.85, cy - 2.2), (cx + facing * long * 1.0, cy - 0.8)], 1.0) & toe, WHITE)
    s.dots([(int(cx - facing * 1), int(cy - 3)), (int(cx - facing * 3), int(cy - 3))], CREAM[1])   # laces


def capsule(s, cx, cy, radius, colors, tilt, clip):
    """A two-tone capsule: coloured top, cream bottom, split on a tilted seam."""
    ball = s.oval(cx, cy, radius, radius)
    s.part(ball, CREAM, shade=0.3, clip=clip)
    dx, dy = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    top = {(x, y) for x, y in ball if dx * (y - cy) - dy * (x - cx) < 0}
    s.part(top, colors, shade=0.3, outline=None, clip=clip, form=ball)
    s.dots([p for p in s.hose([(cx - dx * radius, cy - dy * radius), (cx + dx * radius, cy + dy * radius)], 1.0) if p in ball and p in clip], INK_SOFT)
    s.dots(s.oval(cx - radius * 0.4, cy - radius * 0.45, radius * 0.24, radius * 0.16, -40) & clip & ball, WHITE)


# --- the protagonist: a tired man in a hat and a long coat, 64 x 104 --------------------

CW, CH = 64, 104


def _hat(s, cx, cy, turn, forward=0.0):
    crown = s.rows(s.oval(cx - 0.5, cy - 17.0, 11.5, 9.5, turn), 0, int(cy - 12))
    s.part(crown, HAT, shade=0.3)
    s.part(s.rows(crown, int(cy - 15), int(cy - 13)), RED, mode="flat", outline=None, form=crown)   # band
    s.dots(s.hose([(cx - 3, cy - 25.5), (cx - 1.5, cy - 20)], 1.0), HAT[0])                         # pinch
    s.dots(s.hose([(cx - 8, cy - 19), (cx - 6, cy - 24), (cx - 2, cy - 25.5)], 1.0), HAT[2])
    s.part(s.oval(cx + forward, cy - 11.0, 17.5, 4.0, turn), HAT, shade=0.35)
    s.dots(s.hose([(cx + forward - 13, cy - 11), (cx + forward - 6, cy - 13.2), (cx + forward + 2, cy - 13.6)], 1.0), HAT[2])


def _stubble(s, skull, cx, cy, skip):
    s.dots([(x, y) for x, y in s.rows(skull, int(cy + 9), int(cy + 20))
            if (x * 2 + y) % 4 == 0 and (x, y) not in skip and (x + 1, y) in skull and (x - 1, y) in skull], SKIN[0])


def _man_head(s, cx, cy, side=False):
    """A long face with a heavy jaw, half-shut eyes in the hat's shadow."""
    turn = -4.0
    skull = s.oval(cx, cy, 11.5, 12.0, turn) | s.oval(cx + 0.5, cy + 7.0, 9.2, 7.2, turn)
    if side:
        s.part(skull, SKIN, shade=0.24)
        s.part(s.cols(s.rows(skull, int(cy - 8), int(cy + 9)), 0, int(cx - 6)), HAT, shade=0.3, outline=None, form=skull)   # hair at the back
        s.shadow(s.rows(skull, 0, int(cy - 6)))
        s.part(s.oval(cx - 4.5, cy + 2.0, 2.4, 3.4), SKIN, shade=0.35)                       # ear
        s.part(s.oval(cx + 12.0, cy + 3.5, 3.2, 2.6, -10), SKIN, shade=0.35)                 # nose
        pie_eye(s, cx + 5.5, cy - 0.5, 3.8, 5.0, turn, look=(1.2, 1.2), lid=0.36)
        s.dots(s.hose([(cx + 1, cy - 6), (cx + 6, cy - 7.5), (cx + 10, cy - 5)], 2.2), INK)
        mouth = s.hose([(cx + 3, cy + 10.5), (cx + 7, cy + 11.5), (cx + 10, cy + 9.5)], 1.4)
        _stubble(s, skull, cx, cy, mouth)
        s.dots(mouth, INK)
        s.dots(s.hose([(cx + 9, cy + 10), (cx + 17, cy + 8)], 1.0), CREAM[1])               # matchstick
        s.dots([(int(cx + 18), int(cy + 8))], RED[2])
        _hat(s, cx, cy, turn, 2.0)
        return
    s.part(s.oval(cx - 11.5, cy + 2.5, 2.2, 3.2), SKIN, shade=0.35)                          # ears
    s.part(s.oval(cx + 11.5, cy + 1.5, 2.2, 3.2), SKIN, shade=0.35)
    s.part(skull, SKIN, shade=0.24)
    s.part(s.oval(cx - 10.3, cy - 2.5, 1.8, 4.6), HAT, mode="flat")                          # sideburns
    s.part(s.oval(cx + 10.3, cy - 3.5, 1.8, 4.6), HAT, mode="flat")
    s.shadow(s.rows(skull, 0, int(cy - 6)))                                                  # the brim's shadow
    pie_eye(s, cx - 4.8, cy - 0.2, 3.8, 5.0, turn, look=(1.0, 1.2), lid=0.36)
    pie_eye(s, cx + 5.2, cy - 0.8, 3.8, 5.0, turn, look=(1.0, 1.2), lid=0.36)
    s.dots(s.hose([(cx - 9.5, cy - 6.5), (cx - 5, cy - 7.0), (cx - 1, cy - 5.5)], 1.8), INK)         # heavy brows
    s.dots(s.hose([(cx + 1.5, cy - 6.5), (cx + 6, cy - 8.5), (cx + 10, cy - 7.0)], 1.8), INK)        # one cocked
    s.part(s.oval(cx + 0.4, cy + 6.0, 2.2, 3.0, -12), SKIN, shade=0.4)                       # a long nose
    mouth = s.hose([(cx - 4, cy + 11), (cx, cy + 12.5), (cx + 6, cy + 10)], 1.4)
    _stubble(s, skull, cx, cy, mouth)
    s.dots(mouth, INK)
    s.dots([(int(cx + 7), int(cy + 9))], INK)
    s.dots(s.hose([(cx + 5, cy + 10.5), (cx + 13, cy + 8)], 1.0), CREAM[1])                  # matchstick
    s.dots([(int(cx + 14), int(cy + 8))], RED[2])
    _hat(s, cx, cy, turn)


def kid_front():
    """Standing with a slouch: one hand in the coat pocket, the other flips a coin."""
    s = Sprite(CW, CH)
    s.part(s.hose([(28, 80), (26, 89), (25, 96)], 4.2), BLACK, mode="flat", outline=None)
    s.part(s.hose([(36, 80), (39, 89), (40, 96)], 4.2), BLACK, mode="flat", outline=None)
    shoe(s, 22.5, 98.0, -1, 7.0)
    shoe(s, 42.5, 98.0, 1, 7.0)
    coat = s.poly([(22, 44), (42, 44), (46, 60), (48, 83), (34, 83), (32, 75), (30, 83), (16, 83), (18, 60)])
    s.part(coat, COAT, shade=0.2, mode="tube")
    s.part(s.poly([(28, 44), (36, 44), (32, 55)]), CREAM, mode="flat")                       # shirt
    s.part(s.poly([(31, 45), (33, 45), (34, 52), (32, 56), (30, 52)]), RED, shade=0.4)       # tie, loose
    s.part(s.poly([(24, 44), (29, 44), (32, 57), (27, 54)]), LAPEL, shade=0.3)
    s.part(s.poly([(40, 44), (35, 44), (32, 57), (37, 54)]), LAPEL, shade=0.3)
    s.part(s.poly([(22, 45), (26, 37), (30, 45)]), COAT, shade=0.3)                          # collar turned up
    s.part(s.poly([(42, 45), (38, 37), (34, 45)]), COAT, shade=0.3)
    s.part(s.rows(coat, 63, 65), LAPEL, mode="flat", outline=None, form=coat)                # belt
    s.dots([(x, 62) for x in range(18, 47) if (x, 62) in coat] + [(x, 66) for x in range(17, 48) if (x, 66) in coat], INK_SOFT)
    s.part(s.poly([(30, 62), (34, 62), (34, 66), (30, 66)]), BRASS, mode="flat")
    s.dots([(32, 64)], INK)
    for by in (59, 70, 76):
        s.dots([(28, by), (36, by)], BRASS[1])
    s.dots(s.hose([(32, 67), (32, 75)], 1.0), COAT[0])
    s.part(s.hose([(42, 48), (49.5, 57), (45, 68)], 5.6), COAT, shade=0.35)                  # far arm, hand pocketed
    s.dots(s.hose([(41, 68), (47.5, 70)], 1.0), INK)
    s.part(s.hose([(22, 48), (10, 58), (12, 46)], 5.6), COAT, shade=0.35)                    # near arm, forearm up
    cuff(s, 12.0, 44.0, 3.6, 2.0)
    fist(s, 12.0, 39.0, thumb=(1, -1), radius=4.6)
    coin = s.oval(9.5, 19.0, 4.6, 4.6)
    s.part(coin, GOLD, shade=0.3, gloss=True)
    s.dots(s.oval(9.5, 19.0, 2.8, 2.8) - s.oval(9.5, 19.0, 1.9, 1.9), GOLD[0])
    s.dots(s.hose([(15, 33), (18.5, 29), (17, 26)], 1.0) | s.hose([(9, 32), (7, 28), (8.5, 25.5)], 1.0), CREAM[0])   # the flip
    for sx, sy in ((3, 12), (16, 13)):
        s.dots([(sx, sy - 1), (sx, sy + 1), (sx - 1, sy), (sx + 1, sy)], GOLD[1])
        s.dots([(sx, sy)], WHITE)
    _man_head(s, 32.0, 29.0)
    s.finish(101.5, 20.0, 32.0)
    return s


def kid_side():
    """Walking right, hunched, hands in the pockets, the coat trailing."""
    s = Sprite(CW, CH)
    s.part(s.hose([(29, 80), (24, 89), (19, 94)], 4.2), BLACK, mode="flat", outline=None)    # far leg, pushing off
    shoe(s, 15.5, 96.5, 1, 6.5, 25)
    s.part(s.hose([(33, 80), (39, 88), (41, 96)], 4.2), BLACK, mode="flat", outline=None)    # near leg, reaching
    shoe(s, 44.5, 98.0, 1, 7.0)
    coat = s.poly([(23, 44), (39, 44), (42, 60), (42, 83), (22, 84), (13, 87), (19, 60)])
    s.part(coat, COAT, shade=0.2, mode="tube")
    s.part(s.poly([(25, 45), (31, 36), (37, 45)]), COAT, shade=0.3)                          # collar turned up
    s.part(s.rows(coat, 63, 65), LAPEL, mode="flat", outline=None, form=coat)
    s.dots([(x, 62) for x in range(18, 43) if (x, 62) in coat] + [(x, 66) for x in range(17, 43) if (x, 66) in coat], INK_SOFT)
    s.dots(s.hose([(20, 70), (17, 80), (14, 86)], 1.0), COAT[0])                             # folds of the tail
    s.dots(s.hose([(27, 68), (26, 82)], 1.0), COAT[0])
    s.part(s.hose([(31, 48), (29.5, 58), (35, 67)], 5.6), COAT, shade=0.35)                  # near arm, hand pocketed
    s.dots(s.hose([(32, 68), (38.5, 67)], 1.0), INK)
    _man_head(s, 31.0, 29.0, side=True)
    s.finish(101.5, 21.0, 30.0)
    return s


# --- Capsule Machine No. 1: 88 x 128 ---------------------------------------------------

MW, MH = 88, 128
GLOBE = (44.0, 50.0, 27.0)
PILE = [  # centre, radius, ramp, seam tilt: the back of the pile first
    (27.0, 52.0, 7.4, GREEN, 20), (62.0, 51.0, 7.4, TEAL, -30), (44.0, 66.0, 8.2, RED, -10),
    (30.5, 63.5, 7.8, MUSTARD, 35), (58.0, 63.0, 7.8, GREEN, -40), (21.5, 60.0, 6.0, RED, 60), (66.5, 60.0, 6.0, MUSTARD, -60),
]


def machine(awake=True):
    s = Sprite(MW, MH)
    gx, gy, gr = GLOBE
    if awake:
        # Noodle arms from behind the collar: one up to the cap, one on the hip.
        s.part(s.hose([(27, 79), (4, 76), (11, 30)], 3.8), BLACK, mode="flat", outline=None)
        s.part(s.hose([(61, 79), (84, 82), (75, 98)], 3.8), BLACK, mode="flat", outline=None)
    # Foot ring and the flared body.
    foot = s.poly([(13, 115), (75, 115), (79, 118), (79, 121), (76, 124), (12, 124), (9, 121), (9, 118)])
    s.part(foot, RED, shade=0.22, mode="tube", gloss=True)
    s.shadow(s.rows(foot, 122, 124))
    for bx in (16, 30, 58, 72):
        s.dots([(bx, 119), (bx + 1, 119)], BRASS[2])
        s.dots([(bx, 120), (bx + 1, 120)], RED[0])
    body = s.poly([(29, 80), (59, 80), (73, 115), (15, 115)])
    s.part(body, RED, shade=0.24, mode="tube", gloss=True)
    s.shadow(s.rows(body, 80, 83))                                                         # under the collar
    s.part(s.rows(body, 108, 114), BRASS, shade=0.24, mode="tube", gloss=True, outline=None, form=body)
    s.dots([(x, 107) for x in range(15, 74) if (x, 107) in body], INK_SOFT)
    s.dots(s.hose([(64, 88), (67.5, 104)], 1.0), RED[0])                                   # a seam in the sheet
    collar = s.poly([(26, 73), (62, 73), (64, 75), (64, 79), (62, 81), (26, 81), (24, 79), (24, 75)])
    s.part(collar, BRASS, shade=0.24, mode="tube", gloss=True)
    s.dots([(x, 78) for x in range(25, 64)], BRASS[0])
    # Globe: pale smoky glass over the pile of capsules.
    glass = s.oval(gx, gy, gr, gr)
    inside = s.oval(gx, gy, gr - 1.6, gr - 1.6)
    s.part(glass, GLASS, shade=0.2)
    for bx, by, br, colors, tilt in PILE:
        capsule(s, bx, by, br, colors, tilt, inside)
    s.shadow(s.rows(inside, 0, 30))                                                        # the cap's shadow
    s.dots(s.hose([(22, 44), (24, 33), (33, 27)], 2.2) & inside, WHITE)                    # reflections
    s.dots(s.hose([(36.5, 25.5), (39, 24.8)], 2.0) & inside, WHITE)
    s.dots(s.oval(64.5, 66.5, 1.6, 2.6, 35) & inside, GLASS[2])
    # The cap: tilted like a hat when awake.
    turn = -7.0 if awake else 0.0
    lift = 0.0 if awake else 1.0
    s.part(s.rows(s.oval(44.5, 18.5 + lift, 20.0, 11.0, turn), 0, 22), RED, shade=0.26, gloss=True)
    s.part(s.oval(44.5, 6.5 + lift, 5.0, 3.2, turn), BRASS, shade=0.3, gloss=True)
    brim = s.oval(44.0, 22.5 + lift, 28.5, 5.6, turn)
    s.part(brim, RED, shade=0.3, gloss=True)
    s.dots(s.hose([(24, 23.5 + lift - (2.2 if awake else 0)), (36, 20.8 + lift - (1.0 if awake else 0)), (46, 20.2 + lift)], 1.2) & brim, RED[2])
    # Mechanism: plate, coin slot, crank, chute with a capsule waiting.
    plate = s.poly([(35, 84), (53, 84), (54, 85), (54, 99), (53, 100), (35, 100), (34, 99), (34, 85)])
    s.part(plate, GREY, shade=0.22, mode="tube")
    s.dots([(36, 86), (52, 86), (36, 98), (52, 98)], GREY[2])
    s.part(s.poly([(48, 87), (51, 87), (51, 94), (48, 94)]), BRASS, mode="flat")
    s.dots([(49, y) for y in range(88, 94)] + [(50, y) for y in range(88, 94)], INK)
    s.part(s.oval(41.0, 92.5, 4.6, 4.6), BRASS, shade=0.3, gloss=True)
    s.dots([(41, 92), (41, 93)], INK)
    s.part(s.hose([(41, 92.5), (46, 98.5)], 2.2), GREY, mode="flat")
    s.part(s.oval(47.0, 99.5, 2.6, 2.6), RED, shade=0.3)
    chute = s.poly([(35, 102), (53, 102), (54, 103), (54, 114), (34, 114), (34, 103)])
    s.part(chute, GREY, shade=0.22, mode="tube")
    hole = s.poly([(37, 105), (51, 105), (51, 114), (37, 114)])
    s.dots(hole, INK)
    s.dots(s.rows(hole, 105, 105) | s.cols(hole, 37, 37), BLACK[2])
    waiting = s.oval(44.0, 114.0, 5.4, 5.4)
    s.part(waiting, CREAM, shade=0.3, clip=hole)
    s.part(s.rows(waiting, 0, 111), MUSTARD, shade=0.3, outline=None, clip=hole, form=waiting)
    # What it costs, and a paper label.
    price = s.oval(23.5, 100.0, 5.0, 5.0)
    s.part(price, GOLD, shade=0.3, gloss=True)
    s.dots(s.hose([(23.5, 97.5), (23.5, 102.5)], 1.4) | s.hose([(22.2, 98.6), (23.5, 97.5)], 1.2), INK)
    label = s.poly([(60, 90), (69, 91), (68, 103), (59, 102)])
    s.part(label, CREAM, shade=0.2)
    s.dots(s.hose([(61.5, 93.5), (66.5, 94)], 1.0) | s.hose([(64, 93.5), (63.5, 100)], 1.0) | s.hose([(61, 97), (66.5, 97.5)], 1.0), RED[0])
    if awake:
        pie_eye(s, 35.5, 47.0, 6.4, 8.6, -4, clip=glass, lid=0.34, lid_colors=GLASS)
        pie_eye(s, 52.5, 46.0, 6.4, 8.6, -4, clip=glass, lid=0.34, lid_colors=GLASS)
        s.dots(s.hose([(27, 33.0), (34, 33.0), (42, 37.5)], 2.6) & glass, INK)              # brows drawn down
        s.dots(s.hose([(46, 36.5), (54, 31.0), (61, 32.5)], 2.6) & glass, INK)
        s.dots(s.oval(26.5, 57.0, 3.0, 1.8), ROSE)
        s.dots(s.oval(62.0, 55.5, 3.0, 1.8), ROSE)
        grin(s, 44.5, 60.0, 11.0, -4, clip=inside, teeth=True)
        # Left hand pinches the brim of the cap; right fist sits on the hip.
        cuff(s, 10.5, 30.5, 4.0, 2.2, 12)
        s.part(s.oval(11.0, 24.5, 5.4, 5.0), GLOVE, shade=0.3)
        for fx in (9.0, 12.5, 16.0):
            s.part(s.hose([(fx, 23.0), (fx + 2.5, 18.5)], 3.2, 2.6), GLOVE, shade=0.3)
        s.part(s.hose([(7.0, 26.0), (9.0, 30.0)], 3.0, 2.4), GLOVE, shade=0.3)              # thumb under the brim
        cuff(s, 78.5, 94.5, 2.4, 3.8, -30)
        fist(s, 74.5, 99.5, thumb=(-1, -1), radius=5.4)
    else:
        sleepy_eye(s, 35.5, 46.0, 6.0)
        sleepy_eye(s, 52.5, 46.0, 6.0)
        s.dots(s.hose([(40, 58), (44, 59.5), (48, 58)], 1.3), INK)
        for index, (zx, zy) in enumerate(((70, 20), (76, 12), (81, 5))):                    # z z z
            size = 3 - index * 0.5
            s.dots(s.hose([(zx, zy), (zx + size, zy)], 1.0) | s.hose([(zx + size, zy), (zx, zy + size)], 1.0) | s.hose([(zx, zy + size), (zx + size, zy + size)], 1.0), INK)
    s.finish(124.5, 37.0, 44.0)
    return s


# --- contact sheet ---------------------------------------------------------------

BACKDROP = ramp("#120c0a")[0]
LABEL = ramp("#c9b383")[0]
PAPER = ramp("#2a1e17", "#3d2c20", "#57412d", "#74593c", "#927550", "#ad9066")


def _paper(width, height):
    """Aged paper lit like a pool of lamp light: banded from the centre out,
    with a little grain, so the figures stand in the dark."""
    panel = Image.new("RGBA", (width, height))
    data = panel.load()
    state = 12345
    for y in range(height):
        for x in range(width):
            dx = (x - width * 0.5) / (width * 0.62)
            dy = (y - height * 0.56) / (height * 0.62)
            state = (state * 1103515245 + 12345) & 0x7FFFFFFF
            level = 1.0 - math.sqrt(dx * dx + dy * dy) + ((state >> 16) % 100 - 50) / 900.0
            data[x, y] = PAPER[max(0, min(len(PAPER) - 1, int(level * len(PAPER))))]
    return panel


def _tile(sprite_image, zoom, label):
    tile = Image.new("RGBA", (sprite_image.width * zoom + 24, sprite_image.height * zoom + 44), BACKDROP)
    panel = _paper(sprite_image.width, sprite_image.height).resize((sprite_image.width * zoom, sprite_image.height * zoom), Image.NEAREST)
    panel.alpha_composite(sprite_image.resize(panel.size, Image.NEAREST))
    tile.alpha_composite(panel, (12, 10))
    ImageDraw.Draw(tile).text((12, sprite_image.height * zoom + 18), label, fill=LABEL)
    return tile


def _row(tiles, title):
    row = Image.new("RGBA", (sum(tile.width for tile in tiles) + 16, max(tile.height for tile in tiles) + 26), BACKDROP)
    ImageDraw.Draw(row).text((12, 6), title, fill=LABEL)
    x = 8
    for tile in tiles:
        row.alpha_composite(tile, (x, 22))
        x += tile.width
    return row


def build():
    front, side = kid_front(), kid_side()
    awake, asleep = machine(True), machine(False)
    sheet_rows = [
        _row([_tile(front.image(), 5, "FRENTE: lanza su moneda"), _tile(side.image(), 5, "DERECHA: andando"), _tile(side.flipped().image(), 5, "IZQUIERDA")],
             "PERSONAJE  %d x %d px" % (CW, CH)),
        _row([_tile(awake.image(), 4, "DESPIERTA: demasiado contenta de verte"), _tile(asleep.image(), 4, "APAGADA: dormida")],
             "MAQUINA DE CAPSULAS N. 1  %d x %d px" % (MW, MH)),
    ]
    scene = Image.new("RGBA", (300, MH + 12), CLEAR)
    scene.alpha_composite(awake.image(), (6, 6))
    scene.alpha_composite(front.image(), (98, 6 + MH - CH + 2))
    scene.alpha_composite(side.image(), (160, 6 + MH - CH + 6))
    scene.alpha_composite(asleep.image(), (208, 6))
    sheet_rows.append(_row([_tile(scene, 3, "juntos, proporcion real (x3)")], "ESCALA"))
    sheet = Image.new("RGBA", (max(row.width for row in sheet_rows), sum(row.height for row in sheet_rows)), BACKDROP)
    y = 0
    for row in sheet_rows:
        sheet.alpha_composite(row, (0, y))
        y += row.height
    return sheet


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    build().save(OUT)
    print("wrote %s" % os.path.relpath(OUT))
