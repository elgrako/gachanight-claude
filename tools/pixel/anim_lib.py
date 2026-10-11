"""Shared drawing helpers for the GachaNight animated sprite sheets.

Everything is drawn on sparse pixel layers (dict of (x, y) -> RGB) so parts can
be posed, stamped back-to-front with an automatic 1 px outline, rotated and
finally rendered to RGBA images with alpha 0 or 255 only.
"""
import math

from PIL import Image


def rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# --- Contract palette -------------------------------------------------------
INK = rgb("#1d2a44")
DARK = rgb("#2b2b33")
CREAM = rgb("#f4ecd8")
WALL_CREAM = rgb("#efe4c8")
CORAL = rgb("#ef7a6d")
MINT = rgb("#7ec8a4")
MUSTARD = rgb("#e3b44c")
TEAL = rgb("#4f9ea3")
BATH_MINT = rgb("#c9e6dc")
STAFF_TAN = rgb("#dccaa6")
WOOD = rgb("#a9825a")
WHITE = rgb("#ffffff")

# --- Small extension: one highlight and one shadow per colour ----------------
CORAL_HI = rgb("#f7a596")
CORAL_SH = rgb("#c9585a")
CORAL_DK = rgb("#96404e")
MINT_HI = rgb("#b4e3c8")
MINT_SH = rgb("#57a487")
MUSTARD_HI = rgb("#f6dc8a")
MUSTARD_SH = rgb("#b5852f")
TEAL_HI = rgb("#86c6c6")
TEAL_SH = rgb("#387479")
CREAM_SH = rgb("#cdc3ab")
SKIN = rgb("#f3cba3")
SKIN_SH = rgb("#d59c7b")
DENIM = rgb("#4a6794")
DENIM_SH = rgb("#364c74")
HAIR = rgb("#5a3d3a")
HAIR_HI = rgb("#80574a")
GOLD_HI = rgb("#fff3b0")
SCREEN_BG = rgb("#1f4d3c")
SCREEN_BAND = rgb("#2f6f55")
TUBE_OFF = rgb("#9fb3b3")
GREY = (128, 128, 128)

# Colour used for an outline pixel that falls on top of an already drawn part
# (an inner line), so that inner lines are softer than the ink silhouette.
SHADE = {
    CORAL: CORAL_SH, CORAL_HI: CORAL_SH, CORAL_SH: CORAL_DK,
    MINT: MINT_SH, MINT_HI: MINT_SH,
    MUSTARD: MUSTARD_SH, MUSTARD_HI: MUSTARD_SH,
    TEAL: TEAL_SH, TEAL_HI: TEAL_SH,
    CREAM: CREAM_SH, WHITE: CREAM_SH,
    SKIN: SKIN_SH,
    DENIM: DENIM_SH,
    HAIR_HI: HAIR,
}

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def rnd(v):
    """Round half up (Python's round() is banker's rounding)."""
    return int(math.floor(v + 0.5))


def polar(p, angle_deg, length):
    """Point at `length` from p; angle 0 = straight down, positive = forward (+x)."""
    a = math.radians(angle_deg)
    return (p[0] + math.sin(a) * length, p[1] + math.cos(a) * length)


def ipt(p):
    return (rnd(p[0]), rnd(p[1]))


