extends Node2D
## The store's ambient life: small looping animations placed around the rooms
## from a table, plus a few that small code moves about (a moth at a lamp, a
## mouse along the wall, a wind-up toy on a shelf, a stray capsule). Purely
## decorative: nothing here is usable or touches game state. An animation that
## is missing from the manifests is simply left out.

const Sprites = preload("res://scripts/world/sprite_lib.gd")
const Swing = preload("res://scripts/world/swing.gd")

## Placement table. Each row:
##   anim    animation name in assets/sprites/ambient/anims.json
##   room    where it is, for the reader (positions are world pixels)
##   at      anchor point; its meaning depends on `layer`
##   layer   "wall"     bottom centre on the back wall, behind everything standing
##           "floor"    bottom centre on the floor, depth-sorted with the player
##           "hanging"  top centre, hanging in front of the wall
##           "on"       bottom centre relative to the furniture named in `on`
##                      (store.furniture), drawn just in front of it
##   powered true: runs only while the power is on (electric things)
##   size    contract frame size (only documents the row)
##   solid   floor only: footprint depth in pixels; the player walks around it
##   prop    floor only: static sprite shown instead while the animation is missing
##   hide_off powered only: hidden, not just frozen, while the power is off
##   rigid   hanging only: fixed to the ceiling, so it does not swing when the
##           player runs past (everything else that hangs does)
const PLACEMENT: Array = [
	{"anim": "amb_tap_drip", "room": "bath", "on": "sink", "at": Vector2(0.0, -8.0), "layer": "on", "powered": false, "size": Vector2i(10, 26)},
	{"anim": "amb_lantern", "room": "hall", "at": Vector2(252.0, -104.0), "layer": "hanging", "powered": false, "size": Vector2i(20, 34)},
	{"anim": "amb_plant_sway", "room": "reception", "at": Vector2(866.0, 14.0), "layer": "floor", "powered": false, "size": Vector2i(24, 40), "solid": 6.0, "prop": "props/plant"},
	{"anim": "amb_ceiling_fan", "room": "reception", "at": Vector2(880.0, -112.0), "layer": "hanging", "powered": true, "size": Vector2i(56, 24), "rigid": true},
	{"anim": "amb_exit_sign", "room": "reception", "on": "door", "at": Vector2(0.0, -91.0), "layer": "on", "powered": true, "size": Vector2i(30, 14)},
	{"anim": "amb_maneki_neko", "room": "reception", "on": "counter", "at": Vector2(15.0, -38.0), "layer": "on", "powered": false, "size": Vector2i(26, 32)},
	{"anim": "amb_string_lights", "room": "staff", "at": Vector2(1055.0, -104.0), "layer": "hanging", "powered": true, "size": Vector2i(96, 14), "rigid": true},
	{"anim": "amb_wall_clock", "room": "staff", "at": Vector2(1116.0, -50.0), "layer": "wall", "powered": false, "size": Vector2i(24, 36)},
	{"anim": "amb_fish_bowl", "room": "staff", "on": "table", "at": Vector2(-9.0, -20.0), "layer": "on", "powered": false, "size": Vector2i(26, 26)},
	{"anim": "amb_mug_steam", "room": "staff", "on": "table", "at": Vector2(12.0, -20.0), "layer": "on", "powered": false, "size": Vector2i(14, 24)},
]

## An electric thing without power is frozen on its first frame and dimmed.
const UNPOWERED: Color = Color(0.5, 0.5, 0.56)
## A footprint is this much narrower than the picture.
const FOOTPRINT_INSET: float = 6.0

# --- Moths: one circles each of these lamps (index into the store's lamps) -----
const MOTH_LAMPS: Array = [2]
const MOTH_SIZE: Vector2i = Vector2i(14, 12)
const MOTH_ORBIT: Vector2 = Vector2(15.0, 7.0)
const MOTH_SPEED: float = 2.3
## The orbit breathes in and out so the path never repeats exactly.
const MOTH_WOBBLE_SPEED: float = 0.7
const MOTH_WOBBLE: float = 0.35

# --- Mouse: now and then it dashes along the foot of the wall -----------------
const MOUSE_SIZE: Vector2i = Vector2i(22, 14)
const MOUSE_Y: float = 5.0
const MOUSE_SPEED: float = 95.0
const MOUSE_WAIT: Vector2 = Vector2(7.0, 16.0)
const MOUSE_FIRST_WAIT: float = 4.0
## It starts and ends this far to each side of the view centre: just off screen.
const MOUSE_SPAN: float = 240.0
const MOUSE_MARGIN: float = 14.0

