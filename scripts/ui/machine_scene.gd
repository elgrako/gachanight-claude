extends Control
## The view from inside a machine: pressing E at a machine in the hall brings
## the player here, face to face with it, to play it by hand. From here the
## player can jump straight to any other machine or step back into the hall.
##
## The prize is decided and paid for by the core the moment the coin goes in.
## On the crane and the plinko, steering the claw or choosing where the ball
## drops is only how the player gets to it. On a capsule machine the player's
## hand does count: a timing wheel is stopped before the coin goes in, and the
## closer to its mark, the more luck that one play carries.
##
## A capsule machine is seen from right in front of it, almost in first
## person, all in pixel art: `gacha_pov.gd` draws it in a 320 x 180 viewport
## shown at four screen pixels per pixel, from the state kept here. The crane
## and the plinko are still drawn with simple shapes by this script.

const Style = preload("res://scripts/ui/ui_style.gd")
const Format = preload("res://scripts/core/format.gd")
const GachaPov = preload("res://scripts/ui/gacha_pov.gd")

## AIMING is the capsule machines' timing wheel turning, before any coin goes in.
enum State { IDLE, AIMING, PLAYING, ANIMATING, DONE }

## The scene is laid out on this canvas and centred on the screen.
const CANVAS: Vector2 = Vector2(1280.0, 720.0)
const BACKDROP: Color = Color("#0e0d0c")
const INK: Color = Color("#0e0d0c")
const CREAM: Color = Color("#e3d9c6")
const GLASS: Color = Color("#c9bb9f")
const STEEL: Color = Color("#9a8766")
const DARK_STEEL: Color = Color("#4c4337")
const BODY_COLORS: Dictionary = {
	"machine_001": Color("#9a8766"), "machine_002": Color("#74806c"),
	"machine_005": Color("#5a3d28"), "machine_006": Color("#74806c"),
}
const BALL_COLORS: Array = [Color("#8a4e30"), Color("#74806c"), Color("#b98d5c"), Color("#74806c"), Color("#e3d9c6"), Color("#9a8766")]
const CAPSULE_COLORS: Dictionary = {
	"red": Color("#8a4e30"), "blue": Color("#74806c"), "green": Color("#74806c"), "mustard": Color("#b98d5c"), "gold": Color("#d0b870"),
}
const MESSAGE_SECONDS: float = 2.6
## The machine is drawn a little below the title lines.
const DRAW_OFFSET: Vector2 = Vector2(0.0, 26.0)

# --- Capsule machines ---------------------------------------------------------
## Where the capsule comes to rest in the mouth and where it drops from, in
## this scene's 1280 x 720 (four times the pixel-art view's own coordinates).
const GACHA_CHUTE: Vector2 = Vector2(640.0, 672.0)
const GACHA_DROP_FROM: Vector2 = Vector2(640.0, 560.0)
## Turns a second of the needle, and half the width of the mark in radians,
## before upgrades.
const WHEEL_TURNS: float = 0.8
const MARK_HALF: float = 0.42
## How close to the middle of the mark each grade asks for, as a share of the
## mark's half width, and the luck it adds to that play, in percent.
const GRADES: Array = [["PERFECT!", 0.22, 60.0], ["GREAT", 0.6, 30.0], ["GOOD", 1.0, 12.0]]
const MISS: String = "MISS"
const UPGRADE_KEYS: Array = [KEY_Z, KEY_X, KEY_C]
## Seconds of holding E for one full turn of the crank, at speed 1.
const CRANK_SECONDS: float = 0.9

# --- Crane --------------------------------------------------------------------
const CLAW_WINDOW: Rect2 = Rect2(410.0, 140.0, 460.0, 300.0)
const CLAW_RAIL_Y: float = 158.0
const CLAW_TOP_Y: float = 190.0
const CLAW_GRAB_Y: float = 372.0
const CLAW_MIN_X: float = 450.0
const CLAW_MAX_X: float = 730.0
const CLAW_HOLE_X: float = 815.0
const CLAW_SPEED: float = 240.0
const CLAW_PRIZES: int = 6
const CLAW_PRIZE_Y: float = 408.0
const CLAW_CHUTE: Vector2 = Vector2(815.0, 548.0)

