extends SceneTree
## Boots the real main scene and drives one full loop through the same
## interaction and UI paths the player uses. Run with:
##   godot --headless --path . -s tests/smoke_boot.gd
## Without --headless, set GACHANIGHT_SHOT_DIR to also save screenshots there.

const SAVE_PATH: String = "user://test_smoke.json"
const Sprites = preload("res://scripts/world/sprite_lib.gd")
const FigureIcon = preload("res://scripts/ui/figure_icon.gd")
## Ambient animations that code moves about instead of the placement table.
const AMBIENT_MOVERS: Array = ["amb_moth", "amb_mouse_run", "amb_windup_toy", "amb_capsule_roll", "amb_toy_train", "amb_dust_motes"]

var _checks: int = 0
var _failures: Array = []
var _shot_dir: String = ""


func _initialize() -> void:
	_run()


func check(condition: bool, message: String) -> void:
	_checks += 1
	if not condition:
		_failures.append(message)


func frames(count: int) -> void:
	for index in range(count):
		await process_frame


func shot(shot_name: String) -> void:
	if _shot_dir == "":
		return
	await frames(3)
	root.get_texture().get_image().save_png("%s/%s.png" % [_shot_dir, shot_name])


func _run() -> void:
	await process_frame
	if DisplayServer.get_name() != "headless":
		_shot_dir = OS.get_environment("GACHANIGHT_SHOT_DIR")
	var game: Node = root.get_node_or_null("Game")
	check(game != null, "Game autoload exists")
	if game == null:
		_finish()
		return
	# Never touch the player's real save: point the core at a scratch file first.
	for suffix in ["", ".bak", ".tmp", ".unreadable"]:
		if FileAccess.file_exists(SAVE_PATH + suffix):
			DirAccess.remove_absolute(SAVE_PATH + suffix)
	check(game.core.setup(SAVE_PATH), "core set up on a scratch save")
	var core: RefCounted = game.core
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await frames(5)
	var store: Node2D = main.store
	var ui: CanvasLayer = main.ui
	check(main.player != null and store != null and ui != null, "scene built")
	check(main.player.global_position.distance_to(store.SPAWN) < 2.0, "player starts in the bathroom")
	check(is_equal_approx(main.camera.zoom.x, 3.0), "the camera shows the world at three screen pixels per pixel")
	var view_height: float = 720.0 / main.camera.zoom.y
	check(main.camera.position.y - view_height / 2.0 <= store.VIEW_TOP + 0.5 and main.camera.position.y + view_height / 2.0 >= store.VIEW_BOTTOM - 0.5, "wall top and floor ledge both fit in the view")
	await frames(20)
	check(main.player.focused_interactable() == null, "nothing to use at the spawn point")
	await shot("01_bathroom_dark")

	# Walking right leads out of the bathroom into the corridor; the store ends in a wall.
	Input.action_press("move_right")
	await create_timer(3.2).timeout
	Input.action_release("move_right")
	await frames(3)
	check(main.player.global_position.x > store.room_range("corridor").x, "player can walk from the bathroom into the corridor")
	check(absf(main.player.global_position.y - store.SPAWN.y) < 0.01, "walking sideways keeps the player's depth")
	check(main.player.z_index == store.floor_z(main.player.position.y), "the player is depth-sorted by the floor line")

	# Two axes: towards the camera, then away from it until the back wall.
	var area: Rect2 = store.WALK_AREA
	var depth_before: float = main.player.global_position.y
	Input.action_press("move_back")
	await create_timer(0.6).timeout
	Input.action_release("move_back")
	await frames(3)
	check(main.player.global_position.y > depth_before + 8.0, "S walks towards the camera")
	check(main.player.z_index > store.floor_z(depth_before), "nearer means drawn later")
	Input.action_press("move_forward")
	await create_timer(4.0).timeout
	Input.action_release("move_forward")
	await frames(3)
	check(absf(main.player.global_position.y - area.position.y) < 0.01, "W walks away until the back wall stops the player")
	_go(main, Vector2(area.end.x - 4.0, 60.0))
	Input.action_press("move_right")
	Input.action_press("move_back")
	await create_timer(3.4).timeout
	Input.action_release("move_right")
	Input.action_release("move_back")
	check(main.player.global_position.x <= area.end.x and main.player.global_position.y <= area.end.y, "the end wall and the floor's edge stop the player")
	check(absf(main.player.global_position.y - area.end.y) < 0.01, "the player reaches the near edge of the floor")

	# A machine's footprint is solid; the gap beside it is not.
	var machine_at: Vector2 = store.machines["machine_001"]["at"]
	_go(main, machine_at + Vector2(0.0, 30.0))
	Input.action_press("move_forward")
	await create_timer(1.6).timeout
	Input.action_release("move_forward")
	await frames(3)
	var stopped_y: float = main.player.global_position.y
	check(stopped_y > machine_at.y and stopped_y < machine_at.y + 10.0, "the machine's footprint blocks the player in front of it")
	check(main.player.z_index > store.machines["machine_001"]["root"].z_index, "the player in front of a machine is drawn over it")
	_go(main, Vector2(machine_at.x + 35.0, machine_at.y + 30.0))
	Input.action_press("move_forward")
	await create_timer(1.6).timeout
	Input.action_release("move_forward")
	await frames(3)
	check(main.player.global_position.y < machine_at.y, "the player can walk into the gap between two machines")
	check(main.player.z_index < store.machines["machine_001"]["root"].z_index, "the player behind a machine's front is drawn under it")
	for item in store.interactables:
		_go(main, item.use_point())
		check(main.player.focused_interactable() == item, "%s can be reached" % item.name)
	_go(main, store.SPAWN)
	await frames(2)

	# The gallery shows every figure; nothing is discovered yet, so no base at all.
	check(store.gallery.size() == core.data.figure_order.size(), "the gallery holds every figure")
	check(_gallery_bases(store) == 0, "undiscovered figures stand without a base")
	check(store.gallery[core.data.figure_order[0]]["figure"].modulate == store.SILHOUETTE, "undiscovered figures are dark silhouettes")
	check(_silhouettes_still(store, core), "undiscovered figures show their still picture, not a loop")
	check(_gallery_fits(store, core.data.figure_order.size()) == "", "every gallery spot is whole, inside the wall and clear of the lamps: %s" % _gallery_fits(store, core.data.figure_order.size()))
	check(_unplaced_ambient(store).is_empty(), "every ambient animation has a place: %s" % str(_unplaced_ambient(store)))
	_go(main, Vector2(1010.0, 60.0))
	await shot("01b_gallery_dark")
	_go(main, store.SPAWN)
	# The HUD keeps to the front of the floor: price signs are never under it,
	# and its own parts never meet.
	check(_price_signs_ok(main) == "", "every machine shows its price on a sign clear of the HUD: %s" % _price_signs_ok(main))
	_go(main, store.machines["machine_001"]["body"].use_point())
	ui.toast("Not enough coins. This one costs 250000.")
	await frames(4)
	var hud: Dictionary = ui.hud_rects()
	check(hud.has("prompt") and hud.has("keys") and hud.has("toast"), "prompt, toast and key hint show at a machine")
	check(_hud_overlaps(hud) == "", "no two HUD elements overlap: %s" % _hud_overlaps(hud))
	var screen: Rect2 = Rect2(Vector2.ZERO, main.get_viewport().get_visible_rect().size)
	check(hud.values().all(func(rect: Rect2) -> bool: return screen.encloses(rect)), "the whole HUD is on the screen")
	check(hud.values().all(func(rect: Rect2) -> bool: return rect.position.y > screen.size.y * 0.6), "the HUD keeps to the front of the floor")
	await shot("01c_hud_prompt")
	_go(main, store.SPAWN)

	# Bathroom: coins, then the switch.
	check(not ui.is_modal_open(), "no panel at start")
	for coin in store.coins:
		coin.interact()
	check(core.run.coins == 3, "three floor coins picked up")
	check(not store.coins[0].visible, "collected coin disappears")
	store.machines["machine_001"]["body"].interact()
	check(not core.run.has_pending_prize(), "machine does nothing without power")
	var first: Dictionary = store.machines["machine_001"]
	check(first["off"].visible and not first["anim"].visible, "a machine without power shows its off sprite")
	store.power_switch.interact()
	check(core.run.power_switch_on, "switch turns the power on")
	await create_timer(2.4).timeout
	check(first["anim"].visible and not first["off"].visible, "machines wake up with the power")
	check(first["anim"].animation == "machine_001_idle" and first["anim"].is_playing(), "an awake machine loops its idle animation")
	check(store.machines["machine_006"]["anim"].visible, "the last machine is awake too")
	_go(main, Vector2(400.0, 50.0))
	await shot("02_hall_lit")

	# First spin: sell through the real button.
	core.rand_fn = func() -> float: return 0.0
	store.machines["machine_001"]["body"].interact()
	check(core.run.coins == 2, "spin paid once")
	await create_timer(1.5).timeout
	check(ui.open_modal_name() == "prize", "prize panel opens after the crank")
	var won_id: String = core.pending_prize_view()["figure_id"]
	check(store.gallery[won_id]["base"] != null and store.gallery[won_id]["base"].visible, "the discovered figure stands on a base in the gallery")
	check(store.gallery[won_id]["base"].animation == "base_%s" % core.figure_view(won_id)["rarity_id"], "the base is the one of the figure's rarity")
	check(store.gallery[won_id]["figure"].modulate == Color.WHITE, "the discovered figure is shown in colour")
	var won_sprite: AnimatedSprite2D = store.gallery[won_id]["figure"]
	check(won_sprite.animation == Sprites.FIGURE_IDLE and won_sprite.is_playing(), "the discovered figure plays its idle loop in the gallery")
	check(Sprites.has_figure_idle(won_id) == (won_sprite.sprite_frames.get_frame_count(Sprites.FIGURE_IDLE) > 1), "the loop is the drawn one when there is one, else the still picture")
	check(_silhouettes_still(store, core), "figures not discovered yet stay still")
	check(ui.prize_panel.figure_view.animated == Sprites.has_figure_idle(won_id), "the prize panel plays the idle loop after the reveal")
	check(_gallery_bases(store) == core.discovered_count(), "only discovered figures have a base")
	check(ui.prize_panel.figure_view.base != null, "the prize stands on its rarity base")
	check(not ui.prize_panel.keep_button.disabled, "Keep allowed with 2 coins left")
	await shot("03_prize_panel")
	if _shot_dir != "":
		# The capsule has burst and the figure plays its loop on the base.
		await create_timer(1.3).timeout
		await shot("03a_prize_revealed")
	ui.prize_panel.sell_button.pressed.emit()
	check(core.run.coins == 3, "Sell button credits the sale")
	check(not ui.is_modal_open(), "panel closes after selling")
	ui.prize_panel.sell_button.pressed.emit()
	check(core.run.coins == 3, "a second click sells nothing")

	# Low funds: Keep is disabled, and closing the panel keeps the prize.
	core.run.coins = 2
	store.machines["machine_001"]["body"].interact()
	await create_timer(1.5).timeout
	check(ui.prize_panel.keep_button.disabled, "Keep disabled with 1 coin left")
	ui.close_modal()
	check(core.run.has_pending_prize(), "closing the panel keeps the prize pending")
	store.machines["machine_002"]["body"].interact()
	check(ui.open_modal_name() == "prize", "any machine reopens the pending prize")
	await shot("03b_prize_on_base")
	ui.prize_panel.keep_button.pressed.emit()
	check(core.run.has_pending_prize(), "disabled Keep resolves nothing")
	ui.prize_panel.sell_button.pressed.emit()
	check(not core.run.has_pending_prize(), "prize sold")

	# Catalog and locked sofa.
	ui.toggle_catalog()
	check(ui.open_modal_name() == "catalog", "catalog opens")
	check(_catalog_loops(ui.catalog_panel, core) == "", "the catalog animates discovered figures only: %s" % _catalog_loops(ui.catalog_panel, core))
	await shot("04_catalog")
	ui.toggle_catalog()
	store.sofa.interact()
	check(not ui.is_modal_open(), "sofa is locked before machine 002")

	# Machine 002 unlocks the sofa; Cancel spends nothing.
	core.run.coins = core.machine_price("machine_002") + 10
	store.machines["machine_002"]["body"].interact()
	await create_timer(1.5).timeout
	ui.prize_panel.sell_button.pressed.emit()
	check(core.is_prestige_unlocked(), "machine 002 unlocks prestige")
	# Amounts come from the data tables so a rebalance does not break this test.
	var appraisal_cost: int = core.data.prestige_upgrades["better_appraisal"]["prestige_cost_curve"][0]
	core.perm.banked_prestige = appraisal_cost + 5
	store.sofa.interact()
	check(ui.open_modal_name() == "sofa", "sofa menu opens")
	ui.sofa_panel.row_buttons["better_appraisal"]["plus"].pressed.emit()
	await shot("05_sofa")
	ui.sofa_panel.cancel_button.pressed.emit()
	check(not ui.is_modal_open(), "Cancel closes the sofa menu")
	check(core.perm.banked_prestige == appraisal_cost + 5 and core.perm.total_rebirths == 0, "Cancel spends nothing")

	# Sleep & Rebirth through the real button.
	store.sofa.interact()
	ui.sofa_panel.row_buttons["better_appraisal"]["plus"].pressed.emit()
	ui.sofa_panel.confirm_button.pressed.emit()
	await create_timer(2.5).timeout
	check(core.perm.total_rebirths == 1, "rebirth confirmed")
	check(core.perm.banked_prestige == 5, "the upgrade is paid, the rest banked")
	check(core.perm.upgrade_level("better_appraisal") == 1, "upgrade applied")
	check(not core.run.power_switch_on, "new run starts with the power off")
	check(store.coins[0].visible, "floor coins are back")
	check(main.player.global_position.distance_to(store.SPAWN) < 2.0, "player wakes up in the bathroom")
	check(not ui.is_modal_open() and main.player.controls_enabled, "control returns to the player")

	# Second run: the sales terminal, a robot, the crane, plinko, the key and the door.
	store.reception.interact()
	check(not ui.is_modal_open(), "the terminal needs power")
	store.power_switch.interact()
	store.door.interact()
	check(not ui.is_modal_open() and not core.perm.story_completed, "the door is locked without the key")
	core.run.coins = 1000
	store.machines["machine_001"]["body"].interact()
	await create_timer(1.5).timeout
	ui.prize_panel.sell_button.pressed.emit()
	check(store.machines["machine_001"]["affordable"] and store.machines["machine_001"]["price"].affordable, "a machine the player can pay for lights its price sign")
	check(not store.machines["machine_004"]["affordable"] and not store.machines["machine_004"]["price"].affordable, "a machine that costs too much keeps its sign dull")
	store.reception.interact()
	check(ui.open_modal_name() == "reception", "the sales terminal opens")
	ui.reception_panel.buy_buttons["price_tag_gun"].pressed.emit()
	check(core.run.reception_level("price_tag_gun") == 1, "BUY purchases an upgrade with coins")
	ui.reception_panel.tab_buttons["automation"].pressed.emit()
	ui.reception_panel.buy_buttons["robot_machine_001"].pressed.emit()
	check(core.robot_view("machine_001")["count"] == 1, "BUY purchases a robot")
	await shot("06_reception")
	ui.reception_panel.close_button.pressed.emit()
	check(not ui.is_modal_open(), "LEAVE closes the terminal")
	check(store.machines["machine_001"]["robots"][0].visible, "the robot stands by its machine")
	var spins_before: int = core.run.total_spins
	await create_timer(1.3 / core.robot_view("machine_001")["spins_per_second"]).timeout
	check(core.run.total_spins > spins_before, "the robot spins on its own")
	_go(main, Vector2(350.0, 60.0))
	await shot("07_machine_row")
	# A look at every room with the lights on.
	var tour: Dictionary = {"11_bathroom": Vector2(90.0, 60.0), "12_corridor": Vector2(300.0, 70.0), "13_hall_right": Vector2(650.0, 50.0), "14_gallery_left": Vector2(1020.0, 60.0), "15_gallery_mid": Vector2(1340.0, 70.0), "15b_gallery_right": Vector2(1650.0, 70.0), "16_reception": Vector2(1955.0, 90.0), "17_staff": Vector2(2140.0, 60.0)}
	for shot_name in tour:
		_go(main, tour[shot_name])
		await create_timer(0.3).timeout
		await shot(shot_name)
	# Presentation that is otherwise only seen in passing.
	_go(main, Vector2(store.DOOR_X, 40.0))
	store.play_door_open()
	await create_timer(1.1).timeout
	await shot("18_door_open")
	store.reset_door()
	_go(main, store.sofa.global_position + Vector2(0.0, 40.0))
	main.player.sleep_at(store.sofa.global_position + store.SOFA_SEAT)
	await create_timer(0.3).timeout
	check(main.player.is_sleeping(), "the player can lie down on the sofa")
	await shot("19_sofa_sleep")
	_go(main, Vector2(400.0, 60.0))
	store.celebrate(main.player.position)
	await create_timer(0.5).timeout
	await shot("20_celebration")
	await create_timer(1.6).timeout

	core.run.coins = core.machine_price("machine_005") * 3
	_go(main, store.machines["machine_005"]["body"].use_point())
	store.machines["machine_005"]["body"].interact()
	await create_timer(1.6).timeout
	await shot("08a_crane_moving")
	await create_timer(1.4).timeout
	check(ui.open_modal_name() == "prize", "the crane hands over a prize")
	await shot("08_crane_prize")
	ui.prize_panel.sell_button.pressed.emit()
	core.run.coins = core.machine_price("machine_006") * 3
	store.machines["machine_006"]["body"].interact()
	await create_timer(2.6).timeout
	check(ui.open_modal_name() == "prize", "plinko hands over a prize")
	ui.prize_panel.sell_button.pressed.emit()
	for machine_id in ["machine_002", "machine_003", "machine_004"]:
		core.run.coins = core.machine_price(machine_id) * 3
		var played: Dictionary = core.play_machine(machine_id)
		core.resolve_prize(played["prize"]["transaction_id"], "sell")
	core.run.coins = core.reception_item_view("store_exit_key")["cost"] * 2
	store.reception.interact()
	ui.reception_panel.tab_buttons["exit"].pressed.emit()
	ui.reception_panel.buy_buttons["store_exit_key"].pressed.emit()
	check(core.run.key_owned_this_run, "the key is bought at the terminal")
	check(not store._key.visible, "the bought key is gone from the counter")
	check(not core.perm.story_completed, "buying the key is not the ending")
	ui.reception_panel.close_button.pressed.emit()
	store.door.interact()
	await create_timer(2.4).timeout
	check(ui.open_modal_name() == "ending", "the door starts the ending")
	check(core.perm.story_completed and core.perm.free_play_unlocked, "story completed, Free Play unlocked")
	await create_timer(4.0).timeout
	await shot("09_ending")
	ui.ending_panel.skip()
	await shot("10_credits")
	ui.ending_panel.continue_button.pressed.emit()
	check(not ui.is_modal_open() and main.player.controls_enabled, "Continue returns to the store")
	store.door.interact()
	await create_timer(0.5).timeout
	check(not ui.is_modal_open(), "the ending does not replay")
	_finish()


