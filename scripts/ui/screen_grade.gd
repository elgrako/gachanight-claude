extends CanvasLayer
## The look of the whole game: an old cartoon reel. The art is already drawn
## in sepia, so this pass keeps most of its colour and only adds what film
## adds: a light warm toning, darker corners, fine grain that changes every
## frame of the reel, and now and then a scratch or a speck of dust. It sits
## above the world and every panel, never blurs (text must stay crisp) and
## never takes mouse input.

## Switches grain, vignette, toning, scratches and dust off at once; the
## saturation below still applies.
const FILM_ENABLED: bool = true
## 1.0 is full colour, 0.0 is grey.
const SATURATION: float = 0.85
## How far every colour is pulled towards a sepia print of itself (0 to 1),
## and the tint of that print: a grey of brightness 1 becomes this colour.
const TONE_STRENGTH: float = 0.16
const TONE_COLOR: Color = Color(1.1, 0.96, 0.76)
## The corners are darkened by this share; the darkening starts this far from
## the centre (0) towards a corner (1).
const VIGNETTE_STRENGTH: float = 0.5
const VIGNETTE_START: float = 0.3
## Grain: brightness it adds or takes at most, the side of one grain in real
## pixels, and how many new patterns a second (a film reel, not video noise).
const GRAIN_STRENGTH: float = 0.035
const GRAIN_SIZE: float = 2.0
const GRAIN_FPS: float = 14.0
## Scratches and dust change this many times a second.
const FLAW_FPS: float = 10.0
## A vertical scratch: how much it brightens, its width in real pixels, and the
## chance that one of the two possible scratches shows during one flaw frame.
const SCRATCH_STRENGTH: float = 0.07
const SCRATCH_WIDTH: float = 1.5
const SCRATCH_CHANCE: float = 0.02
## Dust specks: how much one darkens, the side of the cell that may hold one
## (real pixels; a speck is a fraction of it) and the chance per cell and
## flaw frame.
const DUST_STRENGTH: float = 0.16
const DUST_CELL: float = 40.0
const DUST_CHANCE: float = 0.0006
## Above every other layer, the fade to black included.
const LAYER: int = 100

const SHADER_CODE: String = """
shader_type canvas_item;
uniform sampler2D screen : hint_screen_texture, filter_nearest;
uniform float film = 1.0;
uniform float saturation = 0.85;
uniform float tone = 0.16;
uniform vec3 tone_colour = vec3(1.1, 0.96, 0.76);
uniform float vignette = 0.26;
uniform float vignette_start = 0.45;
uniform float grain = 0.035;
uniform float grain_size = 2.0;
uniform float grain_fps = 14.0;
uniform float flaw_fps = 10.0;
uniform float scratch = 0.07;
uniform float scratch_width = 1.5;
uniform float scratch_chance = 0.02;
uniform float dust = 0.16;
uniform float dust_cell = 40.0;
uniform float dust_chance = 0.0006;

float hash(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

void fragment() {
	vec3 colour = texture(screen, SCREEN_UV).rgb;
	float grey = dot(colour, vec3(0.299, 0.587, 0.114));
	colour = mix(vec3(grey), colour, saturation);
	colour = mix(colour, grey * tone_colour, tone * film);

	vec2 pixel = FRAGCOORD.xy;
	// Small tick numbers keep the hash well spread on every GPU.
	float grain_tick = mod(floor(TIME * grain_fps), 251.0);
	float noise = hash(floor(pixel / grain_size) + grain_tick * vec2(17.0, 31.0)) - 0.5;
	colour += noise * grain * film;

	float corner = length(SCREEN_UV - 0.5) * 1.41421;
	colour *= 1.0 - vignette * film * smoothstep(vignette_start, 1.0, corner);

	float flaw_tick = mod(floor(TIME * flaw_fps), 509.0);
	for (int lane = 0; lane < 2; lane++) {
		float seed = flaw_tick + float(lane) * 131.0;
		float shown = step(1.0 - scratch_chance, hash(vec2(seed, 3.7)));
		float at = hash(vec2(seed, 9.1));
		float line = step(abs(SCREEN_UV.x - at), SCREEN_PIXEL_SIZE.x * scratch_width * 0.5);
		// A scratch is not even along its length.
		float wear = 0.5 + 0.5 * hash(vec2(floor(pixel.y / 24.0), seed));
		colour += scratch * film * shown * line * wear;
	}

	vec2 cell = floor(pixel / dust_cell);
	float speck_here = step(1.0 - dust_chance, hash(cell + flaw_tick * vec2(5.3, 7.9)));
	vec2 centre = (cell + 0.25 + 0.5 * vec2(hash(cell + flaw_tick), hash(cell - flaw_tick))) * dust_cell;
	float speck = step(length(pixel - centre), dust_cell * 0.06);
	colour -= dust * film * speck_here * speck;

	COLOR = vec4(clamp(colour, 0.0, 1.0), 1.0);
}
"""

## The full-screen rectangle carrying the shader.
var rect: ColorRect


func _ready() -> void:
	layer = LAYER
	var shader: Shader = Shader.new()
	shader.code = SHADER_CODE
	var material: ShaderMaterial = ShaderMaterial.new()
	material.shader = shader
	var values: Dictionary = {
		"film": 1.0 if FILM_ENABLED else 0.0,
		"saturation": SATURATION,
		"tone": TONE_STRENGTH,
		"tone_colour": Vector3(TONE_COLOR.r, TONE_COLOR.g, TONE_COLOR.b),
		"vignette": VIGNETTE_STRENGTH,
		"vignette_start": VIGNETTE_START,
		"grain": GRAIN_STRENGTH,
		"grain_size": GRAIN_SIZE,
		"grain_fps": GRAIN_FPS,
		"flaw_fps": FLAW_FPS,
		"scratch": SCRATCH_STRENGTH,
		"scratch_width": SCRATCH_WIDTH,
		"scratch_chance": SCRATCH_CHANCE,
		"dust": DUST_STRENGTH,
		"dust_cell": DUST_CELL,
		"dust_chance": DUST_CHANCE,
	}
	for key in values:
		material.set_shader_parameter(key, values[key])
	rect = ColorRect.new()
	rect.material = material
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(rect)
	rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
