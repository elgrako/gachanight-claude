extends Node2D
## Main scene: joins the store, the player and the UI to the game core.

const Store = preload("res://scripts/world/store.gd")
const Player = preload("res://scripts/world/player.gd")
const GameUi = preload("res://scripts/ui/game_ui.gd")
const Format = preload("res://scripts/core/format.gd")
const Sprites = preload("res://scripts/world/sprite_lib.gd")
const ScreenGrade = preload("res://scripts/ui/screen_grade.gd")

## The camera shows about 427 x 240 world pixels on the 1280 x 720 canvas, a
## flat side view like a stage: the whole height of the store, from the top
## of the wall to the floor's ledge, and it only ever travels sideways.
const PIXEL_SCALE: float = 3.0
const CAMERA_Y: float = (Store.VIEW_TOP + Store.VIEW_BOTTOM) / 2.0
## How fast the camera catches up with the player, per second, in the
## frame-rate independent form: each second it closes all but exp(-6) of the
## gap, whatever the frame rate (docs/art/animation-techniques.md).
const CAMERA_FOLLOW: float = 6.0
## Art pixels per world pixel at standard density: the camera only ever rests
## on this grid, so the whole set moves by whole art pixels (texel perfect).
const ART_PER_WORLD: float = 1.5
## Rebirth: asleep on the sofa for a moment, fade out, wake up there in the dark.
const REBIRTH_SLEEP_TIME: float = 0.35
const REBIRTH_FADE_OUT: float = 0.8
const REBIRTH_FADE_IN: float = 0.9
## Waiting on the crane or the plinko board, the player checks the time once
## the reaching hand is back: this long after pressing the button, at speed 1.
const WAIT_FIDGET_AFTER: float = 0.95
## Going through a door between scenes: fade out, then in.
const DOOR_FADE: float = 0.2
## The opening: the front door stays open this long behind the new employee.
const INTRO_DOOR_TIME: float = 1.2
const NOTE_SECONDS: float = 9.0
const NOTE_TEXT: String = "A note on the counter: \"The fuse blows every night. The box is in the cellar.
The door locks itself at dusk. I have the only key. Back in the morning. - The manager\""

var store: Node2D
var player: Node2D
var camera: Camera2D
var ui: CanvasLayer

var _core: RefCounted
## Where the camera would be without snapping; the camera itself sits on the
## nearest art pixel to it.
var _camera_free: Vector2 = Vector2.ZERO
var _busy: bool = false
## A figure was discovered and the player has not celebrated it yet.
var _cheer_pending: bool = false
## A collection was completed or the exit key bought: a party is due as soon
## as no panel hides the store.
var _party_pending: bool = false
## A robot was bought at the terminal: a happy wave once the terminal closes.
var _wave_pending: bool = false
## The opening is playing: the first evening, lights on, nothing to do but
## look around until the sofa.
var _intro: bool = false


func _ready() -> void:
	_core = Game.core
	store = Store.new()
	store.name = "Store"
	add_child(store)
	player = Player.new()
	player.name = "Player"
	player.walk_area = Store.WALK_AREA
	player.solids = store.solids
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
	var grade: CanvasLayer = ScreenGrade.new()
	grade.name = "ScreenGrade"
	add_child(grade)
	_wire_interactions()
	ui.modal_changed.connect(_on_modal_changed)
	ui.rebirth_requested.connect(_on_rebirth_requested)
	ui.quit_requested.connect(_quit)
	ui.ending_finished.connect(_on_ending_finished)
	ui.machine_changed.connect(_stand_at_machine)
	_core.coins_changed.connect(func(_coins: int) -> void: _refresh_affordable())
	_core.figure_collection_completed.connect(func(_figure_id: String, _prestige: int) -> void: _queue_party())
	_core.store_key_bought.connect(func() -> void:
		# The last figure: morning comes and the front door opens by itself.
		store.play_door_open()
		Audio.play("door")
		_queue_party())
	_core.reception_item_bought.connect(_on_reception_item_bought)
	_core.power_changed.connect(func(is_on: bool) -> void: store.set_power(is_on, is_on))
	_core.floor_coin_collected.connect(func(index: int) -> void: store.set_coin_collected(index, true, true))
	_core.modifiers_changed.connect(_refresh_machines)
	_core.robot_state_changed.connect(func(_machine_id: String) -> void: _refresh_machines())
	_core.figure_discovered.connect(_on_figure_discovered)
	_intro = not _core.perm.intro_seen
	_sync_world_to_run()
	_refresh_display()
	_place_player()
	_cheer_pending = false
	if _intro:
		_start_intro()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	# A prize left unresolved when the game closed comes back as the same decision.
	if _core.run.has_pending_prize():
		ui.open_prize()


