"""The protagonist, built from the owner's own picture `diseños/moneda/moneda personaje.png`
(formerly `diseños/moneda1.png`). The walk and the run are built here (the
owner turned down the generator walk of build_peseta_walk.py on 2026-10-15).

The picture is taken apart into the pieces a cartoon cut-out needs (the coin
with its hat, the two gloves, the two shoes), its face is given a few more
expressions, and the pieces are put back together in other poses with rubber
hose limbs drawn between them. The result is written the way the game reads
animations: one horizontal strip per animation (and one more facing left, in
which the 1 is not mirrored) and an `anims.json` manifest.

    python tools/pixel/build_peseta.py

writes assets/sprites/peseta/ (strips, manifest, the loose pieces under
parts/) and a contact sheet, tools/pixel/previews/peseta_sheet.png.

scripts/world/player.gd plays these strips. Frames are at the picture's own
resolution (232 x 222) and the game shows them at a third of that, so one
pixel of the picture is one pixel of a 1080p screen.
"""
import glob
import json
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import proto_peseta as P

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "assets", "sprites", "peseta")
SHEET = os.path.join(HERE, "previews", "peseta_sheet.png")

# A frame: the picture's 185 x 202 with room for arms and legs to swing. The
# feet stand on the bottom rows; the figure is centred.
FW, FH = 232, 222
OX, OY = 24, 22

LINE = (25, 24, 21, 255)          # the picture's own line and field colours
FIELD = (178, 157, 118, 255)
BRIM = (42, 39, 34, 255)
WHITE = (227, 217, 198, 255)
MOUTH = (14, 13, 12, 255)
TONGUE = (138, 119, 90, 255)

# Outlines of the pieces, in the picture's pixel coordinates, and the point
# of each where a limb goes in.
GLOVE_HAT = [(1, 52), (8, 40), (18, 33), (32, 33), (41, 38), (42, 46), (34, 52), (32, 62), (26, 72), (16, 78), (4, 74), (1, 64)]
GLOVE_FIST = [(145, 124), (150, 116), (162, 111), (176, 112), (184, 118), (184, 134), (180, 146), (166, 149), (150, 144), (145, 134)]
SHOE_KICK = [(17, 160), (20, 148), (32, 142), (46, 143), (54, 150), (60, 154), (70, 156), (74, 164), (73, 174), (68, 180), (68, 196), (60, 201), (46, 200), (30, 192), (20, 178)]
SHOE_FLAT = [(98, 172), (104, 162), (110, 156), (124, 156), (130, 164), (140, 168), (152, 170), (157, 180), (156, 190), (148, 197), (124, 198), (104, 194), (98, 186)]
HAT = [(40, 36), (30, 25), (28, 16), (70, -2), (82, 11), (84, 22), (98, 8), (103, 16), (101, 24), (82, 37), (58, 48), (44, 54), (40, 52)]
PIVOTS = {"glove_hat": (12, 76), "glove_fist": (172, 114), "shoe_kick": (65, 158), "shoe_flat": (118, 158)}
SHOULDER_NEAR, SHOULDER_FAR = (36.0, 98.0), (149.0, 92.0)
HIP_FAR, HIP_NEAR = (74.0, 126.0), (124.0, 128.0)          # behind the coin; the legs come out under its edge

# The face, for redrawing it.
EYE_LEFT = [(64, 66), (67, 58), (74, 54), (81, 57), (86, 65), (89, 76), (88, 86), (84, 92), (78, 91), (71, 85), (66, 76)]
EYE_RIGHT = [(95, 52), (99, 45), (105, 43), (111, 46), (116, 56), (117, 68), (116, 76), (97, 76), (96, 64)]
NOSE = (91, 75, 118, 96)
MOUTH_AREA = [(66, 88), (78, 92), (103, 96), (103, 104), (101, 112), (92, 117), (80, 113), (72, 104), (66, 96)]
BROW_LEFT = [(61, 51), (69, 46.5), (79, 50)]
BROW_RIGHT = [(91, 43), (99, 37), (108, 40)]
FACES = ["normal", "parpadeo", "feliz", "sorpresa", "triste", "enfado"]
LEGEND = [(74, 120), (100, 119), (116, 118), (125, 115), (128, 127), (121, 132), (79, 135), (73, 128)]     # the word PESETA
DIGIT_BOX = (103, 99, 117, 120)                                                                           # the 1


def bezier(points, t):
    pts = list(points)
    while len(pts) > 1:
        pts = [(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t) for i in range(len(pts) - 1)]
    return pts[0]