# --- Wind-up toy: paces a little wall shelf in the bathroom ---------------------
const WINDUP_SIZE: Vector2i = Vector2i(18, 18)
const WINDUP_SHELF_AT: Vector2 = Vector2(96.0, -30.0)
const WINDUP_SHELF_SEGMENTS: int = 2
const WINDUP_SHELF_SIZE: Vector2i = Vector2i(34, 12)
## The toy's feet stand this far below the top edge of the shelf picture.
const WINDUP_SEAT: float = 7.0
const WINDUP_SPEED: float = 9.0
const WINDUP_MARGIN: float = 9.0
const WINDUP_TURN_PAUSE: float = 0.6
## The right end of the shelf is kept for a rubber duck: the toy turns before it.
const WINDUP_KEEP_CLEAR: float = 22.0

# --- Stray capsule: rolls a bit across the hall floor, rests, rolls back -------
const STRAY_SIZE: Vector2i = Vector2i(12, 12)
const STRAY_RANGE: Vector2 = Vector2(330.0, 770.0)
## Like the train below, it keeps clear of the front strip the HUD sits on.
const STRAY_Y: float = 96.0
const STRAY_SPEED: float = 26.0
const STRAY_ROLL: Vector2 = Vector2(30.0, 90.0)
const STRAY_REST: Vector2 = Vector2(2.5, 7.0)

# --- Toy train: runs up and down the near edge of the gallery floor ------------
const TRAIN_SIZE: Vector2i = Vector2i(36, 18)
const TRAIN_RANGE: Vector2 = Vector2(850.0, 1820.0)
const TRAIN_Y: float = 100.0
const TRAIN_SPEED: float = 34.0
const TRAIN_STOP: float = 1.5

## A hanging thing the player runs past gets this kick, in radians per second.
const BREEZE_KICK: float = 1.1

## Rows of PLACEMENT that made it into the scene: {anim, layer, powered,
## hide_off, sprite, swing}; `swing` is null for whatever cannot swing.
var placed: Array = []

var _store: Node2D
var _power_on: bool = false
var _time: float = 0.0
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()
var _moths: Array = []
var _mouse: AnimatedSprite2D
var _mouse_wait: float = MOUSE_FIRST_WAIT
var _mouse_target: float = 0.0
var _windup: AnimatedSprite2D
var _windup_range: Vector2 = Vector2.ZERO
var _windup_direction: float = 1.0
var _windup_pause: float = 0.0
var _train: AnimatedSprite2D
var _train_shadow: Polygon2D
var _train_direction: float = 1.0
var _train_stop: float = 0.0
var _stray: AnimatedSprite2D
var _stray_shadow: Polygon2D
var _stray_target: float = 0.0
var _stray_rest: float = 1.0


## Builds everything inside `store` (the store adds this node to itself first).
func setup(store: Node2D) -> void:
	_store = store
	_rng.randomize()
	for row in PLACEMENT:
		_place(row)
	_build_moths()
	_build_mouse()


## Electric things run only with the power on; living things never stop.
func set_power(is_on: bool) -> void:
	_power_on = is_on
	for item in placed:
		if not item["powered"]:
			continue
		var sprite: AnimatedSprite2D = item["sprite"]
		if is_on:
			sprite.modulate = Color.WHITE
			sprite.play(item["anim"])
		else:
			sprite.stop()
			sprite.frame = 0
			sprite.modulate = UNPOWERED
		sprite.visible = is_on or not item["hide_off"]


func _place(row: Dictionary) -> void:
	var anim_name: String = row["anim"]
	var layer: String = row["layer"]
	var at: Vector2 = row["at"]
	var sort_y: float = at.y
	if layer == "on":
		if not _store.furniture.has(row["on"]):
			return
		var support: Vector2 = _store.furniture[row["on"]]
		at += support
		sort_y = support.y
	var size: Vector2i = row["size"]
	if not Sprites.has_animation(anim_name):
		if layer == "floor" and row.has("prop"):
			# The still prop keeps the spot until the animation is drawn.
			var still: Sprite2D = Sprites.standing(row["prop"], size, Color("#2e9e4f"))
			still.position = at
			still.z_index = _store.floor_z(at.y)
			add_child(still)
			_ground(row, at, size)
		return
	var sprite: AnimatedSprite2D = Sprites.animated([anim_name], size)
	if layer == "hanging":
		# Offsets are in sprite pixels: half of the frame actually drawn.
		sprite.offset = Vector2(-floorf(sprite.sprite_frames.get_frame_texture(anim_name, 0).get_width() / 2.0), 0.0)
	sprite.position = at
	match layer:
		"wall":
			sprite.z_index = _store.Z_WALL
		"hanging":
			sprite.z_index = _store.Z_HANGING
		"on":
			# Wall furniture (y <= 0) carries its things on the wall layer.
			sprite.z_index = _store.floor_z(sort_y) + 1 if sort_y > 0.0 else _store.Z_WALL + 1
		_:
			sprite.z_index = _store.floor_z(at.y)
			_ground(row, at, size)
	add_child(sprite)
	sprite.play(anim_name)
	# Copies of one animation do not move in step.
	sprite.frame = placed.size() % maxi(sprite.sprite_frames.get_frame_count(anim_name), 1)
	var swing: RefCounted = Swing.new() if layer == "hanging" and not bool(row.get("rigid", false)) else null
	placed.append({"anim": anim_name, "layer": layer, "powered": bool(row["powered"]), "hide_off": bool(row.get("hide_off", false)), "sprite": sprite, "swing": swing})


