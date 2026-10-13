# GachaNight — where things stand and what is next

Hand-off notes for continuing on another machine or in another session.
Last updated 2026-10-13.

## Set-up on a new machine

1. `git clone https://github.com/elgrako/gachanight-claude`
2. Godot 4.7 (standard build). First run: `godot --headless --path . --import`
   and let it finish, then `godot --path .`
3. Only to regenerate art: Python 3.13 with Pillow (`pip install pillow`).
4. Tests (all must pass before and after any change):
   - `godot --headless --path . -s tests/run_tests.gd` — 360 rule checks
   - `godot --headless --path . -s tests/smoke_boot.gd` — 147 scene checks
   - `godot --headless --path . -s tests/sim_balance.gd -- --seed=1987 --quiet`
5. Agent rules: `AGENTS.md` and `.codex/`. The `.orchestrator/` workspaces are
   not in git; the art contracts that matter were copied to `docs/art/`.
6. The save file is per machine (`user://gachanight_save.json`); a new machine
   starts a new game.

## Where the last session stopped (2026-10-13)

Everything below is committed and pushed to `main` (and the earlier part to
the `diseños` branch, which is now behind `main`). The entries that say
"uncommitted at the time of writing" were written as the work went; they are
all in git now. The owner still wants to be asked before every commit and push.

Open with the owner when the session ended:

- **Palette**: the third trial (25 muted sepia colours) stays "for now"; the
  owner may come back to it. See `docs/art/palette.md`.
- **Screen filter**: five looks on F3, none chosen yet.
- **Capsule machine view**: the pixel-art first-person view was just built
  and has not had the owner's reaction. Its art is by script; the owner said
  they will retouch the background themselves.
- **Story**: the ending is undecided; the last figure stands in for the key.
- Not looked at since the mechanics changed: the balance (`sim_balance.gd`
  was failing by a minute before today and was not rerun).

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

- Flat theatrical side view (owner, 2026-10-13; its curtain was dropped the
  same day, see the next entry): zoom 3 (427 x 240 world pixels, so one pixel of the coin's
  picture is one screen pixel at 720p), wall 188 tall, floor only 44 deep
  with boards fanning from each scene's middle, a dado and rail on the wall,
  bathroom and staff room widened to 300 and 270, store 1280 wide, and a
  proscenium fixed to the screen (`scripts/world/stage_frame.gd`: side
  curtains and a scalloped valance). A rough pass to try the style.

