extends Node2D
## The player character: walks on the floor plane of the store (left/right and
## nearer/farther) and uses whatever it stands next to. Its position is the
## point where its feet touch the floor; one side-facing sprite set, flipped
## by x, serves every direction.

const Sprites = preload("res://scripts/world/sprite_lib.gd")

const WALK_SPEED: float = 80.0
const RUN_SPEED: float = 150.0
## The floor is seen at an angle, so a step away from the camera covers fewer
## screen pixels than a step sideways.
const DEPTH_SPEED_FACTOR: float = 0.7
## Pixels per second each cycle was drawn for; the animation speeds up with the
## real ground speed so the feet do not slide.
const WALK_ANIM_SPEED: float = 37.0
const RUN_ANIM_SPEED: float = 105.0
const MIN_WALK_ANIM_SCALE: float = 0.6
## Above this speed the run cycle is shown, and below IDLE_SPEED the idle one.
const RUN_THRESHOLD: float = WALK_SPEED + 8.0
const IDLE_SPEED: float = 4.0
## Frame of the reaching animation on which the hand is fully stretched out.
const USE_REACH_FRAME: int = 2
const USE_MAX_SPEED: float = 3.0
const USE_MIN_TIME: float = 0.3
const EMOTE_MIN_TIME: float = 0.4
## The protagonist is the coin of assets/sprites/peseta (tools/pixel/build_peseta.py).
## Its strips are drawn far finer than the rest of the art, so they are shown
## reduced and smoothed. At this scale the coin stands about 54 world pixels
## tall, a little over half a capsule machine.
const SKIN_SCALE: Vector2 = Vector2(0.27, 0.27)
const FRAME_SIZE: Vector2i = Vector2i(77, 74)
## What the game asks for -> the strip that plays. The coin has fewer
## animations than the gestures the game knows; each borrows the nearest one.
const SKIN: Dictionary = {
	"player_idle": "peseta_idle", "player_walk": "peseta_walk", "player_run": "peseta_run",
	"player_use": "peseta_use", "player_cheer": "peseta_cheer", "player_stretch": "peseta_cheer",
	"player_shrug": "peseta_wave", "player_watch": "peseta_wave", "player_wave": "peseta_wave",
}
const SLEEP_ANIMATION: String = "peseta_sleep"
## Every strip also exists drawn facing left (the 1 on the coin must not be
## mirrored), so the sprite is never flipped: it plays the left-hand strip.
const LEFT: String = "_left"
## The floating letters start above the dozing coin's hat.
const ZZZ_OFFSET: Vector2 = Vector2(14.0, -70.0)
## How quickly the character reaches its speed and stops, in pixels per second squared.
const ACCELERATION: float = 700.0
const ANIMATIONS: Array = ["player_idle", "player_walk", "player_run", "player_use", "player_cheer", "player_stretch", "player_shrug", "player_watch", "player_wave"]
## Standing still this long (seconds, picked in this range) the character
## checks its watch; any step or gesture starts the wait again.
const FIDGET_AFTER: Vector2 = Vector2(14.0, 24.0)
const FIDGET_ANIMATION: String = "player_watch"
## While running, a puff of dust at the heels this often, in seconds.
const RUN_DUST_EVERY: float = 0.3
## The part of the floor the feet occupy: this wide, and this deep behind the
## position. Solid footprints are tested against it.
const FOOT_HALF_WIDTH: float = 7.0
const FOOT_DEPTH: float = 3.0
const SHADOW_RADIUS: Vector2 = Vector2(14.0, 3.5)
const SHADOW_COLOR: Color = Color(0.0, 0.0, 0.05, 0.3)
const DUST_SIZE: Vector2i = Vector2i(16, 12)
## Draw order of things standing on the floor: this plus the floor y.
const FLOOR_Z_BASE: int = 100

