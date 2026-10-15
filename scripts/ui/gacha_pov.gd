extends Node2D
## A capsule machine seen from right in front of it, almost in first person,
## all of it pixel art on one 320 x 180 grid (shown at four screen pixels per
## pixel by the viewport this node lives in): the dome fills the background,
## and below it are the coin slot, the crank and the mouth the prize comes out
## of. On the left, the upgrades sold at this machine, as a detective's case
## file in dark green; on the right, the timing wheel, as a pocket watch.
##
## Presentation only: it draws what `machine_scene.gd` (its `scene`) holds.
## The pictures come from `tools/pixel/build_pov.py`.

const SIZE: Vector2i = Vector2i(320, 180)
const ART: String = "res://assets/sprites/pov/"
## Order of the letters in the font picture; each is 5 x 7 in a 6-wide cell.
const LETTERS: String = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?:+-%/[]'=*><"
const LETTER_STEP: int = 6
const LINE: int = 9

const INK: Color = Color("#0e0d0c")
const SHADE: Color = Color("#2a2722")
const CREAM: Color = Color("#e3d9c6")
const BONE: Color = Color("#c9bb9f")
const STONE: Color = Color("#9a8766")
const BRASS: Color = Color("#b09448")
const BRASS_LIGHT: Color = Color("#d0b870")
const BRASS_DARK: Color = Color("#8a7038")
const RUST: Color = Color("#8a4e30")
## The file's green: field, darker band, lighter line.
const GREEN: Color = Color("#4a5546")
const GREEN_DARK: Color = Color("#4a4a30")
const GREEN_LIGHT: Color = Color("#74806c")
## Text of what cannot be bought yet, and the rubber stamp.
const DIM: Color = Color("#979a72")
const STAMP: Color = Color("#b0704a")

# Where things are on the machine (as in build_pov.py).
const EYES_AT: Vector2 = Vector2(129.0, 14.0)
const EYES_FRAME: Vector2 = Vector2(62.0, 40.0)
const SLOT: Vector2 = Vector2(160.0, 99.0)
const CRANK: Vector2 = Vector2(160.0, 128.0)
const CRANK_FRAME: float = 46.0
const MOUTH: Rect2 = Rect2(132.0, 150.0, 57.0, 30.0)
const CAPSULE_FRAME: float = 22.0
## The two panels, and the rows of the file.
const FILE: Rect2 = Rect2(4.0, 12.0, 98.0, 156.0)
const WATCH: Rect2 = Rect2(218.0, 12.0, 98.0, 156.0)
const ROW_TOP: float = 34.0
const ROW_HEIGHT: float = 34.0
const DIAL: Vector2 = Vector2(267.0, 78.0)
const DIAL_RADIUS: float = 30.0

## The machine scene whose state is drawn.
var scene: Control

var _dome: Texture2D
var _bodies: Dictionary = {}
var _eyes: Texture2D
var _crank: Texture2D
var _capsule: Texture2D
var _coin: Texture2D
var _font: Texture2D
var _time: float = 0.0


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_dome = load(ART + "dome.png")
	_eyes = load(ART + "eyes.png")
	_crank = load(ART + "crank.png")
	_capsule = load(ART + "capsule.png")
	_coin = load(ART + "coin.png")
	_font = load(ART + "font.png")


func _process(delta: float) -> void:
	_time += delta
	queue_redraw()


## Index of the upgrade row under a point of the 320 x 180 picture, or -1.
func row_at(point: Vector2) -> int:
	if not Rect2(FILE.position.x, FILE.position.y + ROW_TOP, FILE.size.x, ROW_HEIGHT * 3.0).has_point(point):
		return -1
	return int((point.y - FILE.position.y - ROW_TOP) / ROW_HEIGHT)


