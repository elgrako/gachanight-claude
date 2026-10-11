extends PanelContainer
## Prize decision: Sell (coins now) or Keep (one copy towards the collection).

const Style = preload("res://scripts/ui/ui_style.gd")
const FigureView = preload("res://scripts/ui/figure_view.gd")
const Format = preload("res://scripts/core/format.gd")

const TEXT_COMPLETED: String = "Collection completed — sell this duplicate."
const TEXT_LOW_FUNDS: String = "If I run out of money, I'll be stuck here forever."

signal resolved(result: Dictionary)

var sell_button: Button
var keep_button: Button

## Capsule colour to open before the figure appears, set right after a machine
## dropped that capsule. Used once: reopening a pending prize shows it directly.
var reveal_capsule: String = ""

var _core: RefCounted
var _transaction_id: int = -1
var _view: Control
var _new_tag: Label
var _name: Label
var _rarity: Label
var _bonus: Label
var _warning: Label


func _ready() -> void:
	Style.style_panel(self)
	custom_minimum_size = Vector2(440, 0)
	var column: VBoxContainer = VBoxContainer.new()
	column.add_theme_constant_override("separation", 8)
	column.alignment = BoxContainer.ALIGNMENT_CENTER
	add_child(column)
	var title: Label = Style.label("Prize obtained!", 26)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(title)
	_new_tag = Style.label("NEW FIGURE!", 16, Style.CORAL)
	_new_tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(_new_tag)
	_view = FigureView.new()
	_view.custom_minimum_size = Vector2(240, 208)
	_view.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	column.add_child(_view)
	_name = Style.label("", 24)
	_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(_name)
	_rarity = Style.label("", 18)
	_rarity.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(_rarity)
	_bonus = Style.label("", 15, Style.MUTED)
	_bonus.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_bonus.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(_bonus)
	_warning = Style.label("", 16, Style.CORAL)
	_warning.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_warning.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(_warning)
	var buttons: HBoxContainer = HBoxContainer.new()
	buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	buttons.add_theme_constant_override("separation", 16)
	column.add_child(buttons)
	sell_button = Style.button("Sell", Style.MUSTARD)
	sell_button.pressed.connect(_resolve.bind("sell"))
	buttons.add_child(sell_button)
	keep_button = Style.button("Keep", Style.MINT)
	keep_button.pressed.connect(_resolve.bind("keep"))
	buttons.add_child(keep_button)


## Fills the panel from the pending prize. Returns false when there is none.
func show_prize(core: RefCounted, is_new: bool) -> bool:
	var view: Dictionary = core.pending_prize_view()
	if view.is_empty():
		return false
	_core = core
	_transaction_id = view["transaction_id"]
	var figure: Dictionary = view["figure"]
	_new_tag.visible = is_new
	_view.show_figure(figure["id"], figure["rarity_color"], reveal_capsule)
	reveal_capsule = ""
	_name.text = figure["name_en"]
	_rarity.text = figure["rarity_name_en"]
	_rarity.add_theme_color_override("font_color", figure["rarity_color"].darkened(0.35))
	_bonus.text = "Collection reward: %s · +%d prestige" % [figure["bonus_text_en"], figure["prestige_reward"]]
	sell_button.text = "Sell for %s" % Format.coins(view["sell_value"])
	var keep: Dictionary = view["keep"]
	keep_button.disabled = not keep["ok"]
	_warning.visible = not keep["ok"]
	if keep["ok"]:
		keep_button.text = "Keep (%d/%d)" % [figure["copies_held"] + 1, figure["copies_required"]]
	elif keep["reason"] == "collection_completed":
		keep_button.text = "Keep (%d/%d)" % [figure["copies_required"], figure["copies_required"]]
		_warning.text = TEXT_COMPLETED
	else:
		keep_button.text = "Keep (%d/%d)" % [figure["copies_held"], figure["copies_required"]]
		_warning.text = TEXT_LOW_FUNDS
	sell_button.grab_focus()
	return true


func _resolve(choice: String) -> void:
	if _core == null:
		return
	var result: Dictionary = _core.resolve_prize(_transaction_id, choice)
	if result["ok"]:
		resolved.emit(result)