- Night interior after the owner's concept board (`diseños/GachaNight Retro
  Arcade Concept Board.png`), 2026-10-13, uncommitted at the time of
  writing: curtain removed (`stage_frame.gd` deleted); wall and floor are
  flat dark colours drawn in code (boarded wall with a dado, checkered floor
  in perspective), hanging lamps with additive halos, cones and floor pools
  that go out with the power, the GACHA sign and three posters, a black front
  edge with silhouettes, a stronger vignette (0.5 from 0.3). The coin is
  drawn at 0.27 of its strips (about 54 world pixels tall, was 67). The wall
  and floor tile pictures are no longer used. Owner said the board is close
  to what they want but not identical; machines with legs, one continuous
  room and the portrait HUD from the board were left out on purpose.

- Cellar (owner, 2026-10-13), uncommitted at the time of writing: a fourth
  scene at x 1280-1640, reached by stairs in the staff room (`ZONE_DOORS`
  rows now carry a kind: door, down, up). It holds the fuse box (the old
  power switch, same picture, moved from the corridor), the figure shelves
  (moved out of the store; each figure now stands in a cardboard box) and a
  poker table with two mice and a candle that burns with the power off
  (`tools/pixel/build_cellar.py` -> `props/poker_table.png`, a rough
  drawing by Claude, not the owner's). The store's old gallery room is now
  plain hall wall. Consequence for play: the first run starts in the dark
  and the player must cross the store and the staff room to reach the fuse.
  `smoke_boot.gd` is at 140 checks.

- Layout pass (owner, 2026-10-13), uncommitted at the time of writing: the
  staff-room door now stands right of the plinko (x 714); the counter moved
  left (x 852) with two shelves behind it and a hanging RECEPTION sign, so
  the front door (x 974) has nothing in front of it; the sofa moved left
  (x 1126), clear of the cellar stairs. "The door" was read as the
  staff-room door; the owner did not say which.
- The GitHub branch is now `diseños` (renamed from
  `coin-protagonist-bare-store`, which was deleted on the remote).

- New story (owner, 2026-10-13, "something like this, some part may still be
  retouched"): night job, the door locks itself, the manager has the only
  key, sleeping on the sofa restarts the night in the bathroom, the goal is
  every collection, the last figure is a secret replica of the protagonist,
  and the store was completing its own collection. Written into section
  2 bis of `GachaNight_MASTER_DESIGN.md` with a table of what it replaces
  and nine open questions for the owner; README has a short version.
  **Documents only: no game code changed.** The game still ends by buying
  `store_exit_key` and opening the door.
- Owner's answers the same day (recorded in 2 bis): the first night starts
  at the entrance as a new employee, who later falls asleep in the bathroom;
  collections stay per run; for now the secret figure takes the key's place
  as the last reception upgrade; the ending itself is undecided; the front
  door is used only in the opening animation and stays shut until the end;
  the manager exists only in the note; Free Play stays; the computer gives
  no instructions and is a secondary character with its own arc (remembers
  across restarts, not evil, falls silent mid-congratulation). The owner
  said "ask me if you have more doubts": three were asked (see chat) before
  touching code.

- Opening and last figure implemented (owner's second answers, 2026-10-13),
  uncommitted at the time of writing. First launch (`perm.intro_seen`
  false): the player stands at the front door, which shuts behind them, the
  store is lit, nothing can be used; the sofa gives a nap with no menu and
  the player wakes by the sofa in the dark. `Store.SPAWN` is now by the
  sofa for every night, the three floor coins are in the staff room, the
  bathroom is scenery only. With no power the reception shows the manager's
  note (`perm.note_read`). The exit key is shown as "The Last Figure" (same
  id, same rules); buying it opens the front door on daylight, and walking
  out still plays the old ending, as a placeholder: the owner has not
  decided the ending. The computer got general lines by phase of the night
  (`reception_panel.gd`, `greet_again` / `greet_late` / `greet_near`, and a
  congratulation cut mid-word); the owner will rewrite them.
  `smoke_boot.gd` 148 checks, `run_tests.gd` 360. An existing save plays the
  opening once too. One smoke run produced all-black screenshots after the
  first; the rerun was fine and the checks passed both times (cause not
  found, likely the window being covered).

- Cellar dressing (owner, 2026-10-13), uncommitted at the time of writing:
  the figure shelves are an old slotted-steel stock rack (uprights with
  bolt slots, steel decks, cross brace, rust) with cartons and a wire bin of
  loose capsules on its lower decks; the cellar wall has brick courses,
  ceiling pipes, a small barred window with a moon, a cobweb and a
  "STOCK - DO NOT OPEN" stencil. All drawn in code in `store.gd`
  (`_build_cabinet`, `_build_cellar_details`).

- Coin icon (owner, 2026-10-13), uncommitted at the time of writing: the
  game's coin is the face of `diseños/moneda_oro1.png` (the protagonist in
  gold), cut with its hat and without limbs by
  `tools/pixel/build_coin_icon.py` into `assets/sprites/ui/`. The purse
  moved to the top left of the screen: that face and the bare amount. The
  bottom-left plate now only holds the prestige and status lines and hides
  when both are empty. The floor coins, the price plates and the panels
  still use their old coin drawings.

- Stock rack (owner, 2026-10-13: "a display case in the cellar makes no
  sense"), uncommitted at the time of writing: no figure shows in the cellar
  any more, only one closed carton per figure; a found figure's carton gets
  a small sticker (Claude's addition, not asked for). Using the rack
  (`store.stock`, "[E] Check the stock") opens the catalog, which is the
  record of figures; Tab still opens it anywhere.

- Reception (owner, 2026-10-13), uncommitted at the time of writing. Art
  direction stated by the owner: **rubber hose comes first, retro Japan
  second: "as if old Disney cartoons had been drawn in Japan"**. The
  computer is the owner's `diseños/ordenador.png`, with
  `ordenador_kawai.png` as its delighted mood (shown when the player
  stands at the counter, and in the sales terminal when it sells) and a
  dark-screen version made from the first for no power
  (`tools/pixel/build_reception.py` -> `props/pc_on`, `pc_kawai`,
  `pc_off`). The shelves behind the counter are gone. The counter is old
  dark wood with panels and a brass coin (`props/counter_wood.png`, drawn
  by Claude). The old counter's kana were dropped rather than copied: the
  copy lost a stroke and changed the word.

- Palette trials and the owner's first machine (2026-10-13), uncommitted at
  the time of writing. See `docs/art/palette.md`. First trial: 22 colours
  from the coin and the machine picture. The owner then asked for more
  sepia and brown, a smaller palette, on absolutely everything: second
  trial, 16 colours (7 neutrals from the coin, 4 browns, 5 muted accents),
  applied to every generated sprite (`tools/pixel/apply_palette.py`, run on
  the originals restored from git), to the owner's machine, computer and
  coin icon by their builders, and to every colour written in `scripts/`
  (set, HUD, panels). Still a trial: `git checkout -- assets/sprites
  scripts` undoes it.
  Third trial the same day, on the owner's word ("a wider range but tones
  turned down, no blues or reds, more sepia, saturation 0.55 like my
  pictures"): 25 colours, sources desaturated to 0.55 before mapping. This
  is what is on disk now. The owner asked for no testing on this round
  (nothing mechanical changed); a smoke run was made only for screenshots
  and passed.
  Capsule Machine No. 1 is now the owner's `maquina1.png`, pixel for pixel
  in drawing, its colours moved to the palette
  (`tools/pixel/build_maquina1.py`): eyes shut with no power, a 36-frame
  idle that breathes and blinks. No. 2 is the same picture with the body
  turned plum and teal, a stand-in until the owner draws it. Both are
  54 x 85 world pixels now. The crane and the plinko are still the old
  generated art and look out of place next to them. The owner removed eight
  reference pictures from `diseños/` (their own doing, not committed yet).

- Screen filters to try (owner, 2026-10-13: "not too strong, but giving the
  retro touch"), uncommitted at the time of writing. The palette of the
  third trial stays for now ("we may touch it later"). `screen_grade.gd`
  keeps five looks side by side and **F3 steps through them in the running
  game**, showing the name: No filter, Old reel (what the game had, and the
  one shown first), Projector (flicker, a hair of gate weave, glow, rounded
  corners), Picture tube (faint scan lines, glow, rounded glass), Printed
  page (still grain, blotchy paper). The choice is not saved between
  launches. The owner has not picked one yet; when they do, make it
  `START_LOOK` and decide whether the others and the F3 key stay.

- Capsule machine mechanics, first prototype (owner, 2026-10-13),
  uncommitted at the time of writing. Reference for the view:
  `diseños/maquinapov1.gif` (another artist's animation, a reference only,
  never to be shipped). In `machine_scene.gd` a capsule machine is now seen
  in first person: its own picture at 4x in the middle (breathing, shaking
  while the crank turns, hopping on a perfect stop, a coin flying to the
  slot, the capsule popping out), a panel on the left with the upgrades
  sold at that machine (mouse or Z X C), and a timing wheel on the right.
  **Rule change:** E starts the wheel (nothing paid yet), E again stops it,
  pays and rolls; the stop is graded PERFECT / GREAT / GOOD / MISS and adds
  60 / 30 / 12 / 0 % luck to that one play (`Machine.effective_weights`,
  `play_machine(machine_id, extra_luck_pct)`, capped at 60). New reception
  category `machine` with a `machine_id`: three items each for machines 001
  and 002 (wider sweet spot, slower wheel, luck at that machine), bought at
  the machine, hidden from the terminal, lost on rebirth like everything
  bought with coins. All numbers are first guesses. Not done: the crane and
  the plinko keep their old scenes; robots and the simulated player earn no
  timing luck; `sim_balance.gd` was not rerun and the balance was not
  looked at; the background is left plain for the owner to redo.
  `run_tests.gd` 360, `smoke_boot.gd` 147.

- Capsule machine view, second pass (owner, 2026-10-13: closer, almost
  first person, the dome as the background, the crank in view, the prize
  mouth at the bottom and the coin slot a little above; everything pixel
  art, the skill check included; the menu elegant, in a darkish green, with
  old-detective details), uncommitted at the time of writing. New
  `scripts/ui/gacha_pov.gd` draws it in a 320 x 180 viewport shown at 4x, so
  every shape lands on one pixel grid, with its own 5 x 7 pixel alphabet
  (upper case only). Pictures by `tools/pixel/build_pov.py` into
  `assets/sprites/pov/`: drawn by script on the palette, **not the owner's
  art** (the owner's machine picture is no longer shown in this view). Left:
  the upgrades as a case file (magnifying glass, paper clip, typed rows with
  level pips, a "LOST ON SLEEP" rubber stamp). Right: the timing wheel as a
  pocket watch. `machine_scene.gd` keeps the state and the rules of the
  first pass; its own labels and tab bar are hidden on capsule machines
  (Q / R, the number keys and Esc still work). Upgrade "Wider Sweet Spot"
  renamed "Wider Mark" to fit a line. Seen in two stills (idle, wheel
  turning); crank, coin, capsule and the perfect hop were not seen moving.

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

Tests at stop (2026-10-13, end of session): `run_tests.gd` 360 checks pass,
`smoke_boot.gd` 147 pass; `sim_balance.gd` not rerun.

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
