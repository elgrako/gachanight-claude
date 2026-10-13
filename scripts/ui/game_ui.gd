extends CanvasLayer
## HUD and modal panels. Observes the core; the only state it owns is which
## panel is open.

const Style = preload("res://scripts/ui/ui_style.gd")
const Format = preload("res://scripts/core/format.gd")
const PrizePanel = preload("res://scripts/ui/prize_panel.gd")
const CatalogPanel = preload("res://scripts/ui/catalog_panel.gd")
const SofaPanel = preload("res://scripts/ui/sofa_panel.gd")
const ReceptionPanel = preload("res://scripts/ui/reception_panel.gd")
const EndingPanel = preload("res://scripts/ui/ending_panel.gd")
const MachineScene = preload("res://scripts/ui/machine_scene.gd")

const TOAST_SECONDS: float = 3.5

# --- HUD layout, in canvas pixels (the canvas is 720 tall) -------------------
## The whole HUD lives on the front strip of the floor and on the floor's
## ledge: the back wall, where the machines, their price signs, the gallery and
## everything that hangs are, stays free in every room.
## The ledge is the lowest 24 px of the view: the key hint is written on it.
const LEDGE_HEIGHT: float = 24.0
const HUD_MARGIN: float = 16.0
## Bottom edge of the corner plates, above the ledge.
const HUD_BOTTOM: float = LEDGE_HEIGHT + 8.0
## The prompt sits above the row of the corner plates, and the toast above it,
## so none of them can meet whatever the lengths of their texts.
const PROMPT_BOTTOM: float = HUD_BOTTOM + 56.0
const TOAST_BOTTOM: float = PROMPT_BOTTOM + 48.0
const PLATE_COLOR: Color = Color(0.086, 0.075, 0.125, 0.9)
## Height of the coin's face beside the purse, top left.
const COIN_ICON_SIZE: float = 44.0
const COIN_ICON_PATH: String = "res://assets/sprites/ui/coin_icon.png"

signal modal_changed(is_open: bool)
signal rebirth_requested(selection: Dictionary)
signal quit_requested
signal ending_finished
## The player jumped to another machine from inside the machine scene.
signal machine_changed(machine_id: String)

var prize_panel: PanelContainer
var catalog_panel: PanelContainer
var sofa_panel: PanelContainer
var reception_panel: PanelContainer
var pause_panel: PanelContainer
var ending_panel: Control
## The view from inside a machine. It is a place, not a panel: panels (prize,
## catalog) open on top of it and closing them returns to it.
var machine_scene: Control

var _core: RefCounted
var _coins: Label
var _prestige: Label
var _status: Label
var _objective: Label
var _prompt: Label
var _toast: Label
## The plates behind the HUD texts, and the key hint on the ledge.
var _corner_plate: PanelContainer
var _purse_plate: PanelContainer
var _objective_plate: PanelContainer
var _prompt_plate: PanelContainer
var _toast_plate: PanelContainer
var _keys: Label
var _toast_timer: float = 0.0
var _fade: ColorRect
var _modals: Dictionary = {}  # name -> backdrop Control
var _open_modal: String = ""
var _machine_open: bool = false
var _new_figure_ids: Dictionary = {}


