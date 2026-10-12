extends Control
## Large pixel-art picture of a figure for the prize panel: the figure stands
## on the animated base of its rarity, playing its idle loop (or bobbing
## gently while that loop is not drawn), over a burst tinted with its rarity
## colour. A fresh prize first shows its capsule shaking and splitting open;
## figure and base pop out of the flash.

const Sprites = preload("res://scripts/world/sprite_lib.gd")

const BOB_PIXELS: float = 1.0
const BOB_SPEED: float = 2.4
const CAPSULE_SIZE: Vector2i = Vector2i(40, 40)
## Frame of `capsule_open` with the biggest flash: the figure appears under it.
const REVEAL_FRAME: int = 7
## The figure pops in over these sizes, in sprite-pixel steps relative to its
## final pixel size (whole pixels keep the art crisp), one step per POP_STEP.
const POP_STEPS: Array = [-3, -1, 1, 0]
const POP_STEP: float = 0.05
## The burst is drawn at this share of the figure's pixel size (rounded down to
## whole pixels) so its widest ring still fits inside the view.
const BURST_SCALE: float = 0.7
const BURST_SIZE: Vector2i = Vector2i(64, 64)

## The animated base under the figure; null until a rarity was shown.
var base: AnimatedSprite2D

## True when the figure shown has a drawn idle loop.
var animated: bool = false

var _texture: Texture2D
## The frames of the figure (see Sprites.figure_frames) and the pace of its loop.
var _frames: SpriteFrames
var _idle_fps: float = 8.0
var _tint: Color = Color.WHITE
var _time: float = 0.0
var _burst: AnimatedSprite2D
var _capsule: AnimatedSprite2D
var _capsule_anim: String = ""
var _rarity_id: String = ""
## True while the capsule is still closed: figure and base are not drawn yet.
var _hidden: bool = false
var _pop_time: float = 0.0


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	clip_contents = true
	if Sprites.has_animation("rarity_burst"):
		_burst = AnimatedSprite2D.new()
		_burst.sprite_frames = Sprites.frames(["rarity_burst"], BURST_SIZE)
		_burst.sprite_frames.set_animation_loop("rarity_burst", false)
		_burst.visible = false
		# The burst opens behind the toy, not across its face.
		_burst.show_behind_parent = true
		_burst.animation_finished.connect(func() -> void: _burst.visible = false)
		add_child(_burst)
	_capsule = AnimatedSprite2D.new()
	_capsule.visible = false
	_capsule.frame_changed.connect(_on_capsule_frame)
	_capsule.animation_finished.connect(func() -> void:
		_capsule.visible = false
		_reveal())
	add_child(_capsule)


func _process(delta: float) -> void:
	if is_visible_in_tree() and _texture != null:
		_time += delta
		_pop_time += delta
		_layout_effects()
		queue_redraw()


## Figure plus base, in sprite pixels: the figure's feet stand on BASE_STAND.
func _stack_size() -> Vector2:
	return Vector2(Sprites.BASE_SIZE.x, Sprites.FIGURE_SIZE.y + Sprites.BASE_SIZE.y - Sprites.BASE_STAND.y)


## Whole screen pixels per sprite pixel, so the art stays crisp.
func _pixel_size() -> float:
	var stack: Vector2 = _stack_size()
	return maxf(floorf(minf(size.x / stack.x, size.y / stack.y)), 1.0)


## Top-left corner of the base frame on this control.
func _base_origin() -> Vector2:
	var pixel: float = _pixel_size()
	var stack: Vector2 = _stack_size() * pixel
	var corner: Vector2 = ((size - stack) / 2.0).floor()
	return corner + Vector2(0.0, stack.y - Sprites.BASE_SIZE.y * pixel)


## Where the figure's feet touch the base.
func _feet() -> Vector2:
	return _base_origin() + Vector2(Sprites.BASE_STAND) * _pixel_size()


## Keeps the effects on the figure and at its pixel size, whatever the layout did.
func _layout_effects() -> void:
	var pixel: float = _pixel_size()
	var centre: Vector2 = _feet() - Vector2(0.0, Sprites.FIGURE_SIZE.y * pixel / 2.0)
	_capsule.position = centre
	_capsule.scale = Vector2(pixel, pixel)
	if _burst != null:
		_burst.position = centre
		var burst_pixel: float = maxf(floorf(pixel * BURST_SCALE), 1.0)
		_burst.scale = Vector2(burst_pixel, burst_pixel)
	if base != null:
		base.position = _base_origin()
		base.scale = Vector2(pixel, pixel)
		base.visible = not _hidden


