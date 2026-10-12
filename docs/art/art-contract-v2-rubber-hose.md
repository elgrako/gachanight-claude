# Rubber-hose pixel-art contract (v2)

Shared by every agent of this workspace. The game code loads the exact file
names, frame sizes and JSON files listed here, so do not rename or resize them.
Extra files are welcome if you list them in your report.

## The style: rubber hose, retro Japanese, in pixel art

The owner's references are in `diseños/` at the repository root. LOOK AT ALL OF
THEM with the Read tool before drawing anything:

- `machine_simple.jpg`, `Red_Gachapon_Sprite_Sheet_Views_and_Elements.png`,
  `Retro_Gumball_Machine_Sprite_Sheet.png`: the gumball machine (cap, glass
  globe full of balls with eyes, flared base, metal crank plate, chute), its
  parts, its palettes, and the pixel density wanted.
- `Pixel_Gumball_Adventure_Poster.png` and the `gpt-image-...jpg` poster: the
  machine as a living rubber-hose character, and the Showa-era poster mood.

Rules taken from them:

- **Rubber hose** (1920s-30s cartoons): limbs are black noodles of constant
  thickness with no elbows or knees, bending in smooth arcs; white four-finger
  gloves with a cuff; big rounded shoes; "pie" or tall-oval eyes (white oval,
  black oval pupil, often touching each other); simple round shapes; bouncy,
  squashy poses. Objects can be alive: eyes, arms, gloves.
- **Retro Japanese 80s-90s** on top: Showa toy-shop palette and graphics.
- **Outline**: bold, near-black `#161320`, 1 px (2 px on the outer contour of
  large sprites such as machines is fine). Never anti-aliased.
- **Shading**: flat colour plus ONE shadow shade and ONE highlight shade, in
  hard-edged shapes; a white specular dot or streak on glossy things (globe,
  balls, caps). No gradients, no dithering except an occasional halftone accent.
- **Palette** (extend sparingly): ink `#161320`, red `#e2231a`, dark red
  `#9c1420`, orange `#f0802a`, mustard `#f2b632`, cream `#f6e7c1`, paper
  `#fff8e3`, navy `#1f3a8a`, blue `#2f7de1`, sky glass `#9fd3f5`, green
  `#2e9e4f`, steel `#8a93a3`, dark steel `#4a5160`, glove white `#fffdf5`,
  pink `#f59ab5`. Night/unlit versions are made by the game (it tints the
  whole scene), so draw everything lit.
- PNG, RGBA, alpha 0 or 255 only (tiles are opaque). No text or logos of real
  brands; Japanese kana for generic words (ガチャ, おもちゃ) is welcome.

## The view: high-angle oblique ("3/4 from above")

The camera is raised and tilted down, like the FRENTE view of the reference
machine: you see the FRONT of every object plus its TOP. There is no side
perspective and no diamond grid.

- A circle lying flat (cap top, base rim, table top, pedestal) is an ellipse
  whose height is about 0.4-0.45 of its width.
- Vertical things keep their full height.
- The floor is a deep plane: things nearer to the camera are lower on screen.
- Everything that stands on the floor is anchored at the BOTTOM CENTRE of its
  canvas: the lowest pixel row is where it touches the floor (the front edge
  of its footprint), horizontally centred.
- World resolution: one sprite pixel = one world pixel; the camera shows about
  427 x 240 world pixels (x3 on a 720p canvas, nearest filtering).

## How to build

- Python 3.13 + Pillow generators under `tools/pixel/`, deterministic and
  re-runnable. Python: `%LOCALAPPDATA%\Programs\Python\Python313\python.exe`.
- `tools/pixel/pixlib.py` is shared and READ-ONLY (import it or copy what you
  need into your own module). Each agent only edits its own modules, listed in
  its delegation file.
- Each entry script verifies its outputs against this contract (existence,
  exact sizes, manifest consistency), prints OK or the problems, and exits
  non-zero on problems.
