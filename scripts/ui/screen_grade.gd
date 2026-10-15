extends CanvasLayer
## The look of the whole game: a light pass over the finished picture, above
## the world and every panel. The art is drawn on a fixed, muted palette, so
## this pass leaves its colours alone and only adds what an old medium adds.
## It never takes mouse input.
##
## Several looks are kept side by side to try them: F3 steps through them
## while the game runs, and the name of the one showing appears for a moment.
## None of them is strong; they differ in which medium they recall.

const SWITCH_KEY: Key = KEY_F3
## Shown first: the old analogue picture (owner, 2026-10-15).
const START_LOOK: int = 5
## How long the name of a look stays on screen.
const NAME_SECONDS: float = 2.0
## Above every other layer, the fade to black included.
const LAYER: int = 100

## What every look starts from; each look only lists what it changes.
##   saturation      1.0 is the art's own colour, 0.0 is grey
##   tone            how far colours are pulled to a sepia print of themselves
##   vignette        share of light the corners lose; `vignette_start` is how
##                   far from the centre (0) to a corner (1) that begins
##   grain           brightness fine grain adds or takes; `grain_fps` is how
##                   many new patterns a second (0 holds it still, like paper)
##   scratch, dust   film flaws, now and then
##   flicker         how much the whole picture's brightness flutters
##   weave           pixels the picture drifts up and down, as film in a gate
##   scanline        how dark the lines of a picture tube are
##   glow            light that bleeds out of the bright parts
##   paper           unevenness of the paper under a print
##   corner          radius of the rounded corners of the picture, in pixels
##   curve           how much the picture bulges, as on a rounded tube
##   roll            how dark the slow band is that rolls down the picture
##   bleed           screen pixels the red and the blue drift apart, as on old
##                   analogue colour
const BASE: Dictionary = {
	"saturation": 1.0, "tone": 0.1, "vignette": 0.0, "vignette_start": 0.3,
	"grain": 0.0, "grain_fps": 14.0, "scratch": 0.0, "dust": 0.0,
	"flicker": 0.0, "weave": 0.0, "scanline": 0.0, "glow": 0.0, "paper": 0.0, "corner": 0.0,
	"curve": 0.0, "roll": 0.0, "bleed": 0.0,
}
const LOOKS: Array = [
	["No filter", {"tone": 0.0}],
	# What the game had: grain, dark corners, a scratch or a speck now and then.
	["Old reel", {"vignette": 0.5, "grain": 0.035, "scratch": 0.07, "dust": 0.16}],
	# The same reel in a projector: it breathes, drifts a hair and glows.
	["Projector", {"vignette": 0.45, "grain": 0.04, "scratch": 0.07, "dust": 0.16, "flicker": 0.025, "weave": 0.6, "glow": 0.1, "corner": 26.0}],
	# A small picture tube: faint lines, a soft glow, rounded glass.
	["Picture tube", {"vignette": 0.3, "vignette_start": 0.5, "grain": 0.012, "scanline": 0.1, "glow": 0.14, "corner": 34.0}],
	# A printed page: still grain and blotchy paper, nothing moves.
	["Printed page", {"tone": 0.16, "vignette": 0.25, "vignette_start": 0.45, "grain": 0.03, "grain_fps": 0.0, "paper": 0.07}],
	# An old analogue picture, as Cuphead or MOUSE: P.I. For Hire do it: the
	# colours stay, the picture stays flat (no bulging tube, owner 2026-10-15),
	# and the age is in the grain, a little colour bleeding at the edges,
	# flicker, a hair of drift, dark corners, faint lines and the odd speck.
	["Old analogue", {"saturation": 1.1, "tone": 0.06, "vignette": 0.4, "vignette_start": 0.4, "grain": 0.045,
		"scratch": 0.05, "dust": 0.12, "flicker": 0.025, "weave": 0.4, "scanline": 0.035, "glow": 0.08, "bleed": 1.0}],
]

