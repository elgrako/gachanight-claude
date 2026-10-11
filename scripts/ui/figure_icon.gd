extends Control
## Small pixel-art picture of a figure for the catalog. An undiscovered figure
## is the same sprite filled dark, so every silhouette keeps its own shape
## (design section 7.2).

const Sprites = preload("res://scripts/world/sprite_lib.gd")
const SILHOUETTE: Color = Color(0.07, 0.08, 0.12)

var look: Dictionary = {}
var silhouette: bool = false
var _texture: Texture2D


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST


func show_figure(figure_id: String, p_look: Dictionary, p_silhouette: bool) -> void:
	look = p_look
	silhouette = p_silhouette
	var fallback: Color = Color.from_string(str(look.get("color", "#cccccc")), Color.GRAY)
	_texture = Sprites.texture("figures/%s" % figure_id, Vector2i(32, 32), fallback)
	queue_redraw()


func _draw() -> void:
	if _texture == null:
		return
	# Whole screen pixels per sprite pixel keep the art crisp.
	var pixel: float = maxf(floorf(minf(size.x, size.y) / _texture.get_height()), 1.0)
	var picture: Vector2 = Vector2(_texture.get_size()) * pixel
	# Multiplying by a near-black colour keeps the alpha, which is the outline.
	draw_texture_rect(_texture, Rect2(((size - picture) / 2.0).floor(), picture), false, SILHOUETTE if silhouette else Color.WHITE)
