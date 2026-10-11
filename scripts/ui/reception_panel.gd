extends PanelContainer
## The reception computer: an over-eager sales terminal. Sells run-scoped
## upgrades, robots and the exit key for coins. Never shows prestige.

const Format = preload("res://scripts/core/format.gd")

const SCREEN: Color = Color("#0f2419")
const PHOSPHOR: Color = Color("#8dffb5")
const DIM: Color = Color("#4f9f74")
const AMBER: Color = Color("#ffd166")
const ALERT: Color = Color("#ff8a7a")

const CATEGORIES: Array = [
	["income", "INCOME"], ["machines", "MACHINES"], ["automation", "ROBOTS"],
	["convenience", "COMFORT"], ["exit", "EXIT"],
]
const LINES: Dictionary = {
	"greet": [
		"Welcome, valued customer!", "Today's special: more money!", "Your productivity is my happiness!",
		"Everything must go! Mostly to you!", "Deals so good they should be illegal! They are not! Probably!",
		"You look like someone who needs an upgrade!",
	],
	"buy": [
		"Fantastic choice!", "You've got GREAT taste in upgrades!", "Sold! No refunds! Probably!",
		"Just one more upgrade!", "A wise investment! I would know, I sold it to you!",
	],
	"not_enough_coins": ["Oh no! Your wallet is on a diet!", "Come back with more coins, dear customer!"],
	"keep_one_coin": ["Keep one coin, valued customer! A broke customer is a sad customer!"],
	"max_level": ["Sold out! You own ALL of it!"],
	"missing_prerequisite": ["Not yet, valued customer! Terms and conditions apply!"],
	"exit": ["The Store Exit Key! Our most exclusive item! But why would you ever leave?"],
	"key": ["Thank you for shopping! Please do not actually leave!"],
	"robot": ["Robots: like employees, but they never ask about the locked door!"],
}
const FACES: Dictionary = {"greet": "(^o^)/", "buy": "(*^_^*)", "sad": "(;_;)", "exit": "(o_o;)", "robot": "[^_^]"}

signal closed

var close_button: Button
## item id -> Buy button, for tests and focus.
var buy_buttons: Dictionary = {}
var tab_buttons: Dictionary = {}

var _core: RefCounted
var _category: String = "income"
var _face: Label
var _speech: Label
var _coins: Label
var _items: VBoxContainer
var _font: SystemFont
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()


func _ready() -> void:
	_rng.randomize()
	_font = SystemFont.new()
	_font.font_names = PackedStringArray(["Consolas", "Menlo", "DejaVu Sans Mono", "Courier New", "monospace"])
	var bezel: StyleBoxFlat = StyleBoxFlat.new()
	bezel.bg_color = Color("#d8d2bf")
	bezel.border_color = Color("#8d8674")
	bezel.set_border_width_all(4)
	bezel.set_corner_radius_all(18)
	bezel.set_content_margin_all(22)
	add_theme_stylebox_override("panel", bezel)
	custom_minimum_size = Vector2(940, 640)
	var screen: PanelContainer = PanelContainer.new()
	var glass: StyleBoxFlat = StyleBoxFlat.new()
	glass.bg_color = SCREEN
	glass.border_color = Color("#2b2b33")
	glass.set_border_width_all(6)
	glass.set_corner_radius_all(14)
	glass.set_content_margin_all(18)
	screen.add_theme_stylebox_override("panel", glass)
	add_child(screen)
	var column: VBoxContainer = VBoxContainer.new()
	column.add_theme_constant_override("separation", 10)
	screen.add_child(column)
	var header: HBoxContainer = HBoxContainer.new()
	header.add_theme_constant_override("separation", 16)
	column.add_child(header)
	_face = _text("", 34, AMBER)
	_face.custom_minimum_size.x = 150
	header.add_child(_face)
	var talk: VBoxContainer = VBoxContainer.new()
	talk.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(talk)
	talk.add_child(_text("HAPPY SALES TERMINAL  v1.987", 14, DIM))
	_speech = _text("", 20, PHOSPHOR)
	_speech.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_speech.custom_minimum_size.y = 56
	talk.add_child(_speech)
	_coins = _text("", 20, AMBER)
	header.add_child(_coins)
	var tabs: HBoxContainer = HBoxContainer.new()
	tabs.add_theme_constant_override("separation", 8)
	column.add_child(tabs)
	for entry in CATEGORIES:
		var tab: Button = _button(entry[1], DIM)
		tab.pressed.connect(_select_category.bind(entry[0]))
		tabs.add_child(tab)
		tab_buttons[entry[0]] = tab
	var scroll: ScrollContainer = ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	column.add_child(scroll)
	_items = VBoxContainer.new()
	_items.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_items.add_theme_constant_override("separation", 8)
	scroll.add_child(_items)
	var footer: HBoxContainer = HBoxContainer.new()
	column.add_child(footer)
	var note: Label = _text("Everything sold here stays in the store when you sleep.", 14, DIM)
	note.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	footer.add_child(note)
	close_button = _button("LEAVE [Esc]", ALERT)
	close_button.pressed.connect(func() -> void: closed.emit())
	footer.add_child(close_button)


func open(core: RefCounted) -> void:
	_core = core
	_say("greet", "greet")
	_select_category(_category)
	close_button.grab_focus()


