extends Node2D
## The toy store as one side-view strip of rooms, built in code from the
## pixel-art sprites. Presentation only: it never changes game state.
##
## Units are world pixels. The floor line is y = 0, the wall goes up from it,
## and everything that stands on the floor is anchored at its bottom centre.

const Interactable = preload("res://scripts/world/interactable.gd")
const Sprites = preload("res://scripts/world/sprite_lib.gd")

const C_INK: Color = Color("#1d2a44")
const C_CREAM: Color = Color("#f4ecd8")
const C_MUSTARD: Color = Color("#e3b44c")
const C_NIGHT: Color = Color("#0d1322")

# --- Layout -----------------------------------------------------------------
const WALL_TOP: float = -148.0
const FLOOR_DEPTH: float = 32.0
const CEILING_HEIGHT: float = 8.0
const TRIM_HEIGHT: float = 6.0
## Rooms from left to right: name, first x, wall tile, floor tile.
const ROOMS: Array = [
	["bath", 0.0, "wall_bath", "floor_bath"],
	["corridor", 150.0, "wall_corridor", "floor_hall"],
	["hall", 250.0, "wall_hall", "floor_hall"],
	["reception", 790.0, "wall_reception", "floor_hall"],
	["staff", 950.0, "wall_staff", "floor_staff"],
]
const STORE_WIDTH: float = 1110.0
const PILLAR_WIDTH: float = 12.0
const WALK_MIN_X: float = 16.0
const WALK_MAX_X: float = STORE_WIDTH - 16.0
## The player walks a little in front of the wall; robots stand nearer still.
const PLAYER_Y: float = 9.0
const ROBOT_Y: float = 20.0

const SPAWN_X: float = 44.0
const COIN_XS: Array = [84.0, 104.0, 126.0]
const COIN_Y: float = 14.0
const SWITCH_X: float = 200.0
const MACHINE_XS: Dictionary = {
	"machine_001": 300.0,
	"machine_002": 360.0,
	"machine_003": 420.0,
	"machine_004": 480.0,
	"machine_005": 572.0,
	"machine_006": 664.0,
}
const COUNTER_X: float = 848.0
const DOOR_X: float = 918.0
const SOFA_X: float = 1036.0
const LAMP_XS: Array = [75.0, 200.0, 330.0, 450.0, 572.0, 700.0, 868.0, 1030.0]
const LAMP_Y: float = WALL_TOP + CEILING_HEIGHT
const MAX_ROBOT_SPRITES: int = 3
## Where each robot of a team stands, relative to its machine. `robot_work`
## reaches to the robot's right, so the one on the right side is mirrored:
## every arm points at the machine's controls.
const ROBOT_OFFSETS: Array = [Vector2(-10.0, 0.0), Vector2(10.0, 0.0), Vector2(-24.0, 3.0)]
const ROBOT_FLIPS: Array = [false, true, false]
## Team mates neither start on the same frame nor keep the same pace.
const ROBOT_FRAME_OFFSETS: Array = [0, 3, 6]
const ROBOT_PACES: Array = [1.0, 0.91, 1.08]
## Where the sleeping player lies, relative to the sofa's bottom centre.
const SOFA_SEAT: Vector2 = Vector2(0.0, -11.0)

# --- Display rail: every figure, a dark silhouette until discovered -----------
const DISPLAY_START_X: float = 284.0
const DISPLAY_STEP_X: float = 34.0
const DISPLAY_PER_ROW: int = 15
const DISPLAY_ROW_YS: Array = [-108.0, -76.0]
const SILHOUETTE: Color = Color(0.07, 0.08, 0.12)

# --- Machine anchors, relative to the machine's bottom centre ----------------
const GACHA_SIZE: Vector2i = Vector2i(36, 60)
const GACHA_KNOB: Vector2 = Vector2(0.0, -22.0)
const GACHA_CHUTE: Vector2 = Vector2(0.0, -9.0)
const BIG_SIZE: Vector2i = Vector2i(56, 76)
const CLAW_RAIL_Y: float = -66.0
const CLAW_REST_X: float = -14.0
const CLAW_GRAB_Y: float = -56.0
const CLAW_DROP_X: float = 16.0
const CLAW_CHUTE: Vector2 = Vector2(16.0, -12.0)
## Centre of a held capsule below the claw's hanging point, and the prize hole it falls into.
const CLAW_HOLD: Vector2 = Vector2(0.0, 13.0)
const CLAW_HOLE_Y: float = -36.0
## The ball rests on the top peg here; each row is one peg lower and half a slot aside.
const PLINKO_TOP: Vector2 = Vector2(0.0, -65.0)
const PLINKO_MAX_OFFSET: float = 16.0
const PLINKO_ROWS: int = 6
const PLINKO_ROW_STEP: float = 5.0
const PLINKO_COLUMN_STEP: float = 4.0
const PLINKO_SLOT_Y: float = -29.0
const PLINKO_SLOTS: int = 5
const PLINKO_CHUTE: Vector2 = Vector2(0.0, -10.0)
const CAPSULE_COLORS: Array = ["coral", "mint", "mustard", "teal", "gold"]

