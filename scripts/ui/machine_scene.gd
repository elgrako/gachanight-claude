extends Control
## The view from inside a machine: pressing E at a machine in the hall brings
## the player here, face to face with it, to play it by hand. From here the
## player can jump straight to any other machine or step back into the hall.
##
## Presentation only. The prize is decided and paid for by the core the moment
## the coin goes in; turning the crank, steering the claw or choosing where the
## ball drops is how the player gets to it, not what decides it.
##
## Everything is drawn with simple shapes on purpose: this is the first, plain
## version of each machine's scene.

const Style = preload("res://scripts/ui/ui_style.gd")
const Format = preload("res://scripts/core/format.gd")

enum State { IDLE, PLAYING, ANIMATING, DONE }

## The scene is laid out on this canvas and centred on the screen.
const CANVAS: Vector2 = Vector2(1280.0, 720.0)
const BACKDROP: Color = Color("#1c1410")
const INK: Color = Color("#1c1410")
const CREAM: Color = Color("#e8d9b0")
const GLASS: Color = Color("#b9c2b4")
const STEEL: Color = Color("#8b8676")
const DARK_STEEL: Color = Color("#4a4338")
const BODY_COLORS: Dictionary = {
	"machine_001": Color("#b08a3e"), "machine_002": Color("#5f7384"),
	"machine_005": Color("#6e2f2a"), "machine_006": Color("#7d8f8c"),
}
const BALL_COLORS: Array = [Color("#9c3b2e"), Color("#5f7384"), Color("#c9a24a"), Color("#6f7d4f"), Color("#efe3c4"), Color("#b9807a")]
const CAPSULE_COLORS: Dictionary = {
	"red": Color("#9c3b2e"), "blue": Color("#5f7384"), "green": Color("#6f7d4f"), "mustard": Color("#c9a24a"), "gold": Color("#d9b45a"),
}
const MESSAGE_SECONDS: float = 2.6
## The machine is drawn a little below the title lines.
const DRAW_OFFSET: Vector2 = Vector2(0.0, 26.0)

# --- Capsule machines ---------------------------------------------------------
const GLOBE_CENTRE: Vector2 = Vector2(640.0, 250.0)
const GLOBE_RADIUS: float = 132.0
const KNOB_CENTRE: Vector2 = Vector2(640.0, 452.0)
const KNOB_RADIUS: float = 46.0
const GACHA_CHUTE: Vector2 = Vector2(640.0, 556.0)
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
var _balls: Array = []
var _crank_angle: float = 0.0
var _crank_sounded: bool = false
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
	keys.text = "E play · A/D steer · Q / R previous / next machine · 1-6 jump · Tab catalog · Esc back to the hall"
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
	if _state == State.PLAYING or _state == State.ANIMATING or p_machine_id == machine_id:
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


## The play key: pays for a play, performs the machine's action, or reopens a
## prize that is still waiting.
func press_action() -> void:
	match _state:
		State.IDLE, State.DONE:
			if _core.run.has_pending_prize():
				prize_ready.emit("")
			else:
				_start_play()
		State.PLAYING:
			if _type == "claw":
				_drop_claw()
			elif _type == "plinko":
				_drop_ball()


## Ends the hand-played part at once, as if the player had done it perfectly.
## The tests use it; the prize is the same either way.
func finish_now() -> void:
	if _state != State.PLAYING and _state != State.ANIMATING:
		return
	_stop_tween()
	_capsule_visible = true
	_capsule_at = _chute()
	_ball_visible = false
	_finish()


func is_playing() -> bool:
	return _state == State.PLAYING or _state == State.ANIMATING


# --- Flow ---------------------------------------------------------------------

func _set_machine(p_machine_id: String) -> void:
	_stop_tween()
	machine_id = p_machine_id
	_type = str(_core.data.machines[machine_id]["machine_type"])
	_state = State.IDLE
	_reset_parts()
	# The same balls every time for a machine: it is the same globe.
	var seeded: RandomNumberGenerator = RandomNumberGenerator.new()
	seeded.seed = hash(machine_id)
	_balls.clear()
	for index in range(11):
		var angle: float = seeded.randf() * TAU
		var reach: float = sqrt(seeded.randf()) * (GLOBE_RADIUS - 44.0)
		_balls.append({
			"at": GLOBE_CENTRE + Vector2(cos(angle) * reach, absf(sin(angle)) * reach * 0.8 + 14.0),
			"color": BALL_COLORS[seeded.randi_range(0, BALL_COLORS.size() - 1)],
			"eyes": index % 3 == 0,
		})
	for tab_id in tab_buttons:
		tab_buttons[tab_id].button_pressed = tab_id == machine_id
	_message.text = ""
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


func _start_play() -> void:
	var result: Dictionary = _core.play_machine(machine_id)
	if not result["ok"]:
		Audio.play("error")
		match result["reason"]:
			"power_off":
				flash("No power.")
			"not_enough_coins":
				flash("Not enough coins. This one costs %s." % Format.number(result["price"]))
		return
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


# --- Capsule machine: hold the key to turn the crank ---------------------------