func refresh() -> void:
	if _core != null and is_visible_in_tree():
		_coins.text = Format.coins(_core.run.coins)
		_rebuild()


func _select_category(category: String) -> void:
	_category = category
	for key in tab_buttons:
		tab_buttons[key].add_theme_color_override("font_color", AMBER if key == category else PHOSPHOR)
	if category == "exit":
		_say("exit", "exit")
	elif category == "automation":
		_say("robot", "robot")
	_coins.text = Format.coins(_core.run.coins)
	_rebuild()


func _rebuild() -> void:
	for child in _items.get_children():
		_items.remove_child(child)
		child.queue_free()
	buy_buttons.clear()
	for item_id in _core.data.reception_order:
		var view: Dictionary = _core.reception_item_view(item_id)
		if view["category"] == _category:
			_items.add_child(_item_row(view))


func _item_row(view: Dictionary) -> Control:
	var box: PanelContainer = PanelContainer.new()
	var frame: StyleBoxFlat = StyleBoxFlat.new()
	frame.bg_color = Color("#143122")
	frame.border_color = DIM
	frame.set_border_width_all(2)
	frame.set_corner_radius_all(6)
	frame.set_content_margin_all(10)
	box.add_theme_stylebox_override("panel", frame)
	var column: VBoxContainer = VBoxContainer.new()
	box.add_child(column)
	var row: HBoxContainer = HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	column.add_child(row)
	var text: VBoxContainer = VBoxContainer.new()
	text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(text)
	var maxed: bool = view["level"] >= view["max_level"]
	var title: String = view["display_name_en"]
	if view["max_level"] > 1:
		title += "   Lv %d/%d" % [view["level"], view["max_level"]]
	elif maxed:
		title += "   OWNED"
	text.add_child(_text(title, 19, AMBER if maxed else PHOSPHOR))
	var detail: Label = _text(view["description_en"], 14, DIM)
	detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text.add_child(detail)
	if not view["missing_en"].is_empty() and not maxed:
		text.add_child(_text("Requires: " + ", ".join(view["missing_en"]), 14, ALERT))
	var buy: Button = _button("SOLD OUT" if maxed else "BUY  %s" % Format.number(view["cost"]), PHOSPHOR)
	buy.custom_minimum_size.x = 190
	buy.disabled = maxed
	if not maxed and not view["can_buy"]:
		buy.add_theme_color_override("font_color", DIM)
	buy.pressed.connect(_buy.bind(view["id"]))
	row.add_child(buy)
	buy_buttons[view["id"]] = buy
	if view["robot_machine_id"] != "" and view["level"] > 0:
		column.add_child(_robot_controls(view["robot_machine_id"]))
	return box


func _robot_controls(machine_id: String) -> Control:
	var robot: Dictionary = _core.robot_view(machine_id)
	var row: HBoxContainer = HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	var status: Label = _text("%d working · %.1f spins/s" % [robot["count"], robot["spins_per_second"]], 14, DIM)
	if robot["paused"]:
		status.text = "%d on a break" % robot["count"]
	status.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(status)
	var mode: Button = _button("COLLECT, THEN SELL" if robot["mode"] == "collect" else "SELL EVERYTHING", AMBER)
	mode.pressed.connect(func() -> void:
		_core.set_robot_mode(machine_id, "sell_all" if robot["mode"] == "collect" else "collect")
		_rebuild())
	row.add_child(mode)
	var pause: Button = _button("RESUME" if robot["paused"] else "PAUSE", AMBER)
	pause.pressed.connect(func() -> void:
		_core.set_robot_paused(machine_id, not robot["paused"])
		_rebuild())
	row.add_child(pause)
	return row


func _buy(item_id: String) -> void:
	var result: Dictionary = _core.buy_reception_item(item_id)
	if result["ok"]:
		_say("key" if result["bought_key"] else "buy", "buy")
	else:
		_say(result["reason"], "sad")
		Audio.play("error")
	_coins.text = Format.coins(_core.run.coins)
	_rebuild()


func _say(topic: String, face: String) -> void:
	var options: Array = LINES.get(topic, LINES["greet"])
	_speech.text = options[_rng.randi() % options.size()]
	_face.text = FACES.get(face, FACES["greet"])


func _text(content: String, size: int, color: Color) -> Label:
	var label: Label = Label.new()
	label.text = content
	label.add_theme_font_override("font", _font)
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	return label


func _button(content: String, color: Color) -> Button:
	var button: Button = Button.new()
	button.text = content
	button.custom_minimum_size = Vector2(120, 40)
	button.add_theme_font_override("font", _font)
	button.add_theme_font_size_override("font_size", 17)
	for state in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		button.add_theme_color_override(state, color)
	button.add_theme_color_override("font_disabled_color", Color("#3d6b52"))
	for state in ["normal", "hover", "pressed", "focus", "disabled"]:
		var style: StyleBoxFlat = StyleBoxFlat.new()
		style.bg_color = Color("#1f4a33") if state == "hover" or state == "focus" else Color("#183a28")
		style.border_color = color if state != "disabled" else Color("#3d6b52")
		style.set_border_width_all(3 if state == "focus" else 2)
		style.set_corner_radius_all(4)
		style.set_content_margin_all(8)
		button.add_theme_stylebox_override(state, style)
	return button