# --- Plinko -------------------------------------------------------------------
const BOARD: Rect2 = Rect2(430.0, 120.0, 420.0, 400.0)
const PLINKO_SLOTS: int = 5
const PLINKO_ROWS: int = 8
## The ball moves on half-slot steps: 0 is the first slot's centre, 8 the last.
const PLINKO_STEP_X: float = 42.0
const PLINKO_FIRST_X: float = 472.0
const PLINKO_TOP_Y: float = 150.0
const PLINKO_ROW_Y: float = 190.0
const PLINKO_ROW_STEP: float = 36.0
const PLINKO_SLOT_Y: float = 496.0
const PLINKO_HOP_SECONDS: float = 0.15
const PLINKO_CHUTE: Vector2 = Vector2(640.0, 566.0)

## The play finished with a prize to decide on. `capsule_color` is "" when the
## prize was already waiting and its capsule is long open.
signal prize_ready(capsule_color: String)
signal machine_changed(machine_id: String)
signal exit_requested

var machine_id: String = ""
## False while a panel covers the scene: it then ignores every key.
var active: bool = false
var tab_buttons: Dictionary = {}
var exit_button: Button

var _core: RefCounted
var _type: String = "gacha"
var _state: int = State.IDLE
var _result: Dictionary = {}
var _tween: Tween
var _time: float = 0.0
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()
var _title: Label
var _price: Label
var _coins: Label
var _hint: Label
var _message: Label
var _message_left: float = 0.0
var _capsule_color: String = "red"
var _capsule_at: Vector2 = Vector2.ZERO
var _capsule_visible: bool = false
var _crank_angle: float = 0.0
var _crank_sounded: bool = false
var _needle: float = 0.0
var _mark_at: float = 0.0
var _grade: String = ""
var _grade_luck: float = 0.0
## Time since the wheel was stopped, for the pop of the grade.
var _grade_age: float = 10.0
## 0 to 1 while the coin flies to the slot.
var _coin_flight: float = 1.0
## The pixel-art view of a capsule machine, and the viewport it is drawn in.
var _pov: Node2D
var _pov_frame: SubViewportContainer
## What only the plainly drawn machines show: the capsule machine's view
## writes all of it itself, in its own letters.
var _plain_parts: Array = []
var _claw_x: float = CLAW_MIN_X
var _claw_y: float = CLAW_TOP_Y
var _claw_closed: bool = false
var _claw_held: int = -1
var _claw_taken: Array = []
var _column: int = PLINKO_SLOTS / 2
var _ball_at: Vector2 = Vector2.ZERO
var _ball_visible: bool = false
var _lit_slot: int = -1


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_rng.randomize()
	var top: HBoxContainer = HBoxContainer.new()
	top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	top.offset_top = 14.0
	top.offset_left = 16.0
	top.offset_right = -16.0
	top.alignment = BoxContainer.ALIGNMENT_CENTER
	top.add_theme_constant_override("separation", 8)
	add_child(top)
	exit_button = _small_button("< Hall  [Esc]", Style.CORAL)
	exit_button.pressed.connect(func() -> void: exit_requested.emit())
	top.add_child(exit_button)
	_title = _text(24, CREAM)
	_title.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_title.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_title.offset_top = 62.0
	add_child(_title)
	_price = _text(17, Style.MUSTARD)
	_price.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	_price.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_price.offset_left = 26.0
	_price.offset_bottom = -78.0
	add_child(_price)
	_hint = _text(20, CREAM)
	_hint.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	_hint.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_hint.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_hint.offset_bottom = -40.0
	add_child(_hint)
	var keys: Label = _text(13, Color(CREAM, 0.8))
	_plain_parts = [top, _title, _price, _hint, keys]
	keys.text = "E play · A/D steer · Z X C upgrades · Q / R previous / next machine · 1-6 jump · Tab catalog · Esc back to the hall"
	keys.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	keys.grow_horizontal = Control.GROW_DIRECTION_BOTH
	keys.grow_vertical = Control.GROW_DIRECTION_BEGIN
	keys.offset_bottom = -12.0
	add_child(keys)
	_coins = _text(26, Style.MUSTARD)
	_coins.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	_coins.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_coins.offset_left = 24.0
	_coins.offset_bottom = -40.0
	add_child(_coins)
	_message = _text(22, Style.MUSTARD)
	_message.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_message.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_message.offset_top = 96.0
	add_child(_message)
	set_meta("top_bar", top)
	_plain_parts.append(_coins)
	_plain_parts.append(_message)
	_pov_frame = SubViewportContainer.new()
	_pov_frame.stretch = true
	_pov_frame.stretch_shrink = int(CANVAS.x) / GachaPov.SIZE.x
	_pov_frame.size = CANVAS
	_pov_frame.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_pov_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_pov_frame.visible = false
	add_child(_pov_frame)
	var view: SubViewport = SubViewport.new()
	view.size = GachaPov.SIZE
	view.disable_3d = true
	view.snap_2d_transforms_to_pixel = true
	view.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	_pov_frame.add_child(view)
	_pov = GachaPov.new()
	_pov.scene = self
	view.add_child(_pov)


