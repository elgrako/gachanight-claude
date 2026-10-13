"""The protagonist: the 1 PESETA coin of the owner's `diseños/moneda1.png`,
redrawn at about the size of that picture (190 x 214) with its fourteen
colours, its thick dark line and its soft banded shading, in several poses
and with the faces it will wear.

Nothing here is used by the game. It writes
tools/pixel/previews/proto_peseta.png (not shipped). Run from the repository
root:

    python tools/pixel/proto_peseta.py

How it is drawn:
- the palette is the reference's own (already desaturated by the owner), so
  nothing is desaturated again here;
- every shape is rasterised four times larger and reduced, for clean curves;
- volume comes from bands of tone, never hatching: a ball darkens away from a
  highlight, a flat disc darkens across the light, and every part casts a
  line of shadow where it meets the next;
- line: a dark contour on every part and a second pixel around the whole
  figure, as heavy as in the reference;
- rubber hose: thick black limbs without joints that bend in one arc, rolled
  cuffs at wrists and ankles, four-finger gloves, bulbous shoes, tall pie-cut
  eyes, a ball nose and an open laugh; the coin leans into what it does.
"""
import glob
import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "previews", "proto_peseta.png")
SS = 4
W, H = 190, 228
GROUND = 210.0
RISE = 14.0                    # the poses below were measured on the reference; this drops them
LIGHT = (-0.55, -0.83)        # the light comes from the upper left


def rgb(code):
    code = code.lstrip("#")
    return (int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16), 255)


# The reference's colours, dark to light.
K0, K1, K2 = rgb("#000000"), rgb("#0e0d0c"), rgb("#191815")
D1, D2, D3, D4 = rgb("#2a2722"), rgb("#3a352d"), rgb("#4c4337"), rgb("#57544d")
B1, B2, B3 = rgb("#62533e"), rgb("#716049"), rgb("#8a775a")
C1, C2, C3, C4 = rgb("#b29d76"), rgb("#beae90"), rgb("#d8cbb1"), rgb("#e3d9c6")
LINE = K2
ORDER = [K0, K1, K2, D1, D2, D3, B1, B2, B3, C1, C2, C3, C4]     # dark to light, for shadows and anti-aliasing
INKS = (K0, K1, K2)

FIELD = [B2, B3, C1, C1, C2]            # the coin's face
RIM = [B3, C1, C2, C3]                  # its raised rim
EDGE = [K2, D1, D2, D3, B1]             # its thickness, in shadow
WHITE = [B3, C2, C3, C4, C4]            # gloves, cuffs, eyes
LIMB = [K1, K2, K2, D1]
HAT = [K2, D1, D2, D3, D4]
BAND = [C2, C3, C4]
SHOE = [K2, D1, D2, D3, B1]
NOSE = [B2, B3, C1, C2, C3]
TONGUE = [B1, B2, B3]
PANEL = rgb("#5b564f")
BACKDROP = rgb("#191714")
LABEL = rgb("#d8cbb1")


class Sprite:
    def __init__(self, width=W, height=H):
        self.w, self.h = width, height
        self.px = {}

    # --- shapes ---------------------------------------------------------------
    def _mask(self, paint):
        big = Image.new("L", (self.w * SS, self.h * SS), 0)
        paint(ImageDraw.Draw(big))
        data = big.resize((self.w, self.h), Image.BOX).tobytes()
        return {(index % self.w, index // self.w) for index, value in enumerate(data) if value >= 128}

    def oval(self, cx, cy, rx, ry, turn=0.0):
        angle = math.radians(turn)
        points = []
        for step in range(64):
            t = math.tau * step / 64.0
            x, y = math.cos(t) * rx, math.sin(t) * ry
            points.append(((cx + x * math.cos(angle) - y * math.sin(angle) + 0.5) * SS, (cy + x * math.sin(angle) + y * math.cos(angle) + 0.5) * SS))
        return self._mask(lambda d: d.polygon(points, fill=255))

    def poly(self, points):
        scaled = [((x + 0.5) * SS, (y + 0.5) * SS) for x, y in points]
        return self._mask(lambda d: d.polygon(scaled, fill=255))

    @staticmethod
    def bezier(points, t):
        pts = list(points)
        while len(pts) > 1:
            pts = [(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t) for i in range(len(pts) - 1)]
        return pts[0]

    def hose(self, points, width, end_width=None):
        """A curve through control points; thin ones are plotted pixel by pixel."""
        end = width if end_width is None else end_width
        if width < 1.6 and end < 1.6:
            return {(int(round(self.bezier(points, step / 240.0)[0])), int(round(self.bezier(points, step / 240.0)[1]))) for step in range(241)}

        def paint(d):
            for step in range(121):
                t = step / 120.0
                x, y = self.bezier(points, t)
                r = (width + (end - width) * t) / 2.0
                d.ellipse([(x - r + 0.5) * SS, (y - r + 0.5) * SS, (x + r + 0.5) * SS, (y + r + 0.5) * SS], fill=255)
        return self._mask(paint)

    def between(self, upper, lower):
        """The area closed by two curves that share their ends."""
        points = [self.bezier(upper, step / 30.0) for step in range(31)] + [self.bezier(lower, 1.0 - step / 30.0) for step in range(31)]
        return self.poly(points)

    @staticmethod
    def grow(mask, steps=1):
        out = set(mask)
        for index in range(steps):
            near = ((1, 0), (-1, 0), (0, 1), (0, -1)) if index % 2 == 0 else ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))
            out |= {(x + dx, y + dy) for x, y in out for dx, dy in near}
        return out

    # --- painting ---------------------------------------------------------------
    def part(self, mask, colors, mode="ball", cuts=None, line=LINE, weight=1, clip=None, form=None, spot=0.36):
        """A solid shaded in bands of its ramp. "ball" darkens away from a
        highlight, "slab" darkens across the light, "flat" takes the middle."""
        if clip is not None:
            mask = mask & clip
        if not mask:
            return mask
        solid = form if form is not None else mask
        if line is not None:
            ring = self.grow(solid, weight) - solid
            if clip is not None:
                ring &= clip
            for point in ring:
                self.px[point] = line
        count = len(colors)
        if cuts is None:
            cuts = [(index + 1.0) / count for index in range(count - 1)]
        xs = [x for x, _y in solid]
        ys = [y for _x, y in solid]
        cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
        rx, ry = max((max(xs) - min(xs)) / 2.0, 1.0), max((max(ys) - min(ys)) / 2.0, 1.0)
        for x, y in mask:
            if mode == "flat":
                t = 0.5
            elif mode == "slab":
                t = 0.5 - ((x - cx) / rx * LIGHT[0] + (y - cy) / ry * LIGHT[1]) * -0.5
            else:
                dx = (x - cx) / rx - LIGHT[0] * spot
                dy = (y - cy) / ry - LIGHT[1] * spot
                t = 1.0 - math.sqrt(dx * dx + dy * dy) / 1.45
            index = 0
            while index < count - 1 and t > cuts[index]:
                index += 1
            self.px[(x, y)] = colors[index]
        return mask

    def dots(self, points, color):
        for point in points:
            self.px[tuple(point)] = color

    def tint(self, mask, ramp_colors, step):
        """Moves what is drawn in `mask` up (+) or down (-) the ramp."""
        for point in mask:
            color = self.px.get(point)
            if color in ramp_colors:
                self.px[point] = ramp_colors[max(0, min(len(ramp_colors) - 1, ramp_colors.index(color) + step))]

    def darken(self, mask, steps=1):
        """A cast shadow: light colours drop down the palette."""
        for point in mask:
            color = self.px.get(point)
            if color in ORDER and ORDER.index(color) > 5:
                self.px[point] = ORDER[max(ORDER.index(color) - steps, 5)]

    def finish(self, shadow=None):
        """Softens the inside corners of the line work with one in-between
        tone (never the outer edge: the background is not known), then adds
        the second pixel of contour around the figure and its floor shadow."""
        soft = {}
        for (x, y), color in self.px.items():
            if color not in ORDER or ORDER.index(color) < 7:
                continue
            across = self.px.get((x + 1, y)) in INKS or self.px.get((x - 1, y)) in INKS
            along = self.px.get((x, y + 1)) in INKS or self.px.get((x, y - 1)) in INKS
            if across and along:
                soft[(x, y)] = ORDER[ORDER.index(color) - 2]
        self.px.update(soft)
        figure = set(self.px)
        for point in self.grow(figure, 1) - figure:
            self.px[point] = LINE
        if shadow:
            cx, rx = shadow
            for point in self.oval(cx, GROUND, rx, 4.0):
                if point not in self.px:
                    self.px[point] = (20, 18, 15, 110)

    def image(self):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for (x, y), color in self.px.items():
            if 0 <= x < self.w and 0 <= y < self.h:
                img.putpixel((x, y), color)
        if getattr(self, "overlay", None) is not None:
            img.alpha_composite(self.overlay)            # parts lifted from the reference go on top
        return img


