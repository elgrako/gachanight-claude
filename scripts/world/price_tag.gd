extends Node2D
## A machine's price as part of the scene: a little roof sign, a navy board on
## two short legs that stands on top of the machine, with a gold coin and the
## amount painted on it. It is deliberately not a paper tag: the capsule
## machines already wear a numbered one. The node's origin is the bottom
## centre, where the legs meet the machine; the store wobbles it around there.

const C_INK: Color = Color("#161320")
const C_BOARD: Color = Color("#1f3a8a")
const C_BOARD_LIGHT: Color = Color("#2f7de1")
const C_BOARD_DULL: Color = Color("#3b4152")
const C_BOARD_DULL_LIGHT: Color = Color("#4a5160")
const C_TEXT: Color = Color("#fff8e3")
const C_TEXT_DULL: Color = Color("#a9a59a")
const C_STEEL: Color = Color("#8a93a3")
const C_COIN: Color = Color("#f2b632")
const C_COIN_DARK: Color = Color("#c98a1c")
const C_COIN_DULL: Color = Color("#8d8676")

const BOARD_SIZE: Vector2 = Vector2(30.0, 11.0)
## The legs lift the board this far above the origin and stand this far apart.
const LEG_HEIGHT: float = 3.0
const LEG_SPREAD: float = 9.0
## Centre of the painted coin, relative to the origin.
const COIN_CENTRE: Vector2 = Vector2(-10.0, -9.0)
const COIN_RADIUS: float = 3.0
## Where the amount is written, relative to the origin.
const TEXT_AREA: Rect2 = Rect2(-5.0, -13.0, 18.0, 9.0)
const FONT_SIZE: int = 22
## Text is drawn at screen resolution and scaled down into the pixel world.
const TEXT_SCALE: float = 1.0 / 3.0

## The amount shown, without the coin ("50", "250K").
var text: String = "":
	set(value):
		text = value
		_fit_text()

## False greys the board out: the player cannot pay this yet.
var affordable: bool = true:
	set(value):
		if affordable != value:
			affordable = value
			_refresh()

var _label: Label


func _ready() -> void:
	_label = Label.new()
	_label.add_theme_font_size_override("font_size", FONT_SIZE)
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	add_child(_label)
	_refresh()
	_fit_text()


## World position of the coin painted on the board, for a twinkle on it.
func coin_point() -> Vector2:
	return global_position + COIN_CENTRE


## The board's outline in world coordinates, standing straight.
func board_rect() -> Rect2:
	return Rect2(global_position + Vector2(-BOARD_SIZE.x / 2.0, -LEG_HEIGHT - BOARD_SIZE.y), BOARD_SIZE)


func _draw() -> void:
	for side in [-1.0, 1.0]:
		draw_rect(Rect2(side * LEG_SPREAD - 1.5, -LEG_HEIGHT - 1.0, 3.0, LEG_HEIGHT + 1.0), C_INK)
		draw_rect(Rect2(side * LEG_SPREAD - 0.5, -LEG_HEIGHT - 1.0, 1.0, LEG_HEIGHT + 1.0), C_STEEL)
	var board: Rect2 = Rect2(Vector2(-BOARD_SIZE.x / 2.0, -LEG_HEIGHT - BOARD_SIZE.y), BOARD_SIZE)
	draw_rect(board, C_INK)
	draw_rect(board.grow(-1.0), C_BOARD if affordable else C_BOARD_DULL)
	# One lighter line along the top edge: the single highlight shade.
	draw_rect(Rect2(board.position + Vector2(1.0, 1.0), Vector2(BOARD_SIZE.x - 2.0, 1.0)), C_BOARD_LIGHT if affordable else C_BOARD_DULL_LIGHT)
	# The coin: an ink ring, a gold face, a shaded rim and a glint.
	var coin: Vector2 = COIN_CENTRE - Vector2(0.5, 0.5)
	var reach: float = COIN_RADIUS
	draw_rect(Rect2(coin + Vector2(-reach + 1.0, -reach), Vector2(reach * 2.0 - 1.0, reach * 2.0 + 1.0)), C_INK)
	draw_rect(Rect2(coin + Vector2(-reach, -reach + 1.0), Vector2(reach * 2.0 + 1.0, reach * 2.0 - 1.0)), C_INK)
	draw_rect(Rect2(coin + Vector2(-reach + 1.0, -reach + 1.0), Vector2(reach * 2.0 - 1.0, reach * 2.0 - 1.0)), C_COIN if affordable else C_COIN_DULL)
	if affordable:
		draw_rect(Rect2(coin + Vector2(-reach + 1.0, reach - 1.0), Vector2(reach * 2.0 - 1.0, 1.0)), C_COIN_DARK)
		draw_rect(Rect2(coin + Vector2(-1.0, -2.0), Vector2(1.0, 1.0)), C_TEXT)


func _refresh() -> void:
	queue_redraw()
	if _label != null:
		_label.add_theme_color_override("font_color", C_TEXT if affordable else C_TEXT_DULL)


## Writes the amount centred in its area, narrowed when it is too long to fit.
func _fit_text() -> void:
	if _label == null:
		return
	_label.text = text
	var wanted: Vector2 = _label.get_minimum_size()
	_label.size = wanted
	var fit: float = TEXT_SCALE
	if wanted.x * fit > TEXT_AREA.size.x:
		fit = TEXT_AREA.size.x / wanted.x
	_label.scale = Vector2(fit, TEXT_SCALE)
	_label.position = TEXT_AREA.position + (TEXT_AREA.size - wanted * _label.scale) / 2.0