## Shows the scene on a machine. Called once per visit; `show_machine` changes
## machine without leaving.
func open(core: RefCounted, p_machine_id: String) -> void:
	if _core == null:
		_core = core
		_build_tabs()
		core.coins_changed.connect(func(_coins_now: int) -> void: _refresh_texts())
		core.modifiers_changed.connect(_refresh_texts)
		core.prize_resolved.connect(_on_prize_resolved)
	visible = true
	_state = State.IDLE
	_set_machine(p_machine_id)


func close() -> void:
	_stop_tween()
	visible = false
	active = false


## Jumps to another machine. Refused in the middle of a play.
func show_machine(p_machine_id: String) -> bool:
	if is_playing() or p_machine_id == machine_id:
		return false
	if not _core.data.machines.has(p_machine_id):
		return false
	Audio.play("click")
	_set_machine(p_machine_id)
	machine_changed.emit(machine_id)
	return true


## A line of text over the machine for a moment.
func flash(text: String) -> void:
	_message.text = text
	_message_left = MESSAGE_SECONDS


## The play key: starts or stops the timing wheel, pays for a play, performs
## the machine's action, or reopens a prize that is still waiting.
func press_action() -> void:
	match _state:
		State.IDLE, State.DONE:
			if _core.run.has_pending_prize():
				prize_ready.emit("")
			elif _type == "gacha":
				_start_wheel()
			else:
				_start_play()
		State.AIMING:
			_stop_wheel(true)
		State.PLAYING:
			if _type == "claw":
				_drop_claw()
			elif _type == "plinko":
				_drop_ball()


## Ends the hand-played part at once. The tests use it. A timing wheel still
## turning is stopped with no luck earned.
func finish_now() -> void:
	if _state == State.AIMING:
		_stop_wheel(false)
	if _state != State.PLAYING and _state != State.ANIMATING:
		return
	_stop_tween()
	_capsule_visible = true
	_capsule_at = _chute()
	_ball_visible = false
	_coin_flight = 1.0
	_crank_angle = TAU
	_finish()


func is_playing() -> bool:
	return _state == State.AIMING or _state == State.PLAYING or _state == State.ANIMATING


# --- Flow ---------------------------------------------------------------------

func _set_machine(p_machine_id: String) -> void:
	_stop_tween()
	machine_id = p_machine_id
	_type = str(_core.data.machines[machine_id]["machine_type"])
	_state = State.IDLE
	_reset_parts()
	for tab_id in tab_buttons:
		tab_buttons[tab_id].button_pressed = tab_id == machine_id
	_message.text = ""
	_grade = ""
	_grade_age = 10.0
	_pov_frame.visible = _type == "gacha"
	for part in _plain_parts:
		part.visible = _type != "gacha"
	_refresh_texts()
	queue_redraw()


func _reset_parts() -> void:
	_capsule_visible = false
	_crank_angle = 0.0
	_crank_sounded = false
	_claw_x = CLAW_MIN_X
	_claw_y = CLAW_TOP_Y
	_claw_closed = false
	_claw_held = -1
	_claw_taken.clear()
	_column = PLINKO_SLOTS / 2
	_ball_visible = false
	_lit_slot = -1


## Whether a play could be paid for right now; says why not.
func _can_play() -> bool:
	var check: Dictionary = _core.can_play_machine(machine_id)
	if check["ok"]:
		return true
	Audio.play("error")
	match check["reason"]:
		"power_off":
			flash("No power.")
		"not_enough_coins":
			flash("Not enough coins. This one costs %s." % Format.number(check["price"]))
	return false


## Pays for a play and has the core decide the prize. `extra_luck_pct` is what
## the timing wheel earned. False if the play could not be paid for.
func _start_play(extra_luck_pct: float = 0.0) -> bool:
	if not _can_play():
		return false
	var result: Dictionary = _core.play_machine(machine_id, extra_luck_pct)
	if not result["ok"]:
		return false
	# Paid and saved: from here on everything is show.
	_result = result
	_reset_parts()
	var colors: Array = CAPSULE_COLORS.keys()
	_capsule_color = colors[_rng.randi_range(0, colors.size() - 1)]
	Audio.play("coin", -4.0)
	_state = State.PLAYING
	if _type == "plinko":
		_ball_visible = true
		_ball_at = Vector2(_column_x(_column), PLINKO_TOP_Y)
	_refresh_texts()
	return true