# --- the coin ------------------------------------------------------------------------

def _on_rim(s, cx, cy, angle, reach, turn=-6.0):
    """A point of the coin at `angle` degrees (0 right, 90 down), `reach` of the way out."""
    a, t = math.radians(angle), math.radians(turn)
    x, y = math.cos(a) * 55.0 * reach, math.sin(a) * 61.0 * reach
    return (cx + x * math.cos(t) - y * math.sin(t), cy + x * math.sin(t) + y * math.cos(t))


def coin(s, cx, cy, back=False, worn=False):
    """The disc turned a little away from us: its thickness on the far side,
    a raised reeded rim, a ring of beads, the recessed field. Returns the field."""
    side = 1.0 if back else -1.0
    rear = s.oval(cx + side * 9.0, cy + 3.0, 55.0, 61.0, -6)
    front = s.oval(cx, cy, 55.0, 61.0, -6)
    s.part(rear, EDGE, mode="slab")
    for x, y in rear - front:                                                              # reeding in the shade
        notch = int((math.degrees(math.atan2(y - cy - 3.0, x - cx - side * 9.0)) + 360.0) / 2.8) % 2
        s.px[(x, y)] = D3 if notch else D1
    s.part(front, RIM, mode="ball", cuts=(0.22, 0.52, 0.84), spot=0.5)
    field = s.oval(cx + side * 2.5, cy + 1.0, 45.5, 52.0, -6)
    for x, y in front - field:                                                             # reeding on the rim
        if int((math.degrees(math.atan2(y - cy, x - cx)) + 360.0) / 2.2) % 2:               # fine, shallow grooves
            s.tint([(x, y)], RIM, -1)
    if worn:
        for angle in (205.0, 262.0, 18.0, 96.0, 141.0):                                    # nicks knocked out of the rim
            nick = s.oval(*_on_rim(s, cx, cy, angle, 0.99), 3.4, 2.4, angle + 90.0) & (front - field)
            s.dots(nick, D1)
            s.dots({(x + 1, y + 1) for x, y in nick} & (front - field) - nick, C3)
    s.part(field, FIELD, mode="ball", cuts=(0.16, 0.34, 0.5, 0.93), line=B1, spot=0.25)
    step = s.oval(cx + side * 2.5, cy + 1.0, 43.3, 49.8, -6)
    for x, y in field - step:                                                              # the step down from the rim
        lit = (x - cx) * LIGHT[0] + (y - cy) * LIGHT[1] > 0
        s.px[(x, y)] = B2 if lit else C3
    for angle in range(0, 360, 7):                                                         # beading inside the rim
        bx, by = _on_rim(s, cx + side * 2.5, cy + 1.0, angle, 0.74)
        bead = (int(round(bx)), int(round(by)))
        if bead in step:
            s.dots([bead], B3)
            if (bead[0] + 1, bead[1] + 1) in step:
                s.dots([(bead[0] + 1, bead[1] + 1)], C2)
    return field


def wear(s, cx, cy, field):
    """Years in pockets: scratches with a bright lip, a dent, dull patches."""
    for points in ([(cx - 30, cy - 34), (cx - 20, cy - 24)], [(cx - 27, cy - 36), (cx - 19, cy - 29)], [(cx + 24, cy + 30), (cx + 36, cy + 22)],
                   [(cx - 8, cy + 40), (cx + 2, cy + 44)], [(cx + 30, cy - 36), (cx + 37, cy - 26)]):
        line = s.hose(points, 1.0) & field
        s.dots({(x + 1, y + 1) for x, y in line} & field, C3)
        s.dots(line, B2)
    dent = s.oval(cx - 33.0, cy + 26.0, 4.6, 3.4, 30) & field
    s.dots(dent, B3)
    s.dots({(x + 1, y + 1) for x, y in dent} & field - dent, C3)
    s.darken(s.oval(cx + 28.0, cy + 36.0, 10.0, 6.0, -30) & field)
    s.darken(s.oval(cx - 34.0, cy - 6.0, 6.0, 12.0, 10) & field)
    s.dots([(x, y) for x, y in s.oval(cx - 4.0, cy + 30.0, 22.0, 14.0) & field
            if (x * 3 + y * 5) % 11 == 0 and s.px.get((x, y)) in (C1, B3)], B2)               # stubble


