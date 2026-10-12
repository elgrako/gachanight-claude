# Old-cartoon sepia contract (v3)

Binding for every agent of this workspace. It replaces the style, palette and
sizes of the previous contract
(`.orchestrator/plans/2026-10-11-17-45-forge-rubber-hose/art-contract.md`);
that file still describes the view, the folders, the animation manifest format
and what each asset is for, and remains valid where this one is silent.

## What the owner asked for

"An old rubber-hose cartoon look, like the video games Cuphead or MOUSE: P.I.
For Hire", a sepia palette, pixels that are "more defined", and more detail.
The owner's own references are in `diseños/` and outrank everything else. LOOK
AT THEM with the Read tool before drawing: `maquina gumball.jpg` (capsule
machines), `maquina_gancho.png` (crane), `plinko.png`, `pachinko.png`,
`ruleta.png`, `ordenador.png` and `ordenador_kawai.png` (reception computer),
`maquina_limpieza1.png` / `2.png` (the worker robots), `cartera1.png`,
`moneda_oro1.png`, `moneda1.png`, `moneda4.png`, `moneda_madera1.png` (coins,
purse), `colegas.png` and `COLEGAS2.png` (how objects become characters).
Do not copy pixels from them and do not copy any character of Cuphead, MOUSE or
any other existing work: match the language, not the cast.

## The look

- **1930s rubber hose, exaggerated**: pie-cut eyes with a brow line and a
  highlight, big mischievous grins, noodle limbs in sweeping arcs, puffy white
  gloves with three back lines, chunky shoes, top hats, bow ties, monocles.
  Objects are characters: a face, an attitude, a pose. Squash and stretch in
  every animation, with anticipation and overshoot.
- **Machines seen in three quarters**, like the references: a lit front face
  and a narrower side face in shade, the top visible. Furniture too.
- **Ink line**: warm near-black, 1 px, with 2 px on the outer contour of big
  sprites and thick-thin variation where a curve turns. No pure black.
- **Detail and definition**: this is the main change. Every sprite is drawn at
  1.5 times its previous pixel size (table below) and must use the room:
  three or four tones per material (deep shadow, shadow, base, highlight),
  rim light, hard specular shapes on glass and brass, wood grain, rivets,
  screws, seams, stickers, wear and chipped paint, hand-lettered signs.
  Dithering and halftone are allowed for texture and vintage print feel. No
  blur, no anti-aliasing, alpha 0 or 255 only (tiles opaque).
- **Sepia palette**: aged paper and warm browns carry everything; colour is
  rare, muted and warm. Use `tools/pixel/sepia.py` (shared, read-only): import
  its named ramps instead of inventing colours. If a sprite truly needs a
  colour it lacks, add it in your own module, keep it in the same value and
  saturation range, and list it in your report.
- The game adds film grain and a soft vignette itself; do not bake them in.

## Resolution

Every texture is 1.5 times its world size (the game draws art at two thirds),
so on the owner's 1080p screen one sprite pixel is exactly 3 screen pixels.
All sizes, anchors and fixed points of the previous contract are multiplied by
1.5. Bottom-centre anchoring and "feet on the bottom row" are unchanged.

| Asset | Previous | Now |
|---|---|---|
| Capsule machines 001-004 (still and every frame) | 48 x 84 | 72 x 126 |
| Crane 005, Plinko 006 | 72 x 104 | 108 x 156 |
| `capsule_<colour>.png` | 12 x 12 | 18 x 18 |
| `claw_open/closed.png` (hang point top centre) | 20 x 20 | 30 x 30 |
| `plinko_ball.png` | 6 x 6 | 9 x 9 |
| Figures and their idle frames | 40 x 40 | 60 x 60 |
| Bases (`base_<rarity>`), feet point | 56 x 30, (28, 12) | 84 x 45, (42, 18) |
| `player_*` frames | 40 x 56 | 60 x 84 |
| `player_sleep` | 56 x 32 | 84 x 48 |
| `robot_idle`, `robot_work` | 28 x 34 | 42 x 51 |
| `coin_spin` | 12 x 12 | 18 x 18 |
| `coin_pickup` | 20 x 28 | 30 x 42 |
| `coin_flip` | 12 x 28 | 18 x 42 |
| `capsule_open*` | 40 x 40 | 60 x 60 |
| `sparkle`, `zzz` | 16 x 16 | 24 x 24 |
| `rarity_burst` | 64 x 64 | 96 x 96 |
| `dust_puff` | 16 x 12 | 24 x 18 |
| `speech_dots` | 20 x 14 | 30 x 21 |
| Wall tiles | 16 x 16 | 24 x 24 |
| Floor tiles | 16 x 10 | 24 x 15 |
| `wall_top`, `front_ledge` | 16 x 8 | 24 x 12 |
| `trim` | 16 x 6 | 24 x 9 |
| `pillar` | 14 x 16 | 21 x 24 |
| Props and ambient loops | w x h | 1.5 w x 1.5 h |

`anchors.json` stays in sprite pixels, so its numbers are also 1.5 times the
old meaning (the game divides them back).

## Machines

- 001-004 follow `maquina gumball.jpg`: cap with knob, glass globe full of toy
  capsules, the machine's own two big eyes on the globe, collar, flared body in
  three quarters, coin plate with a lever with a red knob, dark chute, stickers
  on the shaded side. No arms. They differ by body metal and cap: 001 brass,
  002 copper-green patina, 003 cast iron with gold trim, 004 enamel blue-grey,
  plus small shape changes so the four silhouettes are not identical. The
  current 48 x 84 brass machine built by `tools/pixel/gumball_001.py` shows the
  intended layout and animation beats; it is superseded and should be removed
  once the new generator covers 001.
- 005 follows `maquina_gancho.png`: a maroon cabinet in three quarters, a face
  on its dome top with a little top hat, PRIZE lettering, a glass box with
  plushes, joystick, chute.
- 006 follows `plinko.png`: a steel-blue cabinet in three quarters, eyes on a
  glass dome, a slanted peg board, five slots, one arm raised waving a glove,
  a star badge and PLINKO lettering.
- Animations, anchors and timing rules are those of the previous contract
  (wake at most 0.6 s starting on the powered-off still; idle looping; play
  at most 0.7 s for 001-004; react at most 0.5 s for 005-006; wake, play and
  react end on idle frame 0; the tray, the crane's glass interior and the
  plinko board stay pixel-stable in idle and react).

## Working rules (usage is limited)

The owner has a hard usage budget. Work economically:

- Read only what you need; do not re-read large files you already read.
- At most three look-and-fix rounds on your contact sheets. Stop when it reads
  well at x3, not when it is perfect.
- Write your generator and outputs early and keep them valid on disk as you go,
  so that an interruption loses little.
- Keep the final report short.
- Do not run git. Never commit. English in files. Edit only your own paths.