func _finish() -> void:
	_state = State.DONE
	Audio.play("capsule")
	if _result.get("auto_sold", false):
		Audio.play("sell", -3.0)
		flash("Duplicate sold: +%s" % Format.coins(_result["coins_gained"]))
		_state = State.IDLE
	else:
		prize_ready.emit(_capsule_color)
	_refresh_texts()


func _on_prize_resolved(result: Dictionary) -> void:
	if not visible:
		return
	_state = State.IDLE
	_capsule_visible = false
	_lit_slot = -1
	if result.get("choice", "") == "sell":
		flash("+%s" % Format.coins(result.get("coins_gained", 0)))
	else:
		flash("Kept!")
	_refresh_texts()


func _speed() -> float:
	return maxf(_core.crank_speed_multiplier(), 0.1)


func _chute() -> Vector2:
	if _type == "claw":
		return CLAW_CHUTE
	if _type == "plinko":
		return PLINKO_CHUTE
	return GACHA_CHUTE


func _stop_tween() -> void:
	if _tween != null:
		_tween.kill()
		_tween = null


func _new_tween() -> Tween:
	_stop_tween()
	_tween = create_tween()
	_tween.set_speed_scale(_speed())
	return _tween


## The capsule falls into the tray with one bounce, then the play is over.
func _tween_capsule(tween: Tween, from: Vector2) -> void:
	var to: Vector2 = _chute()
	tween.tween_callback(func() -> void:
		_capsule_at = from
		_capsule_visible = true)
	tween.tween_property(self, "_capsule_at", to, 0.22).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_property(self, "_capsule_at", to + Vector2(0.0, -12.0), 0.09).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "_capsule_at", to, 0.09).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_callback(_finish)


# --- Capsule machine: the timing wheel, then the crank turns by itself ----------

## The wheel starts turning; nothing is paid yet, so stepping away costs nothing.
func _start_wheel() -> void:
	if not _can_play():
		return
	_state = State.AIMING
	_grade = ""
	_mark_at = _rng.randf_range(0.6, TAU - 0.6)
	_needle = wrapf(_mark_at + PI + _rng.randf_range(-0.8, 0.8), 0.0, TAU)
	Audio.play("click", -6.0)
	_refresh_texts()


## Half the width of the mark, in radians, with this machine's upgrades.
func _mark_half() -> float:
	return minf(MARK_HALF * (1.0 + _core.machine_effect(machine_id, "qte_zone_pct") / 100.0), PI * 0.6)


## Radians a second of the needle, with this machine's upgrades.
func _needle_speed() -> float:
	return TAU * WHEEL_TURNS * maxf(1.0 - _core.machine_effect(machine_id, "qte_slow_pct") / 100.0, 0.3)


## The wheel stops where the needle is: that grades the play, the coin goes in
## and the machine does the rest. `timed` is false when the tests skip the wheel.
func _stop_wheel(timed: bool) -> void:
	var off: float = absf(wrapf(_needle - _mark_at, -PI, PI)) / _mark_half()
	_grade = MISS
	_grade_luck = 0.0
	if timed:
		for grade in GRADES:
			if off <= grade[1]:
				_grade = grade[0]
				_grade_luck = grade[2]
				break
	_grade_age = 0.0
	if not _start_play(_grade_luck):
		_state = State.IDLE
		_refresh_texts()
		return
	_state = State.ANIMATING
	Audio.play("crank")
	_coin_flight = 0.0
	var tween: Tween = _new_tween()
	tween.tween_property(self, "_coin_flight", 1.0, 0.28)
	tween.tween_property(self, "_crank_angle", TAU, CRANK_SECONDS).from(0.0)
	_tween_capsule(tween, GACHA_DROP_FROM)
	_refresh_texts()


# --- Capsule machine: what its pixel-art view reads ------------------------------

func is_aiming() -> bool:
	return _state == State.AIMING


func is_cranking() -> bool:
	return _state == State.ANIMATING and _crank_angle > 0.0 and _crank_angle < TAU


func is_perfect() -> bool:
	return _grade == GRADES[0][0]


func grade_text() -> String:
	return _grade


func grade_luck() -> float:
	return _grade_luck


func grade_age() -> float:
	return _grade_age


func needle_angle() -> float:
	return _needle


func mark_angle() -> float:
	return _mark_at