def laurel(s, stem, clip, side):
    """A sprig struck into the field, drawn as the reference draws it: a fine
    stem and paired leaves in outline, the metal showing through."""
    s.dots(s.hose(stem, 1.0) & clip, B2)
    for index in range(6):
        t = 0.14 + index * 0.155
        x, y = s.bezier(stem, t)
        ahead = s.bezier(stem, min(t + 0.05, 1.0))
        along = math.degrees(math.atan2(ahead[1] - y, ahead[0] - x))
        for lean in (42.0, -42.0):
            angle = math.radians(along + lean)
            leaf = s.oval(x + math.cos(angle) * 5.4, y + math.sin(angle) * 5.4, 5.2, 2.2, along + lean) & clip
            s.dots((s.grow(leaf, 1) - leaf) & clip, B2)
            s.dots(leaf, C1)
            s.dots(s.hose([(x + math.cos(angle) * 2.0, y + math.sin(angle) * 2.0), (x + math.cos(angle) * 8.0, y + math.sin(angle) * 8.0)], 1.0) & leaf, B3)   # the leaf's rib
    del side


FONT = {
    "P": ["11110", "01001", "01001", "01110", "01000", "01000", "11100"],
    "E": ["11111", "01001", "01000", "01110", "01000", "01001", "11111"],
    "S": ["01111", "10001", "10000", "01110", "00001", "10001", "11110"],
    "T": ["11111", "10101", "00100", "00100", "00100", "00100", "01110"],
    "A": ["00100", "00100", "01010", "01010", "01110", "10001", "11011"],
}


def _struck(s, glyph, clip):
    """Raised lettering as the reference draws it: a dark khaki shape in a
    darker line, so it reads on the lit and on the shaded metal alike."""
    glyph = glyph & clip
    s.dots((s.grow(glyph, 1) - glyph) & clip, D3)
    s.dots(glyph, B2)
    s.dots({(x, y) for x, y in glyph if (x - 1, y) not in glyph}, B3)                       # its lit edge


def legend(s, cx, cy, clip):
    """The coin's value, a raised serif 1 below the nose. (The word PESETA
    was dropped at the owner's request.)"""
    one = s.poly([(cx + 16, cy + 23), (cx + 21, cy + 23), (cx + 21, cy + 39), (cx + 16, cy + 39)]) | s.poly([(cx + 12, cy + 39), (cx + 25, cy + 39), (cx + 25, cy + 42), (cx + 12, cy + 42)])
    one |= s.poly([(cx + 11, cy + 29), (cx + 16, cy + 23), (cx + 16, cy + 28), (cx + 13, cy + 31)])
    _struck(s, one, clip)


def reverse(s, cx, cy, clip):
    """The other side: a crowned shield between two columns, worn."""
    shield = s.poly([(cx - 16, cy - 20), (cx + 16, cy - 20), (cx + 16, cy + 4), (cx, cy + 24), (cx - 16, cy + 4)])
    s.part(shield, [B3, C1, C2], mode="slab", line=B1, clip=clip)
    s.dots((s.hose([(cx - 16, cy - 6), (cx + 16, cy - 6)], 1.0) | s.hose([(cx, cy - 20), (cx, cy + 23)], 1.0)) & shield, B1)
    s.part(s.poly([(cx - 12, cy - 22), (cx - 12, cy - 31), (cx - 6, cy - 26), (cx, cy - 33), (cx + 6, cy - 26), (cx + 12, cy - 31), (cx + 12, cy - 22)]),
           [B3, C1, C2], mode="slab", line=B1, clip=clip)
    for side in (-1, 1):
        s.part(s.poly([(cx + side * 24, cy - 16), (cx + side * 29, cy - 16), (cx + side * 29, cy + 14), (cx + side * 24, cy + 14)]), [B3, C1, C2], mode="slab", line=B1, clip=clip)
        s.part(s.poly([(cx + side * 22, cy + 14), (cx + side * 31, cy + 14), (cx + side * 31, cy + 18), (cx + side * 22, cy + 18)]), [B3, C1], mode="slab", line=B1, clip=clip)
    for index, digit_x in enumerate((-13, -5, 3, 11)):                                       # the date, worn to stumps
        s.part(s.poly([(cx + digit_x, cy + 34), (cx + digit_x + 5, cy + 34 - index % 2), (cx + digit_x + 5, cy + 41), (cx + digit_x, cy + 41)]), [B2, B3], mode="slab", line=B1, clip=clip)
    s.dots((s.hose([(cx + 22, cy - 34), (cx + 33, cy - 20)], 1.0) | s.hose([(cx - 34, cy + 16), (cx - 26, cy + 30)], 1.0) | s.hose([(cx - 30, cy - 28), (cx - 24, cy - 22)], 1.0)) & clip, B2)


# --- the face ----------------------------------------------------------------------------

FACES = ["alegre", "sorpresa", "triste", "enfado"]
FACE_NAMES = {"alegre": "ALEGRE (la normal)", "euforico": "EUFORICO", "sorpresa": "SORPRESA", "triste": "TRISTE",
              "enfado": "ENFADO", "sueno": "SUENO", "guino": "GUINO", "miedo": "MIEDO"}
EYES = ((-18.0, -7.5, 12.5, 19.0, -12.0), (11.0, -17.5, 11.0, 20.5, -10.0))    # dx, dy, rx, ry, turn


def _pupil(s, x, y, rx, ry, turn, white, small=False):
    if small:
        s.dots(s.oval(x, y, 3.2, 4.4, turn) & white, K2)
        s.dots(s.oval(x - 0.8, y - 1.2, 0.9, 0.9) & white, C4)
        return
    pupil = s.oval(x, y, rx, ry, turn) & white
    pupil -= s.poly([(x - 0.5, y - 1.0), (x + rx * 1.7, y - ry * 1.1), (x + rx * 1.9, y - ry * 0.05)])   # the pie slice
    s.dots(pupil, K2)
    s.dots({(px, py) for px, py in pupil if (px + 1, py) not in pupil or (px, py + 1) not in pupil} & s.oval(x + rx * 0.3, y + ry * 0.4, rx, ry, turn), K0)


def _cheek(s, x, y, clip, side):
    """A cheek pushed up by the smile: a crease, light on top, shade below."""
    s.dots(s.hose([(x - 5 * side, y - 3), (x, y - 6), (x + 5 * side, y - 2)], 1.0) & clip, C2)
    s.darken(s.oval(x, y + 2.0, 6.5, 3.0, side * 12.0) & clip)