func setup(core: RefCounted) -> void:
	_core = core
	_build_hud()
	machine_scene = MachineScene.new()
	machine_scene.visible = false
	add_child(machine_scene)
	machine_scene.prize_ready.connect(_on_machine_prize_ready)
	machine_scene.machine_changed.connect(func(machine_id: String) -> void: machine_changed.emit(machine_id))
	machine_scene.exit_requested.connect(close_machine)
	prize_panel = PrizePanel.new()
	_add_modal("prize", prize_panel)
	catalog_panel = CatalogPanel.new()
	_add_modal("catalog", catalog_panel)
	sofa_panel = SofaPanel.new()
	_add_modal("sofa", sofa_panel)
	reception_panel = ReceptionPanel.new()
	_add_modal("reception", reception_panel)
	pause_panel = _build_pause_panel()
	_add_modal("pause", pause_panel)
	ending_panel = EndingPanel.new()
	ending_panel.visible = false
	add_child(ending_panel)
	_modals["ending"] = ending_panel
	_fade = ColorRect.new()
	_fade.color = Color(0.0, 0.0, 0.0, 0.0)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_fade)
	prize_panel.resolved.connect(_on_prize_resolved)
	sofa_panel.cancelled.connect(close_modal)
	sofa_panel.rebirth_requested.connect(func(selection: Dictionary) -> void: rebirth_requested.emit(selection))
	reception_panel.closed.connect(close_modal)
	ending_panel.finished.connect(func() -> void:
		close_modal()
		ending_finished.emit())
	core.coins_changed.connect(func(_coins_now: int) -> void: _refresh_hud())
	core.prestige_available_changed.connect(func(_available: int) -> void: _refresh_hud())
	core.run_started.connect(_refresh_hud)
	core.reception_item_bought.connect(func(_item_id: String, _level: int) -> void: _refresh_hud())
	core.robot_state_changed.connect(func(_machine_id: String) -> void: _refresh_hud())
	core.figure_discovered.connect(func(figure_id: String) -> void: _new_figure_ids[figure_id] = true)
	core.prestige_unlocked.connect(func() -> void: toast("Prestige unlocked! The staff room sofa looks inviting..."))
	core.figure_collection_completed.connect(_on_collection_completed)
	core.store_key_bought.connect(func() -> void: toast("The last figure. It looks just like... Outside, the sky is getting light.", 7.0))
	_refresh_hud()


func _process(delta: float) -> void:
	if _toast_timer > 0.0:
		_toast_timer -= delta
		if _toast_timer <= 0.0:
			_toast_plate.visible = false
	var objective: String = _objective_text()
	if objective != _objective.text:
		_objective.text = objective
	if _open_modal == "reception" and Engine.get_process_frames() % 20 == 0:
		reception_panel.refresh()


# --- Public -----------------------------------------------------------------

func is_modal_open() -> bool:
	return _open_modal != "" or _machine_open


## The panel on top, or "machine" when only the machine scene is showing.
func open_modal_name() -> String:
	if _open_modal != "":
		return _open_modal
	return "machine" if _machine_open else ""


func is_machine_open() -> bool:
	return _machine_open


## Steps inside a machine.
func open_machine(machine_id: String) -> void:
	_machine_open = true
	machine_scene.open(_core, machine_id)
	machine_scene.active = _open_modal == ""
	_prompt_plate.visible = false
	modal_changed.emit(true)


## Back to the hall, whatever is open.
func close_machine() -> void:
	if not _machine_open:
		return
	if _open_modal != "":
		_modals[_open_modal].visible = false
		_open_modal = ""
	_machine_open = false
	machine_scene.close()
	modal_changed.emit(false)


func set_prompt(text: String) -> void:
	if text != _prompt.text:
		_prompt.text = text
	_prompt_plate.visible = text != "" and not is_modal_open()


func toast(text: String, seconds: float = TOAST_SECONDS) -> void:
	if _machine_open:
		# The HUD is behind the machine scene: say it there.
		machine_scene.flash(text)
		return
	_toast.text = text
	_toast_plate.visible = true
	_toast_timer = seconds


## Canvas rectangles of every HUD element that is showing, by name.
func hud_rects() -> Dictionary:
	var rects: Dictionary = {}
	var parts: Dictionary = {"purse": _purse_plate, "corner": _corner_plate, "objective": _objective_plate, "prompt": _prompt_plate, "toast": _toast_plate, "keys": _keys}
	for part_name in parts:
		if parts[part_name].visible:
			rects[part_name] = parts[part_name].get_global_rect()
	return rects


func open_prize() -> void:
	var view: Dictionary = _core.pending_prize_view()
	if view.is_empty():
		return
	if prize_panel.show_prize(_core, _new_figure_ids.has(view["figure_id"])):
		_new_figure_ids.erase(view["figure_id"])
		_show_modal("prize")