def stroke(draw, points, width, color):
    """A round-ended line through control points, in the picture's heavy hand."""
    for step in range(81):
        x, y = bezier(points, step / 80.0)
        r = width / 2.0
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)


def _luma(color):
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]


def _struck(color):
    """True for the dark khaki of lettering struck into the field (not the
    field itself, not the black line)."""
    return color[3] > 128 and 70.0 < _luma(color) < _luma(FIELD) - 8.0


def without_legend(image):
    """The picture with the word PESETA smoothed out of the metal. The owner
    asked for it to go; the 1 stays."""
    out = image.copy()
    mask = polygon_mask(out.size, LEGEND).load()
    data = out.load()
    for y in range(out.height):
        for x in range(out.width):
            if mask[x, y] and _struck(data[x, y]):
                data[x, y] = FIELD
    return out


def polygon_mask(size, outline):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(outline, fill=255)
    return mask


# --- taking the picture apart ------------------------------------------------------------

def take(ref, outline, pivot):
    """One piece of the picture and where its pivot lies inside it."""
    mask = polygon_mask(ref.size, outline)
    piece = Image.composite(ref, Image.new("RGBA", ref.size, (0, 0, 0, 0)), mask)
    box = piece.getbbox()
    return piece.crop(box), (pivot[0] - box[0], pivot[1] - box[1])


def take_body(ref):
    """The coin with its hat and nothing else: gloves and shoes are cut out,
    and the limbs, being thin, are worn away by shrinking and regrowing what
    is left. The end of the brim that the glove covered is drawn in."""
    alpha = ref.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    solid = alpha.copy()
    for outline in (GLOVE_HAT, GLOVE_FIST, SHOE_KICK, SHOE_FLAT):
        ImageDraw.Draw(solid).polygon(outline, fill=0)
    thick = solid.filter(ImageFilter.MinFilter(13)).filter(ImageFilter.MaxFilter(13))
    keep = Image.new("L", ref.size, 0)
    keep.paste(255, (0, 0), thick)
    keep.paste(255, (0, 0), polygon_mask(ref.size, HAT))
    ImageDraw.Draw(keep).polygon(GLOVE_HAT, fill=0)
    keep = Image.composite(keep, Image.new("L", ref.size, 0), alpha)
    body = Image.composite(ref, Image.new("RGBA", ref.size, (0, 0, 0, 0)), keep)
    draw = ImageDraw.Draw(body)
    draw.polygon([(45, 34), (37, 37), (31, 42), (28, 47), (31, 51), (38, 54), (46, 54)], fill=LINE)      # the brim's left end, which the glove hid
    draw.polygon([(45, 37), (38, 40), (33, 44), (31, 47), (33, 49), (39, 51), (46, 51)], fill=BRIM)
    return body


# --- more faces for the same coin ------------------------------------------------------------

def _erase(body, mask):
    body.paste(FIELD, (0, 0), mask)


def _eye_masks(size):
    nose = Image.new("L", size, 0)
    ImageDraw.Draw(nose).ellipse(NOSE, fill=255)
    both = Image.new("L", size, 0)
    for outline in (EYE_LEFT, EYE_RIGHT):
        ImageDraw.Draw(both).polygon(outline, fill=255)
    both = both.filter(ImageFilter.MaxFilter(7))
    both.paste(0, (0, 0), nose)
    return both


def _brow_mask(size, points):
    mask = Image.new("L", size, 0)
    stroke(ImageDraw.Draw(mask), points, 6.0, 255)
    return mask


def _lid(draw, outline, inner_drop, outer_drop, left):
    """A slanted upper lid over one of the picture's eyes."""
    xs = [x for x, _y in outline]
    ys = [y for _x, y in outline]
    x0, x1, top = min(xs) - 2, max(xs) + 2, min(ys) - 3
    a, b = (outer_drop, inner_drop) if left else (inner_drop, outer_drop)
    lid = Image.new("L", draw.im.size, 0)
    ImageDraw.Draw(lid).polygon([(x0, top), (x1, top), (x1, top + b), (x0, top + a)], fill=255)
    eye = Image.new("L", draw.im.size, 0)
    ImageDraw.Draw(eye).polygon(outline, fill=255)
    return Image.composite(lid, Image.new("L", lid.size, 0), eye), [(x0 + 1, top + a), (x1 - 1, top + b)]


