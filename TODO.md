# GachaNight — where things stand and what is next

Hand-off notes for continuing on another machine or in another session.
Last updated 2026-10-12.

## Set-up on a new machine

1. `git clone https://github.com/elgrako/gachanight-claude`
2. Godot 4.7 (standard build). First run: `godot --headless --path . --import`
   and let it finish, then `godot --path .`
3. Only to regenerate art: Python 3.13 with Pillow (`pip install pillow`).
4. Tests (all must pass before and after any change):
   - `godot --headless --path . -s tests/run_tests.gd` — 360 rule checks
   - `godot --headless --path . -s tests/smoke_boot.gd` — 140 scene checks
   - `godot --headless --path . -s tests/sim_balance.gd -- --seed=1987 --quiet`
5. Agent rules: `AGENTS.md` and `.codex/`. The `.orchestrator/` workspaces are
   not in git; the art contracts that matter were copied to `docs/art/`.
6. The save file is per machine (`user://gachanight_save.json`); a new machine
   starts a new game.

## Where the last session stopped (2026-10-12, uncommitted)

Nothing of this is committed: 100+ changed files in the working tree. Ask the
owner before committing.

Done, owner's requests in order:

- Placement fix: art not yet redrawn (props, tiles, figures, bases, ambient)
  is authored at world size and now drawn 1:1; redrawn art (machines,
  protagonist, robot, effects) stays at 2/3. `Sprites.density` / `draw_scale`
  in `scripts/world/sprite_lib.gd` decide per texture, so new 1.5x art needs
  no code change. Figure idle loops play again.
- Capsule machines 2 and 3 removed. Four machines: `machine_001` (1 coin),
  `machine_002` (the blue Space Patrol one, 50 coins, unlocks the sofa),
  `machine_005` crane (3,000), `machine_006` plinko (250K). Twenty figures.
  Robots for the crane and plinko cost 60K and 5M; exit key 300M.
- Store 1000 world pixels wide; gallery cabinet has two shelves.
- Camera: zoom 2 (640 x 360 world pixels), wall 120, floor 232, after the
  owner asked for a wider, steeper view.
- Prices are a small plate on the floor in front of each machine
  (`price_tag.gd`), a placeholder until the owner decides how to show them.