## Puts the player on a floor point and the camera over it.
func _go(main: Node, at: Vector2) -> void:
	main.player.place(at)
	main.camera.position.x = at.x
	main.camera.reset_smoothing()


## True when every figure not discovered yet shows its still picture, stopped.
func _silhouettes_still(store: Node2D, core: RefCounted) -> bool:
	for figure_id in store.gallery:
		if core.figure_view(figure_id)["discovered"]:
			continue
		var sprite: AnimatedSprite2D = store.gallery[figure_id]["figure"]
		if sprite.animation != Sprites.FIGURE_STILL or sprite.is_playing() or sprite.modulate != store.SILHOUETTE:
			return false
	return true


## "" when every gallery spot can hold a figure on its base (58 px tall, 56 px
## wide) under the cornice, inside the room, without touching a neighbour, the
## other row or a lamp; else what is wrong.
func _gallery_fits(store: Node2D, count: int) -> String:
	var room: Vector2 = store.room_range("gallery")
	var stack: Vector2 = Vector2(Sprites.BASE_SIZE.x, Sprites.FIGURE_SIZE.y + Sprites.BASE_SIZE.y - Sprites.BASE_STAND.y)
	var rects: Array = []
	for index in range(count):
		var foot: Vector2 = store.gallery_spot(index)
		var rect: Rect2 = Rect2(foot.x - stack.x / 2.0, foot.y - stack.y, stack.x, stack.y)
		if rect.position.y < store.WALL_TOP + store.CORNICE_HEIGHT:
			return "spot %d reaches into the cornice" % index
		if rect.position.x < room.x + store.PILLAR_WIDTH / 2.0 or rect.end.x > room.y - store.PILLAR_WIDTH / 2.0:
			return "spot %d leaves the room" % index
		for other in rects:
			if rect.intersects(other):
				return "spot %d overlaps another" % index
		for lamp in store.lamp_points():
			if absf(lamp.x - foot.x) < (stack.x + store.LAMP_SIZE.x) / 2.0:
				return "spot %d is under a lamp" % index
		rects.append(rect)
	return ""