class Layer:
    def __init__(self):
        self.px = {}

    # -- primitives ---------------------------------------------------------
    def set(self, x, y, c):
        self.px[(int(x), int(y))] = c

    def pts(self, points, c, ox=0, oy=0):
        for x, y in points:
            self.px[(x + ox, y + oy)] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                self.px[(x, y)] = c

    def limb(self, p0, p1, w, c):
        """Constant-volume thick segment: runs of `w` pixels across the major axis."""
        x0, y0 = ipt(p0)
        x1, y1 = ipt(p1)
        dx, dy = x1 - x0, y1 - y0
        lo = -(w // 2)
        if dx == 0 and dy == 0:
            for i in range(w):
                self.px[(x0 + lo + i, y0)] = c
            return
        if abs(dy) >= abs(dx):
            step = 1 if dy > 0 else -1
            for y in range(y0, y1 + step, step):
                x = rnd(x0 + dx * (y - y0) / dy)
                for i in range(w):
                    self.px[(x + lo + i, y)] = c
        else:
            step = 1 if dx > 0 else -1
            for x in range(x0, x1 + step, step):
                y = rnd(y0 + dy * (x - x0) / dx)
                for i in range(w):
                    self.px[(x, y + lo + i)] = c

    def disc(self, cx, cy, r, c):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.px[(x, y)] = c

    def test(self, box, fn, c):
        """Set every pixel in box (x0, y0, x1, y1 inclusive) where fn(x, y) is true."""
        x0, y0, x1, y1 = box
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if fn(x, y):
                    self.px[(x, y)] = c

    # -- composition --------------------------------------------------------
    def merge(self, other, dx=0, dy=0):
        for (x, y), c in other.px.items():
            self.px[(x + dx, y + dy)] = c
        return self

    def stamp(self, other, ink=INK, soft=True):
        """Paste `other` on top with a 1 px outline around it.

        Outline pixels landing on empty space are ink. Where the new part
        overlaps an existing one, only its right and bottom edges draw a soft
        inner line in the covered part's shade colour (a drop shadow away from
        the top-left light), which keeps overlapping limbs clean.
        """
        for (x, y) in other.px:
            for ax, ay in N4:
                q = (x + ax, y + ay)
                if q in other.px:
                    continue
                under = self.px.get(q)
                if under is None or not soft:
                    self.px[q] = ink
                elif under != ink and (ax, ay) in ((1, 0), (0, 1)):
                    self.px[q] = SHADE.get(under, ink)
        self.px.update(other.px)
        return self

    def outlined(self, ink=INK):
        out = Layer()
        out.stamp(self, ink=ink)
        return out

    def shifted(self, dx, dy):
        out = Layer()
        for (x, y), c in self.px.items():
            out.px[(x + dx, y + dy)] = c
        return out

    def rot_ccw(self, w):
        """Rotate 90 degrees counter-clockwise: +x (forward) becomes up."""
        out = Layer()
        for (x, y), c in self.px.items():
            out.px[(y, w - 1 - x)] = c
        return out

    def bbox(self):
        xs = [p[0] for p in self.px]
        ys = [p[1] for p in self.px]
        return min(xs), min(ys), max(xs), max(ys)

    def to_image(self, w, h, strict=True, name=""):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for (x, y), c in self.px.items():
            if 0 <= x < w and 0 <= y < h:
                img.putpixel((x, y), (c[0], c[1], c[2], 255))
            elif strict:
                raise ValueError("%s: pixel (%d, %d) outside %dx%d frame" % (name, x, y, w, h))
        return img


def glyph(rows, legend, ox=0, oy=0, layer=None):
    """Build a layer from text rows; legend maps characters to colours."""
    layer = layer or Layer()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in legend:
                layer.px[(ox + x, oy + y)] = legend[ch]
    return layer


def strip(frames):
    w, h = frames[0].size
    sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * w, 0))
    return sheet


def contact_sheet(frames, scale=4, gap=2):
    w, h = frames[0].size
    n = len(frames)
    sheet = Image.new("RGBA", (n * w * scale + (n + 1) * gap, h * scale + 2 * gap), (96, 96, 96, 255))
    for i, f in enumerate(frames):
        cell = Image.new("RGBA", (w, h), GREY + (255,))
        cell.alpha_composite(f)
        cell = cell.resize((w * scale, h * scale), Image.NEAREST)
        sheet.paste(cell, (gap + i * (w * scale + gap), gap))
    return sheet.convert("RGB")


def save_gif(frames, path, fps, loop, scale=6):
    w, h = frames[0].size
    out = []
    for f in frames:
        cell = Image.new("RGBA", (w, h), GREY + (255,))
        cell.alpha_composite(f)
        out.append(cell.resize((w * scale, h * scale), Image.NEAREST).convert("P", palette=Image.ADAPTIVE, colors=64))
    ms = max(20, int(round(1000.0 / fps / 10.0)) * 10)
    durations = [ms] * len(out)
    if not loop:
        durations[-1] = 900  # hold the last frame so one-shots are readable in review
    out[0].save(path, save_all=True, append_images=out[1:], duration=durations, loop=0, disposal=2)