const TONE_COLOR: Color = Color(1.1, 0.96, 0.76)
const SHADER_CODE: String = """
shader_type canvas_item;
uniform sampler2D screen : hint_screen_texture, filter_nearest;
uniform float saturation = 1.0;
uniform float tone = 0.1;
uniform vec3 tone_colour = vec3(1.1, 0.96, 0.76);
uniform float vignette = 0.0;
uniform float vignette_start = 0.3;
uniform float grain = 0.0;
uniform float grain_fps = 14.0;
uniform float scratch = 0.0;
uniform float dust = 0.0;
uniform float flicker = 0.0;
uniform float weave = 0.0;
uniform float scanline = 0.0;
uniform float glow = 0.0;
uniform float paper = 0.0;
uniform float corner = 0.0;
uniform float curve = 0.0;
uniform float roll = 0.0;
uniform float bleed = 0.0;

float hash(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

void fragment() {
	vec2 pixel = FRAGCOORD.xy;
	vec2 size = 1.0 / SCREEN_PIXEL_SIZE;
	// Small tick numbers keep the hash well spread on every GPU.
	float reel_tick = mod(floor(TIME * 12.0), 251.0);
	// The tube bulges: the picture is pulled in towards the edges.
	vec2 bent = SCREEN_UV - 0.5;
	bent *= 1.0 + curve * dot(bent, bent) * 4.0;
	vec2 glass = bent / (1.0 + curve) + 0.5;
	vec2 uv = glass + vec2(0.0, (hash(vec2(reel_tick, 4.2)) - 0.5) * weave * SCREEN_PIXEL_SIZE.y);
	vec3 colour = texture(screen, uv).rgb;
	// Old analogue colour: red and blue do not quite sit on the picture.
	vec2 drift = vec2(bleed * SCREEN_PIXEL_SIZE.x, 0.0);
	colour.r = mix(colour.r, texture(screen, uv + drift).r, step(0.01, bleed));
	colour.b = mix(colour.b, texture(screen, uv - drift).b, step(0.01, bleed));

	// Light bleeding out of the bright parts; the picture itself stays sharp.
	vec3 spill = vec3(0.0);
	for (int index = 0; index < 4; index++) {
		vec2 away = vec2(float(index % 2) * 2.0 - 1.0, float(index / 2) * 2.0 - 1.0) * 2.5 * SCREEN_PIXEL_SIZE;
		spill += max(texture(screen, uv + away).rgb - 0.55, 0.0);
	}
	colour += spill * 0.25 * glow * 4.0;

	float grey = dot(colour, vec3(0.299, 0.587, 0.114));
	colour = mix(vec3(grey), colour, saturation);
	colour = mix(colour, grey * tone_colour, tone);

	float grain_tick = mod(floor(TIME * grain_fps), 251.0);
	colour += (hash(floor(pixel / 2.0) + grain_tick * vec2(17.0, 31.0)) - 0.5) * grain;
	colour *= 1.0 + (hash(vec2(reel_tick, 1.3)) - 0.5) * 2.0 * flicker;

	// Paper: fine tooth and slow blotches, both still.
	vec2 blot = pixel / 90.0;
	vec2 cell = floor(blot);
	vec2 within = smoothstep(0.0, 1.0, fract(blot));
	float blotch = mix(mix(hash(cell), hash(cell + vec2(1.0, 0.0)), within.x), mix(hash(cell + vec2(0.0, 1.0)), hash(cell + vec2(1.0, 1.0)), within.x), within.y);
	colour *= 1.0 - paper * (0.5 * hash(floor(pixel / 2.0) + 7.0) + blotch);

	colour *= 1.0 - scanline * (0.5 + 0.5 * sin(pixel.y * 3.14159 * 2.0 / 3.0));

	// A slow dark band rolling down the picture.
	float band = fract(glass.y - TIME * 0.06);
	colour *= 1.0 - roll * smoothstep(0.0, 0.08, band) * (1.0 - smoothstep(0.08, 0.2, band));
	float from_centre = length(SCREEN_UV - 0.5) * 1.41421;
	colour *= 1.0 - vignette * smoothstep(vignette_start, 1.0, from_centre);

	float flaw_tick = mod(floor(TIME * 10.0), 509.0);
	for (int lane = 0; lane < 2; lane++) {
		float seed = flaw_tick + float(lane) * 131.0;
		float shown = step(0.98, hash(vec2(seed, 3.7)));
		float line = step(abs(SCREEN_UV.x - hash(vec2(seed, 9.1))), SCREEN_PIXEL_SIZE.x * 0.75);
		// A scratch is not even along its length.
		colour += scratch * shown * line * (0.5 + 0.5 * hash(vec2(floor(pixel.y / 24.0), seed)));
	}
	vec2 dust_cell = floor(pixel / 40.0);
	float speck_here = step(0.9994, hash(dust_cell + flaw_tick * vec2(5.3, 7.9)));
	vec2 centre = (dust_cell + 0.25 + 0.5 * vec2(hash(dust_cell + flaw_tick), hash(dust_cell - flaw_tick))) * 40.0;
	colour -= dust * speck_here * step(length(pixel - centre), 2.4);

	// Rounded corners: black outside the glass or the frame.
	vec2 on_glass = glass * size;
	vec2 inset = max(vec2(corner) - min(on_glass, size - on_glass), 0.0);
	colour *= step(0.0, glass.x) * step(glass.x, 1.0) * step(0.0, glass.y) * step(glass.y, 1.0);
	colour *= 1.0 - smoothstep(corner - 1.5, corner, length(inset)) * step(0.5, corner);

	COLOR = vec4(clamp(colour, 0.0, 1.0), 1.0);
}
"""

## The full-screen rectangle carrying the shader.
var rect: ColorRect
## Index in LOOKS of the look showing.
var look: int = START_LOOK

var _material: ShaderMaterial
var _name: Label
var _name_left: float = 0.0


func _ready() -> void:
	layer = LAYER
	var shader: Shader = Shader.new()
	shader.code = SHADER_CODE
	_material = ShaderMaterial.new()
	_material.shader = shader
	_material.set_shader_parameter("tone_colour", Vector3(TONE_COLOR.r, TONE_COLOR.g, TONE_COLOR.b))
	rect = ColorRect.new()
	rect.material = _material
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(rect)
	rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_name = Label.new()
	_name.add_theme_font_size_override("font_size", 18)
	_name.add_theme_color_override("font_color", Color("#e3d9c6"))
	_name.add_theme_color_override("font_outline_color", Color("#0e0d0c"))
	_name.add_theme_constant_override("outline_size", 6)
	_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_name.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_name.visible = false
	add_child(_name)
	_name.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_name.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_name.offset_top = 14.0
	show_look(look, false)


func _process(delta: float) -> void:
	if _name_left > 0.0:
		_name_left -= delta
		_name.visible = _name_left > 0.0


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == SWITCH_KEY:
		show_look((look + 1) % LOOKS.size(), true)


## Switches to the look at `index` of LOOKS; `announce` shows its name.
func show_look(index: int, announce: bool) -> void:
	look = index
	var values: Dictionary = BASE.duplicate()
	values.merge(LOOKS[index][1], true)
	for key in values:
		_material.set_shader_parameter(key, values[key])
	if announce:
		_name.text = "Filter %d/%d: %s   [F3]" % [index + 1, LOOKS.size(), LOOKS[index][0]]
		_name.visible = true
		_name_left = NAME_SECONDS