## Ambient animations of the manifest that are nowhere in the store.
func _unplaced_ambient(store: Node2D) -> Array:
	var shown: Dictionary = {}
	for item in store.ambient.placed:
		shown[item["anim"]] = true
	var missing: Array = []
	for anim_name in Sprites.manifest():
		if str(anim_name).begins_with("amb_") and Sprites.has_animation(anim_name) and not shown.has(anim_name) and not AMBIENT_MOVERS.has(anim_name):
			missing.append(anim_name)
	return missing


## "" when every machine has a price sign with its amount on the wall, under
## the cornice, and never under the HUD with the camera on that machine.
func _price_signs_ok(main: Node) -> String:
	var store: Node2D = main.store
	for machine_id in store.machines:
		var price: Node2D = store.machines[machine_id]["price"]
		if not price.visible or price.text == "":
			return "%s has no price" % machine_id
		var board: Rect2 = price.board_rect()
		if board.position.y < store.WALL_TOP + store.CORNICE_HEIGHT or board.end.y > 0.0:
			return "%s: the sign is off the wall" % machine_id
		_go(main, store.machines[machine_id]["at"] + Vector2(0.0, 40.0))
		var on_canvas: Rect2 = main.get_viewport().get_canvas_transform() * board
		var hud: Dictionary = main.ui.hud_rects()
		for part in hud:
			if hud[part].intersects(on_canvas):
				return "%s: the sign is under the HUD (%s)" % [machine_id, part]
	return ""