func mark_half() -> float:
	return _mark_half()


func crank_angle() -> float:
	return _crank_angle


func coin_flight() -> float:
	return _coin_flight


func capsule_showing() -> bool:
	return _capsule_visible


func capsule_point() -> Vector2:
	return _capsule_at


func capsule_index() -> int:
	return CAPSULE_COLORS.keys().find(_capsule_color)


func coins() -> int:
	return _core.run.coins


func price() -> int:
	return _core.machine_price(machine_id)


func message_text() -> String:
	return _message.text


func short_number(value: int) -> String:
	return Format.number(value)


func upgrade_views() -> Array:
	return _core.machine_upgrade_views(machine_id)


func upgrade_key(index: int) -> String:
	return OS.get_keycode_string(UPGRADE_KEYS[index]) if index < UPGRADE_KEYS.size() else ""


## What the play key does right now, in a word or two.
func action_text() -> String:
	match _state:
		State.AIMING:
			return "E  STOP!"
		State.ANIMATING, State.PLAYING:
			return "..."
	if _core.run.has_pending_prize():
		return "E  PRIZE"
	if _core.run.coins < price():
		return "NO COINS"
	return "E  SPIN"


# --- Capsule machine: the upgrades sold at this machine ---------------------------

## Buys the upgrade in row `index` of this machine's file.
func buy_upgrade_at(index: int) -> void:
	var views: Array = upgrade_views()
	if index >= 0 and index < views.size():
		_buy_upgrade(views[index]["id"])


func _buy_upgrade(item_id: String) -> void:
	if is_playing():
		return
	var result: Dictionary = _core.buy_reception_item(item_id)
	if result["ok"]:
		Audio.play("sell", -4.0)
		flash("%s  Lv %d" % [_core.data.reception_upgrades[item_id]["display_name_en"], result["level"]])
	else:
		Audio.play("error")
		match result["reason"]:
			"max_level":
				flash("Already at its best.")
			"keep_one_coin":
				flash("Keep one coin for the machine.")
			_:
				flash("Not enough coins.")
	_refresh_texts()


# --- Crane: steer, then drop ---------------------------------------------------

func _steer_claw(delta: float) -> void:
	var axis: float = Input.get_axis("move_left", "move_right")
	_claw_x = clampf(_claw_x + axis * CLAW_SPEED * delta, CLAW_MIN_X, CLAW_MAX_X)


func _prize_x(index: int) -> float:
	return CLAW_MIN_X + (CLAW_MAX_X - CLAW_MIN_X) * index / float(CLAW_PRIZES - 1)


func _drop_claw() -> void:
	_state = State.ANIMATING
	_refresh_texts()
	# The claw always comes up with something: it takes the nearest plush.
	var nearest: int = 0
	for index in range(CLAW_PRIZES):
		if absf(_prize_x(index) - _claw_x) < absf(_prize_x(nearest) - _claw_x):
			nearest = index
	var tween: Tween = _new_tween()
	tween.tween_property(self, "_claw_x", _prize_x(nearest), 0.12)
	tween.tween_property(self, "_claw_y", CLAW_GRAB_Y, 0.45).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_callback(func() -> void:
		_claw_closed = true
		_claw_held = nearest
		_claw_taken.append(nearest)
		Audio.play("click"))
	tween.tween_interval(0.15)
	tween.tween_property(self, "_claw_y", CLAW_TOP_Y, 0.45).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "_claw_x", CLAW_HOLE_X, 0.5).set_trans(Tween.TRANS_SINE)
	tween.tween_callback(func() -> void:
		_claw_closed = false
		_claw_held = -1)
	_tween_capsule(tween, Vector2(CLAW_HOLE_X, CLAW_TOP_Y + 60.0))


# --- Plinko: choose a column, then drop ----------------------------------------

func _column_x(column: int) -> float:
	return PLINKO_FIRST_X + column * 2.0 * PLINKO_STEP_X


func _move_column(step: int) -> void:
	var next: int = clampi(_column + step, 0, PLINKO_SLOTS - 1)
	if next != _column:
		_column = next
		_ball_at = Vector2(_column_x(_column), PLINKO_TOP_Y)
		Audio.play("click", -8.0, 0.2)