def face(s, cx, cy, clip, kind="alegre", heavy=False):
    """Tall pie-cut eyes that stand proud of the metal and shade it, tapered
    brows riding high, a ball nose, an open laugh with a lip under it."""
    whites = []
    for dx, dy, rx, ry, turn in EYES:
        whites.append(s.oval(cx + dx, cy + dy, rx, ry, turn))
    both = whites[0] | whites[1]
    s.darken(({(x + 3, y + 3) for x, y in both} | {(x + 2, y + 2) for x, y in both}) & clip - both)   # the eyes' shadow on the field
    for index, (dx, dy, rx, ry, turn) in enumerate(EYES):
        ex, ey = cx + dx, cy + dy
        white = whites[index]
        s.part(white, WHITE, mode="ball", cuts=(0.05, 0.2, 0.42, 0.7), weight=2, clip=clip)
        s.darken((white - s.oval(ex + 1.0, ey + 4.0, rx, ry, turn)) & clip, 2)                 # the lid's shade on the eyeball
        wide = kind == "sorpresa"
        look = {"triste": (1.5, 6.5), "enfado": (4.0, 3.0)}.get(kind, (4.5, 3.0))
        _pupil(s, ex + (0.0 if wide else look[0]), ey + (0.0 if wide else look[1]), rx * 0.55, ry * 0.6, turn, white & clip, small=wide)
        if heavy:                                                                           # a lid that has seen it all
            lid = s.poly([(ex - rx - 2, ey - ry - 4), (ex + rx + 2, ey - ry - 4), (ex + rx + 2, ey - ry * 0.3), (ex - rx - 2, ey - ry * 0.2)]) & white & clip
            s.dots(lid, C1)
            s.dots({(x, y) for x, y in lid if (x, y - 3) not in lid}, C2)
            s.dots(s.hose([(ex - rx - 1, ey - ry * 0.2), (ex + rx + 1, ey - ry * 0.3)], 2.0) & white & clip, LINE)
            s.dots(s.hose([(ex - rx + 2, ey + ry + 3), (ex, ey + ry + 5), (ex + rx - 2, ey + ry + 3)], 1.0) & clip, B2)   # a bag under it
        if kind == "triste":
            s.dots(s.hose([(ex - rx + 1, ey + ry - 6), (ex, ey + ry - 2), (ex + rx - 1, ey + ry - 6)], 1.0) & white & clip, B3)   # the lower lid swells
        if kind == "enfado":
            drop_in, drop_out = 17.0, 5.0
            left, right = (drop_out, drop_in) if index == 0 else (drop_in, drop_out)
            lid = s.poly([(ex - rx - 2, ey - ry - 4), (ex + rx + 2, ey - ry - 4), (ex + rx + 2, ey - ry + right), (ex - rx - 2, ey - ry + left)]) & white & clip
            s.dots(lid, C1)
            s.dots(s.hose([(ex - rx - 1, ey - ry + left), (ex + rx + 1, ey - ry + right)], 2.0) & white & clip, LINE)
        if kind == "alegre" and not heavy:
            s.dots(s.hose([(ex - rx + 2, ey + ry + 2.5), (ex, ey + ry + 4.5), (ex + rx - 2, ey + ry + 2.0)], 1.0) & clip - white, B2)      # pushed up by the smile
    lift = {"alegre": (0, 0), "sorpresa": (-6, -6), "triste": (0, 0), "enfado": (8, 8)}[kind]
    tilt = {"triste": 7.0, "enfado": -6.0}.get(kind, 0.0)
    s.dots(s.hose([(cx - 34, cy - 30 + lift[0] + tilt), (cx - 26, cy - 34.5 + lift[0]), (cx - 16, cy - 31 + lift[0] - tilt)], 1.0) & clip, LINE)   # brows: a single fine line
    s.dots(s.hose([(cx - 4, cy - 38 + lift[1] - tilt), (cx + 4, cy - 44.5 + lift[1]), (cx + 13, cy - 41 + lift[1] + tilt)], 1.0) & clip, LINE)
    mx, my = cx - 6.0, cy + 22.0
    if kind == "alegre":
        upper = [(mx - 12.5, my - 1), (mx, my + 6), (mx + 12.5, my + 2)]
        lower = [(mx - 12.5, my - 1), (mx - 2, my + 27), (mx + 12.5, my + 2)]
        mouth = s.between(upper, lower) & clip
        s.darken((s.between([(mx - 14, my + 2), (mx, my + 9), (mx + 14, my + 5)], [(mx - 14, my + 2), (mx - 1, my + 38), (mx + 14, my + 5)]) - mouth) & clip)   # shade under the lip
        s.part(mouth, [K0, K1, K2, D1], mode="slab", weight=2, clip=clip)
        tongue = s.oval(mx + 1.5, my + 12.0, 7.0, 4.5, -8) & mouth
        s.part(tongue, [B1, B2, B3, C1], mode="ball", line=K2, clip=mouth)
        s.dots(s.hose([(mx - 2.0, my + 9.5), (mx + 2.5, my + 13.5)], 1.0) & tongue, B1)
        s.dots({(x, y) for x, y in mouth if (x, y - 1) not in mouth or (x, y - 2) not in mouth or (x, y - 3) not in mouth} - tongue, K0)   # the roof in shadow
        s.dots(s.hose([(mx - 12.5, my - 1), (mx - 20, my - 3), (mx - 21, my - 8)], 2.0) & clip, LINE)        # the corner curls up
        s.dots(s.hose([(mx + 12.5, my + 2), (mx + 18, my + 1)], 2.0) & clip, LINE)
        s.dots(s.hose([(mx - 8, my + 15), (mx - 1, my + 18.5), (mx + 7, my + 14)], 1.0) & clip - mouth, C2)   # light on the lower lip
        _cheek(s, mx - 25.0, my - 2.0, clip, -1)
    elif kind == "sorpresa":
        gape = s.oval(mx + 2, my + 11, 6.5, 9.5, -6)
        s.darken((s.oval(mx + 4, my + 14, 7.0, 10.0, -6) - gape) & clip)
        s.part(gape, [K0, K1, K2, D1], mode="slab", weight=2, clip=clip)
        s.part(s.oval(mx + 2.5, my + 16.5, 4.0, 3.2, -6) & gape, [B1, B2, B3], mode="ball", line=None)
        s.dots(s.hose([(mx - 3, my + 23), (mx + 2, my + 25), (mx + 7, my + 23)], 1.0) & clip, C2)
    elif kind == "triste":
        s.dots(s.hose([(mx - 13, my + 13), (mx, my + 4), (mx + 13, my + 12)], 2.6) & clip, LINE)
        s.dots(s.hose([(mx - 15, my + 13), (mx - 17, my + 17)], 1.0) | s.hose([(mx + 15, my + 12), (mx + 17, my + 16)], 1.0), B2)
        s.dots(s.hose([(mx - 6, my + 16), (mx, my + 13), (mx + 6, my + 16)], 1.0) & clip, C2)               # the lip pushed out
        s.darken(s.oval(mx, my + 20.0, 9.0, 3.0) & clip)
        tear = s.hose([(cx - 27, cy + 11), (cx - 29, cy + 21)], 3.0, 6.4)
        s.part(tear, [C2, C3, C4], mode="ball", clip=clip)
        s.dots(s.oval(cx - 30.0, cy + 19.0, 1.0, 1.4) & tear, C4)
    elif kind == "enfado":
        teeth = s.between([(mx - 14, my + 4), (mx, my + 2), (mx + 14, my + 3)], [(mx - 14, my + 4), (mx, my + 20), (mx + 14, my + 3)]) & clip
        s.darken((s.between([(mx - 13, my + 7), (mx, my + 5), (mx + 14, my + 6)], [(mx - 13, my + 7), (mx + 1, my + 24), (mx + 14, my + 6)]) - teeth) & clip)
        s.part(teeth, WHITE, mode="slab", weight=2, clip=clip)
        s.dots({(x, y) for x, y in teeth if (x - int(mx)) % 6 == 0} | (s.hose([(mx - 13, my + 9), (mx + 13, my + 8)], 1.0) & teeth), LINE)
        s.dots(s.hose([(mx - 14, my + 4), (mx - 18, my + 7)], 2.0) | s.hose([(mx + 14, my + 3), (mx + 18, my + 6)], 2.0), LINE)   # the corners pulled down
        s.dots(s.hose([(cx - 12, cy - 27), (cx - 9, cy - 22)], 1.0) | s.hose([(cx - 7, cy - 29), (cx - 5, cy - 24)], 1.0), B2)       # the knot between the brows
    nose = s.oval(cx + 8.5, cy + 5.5, 6.0, 4.8, -8)
    s.darken((s.oval(cx + 10.5, cy + 8.0, 6.2, 4.8, -8) - nose) & clip)                        # the nose's shadow
    s.part(nose, NOSE, mode="ball", weight=2, clip=clip)
    s.dots(s.oval(cx + 6.5, cy + 3.5, 1.7, 1.1, -20) & nose, C4)
    s.dots(s.hose([(cx + 9, cy + 9), (cx + 12.5, cy + 7.5)], 1.0) & nose, B3)                  # light bouncing back under it


