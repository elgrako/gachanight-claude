extends Node2D
## Main scene: joins the store, the player and the UI to the game core.

const Store = preload("res://scripts/world/store.gd")
const Player = preload("res://scripts/world/player.gd")
const GameUi = preload("res://scripts/ui/game_ui.gd")
const Format = preload("res://scripts/core/format.gd")
const Sprites = preload("res://scripts/world/sprite_lib.gd")

## The camera shows 320 x 180 world pixels on the 1280 x 720 canvas.
const PIXEL_SCALE: float = 4.0
const CAMERA_Y: float = -58.0
const CAMERA_FOLLOW: float = 6.0
## Rebirth: asleep on the sofa for a moment, fade out, wake up in the bathroom.
const REBIRTH_SLEEP_TIME: float = 0.35
const REBIRTH_FADE_OUT: float = 0.8
const REBIRTH_FADE_IN: float = 0.9

var store: Node2D
var player: Node2D
var camera: Camera2D
var ui: CanvasLayer

var _core: RefCounted
var _busy: bool = false


func _ready() -> void:
	_core = Game.core
	store = Store.new()
	store.name = "Store"
	add_child(store)
	player = Player.new()
	player.name = "Player"
	player.z_index = 5
	player.position.y = Store.PLAYER_Y
	player.min_x = Store.WALK_MIN_X
	player.max_x = Store.WALK_MAX_X
	player.interactables = store.interactables
	add_child(player)
	camera = Camera2D.new()
	camera.zoom = Vector2(PIXEL_SCALE, PIXEL_SCALE)
	camera.limit_left = 0
	camera.limit_right = int(Store.STORE_WIDTH)
	add_child(camera)
	camera.make_current()
	ui = GameUi.new()
	ui.name = "UI"
	add_child(ui)
	ui.setup(_core)
	_wire_interactions()
	ui.modal_changed.connect(_on_modal_changed)
	ui.rebirth_requested.connect(_on_rebirth_requested)
	ui.quit_requested.connect(_quit)
	ui.ending_finished.connect(_on_ending_finished)
	store.plinko_bounced.connect(func() -> void: Audio.play("plinko", -4.0, 0.2))
	store.machine_lit.connect(func() -> void: Audio.play("click", -10.0, 0.25))
	_core.power_changed.connect(func(is_on: bool) -> void: store.set_power(is_on, is_on))
	_core.floor_coin_collected.connect(func(index: int) -> void: store.set_coin_collected(index, true, true))
	_core.modifiers_changed.connect(_refresh_machines)
	_core.robot_state_changed.connect(func(_machine_id: String) -> void: _refresh_machines())
	_core.figure_discovered.connect(func(_figure_id: String) -> void: _refresh_display())
	_sync_world_to_run()
	_refresh_display()
	_place_player()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	# A prize left unresolved when the game closed comes back as the same decision.
	if _core.run.has_pending_prize():
		ui.open_prize()


func _process(delta: float) -> void:
	var target: Vector2 = Vector2(player.position.x, CAMERA_Y)
	camera.position = camera.position.lerp(target, clampf(delta * CAMERA_FOLLOW, 0.0, 1.0))
	if ui.is_modal_open() or _busy:
		ui.set_prompt("")
		return
	var focused: Object = player.focused_interactable()
	ui.set_prompt(focused.get_prompt() if focused != null else "")


func _unhandled_input(event: InputEvent) -> void:
	if _busy:
		return
	if event.is_action_pressed("ui_cancel"):
		_on_cancel()
	elif event.is_action_pressed("catalog"):
		if ui.open_modal_name() == "" or ui.open_modal_name() == "catalog":
			Audio.play("click")
			ui.toggle_catalog()
	elif event.is_action_pressed("interact") and not ui.is_modal_open():
		var focused: Object = player.focused_interactable()
		if focused != null:
			focused.interact()


# --- Interactions -----------------------------------------------------------

func _wire_interactions() -> void:
	for coin in store.coins:
		var index: int = coin.get_meta("coin_index")
		coin.prompt_fn = func() -> String: return "[E] Pick up coin"
		coin.interact_fn = func() -> void: _core.collect_floor_coin(index)
	store.power_switch.prompt_fn = func() -> String:
		return "" if _core.run.power_switch_on else "[E] Flip the main power switch"
	store.power_switch.interact_fn = func() -> void:
		player.play_use(store.power_switch.global_position.x)
		_core.turn_power_on()
	for machine_id in store.machines:
		var body: Node2D = store.machines[machine_id]["body"]
		body.prompt_fn = _machine_prompt.bind(machine_id)
		body.interact_fn = _use_machine.bind(machine_id)
	store.sofa.prompt_fn = func() -> String: return "[E] Rest on the sofa"
	store.sofa.interact_fn = _use_sofa
	store.reception.prompt_fn = func() -> String:
		return "[E] Use the sales terminal" if _core.run.power_switch_on else "The screen is dark"
	store.reception.interact_fn = _use_reception
	store.door.prompt_fn = func() -> String:
		return "[E] Use key" if _core.run.key_owned_this_run else "[E] Front door"
	store.door.interact_fn = _use_door


func _machine_prompt(machine_id: String) -> String:
	if _core.run.has_pending_prize():
		return "[E] Check your prize"
	if not _core.run.power_switch_on:
		return "No power"
	var machine: Dictionary = _core.data.machines[machine_id]
	var verb: String = "spin"
	if machine["machine_type"] == "claw":
		verb = "grab"
	elif machine["machine_type"] == "plinko":
		verb = "drop"
	return "[E] Insert %s and %s — %s" % [Format.coins(_core.machine_price(machine_id)), verb, machine["display_name_en"]]