- Each entry script writes contact sheets (x4, mid-grey background, and for
  animations all frames side by side) to `tools/pixel/previews/`. Look at them
  with the Read tool and iterate several rounds, comparing against the
  references. This self-review is the quality bar: stop when it looks like the
  references, not when the script runs.
- Do not run git. Never commit. All text in files in English.

## Animation manifests

Animations are horizontal strips of equal frames. Each asset folder that holds
animations has its own `anims.json`:

```json
{ "player_walk": { "file": "player_walk.png", "frame_w": 40, "frame_h": 56, "frames": 8, "fps": 12, "loop": true } }
```

`file` is relative to the folder of that `anims.json`. Frame sizes are fixed by
this contract; frame counts and fps are the author's choice. Animation names
are global: keep the prefixes given here.

## A. Machines — owner `machine-artist`

Folder `assets/sprites/machines/`, manifest `assets/sprites/machines/anims.json`,
anchors `assets/sprites/machines/anchors.json`.
Generator entry `tools/pixel/build_machines.py`, module `tools/pixel/machines.py`
(rewrite it; the old side-view code is obsolete).

The machines are living rubber-hose characters like the references: glass globe
full of balls with eyes, noodle arms with gloves resting at their sides. They
do not walk.

| Asset | Size | Notes |
|---|---|---|
| `machine_001.png` ... `machine_004.png` | 48 x 84 | Capsule machines No. 1-4 exactly in the reference design (cap, globe, flared base, crank plate, chute). POWERED OFF: balls asleep (closed eyes), arms limp, no glow. Body colours: 001 red, 002 green, 003 mustard, 004 blue. Each also differs a little in cap or base shape so the four silhouettes are not identical. |
| `machine_005.png` | 72 x 104 | Crane catcher as a rubber-hose cabinet: glass box with plush prizes piled inside and NO claw drawn, control panel with joystick, chute. Powered off. |
| `machine_006.png` | 72 x 104 | Lucky Plinko as a rubber-hose cabinet: upright peg board (6 staggered rows) with 5 slots along its bottom and NO ball drawn, chute. Powered off. |
| anim `machine_00N_wake` (N = 1..6) | same as its machine | Not looping, at most 0.6 s: power arrives, eyes pop open, a stretch, lights on. Ends in the first idle pose. |
| anim `machine_00N_idle` (N = 1..6) | same | Looping, powered on: balls blink and look around, arms sway, a breathing squash, sign lamps chase. Lively but not distracting. |
| anim `machine_00N_play` (N = 1..4) | same | Not looping, at most 0.7 s: the machine cranks itself (handle turns, body squashes and stretches, globe rattles) and ends in the idle pose. The capsule is NOT drawn: the game drops it. |
| anim `machine_00N_react` (N = 5, 6) | same | Not looping, at most 0.5 s: a happy bounce when the prize drops. The game moves the claw and the ball itself. |
| `capsule_red.png`, `capsule_blue.png`, `capsule_green.png`, `capsule_mustard.png`, `capsule_gold.png` | 12 x 12 | The reference capsule: glossy ball, coloured top half, cream bottom half. |
| `claw_open.png`, `claw_closed.png` | 20 x 20 | Crane claw with a rubber-hose feel, hanging point at top centre (10, 0). |
| `plinko_ball.png` | 6 x 6 | |

`anchors.json` gives pixel coordinates in sprite space (origin top-left), which
the game reads instead of hard-coding them:

```json
{
  "machine_001": { "chute": [24, 74] },
  "machine_005": { "chute": [56, 92], "claw_rail_y": 14, "claw_min_x": 18, "claw_max_x": 54,
                   "claw_rest_x": 20, "grab_y": 34, "drop_x": 56, "drop_y": 52 },
  "machine_006": { "chute": [36, 94], "ball_start": [36, 14], "rows": 6, "row_step": 6,
                   "column_step": 5, "slot_y": 60, "slot_xs": [16, 26, 36, 46, 56] }
}
```