# --- limbs, gloves, shoes, hat ---------------------------------------------------------------

def limb(s, points, width=9.0):
    """A rubber hose: one black arc with a dull sheen along its lit side."""
    body = s.hose(points, width)
    s.part(body, LIMB, mode="flat")
    s.dots(body, K2)
    s.dots(s.hose([(x - 1.6, y - 1.6) for x, y in points], width * 0.22) & body, D2)


GLOVE_CUTS = (0.06, 0.2, 0.44, 0.74)


def cuff(s, cx, cy, rx=8.5, ry=5.2, turn=0.0):
    """A rolled sock: a fat white ring with a fold line."""
    ring = s.oval(cx, cy, rx, ry, turn)
    s.part(ring, WHITE, mode="ball", cuts=(0.1, 0.3, 0.55, 0.8))
    a = math.radians(turn)
    s.dots(s.hose([(cx - math.cos(a) * rx * 0.6, cy - math.sin(a) * rx * 0.6 + ry * 0.35), (cx, cy + ry * 0.55), (cx + math.cos(a) * rx * 0.6, cy + math.sin(a) * rx * 0.6 + ry * 0.35)], 1.0) & ring, C2)


def _inside_line(s, shape, glove, color=LINE):
    """The contour of one part of the glove, drawn only where it runs inside
    the glove: fingers and thumb are lines on one white shape."""
    s.dots((s.grow(shape, 1) - shape) & glove, color)


def fist(s, cx, cy, turn=0.0, thumb=-1):
    """A closed four-finger glove in one piece: back of the hand, curled
    fingers, thumb and rolled cuff share a single contour and a single
    volume; inside it only lines tell them apart. The wrist is at the top."""
    a = math.radians(turn)

    def at(dx, dy):
        return (cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a))
    back = s.oval(*at(0, -1.0), 14.5, 12.0, turn)
    order = (9.4, 3.2, -3.0, -9.0) if thumb < 0 else (-9.4, -3.2, 3.0, 9.0)                    # the little finger first, the index last
    fingers = [s.oval(*at(dx, dy), size, size + 0.8, turn) for dx, size, dy in zip(order, (4.3, 4.9, 5.1, 4.9), (8.8, 10.4, 10.6, 9.8))]
    wrap = s.hose([at(thumb * 14.5, -5.0), at(thumb * 13.0, 3.5), at(thumb * 5.0, 7.0)], 7.4, 6.0)
    roll = s.oval(*at(0, -13.0), 10.5, 5.6, turn)
    glove = back | wrap | roll
    for finger in fingers:
        glove |= finger
    s.part(glove, WHITE, mode="ball", cuts=GLOVE_CUTS, weight=1, spot=0.42)
    _inside_line(s, roll, glove - roll)                                                    # where the cuff rolls over
    s.dots(s.hose([at(-6.5, -12.2), at(0, -10.2), at(6.5, -12.2)], 1.0) & roll, C2)
    for index in range(len(order) - 1):                                                    # the gaps between the fingers
        mid = (order[index] + order[index + 1]) / 2.0
        s.dots(s.hose([at(mid, 6.0), at(mid * 1.04, 15.0)], 1.0) & glove - wrap, LINE)
    s.dots((s.grow(back, 1) - back) & glove & s.grow(fingers[0] | fingers[1] | fingers[2] | fingers[3], 0) - wrap, B2)   # the knuckles fold under
    _inside_line(s, wrap, glove - roll)
    s.darken(({(x + 1, y + 2) for x, y in wrap} - wrap) & glove - roll)                        # the thumb shades the fingers
    for dx in (-4.6, 0.4, 5.4):                                                              # the three darts on the back
        s.dots(s.hose([at(dx, -8.0), at(dx + 0.4, -2.5)], 1.0) & back - wrap, B1)


