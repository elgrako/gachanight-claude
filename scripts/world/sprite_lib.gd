extends RefCounted
## Loads the pixel-art sprites and animation sheets. A missing file becomes a
## flat placeholder of the expected size, so the game still runs without it.

const SPRITE_DIR: String = "res://assets/sprites/"
## Folders (under assets/sprites) that carry an `anims.json`; sheet paths in a
## manifest are relative to its own folder. Animation names are global.
const ANIM_FOLDERS: Array = ["anim", "machines", "bases", "figures", "peseta"]
const MANIFEST_FILE: String = "anims.json"

## Redrawn textures have this many sprite pixels per world pixel, for finer
## detail, and are shown at 1 / ART_SCALE; art still waiting to be redrawn is
## authored at world size and shown as it is (see `density`). World
## coordinates, layout and collisions therefore never depend on the art's
## resolution: sizes passed to the helpers below are WORLD sizes unless a name
## or comment says otherwise.
const ART_SCALE: float = 1.5
## Scale of every node that shows a texture in the world.
const DRAW_SCALE: Vector2 = Vector2(1.0 / ART_SCALE, 1.0 / ART_SCALE)

## In SPRITE pixels of art drawn at ART_SCALE: a figure is 60 x 60 with its
## feet on the bottom row; it stands with its bottom centre on BASE_STAND of
## the 84 x 45 base frame of its rarity.
const FIGURE_SIZE: Vector2i = Vector2i(60, 60)
const BASE_SIZE: Vector2i = Vector2i(84, 45)
const BASE_STAND: Vector2i = Vector2i(42, 18)
## The same in WORLD pixels, which is also the size of the art that has not
## been redrawn at ART_SCALE yet (see `density`).
const FIGURE_WORLD: Vector2i = Vector2i(40, 40)
const BASE_WORLD: Vector2i = Vector2i(56, 30)
const BASE_STAND_WORLD: Vector2i = Vector2i(28, 12)
## Fallback colours of the bases, as in data/rarities.json, used only while
## the base art is missing.
const BASE_COLORS: Dictionary = {
	"common": Color("#c9bb9f"),
	"uncommon": Color("#c9bb9f"),
	"rare": Color("#979a72"),
	"epic": Color("#979a72"),
	"legendary": Color("#d0b870"),
}
## Animations of the SpriteFrames a figure is shown with: `still` is its static
## picture (used for dark silhouettes), `idle` its little loop, or the same
## still picture while that loop has not been drawn.
const FIGURE_STILL: String = "still"
const FIGURE_IDLE: String = "idle"
## Effects drawn over everything in the world.
const Z_EFFECT: int = 900

static var _manifest: Dictionary = {}
static var _manifest_loaded: bool = false
static var _placeholders: Dictionary = {}


## Sprite pixels per world pixel of a picture `texture_pixels` wide that covers
## `world_pixels` of the world: ART_SCALE for the redrawn art, 1 for the older
## art that is still authored at world size. Both kinds keep their world size.
static func density(texture_pixels: float, world_pixels: float) -> float:
	return ART_SCALE if texture_pixels >= world_pixels * (1.0 + ART_SCALE) / 2.0 else 1.0


## Scale of a node showing a picture of `texture_size` sprite pixels that
## covers `world` pixels of the world.
static func draw_scale(texture_size: Vector2, world: Vector2i) -> Vector2:
	var pixels: float = density(texture_size.x, world.x)
	return Vector2(1.0 / pixels, 1.0 / pixels)


## Sprite pixels a picture needs to cover `world` pixels of the world.
static func art_size(world: Vector2i) -> Vector2i:
	return Vector2i(roundi(world.x * ART_SCALE), roundi(world.y * ART_SCALE))


## World pixels covered by a picture of `art` sprite pixels.
static func world_size(art: Vector2i) -> Vector2i:
	return Vector2i(roundi(art.x / ART_SCALE), roundi(art.y / ART_SCALE))