## Shadow and solid footprint of a free-standing thing.
func _ground(row: Dictionary, at: Vector2, size: Vector2i) -> void:
	_store._shadow(at + Vector2(0.0, -1.0), Vector2(size.x / 2.0 + 1.0, 3.5))
	if row.has("solid"):
		_store._solid(at, size.x - FOOTPRINT_INSET, float(row["solid"]))


func _build_moths() -> void:
	if not Sprites.has_animation("amb_moth"):
		return
	var lamps: Array = _store.lamp_points()
	for index in range(MOTH_LAMPS.size()):
		var lamp_index: int = MOTH_LAMPS[index]
		if lamp_index >= lamps.size():
			continue
		var moth: AnimatedSprite2D = _mover("amb_moth", MOTH_SIZE)
		moth.centered = true
		moth.offset = Vector2.ZERO
		moth.z_index = _store.Z_HANGING + 1
		moth.play("amb_moth")
		_moths.append({"sprite": moth, "centre": lamps[lamp_index], "phase": index * 2.1})


func _build_mouse() -> void:
	if not Sprites.has_animation("amb_mouse_run"):
		return
	_mouse = _mover("amb_mouse_run", MOUSE_SIZE)
	_mouse.z_index = _store.floor_z(MOUSE_Y)
	_mouse.visible = false


## The little wall shelf in the bathroom; it is furniture other things stand on.
func _build_bath_shelf() -> void:
	var shelf_size: Vector2 = Vector2(WINDUP_SHELF_SIZE.x * WINDUP_SHELF_SEGMENTS, WINDUP_SHELF_SIZE.y)
	var shelf: TextureRect = Sprites.tiled("props/gallery_shelf", Rect2(WINDUP_SHELF_AT, shelf_size), WINDUP_SHELF_SIZE, Color("#8a5a3a"))
	shelf.z_index = _store.Z_WALL
	add_child(shelf)
	_store.furniture["bath_shelf"] = WINDUP_SHELF_AT + Vector2(shelf_size.x / 2.0, WINDUP_SEAT)
	_windup_range = Vector2(WINDUP_SHELF_AT.x + WINDUP_MARGIN, WINDUP_SHELF_AT.x + shelf_size.x - WINDUP_MARGIN - WINDUP_KEEP_CLEAR)


func _build_windup() -> void:
	if not Sprites.has_animation("amb_windup_toy"):
		return
	_windup = _mover("amb_windup_toy", WINDUP_SIZE)
	_windup.position = Vector2(_windup_range.x, WINDUP_SHELF_AT.y + WINDUP_SEAT)
	_windup.z_index = _store.Z_WALL + 1
	_windup.play("amb_windup_toy")


func _build_stray() -> void:
	if not Sprites.has_animation("amb_capsule_roll"):
		return
	_stray = _mover("amb_capsule_roll", STRAY_SIZE)
	_stray.position = Vector2(_rng.randf_range(STRAY_RANGE.x, STRAY_RANGE.y), STRAY_Y)
	_stray.z_index = _store.floor_z(STRAY_Y)
	_stray_target = _stray.position.x
	_stray_shadow = _store._shadow(_stray.position, Vector2(5.0, 1.5))


func _build_train() -> void:
	if not Sprites.has_animation("amb_toy_train"):
		return
	_train = _mover("amb_toy_train", TRAIN_SIZE)
	_train.position = Vector2(TRAIN_RANGE.x, TRAIN_Y)
	_train.z_index = _store.floor_z(TRAIN_Y)
	_train.play("amb_toy_train")
	_train_shadow = _store._shadow(_train.position, Vector2(TRAIN_SIZE.x / 2.0, 2.0))


func _mover(anim_name: String, size: Vector2i) -> AnimatedSprite2D:
	var sprite: AnimatedSprite2D = Sprites.animated([anim_name], size)
	add_child(sprite)
	return sprite


func _process(delta: float) -> void:
	_time += delta
	_swing_hanging(delta)
	_move_moths()
	_move_mouse(delta)
	_move_windup(delta)
	_move_stray(delta)
	_move_train(delta)


