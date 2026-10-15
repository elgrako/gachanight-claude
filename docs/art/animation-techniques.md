# Animation techniques: the rules (owner, 2026-10-15)

The owner asked for four techniques to be researched and applied to every
sprite and animation: **blockout, delta time, squash and stretch, texel
perfect**. What each means here, how the game applies it, and what is still
out of line.

## 1. Blockout

**What it is.** Animate the key poses first (the extremes and the contacts),
held in place with no in-betweens ("stepped"), judge timing and staging on
those alone, then add the in-betweens ("spline") and polish. Detail never
comes before the keys read.

**Rule here.** Every new animation starts as a strip of key poses with holds,
looked at on its own before any in-between is drawn. In-betweens are few:
one each way is usually enough at 8 to 12 frames a second, which is also the
cheapest.

**Applied.** The capsule machine's idle (`build_maquina1.py`, `BREATH`) was a
continuous drift; it is now blocked: rest (held) → breathe out (squash, one
in-between, held) → rest → breathe in (stretch, one in-between, held) → rest,
with the blink in the long rest. The protagonist's walk already was four
keys per step (contact, down, passing, up).

## 2. Delta time

**What it is.** Anything that moves over time is scaled by the time the frame
took, so the game looks the same at 30, 60 or 144 frames a second. The trap
is smoothing written as `lerp(a, b, k * delta)`, which still depends on the
frame rate; the right form is `lerp(b, a, exp(-k * delta))`.

**Rule here.** Movement uses `* delta`; smoothing uses the exponential form;
timed effects use tweens or animation frames (both run on time, not frames);
shader motion uses `TIME`.

**Applied.** The camera's follow was `lerp(..., delta * 6)`; it is now
exponential (`main.gd`). The rest was already right: the player moves by
`velocity * delta`, the timing wheel's needle by `speed * delta`, sprites
play at fixed frames a second, effects are tweens.

## 3. Squash and stretch

**What it is.** A shape squashes on impact and stretches with speed, and
keeps its volume while doing so (width x height constant), or it reads as
growing and shrinking. Overdone it reads as rubber; for rubber hose that is
partly the point, with restraint.

**Rule here.** `scripts/world/squash.gd`: `amount` > 0 squashes, < 0
stretches, width = 1 / height; `bounce()` goes hit → small rebound the other
way → rest, on a tween.

**Applied.**

| What | When | Amount |
|---|---|---|
| Protagonist | sets off / stops short | stretch 7 % / squash 9 % |
| Protagonist | presses something / cheers | squash 8 % / stretch 12 % |
| Machines in the hall | the power comes on, one after another | stretch 8 % |
| Floor coins | picked up | squash 25 %, then gone |
| Capsule machine idle | breathing | 1 to 2 art pixels each way, baked |
| Close-up view | perfect stop | stretch on the hop, squash on landing |

## 4. Texel perfect

**What it is.** Every art pixel (texel) shows as the same whole number of
screen pixels, and moves by whole texels. Breaking it gives uneven pixels
("mixels"): a picture scaled by a fraction, or standing half a texel off the
grid, or a camera between pixels so the whole scene crawls as it scrolls.

**Rule here.**
- The project snaps every canvas item and vertex to whole pixels
  (`project.godot`, `rendering/2d/snap/*`).
- The camera follows smoothly in a free position but sits on the nearest art
  pixel of the standard grid (1.5 per world pixel), so the set scrolls by
  whole texels (`main.gd`, `ART_PER_WORLD`).
- Squash and stretch on standard art is rounded to whole art pixels
  (`Squash.shape` with the picture's size), or baked into the frames.
- High-density characters are drawn smoothed by the density rule
  (`docs/art/pixel-density.md`) and are exempt.
- The close-up view is drawn in a 320 x 180 viewport, so it is texel perfect
  by construction.

## Still out of line (found in the review)

Pictures drawn at one art pixel per world pixel instead of 1.5: their
texels show 3 screen pixels wide at 720p where the standard is 2, so they
look coarser than everything around them. They need redrawing at 1.5
(scaling by 1.5 would itself make mixels):

- props from the old generator: sofa, front door, posters, hanging lamps,
  the GACHA sign, the fuse box, the key, crates;
- the poker table (`build_cellar.py`);
- the twenty figures (40 x 40) and their bases (56 x 30).

Also: the computer (high density by the rule, but 84 art pixels shown at a
third, where the rule asks for about 130).

## Sources

- Pluralsight, "Stepped vs. spline curves when blocking an animation".
- Binus University DKV, "Squash and stretch: bringing personality to every drawing".
- Howling Moon Software, "Improved lerp smoothing" (also on Game Developer);
  Godot docs, "Interpolation".
- Godot forum, "How to set up smooth sub-pixel camera movement for pixel art
  games" and "Aiming for pixel perfection in Godot"; Godot asset
  "PixelPerfectSmoother".