# --- Animation timing, seconds at speed 1 -----------------------------------
## The player's hand arrives on frame 3 of `player_use` (12 fps); machines and
## the power switch wait this long so the action starts under the hand.
const USE_LEAD_TIME: float = 0.25
# Gacha: lead-in + wind-up + turn + clunk + chute drop = 1.13 s (budget 1.2 s).
const CRANK_WINDUP_TIME: float = 0.1
const CRANK_WINDUP_ANGLE: float = -0.6
const CRANK_TURN: float = 0.42
const CRANK_CLUNK_TIME: float = 0.06
const RATTLE_STEPS: float = 10.0
# Crane: lead-in + 2.30 s = 2.55 s (budget 2.7 s).
const CLAW_MOVE_TIME: float = 0.38
const CLAW_SETTLE_TIME: float = 0.1
const CLAW_LOWER_TIME: float = 0.32
const CLAW_GRAB_TIME: float = 0.16
const CLAW_LIFT_TIME: float = 0.36
const CLAW_CARRY_TIME: float = 0.42
const CLAW_RELEASE_TIME: float = 0.16
const CLAW_RETURN_TIME: float = 0.45
const CLAW_SWAY: float = 0.24
# Plinko: lead-in + drop + 6 hops + slot + blink + chute drop = 2.11 s (budget 2.3 s).
const PLINKO_DROP_TIME: float = 0.14
const PLINKO_HOP_TIME: float = 0.17
const PLINKO_HOP_HEIGHT: float = 2.5
const PLINKO_SLOT_TIME: float = 0.1
const PLINKO_HOLD_TIME: float = 0.3
const PLINKO_BLINKS: float = 3.0
const PEG_FLASH_TIME: float = 0.16
const CHUTE_DROP_TIME: float = 0.3
const POWER_LAMP_STEP: float = 0.12
const POWER_MACHINE_BLINK: float = 0.04
const POWER_MACHINE_STEP: float = 0.05
const DARK: Color = Color(0.3, 0.35, 0.58)
const DOOR_OPEN_TIME: float = 0.9
const DOOR_GLOW_ALPHA: float = 0.6
const DOOR_MOTES: Array = [Vector2(-8.0, -44.0), Vector2(9.0, -28.0), Vector2(-3.0, -14.0)]
## Glow strength for each frame of `lamp_flicker` (off, ends, off, off, on, ends, off, half, on, off, on, on).
const LAMP_FLICKER_LEVELS: Array = [0.0, 0.35, 0.0, 0.0, 1.0, 0.35, 0.0, 0.6, 1.0, 0.0, 1.0, 1.0]
const LAMP_GLOW_TOP: float = 0.17
const COIN_BOB_SPEED: float = 3.0
const COIN_TWINKLE_EVERY: float = 1.7
## Turns per second of a gacha knob while robots work the machine, at most.
const ROBOT_KNOB_MAX_RATE: float = 1.5

## One bounce of the plinko ball, for the sound.
signal plinko_bounced
## One machine waking up during the power-on sequence, for the sound.
signal machine_lit

## machine_id -> {root, body, type, lit, price, robots, knob, capsule, claw, rope, ball, slot_lamp}
var machines: Dictionary = {}
var coins: Array = []
var power_switch: Node2D
var sofa: Node2D
var reception: Node2D
var door: Node2D
## Everything the player can use, for the player's reach test.
var interactables: Array = []

var _modulate: CanvasModulate
var _lamps: Array = []
var _lit_overlays: Array = []
var _switch_sprite: Sprite2D
var _computer: Sprite2D
var _screen_glow: AnimatedSprite2D
var _door_sprite: Sprite2D
var _door_glow: Polygon2D
var _door_tween: Tween
var _power_tween: Tween
var _power_on: bool = false
var _display: Dictionary = {}
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()
var _time: float = 0.0
var _next_twinkle: float = COIN_TWINKLE_EVERY

## Colour name of the capsule the last prize animation used, so the prize
## reveal can open the same capsule.
var last_capsule_color: String = "coral"


func _ready() -> void:
	_rng.randomize()
	_modulate = CanvasModulate.new()
	_modulate.color = DARK
	add_child(_modulate)
	_build_shell()
	_build_bathroom()
	_build_corridor()
	_build_hall()
	_build_reception()
	_build_staff_room()
	_build_lamps()
	set_power(false, false)


func _draw() -> void:
	# Night outside the store, so a wider or taller window never shows a void.
	draw_rect(Rect2(-2000.0, -2000.0, STORE_WIDTH + 4000.0, 4000.0), C_NIGHT)


## Back walls, floors, ceiling, skirting and the pillars between rooms.
func _build_shell() -> void:
	for index in range(ROOMS.size()):
		var room: Array = ROOMS[index]
		var from_x: float = room[1]
		var to_x: float = ROOMS[index + 1][1] if index + 1 < ROOMS.size() else STORE_WIDTH
		_tiled("tiles/%s" % room[2], Rect2(from_x, WALL_TOP, to_x - from_x, -WALL_TOP), Vector2i(16, 16), Color("#efe4c8"))
		_tiled("tiles/%s" % room[3], Rect2(from_x, 0.0, to_x - from_x, FLOOR_DEPTH), Vector2i(16, 16), Color("#a9825a"))
	_tiled("tiles/ceiling", Rect2(0.0, WALL_TOP, STORE_WIDTH, CEILING_HEIGHT), Vector2i(16, 8), C_INK)
	_tiled("tiles/trim", Rect2(0.0, -TRIM_HEIGHT, STORE_WIDTH, TRIM_HEIGHT), Vector2i(16, 6), Color("#a9825a"))
	var pillar_xs: Array = [0.0, STORE_WIDTH - PILLAR_WIDTH]
	for index in range(1, ROOMS.size()):
		pillar_xs.append(ROOMS[index][1] - PILLAR_WIDTH / 2.0)
	for x in pillar_xs:
		_tiled("tiles/pillar", Rect2(x, WALL_TOP + CEILING_HEIGHT, PILLAR_WIDTH, -WALL_TOP - CEILING_HEIGHT), Vector2i(12, 16), Color("#dccaa6"))


func _tiled(path: String, area: Rect2, fallback_size: Vector2i, fallback_color: Color) -> void:
	var rect: TextureRect = TextureRect.new()
	rect.texture = Sprites.texture(path, fallback_size, fallback_color)
	rect.stretch_mode = TextureRect.STRETCH_TILE
	rect.position = area.position
	rect.size = area.size
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(rect)

# --- Public presentation API --------------------------------------------------