func toggle_catalog() -> void:
	if _open_modal == "catalog":
		close_modal()
	elif _open_modal == "" and not (_machine_open and machine_scene.is_playing()):
		catalog_panel.refresh(_core)
		_show_modal("catalog")


func open_sofa() -> void:
	_show_modal("sofa")
	sofa_panel.open(_core)


func open_reception() -> void:
	_show_modal("reception")
	reception_panel.open(_core)


func open_pause() -> void:
	_show_modal("pause")


func open_ending(stats: Dictionary) -> void:
	_show_modal("ending")
	ending_panel.play(stats)


## Closes whatever is on top: a panel first, then the machine scene. Esc cannot
## leave the ending; it has its own button.
func close_modal() -> void:
	if _open_modal == "":
		close_machine()
		return
	_modals[_open_modal].visible = false
	_open_modal = ""
	if _machine_open:
		machine_scene.active = true
		return
	modal_changed.emit(false)


## Fades the screen to black (1.0) or back (0.0).
func fade_to(alpha: float, seconds: float) -> Tween:
	var tween: Tween = create_tween()
	tween.tween_property(_fade, "color:a", alpha, seconds)
	return tween


# --- Internals --------------------------------------------------------------

func _build_hud() -> void:
	var hud: Control = Control.new()
	hud.set_anchors_preset(Control.PRESET_FULL_RECT)
	hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(hud)
	# Top left: the purse, the coin's own face beside the amount.
	_purse_plate = _plate(Style.MUSTARD)
	_purse_plate.position = Vector2(HUD_MARGIN, HUD_MARGIN)
	hud.add_child(_purse_plate)
	var purse: HBoxContainer = HBoxContainer.new()
	purse.add_theme_constant_override("separation", 8)
	purse.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_purse_plate.add_child(purse)
	purse.add_child(_coin_icon())
	_coins = Style.label("", 30, Style.MUSTARD)
	purse.add_child(_coins)
	# Bottom left: prestige and status, in small print, when there is any.
	_corner_plate = _plate(Style.MUSTARD)
	_dock(hud, _corner_plate, Control.SIZE_SHRINK_BEGIN, HUD_BOTTOM)
	var corner: VBoxContainer = VBoxContainer.new()
	corner.add_theme_constant_override("separation", 0)
	corner.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_corner_plate.add_child(corner)
	_status = Style.label("", 13, Style.CREAM)
	corner.add_child(_status)
	_prestige = Style.label("", 13, Style.MINT)
	corner.add_child(_prestige)
	# Bottom right: what to do next.
	_objective_plate = _plate(Style.CREAM)
	_dock(hud, _objective_plate, Control.SIZE_SHRINK_END, HUD_BOTTOM)
	var goal: HBoxContainer = HBoxContainer.new()
	goal.add_theme_constant_override("separation", 8)
	goal.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_objective_plate.add_child(goal)
	goal.add_child(Style.label("GOAL", 12, Style.MUSTARD))
	_objective = Style.label("", 15, Style.CREAM)
	goal.add_child(_objective)
	# Bottom centre, one above the other: the key hint on the ledge, the
	# prompt, and a toast written on a paper note.
	_prompt_plate = _plate(Style.MINT)
	_dock(hud, _prompt_plate, Control.SIZE_SHRINK_CENTER, PROMPT_BOTTOM)
	_prompt_plate.visible = false
	_prompt = Style.label("", 18, Style.CREAM)
	_prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt_plate.add_child(_prompt)
	_toast_plate = PanelContainer.new()
	_toast_plate.add_theme_stylebox_override("panel", Style.box(Style.CREAM, Style.INK, 2, 0, 8))
	_toast_plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_dock(hud, _toast_plate, Control.SIZE_SHRINK_CENTER, TOAST_BOTTOM)
	_toast_plate.visible = false
	_toast = Style.label("", 17, Style.INK)
	_toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_toast_plate.add_child(_toast)
	_keys = Style.label("WASD walk · Shift run · E use · Tab catalog · Esc menu", 13, Color(Style.CREAM, 0.85))
	_keys.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_keys.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	_keys.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_keys.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_keys.offset_bottom = -2.0
	hud.add_child(_keys)


