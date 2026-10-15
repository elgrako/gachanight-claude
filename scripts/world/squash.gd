extends RefCounted
## Squash and stretch at constant volume, texel perfect when asked.
##
## `amount` > 0 squashes (shorter and wider), < 0 stretches (taller and
## thinner); width times height stays 1, as the twelve principles ask. Given
## the picture's size in art pixels, both factors are rounded so the picture
## gains or loses whole art pixels only, never a fraction: on nearest-filtered
## pixel art a fraction gives uneven pixels ("mixels"). High-density art is
## drawn smoothed and passes no size.
##
## Everything runs on tweens, so it takes the same time at any frame rate.
## See docs/art/animation-techniques.md.


## The scale factors for `amount`.
static func shape(amount: float, art_size: Vector2 = Vector2.ZERO) -> Vector2:
	var tall: float = clampf(1.0 - amount, 0.2, 2.0)
	var wide: float = 1.0 / tall
	if art_size.x > 0.0 and art_size.y > 0.0:
		tall = roundf(art_size.y * tall) / art_size.y
		wide = roundf(art_size.x * wide) / art_size.x
	return Vector2(wide, tall)


## Squashes (or stretches) `node` by `amount` and lets it spring back past
## rest the other way before settling: the hit, the rebound, the rest, in
## `seconds`. `base` is the node's scale at rest. Stops any bounce already
## running on the same node.
static func bounce(node: CanvasItem, base: Vector2, amount: float, seconds: float, art_size: Vector2 = Vector2.ZERO) -> Tween:
	if node.has_meta("squash_tween"):
		var running: Tween = node.get_meta("squash_tween")
		if running != null and running.is_valid():
			running.kill()
	var apply: Callable = func(value: float) -> void: node.scale = base * shape(value, art_size)
	var tween: Tween = node.create_tween()
	tween.tween_method(apply, 0.0, amount, seconds * 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_method(apply, amount, -amount * 0.4, seconds * 0.35).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_method(apply, -amount * 0.4, 0.0, seconds * 0.4).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tween.tween_callback(func() -> void: node.scale = base)
	node.set_meta("squash_tween", tween)
	return tween