def face(body, kind):
    """The body with another expression, redrawn over the picture's face in
    its own line. "normal" is the picture untouched."""
    out = body.copy()
    if kind == "normal":
        return out
    draw = ImageDraw.Draw(out)
    size = out.size
    if kind in ("parpadeo", "feliz"):
        _erase(out, _eye_masks(size))
        bend = 1.0 if kind == "parpadeo" else -1.0                                           # shut, or squeezed with joy
        for cx, cy, half in ((76.5, 74.0, 10.0), (106.0, 62.0, 9.0)):
            stroke(draw, [(cx - half, cy - 3.0 * bend), (cx, cy + 9.0 * bend), (cx + half, cy - 3.0 * bend)], 3.0, LINE)
        if kind == "parpadeo":
            return out
    if kind in ("sorpresa", "triste", "enfado"):
        _erase(out, _brow_mask(size, BROW_LEFT))
        _erase(out, _brow_mask(size, BROW_RIGHT))
        lift, tilt = {"sorpresa": (-4.0, 0.0), "triste": (1.0, 5.0), "enfado": (5.0, -5.0)}[kind]
        left = [(BROW_LEFT[0][0], BROW_LEFT[0][1] + lift + tilt), (BROW_LEFT[1][0], BROW_LEFT[1][1] + lift), (BROW_LEFT[2][0], BROW_LEFT[2][1] + lift - tilt)]
        right = [(BROW_RIGHT[0][0], BROW_RIGHT[0][1] + lift - tilt), (BROW_RIGHT[1][0], BROW_RIGHT[1][1] + lift), (BROW_RIGHT[2][0], BROW_RIGHT[2][1] + lift + tilt)]
        stroke(draw, left, 2.2, LINE)
        stroke(draw, right, 2.2, LINE)
    if kind in ("triste", "enfado"):
        drops = (3.0, 13.0) if kind == "triste" else (15.0, 4.0)
        for outline, is_left in ((EYE_LEFT, True), (EYE_RIGHT, False)):
            lid, edge = _lid(draw, outline, drops[0], drops[1], is_left)
            _erase(out, lid)
            stroke(draw, edge, 2.4, LINE)
    if kind in ("sorpresa", "triste", "enfado"):
        _erase(out, polygon_mask(size, MOUTH_AREA))
        if kind == "sorpresa":
            draw.ellipse([80, 96, 95, 115], fill=LINE)
            draw.ellipse([82, 98, 93, 113], fill=MOUTH)
            draw.ellipse([84, 106, 91, 112], fill=TONGUE)
        elif kind == "triste":
            stroke(draw, [(75, 110), (87, 100), (100, 108)], 3.0, LINE)
        else:
            draw.polygon([(73, 99), (101, 98), (99, 111), (75, 112)], fill=LINE)
            draw.polygon([(75, 101), (99, 100), (97, 109), (77, 110)], fill=WHITE)
            for x in (81, 87, 93):
                draw.line([(x, 101), (x, 110)], fill=LINE)
            draw.line([(76, 105), (98, 105)], fill=LINE)
    return out


# --- the hat comes off ----------------------------------------------------------------------

HAT_EDGE = [(44, 53), (58, 47), (72, 40), (86, 32), (99, 21)]     # the lower edge of the brim, where it lies on the coin
COIN_SHAPE = (92.0, 81.5, 60.0, 63.0)                            # centre and radii of the whole coin


def split_hat(body):
    """Takes the hat off the coin, so it can lag and bounce on its own (the
    follow-through rubber hose lives on). The strip of coin the hat covered
    is filled by carrying the metal just below the brim upwards: only a
    sliver of it ever shows."""
    size = body.size
    region = polygon_mask(size, HAT)
    ImageDraw.Draw(region).polygon([(38, 54)] + HAT_EDGE + [(106, 21), (106, 80), (38, 80)], fill=0)
    data = body.load()
    mask = region.load()
    for _round in range(2):                                              # the brim's own dark line belongs to the hat
        found = [(x, y) for y in range(1, 60) for x in range(1, 104)
                 if not mask[x, y] and data[x, y][3] > 128 and _luma(data[x, y]) < 75 and (mask[x, y - 1] or mask[x - 1, y] or mask[x + 1, y])]
        for point in found:
            mask[point] = 255
    hat = Image.composite(body, Image.new("RGBA", size, (0, 0, 0, 0)), region)
    coin = body.copy()
    paint = coin.load()
    cx, cy, rx, ry = COIN_SHAPE
    for x in range(size[0]):
        below = None
        for y in range(size[1] - 1, -1, -1):
            if not mask[x, y]:
                if paint[x, y][3] > 128:
                    below = paint[x, y]
                continue
            inside = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0
            paint[x, y] = below if (inside and below is not None) else (0, 0, 0, 0)
    return coin, hat