Meaning: `chute` = centre of the tray where the 12 x 12 capsule comes to rest
(the body must not move there during idle); `claw_rail_y` = y of the claw's top
when raised; `grab_y` = y of the claw's top when lowered onto the prizes;
`drop_x`/`drop_y` = claw top x over the drop hole and the y where the released
capsule disappears into it; plinko: the ball rests on the top peg at
`ball_start` (centre of the 6 x 6 ball), each row is `row_step` lower and
`column_step` left or right, after `rows` hops it falls into a slot whose ball
centre is (`slot_xs[i]`, `slot_y`); `slot_xs` are spaced 2 x `column_step` and
centred on `ball_start` x. Values above are examples: report your real ones.
Every anchor must hold in all frames of idle/react (keep the glass box and the
board static; animate the body around them).

## B. Figures and bases — owner `figure-artist`

Generator entry `tools/pixel/build_figures.py`, modules `tools/pixel/figures.py`
(rewrite) and `tools/pixel/bases.py`.

### Figures: `assets/sprites/figures/<figure_id>.png`, 40 x 40

One per entry of `data/figures.json` (30). Same toys as their names say, redrawn
as rubber-hose characters: pie or tall-oval eyes, noodle arms and legs, white
gloves, big shoes where it suits the creature, round bouncy bodies, seen from
slightly above (the top of the head is generous). Feet on the bottom row,
centred, NO base in this sprite. Every silhouette distinct (undiscovered
figures are shown as dark silhouettes, without their base).

### Bases: folder `assets/sprites/bases/`, manifest `assets/sprites/bases/anims.json`

A figure always stands on the base of its rarity. Rarity must be readable from
the base alone, and each step up must be clearly more elaborate:

| Animation | Frame | Notes |
|---|---|---|
| `base_common` | 56 x 30 | Plain low disc, cream/grey plastic. One frame is fine. |
| `base_uncommon` | 56 x 30 | Green disc with a rim stripe and a small name plate. |
| `base_rare` | 56 x 30 | Blue two-tier base with studs; a slow glint may travel around. |
| `base_epic` | 56 x 30 | Purple ornate three-tier base with gems that twinkle (animated). |
| `base_legendary` | 56 x 30 | Gold trophy-like base: laurels or wings at the sides, a turning ring of light or stars (animated), unmistakable. |

All five share one geometry so the game can stack any figure on any base:
the base is centred, touches the bottom row, and the figure's feet stand on
the point (28, 12) of the base frame (the centre of its top ellipse). Ornaments
may rise at the sides but must stay outside x 14..41 above y 12 so they do not
cover the figure. Colours follow `data/rarities.json` (common `#c9c2b0`,
uncommon `#7ec8a4`, rare `#5fb3c9`, epic `#c48ad6`, legendary `#e3b44c`).

Also write a preview `tools/pixel/previews/figures_on_bases.png` with every
figure standing on the base of its rarity.

## C. Characters and effects — owner `character-animator`

Folder `assets/sprites/anim/`, manifest `assets/sprites/anim/anims.json`.
Generator entry `tools/pixel/build_anims.py`, modules `tools/pixel/anim_*.py`
(the existing ones are yours to rewrite).