## Half-slot steps, -1 or +1 per row, from the chosen column to the slot the
## core already picked, never leaving the board.
func _plinko_steps(from_half: int, to_half: int) -> Array:
	var steps: Array = []
	var at: int = from_half
	for row in range(PLINKO_ROWS):
		var left_after: int = PLINKO_ROWS - row - 1
		var options: Array = []
		for step in [-1, 1]:
			var next: int = at + step
			if next >= 0 and next <= (PLINKO_SLOTS - 1) * 2 and absi(to_half - next) <= left_after:
				options.append(step)
		var chosen: int = options[_rng.randi_range(0, options.size() - 1)]
		steps.append(chosen)
		at += chosen
	return steps


func _drop_ball() -> void:
	_state = State.ANIMATING
	_refresh_texts()
	var slot: int = clampi(int(_result.get("slot", 0)), 0, PLINKO_SLOTS - 1)
	var half: int = _column * 2
	var tween: Tween = _new_tween()
	var at: Vector2 = Vector2(_column_x(_column), PLINKO_ROW_Y - 12.0)
	tween.tween_property(self, "_ball_at", at, 0.12).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	var row: int = 0
	for step in _plinko_steps(half, slot * 2):
		half += step
		row += 1
		var from: Vector2 = at
		at = Vector2(PLINKO_FIRST_X + half * PLINKO_STEP_X, PLINKO_ROW_Y - 12.0 + row * PLINKO_ROW_STEP)
		tween.tween_callback(func() -> void: Audio.play("plinko", -4.0, 0.2))
		tween.tween_method(_hop_ball.bind(from, at), 0.0, 1.0, PLINKO_HOP_SECONDS)
	tween.tween_property(self, "_ball_at", Vector2(_column_x(slot), PLINKO_SLOT_Y), 0.1)
	tween.tween_callback(func() -> void: _lit_slot = slot)
	tween.tween_interval(0.3)
	tween.tween_callback(func() -> void: _ball_visible = false)
	_tween_capsule(tween, PLINKO_CHUTE + Vector2(0.0, -40.0))


func _hop_ball(progress: float, from: Vector2, to: Vector2) -> void:
	_ball_at = from.lerp(to, progress) - Vector2(0.0, sin(progress * PI) * 12.0)


# --- Input and texts -----------------------------------------------------------

func _process(delta: float) -> void:
	if not visible:
		return
	_time += delta
	if _message_left > 0.0:
		_message_left -= delta
		if _message_left <= 0.0:
			_message.text = ""
	_grade_age += delta
	if _state == State.AIMING:
		_needle = wrapf(_needle + _needle_speed() * delta, 0.0, TAU)
	if active and _state == State.PLAYING and _type == "claw":
		_steer_claw(delta)
	_pov_frame.position = ((size - CANVAS) / 2.0).floor()
	queue_redraw()


## A click on a row of the capsule machine's file buys that upgrade.
func _gui_input(event: InputEvent) -> void:
	if _type != "gacha" or not active:
		return
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var row: int = _pov.row_at((event.position - _pov_frame.position) / float(_pov_frame.stretch_shrink))
		if row >= 0:
			buy_upgrade_at(row)
			accept_event()


func _unhandled_input(event: InputEvent) -> void:
	if not visible or not active:
		return
	if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		press_action()
		accept_event()
	elif _state == State.PLAYING and _type == "plinko" and event.is_action_pressed("move_left"):
		_move_column(-1)
	elif _state == State.PLAYING and _type == "plinko" and event.is_action_pressed("move_right"):
		_move_column(1)
	elif event is InputEventKey and event.pressed and not event.echo:
		var order: Array = _core.data.machine_order
		var index: int = order.find(machine_id)
		if event.physical_keycode == KEY_Q:
			show_machine(order[posmod(index - 1, order.size())])
		elif event.physical_keycode == KEY_R:
			show_machine(order[posmod(index + 1, order.size())])
		elif UPGRADE_KEYS.has(event.physical_keycode):
			if _type == "gacha":
				buy_upgrade_at(UPGRADE_KEYS.find(event.physical_keycode))
		elif event.physical_keycode >= KEY_1 and event.physical_keycode <= KEY_9:
			var wanted: int = event.physical_keycode - KEY_1
			if wanted < order.size():
				show_machine(order[wanted])