var controls_enabled: bool = true
## The floor the feet may stand on, and the footprints (Rect2) they may not enter.
var walk_area: Rect2 = Rect2(0.0, 0.0, 1000.0, 100.0)
var solids: Array = []
## Filled by the main scene with the store's interactables.
var interactables: Array = []
var sprite: AnimatedSprite2D

var _velocity: Vector2 = Vector2.ZERO
var _left: bool = false
var _using: bool = false
var _use_serial: int = 0
var _was_running: bool = false
var _run_dust_in: float = 0.0
var _fidget_in: float = FIDGET_AFTER.y
## True while a fidget plays over the idle pose.
var _fidgeting: bool = false
var _sleeper: AnimatedSprite2D
var _zzz: AnimatedSprite2D
var _shadow: Polygon2D


func _ready() -> void:
	_shadow = Sprites.ellipse(SHADOW_RADIUS, SHADOW_COLOR)
	add_child(_shadow)
	sprite = _skinned(ANIMATIONS)
	add_child(sprite)
	sprite.play(_named("player_idle"))
	_sort()


## The animation to play for a gesture, given the way the coin faces.
func _named(anim_name: String) -> String:
	return anim_name + LEFT if _left else anim_name


## Turns the coin to face left or right, keeping its place in the animation.
func _face(left: bool) -> void:
	if left == _left:
		return
	_left = left
	var playing: bool = sprite.is_playing()
	var frame: int = sprite.frame
	var progress: float = sprite.frame_progress
	var wanted: String = _named(str(sprite.animation).trim_suffix(LEFT))
	if playing:
		sprite.play(wanted)
	else:
		sprite.animation = wanted
	sprite.set_frame_and_progress(frame, progress)


## An animated sprite whose animations carry the game's names and play the
## coin's strips (see SKIN).
func _skinned(anim_names: Array) -> AnimatedSprite2D:
	var strips: Array = []
	for anim_name in anim_names:
		var strip: String = SKIN.get(anim_name, anim_name)
		for side in ["", LEFT]:
			if not strips.has(strip + side) and Sprites.has_animation(strip + side):
				strips.append(strip + side)
	var skinned: AnimatedSprite2D = Sprites.animated(strips, FRAME_SIZE)
	var source: SpriteFrames = skinned.sprite_frames
	var frames: SpriteFrames = SpriteFrames.new()
	if frames.has_animation("default"):
		frames.remove_animation("default")
	for anim_name in anim_names:
		var strip: String = SKIN.get(anim_name, anim_name)
		for side in ["", LEFT]:
			var from: String = strip + side if source.has_animation(strip + side) else strip
			frames.add_animation(anim_name + side)
			frames.set_animation_speed(anim_name + side, source.get_animation_speed(from))
			frames.set_animation_loop(anim_name + side, source.get_animation_loop(from))
			for index in range(source.get_frame_count(from)):
				frames.add_frame(anim_name + side, source.get_frame_texture(from, index))
	skinned.sprite_frames = frames
	skinned.animation = anim_names[0]
	skinned.scale = SKIN_SCALE
	skinned.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	return skinned


func _process(delta: float) -> void:
	if is_sleeping():
		return
	var direction: Vector2 = Vector2.ZERO
	if controls_enabled and not _using:
		direction = Vector2(Input.get_axis("move_left", "move_right"), Input.get_axis("move_forward", "move_back"))
		if direction.length() > 1.0:
			direction = direction.normalized()
	var top_speed: float = RUN_SPEED if Input.is_action_pressed("sprint") else WALK_SPEED
	var wanted: Vector2 = Vector2(direction.x, direction.y * DEPTH_SPEED_FACTOR) * top_speed
	_velocity = _velocity.move_toward(wanted, ACCELERATION * delta)
	_step(delta)
	if direction.x != 0.0:
		_face(direction.x < 0.0)
	_sort()
	_update_animation()
	_update_life(delta)