# --- two more gloves, drawn to go with the picture's fist ----------------------------------------

def draw_glove(kind):
    """An open hand or a pointing hand in the picture's colours and line:
    three fingers and a thumb, one white shape, a rolled cuff at the wrist.
    Drawn for an arm coming straight down into it."""
    s = P.Sprite(72, 76)
    cx, cy = 36.0, 30.0
    roll = s.oval(cx, cy - 15.0, 10.5, 5.6)
    back = s.oval(cx, cy, 13.5, 12.5)
    if kind == "glove_open":
        fingers = [s.hose([(cx + dx * 0.7, cy + 6.0), (cx + dx * 1.3, cy + 22.0 - abs(dx) * 0.3)], 7.8, 6.6) for dx in (-7.5, 0.0, 7.5)]
        thumb = s.hose([(cx - 10.0, cy - 2.0), (cx - 19.0, cy + 2.0), (cx - 22.0, cy + 9.0)], 7.4, 6.0)
    else:
        fingers = [s.hose([(cx - 5.5, cy + 6.0), (cx - 7.0, cy + 25.0)], 7.8, 6.6), s.oval(cx + 2.5, cy + 10.5, 4.9, 5.5), s.oval(cx + 8.5, cy + 9.5, 4.6, 5.2)]
        thumb = s.hose([(cx - 13.0, cy - 4.0), (cx - 14.5, cy + 4.0), (cx - 9.0, cy + 9.0)], 7.2, 6.0)
    glove = back | roll | thumb
    for finger in fingers:
        glove |= finger
    s.part(glove, P.WHITE, mode="ball", cuts=P.GLOVE_CUTS, weight=1, spot=0.42)
    P._inside_line(s, roll, glove - roll)
    s.dots(s.hose([(cx - 6.5, cy - 14.0), (cx, cy - 12.0), (cx + 6.5, cy - 14.0)], 1.0) & roll, P.C2)
    for finger in fingers:
        P._inside_line(s, finger, glove - roll)
    P._inside_line(s, thumb, glove - roll)
    for dx in (-4.5, 0.5, 5.5):                                                            # the three lines on the back
        s.dots(s.hose([(cx + dx, cy - 7.0), (cx + dx + 0.4, cy - 1.5)], 1.0) & back - thumb, P.B1)
    s.finish()
    image = s.image()
    box = image.getbbox()
    return image.crop(box), (int(cx) - box[0], int(cy - 19.0) - box[1])


# --- putting it back together -------------------------------------------------------------

# How the picture's pieces lie. Its fist hangs from the cuff down and to the
# left, not straight down, so an arm arriving straight down needs it turned
# back by this much; its shoe is drawn toe down, as a foot pointing towards
# us looks, and stands level on the floor only when turned back by this much.
FIST_LEAN = 32.0
SHOE_LEAN = 11.0


class Kit:
    def __init__(self):
        ref = Image.open(glob.glob(os.path.join(ROOT, "dise*", "moneda", "moneda personaje.png"))[0]).convert("RGBA")
        ref = without_legend(ref)
        self.ref = ref
        data = ref.load()
        self.digit = [(x, y, data[x, y]) for y in range(DIGIT_BOX[1], DIGIT_BOX[3]) for x in range(DIGIT_BOX[0], DIGIT_BOX[2]) if _struck(data[x, y])]
        self.pieces = {name: take(ref, outline, PIVOTS[name]) for name, outline in
                       (("glove_hat", GLOVE_HAT), ("glove_fist", GLOVE_FIST), ("shoe_kick", SHOE_KICK), ("shoe_flat", SHOE_FLAT))}
        for kind in ("glove_open", "glove_point"):
            self.pieces[kind] = draw_glove(kind)
        coin, self.hat = split_hat(take_body(ref))
        self.coins = {kind: face(coin, kind) for kind in FACES}

    def stamp(self, frame, name, at, mirror=False, turn=0.0):
        """Sets a piece into the frame with its pivot at `at` (picture
        coordinates), optionally mirrored and turned about the pivot."""
        image, (px, py) = self.pieces[name]
        if mirror:
            image, px = ImageOps.mirror(image), image.width - 1 - px
        if turn:
            reach_px = int(math.ceil(math.hypot(max(px, image.width - px), max(py, image.height - py)))) + 2
            padded = Image.new("RGBA", (reach_px * 2, reach_px * 2), (0, 0, 0, 0))
            padded.alpha_composite(image, (reach_px - px, reach_px - py))
            # Turned four times larger and reduced: the pixels keep their shape better.
            large = padded.resize((reach_px * 8, reach_px * 8), Image.NEAREST).rotate(-turn, resample=Image.NEAREST)
            image, px, py = large.resize((reach_px * 2, reach_px * 2), Image.NEAREST), reach_px, reach_px
        frame.alpha_composite(image, (int(round(at[0] - px)) + OX, int(round(at[1] - py)) + OY))


