extends RefCounted
## Reception computer: upgrades, robots and the exit key, paid with coins.
## Everything bought here belongs to the run and is lost on rebirth.

## Coins that must remain after a purchase so machine 001 stays affordable.
const MIN_COINS_AFTER_PURCHASE: int = 1


static func next_cost(data: RefCounted, run: RefCounted, item_id: String) -> int:
	var item: Dictionary = data.reception_upgrades[item_id]
	return int(round(float(item["base_cost"]) * pow(float(item["cost_growth"]), run.reception_level(item_id))))


static func robot_count(data: RefCounted, run: RefCounted, machine_id: String) -> int:
	var item_id: String = data.robot_item_for_machine(machine_id)
	return run.reception_level(item_id) if item_id != "" else 0


## Reasons: "unknown_item", "max_level", "missing_prerequisite", "not_enough_coins", "keep_one_coin".
static func can_buy(data: RefCounted, run: RefCounted, item_id: String) -> Dictionary:
	if not data.reception_upgrades.has(item_id):
		return {"ok": false, "reason": "unknown_item", "cost": 0}
	var item: Dictionary = data.reception_upgrades[item_id]
	var cost: int = next_cost(data, run, item_id)
	if run.reception_level(item_id) >= int(item["max_level"]):
		return {"ok": false, "reason": "max_level", "cost": 0}
	if not missing_prerequisites(data, run, item_id).is_empty():
		return {"ok": false, "reason": "missing_prerequisite", "cost": cost}
	if run.coins < cost:
		return {"ok": false, "reason": "not_enough_coins", "cost": cost}
	if run.coins - cost < MIN_COINS_AFTER_PURCHASE:
		return {"ok": false, "reason": "keep_one_coin", "cost": cost}
	return {"ok": true, "reason": "", "cost": cost}


## English descriptions of the requirements still unmet.
static func missing_prerequisites(data: RefCounted, run: RefCounted, item_id: String) -> Array:
	var missing: Array = []
	var prerequisites: Dictionary = data.reception_upgrades[item_id]["prerequisites"]
	for required_id in prerequisites["upgrades"]:
		var level: int = int(prerequisites["upgrades"][required_id])
		if run.reception_level(required_id) < level:
			missing.append("%s Lv %d" % [data.reception_upgrades[required_id]["display_name_en"], level])
	for machine_id in prerequisites["machines_used"]:
		if not run.machines_used.has(machine_id):
			missing.append("Try %s" % data.machines[machine_id]["display_name_en"])
	return missing


static func buy(data: RefCounted, run: RefCounted, item_id: String) -> Dictionary:
	var check: Dictionary = can_buy(data, run, item_id)
	if not check["ok"]:
		return check
	var item: Dictionary = data.reception_upgrades[item_id]
	run.coins -= int(check["cost"])
	run.reception_levels[item_id] = run.reception_level(item_id) + 1
	var result: Dictionary = {
		"ok": true, "reason": "", "cost": check["cost"], "item_id": item_id,
		"level": run.reception_level(item_id), "bought_key": false, "robot_machine_id": item["robot_machine_id"],
	}
	if item["is_store_exit_key"]:
		run.key_owned_this_run = true
		result["bought_key"] = true
	if item["robot_machine_id"] != "":
		run.robot_state(item["robot_machine_id"])
	return result
