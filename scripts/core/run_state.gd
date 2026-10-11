extends RefCounted
## State of the current cycle. Saved on exit, reset only by a rebirth.

const FLOOR_COIN_COUNT: int = 3
const ROBOT_MODES: Array = ["collect", "sell_all"]

var coins: int = 0
var power_switch_on: bool = false
var floor_coins_collected: Array = [false, false, false]
var figure_copies_held: Dictionary = {}  # figure_id -> int
var figure_collections_completed: Dictionary = {}  # figure_id -> true
var active_collection_bonuses: Array = []  # figure ids, in activation order
var pending_prestige: int = 0
var pending_prize: Dictionary = {}  # empty when there is none
var next_transaction_id: int = 1
var reception_levels: Dictionary = {}  # reception item id -> int
var robots: Dictionary = {}  # machine_id -> {mode, paused, progress}
var machines_used: Dictionary = {}  # machine_id -> true
var key_owned_this_run: bool = false
var total_spins: int = 0
var run_playtime_seconds: float = 0.0


func copies_held(figure_id: String) -> int:
	return int(figure_copies_held.get(figure_id, 0))


func has_pending_prize() -> bool:
	return not pending_prize.is_empty()


func reception_level(item_id: String) -> int:
	return int(reception_levels.get(item_id, 0))


## Settings of the robots on a machine, created on first use.
func robot_state(machine_id: String) -> Dictionary:
	if not robots.has(machine_id):
		robots[machine_id] = {"mode": "collect", "paused": false, "progress": 0.0}
	return robots[machine_id]


func to_dict() -> Dictionary:
	return {
		"coins": coins,
		"power_switch_on": power_switch_on,
		"floor_coins_collected": floor_coins_collected.duplicate(),
		"figure_copies_held": figure_copies_held.duplicate(),
		"figure_collections_completed": figure_collections_completed.keys(),
		"active_collection_bonuses": active_collection_bonuses.duplicate(),
		"pending_prestige": pending_prestige,
		"pending_prize": pending_prize.duplicate(true),
		"next_transaction_id": next_transaction_id,
		"reception_levels": reception_levels.duplicate(),
		"robots": robots.duplicate(true),
		"machines_used": machines_used.keys(),
		"key_owned_this_run": key_owned_this_run,
		"total_spins": total_spins,
		"run_playtime_seconds": run_playtime_seconds,
	}


func from_dict(source: Dictionary) -> void:
	coins = maxi(0, int(source.get("coins", 0)))
	power_switch_on = bool(source.get("power_switch_on", false))
	floor_coins_collected = [false, false, false]
	var collected: Array = source.get("floor_coins_collected", [])
	for index in range(mini(collected.size(), FLOOR_COIN_COUNT)):
		floor_coins_collected[index] = bool(collected[index])
	figure_copies_held.clear()
	var copies: Dictionary = source.get("figure_copies_held", {})
	for figure_id in copies:
		figure_copies_held[str(figure_id)] = maxi(0, int(copies[figure_id]))
	figure_collections_completed.clear()
	for figure_id in source.get("figure_collections_completed", []):
		figure_collections_completed[str(figure_id)] = true
	active_collection_bonuses.clear()
	for figure_id in source.get("active_collection_bonuses", []):
		active_collection_bonuses.append(str(figure_id))
	pending_prestige = maxi(0, int(source.get("pending_prestige", 0)))
	pending_prize = {}
	var prize: Dictionary = source.get("pending_prize", {})
	if not prize.is_empty():
		pending_prize = {
			"transaction_id": int(prize.get("transaction_id", 0)),
			"machine_id": str(prize.get("machine_id", "")),
			"figure_id": str(prize.get("figure_id", "")),
			"sell_value": int(prize.get("sell_value", 1)),
			"low_funds_lock": bool(prize.get("low_funds_lock", false)),
			"state": str(prize.get("state", "REVEALED")),
		}
	next_transaction_id = maxi(1, int(source.get("next_transaction_id", 1)))
	reception_levels.clear()
	var levels: Dictionary = source.get("reception_levels", {})
	for item_id in levels:
		reception_levels[str(item_id)] = maxi(0, int(levels[item_id]))
	robots.clear()
	var saved_robots: Dictionary = source.get("robots", {})
	for machine_id in saved_robots:
		var saved: Dictionary = saved_robots[machine_id]
		var mode: String = str(saved.get("mode", "collect"))
		robots[str(machine_id)] = {
			"mode": mode if ROBOT_MODES.has(mode) else "collect",
			"paused": bool(saved.get("paused", false)),
			"progress": clampf(float(saved.get("progress", 0.0)), 0.0, 1.0),
		}
	machines_used.clear()
	for machine_id in source.get("machines_used", []):
		machines_used[str(machine_id)] = true
	key_owned_this_run = bool(source.get("key_owned_this_run", false))
	total_spins = maxi(0, int(source.get("total_spins", 0)))
	run_playtime_seconds = maxf(0.0, float(source.get("run_playtime_seconds", 0.0)))