def hat_hand(s, cx, cy):
    """The glove that tips the hat, in one piece: the back of the hand below
    the brim, the thumb under it, three fingers laid over it, the cuff."""
    back = s.oval(cx - 1.0, cy + 3.0, 13.5, 14.0, -24)
    thumb = s.hose([(cx + 7.0, cy + 11.0), (cx + 15.0, cy + 8.0), (cx + 20.0, cy + 2.0)], 7.4, 5.8)
    fingers = []
    for index in range(3):                                                                 # farthest finger first
        bx, by = cx - 7.0 + index * 6.2, cy - 6.5 + index * 1.6
        fingers.append(s.hose([(bx, by), (bx + 5.5, by - 5.5), (bx + 13.0 - index, by - 8.0 + index * 0.6)], 7.4, 6.2))
    roll = s.oval(cx - 7.5, cy + 16.0, 10.5, 5.6, -24)
    glove = back | thumb | roll
    for finger in fingers:
        glove |= finger
    s.part(glove, WHITE, mode="ball", cuts=GLOVE_CUTS, weight=1, spot=0.42)
    _inside_line(s, roll, glove - roll)
    s.dots(s.hose([(cx - 13.0, cy + 15.0), (cx - 7.0, cy + 18.5), (cx - 1.5, cy + 15.5)], 1.0) & roll, C2)
    _inside_line(s, thumb, glove - roll)
    for finger in fingers:
        _inside_line(s, finger, glove - roll)
        s.darken(({(x + 1, y + 2) for x, y in finger} - finger) & back - thumb)
    for dx in (-7.5, -3.0, 1.5):                                                             # darts
        s.dots(s.hose([(cx + dx, cy + 4.0), (cx + dx - 2.0, cy + 10.5)], 1.0) & back - thumb, B1)


def shoe(s, ax, ay, turn=0.0, facing=1):
    """A 1930s cartoon shoe in profile, hung from the ankle at (ax, ay): the
    mouth the leg goes into, a low quarter and heel counter, a vamp rising to
    a fat round toe, a pale welted sole and a stacked heel under it."""
    a = math.radians(turn)

    def at(dx, dy):
        return (ax + facing * (dx * math.cos(a) - dy * math.sin(a)), ay + dx * math.sin(a) + dy * math.cos(a))

    def quad(x0, y0, x1, y1):
        return s.poly([at(x0, y0), at(x1, y0), at(x1, y1), at(x0, y1)])
    lean = turn * facing
    upper = s.oval(*at(0.0, 5.5), 11.5, 9.0, lean) | s.oval(*at(15.0, 6.0), 13.0, 8.0, lean) | s.oval(*at(23.0, 4.0), 10.5, 9.5, lean)
    upper &= quad(-20.0, -12.0, 40.0, 11.0)                                                # cut flat where the sole begins
    sole = quad(-12.5, 11.0, 34.5, 14.0) | s.oval(*at(33.5, 12.0), 2.6, 2.4, lean)
    heel = quad(-12.5, 14.0, -1.5, 17.5)
    s.part(heel, [K1, K2, D1], mode="slab", weight=2)
    s.part(sole, [B1, B2, B3, C1], mode="slab", weight=2, cuts=(0.2, 0.5, 0.8))
    s.part(upper, SHOE, mode="ball", cuts=(0.1, 0.32, 0.6, 0.84), weight=2, spot=0.4)
    s.dots(s.hose([at(-11.0, 12.5), at(33.0, 12.5)], 1.0) & sole, B1)                          # the welt's seam
    s.dots({point for point in s.hose([at(-10.0, 9.5), at(32.0, 9.5)], 1.0) & upper if (point[0] + point[1]) % 3 == 0}, B1)     # stitches
    cap = s.oval(*at(26.0, 4.5), 9.5, 10.5, lean) & upper                                     # the toe cap
    s.dots((s.grow(cap, 1) - cap) & upper, K1)
    s.dots(s.oval(*at(22.5, -1.0), 4.6, 2.4, lean - 12) & upper, D4)                           # the toe shines
    s.dots(s.oval(*at(21.5, -1.6), 2.0, 1.1, lean - 12) & upper, C1)
    s.dots(s.hose([at(8.5, -1.0), at(11.0, 3.0), at(10.0, 8.0)], 1.0) & upper, K1)             # creases across the vamp
    s.dots(s.hose([at(12.5, 0.0), at(14.5, 3.5), at(14.0, 7.5)], 1.0) & upper, D1)
    s.dots(s.hose([at(-8.0, -1.0), at(-9.5, 5.0), at(-8.5, 10.0)], 1.0) & upper, K1)           # the counter's seam
    s.dots(s.oval(*at(-3.5, 2.0), 2.4, 1.2, lean - 10) & upper, D4)
    mouth = s.oval(*at(0.5, -2.2), 7.6, 3.0, lean)                                           # where the leg goes in
    s.part(mouth, [K0, K1, K2], mode="slab", weight=1)


def ankle(s, ax, ay, turn, facing):
    """The sock rolled over the shoe's mouth: it hides where leg meets shoe."""
    a = math.radians(turn)
    cuff(s, ax + facing * (0.5 * math.cos(a) + 3.0 * math.sin(a)), ay + 0.5 * math.sin(a) - 3.0 * math.cos(a), 8.6, 5.2, turn * facing)


def hat(s, cx, cy, turn, style="canotier"):
    """The hat, tipped: a flat-crowned "canotier" with a pale band and a bow,
    a round "bombin", or a soft "gorra" with a short peak."""
    a = math.radians(turn)

    def at(dx, dy):
        return (cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a))
    if style == "gorra":
        cap = s.poly([at(-24, 0), at(-22, -9), at(-10, -15), at(8, -15), at(20, -10), at(24, 0)])
        s.part(cap, HAT, mode="ball", cuts=(0.12, 0.4, 0.66, 0.88), weight=2)
        for dx in (-12.0, 0.0, 12.0):                                                      # panels and a button
            s.dots(s.hose([at(dx * 1.6, -1.0), at(dx * 0.7, -9.0), at(0, -14.5)], 1.0) & cap, K1)
        s.part(s.oval(*at(0, -14.5), 2.2, 1.6), [K2, D2, D3], mode="ball")
        s.part(s.poly([at(8, 0), at(34, 2), at(32, 5.5), at(6, 4)]), HAT, mode="slab", cuts=(0.12, 0.42, 0.72, 0.92), weight=2)   # peak
        s.dots(s.hose([at(-24, 0), at(0, 1.5), at(24, 0)], 1.0), K1)
        return
    if style == "bombin":
        crown = {(x, y) for x, y in s.oval(*at(0, -4), 21.0, 21.0, turn)} - s.poly([at(-40, 0), at(40, 0), at(40, 40), at(-40, 40)])
    else:
        crown = s.poly([at(-20, -21), at(-18, -23), at(18, -23), at(20, -21), at(21, 0), at(-21, 0)])
    s.part(crown, HAT, mode="ball" if style == "bombin" else "slab", cuts=(0.12, 0.4, 0.7, 0.9), weight=2)
    if style == "canotier":
        s.dots(s.oval(*at(0, -21.5), 18.0, 3.0, turn) & crown, D4)                             # the flat top
    band = s.poly([at(-23, -12), at(23, -12), at(23, -2), at(-23, -2)]) & crown
    s.part(band, BAND, mode="slab", line=None, form=crown, cuts=(0.3, 0.7))
    s.dots({(x, y) for x, y in band if (x, y - 1) not in band or (x, y + 1) not in band}, D1)
    s.part(s.poly([at(8, -11.5), at(15, -8), at(15, -4), at(8, -0.5), at(10, -6)]) | s.poly([at(22, -11.5), at(15, -8), at(15, -4), at(22, -0.5), at(20, -6)]),
           BAND, mode="slab", cuts=(0.3, 0.7))                                              # the bow
    s.dots(s.oval(*at(15, -6), 1.6, 2.4, turn), C1)
    brim = s.oval(cx, cy + 1.0, 37.5, 6.6, turn)
    s.part(brim, HAT, mode="slab", cuts=(0.12, 0.42, 0.72, 0.92), weight=2)
    s.dots(s.hose([at(-26, -0.5), at(-8, -4.2), at(12, -4.0)], 1.0) & brim, D3)
    s.dots(s.hose([at(-28, 3.0), at(0, 6.5), at(28, 3.0)], 1.0) & brim, K1)                    # the brim's underside