## A length or a point measured on a picture, in world pixels.
static func to_world(sprite_pixels: float) -> float:
	return sprite_pixels / ART_SCALE


## `path` is relative to assets/sprites, without extension: "props/sofa".
## `fallback_size` is the WORLD size the picture covers; the placeholder is
## made ART_SCALE times larger, like the real art.
static func texture(path: String, fallback_size: Vector2i = Vector2i(16, 16), fallback_color: Color = Color("#b98d5c")) -> Texture2D:
	var full: String = "%s%s.png" % [SPRITE_DIR, path]
	if ResourceLoader.exists(full):
		var loaded: Resource = load(full)
		if loaded is Texture2D:
			return loaded
	return placeholder(art_size(fallback_size), fallback_color)


## A flat picture of `size` SPRITE pixels.
static func placeholder(size: Vector2i, color: Color) -> Texture2D:
	var key: String = "%dx%d%s" % [size.x, size.y, color.to_html()]
	if not _placeholders.has(key):
		var image: Image = Image.create(maxi(size.x, 1), maxi(size.y, 1), false, Image.FORMAT_RGBA8)
		image.fill(color)
		_placeholders[key] = ImageTexture.create_from_image(image)
	return _placeholders[key]


static func has_texture(path: String) -> bool:
	return ResourceLoader.exists("%s%s.png" % [SPRITE_DIR, path])


## A sprite whose origin is the bottom centre of its picture.
static func standing(path: String, fallback_size: Vector2i, fallback_color: Color = Color("#b98d5c")) -> Sprite2D:
	var sprite: Sprite2D = Sprite2D.new()
	sprite.centered = false
	set_standing_texture(sprite, texture(path, fallback_size, fallback_color))
	sprite.scale = draw_scale(sprite.texture.get_size(), fallback_size)
	return sprite


## Swaps the picture of a standing sprite and keeps its bottom centre in place,
## whatever the size of the new picture.
static func set_standing_texture(sprite: Sprite2D, new_texture: Texture2D) -> void:
	sprite.texture = new_texture
	sprite.offset = Vector2(-floorf(new_texture.get_width() / 2.0), -new_texture.get_height())


## A rectangle of the world filled with a repeated tile. The control is made
## as many times larger as the tile is finer than the world and scaled back,
## so the tile keeps its world size.
static func tiled(path: String, area: Rect2, fallback_size: Vector2i, fallback_color: Color) -> TextureRect:
	var rect: TextureRect = TextureRect.new()
	rect.texture = texture(path, fallback_size, fallback_color)
	rect.stretch_mode = TextureRect.STRETCH_TILE
	rect.position = area.position
	rect.scale = draw_scale(rect.texture.get_size(), fallback_size)
	rect.size = area.size / rect.scale
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return rect


## Every manifest merged into one table. Each entry also remembers its folder.
static func manifest() -> Dictionary:
	if not _manifest_loaded:
		_manifest_loaded = true
		_manifest = {}
		for folder in ANIM_FOLDERS:
			var path: String = "%s%s/%s" % [SPRITE_DIR, folder, MANIFEST_FILE]
			if not FileAccess.file_exists(path):
				continue
			var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
			if not parsed is Dictionary:
				continue
			for anim_name in parsed:
				var entry: Variant = parsed[anim_name]
				# A half-written manifest must not break the game: skip bad rows.
				if not entry is Dictionary or not _is_valid_entry(entry):
					continue
				var info: Dictionary = entry.duplicate()
				info["folder"] = folder
				_manifest[str(anim_name)] = info
	return _manifest


static func _is_valid_entry(entry: Dictionary) -> bool:
	for key in ["file", "frame_w", "frame_h", "frames"]:
		if not entry.has(key):
			return false
	return int(entry["frame_w"]) > 0 and int(entry["frame_h"]) > 0 and int(entry["frames"]) > 0


## Forgets the manifests, so the next call reads them from disk again.
static func reload_manifest() -> void:
	_manifest_loaded = false