| Animation | Frame | Notes |
|---|---|---|
| `player_idle` | 40 x 56 | The protagonist as a rubber-hose character facing RIGHT in a slight 3/4 from above (the game flips it; it is used for every walking direction): round head with pie eyes and a hair tuft, red hoodie, noodle limbs, white gloves, big shoes. About 30 px wide and 48 px tall, feet on the bottom row. Bouncy breathing, blinks. |
| `player_walk` | 40 x 56 | Rubber-hose strut: bobbing body, swinging noodle arms, big shoe steps. |
| `player_run` | 40 x 56 | |
| `player_use` | 40 x 56 | Reaches forward to press / drop a coin, not looping. Report the frame where the hand reaches furthest. |
| `player_cheer` | 40 x 56 | Jump for joy with both arms up, not looping (new figure). |
| `player_sleep` | 56 x 32 | Asleep lying down (on the sofa), breathing. |
| `robot_idle`, `robot_work` | 28 x 34 | Small rubber-hose tin robot (wind-up key, pie eyes, noodle arms, gloves). `work` reaches to its RIGHT to turn a crank. |
| `coin_spin` | 12 x 12 | Coin lying/spinning on the floor seen from above-front. |
| `coin_pickup` | 20 x 28 | Not looping. |
| `capsule_open`, `capsule_open_blue`, `capsule_open_green`, `capsule_open_mustard`, `capsule_open_gold` | 40 x 40 | The reference capsule (coloured top, cream bottom; plain = red) shaking and bursting open, not looping. Report the frame of the biggest flash. |
| `sparkle` | 16 x 16 | Not looping. |
| `rarity_burst` | 64 x 64 | White burst the game tints, not looping. |
| `zzz` | 16 x 16 | |
| `dust_puff` | 16 x 12 | Little cloud at the feet when starting to run or stopping, not looping. |
| `coin_flip` | 12 x 28 | A coin tossed up and falling into a slot, not looping. |
| `speech_dots` | 20 x 14 | Three bouncing dots in a bubble (machine "thinking"), looping. |

Report the natural ground speed of walk and run in pixels per second.

## D. Environment — owner `environment-artist`

Generator entry `tools/pixel/build_environment.py`, modules `tools/pixel/props.py`
and `tools/pixel/tiles.py` (rewrite). Everything in the oblique view, in the
same Showa toy-shop mood, lit.

Tiles, `assets/sprites/tiles/`, opaque, seamless:

| File | Size | Notes |
|---|---|---|
| `wall_bath.png`, `wall_corridor.png`, `wall_hall.png`, `wall_gallery.png`, `wall_reception.png`, `wall_staff.png` | 16 x 16 | Back-wall patterns: bath = small ceramic tiles; corridor = plain cream; hall = cream with a red-and-navy retro pattern, subtle; gallery = deep navy felt so toys pop; reception = cream with thin stripes; staff = tan wallpaper. |
| `floor_bath.png`, `floor_hall.png`, `floor_gallery.png`, `floor_staff.png` | 16 x 10 | Floors seen from above at an angle (tiles are wider than tall): bath = small checker; hall = red/cream checker lino; gallery = dark wood; staff = wood planks. Keep contrast moderate: characters walk on it. |
| `wall_top.png` | 16 x 8 | Cornice strip at the top of the wall. |
| `trim.png` | 16 x 6 | Skirting board between wall and floor. |
| `pillar.png` | 14 x 16 | Room divider on the back wall, repeats vertically. |
| `front_ledge.png` | 16 x 8 | Near edge of the floor (top of the front wall seen from above), repeats horizontally. |

Props, `assets/sprites/props/`:

| File | Size | Notes |
|---|---|---|
| `toilet.png` | 30 x 40 | |
| `sink.png` | 30 x 50 | with a mirror above |
| `power_switch_off.png`, `power_switch_on.png` | 20 x 28 | Wall breaker box with a big lever and a lamp; a rubber-hose face is welcome. |
| `lamp_off.png`, `lamp_on.png` | 30 x 34 | Pendant lamp hanging from a cord that starts at the top centre of the canvas; shade seen from slightly above. |
| `sofa.png` | 80 x 46 | Old comfy sofa, front view from above. |
| `counter.png` | 100 x 50 | Reception counter with a visible top surface. |
| `computer_off.png`, `computer_on.png` | 30 x 30 | Chunky CRT terminal; ON shows a rubber-hose salesman face on a green screen. Screen area must be the same rectangle in both. |
| `door_closed.png`, `door_open.png` | 58 x 88 | Glass shop door in the back wall; closed = night outside, open = bright daylight. |
| `shelf_a.png`, `shelf_b.png` | 58 x 84 | Shelves of toy boxes and plushes. |
| `locker.png` | 30 x 74 | |
| `table.png` | 46 x 32 | Low table with a visible top. |
| `poster_a.png` ... `poster_d.png` | 28 x 36 | Showa-style toy posters like the references (sunburst, kana, mascots). |
| `sign_gacha.png` | 110 x 28 | Hanging sign ガチャ / GACHA. |
| `key.png` | 14 x 10 | |
| `plant.png` | 24 x 40 | |
| `gallery_shelf.png` | 34 x 12 | One segment of a wall shelf seen from above-front; repeats horizontally. |
| `rug.png` | 96 x 34 | Flat floor rug seen at the floor angle. |
| `crate.png` | 28 x 30 | Cardboard box of toys, free-standing. |