## A dark plate with a thin coloured frame: HUD text is always read on it,
## never straight on the scene.
func _plate(frame: Color) -> PanelContainer:
	var plate: PanelContainer = PanelContainer.new()
	var style: StyleBoxFlat = Style.box(PLATE_COLOR, frame, 2, 0, 8)
	style.content_margin_top = 4.0
	style.content_margin_bottom = 4.0
	plate.add_theme_stylebox_override("panel", style)
	plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return plate


## Puts a plate `bottom` pixels above the bottom edge of the screen, at the
## left, centre or right (`side` is a SIZE_SHRINK_* flag). The container keeps
## it there and fits it to its text whenever that changes.
func _dock(hud: Control, plate: Control, side: int, bottom: float) -> void:
	var dock: MarginContainer = MarginContainer.new()
	dock.set_anchors_preset(Control.PRESET_FULL_RECT)
	dock.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dock.add_theme_constant_override("margin_left", int(HUD_MARGIN))
	dock.add_theme_constant_override("margin_right", int(HUD_MARGIN))
	dock.add_theme_constant_override("margin_bottom", int(bottom))
	hud.add_child(dock)
	plate.size_flags_horizontal = side
	plate.size_flags_vertical = Control.SIZE_SHRINK_END
	dock.add_child(plate)


## The game's coin: the face cut from the owner's gold picture
## (`tools/pixel/build_coin_icon.py`), or a flat gold disc if it is missing.
func _coin_icon() -> Control:
	if ResourceLoader.exists(COIN_ICON_PATH):
		var face: TextureRect = TextureRect.new()
		face.texture = load(COIN_ICON_PATH)
		face.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		face.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		face.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		face.custom_minimum_size = Vector2(COIN_ICON_SIZE * face.texture.get_width() / face.texture.get_height(), COIN_ICON_SIZE)
		face.mouse_filter = Control.MOUSE_FILTER_IGNORE
		return face
	var coin: Panel = Panel.new()
	var style: StyleBoxFlat = StyleBoxFlat.new()
	style.bg_color = Style.MUSTARD
	style.border_color = Color("#0e0d0c")
	style.set_border_width_all(3)
	style.set_corner_radius_all(int(COIN_ICON_SIZE / 2.0))
	style.anti_aliasing = false
	coin.add_theme_stylebox_override("panel", style)
	coin.custom_minimum_size = Vector2(COIN_ICON_SIZE, COIN_ICON_SIZE)
	coin.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	coin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return coin


func _build_pause_panel() -> PanelContainer:
	var panel: PanelContainer = PanelContainer.new()
	Style.style_panel(panel)
	panel.custom_minimum_size = Vector2(420, 0)
	var column: VBoxContainer = VBoxContainer.new()
	column.add_theme_constant_override("separation", 12)
	panel.add_child(column)
	var title: Label = Style.label("Paused", 26)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(title)
	column.add_child(_slider_row("Volume", "master_volume", 0.0, 1.0))
	column.add_child(_slider_row("Music", "music_volume", 0.0, 1.0))
	column.add_child(_toggle_row("Fullscreen", "fullscreen"))
	var resume: Button = Style.button("Resume", Style.MINT)
	resume.pressed.connect(close_modal)
	column.add_child(resume)
	var quit: Button = Style.button("Save & Quit", Style.CORAL)
	quit.pressed.connect(func() -> void: quit_requested.emit())
	column.add_child(quit)
	return panel