static func animation_info(anim_name: String) -> Dictionary:
	return manifest().get(anim_name, {})


## True when the animation is in a manifest and its sheet is imported.
static func has_animation(anim_name: String) -> bool:
	var info: Dictionary = animation_info(anim_name)
	return not info.is_empty() and has_texture(_sheet_path(info))


static func _sheet_path(info: Dictionary) -> String:
	return "%s/%s" % [info["folder"], str(info["file"]).get_basename()]


## Seconds one pass of the animation takes; 0 when it is unknown.
static func animation_length(anim_name: String) -> float:
	var info: Dictionary = animation_info(anim_name)
	if info.is_empty():
		return 0.0
	return float(info["frames"]) / maxf(float(info.get("fps", 8)), 1.0)


static func frame_size(anim_name: String, fallback_size: Vector2i) -> Vector2i:
	var info: Dictionary = animation_info(anim_name)
	if info.is_empty():
		return fallback_size
	return Vector2i(int(info["frame_w"]), int(info["frame_h"]))


## SpriteFrames holding the named animations from the manifests. A missing
## animation becomes one frame: `fallback_texture` when given, else a flat
## placeholder covering `fallback_size` world pixels.
static func frames(anim_names: Array, fallback_size: Vector2i, fallback_color: Color = Color("#74806c"), fallback_texture: Texture2D = null) -> SpriteFrames:
	var result: SpriteFrames = SpriteFrames.new()
	if result.has_animation("default"):
		result.remove_animation("default")
	for anim_name in anim_names:
		result.add_animation(anim_name)
		var info: Dictionary = animation_info(anim_name)
		var count: int = 0
		var sheet: Texture2D = null
		var frame_w: int = 0
		var frame_h: int = 0
		if has_animation(anim_name):
			sheet = texture(_sheet_path(info))
			frame_w = int(info["frame_w"])
			frame_h = int(info["frame_h"])
			# A sheet being redrawn may be shorter than its manifest says.
			count = mini(int(info["frames"]), sheet.get_width() / frame_w)
			if sheet.get_height() < frame_h:
				count = 0
		if count <= 0:
			result.set_animation_loop(anim_name, true)
			result.add_frame(anim_name, fallback_texture if fallback_texture != null else placeholder(art_size(fallback_size), fallback_color))
			continue
		result.set_animation_speed(anim_name, float(info.get("fps", 8)))
		result.set_animation_loop(anim_name, bool(info.get("loop", true)))
		for index in range(count):
			var atlas: AtlasTexture = AtlasTexture.new()
			atlas.atlas = sheet
			atlas.region = Rect2(index * frame_w, 0, frame_w, frame_h)
			result.add_frame(anim_name, atlas)
	return result


## An animated sprite whose origin is the bottom centre of its frame.
static func animated(anim_names: Array, fallback_size: Vector2i, fallback_color: Color = Color("#74806c"), fallback_texture: Texture2D = null) -> AnimatedSprite2D:
	var sprite: AnimatedSprite2D = AnimatedSprite2D.new()
	sprite.sprite_frames = frames(anim_names, fallback_size, fallback_color, fallback_texture)
	sprite.centered = false
	var first: Texture2D = sprite.sprite_frames.get_frame_texture(anim_names[0], 0)
	sprite.scale = draw_scale(first.get_size(), fallback_size)
	sprite.offset = Vector2(-floorf(first.get_width() / 2.0), -first.get_height())
	sprite.animation = anim_names[0]
	return sprite


## Name of a figure's idle loop in `figures/anims.json`.
static func figure_idle_name(figure_id: String) -> String:
	return "fig_%s_idle" % figure_id


## True when the figure's idle loop is drawn, imported and of the figure size.
static func has_figure_idle(figure_id: String) -> bool:
	var anim_name: String = figure_idle_name(figure_id)
	return has_animation(anim_name) and frame_size(anim_name, Vector2i.ZERO) in [FIGURE_SIZE, FIGURE_WORLD]


