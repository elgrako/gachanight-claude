"""The game's coin, cut from the owner's gold picture of the protagonist.

Takes `diseños/moneda_oro1.png`, keeps the coin's face and its hat, drops the
arms, gloves and legs, and writes two pictures:

    assets/sprites/ui/coin_face.png   the cut at the picture's own size
    assets/sprites/ui/coin_icon.png   the same reduced for the HUD

Run from the repository root:

    py -3.13 tools/pixel/build_coin_icon.py
"""
import glob
import os

from PIL import Image, ImageChops, ImageDraw

OUT_DIR = os.path.join("assets", "sprites", "ui")
# The coin's disc in the picture: centre and radii.
DISC = (93.0, 83.5, 58.5, 59.5)
# The hat, clear of the glove that tips it.
HAT = [(38, 34), (33, 22), (38, 10), (56, 3), (74, 2), (83, 10), (87, 28), (84, 40), (70, 46), (50, 52), (40, 50)]
ICON_HEIGHT = 80
INK = (30, 16, 8, 255)


def build():
    source = glob.glob(os.path.join("dise*", "moneda_oro1.png"))[0]
    picture = Image.open(source).convert("RGBA")
    keep = Image.new("L", picture.size, 0)
    draw = ImageDraw.Draw(keep)
    cx, cy, rx, ry = DISC
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
    draw.polygon(HAT, fill=255)
    alpha = ImageChops.multiply(picture.getchannel("A"), keep)
    face = picture.copy()
    face.putalpha(alpha)
    # Close the cuts with the picture's ink where limbs were taken away.
    pixels = face.load()
    closing = []
    for y in range(face.height):
        for x in range(face.width):
            if pixels[x, y][3] == 0:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                outside = not (0 <= nx < face.width and 0 <= ny < face.height) or pixels[nx, ny][3] == 0
                if outside and sum(pixels[x, y][:3]) > 160:
                    closing.append((x, y))
                    break
    for x, y in closing:
        pixels[x, y] = INK
    face = face.crop(face.getbbox())
    os.makedirs(OUT_DIR, exist_ok=True)
    face.save(os.path.join(OUT_DIR, "coin_face.png"))
    width = round(face.width * ICON_HEIGHT / face.height)
    face.resize((width, ICON_HEIGHT), Image.LANCZOS).save(os.path.join(OUT_DIR, "coin_icon.png"))
    print("wrote coin_face.png", face.size, "and coin_icon.png", (width, ICON_HEIGHT))


if __name__ == "__main__":
    build()