# --- poses -----------------------------------------------------------------------------------

# The gloves (with their cuffs) and the shoes (with their socks) of the owner's
# picture, as outlines in its own pixel coordinates. They are lifted from it
# pixel for pixel and set into the figure, which is drawn to the same measure.
REFERENCE = os.path.join(os.path.dirname(os.path.dirname(HERE)), "dise*", "moneda1.png")
REFERENCE_PARTS = [
    [(1, 52), (8, 40), (18, 33), (32, 33), (41, 38), (42, 46), (34, 52), (32, 62), (26, 72), (16, 78), (4, 74), (1, 64)],                       # glove on the hat
    [(145, 124), (150, 116), (162, 111), (176, 112), (184, 118), (184, 134), (180, 146), (166, 149), (150, 144), (145, 134)],                   # fist
    [(17, 160), (20, 148), (32, 142), (46, 143), (54, 150), (60, 154), (70, 156), (74, 164), (73, 174), (68, 180), (68, 196), (60, 201), (46, 200), (30, 192), (20, 178)],   # shoe kicked back
    [(98, 172), (104, 162), (110, 156), (124, 156), (130, 164), (140, 168), (152, 170), (157, 180), (156, 190), (148, 197), (124, 198), (104, 194), (98, 186)],          # standing shoe
]
# The eyes: taken a little wide, so the metal around them comes too and no drawn
# line shows beside the reference's.
REFERENCE_EYES = [
    [(64, 66), (67, 58), (74, 54), (81, 57), (86, 65), (89, 76), (88, 86), (84, 92), (78, 91), (71, 85), (66, 76)],                              # left eye
    [(95, 52), (99, 45), (105, 43), (111, 46), (116, 56), (117, 68), (116, 76), (97, 76), (96, 64)],                                         # right eye, above the nose
]
RIGHT_EYE_FLOOR = 77          # the reference's large nose began below this row


def reference_parts():
    """The reference's gloves and shoes on a canvas of this sheet's size."""
    ref = Image.open(glob.glob(REFERENCE)[0]).convert("RGBA")
    mask = Image.new("L", ref.size, 0)
    for outline in REFERENCE_PARTS:
        ImageDraw.Draw(mask).polygon(outline, fill=255)
    eyes = Image.new("L", ref.size, 0)
    for outline in REFERENCE_EYES:
        ImageDraw.Draw(eyes).polygon(outline, fill=255)
    eyes = eyes.filter(ImageFilter.MaxFilter(7))
    ImageDraw.Draw(eyes).rectangle([92, RIGHT_EYE_FLOOR, 122, 96], fill=0)
    mask.paste(255, (0, 0), eyes)
    lifted = Image.composite(ref, Image.new("RGBA", ref.size, (0, 0, 0, 0)), mask)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(lifted, (0, int(RISE)))
    return out


POSES = {
    # legs: (limb points ending at the ankle, shoe turn, facing); arms: (limb points ending at the wrist, hand)
    "saludo": {
        "legs": [([(80, 138), (74, 150), (66, 160)], 34.0, -1), ([(118, 140), (120, 150), (118, 163)], 0.0, 1)],
        "far": ([(148, 93), (170, 86), (180, 98), (172, 116)], ("fist", 165, 134, 12)),
        "near": ([(36, 98), (8, 102), (0, 88), (12, 74)], ("hat", 22, 54)),
        "hat": (64.5, 29.5, -24.0),
    },
    "quieto": {
        "legs": [([(80, 138), (77, 153), (76, 167)], 0.0, -1), ([(116, 140), (120, 153), (121, 167)], 0.0, 1)],
        "far": ([(149, 94), (177, 106), (166, 124)], ("fist", 161, 140, 20)),
        "near": ([(35, 100), (12, 112), (29, 126)], ("fist", 35, 142, -20)),
        "hat": (86.0, 20.0, -7.0),
    },
    "paso": {
        "legs": [([(80, 138), (63, 146), (58, 162)], -10.0, -1), ([(118, 140), (130, 152), (143, 160)], -34.0, 1)],
        "far": ([(149, 90), (177, 78), (176, 60)], ("fist", 176, 43, 180)),
        "near": ([(35, 100), (10, 104), (14, 124)], ("fist", 15, 140, 0)),
        "hat": (84.0, 20.0, -9.0),
    },
}


def _drop(points):
    return [(x, y + RISE) for x, y in points]


VARIANTS = {"clasica": "canotier", "gastada": "gorra", "caballero": "bombin"}


def _gentleman(s, cx, cy, clip):
    """A monocle on its chain and a waxed moustache."""
    dx, dy, rx, ry, turn = EYES[1]
    ex, ey = cx + dx, cy + dy
    ring = s.oval(ex, ey, rx + 3.6, ry + 3.6, turn) - s.oval(ex, ey, rx + 1.6, ry + 1.6, turn)
    s.part(ring & clip, [B3, C2, C4], mode="slab", cuts=(0.3, 0.7), clip=clip)
    for step in range(12):                                                                 # the chain
        t = step / 11.0
        x, y = s.bezier([(ex + rx + 2, ey + ry - 2), (ex + rx + 12, ey + ry + 22), (ex + rx + 6, ey + ry + 40)], t)
        if (int(round(x)), int(round(y))) in clip:
            s.dots([(int(round(x)), int(round(y)))], C3 if step % 2 else B1)
    for points in ([(cx + 6, cy + 12), (cx - 8, cy + 19), (cx - 19, cy + 8)], [(cx + 10, cy + 12), (cx + 24, cy + 18), (cx + 33, cy + 6)]):
        whisker = s.hose(points, 5.6, 1.6) & clip
        s.part(whisker, [K1, K2, D1], mode="slab", weight=1, clip=clip)
        s.dots(s.hose([(x - 0.8, y - 1.2) for x, y in points], 1.0) & whisker, D2)