func _use_machine(machine_id: String) -> void:
	if _core.run.has_pending_prize():
		ui.open_prize()
		return
	var result: Dictionary = _core.play_machine(machine_id)
	if not result["ok"]:
		Audio.play("error")
		match result["reason"]:
			"power_off":
				ui.toast("No power. The whole store is dead.")
			"not_enough_coins":
				ui.toast("Not enough coins. This one costs %s." % Format.number(result["price"]))
		return
	# The prize is already paid and saved; the machine animation is only presentation.
	_busy = true
	player.controls_enabled = false
	var speed: float = maxf(_core.crank_speed_multiplier(), 0.1)
	player.play_use(store.machines[machine_id]["body"].global_position.x, speed)
	# The coin goes in, and the machine starts, when the hand arrives.
	var reach: float = player.use_reach_time()
	var is_gacha: bool = _core.data.machines[machine_id]["machine_type"] == "gacha"
	get_tree().create_timer(reach / speed).timeout.connect(_play_insert_sounds.bind(is_gacha))
	await store.play_prize_animation(machine_id, result["slot"], speed, reach).finished
	Audio.play("capsule")
	_busy = false
	player.controls_enabled = true
	if result["auto_sold"]:
		Audio.play("sell", -3.0)
		ui.toast("Duplicate sold: +%s" % Format.coins(result["coins_gained"]))
	else:
		# The panel opens the same capsule that just dropped into the tray.
		ui.prize_panel.reveal_capsule = store.last_capsule_color
		ui.open_prize()


func _play_insert_sounds(is_gacha: bool) -> void:
	Audio.play("coin", -4.0)
	if is_gacha:
		Audio.play("crank")


func _use_sofa() -> void:
	if not _core.is_prestige_unlocked():
		ui.toast("An old sofa. I'm not sleepy yet.")
		return
	if _core.run.has_pending_prize():
		ui.toast("I should deal with my prize first.")
		return
	Audio.play("click")
	ui.open_sofa()


func _use_reception() -> void:
	if not _core.run.power_switch_on:
		ui.toast("The computer has no power.")
		return
	Audio.play("click")
	ui.open_reception()


func _use_door() -> void:
	var result: Dictionary = _core.use_exit_door()
	if not result["ok"]:
		Audio.play("error")
		ui.toast("Locked. I need a key to get out of here.")
		return
	Audio.play("door")
	if not result["first_time"]:
		ui.toast("I could leave any time now. But there are still capsules to open.")
		return
	# Buying the key is not the ending: walking out through this door is.
	_busy = true
	player.controls_enabled = false
	player.play_use(store.door.global_position.x)
	# The door opens on daylight while the screen fades; it is shut again
	# behind the black screen, ready for Free Play.
	store.play_door_open()
	await ui.fade_to(1.0, 1.6).finished
	store.reset_door()
	_busy = false
	Audio.stop_music()
	Audio.play_music("ending")
	ui.open_ending({
		"playtime_seconds": _core.perm.story_playtime_seconds,
		"rebirths": _core.perm.total_rebirths,
		"discovered": _core.discovered_count(),
		"total": _core.data.figure_order.size(),
	})
	ui.fade_to(0.0, 0.8)


func _on_ending_finished() -> void:
	Audio.resume_store_music()
	ui.toast("Free Play unlocked. The store is yours.")


func _on_rebirth_requested(selection: Dictionary) -> void:
	if _busy:
		return
	if not _core.get_rebirth_quote(selection)["ok"]:
		return
	_busy = true
	# The menu closes on the player already asleep on the sofa; closing it
	# changes nothing, the rebirth itself is confirmed behind the black screen.
	ui.close_modal()
	player.controls_enabled = false
	player.sleep_at(store.sofa.global_position + Store.SOFA_SEAT)
	await get_tree().create_timer(REBIRTH_SLEEP_TIME).timeout
	await ui.fade_to(1.0, REBIRTH_FADE_OUT).finished
	var result: Dictionary = _core.confirm_rebirth(selection)
	if result["ok"]:
		_sync_world_to_run()
		_place_player()
	else:
		player.wake()
	await ui.fade_to(0.0, REBIRTH_FADE_IN).finished
	_busy = false
	player.controls_enabled = not ui.is_modal_open()
	if not result["ok"]:
		ui.toast("I can't sleep right now.")


# --- State sync -------------------------------------------------------------

func _place_player() -> void:
	player.place(Store.SPAWN_X)
	camera.position = Vector2(player.position.x, CAMERA_Y)
	camera.reset_smoothing()


func _sync_world_to_run() -> void:
	store.set_power(_core.run.power_switch_on, false)
	for index in range(store.coins.size()):
		store.set_coin_collected(index, _core.run.floor_coins_collected[index])
	_refresh_machines()


## Prices and robots shown at each machine.
func _refresh_machines() -> void:
	for machine_id in store.machines:
		store.set_price_text(machine_id, Format.coins(_core.machine_price(machine_id)).to_upper())
		var robot: Dictionary = _core.robot_view(machine_id)
		store.set_robots(machine_id, robot["count"], 0.0 if robot["paused"] else robot["spins_per_second"])


## The hall's display rail: discovery is permanent, so it survives rebirths.
func _refresh_display() -> void:
	var figures: Array = []
	for figure_id in _core.data.figure_order:
		figures.append({"id": figure_id, "discovered": bool(_core.figure_view(figure_id)["discovered"])})
	store.set_display(figures)


func _on_modal_changed(is_open: bool) -> void:
	player.controls_enabled = not is_open and not _busy


func _on_cancel() -> void:
	match ui.open_modal_name():
		"":
			ui.open_pause()
		"ending":
			pass
		_:
			# Closing never resolves anything: a prize stays pending, the sofa spends nothing.
			ui.close_modal()


func _quit() -> void:
	_core.save()
	get_tree().quit()