## `capsule_color` (red, blue, green, mustard, gold) plays the capsule opening
## first; leave it empty to show the figure at once. `rarity_id` picks the base.
func show_figure(figure_id: String, rarity_color: Color, capsule_color: String = "", rarity_id: String = "") -> void:
	_frames = Sprites.figure_frames(figure_id)
	_texture = _frames.get_frame_texture(Sprites.FIGURE_STILL, 0)
	animated = Sprites.has_figure_idle(figure_id)
	_idle_fps = maxf(_frames.get_animation_speed(Sprites.FIGURE_IDLE), 1.0)
	_tint = rarity_color
	_time = 0.0
	_pop_time = POP_STEP * POP_STEPS.size()
	_hidden = false
	_set_base(rarity_id)
	_capsule.stop()
	_capsule.visible = false
	if _burst != null:
		_burst.stop()
		_burst.visible = false
	var anim: String = _capsule_animation(capsule_color)
	if anim != "":
		_start_capsule(anim)
	else:
		_play_burst()
	_layout_effects()
	queue_redraw()


func _set_base(rarity_id: String) -> void:
	if rarity_id == _rarity_id:
		return
	_rarity_id = rarity_id
	if base != null:
		base.queue_free()
		base = null
	if rarity_id == "":
		return
	base = Sprites.base_sprite(rarity_id)
	# Behind the figure this control draws, in front of the burst.
	base.show_behind_parent = true
	add_child(base)
	if _burst != null:
		move_child(_burst, 0)


## The sheet for a capsule colour; red is the plain `capsule_open`.
func _capsule_animation(capsule_color: String) -> String:
	if capsule_color == "":
		return ""
	var anim: String = "capsule_open_%s" % capsule_color
	if not Sprites.has_animation(anim):
		anim = "capsule_open"
	return anim if Sprites.has_animation(anim) else ""


func _start_capsule(anim: String) -> void:
	if anim != _capsule_anim:
		_capsule_anim = anim
		_capsule.sprite_frames = Sprites.frames([anim], CAPSULE_SIZE)
		_capsule.sprite_frames.set_animation_loop(anim, false)
	_hidden = true
	_layout_effects()
	_capsule.visible = true
	_capsule.play(anim)
	_capsule.frame = 0


func _on_capsule_frame() -> void:
	if _capsule.visible and _capsule.frame >= REVEAL_FRAME:
		_reveal()


## The capsule has burst: figure and base appear under the flash.
func _reveal() -> void:
	if not _hidden:
		return
	_hidden = false
	_pop_time = 0.0
	_time = 0.0
	_play_burst()
	_layout_effects()
	queue_redraw()


func _play_burst() -> void:
	if _burst == null:
		return
	_layout_effects()
	_burst.modulate = Color(_tint, 0.9)
	_burst.visible = true
	_burst.play("rarity_burst")
	_burst.frame = 0


func _draw() -> void:
	if _texture == null or _hidden:
		return
	var pixel: float = _pixel_size()
	var picture: Vector2 = Vector2(_texture.get_size()) * pixel
	var feet: Vector2 = _feet()
	var step: int = int(_pop_time / POP_STEP)
	if step < POP_STEPS.size():
		# Popping out of the capsule: small, a little too big, then settled.
		var popped: Vector2 = Vector2(_texture.get_size()) * maxf(pixel + POP_STEPS[step], 1.0)
		draw_texture_rect(_texture, Rect2((feet - Vector2(popped.x / 2.0, popped.y)).floor(), popped), false)
		return
	if animated:
		# The idle loop of the figure, started on its first frame at the reveal.
		var frame: int = int(_time * _idle_fps) % _frames.get_frame_count(Sprites.FIGURE_IDLE)
		draw_texture_rect(_frames.get_frame_texture(Sprites.FIGURE_IDLE, frame), Rect2((feet - Vector2(picture.x / 2.0, picture.y)).floor(), picture), false)
		return
	# No loop drawn: a springy little hop on the base, by whole sprite pixels.
	var lift: float = maxf(roundf(sin(_time * BOB_SPEED) * BOB_PIXELS), 0.0) * pixel
	draw_texture_rect(_texture, Rect2((feet - Vector2(picture.x / 2.0, picture.y + lift)).floor(), picture), false)
