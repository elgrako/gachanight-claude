extends Node2D
## Side-view character: walks left and right along the store floor and uses
## whatever it stands next to.

const Sprites = preload("res://scripts/world/sprite_lib.gd")

const WALK_SPEED: float = 46.0
const RUN_SPEED: float = 96.0
## Pixels per second each cycle was drawn for; the animation speeds up with the
## real speed so the feet do not slide. The walk sheet covers 20 px in 8 frames
## and the run sheet 30 px in 6 frames, both at 12 fps.
const WALK_ANIM_SPEED: float = 30.0
const RUN_ANIM_SPEED: float = 60.0
## Frame of `player_use` on which the hand is fully stretched out.
const USE_REACH_FRAME: int = 3
const USE_MAX_SPEED: float = 3.0
const SLEEP_FRAME_SIZE: Vector2i = Vector2i(40, 24)
## The floating letters start above the sleeper's head, which lies to the left.
const ZZZ_OFFSET: Vector2 = Vector2(-9.0, -13.0)
## How quickly the character reaches its speed and stops, in pixels per second squared.
const ACCELERATION: float = 700.0
const FRAME_SIZE: Vector2i = Vector2i(24, 40)
const ANIMATIONS: Array = ["player_idle", "player_walk", "player_run", "player_use"]

var controls_enabled: bool = true
var min_x: float = 0.0
var max_x: float = 1000.0
## Filled by the main scene with the store's interactables.
var interactables: Array = []
var sprite: AnimatedSprite2D

var _velocity: float = 0.0
var _using: bool = false
var _use_serial: int = 0
var _sleeper: AnimatedSprite2D
var _zzz: AnimatedSprite2D


func _ready() -> void:
	sprite = Sprites.animated(ANIMATIONS, FRAME_SIZE)
	add_child(sprite)
	sprite.play("player_idle")


func _process(delta: float) -> void:
	var direction: float = 0.0
	if is_sleeping():
		return
	if controls_enabled and not _using:
		direction = Input.get_axis("move_left", "move_right")
	var top_speed: float = RUN_SPEED if Input.is_action_pressed("sprint") else WALK_SPEED
	_velocity = move_toward(_velocity, direction * top_speed, ACCELERATION * delta)
	var next_x: float = clampf(position.x + _velocity * delta, min_x, max_x)
	if next_x == position.x and direction == 0.0:
		_velocity = 0.0
	if next_x == min_x or next_x == max_x:
		_velocity = 0.0
	position.x = next_x
	if direction != 0.0:
		sprite.flip_h = direction < 0.0
	_update_animation()


func _update_animation() -> void:
	if _using:
		return
	var speed: float = absf(_velocity)
	var wanted: String = "player_idle"
	sprite.speed_scale = 1.0
	if speed > WALK_SPEED + 8.0:
		wanted = "player_run"
		sprite.speed_scale = speed / RUN_ANIM_SPEED
	elif speed > 4.0:
		wanted = "player_walk"
		sprite.speed_scale = maxf(speed / WALK_ANIM_SPEED, 0.6)
	if sprite.animation != wanted:
		sprite.play(wanted)


## The closest usable thing within reach, or null.
func focused_interactable() -> Object:
	var best: Object = null
	var best_distance: float = INF
	for item in interactables:
		if not is_instance_valid(item) or not item.visible:
			continue
		var distance: float = absf(item.global_position.x - global_position.x)
		if distance <= item.reach and distance < best_distance:
			best = item
			best_distance = distance
	return best


## Turns towards a world x and plays the reaching animation once. `speed`
## shortens it together with a sped-up machine.
func play_use(target_x: float, speed: float = 1.0) -> void:
	if absf(target_x - global_position.x) > 1.0:
		sprite.flip_h = target_x < global_position.x
	var pace: float = clampf(speed, 1.0, USE_MAX_SPEED)
	_using = true
	_velocity = 0.0
	sprite.speed_scale = pace
	sprite.play("player_use")
	_use_serial += 1
	var serial: int = _use_serial
	await get_tree().create_timer(maxf(Sprites.animation_length("player_use"), 0.3) / pace).timeout
	if serial == _use_serial and _using:
		_using = false
		sprite.speed_scale = 1.0
		sprite.play("player_idle")


## Seconds from `play_use` until the hand is fully stretched out, at speed 1.
## Whatever the hand touches should start then.
func use_reach_time() -> float:
	var info: Dictionary = Sprites.animation_info("player_use")
	if info.is_empty():
		return 0.0
	return USE_REACH_FRAME / maxf(float(info["fps"]), 1.0)


## Lies down asleep with its bottom centre at a world position (the sofa seat).
## `place` wakes it up again.
func sleep_at(world_position: Vector2) -> void:
	if Sprites.animation_info("player_sleep").is_empty():
		return
	if _sleeper == null:
		_sleeper = Sprites.animated(["player_sleep"], SLEEP_FRAME_SIZE)
		add_child(_sleeper)
		_zzz = Sprites.animated(["zzz"], Vector2i(16, 16))
		_sleeper.add_child(_zzz)
		_zzz.position = ZZZ_OFFSET
	_using = false
	_use_serial += 1
	_velocity = 0.0
	sprite.visible = false
	_sleeper.global_position = world_position
	_sleeper.visible = true
	_sleeper.play("player_sleep")
	_zzz.play("zzz")


func wake() -> void:
	if _sleeper != null:
		_sleeper.visible = false
		_sleeper.stop()
		_zzz.stop()
	sprite.visible = true


func is_sleeping() -> bool:
	return _sleeper != null and _sleeper.visible


func place(spawn_x: float, face_left: bool = false) -> void:
	position = Vector2(spawn_x, position.y)
	_velocity = 0.0
	_using = false
	_use_serial += 1
	wake()
	sprite.flip_h = face_left
	sprite.speed_scale = 1.0
	sprite.play("player_idle")
