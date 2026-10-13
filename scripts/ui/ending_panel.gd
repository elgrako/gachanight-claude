extends Control
## Ending: a few lines of text over a dawn sky, the credits, then back to the
## store in Free Play. Plays once per completed story; can be skipped.

const Style = preload("res://scripts/ui/ui_style.gd")
const Format = preload("res://scripts/core/format.gd")
const CREDITS_PATH: String = "res://data/credits.json"

signal finished

var continue_button: Button

var _sky: ColorRect
var _text: Label
var _credits: VBoxContainer
var _stats: Label
var _sequence: Tween
var _sky_tween: Tween
var _ending_lines: Array = []
var _credit_rows: Array = []


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_load_text()
	_sky = ColorRect.new()
	_sky.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_sky.color = Color("#0e0d0c")
	add_child(_sky)
	var center: CenterContainer = CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	var column: VBoxContainer = VBoxContainer.new()
	column.add_theme_constant_override("separation", 18)
	column.custom_minimum_size.x = 820
	center.add_child(column)
	_text = Style.label("", 28, Style.CREAM)
	_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(_text)
	_credits = VBoxContainer.new()
	_credits.add_theme_constant_override("separation", 14)
	_credits.visible = false
	column.add_child(_credits)
	for row in _credit_rows:
		if str(row[0]) != "":
			var role: Label = Style.label(str(row[0]), 30 if str(row[1]) == "" else 16, Style.MUSTARD)
			role.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			_credits.add_child(role)
		if str(row[1]) != "":
			var who: Label = Style.label(str(row[1]), 22, Style.CREAM)
			who.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			_credits.add_child(who)
	_stats = Style.label("", 16, Style.MINT)
	_stats.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_credits.add_child(_stats)
	continue_button = Style.button("Continue in Free Play", Style.MINT)
	continue_button.custom_minimum_size = Vector2(280, 48)
	continue_button.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	continue_button.visible = false
	continue_button.pressed.connect(func() -> void: finished.emit())
	column.add_child(continue_button)
	var hint: Label = Style.label("[Space] skip", 14, Color(1, 1, 1, 0.45))
	hint.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
	hint.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	hint.grow_vertical = Control.GROW_DIRECTION_BEGIN
	hint.offset_right = -24
	hint.offset_bottom = -18
	add_child(hint)


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_accept") and not continue_button.visible:
		skip()
		get_viewport().set_input_as_handled()


## Starts the sequence. stats: {playtime_seconds, rebirths, discovered, total}.
func play(stats: Dictionary) -> void:
	_stats.text = "Time in the store: %s   ·   Nights slept: %d   ·   Figures found: %d/%d" % [
		Format.duration(stats.get("playtime_seconds", 0.0)), stats.get("rebirths", 0),
		stats.get("discovered", 0), stats.get("total", 0),
	]
	_credits.visible = false
	continue_button.visible = false
	_text.visible = true
	_text.text = ""
	_text.modulate.a = 0.0
	_sky.color = Color("#0e0d0c")
	# The sky brightens on its own tween so the text does not wait for it.
	_sky_tween = create_tween()
	_sky_tween.tween_property(_sky, "color", Color("#b98d5c"), 14.0)
	_sequence = create_tween()
	_sequence.tween_interval(0.6)
	for line in _ending_lines:
		_sequence.tween_callback(_text.set_text.bind(str(line)))
		_sequence.tween_property(_text, "modulate:a", 1.0, 0.9)
		_sequence.tween_interval(2.6)
		_sequence.tween_property(_text, "modulate:a", 0.0, 0.7)
	_sequence.tween_callback(_show_credits)


func skip() -> void:
	if _sequence != null and _sequence.is_valid():
		_sequence.kill()
	if _sky_tween != null and _sky_tween.is_valid():
		_sky_tween.kill()
	_sky.color = Color("#b98d5c")
	_show_credits()


func _show_credits() -> void:
	_text.visible = false
	_credits.visible = true
	continue_button.visible = true
	continue_button.grab_focus()


func _load_text() -> void:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(CREDITS_PATH)) if FileAccess.file_exists(CREDITS_PATH) else null
	if typeof(parsed) == TYPE_DICTIONARY:
		_ending_lines = parsed.get("ending_lines", [])
		_credit_rows = parsed.get("credits", [])
	if _ending_lines.is_empty():
		_ending_lines = ["The door opens."]
	if _credit_rows.is_empty():
		_credit_rows = [["GACHANIGHT", ""], ["", "Thank you for playing"]]
