# Palette (fourth trial, 2026-10-15)

Kept by the owner ("we will keep this palette", 2026-10-15). Source of truth: `tools/pixel/palette.py`.

## The owner's brief, as it grew

1. About 16 colours; the protagonist stands out by being greyer; the
   computer more muted and sepia.
2. More sepia and brown, smaller, on absolutely everything.
3. A slightly wider range, tones down, no blues and no reds, 0.55 saturation.
4. (2026-10-15) The capsule machine, red in the owner's drawing, came out
   "like an old Game Boy": **more colours, still warm and muted.** Reds are
   back, muted and warm.

## The thirty-four

| Ramp | Colours |
|---|---|
| Neutral (7), from the owner's coin | `#0e0d0c` `#2a2722` `#4c4337` `#716049` `#9a8766` `#c9bb9f` `#e3d9c6` |
| Umber (5) | `#3d2a1e` `#5a3d28` `#7a5534` `#9a7046` `#b98d5c` |
| Ochre (4) | `#8a7038` `#b09448` `#d0b870` `#e0c890` |
| Olive (3) | `#4a4a30` `#6e6e48` `#979a72` |
| Red (5), muted and warm | `#3e1a1a` `#5e2a26` `#80382f` `#a14d3e` `#bf6d55` |
| Rust (3) | `#5e3424` `#8a4e30` `#b0704a` |
| Peach (1), lit red | `#d4a07a` |
| Grey-green (3), where blue used to be | `#4a5546` `#74806c` `#9fa68e` |
| Brown mauve (3), glass and night | `#453a38` `#6e5e5a` `#968683` |

Everything but the neutrals was chosen by Claude. No blue: the owner's blues
(the capsule machine's glass and some capsules) land on mauve and grey-green.

## How it is applied

- `remap` takes a picture down to saturation 0.8 (was 0.55, at which the
  reds turned brown) and then picks the nearest palette colour.
- `tools/pixel/apply_palette.py`: every generated picture under
  `assets/sprites`, in place. Lossy: run it on a generator's output, never on
  an already remapped picture. For the fourth trial the sprites were first
  restored from commit `307438a`, from before any palette.
- The owner's pictures keep their drawing and take the palette through their
  builders: capsule machine (`build_maquina1.py`; No. 2 is No. 1 with the
  reds turned grey-green), computer (`build_reception.py`), gold coin icon
  (`build_coin_icon.py`). The protagonist is never touched.
- Every colour written under `scripts/` is a palette colour (all are from the
  third trial's 25, which this palette contains).
- Screen pass: see `scripts/ui/screen_grade.gd`; the default old-television
  look keeps the colours (saturation 1.12).

## Known weak points

- The script colours were brought onto the new reds by hand where red was
  meant: the UI's coral and alert, the terminal's amber, the machine scene's
  red capsule and machine body, the staff room wall, the reception sign, and
  the close-up view's body and red capsules (`build_pov.py`). The rest kept
  the third trial's colours, which this palette contains.
- Looked at in the machine hall, the reception and the close-up view.