func _draw() -> void:
	if scene == null or scene.machine_id == "":
		return
	var cranking: bool = scene.is_cranking()
	# The whole machine rattles by a pixel while the crank turns and hops on a
	# perfect stop.
	var rattle: Vector2 = Vector2(roundf(sin(_time * 38.0)), 0.0) if cranking else Vector2.ZERO
	if scene.is_perfect() and scene.grade_age() < 0.3:
		rattle.y = -roundf(sin(scene.grade_age() / 0.3 * PI) * 3.0)
	# Stretch on the way up, squash on landing, at constant volume; the view is
	# a 320 x 180 grid, so any scale lands on whole pixels.
	var shape: Vector2 = Vector2.ONE
	var age: float = scene.grade_age()
	if scene.is_perfect() and age < 0.45:
		var amount: float = -0.05 * sin(age / 0.3 * PI) if age < 0.3 else 0.06 * sin((age - 0.3) / 0.15 * PI)
		shape = Vector2(1.0 / (1.0 - amount), 1.0 - amount)
	draw_set_transform_matrix(Transform2D(0.0, shape, 0.0, Vector2(160.0, 180.0) * (Vector2.ONE - shape)))
	draw_texture(_dome, rattle * 2.0)
	# A blink every few seconds: half shut, shut, half shut.
	var blink: float = fmod(_time, 4.3)
	var eye_frame: int = 0
	if blink > 4.0:
		eye_frame = 2 if blink > 4.1 and blink < 4.2 else 1
	draw_texture_rect_region(_eyes, Rect2(EYES_AT + rattle, EYES_FRAME), Rect2(eye_frame * EYES_FRAME.x, 0.0, EYES_FRAME.x, EYES_FRAME.y))
	draw_texture(_body(scene.machine_id), rattle)
	var turn: int = posmod(roundi(scene.crank_angle() / (PI / 8.0)), 8)
	draw_texture_rect_region(_crank, Rect2(CRANK + rattle - Vector2(CRANK_FRAME, CRANK_FRAME) / 2.0, Vector2(CRANK_FRAME, CRANK_FRAME)), Rect2(turn * CRANK_FRAME, 0.0, CRANK_FRAME, CRANK_FRAME))
	draw_set_transform_matrix(Transform2D.IDENTITY)
	_capsule_in_mouth(rattle)
	var flight: float = scene.coin_flight()
	if flight < 1.0:
		var from: Vector2 = Vector2(160.0, 176.0)
		var at: Vector2 = from.lerp(SLOT, flight) + Vector2(0.0, -sin(flight * PI) * 16.0)
		draw_texture(_coin, (at - Vector2(4.0, 4.0)).round())
	_file()
	_watch()
	_footer()


func _body(machine_id: String) -> Texture2D:
	if not _bodies.has(machine_id):
		var path: String = "%sbody_%s.png" % [ART, machine_id]
		_bodies[machine_id] = load(path) if ResourceLoader.exists(path) else load(ART + "body_machine_001.png")
	return _bodies[machine_id]


## The capsule drops into the tray from inside the mouth: only the part below
## the mouth's upper edge shows.
func _capsule_in_mouth(rattle: Vector2) -> void:
	if not scene.capsule_showing():
		return
	var at: Vector2 = (scene.capsule_point() / 4.0).round() + rattle
	var top: float = at.y - CAPSULE_FRAME / 2.0
	var hidden: float = clampf(MOUTH.position.y - top, 0.0, CAPSULE_FRAME)
	if hidden >= CAPSULE_FRAME:
		return
	var frame: int = scene.capsule_index() % 3
	draw_texture_rect_region(_capsule, Rect2(at.x - CAPSULE_FRAME / 2.0, top + hidden, CAPSULE_FRAME, CAPSULE_FRAME - hidden),
		Rect2(frame * CAPSULE_FRAME, hidden, CAPSULE_FRAME, CAPSULE_FRAME - hidden))


# --- The case file: this machine's upgrades ---------------------------------------

func _file() -> void:
	_folder(FILE, "CASE FILE", "NO.%s" % scene.machine_id.right(3))
	# A magnifying glass by the title.
	var glass: Vector2 = FILE.position + Vector2(10.0, 12.0)
	draw_arc(glass, 4.0, 0.0, TAU, 12, BRASS, 1.0)
	draw_line(glass + Vector2(3.0, 3.0), glass + Vector2(7.0, 7.0), BRASS, 2.0)
	var views: Array = scene.upgrade_views()
	var playing: bool = scene.is_playing()
	for index in range(views.size()):
		var view: Dictionary = views[index]
		var top: float = FILE.position.y + ROW_TOP + index * ROW_HEIGHT
		var left: float = FILE.position.x + 6.0
		var maxed: bool = view["level"] >= view["max_level"]
		var can_buy: bool = bool(view["can_buy"]) and not playing
		var ink: Color = CREAM if can_buy or maxed else DIM
		if can_buy:
			draw_rect(Rect2(FILE.position.x + 3.0, top - 2.0, FILE.size.x - 6.0, ROW_HEIGHT - 3.0), GREEN_DARK)
			draw_rect(Rect2(FILE.position.x + 3.0, top - 2.0, 1.0, ROW_HEIGHT - 3.0), BRASS)
		_write(Vector2(left, top), "%s %s" % [scene.upgrade_key(index), str(view["display_name_en"]).to_upper()], ink)
		# One pip per level, filled as they are bought.
		for pip in range(int(view["max_level"])):
			var box: Rect2 = Rect2(left + pip * 7.0, top + LINE + 1.0, 5.0, 5.0)
			draw_rect(box, BRASS if pip < int(view["level"]) else GREEN_DARK)
			draw_rect(box, INK, false, 1.0)
		var cost: String = "MAX" if maxed else "%sC" % scene.short_number(view["cost"])
		_write(Vector2(FILE.end.x - 6.0 - cost.length() * LETTER_STEP, top + LINE), cost, BRASS_LIGHT if can_buy else DIM)
		_write(Vector2(left, top + LINE * 2.0), _effect(view), BONE if can_buy or maxed else DIM)
		_dots(Vector2(FILE.position.x + 6.0, top + ROW_HEIGHT - 4.0), FILE.size.x - 12.0)
	# A rubber stamp at the foot of the page: what is bought here goes at dawn.
	var stamp: Rect2 = Rect2(FILE.position.x + 9.0, FILE.end.y - 17.0, FILE.size.x - 18.0, 12.0)
	draw_rect(stamp, STAMP, false, 1.0)
	_write_centred(stamp.position.y + 3.0, stamp, "LOST ON SLEEP", STAMP)


