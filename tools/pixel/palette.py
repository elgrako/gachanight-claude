"""The game's palette: thirty-four warm, muted colours (fourth trial, 2026-10-15).

The owner's brief, as it grew: a smaller, browner palette; then a slightly
wider one, tones turned down, no blues and no reds, 0.55 saturation; then,
seeing the capsule machine (red in the owner's drawing) come out looking
like an old Game Boy: **more colours, still warm and muted**. So reds are
back, muted and warm, and most ramps got one more step.

- NEUTRAL: the warm greys of `diseños/moneda/moneda personaje.png`, reduced
  from 17 to 7. The protagonist uses nothing else.
- Ramps for everything else: umber, ochre, olive, red (muted, warm), rust,
  a peach for lit red, grey-green (where blue and teal used to be) and a
  brown mauve for glass and night.

`remap` first takes a picture down to SATURATION and only then looks for the
nearest palette colour, so a bright colour lands on a muted one of the same
family. It was 0.55 in the third trial; at that the reds turned brown.
"""
from PIL import Image, ImageEnhance

SATURATION = 0.8
NEUTRAL = ["#0e0d0c", "#2a2722", "#4c4337", "#716049", "#9a8766", "#c9bb9f", "#e3d9c6"]
UMBER = ["#3d2a1e", "#5a3d28", "#7a5534", "#9a7046", "#b98d5c"]
OCHRE = ["#8a7038", "#b09448", "#d0b870", "#e0c890"]
OLIVE = ["#4a4a30", "#6e6e48", "#979a72"]
RED = ["#3e1a1a", "#5e2a26", "#80382f", "#a14d3e", "#bf6d55"]
RUST = ["#5e3424", "#8a4e30", "#b0704a"]
PEACH = ["#d4a07a"]
GREY_GREEN = ["#4a5546", "#74806c", "#9fa68e"]
MAUVE = ["#453a38", "#6e5e5a", "#968683"]
COLOUR = UMBER + OCHRE + OLIVE + RED + RUST + PEACH + GREY_GREEN + MAUVE
PALETTE = NEUTRAL + COLOUR


def rgb(colour):
    return tuple(int(colour[index:index + 2], 16) for index in (1, 3, 5))


def muted(colour):
    """`colour` ("#rrggbb") taken down to SATURATION, as (r, g, b)."""
    r, g, b = rgb(colour)
    grey = 0.299 * r + 0.587 * g + 0.114 * b
    return tuple(grey + (channel - grey) * SATURATION for channel in (r, g, b))


def nearest(colour, allowed=PALETTE):
    """The allowed colour closest to `colour` once muted (both "#rrggbb")."""
    if colour in allowed:
        return colour
    source = muted(colour)
    return min(allowed, key=lambda other: sum((x - y) ** 2 * w for x, y, w in zip(source, rgb(other), (0.3, 0.59, 0.11))))


def remap(picture, allowed=PALETTE):
    """`picture` muted, then every pixel moved to its nearest allowed colour; alpha is kept."""
    picture = picture.convert("RGBA")
    swatch = Image.new("P", (1, 1))
    flat = []
    for colour in allowed:
        flat.extend(rgb(colour))
    swatch.putpalette(flat + flat[:3] * (256 - len(allowed)))
    dull = ImageEnhance.Color(picture.convert("RGB")).enhance(SATURATION)
    mapped = dull.quantize(palette=swatch, dither=Image.Dither.NONE).convert("RGBA")
    mapped.putalpha(picture.getchannel("A"))
    return mapped
