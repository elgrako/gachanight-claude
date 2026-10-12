# GachaNight — where things stand and what is next

Hand-off notes for continuing on another machine or in another session.
Last updated 2026-10-12.

## Set-up on a new machine

1. `git clone https://github.com/elgrako/gachanight-claude`
2. Godot 4.7 (standard build). First run: `godot --headless --path . --import`
   and let it finish, then `godot --path .`
3. Only to regenerate art: Python 3.13 with Pillow (`pip install pillow`).
4. Tests (all must pass before and after any change):
   - `godot --headless --path . -s tests/run_tests.gd` — 374 rule checks
   - `godot --headless --path . -s tests/smoke_boot.gd` — 146 scene checks
   - `godot --headless --path . -s tests/sim_balance.gd -- --seed=1987 --quiet`
5. Agent rules: `AGENTS.md` and `.codex/`. The `.orchestrator/` workspaces are
   not in git; the art contracts that matter were copied to `docs/art/`.
6. The save file is per machine (`user://gachanight_save.json`); a new machine
   starts a new game.

## State of the game

- Rules, economy, saving, balance: complete and tested; untouched by the art work.
- Three scenes joined by doors: bathroom, store (corridor, six machines, figure
  cabinet, reception), staff room. The store is 1130 world pixels wide.
- `E` at a machine steps inside it (`scripts/ui/machine_scene.gd`): played by
  hand, `Q`/`R` or `1`-`6` jump between machines, `Esc` back to the hall. Those
  scenes are still drawn with plain shapes.
- Art direction (owner, 2026-10-12): old rubber-hose cartoon like Cuphead or
  MOUSE: P.I. For Hire, sepia palette, more detailed pixels. Contract:
  `docs/art/art-contract-v3-sepia.md` (v2 beside it still defines file names,
  manifests and anchors). Palette: `tools/pixel/sepia.py`. References:
  `diseños/`.
- Every texture is authored at 1.5 times its world size and drawn at two
  thirds (`ART_SCALE` in `scripts/world/sprite_lib.gd`).
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
      Thirty figures at 60 x 60, an idle loop each (`fig_<id>_idle`, frame 0
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
