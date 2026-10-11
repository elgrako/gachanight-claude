extends RefCounted
## Loads the pixel-art sprites and animation sheets. A missing file becomes a
## flat placeholder of the expected size, so the game still runs without it.

const SPRITE_DIR: String = "res://assets/sprites/"
const ANIM_MANIFEST: String = "res://assets/sprites/anim/anims.json"

static var _manifest: Dictionary = {}
static var _manifest_loaded: bool = false
static var _placeholders: Dictionary = {}


## `path` is relative to assets/sprites, without extension: "props/sofa".
static func texture(path: String, fallback_size: Vector2i = Vector2i(16, 16), fallback_color: Color = Color("#ef7a6d")) -> Texture2D:
	var full: String = "%s%s.png" % [SPRITE_DIR, path]
	if ResourceLoader.exists(full):
		return load(full)
	var key: String = "%dx%d%s" % [fallback_size.x, fallback_size.y, fallback_color.to_html()]
	if not _placeholders.has(key):
		var image: Image = Image.create(fallback_size.x, fallback_size.y, false, Image.FORMAT_RGBA8)
		image.fill(fallback_color)
		_placeholders[key] = ImageTexture.create_from_image(image)
	return _placeholders[key]


static func has_texture(path: String) -> bool:
	return ResourceLoader.exists("%s%s.png" % [SPRITE_DIR, path])


## A sprite whose origin is the bottom centre of its picture.
static func standing(path: String, fallback_size: Vector2i, fallback_color: Color = Color("#ef7a6d")) -> Sprite2D:
	var sprite: Sprite2D = Sprite2D.new()
	sprite.texture = texture(path, fallback_size, fallback_color)
	sprite.centered = false
	sprite.offset = Vector2(-sprite.texture.get_width() / 2.0, -sprite.texture.get_height())
	return sprite


static func manifest() -> Dictionary:
	if not _manifest_loaded:
		_manifest_loaded = true
		if FileAccess.file_exists(ANIM_MANIFEST):
			var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(ANIM_MANIFEST))
			if parsed is Dictionary:
				_manifest = parsed
	return _manifest


static func animation_info(anim_name: String) -> Dictionary:
	return manifest().get(anim_name, {})


## Seconds one pass of the animation takes; 0 when it is unknown.
static func animation_length(anim_name: String) -> float:
	var info: Dictionary = animation_info(anim_name)
	if info.is_empty():
		return 0.0
	return float(info["frames"]) / maxf(float(info["fps"]), 1.0)


## SpriteFrames holding the named animations from the manifest. `fallbacks`
## gives the frame size used for a placeholder when a sheet is missing.
static func frames(anim_names: Array, fallback_size: Vector2i, fallback_color: Color = Color("#4f9ea3")) -> SpriteFrames:
	var result: SpriteFrames = SpriteFrames.new()
	if result.has_animation("default"):
		result.remove_animation("default")
	for anim_name in anim_names:
		result.add_animation(anim_name)
		var info: Dictionary = animation_info(anim_name)
		var sheet_path: String = "anim/%s" % str(info.get("file", "")).get_basename()
		if info.is_empty() or not has_texture(sheet_path):
			result.set_animation_loop(anim_name, true)
			result.add_frame(anim_name, texture("anim/_missing_%s" % anim_name, fallback_size, fallback_color))
			continue
		var sheet: Texture2D = texture(sheet_path)
		var frame_w: int = int(info["frame_w"])
		var frame_h: int = int(info["frame_h"])
		result.set_animation_speed(anim_name, float(info.get("fps", 8)))
		result.set_animation_loop(anim_name, bool(info.get("loop", true)))
		for index in range(int(info["frames"])):
			var atlas: AtlasTexture = AtlasTexture.new()
			atlas.atlas = sheet
			atlas.region = Rect2(index * frame_w, 0, frame_w, frame_h)
			result.add_frame(anim_name, atlas)
	return result


## An animated sprite whose origin is the bottom centre of its frame.
static func animated(anim_names: Array, fallback_size: Vector2i, fallback_color: Color = Color("#4f9ea3")) -> AnimatedSprite2D:
	var sprite: AnimatedSprite2D = AnimatedSprite2D.new()
	sprite.sprite_frames = frames(anim_names, fallback_size, fallback_color)
	sprite.centered = false
	var first: Texture2D = sprite.sprite_frames.get_frame_texture(anim_names[0], 0)
	sprite.offset = Vector2(-first.get_width() / 2.0, -first.get_height())
	sprite.animation = anim_names[0]
	return sprite


## Plays a non-looping effect once at a world position and frees it.
static func burst(parent: Node, anim_name: String, at: Vector2, fallback_size: Vector2i, tint: Color = Color.WHITE) -> AnimatedSprite2D:
	var sprite: AnimatedSprite2D = AnimatedSprite2D.new()
	sprite.sprite_frames = frames([anim_name], fallback_size, Color(1, 1, 1, 0.6))
	sprite.sprite_frames.set_animation_loop(anim_name, false)
	sprite.position = at
	sprite.modulate = tint
	sprite.z_index = 20
	parent.add_child(sprite)
	sprite.animation_finished.connect(sprite.queue_free)
	sprite.play(anim_name)
	return sprite
