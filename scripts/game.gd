extends Node
## Autoload "Game": owns the single GameCore, input actions, the robot tick
## and periodic saving.

const GameCore = preload("res://scripts/core/game_core.gd")
const AUTOSAVE_INTERVAL_SECONDS: float = 20.0

var core: RefCounted
var _autosave_timer: float = 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_register_input()
	core = GameCore.new()
	if not core.setup():
		push_error("GachaNight could not load its data tables.")
		return
	core.settings_changed.connect(apply_window_settings)
	apply_window_settings()


func _process(delta: float) -> void:
	if core == null or core.run == null:
		return
	core.add_playtime(delta)
	# Robots work in real time, including while a menu is open.
	core.tick(delta)
	_autosave_timer += delta
	if _autosave_timer >= AUTOSAVE_INTERVAL_SECONDS:
		_autosave_timer = 0.0
		core.save()


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST and core != null and core.run != null:
		core.save()


func apply_window_settings() -> void:
	if DisplayServer.get_name() == "headless":
		return
	var wants_fullscreen: bool = bool(core.setting("fullscreen"))
	var is_fullscreen: bool = DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
	if wants_fullscreen != is_fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if wants_fullscreen else DisplayServer.WINDOW_MODE_WINDOWED)


func _register_input() -> void:
	_add_key_action("move_forward", [KEY_W, KEY_UP])
	_add_key_action("move_back", [KEY_S, KEY_DOWN])
	_add_key_action("move_left", [KEY_A, KEY_LEFT])
	_add_key_action("move_right", [KEY_D, KEY_RIGHT])
	_add_key_action("interact", [KEY_E])
	_add_key_action("catalog", [KEY_TAB])
	_add_key_action("sprint", [KEY_SHIFT])


func _add_key_action(action: String, keys: Array) -> void:
	if InputMap.has_action(action):
		return
	InputMap.add_action(action)
	for key in keys:
		var event: InputEventKey = InputEventKey.new()
		event.physical_keycode = key
		InputMap.action_add_event(action, event)