## Dust while running, and a look at the watch after standing around.
func _update_life(delta: float) -> void:
	if _was_running and not _using:
		_run_dust_in -= delta
		if _run_dust_in <= 0.0:
			_run_dust_in = RUN_DUST_EVERY
			_dust()
	if _using or _fidgeting or _velocity.length() > IDLE_SPEED:
		_fidget_in = randf_range(FIDGET_AFTER.x, FIDGET_AFTER.y)
		return
	_fidget_in -= delta
	if _fidget_in <= 0.0:
		_fidget_in = randf_range(FIDGET_AFTER.x, FIDGET_AFTER.y)
		play_emote(FIDGET_ANIMATION, true)


## Speed over the floor, in pixels per second.
func velocity() -> Vector2:
	return _velocity


## Moves one axis at a time, so the character slides along walls and
## footprints instead of sticking to them.
func _step(delta: float) -> void:
	var low: Vector2 = walk_area.position
	var high: Vector2 = walk_area.end
	var next_x: float = clampf(position.x + _velocity.x * delta, low.x, high.x)
	if next_x != position.x and _blocked(Vector2(next_x, position.y)):
		next_x = position.x
	if next_x == position.x:
		_velocity.x = 0.0
	position.x = next_x
	var next_y: float = clampf(position.y + _velocity.y * delta, low.y, high.y)
	if next_y != position.y and _blocked(Vector2(position.x, next_y)):
		next_y = position.y
	if next_y == position.y:
		_velocity.y = 0.0
	position.y = next_y


## True when feet at `at` would stand inside a solid footprint. Feet that are
## already inside one (placed there) are never held: they may always walk out.
func _blocked(at: Vector2) -> bool:
	return _feet_hit(at) and not _feet_hit(position)


func _feet_hit(at: Vector2) -> bool:
	var feet: Rect2 = Rect2(at.x - FOOT_HALF_WIDTH, at.y - FOOT_DEPTH, FOOT_HALF_WIDTH * 2.0, FOOT_DEPTH)
	for solid in solids:
		if solid.intersects(feet):
			return true
	return false


## Nearer things are drawn over farther ones.
func _sort() -> void:
	z_index = FLOOR_Z_BASE + int(position.y)


func _update_animation() -> void:
	if _using:
		return
	var speed: float = _velocity.length()
	var wanted: String = "player_idle"
	sprite.speed_scale = 1.0
	if speed > RUN_THRESHOLD:
		wanted = "player_run"
		sprite.speed_scale = speed / RUN_ANIM_SPEED
	elif speed > IDLE_SPEED:
		wanted = "player_walk"
		sprite.speed_scale = maxf(speed / WALK_ANIM_SPEED, MIN_WALK_ANIM_SCALE)
	if _fidgeting:
		# A fidget plays to its end over the idle pose; a step cuts it short.
		if wanted == "player_idle" and sprite.is_playing():
			return
		_fidgeting = false
	var running: bool = wanted == "player_run"
	if running != _was_running:
		# A little cloud at the heels when breaking into a run and when stopping.
		_was_running = running
		_run_dust_in = RUN_DUST_EVERY
		_dust()
	if sprite.animation != _named(wanted):
		sprite.play(_named(wanted))


func _dust() -> void:
	if get_parent() == null:
		return
	var behind: float = 8.0 if _left else -8.0
	Sprites.burst(get_parent(), "dust_puff", global_position + Vector2(behind, -DUST_SIZE.y / 2.0), DUST_SIZE)


## The closest usable thing whose use point is within reach, or null.
func focused_interactable() -> Object:
	var best: Object = null
	var best_distance: float = INF
	for item in interactables:
		if not is_instance_valid(item) or not item.visible:
			continue
		var distance: float = item.use_point().distance_to(global_position)
		if distance <= item.reach and distance < best_distance:
			best = item
			best_distance = distance
	return best


