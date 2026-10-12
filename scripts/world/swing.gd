extends RefCounted
## A damped pendulum for things that hang (lamps, lanterns, price boards): a
## kick sets it swinging and it comes back to rest by itself.

## Pull back towards rest and loss of speed, per second.
const STIFFNESS: float = 34.0
const DAMPING: float = 2.6
const MAX_ANGLE: float = 0.4
## Long frames are cut into steps no longer than this, so it never blows up.
const MAX_STEP: float = 1.0 / 30.0
## Below these it is at rest: nothing left to see.
const REST_ANGLE: float = 0.002
const REST_SPEED: float = 0.01

## Radians away from hanging straight down.
var angle: float = 0.0
var velocity: float = 0.0


## Pushes it sideways; `amount` is radians per second.
func kick(amount: float) -> void:
	velocity += amount


## Advances the swing and returns the new angle.
func step(delta: float) -> float:
	if absf(angle) < REST_ANGLE and absf(velocity) < REST_SPEED:
		angle = 0.0
		velocity = 0.0
		return 0.0
	var left: float = minf(delta, 0.25)
	while left > 0.0:
		var slice: float = minf(left, MAX_STEP)
		left -= slice
		velocity += (-STIFFNESS * angle - DAMPING * velocity) * slice
		angle = clampf(angle + velocity * slice, -MAX_ANGLE, MAX_ANGLE)
	return angle