func _refresh_texts() -> void:
	if _core == null or machine_id == "":
		return
	var machine: Dictionary = _core.data.machines[machine_id]
	_title.text = "%s — %s" % [machine["display_name_en"], machine.get("series_name_en", "")]
	var price: int = _core.machine_price(machine_id)
	_price.text = "One play: %s" % Format.coins(price)
	_coins.text = Format.coins(_core.run.coins)
	for tab_id in tab_buttons:
		tab_buttons[tab_id].disabled = is_playing() and tab_id != machine_id
	match _state:
		State.AIMING:
			_hint.text = "[E] Stop the wheel on the mark"
		State.PLAYING:
			if _type == "claw":
				_hint.text = "[A/D] Steer the claw   [E] Drop it"
			elif _type == "plinko":
				_hint.text = "[A/D] Choose where the ball falls   [E] Let go"
		State.ANIMATING:
			_hint.text = "..."
		_:
			if _core.run.has_pending_prize():
				_hint.text = "[E] Check your prize"
			elif _core.run.coins < price:
				_hint.text = "Not enough coins for this machine"
			elif _type == "gacha":
				_hint.text = "[E] Spin the wheel   (a play costs %s)" % Format.coins(price)
			else:
				_hint.text = "[E] Insert %s" % Format.coins(price)


func _build_tabs() -> void:
	var top: HBoxContainer = get_meta("top_bar")
	var number: int = 0
	for tab_id in _core.data.machine_order:
		number += 1
		var tab: Button = _small_button("%d  %s" % [number, _core.data.machines[tab_id]["display_name_en"]], BODY_COLORS.get(tab_id, STEEL).lightened(0.35))
		tab.toggle_mode = true
		tab.pressed.connect(func() -> void:
			if not show_machine(tab_id):
				tab.button_pressed = tab_id == machine_id)
		top.add_child(tab)
		tab_buttons[tab_id] = tab


func _small_button(text: String, color: Color) -> Button:
	var button: Button = Style.button(text, color)
	button.custom_minimum_size = Vector2(0.0, 36.0)
	button.add_theme_font_size_override("font_size", 14)
	# Keys belong to the machine; the mouse can still click.
	button.focus_mode = Control.FOCUS_NONE
	return button


func _text(font_size: int, color: Color) -> Label:
	var label: Label = Label.new()
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", INK)
	label.add_theme_constant_override("outline_size", 6)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label


# --- Drawing -------------------------------------------------------------------

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), BACKDROP)
	if machine_id == "" or _type == "gacha":
		return                                              # a capsule machine has its own pixel-art view
	var body: Color = BODY_COLORS.get(machine_id, STEEL)
	draw_set_transform(((size - CANVAS) / 2.0).floor() + DRAW_OFFSET)
	# The room behind, far and dim, so it still feels like the store.
	draw_rect(Rect2(-400.0, 0.0, CANVAS.x + 800.0, 470.0), body.darkened(0.72))
	draw_rect(Rect2(-400.0, 470.0, CANVAS.x + 800.0, 250.0), body.darkened(0.82))
	match _type:
		"claw":
			_draw_crane(body)
		"plinko":
			_draw_plinko(body)
	if _capsule_visible:
		_draw_capsule(_capsule_at, 24.0, CAPSULE_COLORS.get(_capsule_color, BALL_COLORS[0]))
	draw_set_transform(Vector2.ZERO)


func _box(rect: Rect2, color: Color, outline: float = 6.0) -> void:
	draw_rect(rect, color)
	draw_rect(rect, INK, false, outline)


func _disc(at: Vector2, radius: float, color: Color, outline: float = 5.0) -> void:
	draw_circle(at, radius, INK)
	draw_circle(at, radius - outline, color)


func _eyes(at: Vector2, scale_by: float) -> void:
	for side in [-1.0, 1.0]:
		var eye: Vector2 = at + Vector2(side * 7.0 * scale_by, 0.0)
		draw_rect(Rect2(eye - Vector2(5.0, 9.0) * scale_by, Vector2(10.0, 18.0) * scale_by), CREAM)
		draw_rect(Rect2(eye - Vector2(5.0, 9.0) * scale_by, Vector2(10.0, 18.0) * scale_by), INK, false, 2.0)
		draw_rect(Rect2(eye + Vector2(0.0, -5.0) * scale_by, Vector2(4.0, 12.0) * scale_by), INK)


func _draw_capsule(at: Vector2, radius: float, color: Color) -> void:
	draw_circle(at, radius, INK)
	draw_circle(at, radius - 4.0, CREAM)
	# Coloured top half.
	var top: PackedVector2Array = PackedVector2Array()
	for step in range(13):
		var angle: float = PI + PI * step / 12.0
		top.append(at + Vector2(cos(angle), sin(angle)) * (radius - 4.0))
	draw_colored_polygon(top, color)
	draw_line(at + Vector2(-radius + 4.0, 0.0), at + Vector2(radius - 4.0, 0.0), INK, 3.0)
	draw_circle(at + Vector2(-radius * 0.35, -radius * 0.45), radius * 0.16, Color.WHITE)