## "" when no two of the HUD rectangles meet; else the pair that does.
func _hud_overlaps(rects: Dictionary) -> String:
	var names: Array = rects.keys()
	for first in range(names.size()):
		for second in range(first + 1, names.size()):
			if rects[names[first]].intersects(rects[names[second]]):
				return "%s and %s" % [names[first], names[second]]
	return ""


## "" when the catalog plays an idle loop for exactly the discovered figures
## that have one; else the first wrong icon.
func _catalog_loops(panel: Node, core: RefCounted) -> String:
	var icons: Array = panel.find_children("*", "Control", true, false).filter(func(node: Node) -> bool: return node.get_script() == FigureIcon)
	if icons.size() != core.data.figure_order.size():
		return "%d icons" % icons.size()
	var discovered: int = 0
	for icon in icons:
		if icon.silhouette and (icon.animated or icon.is_processing() or icon.base != null):
			return "a silhouette is animated or has a base"
		if not icon.silhouette:
			discovered += 1
	if discovered != core.discovered_count():
		return "%d icons in colour" % discovered
	return ""


## How many gallery figures stand on a visible base.
func _gallery_bases(store: Node2D) -> int:
	var count: int = 0
	for figure_id in store.gallery:
		var base: Node = store.gallery[figure_id]["base"]
		if base != null and base.visible:
			count += 1
	return count


func _finish() -> void:
	print("")
	if _failures.is_empty():
		print("SMOKE PASSED: %d checks" % _checks)
		quit(0)
	else:
		for failure in _failures:
			print("FAIL  %s" % failure)
		print("SMOKE FAILED: %d of %d checks" % [_failures.size(), _checks])
		quit(1)