func _process(delta: float) -> void:
	var target: Vector2 = Vector2(player.position.x, CAMERA_Y)
	if camera.position.distance_to(_camera_free) > 2.0:
		_camera_free = camera.position                       # something placed the camera: start from there
	_camera_free = target.lerp(_camera_free, exp(-CAMERA_FOLLOW * delta))
	camera.position = (_camera_free * ART_PER_WORLD).round() / ART_PER_WORLD
	if ui.is_modal_open() or _busy:
		ui.set_prompt("")
		return
	var focused: Object = player.focused_interactable()
	ui.set_prompt(focused.get_prompt() if focused != null else "")
	# The computer is delighted to see a customer at the counter.
	store.set_computer_happy(focused == store.reception)


func _unhandled_input(event: InputEvent) -> void:
	if _busy:
		return
	if event.is_action_pressed("ui_cancel"):
		_on_cancel()
	elif event.is_action_pressed("catalog"):
		if ui.open_modal_name() in ["", "catalog", "machine"]:
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
		coin.prompt_fn = func() -> String: return "" if _intro else "[E] Pick up coin"
		coin.interact_fn = func() -> void:
			if not _intro:
				_core.collect_floor_coin(index)
	store.power_switch.prompt_fn = func() -> String:
		return "" if _intro or _core.run.power_switch_on else "[E] Put the fuse in"
	store.power_switch.interact_fn = func() -> void:
		if _intro:
			return
		player.play_use(store.power_switch.global_position.x)
		_core.turn_power_on()
	for machine_id in store.machines:
		var body: Node2D = store.machines[machine_id]["body"]
		body.prompt_fn = _machine_prompt.bind(machine_id)
		body.interact_fn = _use_machine.bind(machine_id)
	store.stock.prompt_fn = func() -> String: return "" if _intro else "[E] Check the stock"
	store.stock.interact_fn = func() -> void:
		if _intro or ui.is_modal_open():
			return
		Audio.play("click")
		ui.toggle_catalog()
	store.sofa.prompt_fn = func() -> String: return "[E] Sit down for a minute" if _intro else "[E] Rest on the sofa"
	store.sofa.interact_fn = _use_sofa
	store.reception.prompt_fn = func() -> String:
		if _intro:
			return "[E] Look at the computer"
		return "[E] Use the sales terminal" if _core.run.power_switch_on else "[E] Read the note"
	store.reception.interact_fn = _use_reception
	store.door.prompt_fn = func() -> String:
		return "[E] Step outside" if _core.run.key_owned_this_run else "[E] Front door"
	store.door.interact_fn = _use_door
	for zone_door in store.zone_doors:
		var target: String = zone_door["zone"]
		zone_door["node"].prompt_fn = _zone_door_prompt.bind(target)
		zone_door["node"].interact_fn = _use_zone_door.bind(zone_door)


func _machine_prompt(machine_id: String) -> String:
	if _intro:
		return "[E] Look"
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
	return "[E] Play %s — %s to %s" % [machine["display_name_en"], Format.coins(_core.machine_price(machine_id)), verb]


## The hall is the lobby: using a machine steps inside it, where it is played
## by hand (`machine_scene.gd`). Paying and the prize happen in there.
func _use_machine(machine_id: String) -> void:
	if _intro:
		ui.toast("Was it looking at me? ...No. Machines don't look.")
		return
	if _core.run.has_pending_prize():
		ui.open_prize()
		return
	if not _core.run.power_switch_on:
		Audio.play("error")
		ui.toast("No power. The whole store is dead.")
		return
	Audio.play("click")
	player.play_use(store.machines[machine_id]["body"].global_position.x)
	ui.open_machine(machine_id)