func set_power(is_on: bool, animate: bool) -> void:
	if _power_tween != null:
		_power_tween.kill()
		_power_tween = null
	_power_on = is_on
	if is_on and animate:
		_play_power_on()
		return
	_set_switch(is_on)
	_modulate.color = Color.WHITE if is_on else DARK
	for lamp in _lamps:
		_set_lamp(lamp, is_on)
	for overlay in _lit_overlays:
		overlay.visible = is_on
	_set_computer(is_on)


func set_coin_collected(index: int, collected: bool, animate: bool = false) -> void:
	var coin: Node2D = coins[index]
	if collected and animate and coin.visible:
		# The effect's first frame has the coin at the bottom of its 24 px frame.
		Sprites.burst(self, "coin_pickup", coin.position + Vector2(0.0, -12.0), Vector2i(16, 24))
	coin.visible = not collected


func set_price_text(machine_id: String, text: String) -> void:
	machines[machine_id]["price"].text = text


## `rate` is spins per second for the whole team; 0 means the robots are idle.
func set_robots(machine_id: String, count: int, rate: float) -> void:
	var robots: Array = machines[machine_id]["robots"]
	machines[machine_id]["robot_rate"] = rate if count > 0 else 0.0
	var cycle: float = maxf(Sprites.animation_length("robot_work"), 0.1)
	for index in range(robots.size()):
		var robot: AnimatedSprite2D = robots[index]
		robot.visible = index < count
		if not robot.visible:
			continue
		var wanted: String = "robot_work" if rate > 0.0 else "robot_idle"
		var pace: float = ROBOT_PACES[index % ROBOT_PACES.size()]
		robot.speed_scale = (clampf(rate * cycle, 0.5, 2.5) if rate > 0.0 else 1.0) * pace
		if robot.animation != wanted or not robot.is_playing():
			robot.play(wanted)
			# Team mates do not hop in step.
			robot.frame = ROBOT_FRAME_OFFSETS[index % ROBOT_FRAME_OFFSETS.size()] % maxi(robot.sprite_frames.get_frame_count(wanted), 1)


## Shows every figure on the hall's display rail; undiscovered ones as silhouettes.
## `figures` is an ordered Array of {id, discovered}.
func set_display(figures: Array) -> void:
	for index in range(figures.size()):
		var figure: Dictionary = figures[index]
		var figure_id: String = figure["id"]
		if not _display.has(figure_id):
			var row: int = mini(index / DISPLAY_PER_ROW, DISPLAY_ROW_YS.size() - 1)
			var column: int = index - row * DISPLAY_PER_ROW
			var at: Vector2 = Vector2(DISPLAY_START_X + column * DISPLAY_STEP_X, DISPLAY_ROW_YS[row])
			_display[figure_id] = _standing("figures/%s" % figure_id, at, Vector2i(32, 32))
		_display[figure_id].modulate = Color.WHITE if figure["discovered"] else SILHOUETTE


## Plays the machine's prize animation. The returned tween finishes when the
## capsule is in the tray; the prize itself was decided before this started.
## `lead_in` seconds pass first, while the player's hand reaches the machine.
func play_prize_animation(machine_id: String, slot: int, speed: float, lead_in: float = 0.0) -> Tween:
	var machine: Dictionary = machines[machine_id]
	_rest_machine(machine)
	var capsule: Sprite2D = machine["capsule"]
	last_capsule_color = CAPSULE_COLORS[_rng.randi_range(0, CAPSULE_COLORS.size() - 1)]
	capsule.texture = Sprites.texture("machines/capsule_%s" % last_capsule_color, Vector2i(10, 10), C_MUSTARD)
	machine["speed"] = maxf(speed, 0.1)
	var tween: Tween = create_tween()
	tween.set_speed_scale(machine["speed"])
	if lead_in > 0.0:
		tween.tween_interval(lead_in)
	match machine["type"]:
		"claw":
			_animate_claw(tween, machine)
		"plinko":
			_animate_plinko(tween, machine, slot)
		_:
			_animate_crank(tween, machine)
	machine["busy"] = true
	tween.finished.connect(func() -> void: machine["busy"] = false)
	return tween


## The door swings open and daylight spills across the floor.
func play_door_open() -> void:
	if _door_tween != null:
		_door_tween.kill()
	_door_sprite.texture = Sprites.texture("props/door_open", Vector2i(44, 68), C_CREAM)
	_door_glow.visible = true
	_door_glow.modulate.a = 0.0
	_door_glow.scale = Vector2(0.35, 1.0)
	_door_tween = create_tween()
	_door_tween.tween_property(_door_glow, "modulate:a", DOOR_GLOW_ALPHA, DOOR_OPEN_TIME * 0.5).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	_door_tween.parallel().tween_property(_door_glow, "scale:x", 1.0, DOOR_OPEN_TIME).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	# Dust motes catch the light, one after another.
	for index in range(DOOR_MOTES.size()):
		_door_tween.parallel().tween_callback(_door_mote.bind(DOOR_MOTES[index])).set_delay(DOOR_OPEN_TIME * (0.25 + 0.2 * index))


func _door_mote(offset: Vector2) -> void:
	Sprites.burst(self, "sparkle", Vector2(DOOR_X, 0.0) + offset, Vector2i(16, 16))


func reset_door() -> void:
	if _door_tween != null:
		_door_tween.kill()
		_door_tween = null
	_door_sprite.texture = Sprites.texture("props/door_closed", Vector2i(44, 68), Color("#4f9ea3"))
	_door_glow.visible = false


# --- Machine animations -------------------------------------------------------