func _toggle_row(title: String, key: String) -> CheckButton:
	var toggle: CheckButton = CheckButton.new()
	toggle.text = title
	for state in ["font_color", "font_pressed_color", "font_hover_color", "font_hover_pressed_color", "font_focus_color"]:
		toggle.add_theme_color_override(state, Style.INK)
	toggle.button_pressed = bool(_core.setting(key))
	toggle.toggled.connect(func(pressed: bool) -> void: _core.set_setting(key, pressed))
	return toggle


func _slider_row(title: String, key: String, low: float, high: float) -> Control:
	var row: HBoxContainer = HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	var label: Label = Style.label(title, 16)
	label.custom_minimum_size.x = 170
	row.add_child(label)
	var slider: HSlider = HSlider.new()
	slider.min_value = low
	slider.max_value = high
	slider.step = 0.05
	slider.value = float(_core.setting(key))
	slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	slider.value_changed.connect(func(value: float) -> void: _core.set_setting(key, value))
	row.add_child(slider)
	return row


func _add_modal(modal_name: String, panel: Control) -> void:
	var backdrop: ColorRect = ColorRect.new()
	backdrop.color = Color(0.05, 0.07, 0.13, 0.55)
	backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
	backdrop.visible = false
	add_child(backdrop)
	var center: CenterContainer = CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	backdrop.add_child(center)
	center.add_child(panel)
	_modals[modal_name] = backdrop


func _show_modal(modal_name: String) -> void:
	if _open_modal != "":
		_modals[_open_modal].visible = false
	_open_modal = modal_name
	_modals[modal_name].visible = true
	machine_scene.active = false
	_prompt_plate.visible = false
	modal_changed.emit(true)


func _refresh_hud() -> void:
	_coins.text = Format.number(_core.run.coins)
	var pending: int = _core.run.pending_prestige
	_prestige.visible = pending > 0 or _core.perm.banked_prestige > 0
	_prestige.text = "Prestige: %d pending · %d banked" % [pending, _core.perm.banked_prestige]
	var notes: Array = []
	var robots: int = 0
	for machine_id in _core.data.machine_order:
		robots += _core.robot_view(machine_id)["count"]
	if robots > 0:
		notes.append("%d %s at work" % [robots, "robot" if robots == 1 else "robots"])
	if _core.run.key_owned_this_run:
		notes.append("The last figure is yours")
	_status.visible = not notes.is_empty()
	_corner_plate.visible = _status.visible or _prestige.visible
	_status.text = " · ".join(notes)


func _objective_text() -> String:
	var run: RefCounted = _core.run
	if not _core.perm.intro_seen:
		return "First night shift: look around, then rest on the staff room sofa"
	if not run.power_switch_on:
		if not _core.perm.note_read:
			return "The lights are out. Check the reception"
		return "No power: the fuse box is in the cellar"
	if run.floor_coins_collected.has(false) and run.coins == 0 and _core.discovered_count() == 0:
		return "Pick up the coins on the staff room floor"
	if _core.perm.story_completed:
		return "Free Play"
	if run.key_owned_this_run:
		return "It is morning: the front door is open"
	if _core.perm.total_rebirths > 0:
		return "Earn enough for the last figure at reception"
	if _core.discovered_count() == 0:
		return "Try Capsule Machine No. 1"
	if not _core.is_prestige_unlocked():
		return "Save 50 coins for Capsule Machine No. 2"
	return "Complete collections, then rest on the staff room sofa"


func _on_machine_prize_ready(capsule_color: String) -> void:
	prize_panel.reveal_capsule = capsule_color
	open_prize()


func _on_prize_resolved(result: Dictionary) -> void:
	close_modal()
	# Inside a machine the scene itself reports the sale.
	if result["choice"] == "sell" and not _machine_open:
		toast("+%s" % Format.coins(result["coins_gained"]))


func _on_collection_completed(figure_id: String, prestige: int) -> void:
	var figure: Dictionary = _core.figure_view(figure_id)
	toast("Collection completed! %s — %s, +%d prestige" % [figure["name_en"], figure["bonus_text_en"], prestige])