## Jumping between machines from inside moves the player in the hall too, so
## stepping out leaves them in front of the machine they were playing.
func _stand_at_machine(machine_id: String) -> void:
	player.place(store.machines[machine_id]["body"].use_point())
	sync_zone()
	camera.position = Vector2(player.position.x, CAMERA_Y)
	camera.reset_smoothing()


func _zone_door_prompt(target: String) -> String:
	match target:
		"bath":
			return "[E] Bathroom"
		"staff":
			return "[E] Staff room"
		"cellar":
			return "[E] Down to the cellar"
	return "[E] Back to the store"


## The bathroom and the staff room are scenes of their own, behind a door.
func _use_zone_door(zone_door: Dictionary) -> void:
	if _busy:
		return
	_busy = true
	player.controls_enabled = false
	Audio.play("door", -6.0)
	await ui.fade_to(1.0, DOOR_FADE).finished
	player.place(zone_door["to"])
	sync_zone()
	await ui.fade_to(0.0, DOOR_FADE).finished
	_busy = false
	player.controls_enabled = not ui.is_modal_open()


## Shows the scene the player stands in: its walls bound the walk and the view.
func sync_zone() -> void:
	var zone_name: String = Store.zone_at(player.position.x)
	store.set_zone(zone_name)
	player.walk_area = Store.zone_walk_area(zone_name)
	var span: Vector2 = Store.ZONES[zone_name]
	var half_view: float = get_viewport_rect().size.x / PIXEL_SCALE / 2.0
	if span.y - span.x < half_view * 2.0:
		# A room narrower than the screen sits still in the middle of it.
		var centre: float = (span.x + span.y) / 2.0
		span = Vector2(centre - half_view, centre + half_view)
	camera.limit_left = int(span.x)
	camera.limit_right = int(span.y)
	camera.position = Vector2(player.position.x, CAMERA_Y)
	camera.reset_smoothing()


func _use_sofa() -> void:
	if _intro:
		_doze_off()
		return
	if not _core.is_prestige_unlocked():
		ui.toast("An old sofa. I'm not sleepy yet.")
		return
	if _core.run.has_pending_prize():
		ui.toast("I should deal with my prize first.")
		return
	Audio.play("click")
	ui.open_sofa()


func _use_reception() -> void:
	if _intro:
		ui.toast("An old computer. The screen says: WELCOME, VALUED CUSTOMER!")
		return
	if not _core.run.power_switch_on:
		# No power, no salesman: only the manager's note on the counter.
		ui.toast(NOTE_TEXT, NOTE_SECONDS)
		_core.read_note()
		player.play_emote("player_shrug")
		return
	Audio.play("click")
	# A wave to the salesman on the screen.
	player.play_emote("player_wave")
	ui.open_reception()


func _use_door() -> void:
	if _intro:
		ui.toast("I only just got here.")
		return
	var result: Dictionary = _core.use_exit_door()
	if not result["ok"]:
		Audio.play("error")
		ui.toast("Locked. It shut itself at dusk, and the manager has the only key.")
		player.play_emote("player_shrug")
		return
	Audio.play("door")
	if not result["first_time"]:
		ui.toast("I could leave any time now. But there are still capsules to open.")
		return
	# Getting the last figure is not the ending: walking out into the morning is.
	_busy = true
	player.controls_enabled = false
	player.play_use(store.door.global_position.x)
	# The door stands open on daylight since the last figure was bought.
	await ui.fade_to(1.0, 1.6).finished
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
	if result["ok"]:
		# The night again: a yawn and a stretch by the sofa.
		player.play_emote("player_stretch")
	player.controls_enabled = not ui.is_modal_open()
	if not result["ok"]:
		ui.toast("I can't sleep right now.")


# --- The opening ---------------------------------------------------------------