## Turns towards a world x and plays the reaching animation once. `speed`
## shortens it together with a sped-up machine.
func play_use(target_x: float, speed: float = 1.0) -> void:
	if absf(target_x - global_position.x) > 1.0:
		_face(target_x < global_position.x)
	_play_once("player_use", clampf(speed, 1.0, USE_MAX_SPEED), USE_MIN_TIME)


## Jumps for joy once (a new figure).
func play_cheer() -> void:
	play_emote("player_cheer")


## Plays a one-shot gesture (player_cheer, player_stretch, player_shrug,
## player_watch, player_wave); nothing happens while its art is missing. An
## `idle_only` gesture is a fidget: walking is not held and any step ends it.
func play_emote(anim_name: String, idle_only: bool = false) -> void:
	if is_sleeping() or not ANIMATIONS.has(anim_name) or not Sprites.has_animation(SKIN.get(anim_name, anim_name)):
		return
	if idle_only:
		if not _using:
			_fidgeting = true
			sprite.speed_scale = 1.0
			sprite.play(_named(anim_name))
		return
	_play_once(anim_name, 1.0, EMOTE_MIN_TIME)


## Plays a one-shot animation; walking is held until it ends.
func _play_once(anim_name: String, pace: float, min_time: float) -> void:
	_using = true
	_fidgeting = false
	_velocity = Vector2.ZERO
	sprite.speed_scale = pace
	sprite.play(_named(anim_name))
	_use_serial += 1
	var serial: int = _use_serial
	await get_tree().create_timer(maxf(Sprites.animation_length(SKIN.get(anim_name, anim_name)), min_time) / pace).timeout
	if serial == _use_serial and _using:
		_using = false
		sprite.speed_scale = 1.0
		sprite.play(_named("player_idle"))


## Seconds from `play_use` until the hand is fully stretched out, at speed 1.
## Whatever the hand touches should start then.
func use_reach_time() -> float:
	var info: Dictionary = Sprites.animation_info(SKIN["player_use"])
	if info.is_empty():
		return 0.0
	return USE_REACH_FRAME / maxf(float(info.get("fps", 12)), 1.0)


## Lies down asleep with its bottom centre at a world position (the sofa seat).
## `place` wakes it up again.
func sleep_at(world_position: Vector2) -> void:
	if not Sprites.has_animation(SLEEP_ANIMATION):
		return
	if _sleeper == null:
		_sleeper = _skinned([SLEEP_ANIMATION])
		# The sleeper lies on the sofa wherever the character stood before.
		_sleeper.z_as_relative = false
		_sleeper.z_index = Sprites.Z_EFFECT - 1
		add_child(_sleeper)
		_zzz = Sprites.animated(["zzz"], Vector2i(16, 16), Color(1, 1, 1, 0))
		_sleeper.add_child(_zzz)
		# The sleeper is drawn at a third; the letters keep their own size.
		_zzz.scale = Sprites.DRAW_SCALE / SKIN_SCALE
		_zzz.position = ZZZ_OFFSET / SKIN_SCALE
	_using = false
	_use_serial += 1
	_velocity = Vector2.ZERO
	sprite.visible = false
	_shadow.visible = false
	_sleeper.global_position = world_position
	_sleeper.visible = true
	_sleeper.play(SLEEP_ANIMATION)
	_zzz.play("zzz")


func wake() -> void:
	if _sleeper != null:
		_sleeper.visible = false
		_sleeper.stop()
		_zzz.stop()
	sprite.visible = true
	_shadow.visible = true


func is_sleeping() -> bool:
	return _sleeper != null and _sleeper.visible


## Stands the character on a floor point, idle.
func place(at: Vector2, face_left: bool = false) -> void:
	position = at
	_velocity = Vector2.ZERO
	_using = false
	_use_serial += 1
	_was_running = false
	_fidgeting = false
	wake()
	_left = face_left
	sprite.speed_scale = 1.0
	sprite.play(_named("player_idle"))
	_sort()
