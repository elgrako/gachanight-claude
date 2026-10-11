extends PanelContainer
## Sofa menu: provisional selection of permanent upgrades. Nothing is spent or
## applied until Sleep & Rebirth is confirmed; Cancel leaves everything as it was.

const Style = preload("res://scripts/ui/ui_style.gd")

signal cancelled
signal rebirth_requested(selection: Dictionary)

var confirm_button: Button
var cancel_button: Button
## upgrade_id -> {minus, plus}
var row_buttons: Dictionary = {}

var _core: RefCounted
var _selection: Dictionary = {}
var _points: Label
var _rows: VBoxContainer
var _summary: Label
var _row_labels: Dictionary = {}


func _ready() -> void:
	Style.style_panel(self)
	custom_minimum_size = Vector2(760, 0)
	var column: VBoxContainer = VBoxContainer.new()
	column.add_theme_constant_override("separation", 10)
	add_child(column)
	column.add_child(Style.label("The staff room sofa", 26))
	var hint: Label = Style.label("Sleeping ends this run: coins, kept figures and collection bonuses are lost. Upgrades bought here are permanent.", 15, Style.MUTED)
	hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(hint)
	_points = Style.label("", 18)
	column.add_child(_points)
	var scroll: ScrollContainer = ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(0, 360)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	column.add_child(scroll)
	_rows = VBoxContainer.new()
	_rows.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_rows.add_theme_constant_override("separation", 8)
	scroll.add_child(_rows)
	_summary = Style.label("", 18)
	column.add_child(_summary)
	var buttons: HBoxContainer = HBoxContainer.new()
	buttons.alignment = BoxContainer.ALIGNMENT_END
	buttons.add_theme_constant_override("separation", 16)
	column.add_child(buttons)
	cancel_button = Style.button("Cancel", Color("#e6dcc4"))
	cancel_button.pressed.connect(func() -> void: cancelled.emit())
	buttons.add_child(cancel_button)
	confirm_button = Style.button("Sleep & Rebirth", Style.CORAL)
	confirm_button.custom_minimum_size.x = 200
	confirm_button.pressed.connect(func() -> void: rebirth_requested.emit(_selection.duplicate()))
	buttons.add_child(confirm_button)


func open(core: RefCounted) -> void:
	_core = core
	_selection = {}
	_build_rows()
	_refresh()
	cancel_button.grab_focus()


func _build_rows() -> void:
	for child in _rows.get_children():
		_rows.remove_child(child)
		child.queue_free()
	row_buttons.clear()
	_row_labels.clear()
	for upgrade_id in _core.data.upgrade_order:
		var upgrade: Dictionary = _core.data.prestige_upgrades[upgrade_id]
		var row: HBoxContainer = HBoxContainer.new()
		row.add_theme_constant_override("separation", 10)
		_rows.add_child(row)
		var text: VBoxContainer = VBoxContainer.new()
		text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(text)
		text.add_child(Style.label(upgrade["display_name_en"], 18))
		var detail: Label = Style.label("", 14, Style.MUTED)
		detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		text.add_child(detail)
		var level: Label = Style.label("", 16)
		level.custom_minimum_size.x = 150
		level.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		row.add_child(level)
		var minus: Button = Style.button("-", Color("#e6dcc4"))
		minus.custom_minimum_size = Vector2(44, 44)
		minus.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		minus.pressed.connect(_change.bind(upgrade_id, -1))
		row.add_child(minus)
		var plus: Button = Style.button("+", Style.MINT)
		plus.custom_minimum_size = Vector2(44, 44)
		plus.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		plus.pressed.connect(_change.bind(upgrade_id, 1))
		row.add_child(plus)
		row_buttons[upgrade_id] = {"minus": minus, "plus": plus}
		_row_labels[upgrade_id] = {"detail": detail, "level": level}


func _change(upgrade_id: String, delta: int) -> void:
	var candidate: Dictionary = _selection.duplicate()
	candidate[upgrade_id] = int(candidate.get(upgrade_id, 0)) + delta
	if candidate[upgrade_id] <= 0:
		candidate.erase(upgrade_id)
	# The core is the authority: only keep selections it accepts.
	if _core.get_rebirth_quote(candidate)["ok"]:
		_selection = candidate
	_refresh()


func _refresh() -> void:
	var quote: Dictionary = _core.get_rebirth_quote(_selection)
	_points.text = "Banked prestige: %d    Pending this run: %d    Available: %d" % [
		_core.perm.banked_prestige, _core.run.pending_prestige, quote["available"],
	]
	for upgrade_id in _core.data.upgrade_order:
		var upgrade: Dictionary = _core.data.prestige_upgrades[upgrade_id]
		var owned: int = _core.perm.upgrade_level(upgrade_id)
		var adding: int = int(_selection.get(upgrade_id, 0))
		var labels: Dictionary = _row_labels[upgrade_id]
		var level_text: String = "Lv %d/%d" % [owned, upgrade["max_level"]]
		if adding > 0:
			level_text += "  (+%d)" % adding
		labels["level"].text = level_text
		var next_level: int = owned + adding
		var detail: String = upgrade["description_en"]
		if next_level < int(upgrade["max_level"]):
			detail += "  Next level: %d prestige." % int(upgrade["prestige_cost_curve"][next_level])
		else:
			detail += "  Maxed."
		for required_id in upgrade["prerequisites"]:
			detail += "  Requires %s Lv %d." % [
				_core.data.prestige_upgrades[required_id]["display_name_en"], upgrade["prerequisites"][required_id],
			]
		labels["detail"].text = detail
		var more: Dictionary = _selection.duplicate()
		more[upgrade_id] = adding + 1
		row_buttons[upgrade_id]["plus"].disabled = not _core.get_rebirth_quote(more)["ok"]
		row_buttons[upgrade_id]["minus"].disabled = adding <= 0
	_summary.text = "Cost: %d    Left after sleeping: %d" % [quote["cost"], quote["remaining"]]
	confirm_button.disabled = not quote["ok"] or _core.run.has_pending_prize()
