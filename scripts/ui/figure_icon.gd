extends Control
## Small pixel-art picture of a figure for the catalog. A discovered figure
## stands on the base of its rarity. An undiscovered one is the same sprite
## filled dark, so every silhouette keeps its own shape (design section 7.2),
## and it has no base: the base would give its rarity away. A discovered figure
## plays its idle loop; a silhouette is always the still picture.

const Sprites = preload("res://scripts/world/sprite_lib.gd")
const SILHOUETTE: Color = Color(0.07, 0.08, 0.12)
## A silhouette stands this many world pixels above the bottom of the base
## frame it does not show.
const SILHOUETTE_FOOT: int = 4

var look: Dictionary = {}
var silhouette: bool = false
## The animated base under a discovered figure; null for a silhouette.
var base: AnimatedSprite2D
## True while the icon plays the idle loop of the figure (discovered ones only).
var animated: bool = false
## Seconds into the loop; set it before `show_figure` so icons side by side
## do not move in step.
var time_offset: float = 0.0
var _texture: Texture2D
var _frames: SpriteFrames
var _idle_fps: float = 8.0
var _time: float = 0.0
var _frame: int = 0
var _rarity_id: String = ""
## Scale that shows the base at one screen pixel per world pixel.
var _base_scale: Vector2 = Sprites.DRAW_SCALE


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	set_process(animated)


func _process(delta: float) -> void:
	if not is_visible_in_tree():
		return
	_time += delta
	var frame: int = int(_time * _idle_fps) % _frames.get_frame_count(Sprites.FIGURE_IDLE)
	if frame != _frame:
		_frame = frame
		queue_redraw()


func _notification(what: int) -> void:
	# The grid sizes the icon after `show_figure`: follow every resize.
	if what == NOTIFICATION_RESIZED:
		_layout_base()
		queue_redraw()


func show_figure(figure_id: String, p_look: Dictionary, p_silhouette: bool, rarity_id: String = "") -> void:
	look = p_look
	silhouette = p_silhouette
	var fallback: Color = Color.from_string(str(look.get("color", "#cccccc")), Color.GRAY)
	_frames = Sprites.figure_frames(figure_id, fallback)
	_texture = _frames.get_frame_texture(Sprites.FIGURE_STILL, 0)
	animated = not silhouette and Sprites.has_figure_idle(figure_id)
	_idle_fps = maxf(_frames.get_animation_speed(Sprites.FIGURE_IDLE), 1.0)
	_time = time_offset
	_frame = 0
	set_process(animated)
	var wanted: String = "" if silhouette else rarity_id
	if wanted != _rarity_id:
		_rarity_id = wanted
		if base != null:
			base.queue_free()
			base = null
		if wanted != "":
			base = Sprites.base_sprite(wanted)
			_base_scale = base.scale
			# The figure, drawn by this control, stands in front of its base.
			base.show_behind_parent = true
			add_child(base)
	_layout_base()
	queue_redraw()


## Figure plus base, in world pixels: the figure's feet stand on the base's
## stand point.
func _stack_size() -> Vector2:
	return Vector2(Sprites.BASE_WORLD.x, Sprites.FIGURE_WORLD.y + Sprites.BASE_WORLD.y - Sprites.BASE_STAND_WORLD.y)


## Screen pixels per WORLD pixel: the stack fills the control by a whole
## number of them. Each picture is then drawn at this times its own world
## scale, so art of either resolution keeps the same size on screen.
func _pixel_size() -> float:
	var stack: Vector2 = _stack_size()
	return maxf(floorf(minf(size.x / stack.x, size.y / stack.y)), 1.0)


## Screen size of the figure's picture at `pixel` screen pixels per world pixel.
func _picture_size(pixel: float) -> Vector2:
	return Vector2(_texture.get_size()) * Sprites.draw_scale(_texture.get_size(), Sprites.FIGURE_WORLD) * pixel


## Top-left corner of the base frame on this control.
func _base_origin() -> Vector2:
	var pixel: float = _pixel_size()
	var stack: Vector2 = _stack_size() * pixel
	var corner: Vector2 = ((size - stack) / 2.0).floor()
	return corner + Vector2(0.0, stack.y - Sprites.BASE_WORLD.y * pixel)


func _layout_base() -> void:
	if base == null:
		return
	var pixel: float = _pixel_size()
	base.position = _base_origin()
	base.scale = _base_scale * pixel


func _draw() -> void:
	if _texture == null:
		return
	var pixel: float = _pixel_size()
	var picture: Vector2 = _picture_size(pixel)
	var origin: Vector2 = _base_origin()
	# A discovered figure has its feet on the base; a silhouette stands where
	# the base's own foot would be.
	var feet: Vector2 = origin + Vector2(Sprites.BASE_STAND_WORLD.x, Sprites.BASE_STAND_WORLD.y if base != null else Sprites.BASE_WORLD.y - SILHOUETTE_FOOT) * pixel
	# Multiplying by a near-black colour keeps the alpha, which is the outline.
	var shown: Texture2D = _frames.get_frame_texture(Sprites.FIGURE_IDLE, _frame) if animated else _texture
	draw_texture_rect(shown, Rect2((feet - Vector2(picture.x / 2.0, picture.y)).floor(), picture), false, SILHOUETTE if silhouette else Color.WHITE)
