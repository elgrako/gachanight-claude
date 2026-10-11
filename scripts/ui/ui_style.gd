extends RefCounted
## Shared look for the UI: hard-edged pixel panels in the store palette.

const INK: Color = Color("#1d2a44")
const CREAM: Color = Color("#f4ecd8")
const CORAL: Color = Color("#ef7a6d")
const MINT: Color = Color("#7ec8a4")
const MUSTARD: Color = Color("#e3b44c")
const TEAL: Color = Color("#4f9ea3")
const MUTED: Color = Color("#6f6a5c")


## `radius` is kept for callers but ignored: pixel panels have square corners
## and a hard drop shadow.
static func box(background: Color, border: Color = INK, border_width: int = 3, _radius: int = 0, margin: int = 16) -> StyleBoxFlat:
	var style: StyleBoxFlat = StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = border
	style.set_border_width_all(maxi(border_width, 4) if border_width > 2 else border_width)
	style.anti_aliasing = false
	style.shadow_color = Color(INK, 0.55)
	style.shadow_size = 1
	style.shadow_offset = Vector2(4, 4)
	style.set_content_margin_all(margin)
	return style


static func style_panel(panel: PanelContainer) -> void:
	panel.add_theme_stylebox_override("panel", box(CREAM))


static func label(text: String, size: int = 18, color: Color = INK) -> Label:
	var node: Label = Label.new()
	node.text = text
	node.add_theme_font_size_override("font_size", size)
	node.add_theme_color_override("font_color", color)
	return node


static func button(text: String, background: Color = MINT) -> Button:
	var node: Button = Button.new()
	node.text = text
	node.custom_minimum_size = Vector2(150, 44)
	node.add_theme_font_size_override("font_size", 18)
	for state in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		node.add_theme_color_override(state, INK)
	node.add_theme_color_override("font_disabled_color", MUTED)
	node.add_theme_stylebox_override("normal", box(background, INK, 3, 8, 10))
	node.add_theme_stylebox_override("hover", box(background.lightened(0.2), INK, 3, 8, 10))
	node.add_theme_stylebox_override("pressed", box(background.darkened(0.15), INK, 3, 8, 10))
	node.add_theme_stylebox_override("focus", box(background.lightened(0.2), INK, 4, 8, 10))
	node.add_theme_stylebox_override("disabled", box(Color("#d6cfbd"), MUTED, 3, 8, 10))
	return node