func _turn_crank(delta: float) -> void:
	if not Input.is_action_pressed("interact") and not Input.is_action_pressed("ui_accept"):
		return
	if not _crank_sounded:
		_crank_sounded = true
		Audio.play("crank")
	_crank_angle += delta * TAU / CRANK_SECONDS * _speed()
	if _crank_angle >= TAU:
		_crank_angle = TAU
		_state = State.ANIMATING
		_tween_capsule(_new_tween(), GACHA_CHUTE + Vector2(0.0, -70.0))
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
	if active and _state == State.PLAYING:
		if _type == "gacha":
			_turn_crank(delta)
		elif _type == "claw":
			_steer_claw(delta)
	queue_redraw()


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
		State.PLAYING:
			if _type == "claw":
				_hint.text = "[A/D] Steer the claw   [E] Drop it"
			elif _type == "plinko":
				_hint.text = "[A/D] Choose where the ball falls   [E] Let go"
			else:
				_hint.text = "Hold [E] to turn the crank"
		State.ANIMATING:
			_hint.text = "..."
		_:
			if _core.run.has_pending_prize():
				_hint.text = "[E] Check your prize"
			elif _core.run.coins < price:
				_hint.text = "Not enough coins for this machine"
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
	if machine_id == "":
		return
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
		_:
			_draw_gacha(body)
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


func _draw_gacha(body: Color) -> void:
	# Flared base, cap and globe: the machine seen from right in front of it.
	draw_colored_polygon(PackedVector2Array([Vector2(520.0, 360.0), Vector2(760.0, 360.0), Vector2(840.0, 610.0), Vector2(440.0, 610.0)]), body)
	draw_polyline(PackedVector2Array([Vector2(520.0, 360.0), Vector2(760.0, 360.0), Vector2(840.0, 610.0), Vector2(440.0, 610.0), Vector2(520.0, 360.0)]), INK, 6.0)
	_disc(GLOBE_CENTRE, GLOBE_RADIUS, GLASS, 6.0)
	for ball in _balls:
		# The balls rattle while the crank turns.
		var shake: Vector2 = Vector2.ZERO
		if _state == State.PLAYING and _crank_angle > 0.0:
			shake = Vector2(sin(_time * 40.0 + ball["at"].x), cos(_time * 37.0 + ball["at"].y)) * 3.0
		_disc(ball["at"] + shake, 34.0, ball["color"], 4.0)
		if ball["eyes"]:
			_eyes(ball["at"] + shake, 1.0)
	draw_arc(GLOBE_CENTRE, GLOBE_RADIUS - 18.0, PI * 1.1, PI * 1.45, 12, Color(0.96, 0.91, 0.78, 0.85), 8.0)
	# The machine's own big eyes on the glass, as on its sprite.
	_eyes(GLOBE_CENTRE + Vector2(40.0, -18.0), 4.0)
	_box(Rect2(540.0, 100.0, 200.0, 34.0), body.lightened(0.1))
	_box(Rect2(566.0, 388.0, 148.0, 128.0), STEEL)
	_disc(KNOB_CENTRE, KNOB_RADIUS, DARK_STEEL)
	var handle: Vector2 = Vector2(cos(_crank_angle - PI / 2.0), sin(_crank_angle - PI / 2.0))
	draw_line(KNOB_CENTRE - handle * 34.0, KNOB_CENTRE + handle * 34.0, INK, 20.0)
	draw_line(KNOB_CENTRE - handle * 32.0, KNOB_CENTRE + handle * 32.0, CREAM, 12.0)
	if _state == State.PLAYING:
		draw_arc(KNOB_CENTRE, KNOB_RADIUS + 10.0, -PI / 2.0, -PI / 2.0 + _crank_angle, 32, Style.MUSTARD, 6.0)
	_box(Rect2(GACHA_CHUTE.x - 56.0, GACHA_CHUTE.y - 34.0, 112.0, 64.0), INK.lightened(0.08))


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
	_box(Rect2(claw.x - 16.0, claw.y - 8.0, 32.0, 16.0), Color("#9c3b2e"), 4.0)
	var spread: float = 14.0 if _claw_closed else 34.0
	for side in [-1.0, 1.0]:
		draw_polyline(PackedVector2Array([claw + Vector2(side * 10.0, 6.0), claw + Vector2(side * spread, 30.0), claw + Vector2(side * (spread - 12.0), 52.0)]), INK, 7.0)
	# Control panel: the joystick leans the way the claw is pushed.
	_box(Rect2(410.0, 456.0, 460.0, 44.0), CREAM)
	var lean: float = Input.get_axis("move_left", "move_right") * 14.0 if active and _state == State.PLAYING else 0.0
	draw_line(Vector2(500.0, 486.0), Vector2(500.0 + lean, 452.0), INK, 8.0)
	_disc(Vector2(500.0 + lean, 448.0), 14.0, Color("#9c3b2e"), 4.0)
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
			draw_circle(Vector2(PLINKO_FIRST_X + half * PLINKO_STEP_X, PLINKO_ROW_Y + row * PLINKO_ROW_STEP), 6.0, Color("#9c3b2e"))
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