def hoses(limbs):
    """Rubber hose limbs as one layer: each a single black arc with a dull
    sheen and the picture's heavy contour."""
    layer = P.Sprite(FW, FH)
    for points in limbs:
        P.limb(layer, [(x + OX, y + OY) for x, y in points], 8.0)
    figure = set(layer.px)
    for point in layer.grow(figure, 1) - figure:
        layer.px[point] = P.LINE
    return layer.image()


def reach(start, end, bow, depth=3.0):
    """A limb from `start` to `end`: one soft bend of `bow` pixels to the
    side, carried a little way into the cuff or sock. Also returns the
    direction it arrives in."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = max(math.hypot(dx, dy), 1.0)
    ux, uy = dx / length, dy / length
    mid = ((start[0] + end[0]) / 2.0 - uy * bow, (start[1] + end[1]) / 2.0 + ux * bow)
    tip = (end[0] + ux * depth, end[1] + uy * depth)
    ax, ay = tip[0] - mid[0], tip[1] - mid[1]
    norm = max(math.hypot(ax, ay), 1.0)
    return [start, mid, tip], (ax / norm, ay / norm)


def turn_for(direction):
    """How far a piece drawn for a limb coming straight down must be turned
    (clockwise, in degrees) to meet a limb arriving along `direction`."""
    return math.degrees(math.atan2(-direction[0], direction[1]))


COIN_FOOT = (92.0, 143.0)        # the lowest point of the coin: squash and stretch hold it still


def pose(kit, face_kind="normal", lift=0.0, shift=0.0, squash=0.0, hat=(0.0, 0.0), near=None, far=None, feet=None):
    """One frame.

    `lift` raises the coin and `shift` moves it sideways; `squash` flattens it
    (negative stretches it) while keeping its volume and its lowest point;
    `hat` is how far the hat sits from its place on the coin. `near` and `far`
    are the wrists as (x, y, bow, glove); `feet` is [far foot, near foot] as
    (ankle x, y, shoe turn, knee bow, mirrored). Gloves and shoes turn to
    line up with their limbs."""
    near = near or REST_NEAR
    far = far or REST_FAR
    feet = feet or REST_FEET
    frame = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    drop = squash * 48.0                                                                    # the shoulders ride on the coin
    hips = ((HIP_FAR[0] + shift, HIP_FAR[1] - lift), (HIP_NEAR[0] + shift, HIP_NEAR[1] - lift))
    legs = [reach(hips[index], (feet[index][0], feet[index][1]), feet[index][3])[0] for index in (0, 1)]
    far_arm, far_way = reach((SHOULDER_FAR[0] + shift, SHOULDER_FAR[1] - lift + drop), (far[0], far[1]), far[2])
    near_arm, near_way = reach((SHOULDER_NEAR[0] + shift, SHOULDER_NEAR[1] - lift + drop), (near[0], near[1]), near[2])

    def shoe(index):
        mirrored = len(feet[index]) > 4 and feet[index][4]
        kit.stamp(frame, "shoe_flat", (feet[index][0], feet[index][1]), mirror=mirrored, turn=feet[index][2] + (SHOE_LEAN if mirrored else -SHOE_LEAN))

    def glove(hand, way, mirrored):
        lean = FIST_LEAN if hand[3] == "glove_fist" else 0.0
        kit.stamp(frame, hand[3], (hand[0], hand[1]), mirror=mirrored, turn=turn_for(way) + (lean if mirrored else -lean))
    frame.alpha_composite(hoses([legs[0]]))
    shoe(0)
    frame.alpha_composite(hoses([legs[1], far_arm]))
    shoe(1)
    glove(far, far_way, False)
    coin = kit.coins[face_kind]
    wide, tall = 1.0 + squash, 1.0 - squash
    if squash:
        coin = coin.resize((int(round(coin.width * wide)), int(round(coin.height * tall))), Image.NEAREST)
    left = OX + shift + COIN_FOOT[0] * (1.0 - wide)
    top = OY - lift + COIN_FOOT[1] * (1.0 - tall)
    frame.alpha_composite(coin, (int(round(left)), int(round(top))))
    frame.alpha_composite(kit.hat, (int(round(OX + shift + hat[0])), int(round(OY - lift + hat[1] + squash * 118.0))))
    frame.alpha_composite(hoses([near_arm]))
    glove(near, near_way, True)
    # Where the coin's 1 fell, for the frame drawn facing left.
    frame.info["digit"] = ([(int(round(left + x * wide)), int(round(top + y * tall))) for x, y, _color in kit.digit],
                           (int(round(left + DIGIT_BOX[0] * wide)), int(round(top + DIGIT_BOX[1] * tall))))
    return frame


def facing_left(kit, frame):
    """The same frame for walking left: mirrored, except the 1, which is
    struck the right way round where its mirror image fell."""
    spots, (ox, oy) = frame.info["digit"]
    out = ImageOps.mirror(frame)
    data = out.load()
    for x, y in spots:
        if 0 <= FW - 1 - x < FW and 0 <= y < FH:
            data[FW - 1 - x, y] = FIELD
    x0 = FW - (ox + DIGIT_BOX[2] - DIGIT_BOX[0])
    for x, y, color in kit.digit:
        px, py = x0 + (x - DIGIT_BOX[0]), oy + (y - DIGIT_BOX[1])
        if 0 <= px < FW and 0 <= py < FH:
            data[px, py] = color
    return out


# Standing at rest, and no "twins": the near fist sits on the hip with the
# elbow out while the far arm hangs; the far foot turns out, heel towards the
# other. The near leg is the shorter one and the far leg the longer, as the
# owner asked.
REST_NEAR = (46.0, 136.0, 14.0, "glove_fist")
REST_FAR = (157.0, 127.0, -6.0, "glove_fist")
HANG_NEAR = (31.0, 131.0, 6.0, "glove_fist")                 # the near arm when it swings instead
REST_FEET = [(70.0, 161.0, 0.0, 1.5, True), (124.0, 153.0, 0.0, -1.5, False)]


def _lag(values, amount=0.7):
    """How far a loose thing (the hat) sits behind a body that moves by
    `values` from frame to frame: it follows one frame late."""
    return [amount * (values[index] - values[index - 1]) for index in range(len(values))]


# --- animations -----------------------------------------------------------------------------

def anim_idle(kit):
    """Standing: the coin sinks and rises a little, the hat settling after
    it; one blink."""
    sinks = (0, 0, 1, 2, 2, 1, 0, 0)
    lag = _lag([-sink for sink in sinks])
    frames = []
    for index, sink in enumerate(sinks):
        frames.append(pose(kit, "parpadeo" if index == 5 else "normal", lift=-sink, squash=0.008 * sink, hat=(0.0, lag[index]),
                           near=(REST_NEAR[0], REST_NEAR[1] + sink * 0.5, REST_NEAR[2], REST_NEAR[3]), far=(REST_FAR[0], REST_FAR[1] + sink * 0.5, REST_FAR[2], REST_FAR[3])))
    return frames, 8, True


def _ease(t):
    return t * t * (3.0 - 2.0 * t)


def _step(phase, base_x, ground, stride=26.0, height=12.0, planted=0.5):
    """One foot at `phase` of the cycle, going to the right; 0 is the heel
    striking ahead of the body. While planted the foot is carried back under
    the body and at the end the heel peels up onto the toe; then it leaves
    the ground, swings forward with the hose bowed and comes down toe up."""
    phase %= 1.0
    if phase < planted:
        along = phase / planted
        x = base_x + stride * (1.0 - 2.0 * along)
        if along < 0.14:
            turn = -12.0                                                                   # just landed: toe still up
        elif along > 0.72:
            turn = 30.0 * (along - 0.72) / 0.28                                             # heel peels off the ground
        else:
            turn = 0.0
        return (x, ground - max(turn, 0.0) * 0.34, turn, -1.0)
    swing = (phase - planted) / (1.0 - planted)
    x = base_x + stride * (-1.0 + 2.0 * _ease(swing))
    y = ground - 6.0 - height * math.sin(math.pi * swing)
    turn = 30.0 * (1.0 - swing * 2.0) if swing < 0.5 else -14.0 * (swing - 0.5) * 2.0
    return (x, y, turn, 9.0)


def anim_walk(kit):
    """A plain walk to the right in eight frames, in place: contact, down,
    passing, up, for each foot. The coin squashes a touch as each foot lands
    and is lowest then, highest as a foot passes under it; each arm swings
    with the opposite leg, its curve trailing; the hat follows a beat late."""
    lifts = [3.0 * abs(math.sin(math.tau * index / 8.0)) for index in range(8)]
    lag = _lag(lifts)
    frames = []
    for index in range(8):
        phase = index / 8.0
        swing = math.cos(math.tau * phase)                                                  # +1 with the near foot forward
        drag = math.sin(math.tau * phase)                                                   # which way the arms are moving
        frames.append(pose(kit, lift=lifts[index], squash=0.025 if index % 4 == 0 else 0.0, hat=(0.0, lag[index]),
                           feet=[_step(phase + 0.5, 76.0, 161.0), _step(phase, 122.0, 153.0)],
                           near=(HANG_NEAR[0] - 11.0 * swing, HANG_NEAR[1] - 5.0 * abs(swing), 6.0 - 3.0 * drag, "glove_fist"),
                           far=(REST_FAR[0] + 11.0 * swing, REST_FAR[1] - 5.0 * abs(swing), -6.0 - 3.0 * drag, "glove_fist")))
    return frames, 10, True


def anim_run(kit):
    """A run in six frames: a longer stride, each foot on the ground for less
    than half the cycle so the coin is in the air between steps, the arms
    pumping high and bent, the coin leaning into it and the hat streaming
    behind."""
    lifts = [6.0 * abs(math.sin(math.tau * index / 6.0)) for index in range(6)]
    lag = _lag(lifts, 0.9)
    frames = []
    for index in range(6):
        phase = index / 6.0
        swing = math.cos(math.tau * phase)
        frames.append(pose(kit, lift=lifts[index] + 2.0, shift=3.0, squash=0.04 if index % 3 == 0 else -0.015, hat=(-3.0, lag[index]),
                           feet=[_step(phase + 0.5, 78.0, 161.0, 34.0, 20.0, 0.38), _step(phase, 124.0, 153.0, 34.0, 20.0, 0.38)],
                           near=(HANG_NEAR[0] - 5.0 - 11.0 * swing, HANG_NEAR[1] - 12.0 - 8.0 * abs(swing), 13.0, "glove_fist"),
                           far=(REST_FAR[0] + 16.0 * swing, REST_FAR[1] - 12.0 - 8.0 * abs(swing), -13.0, "glove_fist")))
    return frames, 14, True


def anim_use(kit):
    """A reach with the far hand, finger out: first a small pull back the
    other way, then the stretch, a hair too far, and the return."""
    frames = []
    for amount, lift, shift in ((-0.18, -1.0, -1.0), (0.5, 0.0, 1.0), (1.08, 1.0, 3.0), (1.0, 1.0, 2.0), (1.0, 1.0, 2.0), (0.4, 0.0, 1.0), (0.0, 0.0, 0.0)):
        frames.append(pose(kit, lift=lift, shift=shift, squash=0.03 if amount < 0 else 0.0,
                           far=(REST_FAR[0] + 16.0 * amount, REST_FAR[1] - 50.0 * amount, -4.0, "glove_point" if amount > 0.3 else "glove_fist")))
    return frames, 12, False


def anim_cheer(kit):
    """A crouch, a hop with both hands thrown open in the air and the eyes
    squeezed shut, the hat leaving the head at the top, and a settle."""
    steps = ((-3.0, 0.0, 0.05, 1.0), (4.0, 0.7, -0.04, 2.0), (11.0, 1.0, -0.02, -2.0), (8.0, 1.0, 0.0, -6.0), (2.0, 0.8, 0.0, -3.0), (-2.0, 0.3, 0.05, 2.0), (0.0, 0.0, 0.0, 0.0))
    frames = []
    for hop, up, squash, hat_y in steps:
        air = max(hop, 0.0)
        glove = "glove_open" if up > 0.5 else "glove_fist"
        frames.append(pose(kit, "feliz" if up > 0.5 else "normal", lift=hop, squash=squash, hat=(0.0, hat_y),
                           near=(HANG_NEAR[0] - 10.0 * up, HANG_NEAR[1] - 84.0 * up - hop, 6.0, glove), far=(REST_FAR[0] + 10.0 * up, REST_FAR[1] - 84.0 * up - hop, -6.0, glove),
                           feet=[(REST_FEET[0][0], REST_FEET[0][1] - air, -14.0 * up if air else 0.0, 1.5 if air else 5.0, True),
                                 (REST_FEET[1][0], REST_FEET[1][1] - air, 14.0 * up if air else 0.0, -1.5 if air else -5.0, False)]))
    return frames, 12, False


def anim_sleep(kit):
    """Asleep sitting down: the coin rests on the seat with its legs out in
    front, hands in its lap, the hat tipped over its eyes, breathing slowly."""
    frames = []
    for breath in (0.0, 1.0, 2.0, 1.0):
        frames.append(pose(kit, "parpadeo", lift=-21.0 - breath, squash=0.012 * breath, hat=(9.0, 15.0),
                           near=(58.0, 160.0, 10.0, "glove_fist"), far=(138.0, 156.0, -8.0, "glove_fist"),
                           feet=[(118.0, 166.0, -6.0, 4.0, False), (152.0, 160.0, -10.0, -3.0, False)]))
    return frames, 3, True


def anim_wave(kit):
    """The picture itself: the tip of the hat."""
    frame = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    frame.alpha_composite(kit.ref, (OX, OY))
    frame.info["digit"] = ([(OX + x, OY + y) for x, y, _color in kit.digit], (OX + DIGIT_BOX[0], OY + DIGIT_BOX[1]))
    return [frame, frame], 2, False


ANIMATIONS = [("peseta_idle", anim_idle), ("peseta_walk", anim_walk), ("peseta_run", anim_run), ("peseta_use", anim_use), ("peseta_cheer", anim_cheer),
              ("peseta_wave", anim_wave), ("peseta_sleep", anim_sleep)]


# --- output -------------------------------------------------------------------------------------

def build():
    kit = Kit()
    os.makedirs(os.path.join(OUT, "parts"), exist_ok=True)
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    for name, (image, _pivot) in kit.pieces.items():
        image.save(os.path.join(OUT, "parts", name + ".png"))
    for kind, image in kit.coins.items():
        image.save(os.path.join(OUT, "parts", "coin_%s.png" % kind))
    kit.hat.save(os.path.join(OUT, "parts", "hat.png"))
    with open(os.path.join(OUT, "parts", "pivots.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump({name: list(pivot) for name, (_image, pivot) in kit.pieces.items()}, handle, indent=2)
        handle.write("\n")
    manifest, rows = {}, []
    panel = (91, 86, 79, 255)
    for name, make in ANIMATIONS:
        frames, fps, loop = make(kit)
        strip = Image.new("RGBA", (FW * len(frames), FH), (0, 0, 0, 0))
        left = Image.new("RGBA", (FW * len(frames), FH), (0, 0, 0, 0))
        shown = Image.new("RGBA", (FW * len(frames), FH), panel)
        for index, frame in enumerate(frames):
            strip.alpha_composite(frame, (index * FW, 0))
            shown.alpha_composite(frame, (index * FW, 0))
            left.alpha_composite(facing_left(kit, frame), (index * FW, 0))
        strip.save(os.path.join(OUT, name + ".png"))
        left.save(os.path.join(OUT, name + "_left.png"))
        for suffix in ("", "_left"):
            manifest[name + suffix] = {"file": name + suffix + ".png", "frame_w": FW, "frame_h": FH, "frames": len(frames), "fps": fps, "loop": loop}
        rows.append(shown)
    with open(os.path.join(OUT, "anims.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    faces = Image.new("RGBA", (165 * len(FACES), 160), panel)
    for index, kind in enumerate(FACES):
        head = kit.coins[kind].copy()
        head.alpha_composite(kit.hat)
        faces.alpha_composite(head.crop((20, 0, 185, 160)), (index * 165, 0))
    rows.insert(0, faces.resize((faces.width * 2, faces.height * 2), Image.NEAREST))
    sheet = Image.new("RGBA", (max(row.width for row in rows), sum(row.height + 6 for row in rows)), (25, 23, 20, 255))
    y = 0
    for row in rows:
        sheet.alpha_composite(row, (0, y))
        y += row.height + 6
    try:
        sheet.save(SHEET)
    except OSError:
        print("could not write %s (is it open in a viewer?)" % os.path.relpath(SHEET, ROOT))
    print("wrote %d strips to %s" % (len(manifest), os.path.relpath(OUT, ROOT)))


if __name__ == "__main__":
    build()
