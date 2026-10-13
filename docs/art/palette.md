# Palette (third trial, 2026-10-13)

Not final: the owner is trying it in the game. Source of truth:
`tools/pixel/palette.py`.

## The owner's brief, as it grew

1. About 16 colours, a few more allowed; the protagonist stands out by being
   greyer than the set; the computer more muted and sepia.
2. After a first trial (22 colours from the coin and the machine picture):
   more sepia and brown, smaller, on absolutely everything.
3. After a second trial (16 colours): **a slightly wider range, tones turned
   down, no blues and no reds, more sepia, and the 0.55 saturation the owner
   used for the pictures in `diseños/`.**

## The twenty-five

| Ramp | Colours |
|---|---|
| Neutral (7), from `diseños/moneda1.png` | `#0e0d0c` `#2a2722` `#4c4337` `#716049` `#9a8766` `#c9bb9f` `#e3d9c6` |
| Umber (5) | `#3d2a1e` `#5a3d28` `#7a5534` `#9a7046` `#b98d5c` |
| Ochre (3) | `#8a7038` `#b09448` `#d0b870` |
| Olive (3) | `#4a4a30` `#6e6e48` `#979a72` |
| Rust (3), where red used to be | `#5e3424` `#8a4e30` `#b0704a` |
| Grey-green (2), where blue and teal used to be | `#4a5546` `#74806c` |
| Brown mauve (2), glass and night | `#453a38` `#6e5e5a` |

Everything but the neutrals was chosen by Claude.

## How it is applied

- `remap` takes a picture down to saturation 0.55 first and only then picks
  the nearest palette colour.
- `tools/pixel/apply_palette.py`: every generated picture under
  `assets/sprites`, in place (127 pictures). Lossy: run it on a generator's
  output, never on an already remapped picture.
- The owner's pictures keep their drawing and take the palette through their
  builders: capsule machine, computer, gold coin icon. The protagonist is
  never touched.
- Every colour written under `scripts/` is a palette colour (set, HUD,
  panels).
- Screen pass: saturation 1.0 (was 0.85), sepia tint 0.1 (was 0.16).

## Known weak points

- It is close to monochrome. The owner's machine lost all its red; its
  untouched picture is still `diseños/maquina1.png`.
- Capsule Machines No. 1 and No. 2 now look the same: the body colours that
  told them apart no longer exist after the remap.
- Looked at in the machine hall and the cellar only.