## What one level of an upgrade gives, short enough for the page.
func _effect(view: Dictionary) -> String:
	return str(view["effect_en"]).to_upper().replace("SWEET SPOT", "MARK").replace("WHEEL SPEED", "SPEED").replace(" HERE", "")


# --- The pocket watch: the timing wheel ---------------------------------------------

func _watch() -> void:
	_folder(WATCH, "STEADY HAND", "")
	var aiming: bool = scene.is_aiming()
	var graded: bool = scene.grade_text() != ""
	# The watch: bow and crown on top, a brass case, a pale face with ticks.
	draw_arc(DIAL + Vector2(0.0, -DIAL_RADIUS - 8.0), 4.0, 0.0, TAU, 12, BRASS, 1.0)
	draw_rect(Rect2(DIAL.x - 3.0, DIAL.y - DIAL_RADIUS - 5.0, 6.0, 5.0), BRASS_DARK)
	draw_circle(DIAL, DIAL_RADIUS + 3.0, INK)
	draw_circle(DIAL, DIAL_RADIUS + 2.0, BRASS)
	draw_arc(DIAL, DIAL_RADIUS + 1.0, PI * 0.9, PI * 1.6, 16, BRASS_LIGHT, 1.0)
	draw_circle(DIAL, DIAL_RADIUS - 1.0, INK)
	draw_circle(DIAL, DIAL_RADIUS - 2.0, BONE if aiming or graded else STONE)
	if aiming or graded:
		# Angles on the dial run clockwise from twelve.
		var half: float = scene.mark_half()
		for band in [[1.0, GREEN_LIGHT], [scene.GRADES[1][1], BRASS], [scene.GRADES[0][1], RUST]]:
			var reach: float = half * band[0]
			draw_arc(DIAL, DIAL_RADIUS - 8.0, scene.mark_angle() - reach - PI / 2.0, scene.mark_angle() + reach - PI / 2.0, 20, band[1], 11.0)
	for tick in range(12):
		var out: Vector2 = Vector2(sin(tick * TAU / 12.0), -cos(tick * TAU / 12.0))
		draw_line(DIAL + out * (DIAL_RADIUS - 5.0), DIAL + out * (DIAL_RADIUS - 2.0), INK, 1.0)
	if aiming or graded:
		var hand: Vector2 = Vector2(sin(scene.needle_angle()), -cos(scene.needle_angle()))
		draw_line(DIAL - hand * 5.0, DIAL + hand * (DIAL_RADIUS - 4.0), INK, 2.0)
	draw_circle(DIAL, 2.5, INK)
	draw_circle(DIAL, 1.5, BRASS_LIGHT)
	var line: float = DIAL.y + DIAL_RADIUS + 10.0
	if graded:
		var tint: Color = BRASS_LIGHT if scene.is_perfect() else (CREAM if scene.grade_luck() > 0.0 else GREEN_LIGHT)
		# The grade drops in from above and settles.
		var drop: float = roundf(maxf(0.0, 1.0 - scene.grade_age() / 0.18) * -6.0)
		_write_centred(line + drop, WATCH, scene.grade_text(), tint)
		_write_centred(line + LINE + 2.0, WATCH, ("+%d%% LUCK" % int(scene.grade_luck())) if scene.grade_luck() > 0.0 else "NO LUCK", BONE)
	elif aiming:
		_write_centred(line, WATCH, "ON THE MARK!", CREAM)
		_write_centred(line + LINE + 2.0, WATCH, "CLOSER=RARER", BONE)
	else:
		for index in range(scene.GRADES.size()):
			var grade: Array = scene.GRADES[index]
			_write_centred(line + index * LINE - 4.0, WATCH, "%s +%d%%" % [str(grade[0]).trim_suffix("!"), int(grade[2])], [STAMP, BRASS_LIGHT, BONE][index])
	var action: Rect2 = Rect2(WATCH.position.x + 9.0, WATCH.end.y - 17.0, WATCH.size.x - 18.0, 12.0)
	draw_rect(action, GREEN_DARK)
	draw_rect(action, BRASS, false, 1.0)
	_write_centred(action.position.y + 3.0, action, scene.action_text(), CREAM)


