"""The game's palette: twenty-five muted, sepia colours (third trial, 2026-10-13).

The owner's brief for this one: a slightly wider range than the sixteen of
the second trial, but with the tones turned down; no blues and no reds; more
sepia; and the same 0.55 saturation the owner used for the pictures in
`diseños/`.

- NEUTRAL: the warm greys of `diseños/moneda1.png`, reduced from 17 to 7. The
  protagonist uses nothing else.
- Six short ramps for everything else, all between orange-brown and
  grey-green on the colour wheel: umber, ochre, olive, rust (where red used
  to be), grey-green (where blue and teal used to be) and a brown mauve for
  glass and night.

`remap` first takes a picture down to SATURATION and only then looks for the
nearest palette colour, so a bright red lands on rust and a blue on
grey-green by their lightness, not by their hue.
"""
from PIL import Image, ImageEnhance

SATURATION = 0.55
NEUTRAL = ["#0e0d0c", "#2a2722", "#4c4337", "#716049", "#9a8766", "#c9bb9f", "#e3d9c6"]
UMBER = ["#3d2a1e", "#5a3d28", "#7a5534", "#9a7046", "#b98d5c"]
OCHRE = ["#8a7038", "#b09448", "#d0b870"]
OLIVE = ["#4a4a30", "#6e6e48", "#979a72"]
RUST = ["#5e3424", "#8a4e30", "#b0704a"]
GREY_GREEN = ["#4a5546", "#74806c"]
MAUVE = ["#453a38", "#6e5e5a"]
COLOUR = UMBER + OCHRE + OLIVE + RUST + GREY_GREEN + MAUVE
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
