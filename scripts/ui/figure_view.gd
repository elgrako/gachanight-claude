extends Control
## Large pixel-art picture of a figure for the prize panel: the sprite bobs
## gently over a burst tinted with its rarity colour. A fresh prize first shows
## its capsule shaking and splitting open; the figure pops out of the flash.

const Sprites = preload("res://scripts/world/sprite_lib.gd")

const BOB_PIXELS: float = 1.0
const BOB_SPEED: float = 2.4
const CAPSULE_SIZE: Vector2i = Vector2i(32, 32)
## Frame of `capsule_open` with the biggest flash: the figure appears under it.
const REVEAL_FRAME: int = 7
## The figure pops in over these sizes, in sprite-pixel steps relative to its
## final pixel size (whole pixels keep the art crisp), one step per POP_STEP.
const POP_STEPS: Array = [-3, -1, 1, 0]
const POP_STEP: float = 0.05
## The burst is drawn at this share of the figure's pixel size (rounded down to
## whole pixels) so its widest ring still fits inside the view.
const BURST_SCALE: float = 0.7

var _texture: Texture2D
var _tint: Color = Color.WHITE
var _time: float = 0.0
var _burst: AnimatedSprite2D
var _capsule: AnimatedSprite2D
var _capsule_anim: String = ""
## True while the capsule is still closed: the figure is not drawn yet.
var _hidden: bool = false
var _pop_time: float = 0.0


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	clip_contents = true
	if not Sprites.animation_info("rarity_burst").is_empty():
		_burst = AnimatedSprite2D.new()
		_burst.sprite_frames = Sprites.frames(["rarity_burst"], Vector2i(48, 48))
		_burst.sprite_frames.set_animation_loop("rarity_burst", false)
		_burst.visible = false
		# The burst opens behind the toy, not across its face.
		_burst.show_behind_parent = true
		_burst.animation_finished.connect(func() -> void: _burst.visible = false)
		add_child(_burst)
	_capsule = AnimatedSprite2D.new()
	_capsule.visible = false
	_capsule.frame_changed.connect(_on_capsule_frame)
	_capsule.animation_finished.connect(func() -> void: _capsule.visible = false)
	add_child(_capsule)


func _process(delta: float) -> void:
	if is_visible_in_tree() and _texture != null:
		_time += delta
		_pop_time += delta
		_layout_effects()
		queue_redraw()


## Keeps the effects centred and at the figure's pixel size, whatever the layout did.
func _layout_effects() -> void:
	var pixel: float = _pixel_size()
	var centre: Vector2 = (size / 2.0).floor()
	_capsule.position = centre
	_capsule.scale = Vector2(pixel, pixel)
	if _burst != null:
		_burst.position = centre
		var burst_pixel: float = maxf(floorf(pixel * BURST_SCALE), 1.0)
		_burst.scale = Vector2(burst_pixel, burst_pixel)


## `capsule_color` (coral, mint, mustard, teal, gold) plays the capsule opening
## first; leave it empty to show the figure at once.
func show_figure(figure_id: String, rarity_color: Color, capsule_color: String = "") -> void:
	_texture = Sprites.texture("figures/%s" % figure_id, Vector2i(32, 32))
	_tint = rarity_color
	_time = 0.0
	_pop_time = POP_STEP * POP_STEPS.size()
	_hidden = false
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
	queue_redraw()


## The sheet for a capsule colour; coral is the plain `capsule_open`.
func _capsule_animation(capsule_color: String) -> String:
	if capsule_color == "":
		return ""
	var anim: String = "capsule_open_%s" % capsule_color
	if Sprites.animation_info(anim).is_empty():
		anim = "capsule_open"
	return "" if Sprites.animation_info(anim).is_empty() else anim


func _start_capsule(anim: String) -> void:
	if anim != _capsule_anim:
		_capsule_anim = anim
		_capsule.sprite_frames = Sprites.frames([anim], CAPSULE_SIZE)
		_capsule.sprite_frames.set_animation_loop(anim, false)
	_layout_effects()
	_capsule.visible = true
	_hidden = true
	_capsule.play(anim)
	_capsule.frame = 0


func _on_capsule_frame() -> void:
	if _hidden and _capsule.visible and _capsule.frame >= REVEAL_FRAME:
		_hidden = false
		_pop_time = 0.0
		_time = 0.0
		_play_burst()
		queue_redraw()


func _play_burst() -> void:
	if _burst == null:
		return
	_layout_effects()
	_burst.modulate = Color(_tint, 0.9)
	_burst.visible = true
	_burst.play("rarity_burst")
	_burst.frame = 0


## Whole screen pixels per sprite pixel, so the art stays crisp.
func _pixel_size() -> float:
	if _texture == null:
		return 4.0
	return maxf(floorf(minf(size.x, size.y) / _texture.get_height()), 1.0)


func _draw() -> void:
	if _texture == null or _hidden:
		return
	var pixel: float = _pixel_size()
	var picture: Vector2 = Vector2(_texture.get_size()) * pixel
	var at: Vector2 = ((size - picture) / 2.0).floor()
	# A soft pad of the rarity colour under the toy.
	var pad: Vector2 = Vector2(picture.x * 0.7, pixel * 3.0)
	draw_rect(Rect2(Vector2((size.x - pad.x) / 2.0, at.y + picture.y - pixel), pad), Color(_tint, 0.45))
	var step: int = int(_pop_time / POP_STEP)
	if step < POP_STEPS.size():
		# Popping out of the capsule: small, a little too big, then settled.
		var popped: Vector2 = Vector2(_texture.get_size()) * maxf(pixel + POP_STEPS[step], 1.0)
		var feet: Vector2 = Vector2(size.x / 2.0, at.y + picture.y - pixel)
		draw_texture_rect(_texture, Rect2((feet - Vector2(popped.x / 2.0, popped.y)).floor(), popped), false)
		return
	# The bob moves by whole sprite pixels.
	at.y += roundf(sin(_time * BOB_SPEED) * BOB_PIXELS) * pixel - pixel
	draw_texture_rect(_texture, Rect2(at, picture), false)