## Wind back, one full turn with the cabinet rattling, a clunk, then the capsule.
func _animate_crank(tween: Tween, machine: Dictionary) -> void:
	var knob: Sprite2D = machine["knob"]
	var root: Node2D = machine["root"]
	var rest_x: float = machine["x"]
	tween.tween_callback(func() -> void: knob.rotation = 0.0)
	tween.tween_property(knob, "rotation", CRANK_WINDUP_ANGLE, CRANK_WINDUP_TIME).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tween.tween_property(knob, "rotation", TAU, CRANK_TURN).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_method(_rattle.bind(root, rest_x), 0.0, 1.0, CRANK_TURN)
	tween.tween_callback(func() -> void:
		knob.rotation = 0.0
		root.position.x = rest_x)
	# The capsule lands inside: the whole cabinet hops one pixel.
	tween.tween_property(root, "position:y", -1.0, CRANK_CLUNK_TIME * 0.5)
	tween.tween_property(root, "position:y", 0.0, CRANK_CLUNK_TIME * 0.5)
	_tween_chute_drop(tween, machine, GACHA_CHUTE + Vector2(0.0, -6.0), GACHA_CHUTE)


## Whole-pixel shake that dies out before the turn ends.
func _rattle(progress: float, root: Node2D, rest_x: float) -> void:
	var side: float = 1.0 if int(progress * RATTLE_STEPS) % 2 == 0 else -1.0
	root.position.x = rest_x + (side if progress < 0.8 else 0.0)