## Frames of a figure: FIGURE_STILL (one frame, the static sprite) and
## FIGURE_IDLE (its loop, or the static sprite again when there is none).
static func figure_frames(figure_id: String, fallback_color: Color = Color("#b98d5c")) -> SpriteFrames:
	var figure_world: Vector2i = FIGURE_WORLD
	var still: Texture2D = texture("figures/%s" % figure_id, figure_world, fallback_color)
	var anim_name: String = figure_idle_name(figure_id)
	# An unknown name makes `frames` fall back to the still picture.
	var result: SpriteFrames = frames([anim_name if has_figure_idle(figure_id) else "none"], figure_world, fallback_color, still)
	result.rename_animation(result.get_animation_names()[0], FIGURE_IDLE)
	result.set_animation_loop(FIGURE_IDLE, true)
	result.add_animation(FIGURE_STILL)
	result.add_frame(FIGURE_STILL, still)
	return result


## A figure standing with its feet on its origin, showing its still picture.
static func figure_sprite(figure_id: String) -> AnimatedSprite2D:
	var sprite: AnimatedSprite2D = AnimatedSprite2D.new()
	sprite.sprite_frames = figure_frames(figure_id)
	sprite.centered = false
	var still: Texture2D = sprite.sprite_frames.get_frame_texture(FIGURE_STILL, 0)
	sprite.scale = draw_scale(still.get_size(), FIGURE_WORLD)
	sprite.offset = Vector2(-floorf(still.get_width() / 2.0), -still.get_height())
	sprite.animation = FIGURE_STILL
	return sprite


## The looping base of a rarity, origin at the top-left corner of its frame.
## Without art it is a flat slab of the rarity colour. Its scale shows it at
## world size (BASE_WORLD); the UI and the gallery multiply that by their own.
static func base_sprite(rarity_id: String) -> AnimatedSprite2D:
	var anim_name: String = "base_%s" % rarity_id
	var sprite: AnimatedSprite2D = AnimatedSprite2D.new()
	sprite.sprite_frames = frames([anim_name], BASE_WORLD, BASE_COLORS.get(rarity_id, Color.GRAY))
	sprite.centered = false
	sprite.scale = draw_scale(sprite.sprite_frames.get_frame_texture(anim_name, 0).get_size(), BASE_WORLD)
	sprite.animation = anim_name
	sprite.play(anim_name)
	return sprite


## A flat ellipse centred on its origin: drop shadows and pools of light.
static func ellipse(radius: Vector2, color: Color, points: int = 16) -> Polygon2D:
	var shape: Polygon2D = Polygon2D.new()
	var outline: PackedVector2Array = PackedVector2Array()
	for index in range(points):
		var angle: float = TAU * index / points
		outline.append(Vector2(cos(angle) * radius.x, sin(angle) * radius.y))
	shape.polygon = outline
	shape.color = color
	return shape


## Plays a non-looping effect once at a world position and frees it. Returns
## null, and shows nothing, when the effect's art is missing.
static func burst(parent: Node, anim_name: String, at: Vector2, fallback_size: Vector2i, tint: Color = Color.WHITE) -> AnimatedSprite2D:
	if not has_animation(anim_name):
		return null
	var sprite: AnimatedSprite2D = AnimatedSprite2D.new()
	sprite.sprite_frames = frames([anim_name], fallback_size, Color(1, 1, 1, 0.6))
	sprite.sprite_frames.set_animation_loop(anim_name, false)
	sprite.position = at
	sprite.scale = draw_scale(sprite.sprite_frames.get_frame_texture(anim_name, 0).get_size(), fallback_size)
	sprite.modulate = tint
	sprite.z_as_relative = false
	sprite.z_index = Z_EFFECT
	parent.add_child(sprite)
	sprite.animation_finished.connect(sprite.queue_free)
	sprite.play(anim_name)
	return sprite