func _draw_crane(body: Color) -> void:
	_box(Rect2(380.0, 96.0, 520.0, 520.0), body)
	_box(CLAW_WINDOW, GLASS)
	_eyes(Vector2(640.0, 118.0), 1.0)
	draw_line(Vector2(CLAW_WINDOW.position.x, CLAW_RAIL_Y), Vector2(CLAW_WINDOW.end.x, CLAW_RAIL_Y), DARK_STEEL, 8.0)
	# The drop hole on the right of the box.
	draw_rect(Rect2(CLAW_HOLE_X - 36.0, CLAW_WINDOW.end.y - 34.0, 72.0, 34.0), INK)
	for index in range(CLAW_PRIZES):
		if _claw_taken.has(index):
			continue
		var at: Vector2 = Vector2(_prize_x(index), CLAW_PRIZE_Y)
		_disc(at, 26.0, BALL_COLORS[index % BALL_COLORS.size()], 4.0)
		_eyes(at + Vector2(0.0, -2.0), 0.8)
	var claw: Vector2 = Vector2(_claw_x, _claw_y)
	draw_line(Vector2(_claw_x, CLAW_RAIL_Y), claw, INK, 4.0)
	if _claw_held >= 0:
		var held: Vector2 = claw + Vector2(0.0, 40.0)
		_disc(held, 26.0, BALL_COLORS[_claw_held % BALL_COLORS.size()], 4.0)
		_eyes(held + Vector2(0.0, -2.0), 0.8)
	_box(Rect2(claw.x - 16.0, claw.y - 8.0, 32.0, 16.0), Color("#8a4e30"), 4.0)
	var spread: float = 14.0 if _claw_closed else 34.0
	for side in [-1.0, 1.0]:
		draw_polyline(PackedVector2Array([claw + Vector2(side * 10.0, 6.0), claw + Vector2(side * spread, 30.0), claw + Vector2(side * (spread - 12.0), 52.0)]), INK, 7.0)
	# Control panel: the joystick leans the way the claw is pushed.
	_box(Rect2(410.0, 456.0, 460.0, 44.0), CREAM)
	var lean: float = Input.get_axis("move_left", "move_right") * 14.0 if active and _state == State.PLAYING else 0.0
	draw_line(Vector2(500.0, 486.0), Vector2(500.0 + lean, 452.0), INK, 8.0)
	_disc(Vector2(500.0 + lean, 448.0), 14.0, Color("#8a4e30"), 4.0)
	_disc(Vector2(600.0, 478.0), 14.0, Style.MUSTARD, 4.0)
	_box(Rect2(CLAW_CHUTE.x - 52.0, CLAW_CHUTE.y - 34.0, 104.0, 64.0), INK.lightened(0.08))


func _draw_plinko(body: Color) -> void:
	_box(Rect2(390.0, 76.0, 500.0, 540.0), body)
	_eyes(Vector2(640.0, 98.0), 1.0)
	_box(BOARD, CREAM)
	for row in range(PLINKO_ROWS):
		# Pegs sit where the ball can land: every other half-step, staggered.
		var half: int = row % 2
		while half <= (PLINKO_SLOTS - 1) * 2:
			draw_circle(Vector2(PLINKO_FIRST_X + half * PLINKO_STEP_X, PLINKO_ROW_Y + row * PLINKO_ROW_STEP), 6.0, Color("#8a4e30"))
			half += 2
	for slot in range(PLINKO_SLOTS):
		var slot_rect: Rect2 = Rect2(_column_x(slot) - PLINKO_STEP_X + 3.0, PLINKO_SLOT_Y - 20.0, PLINKO_STEP_X * 2.0 - 6.0, 40.0)
		var color: Color = BALL_COLORS[slot % BALL_COLORS.size()]
		if slot == _lit_slot and int(_time * 10.0) % 2 == 0:
			color = Color.WHITE
		_box(slot_rect, color, 3.0)
	if _state == State.PLAYING:
		# Where the ball will be let go.
		draw_line(Vector2(_column_x(_column), PLINKO_TOP_Y + 14.0), Vector2(_column_x(_column), PLINKO_ROW_Y - 12.0), Color(INK, 0.35), 3.0)
	if _ball_visible:
		_disc(_ball_at, 11.0, STEEL.lightened(0.5), 3.0)
	_box(Rect2(PLINKO_CHUTE.x - 56.0, PLINKO_CHUTE.y - 30.0, 112.0, 60.0), INK.lightened(0.08))
