# Pixel density: the rule (decided 2026-10-14)

Decided by the owner after a still test of one density for everything (the
protagonist reduced to 64 px lost too much and would have needed redrawing).
Goal behind it: keep the art cost as low as possible without losing the
essence.

## The rule

| | Grid | One art pixel on screen at 1080p | Used for |
|---|---|---|---|
| **Standard** | 640 x 360 | 3 x 3 screen pixels | the set, machines, props, figures, robots, effects, close-up views |
| **High density** | 3 times finer than standard | 1 screen pixel | the protagonist, the reception computer, and later only characters with a face that talk or react |

- At 1080p (the most common Steam resolution) both are exact: standard x3,
  high density x1. At 4K both are exact too (x6 and x2).
- At 720p and 1440p the high-density art is scaled smoothly (x0.67, x1.33);
  the standard art stays exact (x2, x4). Accepted.
- Why three times and not twice: twice would put high density at 1.5 screen
  pixels at 1080p, which gives uneven pixels.

## Sizes, in standard pixels

| Thing | Height | Canvas | Note |
|---|---|---|---|
| Capsule machine | 128 | 81 x 128 | the owner's `diseños/maquina1.png` already is this |
| Crane, plinko | about 140 | about 100 x 140 | today's pictures are 156 tall |
| Figures | about 32 | 48 x 48 | |
| Props | 32 to 64 | | |
| Close-up of a machine | the screen | 640 x 360 | today 320 x 180; the owner will rework it, so it moves to standard |

High density, in its own pixels (three per standard pixel):

| Thing | Height | Note |
|---|---|---|
| Protagonist | about 190 to 200 (about 64 standard) | `diseños/moneda1.png` is used as drawn |
| Reception computer | about 130 (about 44 standard) | today's `ordenador.png` is 88 and comes out small: redraw it at about 130, or show it larger |

## Conditions, so the mix reads as intended

1. **Same outline weight on screen.** High-density characters ink their
   outline about 3 of their pixels thick, the same as one standard pixel.
2. **Same palette and the same way of shading** at both densities
   (`docs/art/palette.md`).
3. **Few exceptions:** characters with a face only. Everything else is
   standard.

## Keeping the cost down

- Characters are animated by parts (body, hat, gloves, shoes drawn once and
  moved by code, as `tools/pixel/build_peseta.py` does), so a high-density
  character is drawn once, not once per frame.
- Left-facing art is the right-facing art mirrored.
- Variants are palette swaps (Capsule Machine No. 2 is No. 1 recoloured).
- Idles are a few frames; breathing, blinking and shaking are done in code.

## Not yet applied

The rule is written down; the game has not been changed to follow it. Out of
line today: the computer (88 px shown at 1x), the close-up view (320 x 180),
the crane and the plinko (156 tall), and the camera, which shows 427 x 240
world pixels with art at 1.5 pixels per world pixel (the same density as the
standard grid, under another name).
