extends Node2D
## Anything the player can stand next to and use with the interact key.

var prompt_fn: Callable = Callable()
var interact_fn: Callable = Callable()
## How far to each side of its position, in world pixels, the player can use it.
var reach: float = 16.0


func get_prompt() -> String:
	if prompt_fn.is_valid():
		return str(prompt_fn.call())
	return ""


func interact() -> void:
	if interact_fn.is_valid():
		interact_fn.call()