def figure(pose="saludo", kind="alegre", back=False, variant="clasica", lifted=False):
    s = Sprite()
    data = POSES[pose]
    cx, cy = 95.0, 81.0 + RISE
    for points, sturn, facing in data["legs"]:
        leg = _drop(points)
        ax, ay = leg[-1]
        if not lifted:
            shoe(s, ax, ay, sturn, facing)
        limb(s, leg)                                                                       # the leg goes down into the shoe's mouth
        if not lifted:
            ankle(s, ax, ay, sturn, facing)
    points, hand = data["far"]
    limb(s, _drop(points))
    field = coin(s, cx, cy, back, worn=variant == "gastada")
    if back:
        reverse(s, cx, cy, field)
    else:
        laurel(s, [(cx - 26, cy + 39), (cx - 37, cy + 15), (cx - 40, cy - 9)], field, -1)
        laurel(s, [(cx + 33, cy + 31), (cx + 35, cy + 5), (cx + 30, cy - 23)], field, 1)
        if variant == "gastada":
            wear(s, cx, cy, field)
        face(s, cx, cy, field, kind, heavy=variant == "gastada")
        legend(s, cx, cy, field)
        if variant == "caballero":
            _gentleman(s, cx, cy, field)
    if variant == "caballero":                                                             # a cane in the far hand
        s.part(s.hose([(hand[1] + 1, hand[2] + RISE - 20), (hand[1] + 9, GROUND - 3)], 3.6), [D3, B1, B2], mode="slab")
        s.part(s.oval(hand[1] + 0.5, hand[2] + RISE - 22, 4.2, 4.2), [B3, C2, C4], mode="ball")
    if not lifted:
        fist(s, hand[1], hand[2] + RISE, hand[3], thumb=-1)
    hx, hy, hturn = data["hat"]
    s.darken(s.oval(hx + 4.0, hy + RISE + 7.0, 37.0, 7.5, hturn) & s.oval(cx, cy, 55.0, 61.0, -6))   # the brim's shadow on the coin
    hat(s, hx, hy + RISE, hturn, VARIANTS[variant])
    points, hand = data["near"]
    limb(s, _drop(points))                                                                 # this arm starts on the coin's edge
    if lifted:
        s.overlay = reference_parts()
    elif hand[0] == "hat":
        hat_hand(s, hand[1], hand[2] + RISE)
    else:
        fist(s, hand[1], hand[2] + RISE, hand[3], thumb=1)
    s.finish(shadow=(96.0, 62.0))
    return s


def head(kind):
    """The coin and its hat alone, for the sheet of faces."""
    s = Sprite(150, 152)
    cx, cy = 80.0, 84.0
    field = coin(s, cx, cy)
    laurel(s, [(cx - 26, cy + 39), (cx - 37, cy + 15), (cx - 40, cy - 9)], field, -1)
    laurel(s, [(cx + 33, cy + 31), (cx + 35, cy + 5), (cx + 30, cy - 23)], field, 1)
    legend(s, cx, cy, field)
    face(s, cx, cy, field, kind)
    hat(s, 52.0, 30.0, -18.0)
    s.finish()
    return s


# --- sheet -------------------------------------------------------------------------------------

def _tile(sprite_image, zoom, label):
    tile = Image.new("RGBA", (sprite_image.width * zoom + 20, sprite_image.height * zoom + 40), BACKDROP)
    panel = Image.new("RGBA", sprite_image.size, PANEL)
    panel.alpha_composite(sprite_image)
    tile.alpha_composite(panel.resize((sprite_image.width * zoom, sprite_image.height * zoom), Image.NEAREST), (10, 8))
    ImageDraw.Draw(tile).text((10, sprite_image.height * zoom + 16), label, fill=LABEL)
    return tile


def _row(tiles, title):
    row = Image.new("RGBA", (sum(tile.width for tile in tiles) + 12, max(tile.height for tile in tiles) + 24), BACKDROP)
    ImageDraw.Draw(row).text((10, 6), title, fill=LABEL)
    x = 6
    for tile in tiles:
        row.alpha_composite(tile, (x, 20))
        x += tile.width
    return row


def studies():
    """Close-ups of what was redrawn: the two gloves, a shoe with its ankle."""
    s1 = Sprite(64, 62)
    limb(s1, [(32.0, 0.0), (32.0, 12.0)])
    fist(s1, 32.0, 34.0, 0.0, thumb=-1)
    s1.finish()
    s2 = Sprite(64, 62)
    s2.part(s2.oval(46.0, 14.0, 30.0, 6.0, -18), HAT, mode="slab", cuts=(0.12, 0.42, 0.72, 0.92), weight=2)
    limb(s2, [(8.0, 62.0), (14.0, 50.0)])
    hat_hand(s2, 26.0, 32.0)
    s2.finish()
    s3 = Sprite(72, 62)
    shoe(s3, 22.0, 30.0, 0.0, 1)
    limb(s3, [(18.0, 0.0), (20.0, 14.0), (22.0, 30.0)])
    ankle(s3, 22.0, 30.0, 0.0, 1)
    s3.finish()
    return [("GUANTE: PUNO", s1), ("GUANTE: MANO EN EL ALA", s2), ("ZAPATO Y TOBILLO", s3)]


def build():
    ref = Image.open(glob.glob(REFERENCE)[0]).convert("RGBA")
    reference = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    reference.alpha_composite(ref, (0, int(RISE)))
    rows = [_row([_tile(figure("saludo", lifted=True).image(), 4, "PROTOTIPO: manos y zapatos de moneda1"), _tile(reference, 4, "moneda1 (referencia)")],
                 "LA PESETA  %d x %d px, colores de moneda1" % (W, H))]
    sheet = Image.new("RGBA", (max(row.width for row in rows), sum(row.height for row in rows)), BACKDROP)
    y = 0
    for row in rows:
        sheet.alpha_composite(row, (0, y))
        y += row.height
    return sheet


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    build().save(OUT)
    print("wrote %s" % os.path.relpath(OUT))