## Lanterns, the mobile, the wind chime and the spider swing on their cords
## when the player runs past underneath.
func _swing_hanging(delta: float) -> void:
	for item in placed:
		var swing: RefCounted = item["swing"]
		if swing == null:
			continue
		var sprite: AnimatedSprite2D = item["sprite"]
		var push: float = _store.breeze(sprite.position.x)
		if push != 0.0:
			swing.kick(push * BREEZE_KICK)
		sprite.rotation = swing.step(delta)


func _move_moths() -> void:
	for moth in _moths:
		var sprite: AnimatedSprite2D = moth["sprite"]
		var angle: float = _time * MOTH_SPEED + moth["phase"]
		var breathe: float = 1.0 + sin(_time * MOTH_WOBBLE_SPEED + moth["phase"]) * MOTH_WOBBLE
		var at: Vector2 = moth["centre"] + Vector2(cos(angle) * MOTH_ORBIT.x, sin(angle * 1.3) * MOTH_ORBIT.y) * breathe
		sprite.flip_h = at.x < sprite.position.x
		sprite.position = at.round()


func _move_mouse(delta: float) -> void:
	if _mouse == null:
		return
	if not _mouse.visible:
		_mouse_wait -= delta
		if _mouse_wait > 0.0:
			return
		# Across what the camera shows, from one side to the other.
		var low: float = maxf(_store.view_x - MOUSE_SPAN, MOUSE_MARGIN)
		var high: float = minf(_store.view_x + MOUSE_SPAN, _store.STORE_WIDTH - MOUSE_MARGIN)
		var rightwards: bool = _rng.randf() < 0.5
		_mouse.position = Vector2(low if rightwards else high, MOUSE_Y)
		_mouse_target = high if rightwards else low
		_mouse.flip_h = not rightwards
		_mouse.visible = true
		_mouse.play("amb_mouse_run")
		return
	_mouse.position.x = move_toward(_mouse.position.x, _mouse_target, MOUSE_SPEED * delta)
	if _mouse.position.x == _mouse_target:
		_mouse.visible = false
		_mouse.stop()
		_mouse_wait = _rng.randf_range(MOUSE_WAIT.x, MOUSE_WAIT.y)


func _move_windup(delta: float) -> void:
	# Not in the compact store.
	if _windup == null:
		return
	if _windup == null:
		return
	if _windup_pause > 0.0:
		# It marks time at the end of the shelf before turning round.
		_windup_pause -= delta
		if _windup_pause <= 0.0:
			_windup_direction = -_windup_direction
			_windup.flip_h = _windup_direction < 0.0
		return
	var goal: float = _windup_range.y if _windup_direction > 0.0 else _windup_range.x
	_windup.position.x = move_toward(_windup.position.x, goal, WINDUP_SPEED * delta)
	if _windup.position.x == goal:
		_windup_pause = WINDUP_TURN_PAUSE


func _move_train(delta: float) -> void:
	# Not in the compact store.
	if _train == null:
		return
	if _train == null:
		return
	if _train_stop > 0.0:
		# A short halt at the end of the line, then back the other way.
		_train_stop -= delta
		if _train_stop <= 0.0:
			_train_direction = -_train_direction
			_train.flip_h = _train_direction < 0.0
			_train.play("amb_toy_train")
		return
	var goal: float = TRAIN_RANGE.y if _train_direction > 0.0 else TRAIN_RANGE.x
	_train.position.x = move_toward(_train.position.x, goal, TRAIN_SPEED * delta)
	_train_shadow.position.x = _train.position.x
	if _train.position.x == goal:
		_train.pause()
		_train_stop = TRAIN_STOP


func _move_stray(delta: float) -> void:
	# Not in the compact store.
	if _stray == null:
		return
	if _stray == null:
		return
	if _stray.position.x == _stray_target:
		_stray_rest -= delta
		if _stray_rest > 0.0:
			return
		var side: float = 1.0 if _rng.randf() < 0.5 else -1.0
		var wanted: float = _stray.position.x + side * _rng.randf_range(STRAY_ROLL.x, STRAY_ROLL.y)
		if wanted < STRAY_RANGE.x or wanted > STRAY_RANGE.y:
			wanted = _stray.position.x - side * _rng.randf_range(STRAY_ROLL.x, STRAY_ROLL.y)
		_stray_target = roundf(clampf(wanted, STRAY_RANGE.x, STRAY_RANGE.y))
		_stray.flip_h = _stray_target < _stray.position.x
		_stray.play("amb_capsule_roll")
		return
	# It slows down as it comes to rest.
	var left: float = absf(_stray_target - _stray.position.x)
	var pace: float = clampf(left / 20.0, 0.25, 1.0)
	_stray.speed_scale = pace
	_stray.position.x = move_toward(_stray.position.x, _stray_target, STRAY_SPEED * pace * delta)
	_stray_shadow.position.x = _stray.position.x
	if _stray.position.x == _stray_target:
		_stray.pause()
		_stray_rest = _rng.randf_range(STRAY_REST.x, STRAY_REST.y)
