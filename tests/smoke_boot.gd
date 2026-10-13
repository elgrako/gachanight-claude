extends SceneTree
## Boots the real main scene and drives one full loop through the same
## interaction and UI paths the player uses. Run with:
##   godot --headless --path . -s tests/smoke_boot.gd
## Without --headless, set GACHANIGHT_SHOT_DIR to also save screenshots there.

const SAVE_PATH: String = "user://test_smoke.json"
const Sprites = preload("res://scripts/world/sprite_lib.gd")
const FigureIcon = preload("res://scripts/ui/figure_icon.gd")



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
	# The opening: in through the front door with the lights on, nothing to
	# do but look around, then a nap on the sofa and waking up in the dark.
	check(main.player.global_position.distance_to(store.door.use_point()) < 2.0, "the first evening starts at the front door")
	check(store.machines["machine_001"]["anim"].visible, "the store is lit on the first evening")
	check(not store.coins[0].visible, "no coins on the floor yet")
	await shot("00_arrival")
	store.machines["machine_001"]["body"].interact()
	store.reception.interact()
	store.door.interact()
	check(not ui.is_modal_open() and core.run.coins == 0 and not core.perm.story_completed, "nothing can be used on the first evening")
	store.sofa.interact()
	check(not ui.is_modal_open(), "the first nap has no menu")
	await create_timer(4.2).timeout
	check(core.perm.intro_seen and main.player.controls_enabled, "the nap ends the opening")
	check(not store.machines["machine_001"]["anim"].visible and store.coins[0].visible, "the player wakes to a dark store, coins on the floor")
	check(main.player.global_position.distance_to(store.SPAWN) < 2.0, "the player wakes by the sofa")
	store.reception.interact()
	check(core.perm.note_read and not ui.is_modal_open(), "with no power the reception holds the manager's note")
	check(is_equal_approx(main.camera.zoom.x, 3.0), "the camera shows the world at three screen pixels per pixel")
	var view_height: float = 720.0 / main.camera.zoom.y
	check(main.camera.position.y - view_height / 2.0 <= store.VIEW_TOP + 0.5 and main.camera.position.y + view_height / 2.0 >= store.VIEW_BOTTOM - 0.5, "wall top and floor ledge both fit in the view")
	await frames(20)
	check(main.player.focused_interactable() == store.sofa, "the sofa is at hand on waking")
	await shot("01_bathroom_dark")

	# Walking right: the staff room's wall stops the player.
	Input.action_press("move_right")
	await create_timer(3.2).timeout
	Input.action_release("move_right")
	await frames(3)
	check(main.player.global_position.x < store.ZONES["staff"].y, "the staff room is a room of its own: its wall stops the player")
	check(store.zone == "staff", "the night starts in the staff room scene")
	check(absf(main.player.global_position.y - store.SPAWN.y) < 0.01, "walking sideways keeps the player's depth")
	check(main.player.z_index == store.floor_z(main.player.position.y), "the player is depth-sorted by the floor line")
	# Doors lead from one scene to another.
	_go(main, store.zone_doors[1]["node"].use_point())
	check(main.player.focused_interactable() == store.zone_doors[1]["node"], "the bathroom has a door")
	store.zone_doors[1]["node"].interact()
	await create_timer(0.7).timeout
	check(store.zone == "store" and main.player.controls_enabled, "the bathroom door leads into the store")
	check(main.player.global_position.distance_to(store.zone_doors[0]["node"].use_point()) < 2.0, "the player comes out at the door on the other side")
	store.zone_doors[2]["node"].interact()
	await create_timer(0.7).timeout
	check(store.zone == "staff", "a door in the reception leads to the staff room")
	check(main.player.walk_area.position.x >= store.ZONES["staff"].x, "the staff room's own walls bound the walk")
	store.zone_doors[4]["node"].interact()
	await create_timer(0.7).timeout
	check(store.zone == "cellar", "stairs in the staff room lead down to the cellar")
	check(store.zone_at(store.power_switch.global_position.x) == "cellar", "the fuse box is in the cellar")
	check(store.zone_at(store.gallery_spot(0).x) == "cellar", "the figures are kept in the cellar")
	store.zone_doors[5]["node"].interact()
	await create_timer(0.7).timeout
	check(store.zone == "staff", "and the stairs lead back up")
	store.zone_doors[3]["node"].interact()
	await create_timer(0.7).timeout
	check(store.zone == "store", "and its door leads back to the store")

	# Two axes: towards the camera, then away from it until the back wall.
	var area: Rect2 = store.WALK_AREA
	# In the corridor, where nothing stands between the player and the wall.
	_go(main, Vector2(store.room_range("corridor").x + 40.0, store.SPAWN.y))
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
	_go(main, Vector2(area.end.x - 4.0, area.end.y - 60.0))
	Input.action_press("move_right")
	Input.action_press("move_back")
	await create_timer(3.4).timeout
	Input.action_release("move_right")
	Input.action_release("move_back")
	check(main.player.global_position.x <= area.end.x and main.player.global_position.y <= area.end.y, "the end wall and the floor's edge stop the player")
	check(absf(main.player.global_position.y - area.end.y) < 0.01, "the player reaches the near edge of the floor")

	# Art is drawn finer than the world and shown at 1 / ART_SCALE; anchors are
	# measured on the pictures and converted to world pixels.
	for machine_id in store.machines:
		var built: Dictionary = store.machines[machine_id]
		var picture: Vector2 = Vector2(built["off"].texture.get_size())
		check((picture * built["off"].scale).is_equal_approx(picture / Sprites.ART_SCALE) and built["anim"].scale.is_equal_approx(built["off"].scale), "%s is shown at its texture size divided by the art scale" % machine_id)
	var grade: CanvasLayer = main.get_node_or_null("ScreenGrade")
	check(grade != null and grade.get_child_count() > 0, "the film grade layer exists")
	var grade_passes_mouse: bool = grade != null
	if grade != null:
		for child in grade.get_children():
			if child is Control and child.mouse_filter != Control.MOUSE_FILTER_IGNORE:
				grade_passes_mouse = false
	check(grade_passes_mouse, "the film grade never stops mouse input")

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

	# The stock rack: one closed box per figure, and no figure to be seen.
	check(store.gallery.size() == core.data.figure_order.size(), "the stock rack holds a box for every figure")
	check(_stickers(store) == 0, "no box is marked before its figure is found")
	check(store.find_children("*", "AnimatedSprite2D", true, false).all(func(node: Node) -> bool: return not node.animation.begins_with("figure_")), "no figure shows in the cellar")
	_go(main, store.stock.use_point())
	check(main.player.focused_interactable() == store.stock, "the stock rack can be used")
	store.stock.interact()
	check(ui.open_modal_name() == "catalog", "using the stock rack opens the record of figures")
	ui.close_modal()

	_go(main, Vector2(1500.0, 30.0))
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
	check(hud.has("purse") and hud["purse"].end.y < screen.size.y * 0.15 and hud["purse"].end.x < screen.size.x * 0.3, "the purse sits in the top left corner")
	check(hud.keys().all(func(part: String) -> bool: return part == "purse" or hud[part].position.y > screen.size.y * 0.6), "the rest of the HUD keeps to the front of the floor")
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
	_go(main, Vector2(390.0, 50.0))
	await shot("02_hall_lit")

	# First spin: sell through the real button.
	core.rand_fn = func() -> float: return 0.0
	store.machines["machine_001"]["body"].interact()
	check(ui.open_modal_name() == "machine" and ui.machine_scene.machine_id == "machine_001", "using a machine steps inside it")
	check(core.run.coins == 3 and not core.run.has_pending_prize(), "stepping inside costs nothing")
	check(not main.player.controls_enabled, "the hall waits while the player is inside a machine")
	await shot("21_machine_gacha")
	ui.machine_scene.press_action()
	check(core.run.coins == 2 and core.run.has_pending_prize(), "the play key pays once and the prize is decided")
	check(ui.machine_scene.is_playing(), "the crank is waiting for the player's hand")
	check(not ui.machine_scene.show_machine("machine_002"), "no jumping to another machine in the middle of a play")
	ui.machine_scene.press_action()
	check(core.run.coins == 2, "pressing again mid-play pays nothing")
	ui.machine_scene.finish_now()
	check(ui.open_modal_name() == "prize", "prize panel opens after the crank")
	var won_id: String = core.pending_prize_view()["figure_id"]
	check(store.gallery[won_id]["sticker"].visible, "the box of a found figure gets a sticker")
	check(ui.prize_panel.figure_view.animated == Sprites.has_figure_idle(won_id), "the prize panel plays the idle loop after the reveal")
	check(_stickers(store) == core.discovered_count(), "only found figures have a sticker")
	check(ui.prize_panel.figure_view.base != null, "the prize stands on its rarity base")
	check(not ui.prize_panel.keep_button.disabled, "Keep allowed with 2 coins left")
	await shot("03_prize_panel")
	if _shot_dir != "":
		# The capsule has burst and the figure plays its loop on the base.
		await create_timer(1.3).timeout
		await shot("03a_prize_revealed")
	ui.prize_panel.sell_button.pressed.emit()
	check(core.run.coins == 3, "Sell button credits the sale")
	check(ui.open_modal_name() == "machine", "selling returns to the machine, ready for another play")
	check(ui.machine_scene.show_machine("machine_005") and ui.machine_scene.machine_id == "machine_005", "the player can jump straight to another machine")
	check(main.player.global_position.distance_to(store.machines["machine_005"]["body"].use_point()) < 2.0, "jumping machines moves the player in the hall too")
	await shot("22_machine_crane")
	ui.machine_scene.show_machine("machine_006")
	await shot("23_machine_plinko")
	ui.close_modal()
	check(not ui.is_modal_open() and main.player.controls_enabled, "Esc steps back out into the hall")
	check(main.player.global_position.distance_to(store.machines["machine_006"]["body"].use_point()) < 2.0, "the player comes out in front of the last machine")
	ui.prize_panel.sell_button.pressed.emit()
	check(core.run.coins == 3, "a second click sells nothing")

	# Low funds: Keep is disabled, and closing the panel keeps the prize.
	core.run.coins = 2
	_spin(main, "machine_001")
	check(ui.prize_panel.keep_button.disabled, "Keep disabled with 1 coin left")
	ui.close_modal()
	check(core.run.has_pending_prize(), "closing the panel keeps the prize pending")
	check(ui.open_modal_name() == "machine", "closing the prize returns to the machine")
	ui.machine_scene.press_action()
	check(ui.open_modal_name() == "prize", "the play key reopens a waiting prize instead of paying again")
	ui.close_machine()
	check(not ui.is_modal_open() and core.run.has_pending_prize(), "leaving the machine keeps the prize pending")
	store.machines["machine_002"]["body"].interact()
	check(ui.open_modal_name() == "prize", "any machine reopens the pending prize")
	await shot("03b_prize_on_base")
	ui.prize_panel.keep_button.pressed.emit()
	check(core.run.has_pending_prize(), "disabled Keep resolves nothing")
	ui.prize_panel.sell_button.pressed.emit()
	check(not core.run.has_pending_prize(), "prize sold")
	ui.close_machine()

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
	_spin(main, "machine_002")
	ui.prize_panel.sell_button.pressed.emit()
	ui.close_machine()
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
	check(main.player.global_position.distance_to(store.SPAWN) < 2.0, "player wakes up by the sofa")
	check(not ui.is_modal_open() and main.player.controls_enabled, "control returns to the player")

	# Second run: the sales terminal, a robot, the crane, plinko, the key and the door.
	store.reception.interact()
	check(not ui.is_modal_open(), "the terminal needs power")
	store.power_switch.interact()
	store.door.interact()
	check(not ui.is_modal_open() and not core.perm.story_completed, "the door is locked without the key")
	core.run.coins = 1000
	_spin(main, "machine_001")
	ui.prize_panel.sell_button.pressed.emit()
	ui.close_machine()
	check(store.machines["machine_001"]["affordable"] and store.machines["machine_001"]["price"].affordable, "a machine the player can pay for lights its price sign")
	check(not store.machines["machine_006"]["affordable"] and not store.machines["machine_006"]["price"].affordable, "a machine that costs too much keeps its sign dull")
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
	var tour: Dictionary = {"11_bathroom": Vector2(70.0, 60.0), "12_corridor": Vector2(200.0, 60.0), "13_hall_right": Vector2(560.0, 50.0), "14_cellar": Vector2(1470.0, 34.0), "15_cellar_stairs": Vector2(1330.0, 30.0), "16_reception": Vector2(900.0, 90.0), "17_staff": Vector2(1055.0, 60.0)}
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
	_go(main, Vector2(390.0, 60.0))
	await create_timer(0.5).timeout
	await shot("20_celebration")
	await create_timer(1.6).timeout

	core.run.coins = core.machine_price("machine_005") * 3
	_go(main, store.machines["machine_005"]["body"].use_point())
	store.machines["machine_005"]["body"].interact()
	ui.machine_scene.press_action()
	ui.machine_scene.press_action()
	await create_timer(1.0).timeout
	await shot("08a_crane_moving")
	await create_timer(2.2).timeout
	check(ui.open_modal_name() == "prize", "the crane hands over a prize")
	await shot("08_crane_prize")
	ui.prize_panel.sell_button.pressed.emit()
	core.run.coins = core.machine_price("machine_006") * 3
	check(ui.machine_scene.show_machine("machine_006"), "from the crane straight to the plinko board")
	ui.machine_scene.press_action()
	ui.machine_scene.press_action()
	await create_timer(3.0).timeout
	check(ui.open_modal_name() == "prize", "plinko hands over a prize")
	ui.prize_panel.sell_button.pressed.emit()
	ui.close_machine()
	for machine_id in ["machine_002"]:
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


## Steps inside a machine and plays it through to the prize panel.
func _spin(main: Node, machine_id: String) -> void:
	main.store.machines[machine_id]["body"].interact()
	main.ui.machine_scene.press_action()
	main.ui.machine_scene.finish_now()


## Puts the player on a floor point and the camera over it.
func _go(main: Node, at: Vector2) -> void:
	main.player.place(at)
	main.sync_zone()
	main.camera.position.x = at.x
	main.camera.reset_smoothing()


## "" when every machine has its price with its amount on the floor in front
## of it, and never under the HUD with the camera on that machine.
func _price_signs_ok(main: Node) -> String:
	var store: Node2D = main.store
	for machine_id in store.machines:
		var price: Node2D = store.machines[machine_id]["price"]
		if not price.visible or price.text == "":
			return "%s has no price" % machine_id
		var board: Rect2 = price.board_rect()
		if board.position.y < 0.0 or board.end.y > store.FLOOR_DEPTH:
			return "%s: the price is off the floor" % machine_id
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


## How many boxes on the stock rack carry a sticker.
func _stickers(store: Node2D) -> int:
	var count: int = 0
	for figure_id in store.gallery:
		if store.gallery[figure_id]["sticker"].visible:
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
