extends Node2D
## Anything the player can stand next to and use with the interact key.

var prompt_fn: Callable = Callable()
var interact_fn: Callable = Callable()
## How far from its use point, in world pixels, the player can use it.
var reach: float = 16.0
## Where the player stands to use it, relative to this node. Things on the
## back wall are used from the floor in front of them.
var use_offset: Vector2 = Vector2.ZERO


## The spot on the floor, in world coordinates, the reach is measured from.
func use_point() -> Vector2:
	return global_position + use_offset


func get_prompt() -> String:
	if prompt_fn.is_valid():
		return str(prompt_fn.call())
	return ""


func interact() -> void:
	if interact_fn.is_valid():
		interact_fn.call()
