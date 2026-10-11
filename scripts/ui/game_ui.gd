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

const TOAST_SECONDS: float = 3.5

signal modal_changed(is_open: bool)
signal rebirth_requested(selection: Dictionary)
signal quit_requested
signal ending_finished

var prize_panel: PanelContainer
var catalog_panel: PanelContainer
var sofa_panel: PanelContainer
var reception_panel: PanelContainer
var pause_panel: PanelContainer
var ending_panel: Control

var _core: RefCounted
var _coins: Label
var _prestige: Label
var _status: Label
var _objective: Label
var _prompt: Label
var _toast: Label
var _toast_timer: float = 0.0
var _fade: ColorRect
var _modals: Dictionary = {}  # name -> backdrop Control
var _open_modal: String = ""
var _new_figure_ids: Dictionary = {}


func setup(core: RefCounted) -> void:
	_core = core
	_build_hud()
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
	core.store_key_bought.connect(func() -> void: toast("You bought the Store Exit Key. The front door is waiting."))
	_refresh_hud()


func _process(delta: float) -> void:
	if _toast_timer > 0.0:
		_toast_timer -= delta
		if _toast_timer <= 0.0:
			_toast.visible = false
	_objective.text = _objective_text()
	if _open_modal == "reception" and Engine.get_process_frames() % 20 == 0:
		reception_panel.refresh()


# --- Public -----------------------------------------------------------------

func is_modal_open() -> bool:
	return _open_modal != ""


func open_modal_name() -> String:
	return _open_modal


func set_prompt(text: String) -> void:
	_prompt.text = text
	_prompt.visible = text != "" and not is_modal_open()


func toast(text: String) -> void:
	_toast.text = text
	_toast.visible = true
	_toast_timer = TOAST_SECONDS


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
	elif _open_modal == "":
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


## Closes whatever is open. Esc cannot leave the ending; it has its own button.
func close_modal() -> void:
	if _open_modal == "":
		return
	_modals[_open_modal].visible = false
	_open_modal = ""
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
	var corner: VBoxContainer = VBoxContainer.new()
	corner.position = Vector2(24, 20)
	corner.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(corner)
	_coins = _hud_label(30, Style.MUSTARD)
	corner.add_child(_coins)
	_prestige = _hud_label(18, Style.MINT)
	corner.add_child(_prestige)
	_status = _hud_label(16, Style.CREAM)
	corner.add_child(_status)
	_objective = _hud_label(18, Style.CREAM)
	_objective.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	_objective.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_objective.offset_right = -24
	_objective.offset_top = 24
	_objective.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	hud.add_child(_objective)
	_toast = _hud_label(22, Style.CREAM)
	_toast.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_toast.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_toast.offset_top = 90
	_toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_toast.visible = false
	hud.add_child(_toast)
	_prompt = _hud_label(22, Style.CREAM)
	_prompt.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	_prompt.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_prompt.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_prompt.offset_bottom = -34
	_prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt.visible = false
	hud.add_child(_prompt)
	var keys: Label = _hud_label(14, Style.CREAM)
	keys.text = "A/D walk · Shift run · E use · Tab catalog · Esc menu"
	keys.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	keys.grow_horizontal = Control.GROW_DIRECTION_BOTH
	keys.grow_vertical = Control.GROW_DIRECTION_BEGIN
	keys.offset_bottom = -18
	hud.add_child(keys)


func _hud_label(size: int, color: Color) -> Label:
	var label: Label = Style.label("", size, color)
	label.add_theme_color_override("font_outline_color", Style.INK)
	label.add_theme_constant_override("outline_size", 8)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label


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
	_prompt.visible = false
	modal_changed.emit(true)


func _refresh_hud() -> void:
	_coins.text = Format.coins(_core.run.coins)
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
		notes.append("Exit key in your pocket")
	_status.visible = not notes.is_empty()
	_status.text = " · ".join(notes)


func _objective_text() -> String:
	var run: RefCounted = _core.run
	if run.floor_coins_collected.has(false) and not run.power_switch_on and run.coins == 0:
		return "Pick up the coins on the floor"
	if not run.power_switch_on:
		return "Find the main power switch"
	if _core.perm.story_completed:
		return "Free Play"
	if run.key_owned_this_run:
		return "Use the key on the front door"
	if _core.perm.total_rebirths > 0:
		return "Earn enough for the Store Exit Key at reception"
	if _core.discovered_count() == 0:
		return "Try Capsule Machine No. 1"
	if not _core.is_prestige_unlocked():
		return "Save 50 coins for Capsule Machine No. 2"
	return "Complete collections, then rest on the staff room sofa"


func _on_prize_resolved(result: Dictionary) -> void:
	close_modal()
	if result["choice"] == "sell":
		toast("+%s" % Format.coins(result["coins_gained"]))


func _on_collection_completed(figure_id: String, prestige: int) -> void:
	var figure: Dictionary = _core.figure_view(figure_id)
	toast("Collection completed! %s — %s, +%d prestige" % [figure["name_en"], figure["bonus_text_en"], prestige])