Report, for each free-standing prop, the depth of its footprint in pixels
(how far back from its bottom row it occupies the floor).

## E. Ambient life — owner `ambient-animator`

Folder `assets/sprites/ambient/`, manifest `assets/sprites/ambient/anims.json`.
Generator entry `tools/pixel/build_ambient.py`, modules `tools/pixel/ambient_*.py`.
Small looping animations that make the store feel alive, rubber-hose where a
creature or face is involved. All loop unless noted.

| Animation | Frame | Notes |
|---|---|---|
| `amb_maneki_neko` | 26 x 32 | Lucky cat waving its paw (stands on the counter). |
| `amb_wall_clock` | 24 x 36 | Wall clock with a swinging pendulum and pie eyes that tick left-right. |
| `amb_ceiling_fan` | 56 x 24 | Hanging fan seen from below-front, blades turning. |
| `amb_tv` | 38 x 44 | Small CRT TV on a stand showing a looping rubber-hose cartoon and static. |
| `amb_neon_sign` | 72 x 28 | Neon ガチャ sign buzzing and flickering. |
| `amb_string_lights` | 96 x 14 | Garland of coloured bulbs chasing; tiles horizontally. |
| `amb_lantern` | 20 x 34 | Paper lantern (chochin) swaying on its cord, top centre fixed. |
| `amb_fish_bowl` | 26 x 26 | Goldfish swimming in a bowl. |
| `amb_tap_drip` | 10 x 26 | A drop forming at a tap and falling (bathroom). |
| `amb_moth` | 14 x 12 | Moth fluttering in place (the game moves it around a lamp). |
| `amb_mouse_run` | 22 x 14 | Rubber-hose mouse running, facing RIGHT (the game moves it). |
| `amb_cat_sleep` | 36 x 22 | Cat asleep, breathing, tail flick. |
| `amb_plant_sway` | 24 x 40 | Potted plant swaying. Same pot as a plant prop is not required. |
| `amb_mug_steam` | 14 x 24 | Mug with rising steam. |
| `amb_radio` | 30 x 30 | Old radio bouncing to the music with notes popping out. |
| `amb_balloon` | 18 x 44 | Balloon on a string bobbing, string bottom fixed at bottom centre. |
| `amb_windup_toy` | 18 x 18 | Wind-up toy walking, facing RIGHT (the game moves it). |
| `amb_dust_motes` | 48 x 48 | Sparse motes drifting in a light beam, very subtle. |
| `amb_exit_sign` | 30 x 14 | Lit EXIT / 出口 sign that flickers now and then. |
| `amb_vending` | 46 x 86 | Drink vending machine, front lit, lights rippling, free-standing. |
| `amb_koinobori` | 64 x 24 | Carp streamer rippling on the wall. |
| `amb_capsule_roll` | 12 x 12 | A stray capsule rolling, facing RIGHT (the game moves it). |
| `amb_spider` | 12 x 30 | Tiny cute spider sliding down its thread and back up, top fixed. |
| `amb_pinwheel` | 18 x 30 | Toy pinwheel spinning in a pot. |
| `amb_arcade_cab` | 40 x 78 | Decorative arcade cabinet with an attract-mode screen (not usable). |
| `amb_bubbles` | 16 x 32 | Soap bubbles rising and popping (bathroom sink). |

At least these 26; more are welcome (list them with frame size and where they
would go).