# --- Shared pieces --------------------------------------------------------------------

## A dark green folder page: ink edge, a fine brass rule with corner marks, a
## paper clip, and a typed heading.
func _folder(area: Rect2, title: String, number: String) -> void:
	draw_rect(Rect2(area.position + Vector2(2.0, 2.0), area.size), Color(INK, 0.5))
	draw_rect(area, INK)
	draw_rect(area.grow(-1.0), GREEN)
	draw_rect(Rect2(area.position.x + 1.0, area.position.y + 1.0, area.size.x - 2.0, 22.0), GREEN_DARK)
	draw_rect(area.grow(-3.0), BRASS_DARK, false, 1.0)
	for corner in [area.position + Vector2(3.0, 3.0), Vector2(area.end.x - 6.0, area.position.y + 3.0),
			Vector2(area.position.x + 3.0, area.end.y - 6.0), area.end - Vector2(6.0, 6.0)]:
		draw_rect(Rect2(corner, Vector2(3.0, 3.0)), BRASS)
	# The paper clip on the top edge.
	var clip: Vector2 = Vector2(area.end.x - 16.0, area.position.y - 3.0)
	draw_rect(Rect2(clip, Vector2(5.0, 12.0)), STONE, false, 1.0)
	draw_rect(Rect2(clip + Vector2(2.0, 3.0), Vector2(1.0, 7.0)), STONE)
	var left: float = area.position.x + (20.0 if number != "" else 0.0)
	if number != "":
		_write(Vector2(left, area.position.y + 6.0), title, CREAM)
		_write(Vector2(left, area.position.y + 6.0 + LINE - 1.0), number, BRASS_LIGHT)
	else:
		_write_centred(area.position.y + 9.0, area, title, CREAM)
	_dots(Vector2(area.position.x + 6.0, area.position.y + 25.0), area.size.x - 12.0)


## The purse, the machine's name and whatever the scene has to say, along the
## bottom and the top of the picture.
func _footer() -> void:
	var purse: String = "%s COINS" % scene.short_number(scene.coins())
	_plate(Rect2(4.0, 170.0, purse.length() * LETTER_STEP + 16.0, 10.0))
	draw_texture(_coin, Vector2(6.0, 170.0))
	_write(Vector2(17.0, 171.0), purse, BRASS_LIGHT)
	var price: String = "%sC" % scene.short_number(scene.price())
	_write(Vector2(SLOT.x + 19.0, SLOT.y - 3.0), price, CREAM)
	var keys: String = "Q/R MACHINE  ESC HALL"
	_write(Vector2(SIZE.x - 4.0 - keys.length() * LETTER_STEP, 171.0), keys, Color(BONE, 0.8))
	var said: String = scene.message_text().to_upper()
	if said != "":
		var width: float = said.length() * LETTER_STEP + 8.0
		_plate(Rect2(roundf(160.0 - width / 2.0), 2.0, width, 11.0))
		_write(Vector2(roundf(160.0 - width / 2.0) + 4.0, 4.0), said, CREAM)


func _plate(area: Rect2) -> void:
	draw_rect(area, INK)
	draw_rect(area.grow(-1.0), SHADE)


func _dots(from: Vector2, width: float) -> void:
	var x: float = 0.0
	while x < width:
		draw_rect(Rect2(from + Vector2(x, 0.0), Vector2(1.0, 1.0)), GREEN_LIGHT)
		x += 3.0


## Text in the pixel alphabet, upper case only; what it has no letter for is
## left as a gap.
func _write(at: Vector2, text: String, color: Color) -> void:
	var x: float = roundf(at.x)
	for letter in text.to_upper():
		var index: int = LETTERS.find(letter)
		if index > 0:
			draw_texture_rect_region(_font, Rect2(x, roundf(at.y), 5.0, 7.0), Rect2(index * LETTER_STEP, 0.0, 5.0, 7.0), color)
		x += LETTER_STEP


func _write_centred(y: float, area: Rect2, text: String, color: Color) -> void:
	_write(Vector2(area.position.x + roundf((area.size.x - text.length() * LETTER_STEP + 1.0) / 2.0), y), text, color)