- Store stripped to a bare set (owner, 2026-10-13: "we will change everything
  later"): `scripts/world/store.gd` went from about 1,700 lines to under
  500. Gone: `ambient.gd`, `swing.gd`, every ambient loop and its
  generators, lamps, decorative props, the GACHA sign, the power-on
  sequence, machine greetings and nudges, the in-hall prize animations
  (crank, claw, plinko), confetti, the shaking view. Kept: shell, zone
  doors, coins, switch, machines (off picture or idle loop, price, robots),
  figure cabinet, counter with computer and key, front door, sofa. Unused
  art left on disk: decor props, machine wake / play / react sheets,
  capsules, claw, ball, `machines/anchors.json`, the old `player_*` sheets.

Next, owner's direction (not started):

- [ ] The protagonist is the owner's own picture, `diseños/moneda1.png`
      (a 1 PESETA coin tipping its hat). After many prototype rounds the owner
      said (2026-10-13): forget the prototypes, work on moneda1 itself and
      make its poses and faces so it is as easy as possible to put in the
      game. `python tools/pixel/build_peseta.py` takes the picture apart
      (coin with hat, two gloves, two shoes), redraws its face for six
      expressions (normal, parpadeo, feliz, sorpresa, triste, enfado) and
      reassembles it with rubber-hose limbs into strips in the game's format:
      `assets/sprites/peseta/` with `anims.json` (`peseta_idle` 8 frames,
      `peseta_walk` 8, `peseta_use` 6, `peseta_cheer` 6, `peseta_wave` 1 = the
      picture itself; frames 232 x 222) and loose pieces under `parts/`.
      Contact sheet: `tools/pixel/previews/peseta_sheet.png`.
      WIRED IN (2026-10-13): `sprite_lib.gd` reads the `peseta` manifest and
      `scripts/world/player.gd` plays its strips through the `SKIN` table
      (game animation name -> strip), at a third of their size with linear
      filtering: one pixel of the picture is one pixel of a 1080p screen.
      Every strip also exists as `<name>_left` (mirrored, with the coin's 1
      struck the right way round); the player never flips the sprite, it
      plays the left strip. Borrowed for now: run = walk, stretch = cheer,
      shrug / watch / wave = the hat-tip picture, sleep = dozing upright.
      Owner's corrections applied since: limbs nearly straight with one soft
      curve; fists and shoes turned to how they lie in the picture
      (`FIST_LEAN`, `SHOE_LEAN`); legs straight down from hips set apart
      behind the coin; arms close to the body; the word PESETA removed, the 1
      kept; near leg shorter than the far leg (their call); walk on one shoe
      drawing rolled heel to toe. Owner's verdict at the last round:
      "muchísimo mejor".
      Then the owner asked for an intensive study of rubber hose drawing:
      `docs/art/rubber-hose-notes.md` holds the rules found, the coin checked
      against them and a ranked list of what is missing (twins at rest, hat
      that cannot lag, one fist for both hands, no squash and stretch).
      Known besides: the walk was judged on stills; the screen's 0.55
      saturation pass makes the already-desaturated coin greyer than the
      picture; a small black stump on the coin's left edge; a stray dot by
      the 1. The old `player_*` sheets are still in `assets/sprites/anim/`.
      Rejected rounds, kept only as history: `proto_hero.py`, `proto_cast.py`,
      `proto_coin.py`, `proto_peseta.py` (the last is imported by
      `build_peseta.py` for its limb drawing).
- [ ] Balance: `sim_balance.gd` fails on the default seed by one minute
      (181.1 min; seeds 7, 42, 3, 99 give 147-165, 7-9 rebirths). The key
      price is a step, not a slope: at 285M the same seed ends in 89 min with
      3 rebirths. Needs crane/plinko prices or sale factors retuned.
- [ ] With zoom 2 the bathroom and staff room are small strips in a dark
      screen and the floor is large and empty.
- [ ] `GACHA` sign, lamps and ambient positions were only nudged by eye.

Tests at stop (2026-10-13, bare store): `run_tests.gd` 360 checks pass,
`smoke_boot.gd` 135 pass (five checks of removed scenery dropped);
`sim_balance.gd` not rerun.

## State of the game

- Rules, economy, saving, balance: complete and tested; untouched by the art work.
- Three scenes joined by doors: bathroom, store (corridor, four machines, figure
  cabinet, reception), staff room. The store is 1000 world pixels wide.
- `E` at a machine steps inside it (`scripts/ui/machine_scene.gd`): played by
  hand, `Q`/`R` or `1`-`4` jump between machines, `Esc` back to the hall. Those
  scenes are still drawn with plain shapes.
- Art direction (owner, 2026-10-12): old rubber-hose cartoon like Cuphead or
  MOUSE: P.I. For Hire, sepia palette, more detailed pixels. Contract:
  `docs/art/art-contract-v3-sepia.md` (v2 beside it still defines file names,
  manifests and anchors). Palette: `tools/pixel/sepia.py`. References:
  `diseños/`.
- Redrawn textures are authored at 1.5 times their world size and drawn at
  two thirds (`ART_SCALE` in `scripts/world/sprite_lib.gd`); older ones are
  authored at world size and drawn as they are.
- Old-film pass over the whole screen: `scripts/ui/screen_grade.gd`.

## Sepia redesign: done (wave 1)

- [x] Code: art scale, film pass, door sprite hook, sepia tint of the machine scene.
- [x] Machines 001-006 with wake / idle / play / react sheets, capsules, claw,
      ball, `anchors.json` (`tools/pixel/machines.py`, `build_machines.py`).
- [x] Protagonist, worker robot, coins, capsule opening and effects
      (`tools/pixel/anim_*.py`, `build_anims.py`).

## Sepia redesign: to do (wave 2)

Until this is done the game mixes new art with old art shown at two-thirds
size (lamps, furniture, tiles, figures and bases look small and too colourful).

- [ ] Figures and bases — `tools/pixel/figures.py`, `bases.py`,
      `build_figures.py`; outputs `assets/sprites/figures/`, `assets/sprites/bases/`.
      Twenty figures at 60 x 60, an idle loop each (`fig_<id>_idle`, frame 0
      equal to the still), five bases at 84 x 45 with the feet point at
      (42, 18), rarity colours from `sepia.RARITY`. Silhouettes must stay distinct.
- [ ] Environment — `tools/pixel/props.py`, `tiles.py`, `build_environment.py`;
      outputs `assets/sprites/props/`, `assets/sprites/tiles/`. Tiles at
      24 x 24 (walls) and 24 x 15 (floors); every prop the compact store uses
      at 1.5 times its old size: toilet, sink, power switch (off/on), lamp
      (off/on), sofa, counter, computer (off/on, after `diseños/ordenador*.png`),
      front door (closed/open), locker, table, poster_b, sign_gacha, key, plant.
      New: `props/zone_door.png`, 45 x 96, a wooden door (the code already uses
      it when present). `build_environment.py` still reads machine frames at
      the old widths (48 and 72); they are 72 and 108 now.
- [ ] Ambient loops the store still places, at 1.5 times: `amb_tap_drip`,
      `amb_lantern`, `amb_plant_sway`, `amb_ceiling_fan`, `amb_exit_sign`,
      `amb_maneki_neko`, `amb_string_lights`, `amb_wall_clock`, `amb_fish_bowl`,
      `amb_mug_steam`, `amb_moth`, `amb_mouse_run`, `amb_dust_motes`
      (`tools/pixel/ambient_*.py`, `build_ambient.py`). The other 29 loops in
      `assets/sprites/ambient/` are unused: delete them or leave them out of
      the build.
- [ ] After wave 2: re-import, run the three suites, look at screenshots of
      every room (run the smoke test without `--headless` and with
      `GACHANIGHT_SHOT_DIR` set), check figure-on-base alignment in the prize
      panel and the catalog, and the claw and plinko paths against the new anchors.

## Known rough spots

- [ ] Plinko cabinet is an upright box, not the slanted wedge of `diseños/plinko.png`.
- [ ] Machine scenes (close-up) are plain shapes; they should get art in the
      new look, possibly straight from the reference drawings at this size.
- [ ] Robots still work in the hall while the player is inside a machine; the
      machine scene shows nothing of them.
- [ ] Hand play does not change the prize (the crane always grabs, the plinko
      ball ends in the slot already drawn). Owner has not decided whether skill
      should matter; it would change rules and balance.
- [ ] Zone doors are plain rectangles until `props/zone_door.png` exists.
- [ ] Bathroom and staff room are narrow strips in the middle of a dark screen.
- [ ] Gallery miniatures are a quarter of full size; the owner is fine with it for now.
- [ ] Walk animation runs about 1.8 times its drawn pace at the current walk speed (80 px/s).
- [ ] Sleeping pose, brows, open-hand gloves and the walk's passing pose are weak (animator's notes).
- [ ] Nobody has watched the animations move or listened to the audio.
- [ ] Balance was only validated by simulation; the Store Exit Key price is a sensitivity cliff.
- [ ] Before exporting a build: add `*.json` to the export filter.

## Owner's wish list (not started)

- [ ] New machines from `diseños/todolist.txt`: coin pusher, Skee-Ball.
      `diseños/pachinko.png` and `diseños/ruleta.png` suggest two more.
- [ ] Coins and purse in the HUD after `diseños/moneda*.png` and `cartera1.png`.

## Working agreements with the owner

- Never commit or push without being asked each time.
- Usage budget: do not pass 95%. The agent cannot read the meter: run art
  agents in small waves, tell them to work economically, and stop between
  waves to ask how much is left.
- Conversation in Spanish; everything in the repository in English
  (`GachaNight_MASTER_DESIGN.md` is the exception, in Spanish).