## The first evening: the new employee walks in through the front door, which
## shuts behind them. The lights are on, the coins are not on the floor yet,
## and there is nothing to do but look around and end up on the sofa.
func _start_intro() -> void:
	store.set_power(true, false)
	for index in range(store.coins.size()):
		store.set_coin_collected(index, true)
	player.place(store.door.use_point(), true)
	sync_zone()
	store.play_door_open()
	ui.toast("First night shift. ...Hello? Anybody here?")
	await get_tree().create_timer(INTRO_DOOR_TIME).timeout
	store.reset_door()
	Audio.play("door", -6.0)


## Only a nap, with no menu: the lights are out when the player wakes, and
## the game proper starts.
func _doze_off() -> void:
	if _busy:
		return
	_busy = true
	player.controls_enabled = false
	player.sleep_at(store.sofa.global_position + Store.SOFA_SEAT)
	await get_tree().create_timer(1.2).timeout
	await ui.fade_to(1.0, REBIRTH_FADE_OUT).finished
	_intro = false
	_core.finish_intro()
	_sync_world_to_run()
	_place_player()
	await get_tree().create_timer(0.6).timeout
	await ui.fade_to(0.0, REBIRTH_FADE_IN).finished
	_busy = false
	player.controls_enabled = not ui.is_modal_open()
	player.play_emote("player_stretch")
	ui.toast("...I fell asleep? It's dark. The lights are out.")


# --- State sync -------------------------------------------------------------

func _place_player() -> void:
	player.place(Store.SPAWN)
	sync_zone()
	camera.position = Vector2(player.position.x, CAMERA_Y)
	camera.reset_smoothing()


func _sync_world_to_run() -> void:
	store.set_power(_core.run.power_switch_on, false)
	for index in range(store.coins.size()):
		store.set_coin_collected(index, _core.run.floor_coins_collected[index])
	# The manager has the only key: none lies on the counter any more.
	store.set_key_on_counter(false)
	if _core.run.key_owned_this_run:
		store.play_door_open()
	else:
		store.reset_door()
	_refresh_machines()


## Prices and robots shown at each machine.
func _refresh_machines() -> void:
	for machine_id in store.machines:
		store.set_price_text(machine_id, Format.number(_core.machine_price(machine_id)))
		var robot: Dictionary = _core.robot_view(machine_id)
		store.set_robots(machine_id, robot["count"], 0.0 if robot["paused"] else robot["spins_per_second"])
	_refresh_affordable()


## Which machines the player could pay for right now: their price signs light
## up and they call for attention.
func _refresh_affordable() -> void:
	for machine_id in store.machines:
		store.set_affordable(machine_id, _core.run.coins >= _core.machine_price(machine_id))


func _on_reception_item_bought(item_id: String, _level: int) -> void:
	if item_id.begins_with("robot_"):
		_wave_pending = true


## A party in the store, now or as soon as the open panel closes.
func _queue_party() -> void:
	_party_pending = true
	if not ui.is_modal_open() and not _busy:
		_throw_party()


func _throw_party() -> void:
	_party_pending = false
	_cheer_pending = false
	_wave_pending = false
	Audio.play("sell", -6.0, 0.3)
	player.play_cheer()


## The stock rack: discovery is permanent, so it survives rebirths. A found
## figure's box gets a sticker; the figures themselves show in the catalog.
func _refresh_display() -> void:
	var figures: Array = []
	for figure_id in _core.data.figure_order:
		var view: Dictionary = _core.figure_view(figure_id)
		figures.append({"id": figure_id, "discovered": bool(view["discovered"]), "rarity_id": view["rarity_id"]})
	store.set_display(figures)


func _on_figure_discovered(_figure_id: String) -> void:
	_refresh_display()
	_cheer_pending = true


func _on_modal_changed(is_open: bool) -> void:
	player.controls_enabled = not is_open and not _busy
	if is_open or _busy:
		return
	if _party_pending:
		_throw_party()
	elif _wave_pending:
		_wave_pending = false
		player.play_emote("player_wave")
	elif _cheer_pending and not _core.run.has_pending_prize():
		# The new figure is dealt with: a jump for joy back in the store.
		_cheer_pending = false
		player.play_cheer()


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
