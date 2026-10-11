extends SceneTree
## Boots the real main scene and drives one full loop through the same
## interaction and UI paths the player uses. Run with:
##   godot --headless --path . -s tests/smoke_boot.gd
## Without --headless, set GACHANIGHT_SHOT_DIR to also save screenshots there.

const SAVE_PATH: String = "user://test_smoke.json"

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
	check(absf(main.player.global_position.x - store.SPAWN_X) < 2.0, "player starts in the bathroom")
	await frames(20)
	check(main.player.focused_interactable() == null, "nothing to use at the spawn point")
	await shot("01_bathroom_dark")

	# Walking right leads out of the bathroom into the corridor; the store ends in a wall.
	Input.action_press("move_right")
	await create_timer(3.2).timeout
	Input.action_release("move_right")
	await frames(3)
	check(main.player.global_position.x > 150.0, "player can walk from the bathroom into the corridor")
	check(absf(main.player.global_position.y - store.PLAYER_Y) < 0.01, "walking keeps the player on the floor line")
	_go(main, store.WALK_MAX_X - 4.0)
	Input.action_press("move_right")
	await create_timer(0.6).timeout
	Input.action_release("move_right")
	check(main.player.global_position.x <= store.WALK_MAX_X, "the end wall stops the player")
	for item in store.interactables:
		_go(main, item.global_position.x)
		check(main.player.focused_interactable() == item, "%s can be reached" % item.name)
	_go(main, store.SPAWN_X)
	await frames(2)

	# Bathroom: coins, then the switch.
	check(not ui.is_modal_open(), "no panel at start")
	for coin in store.coins:
		coin.interact()
	check(core.run.coins == 3, "three floor coins picked up")
	check(not store.coins[0].visible, "collected coin disappears")
	store.machines["machine_001"]["body"].interact()
	check(not core.run.has_pending_prize(), "machine does nothing without power")
	store.power_switch.interact()
	check(core.run.power_switch_on, "switch turns the power on")
	await create_timer(2.4).timeout
	check(store.machines["machine_001"]["lit"].visible, "machines light up with the power")
	_go(main, 390.0)
	await shot("02_hall_lit")

	# First spin: sell through the real button.
	core.rand_fn = func() -> float: return 0.0
	store.machines["machine_001"]["body"].interact()
	check(core.run.coins == 2, "spin paid once")
	await create_timer(1.5).timeout
	check(ui.open_modal_name() == "prize", "prize panel opens after the crank")
	check(not ui.prize_panel.keep_button.disabled, "Keep allowed with 2 coins left")
	await shot("03_prize_panel")
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
	ui.prize_panel.keep_button.pressed.emit()
	check(core.run.has_pending_prize(), "disabled Keep resolves nothing")
	ui.prize_panel.sell_button.pressed.emit()
	check(not core.run.has_pending_prize(), "prize sold")

	# Catalog and locked sofa.
	ui.toggle_catalog()
	check(ui.open_modal_name() == "catalog", "catalog opens")
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
	check(absf(main.player.global_position.x - store.SPAWN_X) < 2.0, "player wakes up in the bathroom")
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
	_go(main, 330.0)
	await shot("07_machine_row")

	core.run.coins = core.machine_price("machine_005") * 3
	_go(main, 600.0)
	store.machines["machine_005"]["body"].interact()
	await create_timer(3.0).timeout
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


## Puts the player and the camera at a world x.
func _go(main: Node, x: float) -> void:
	main.player.place(x)
	main.camera.position.x = x
	main.camera.reset_smoothing()


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
