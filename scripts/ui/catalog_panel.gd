extends PanelContainer
## Figure album. Available from the start; unknown figures show their own silhouette.

## Each cell starts the idle loop of its figure this much later than the one before.
const IDLE_STAGGER: float = 0.37

const Style = preload("res://scripts/ui/ui_style.gd")
const FigureIcon = preload("res://scripts/ui/figure_icon.gd")

var _title: Label
var _content: VBoxContainer
var _bonuses: Label


func _ready() -> void:
	Style.style_panel(self)
	custom_minimum_size = Vector2(880, 660)
	var column: VBoxContainer = VBoxContainer.new()
	column.add_theme_constant_override("separation", 10)
	add_child(column)
	_title = Style.label("Figure Catalog", 26)
	column.add_child(_title)
	var scroll: ScrollContainer = ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	column.add_child(scroll)
	_content = VBoxContainer.new()
	_content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_content.add_theme_constant_override("separation", 12)
	scroll.add_child(_content)
	_bonuses = Style.label("", 15, Style.MUTED)
	_bonuses.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(_bonuses)
	column.add_child(Style.label("[Tab] or [Esc] to close", 14, Style.MUTED))


func refresh(core: RefCounted) -> void:
	_title.text = "Figure Catalog — Discovered %d/%d" % [core.discovered_count(), core.data.figure_order.size()]
	for child in _content.get_children():
		_content.remove_child(child)
		child.queue_free()
	for machine_id in core.data.machine_order:
		var machine: Dictionary = core.data.machines[machine_id]
		var heading: String = machine["display_name_en"]
		if machine["series_name_en"] != "":
			heading += " — " + machine["series_name_en"]
		_content.add_child(Style.label(heading, 20, Style.TEAL))
		var grid: GridContainer = GridContainer.new()
		grid.columns = 5
		grid.add_theme_constant_override("h_separation", 12)
		grid.add_theme_constant_override("v_separation", 12)
		_content.add_child(grid)
		for entry in machine["prize_table"]:
			grid.add_child(_cell(core.figure_view(entry["figure_id"]), grid.get_child_count() + _content.get_child_count()))
	var active: Array = core.active_bonus_views()
	if active.is_empty():
		_bonuses.text = "Active bonuses: none yet. Complete a figure's collection to earn one for this run."
	else:
		var parts: Array = []
		for bonus in active:
			parts.append("%s (%s)" % [bonus["text_en"], bonus["source_en"]])
		_bonuses.text = "Active bonuses: " + ", ".join(parts)


func _cell(figure: Dictionary, order: int) -> Control:
	var cell: PanelContainer = PanelContainer.new()
	cell.custom_minimum_size = Vector2(156, 202)
	cell.add_theme_stylebox_override("panel", Style.box(Color("#fffaf0"), Style.INK, 2, 8, 8))
	var column: VBoxContainer = VBoxContainer.new()
	column.add_theme_constant_override("separation", 2)
	cell.add_child(column)
	var icon: Control = FigureIcon.new()
	# Room for the stack of figure and base (56 x 58 world pixels) at two
	# screen pixels each.
	icon.custom_minimum_size = Vector2(112, 116)
	icon.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	icon.time_offset = order * IDLE_STAGGER
	icon.show_figure(figure["id"], figure["look"], not figure["discovered"], figure["rarity_id"])
	column.add_child(icon)
	var name_label: Label = Style.label(figure["name_en"] if figure["discovered"] else "???", 15)
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(name_label)
	var rarity: Label = Style.label(figure["rarity_name_en"] if figure["discovered"] else " ", 13, Style.MUTED)
	if figure["discovered"]:
		rarity.add_theme_color_override("font_color", figure["rarity_color"].darkened(0.35))
	rarity.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(rarity)
	var progress_text: String = "%d/%d" % [figure["copies_held"], figure["copies_required"]]
	if figure["completed"]:
		progress_text = "Completed this run"
	elif not figure["discovered"]:
		# Copies required would hint at the rarity of a figure not seen yet.
		progress_text = " "
	var progress: Label = Style.label(progress_text, 13, Style.TEAL if figure["completed"] else Style.INK)
	progress.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(progress)
	return cell