## Travel with the claw swinging behind, lower, grab, lift, carry, release.
func _animate_claw(tween: Tween, machine: Dictionary) -> void:
	var claw: Sprite2D = machine["claw"]
	var capsule: Sprite2D = machine["capsule"]
	var root: Node2D = machine["root"]
	var rest_x: float = machine["x"]
	var speed: float = machine["speed"]
	var target_x: float = roundf(_rng.randf_range(-10.0, 4.0))
	var open: Texture2D = Sprites.texture("machines/claw_open", Vector2i(16, 16), C_INK)
	var closed: Texture2D = Sprites.texture("machines/claw_closed", Vector2i(16, 16), C_INK)
	# Out to the prize: the claw lags behind the carriage, then settles.
	tween.tween_property(claw, "position:x", target_x, CLAW_MOVE_TIME).set_trans(Tween.TRANS_SINE)
	tween.parallel().tween_method(_sway.bind(claw, CLAW_SWAY, 1.5), 0.0, 1.0, CLAW_MOVE_TIME + CLAW_SETTLE_TIME)
	tween.tween_property(claw, "position:y", CLAW_GRAB_Y, CLAW_LOWER_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	# Grab: the claw snaps shut, dips into the pile and the cabinet shudders.
	tween.tween_callback(func() -> void:
		claw.texture = closed
		machine["held"] = true
		capsule.rotation = 0.0
		capsule.position = claw.position + CLAW_HOLD
		capsule.visible = true)
	tween.tween_property(claw, "position:y", CLAW_GRAB_Y + 1.0, CLAW_GRAB_TIME * 0.3)
	tween.tween_property(claw, "position:y", CLAW_GRAB_Y, CLAW_GRAB_TIME * 0.3)
	tween.parallel().tween_method(_rattle.bind(root, rest_x), 0.5, 1.0, CLAW_GRAB_TIME * 0.7)
	tween.tween_property(claw, "position:y", CLAW_RAIL_Y, CLAW_LIFT_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_method(_sway.bind(claw, CLAW_SWAY * 0.4, 1.0), 0.0, 1.0, CLAW_LIFT_TIME)
	# Carry to the prize hole, swinging with the weight.
	tween.tween_property(claw, "position:x", CLAW_DROP_X, CLAW_CARRY_TIME).set_trans(Tween.TRANS_SINE)
	tween.parallel().tween_method(_sway.bind(claw, CLAW_SWAY, 1.5), 0.0, 1.0, CLAW_CARRY_TIME + CLAW_SETTLE_TIME)
	# Release: the capsule falls into the hole, the claw kicks back and goes home.
	tween.tween_callback(func() -> void:
		claw.texture = open
		machine["held"] = false
		capsule.position = Vector2(CLAW_DROP_X, CLAW_RAIL_Y) + CLAW_HOLD
		var home: Tween = create_tween()
		home.set_speed_scale(speed)
		home.tween_method(_sway.bind(claw, -CLAW_SWAY * 0.6, 1.0), 0.0, 1.0, CLAW_RELEASE_TIME)
		home.tween_property(claw, "position:x", CLAW_REST_X, CLAW_RETURN_TIME).set_trans(Tween.TRANS_SINE)
		home.parallel().tween_method(_sway.bind(claw, -CLAW_SWAY * 0.5, 1.5), 0.0, 1.0, CLAW_RETURN_TIME + CLAW_SETTLE_TIME)
		machine["aux"] = home)
	tween.tween_property(capsule, "position:y", CLAW_HOLE_Y, CLAW_RELEASE_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	_tween_chute_drop(tween, machine, CLAW_CHUTE + Vector2(0.0, -6.0), CLAW_CHUTE)


## A damped pendulum swing of the claw around its hanging point. A positive
## amplitude starts by trailing to the left (the claw is moving right).
func _sway(progress: float, claw: Sprite2D, amplitude: float, swings: float) -> void:
	claw.rotation = amplitude * sin(progress * TAU * swings) * (1.0 - progress)


## The ball drops onto the top peg, hops down row by row and lights its slot.
func _animate_plinko(tween: Tween, machine: Dictionary, slot: int) -> void:
	var ball: Sprite2D = machine["ball"]
	var lamp: Polygon2D = machine["slot_lamp"]
	var root: Node2D = machine["root"]
	var final_slot: int = clampi(slot, 0, PLINKO_SLOTS - 1)
	# Each row moves the ball half a slot; the mix of lefts and rights decides the slot.
	var rights: int = PLINKO_ROWS / 2 + (final_slot - PLINKO_SLOTS / 2)
	var steps: Array = []
	for index in range(PLINKO_ROWS):
		steps.append(1.0 if index < rights else -1.0)
	# Shuffle until the path stays on the pegs of the board.
	for attempt in range(40):
		for index in range(steps.size() - 1, 0, -1):
			var other: int = _rng.randi_range(0, index)
			var kept: float = steps[index]
			steps[index] = steps[other]
			steps[other] = kept
		var offset: float = 0.0
		var widest: float = 0.0
		for step in steps:
			offset += step * PLINKO_COLUMN_STEP
			widest = maxf(widest, absf(offset))
		if widest <= PLINKO_MAX_OFFSET:
			break
	var at: Vector2 = PLINKO_TOP
	tween.tween_callback(func() -> void:
		ball.position = PLINKO_TOP + Vector2(0.0, -4.0)
		ball.visible = true)
	tween.tween_property(ball, "position", at, PLINKO_DROP_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	for step in steps:
		var from: Vector2 = at
		at += Vector2(step * PLINKO_COLUMN_STEP, PLINKO_ROW_STEP)
		tween.tween_callback(_peg_hit.bind(root, from))
		tween.tween_method(_pose_hop.bind(ball, from, at), 0.0, 1.0, PLINKO_HOP_TIME)
	var slot_x: float = (final_slot - PLINKO_SLOTS / 2) * PLINKO_COLUMN_STEP * 2.0
	tween.tween_property(ball, "position", Vector2(slot_x, PLINKO_SLOT_Y), PLINKO_SLOT_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_callback(func() -> void: lamp.position = Vector2(slot_x, PLINKO_SLOT_Y))
	tween.tween_method(_blink.bind(lamp), 0.0, 1.0, PLINKO_HOLD_TIME)
	tween.tween_callback(func() -> void:
		ball.visible = false
		lamp.visible = false)
	_tween_chute_drop(tween, machine, PLINKO_CHUTE + Vector2(0.0, -6.0), PLINKO_CHUTE)


## The ball strikes the peg it rests on: a sound and a glint on the peg.
func _peg_hit(root: Node2D, ball_at: Vector2) -> void:
	plinko_bounced.emit()
	_flash(root, ball_at + Vector2(-1.0, 2.0), Vector2(2.0, 2.0), PEG_FLASH_TIME)


## A bounce off a peg: straight across, up and over under gravity.
func _pose_hop(progress: float, ball: Sprite2D, from: Vector2, to: Vector2) -> void:
	var at: Vector2 = from.lerp(to, progress)
	at.y = from.y + (to.y - from.y) * progress * progress - sin(progress * PI) * PLINKO_HOP_HEIGHT
	ball.position = at.round()


func _blink(progress: float, lamp: Polygon2D) -> void:
	lamp.visible = int(progress * PLINKO_BLINKS * 2.0) % 2 == 0


## A small square of light that fades out, e.g. a peg struck by the ball.
func _flash(parent: Node2D, at: Vector2, flash_size: Vector2, seconds: float) -> void:
	var flash: ColorRect = ColorRect.new()
	flash.color = Color(1.0, 1.0, 0.85, 0.95)
	flash.position = at
	flash.size = flash_size
	flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(flash)
	var fade: Tween = flash.create_tween()
	fade.tween_property(flash, "color:a", 0.0, seconds)
	fade.tween_callback(flash.queue_free)


## The capsule drops out of the chute, bounces twice while it rolls a quarter
## turn per bounce, and a sparkle marks it in the tray.
func _tween_chute_drop(tween: Tween, machine: Dictionary, from: Vector2, to: Vector2) -> void:
	var capsule: Sprite2D = machine["capsule"]
	var root: Node2D = machine["root"]
	tween.tween_callback(func() -> void:
		capsule.position = from
		capsule.rotation = 0.0
		capsule.visible = true)
	tween.tween_property(capsule, "position", to, CHUTE_DROP_TIME * 0.4).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_callback(func() -> void: capsule.rotation = PI / 2.0)
	tween.tween_property(capsule, "position", to + Vector2(0.0, -3.0), CHUTE_DROP_TIME * 0.2).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(capsule, "position", to, CHUTE_DROP_TIME * 0.2).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_callback(func() -> void: capsule.rotation = PI)
	tween.tween_property(capsule, "position", to + Vector2(0.0, -1.0), CHUTE_DROP_TIME * 0.1)
	tween.tween_property(capsule, "position", to, CHUTE_DROP_TIME * 0.1)
	tween.tween_callback(_tray_sparkle.bind(root, to))


func _tray_sparkle(root: Node2D, tray: Vector2) -> void:
	Sprites.burst(self, "sparkle", root.position + tray + Vector2(4.0, -5.0), Vector2i(16, 16))


## Puts the moving parts back before a new animation.
func _rest_machine(machine: Dictionary) -> void:
	if machine["aux"] != null and machine["aux"].is_valid():
		machine["aux"].kill()
	machine["aux"] = null
	machine["held"] = false
	machine["root"].position = Vector2(machine["x"], 0.0)
	machine["capsule"].visible = false
	machine["capsule"].rotation = 0.0
	match machine["type"]:
		"claw":
			machine["claw"].position = Vector2(CLAW_REST_X, CLAW_RAIL_Y)
			machine["claw"].rotation = 0.0
			machine["claw"].texture = Sprites.texture("machines/claw_open", Vector2i(16, 16), C_INK)
		"plinko":
			machine["ball"].visible = false
			machine["slot_lamp"].visible = false
		_:
			machine["knob"].rotation = 0.0


# --- Power --------------------------------------------------------------------

## The lever flips under the player's hand, the lamps flicker on from the
## switch outwards while the room brightens, then the machines wake one by one.
func _play_power_on() -> void:
	_power_tween = create_tween()
	_power_tween.tween_interval(USE_LEAD_TIME)
	_power_tween.tween_callback(_set_switch.bind(true))
	var order: Array = _lamps.duplicate()
	order.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		return absf(a["x"] - SWITCH_X) < absf(b["x"] - SWITCH_X))
	var lit: int = 0
	for lamp in order:
		lit += 1
		var level: float = float(lit) / order.size()
		_power_tween.tween_callback(_flicker_lamp.bind(lamp))
		_power_tween.tween_property(_modulate, "color", DARK.lerp(Color.WHITE, level), POWER_LAMP_STEP)
	_power_tween.tween_callback(_set_computer.bind(true))
	for overlay in _lit_overlays:
		# Each sign blinks once before it stays on.
		_power_tween.tween_callback(_wake_overlay.bind(overlay, true, true))
		_power_tween.tween_interval(POWER_MACHINE_BLINK)
		_power_tween.tween_callback(_wake_overlay.bind(overlay, false, false))
		_power_tween.tween_interval(POWER_MACHINE_BLINK)
		_power_tween.tween_callback(_wake_overlay.bind(overlay, true, false))
		_power_tween.tween_interval(POWER_MACHINE_STEP)


## One step of a machine sign coming on; the first one clicks, the last one twinkles.
func _wake_overlay(overlay: Sprite2D, is_on: bool, first: bool) -> void:
	overlay.visible = is_on
	if first:
		machine_lit.emit()
	elif is_on:
		var machine_root: Node2D = overlay.get_parent()
		var top: float = -float(overlay.texture.get_height()) + 6.0
		Sprites.burst(self, "sparkle", machine_root.position + Vector2(_rng.randf_range(-8.0, 8.0), top), Vector2i(16, 16))


func _set_switch(is_on: bool) -> void:
	_switch_sprite.texture = Sprites.texture("props/power_switch_%s" % ("on" if is_on else "off"), Vector2i(16, 24))


func _flicker_lamp(lamp: Dictionary) -> void:
	_set_lamp(lamp, true)
	var flicker: AnimatedSprite2D = lamp["flicker"]
	if flicker != null:
		lamp["glow"].modulate.a = 0.0
		flicker.visible = true
		flicker.play("lamp_flicker")


## The light cone follows the tube while it flickers.
func _on_flicker_frame(lamp: Dictionary) -> void:
	var flicker: AnimatedSprite2D = lamp["flicker"]
	if flicker.visible and flicker.is_playing() and flicker.frame < LAMP_FLICKER_LEVELS.size():
		lamp["glow"].modulate.a = LAMP_FLICKER_LEVELS[flicker.frame]


func _on_flicker_finished(lamp: Dictionary) -> void:
	lamp["flicker"].visible = false
	lamp["glow"].modulate.a = 1.0


func _set_lamp(lamp: Dictionary, is_on: bool) -> void:
	lamp["sprite"].texture = Sprites.texture("props/ceiling_lamp_%s" % ("on" if is_on else "off"), Vector2i(32, 12), C_CREAM if is_on else C_INK)
	lamp["glow"].visible = is_on
	lamp["glow"].modulate.a = 1.0
	if lamp["flicker"] != null:
		lamp["flicker"].stop()
		lamp["flicker"].visible = false


func _set_computer(is_on: bool) -> void:
	_computer.texture = Sprites.texture("props/computer_%s" % ("on" if is_on else "off"), Vector2i(24, 22), C_INK)
	if _screen_glow != null:
		_screen_glow.visible = is_on


# --- Rooms --------------------------------------------------------------------

func _build_bathroom() -> void:
	_standing("props/toilet", Vector2(24.0, 0.0), Vector2i(24, 30))
	_standing("props/sink", Vector2(66.0, 0.0), Vector2i(24, 34))
	_standing("props/poster_d", Vector2(112.0, -58.0), Vector2i(24, 32))
	for index in range(COIN_XS.size()):
		var coin: Node2D = _interactable("Coin%d" % index, Vector2(COIN_XS[index], COIN_Y), 11.0)
		coin.set_meta("coin_index", index)
		var spin: AnimatedSprite2D = Sprites.animated(["coin_spin"], Vector2i(10, 10), C_MUSTARD)
		spin.play("coin_spin")
		spin.frame = index * 2
		coin.add_child(spin)
		coin.set_meta("spin", spin)
		coins.append(coin)


func _build_corridor() -> void:
	power_switch = _interactable("PowerSwitch", Vector2(SWITCH_X, 0.0), 14.0)
	_switch_sprite = Sprites.standing("props/power_switch_off", Vector2i(16, 24), C_INK)
	_switch_sprite.position = Vector2(0.0, -30.0)
	power_switch.add_child(_switch_sprite)
	_standing("props/poster_a", Vector2(172.0, -54.0), Vector2i(24, 32))
	_standing("props/plant", Vector2(232.0, 0.0), Vector2i(18, 30))


func _build_hall() -> void:
	# Two wooden rails for the figure display.
	for rail_y in DISPLAY_ROW_YS:
		var rail: ColorRect = ColorRect.new()
		rail.color = Color("#a9825a")
		rail.position = Vector2(DISPLAY_START_X - 20.0, rail_y)
		rail.size = Vector2(DISPLAY_STEP_X * (DISPLAY_PER_ROW - 1) + 40.0, 2.0)
		rail.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(rail)
		var shade: ColorRect = ColorRect.new()
		shade.color = C_INK
		shade.position = rail.position + Vector2(0.0, 2.0)
		shade.size = Vector2(rail.size.x, 1.0)
		shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(shade)
	for machine_id in MACHINE_XS:
		_build_machine(machine_id)
	_standing("props/shelf_a", Vector2(732.0, 0.0), Vector2i(44, 64))
	_standing("props/plant", Vector2(770.0, 0.0), Vector2i(18, 30))
	_standing("props/plant", Vector2(268.0, 0.0), Vector2i(18, 30))
	_standing("props/poster_b", Vector2(526.0, -18.0), Vector2i(24, 32))
	_standing("props/poster_c", Vector2(618.0, -18.0), Vector2i(24, 32))


func _build_machine(machine_id: String) -> void:
	var x: float = MACHINE_XS[machine_id]
	var index: int = MACHINE_XS.keys().find(machine_id)
	var kind: String = "gacha"
	if machine_id == "machine_005":
		kind = "claw"
	elif machine_id == "machine_006":
		kind = "plinko"
	var canvas: Vector2i = GACHA_SIZE if kind == "gacha" else BIG_SIZE
	var root: Node2D = Node2D.new()
	root.name = machine_id
	root.position = Vector2(x, 0.0)
	add_child(root)
	root.add_child(Sprites.standing("machines/%s" % machine_id, canvas, Color.from_hsv(index * 0.15, 0.5, 0.85)))
	var lit: Sprite2D = Sprites.standing("machines/%s_lit" % machine_id, Vector2i(1, 1), Color(1, 1, 1, 0))
	root.add_child(lit)
	_lit_overlays.append(lit)
	var machine: Dictionary = {"root": root, "x": x, "type": kind, "lit": lit, "robots": [], "busy": false, "held": false, "aux": null, "robot_rate": 0.0, "speed": 1.0}
	match kind:
		"claw":
			var rope: Line2D = Line2D.new()
			rope.width = 1.0
			rope.default_color = C_INK
			rope.points = PackedVector2Array([Vector2.ZERO, Vector2.ZERO])
			root.add_child(rope)
			var claw: Sprite2D = Sprite2D.new()
			claw.centered = false
			claw.offset = Vector2(-8.0, 0.0)
			claw.texture = Sprites.texture("machines/claw_open", Vector2i(16, 16), C_INK)
			claw.position = Vector2(CLAW_REST_X, CLAW_RAIL_Y)
			root.add_child(claw)
			machine["claw"] = claw
			machine["rope"] = rope
		"plinko":
			var lamp: Polygon2D = Polygon2D.new()
			lamp.polygon = PackedVector2Array([Vector2(-3, -4), Vector2(3, -4), Vector2(3, 3), Vector2(-3, 3)])
			lamp.color = Color(1.0, 0.95, 0.6, 0.7)
			lamp.visible = false
			root.add_child(lamp)
			var ball: Sprite2D = Sprite2D.new()
			ball.texture = Sprites.texture("machines/plinko_ball", Vector2i(6, 6), C_CREAM)
			ball.visible = false
			root.add_child(ball)
			machine["ball"] = ball
			machine["slot_lamp"] = lamp
		_:
			var knob: Sprite2D = Sprite2D.new()
			knob.texture = Sprites.texture("machines/gacha_knob", Vector2i(12, 12), C_CREAM)
			knob.position = GACHA_KNOB
			root.add_child(knob)
			machine["knob"] = knob
	var capsule: Sprite2D = Sprite2D.new()
	capsule.texture = Sprites.texture("machines/capsule_coral", Vector2i(10, 10), C_MUSTARD)
	capsule.visible = false
	root.add_child(capsule)
	machine["capsule"] = capsule
	# The price is a sticker on the floor in front of the machine.
	machine["price"] = _label("", Vector2(x, 6.0), 24, C_CREAM)
	for robot_index in range(MAX_ROBOT_SPRITES):
		var robot: AnimatedSprite2D = Sprites.animated(["robot_idle", "robot_work"], Vector2i(20, 24))
		robot.position = Vector2(x, ROBOT_Y) + ROBOT_OFFSETS[robot_index % ROBOT_OFFSETS.size()]
		robot.flip_h = ROBOT_FLIPS[robot_index % ROBOT_FLIPS.size()]
		robot.z_index = 6
		robot.visible = false
		add_child(robot)
		machine["robots"].append(robot)
	var body: Node2D = _interactable("Use_%s" % machine_id, Vector2(x, 0.0), canvas.x / 2.0 + 2.0)
	machine["body"] = body
	machines[machine_id] = machine


func _process(delta: float) -> void:
	_time += delta
	for machine_id in machines:
		var machine: Dictionary = machines[machine_id]
		if machine["type"] == "claw":
			# The rope follows the claw, and a held capsule swings with it.
			var claw: Sprite2D = machine["claw"]
			machine["rope"].points = PackedVector2Array([Vector2(claw.position.x, CLAW_RAIL_Y - 2.0), claw.position])
			if machine["held"]:
				machine["capsule"].position = (claw.position + CLAW_HOLD.rotated(claw.rotation)).round()
		elif machine["type"] == "gacha" and not machine["busy"]:
			# Robots keep the knob turning between the player's own spins.
			var rate: float = machine["robot_rate"]
			var knob: Sprite2D = machine["knob"]
			if rate > 0.0 and _power_on:
				knob.rotation = fposmod(knob.rotation + delta * TAU * minf(rate, ROBOT_KNOB_MAX_RATE), TAU)
			elif knob.rotation != 0.0:
				knob.rotation = 0.0
	_animate_coins()


## Floor coins bob by a pixel, out of step, and one of them twinkles now and
## then so they can be found in the dark.
func _animate_coins() -> void:
	var waiting: Array = []
	for index in range(coins.size()):
		var coin: Node2D = coins[index]
		if not coin.visible:
			continue
		waiting.append(coin)
		var spin: Node2D = coin.get_meta("spin")
		spin.position.y = roundf(sin(_time * COIN_BOB_SPEED + index * 1.9))
	if _time >= _next_twinkle:
		_next_twinkle = _time + COIN_TWINKLE_EVERY * _rng.randf_range(0.7, 1.3)
		if not waiting.is_empty():
			var lucky: Node2D = waiting[_rng.randi_range(0, waiting.size() - 1)]
			Sprites.burst(self, "sparkle", lucky.position + Vector2(_rng.randf_range(-3.0, 3.0), -8.0), Vector2i(16, 16))


func _build_reception() -> void:
	_standing("props/sign_gacha", Vector2(868.0, -112.0), Vector2i(96, 20))
	_door_glow = Polygon2D.new()
	_door_glow.polygon = PackedVector2Array([Vector2(-20, -66), Vector2(20, -66), Vector2(44, FLOOR_DEPTH), Vector2(-44, FLOOR_DEPTH)])
	# Bright at the doorway, fading out across the floor.
	_door_glow.color = Color.WHITE
	_door_glow.vertex_colors = PackedColorArray([Color(1.0, 0.97, 0.85, 1.0), Color(1.0, 0.97, 0.85, 1.0), Color(1.0, 0.95, 0.75, 0.15), Color(1.0, 0.95, 0.75, 0.15)])
	_door_glow.position = Vector2(DOOR_X, 0.0)
	_door_glow.z_index = 8
	_door_glow.visible = false
	door = _interactable("FrontDoor", Vector2(DOOR_X, 0.0), 18.0)
	_door_sprite = Sprites.standing("props/door_closed", Vector2i(44, 68), Color("#4f9ea3"))
	door.add_child(_door_sprite)
	add_child(_door_glow)
	_standing("props/counter", Vector2(COUNTER_X, 0.0), Vector2i(76, 30))
	reception = _interactable("Reception", Vector2(COUNTER_X, 0.0), 26.0)
	_computer = Sprites.standing("props/computer_off", Vector2i(24, 22), C_INK)
	_computer.position = Vector2(-8.0, -30.0)
	reception.add_child(_computer)
	if not Sprites.animation_info("screen_glow").is_empty():
		_screen_glow = Sprites.animated(["screen_glow"], Vector2i(24, 22))
		_screen_glow.position = _computer.position
		_screen_glow.play("screen_glow")
		reception.add_child(_screen_glow)
	_standing("props/key", Vector2(COUNTER_X + 24.0, -30.0), Vector2i(12, 8))


func _build_staff_room() -> void:
	_standing("props/locker", Vector2(976.0, 0.0), Vector2i(22, 56))
	_standing("props/shelf_b", Vector2(1080.0, 0.0), Vector2i(44, 64))
	sofa = _interactable("Sofa", Vector2(SOFA_X, 0.0), 24.0)
	sofa.add_child(Sprites.standing("props/sofa", Vector2i(60, 30), Color("#ef7a6d")))
	_standing("props/table", Vector2(1000.0, 14.0), Vector2i(34, 22), 6)
	_standing("props/poster_b", Vector2(SOFA_X, -52.0), Vector2i(24, 32))


func _build_lamps() -> void:
	for x in LAMP_XS:
		var glow: Polygon2D = Polygon2D.new()
		glow.polygon = PackedVector2Array([Vector2(-12, 10), Vector2(12, 10), Vector2(46, -LAMP_Y), Vector2(-46, -LAMP_Y)])
		# A soft cone: brightest under the tube, gone at the floor.
		var bright: Color = Color(1.0, 0.95, 0.7, LAMP_GLOW_TOP)
		var faded: Color = Color(1.0, 0.95, 0.7, 0.0)
		glow.color = Color.WHITE
		glow.vertex_colors = PackedColorArray([bright, bright, faded, faded])
		glow.position = Vector2(x, LAMP_Y)
		glow.z_index = 7
		add_child(glow)
		var halo: Polygon2D = Polygon2D.new()
		halo.polygon = PackedVector2Array([Vector2(-19, 2), Vector2(19, 2), Vector2(23, 16), Vector2(-23, 16)])
		halo.color = Color.WHITE
		halo.vertex_colors = PackedColorArray([bright, bright, faded, faded])
		glow.add_child(halo)
		var sprite: Sprite2D = Sprite2D.new()
		sprite.centered = false
		sprite.offset = Vector2(-16.0, 0.0)
		sprite.position = Vector2(x, LAMP_Y)
		add_child(sprite)
		var flicker: AnimatedSprite2D = null
		if not Sprites.animation_info("lamp_flicker").is_empty():
			flicker = AnimatedSprite2D.new()
			flicker.sprite_frames = Sprites.frames(["lamp_flicker"], Vector2i(32, 12))
			flicker.centered = false
			flicker.offset = Vector2(-16.0, 0.0)
			flicker.position = Vector2(x, LAMP_Y)
			flicker.visible = false
			add_child(flicker)
		var lamp: Dictionary = {"x": x, "sprite": sprite, "glow": glow, "flicker": flicker}
		if flicker != null:
			flicker.frame_changed.connect(_on_flicker_frame.bind(lamp))
			flicker.animation_finished.connect(_on_flicker_finished.bind(lamp))
		_lamps.append(lamp)


# --- Helpers ------------------------------------------------------------------

func _standing(path: String, at: Vector2, fallback_size: Vector2i, z: int = 0) -> Sprite2D:
	var sprite: Sprite2D = Sprites.standing(path, fallback_size)
	sprite.position = at
	sprite.z_index = z
	add_child(sprite)
	return sprite


func _interactable(node_name: String, at: Vector2, reach: float) -> Node2D:
	var node: Node2D = Interactable.new()
	node.name = node_name
	node.position = at
	node.reach = reach
	add_child(node)
	interactables.append(node)
	return node


## Text is drawn at screen resolution and scaled down into the pixel world.
func _label(text: String, at: Vector2, font_size: int, color: Color) -> Label:
	var label: Label = Label.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.size = Vector2(320.0, 40.0)
	label.scale = Vector2(0.25, 0.25)
	label.position = at - Vector2(40.0, 5.0)
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", C_INK)
	label.add_theme_constant_override("outline_size", 8)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	add_child(label)
	return label
