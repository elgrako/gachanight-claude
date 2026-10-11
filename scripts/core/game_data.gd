extends RefCounted
## Static game definitions loaded from JSON tables. Never mutated as game state.

const RARITY_IDS: Array = ["common", "uncommon", "rare", "epic", "legendary"]
const BONUS_TYPES: Array = ["sell_value_pct", "price_discount_pct", "luck_pct", "robot_speed_pct"]
const UPGRADE_EFFECT_TYPES: Array = [
	"start_with_floor_coins", "start_coins", "sell_value_pct", "price_discount_pct", "luck_pct",
	"crank_speed_pct", "robot_speed_pct", "prestige_gain_pct", "auto_sell_duplicates",
]
const MACHINE_TYPES: Array = ["gacha", "claw", "plinko"]
const RECEPTION_CATEGORIES: Array = ["income", "machines", "automation", "convenience", "exit"]

var rarities: Dictionary = {}
var figures: Dictionary = {}
var machines: Dictionary = {}
var prestige_upgrades: Dictionary = {}
var reception_upgrades: Dictionary = {}
var figure_order: Array = []
var machine_order: Array = []
var upgrade_order: Array = []
var reception_order: Array = []
var exit_key_id: String = ""
## Seconds one robot needs for one spin before speed bonuses.
var robot_base_spin_seconds: float = 2.5
var errors: Array = []


func load_all(dir: String = "res://data") -> bool:
	errors.clear()
	_load_rarities(_read_table(dir + "/rarities.json", "rarities"))
	_load_figures(_read_table(dir + "/figures.json", "figures"))
	_load_machines(_read_table(dir + "/machines.json", "machines"))
	_load_upgrades(_read_table(dir + "/prestige_upgrades.json", "upgrades"))
	_load_reception(_read_table(dir + "/reception_upgrades.json", "upgrades"))
	robot_base_spin_seconds = _read_number(dir + "/reception_upgrades.json", "robot_base_spin_seconds", 2.5)
	if robot_base_spin_seconds <= 0.0:
		errors.append("robot_base_spin_seconds must be positive")
	return errors.is_empty()


## Machine a reception robot item works on, or "" when the item is not a robot.
func robot_item_for_machine(machine_id: String) -> String:
	for item_id in reception_order:
		if reception_upgrades[item_id]["robot_machine_id"] == machine_id:
			return item_id
	return ""


## Value of one effect entry at a level: values[level - 1] when given, else per_level * level.
static func effect_value(effect: Dictionary, level: int) -> float:
	if level <= 0:
		return 0.0
	var values: Array = effect.get("values", [])
	if not values.is_empty():
		return float(values[mini(level, values.size()) - 1])
	return float(effect["per_level"]) * level


func figure_machine_ids(figure_id: String) -> Array:
	var result: Array = []
	for machine_id in machine_order:
		for entry in machines[machine_id]["prize_table"]:
			if entry["figure_id"] == figure_id:
				result.append(machine_id)
				break
	return result


func rarity_order(rarity_id: String) -> int:
	return int(rarities[rarity_id]["order"])


func _read_table(path: String, key: String) -> Array:
	if not FileAccess.file_exists(path):
		errors.append("missing data file: %s" % path)
		return []
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY or typeof(parsed.get(key)) != TYPE_ARRAY:
		errors.append("invalid data file: %s (expected object with '%s' array)" % [path, key])
		return []
	return parsed[key]


func _read_number(path: String, key: String, fallback: float) -> float:
	if not FileAccess.file_exists(path):
		return fallback
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		return fallback
	return float(parsed.get(key, fallback))


func _load_rarities(rows: Array) -> void:
	rarities.clear()
	for row in rows:
		var id: String = str(row.get("id", ""))
		if not RARITY_IDS.has(id):
			errors.append("unknown rarity id: %s" % id)
			continue
		rarities[id] = {
			"id": id,
			"name_en": str(row.get("name_en", id)),
			"order": int(row.get("order", RARITY_IDS.find(id))),
			"color": Color.from_string(str(row.get("color", "#ffffff")), Color.WHITE),
		}
	for id in RARITY_IDS:
		if not rarities.has(id):
			errors.append("missing rarity: %s" % id)
	if rarities.size() != RARITY_IDS.size():
		errors.append("there must be exactly %d rarities" % RARITY_IDS.size())


func _load_figures(rows: Array) -> void:
	figures.clear()
	figure_order.clear()
	for row in rows:
		var id: String = str(row.get("id", ""))
		if id.is_empty() or figures.has(id):
			errors.append("figure id missing or duplicated: '%s'" % id)
			continue
		var figure: Dictionary = {
			"id": id,
			"name_en": str(row.get("name_en", id)),
			"rarity_id": str(row.get("rarity_id", "")),
			"base_sell_value": int(row.get("base_sell_value", 0)),
			"copies_required": int(row.get("copies_required", 0)),
			"prestige_reward": int(row.get("prestige_reward", 0)),
			"collection_bonus_id": str(row.get("collection_bonus_id", "")),
			"collection_bonus_params": row.get("collection_bonus_params", {}),
			"look": row.get("look", {}),
		}
		if not rarities.has(figure["rarity_id"]):
			errors.append("figure %s has unknown rarity '%s'" % [id, figure["rarity_id"]])
		if figure["base_sell_value"] < 1:
			errors.append("figure %s must sell for at least 1" % id)
		if figure["copies_required"] < 1:
			errors.append("figure %s needs copies_required >= 1" % id)
		if figure["prestige_reward"] < 1:
			errors.append("figure %s needs prestige_reward >= 1" % id)
		if not BONUS_TYPES.has(figure["collection_bonus_id"]):
			errors.append("figure %s has unknown bonus '%s'" % [id, figure["collection_bonus_id"]])
		figures[id] = figure
		figure_order.append(id)


func _load_machines(rows: Array) -> void:
	machines.clear()
	machine_order.clear()
	for row in rows:
		var id: String = str(row.get("id", ""))
		if id.is_empty() or machines.has(id):
			errors.append("machine id missing or duplicated: '%s'" % id)
			continue
		var machine: Dictionary = {
			"id": id,
			"machine_type": str(row.get("machine_type", "gacha")),
			"display_name_en": str(row.get("display_name_en", id)),
			"series_name_en": str(row.get("series_name_en", "")),
			"price_per_attempt": int(row.get("price_per_attempt", 0)),
			"min_sell_value": int(row.get("min_sell_value", 1)),
			"unlocks_prestige": bool(row.get("unlocks_prestige", false)),
			"prize_table": [],
		}
		if machine["price_per_attempt"] < 1:
			errors.append("machine %s needs price_per_attempt >= 1" % id)
		if not MACHINE_TYPES.has(machine["machine_type"]):
			errors.append("machine %s has unknown type '%s'" % [id, machine["machine_type"]])
		for entry in row.get("prize_table", []):
			var figure_id: String = str(entry.get("figure_id", ""))
			var weight: float = float(entry.get("weight", 0))
			if not figures.has(figure_id):
				errors.append("machine %s references unknown figure '%s'" % [id, figure_id])
				continue
			if weight <= 0.0:
				errors.append("machine %s has non-positive weight for %s" % [id, figure_id])
				continue
			if figures[figure_id]["base_sell_value"] < machine["min_sell_value"]:
				errors.append("figure %s sells below the minimum of %s" % [figure_id, id])
			machine["prize_table"].append({"figure_id": figure_id, "weight": weight})
		if machine["prize_table"].is_empty():
			errors.append("machine %s has an empty prize table" % id)
		machines[id] = machine
		machine_order.append(id)


func _load_upgrades(rows: Array) -> void:
	prestige_upgrades.clear()
	upgrade_order.clear()
	for row in rows:
		var id: String = str(row.get("id", ""))
		if id.is_empty() or prestige_upgrades.has(id):
			errors.append("upgrade id missing or duplicated: '%s'" % id)
			continue
		var costs: Array = []
		for cost in row.get("prestige_cost_curve", []):
			costs.append(int(cost))
		var prerequisites: Dictionary = {}
		var raw_prerequisites: Dictionary = row.get("prerequisites", {})
		for key in raw_prerequisites:
			prerequisites[str(key)] = int(raw_prerequisites[key])
		var effects: Array = _parse_effects(id, row.get("permanent_effects", []))
		var upgrade: Dictionary = {
			"id": id,
			"category": str(row.get("category", "")),
			"display_name_en": str(row.get("display_name_en", id)),
			"description_en": str(row.get("description_en", "")),
			"max_level": int(row.get("max_level", 1)),
			"prestige_cost_curve": costs,
			"prerequisites": prerequisites,
			"permanent_effects": effects,
		}
		if upgrade["max_level"] < 1 or costs.size() != upgrade["max_level"]:
			errors.append("upgrade %s needs one cost per level" % id)
		for cost in costs:
			if cost < 1:
				errors.append("upgrade %s has a cost below 1" % id)
		prestige_upgrades[id] = upgrade
		upgrade_order.append(id)
	for id in upgrade_order:
		for required_id in prestige_upgrades[id]["prerequisites"]:
			if not prestige_upgrades.has(required_id):
				errors.append("upgrade %s requires unknown upgrade '%s'" % [id, required_id])

func _parse_effects(owner_id: String, rows: Array) -> Array:
	var effects: Array = []
	for effect in rows:
		var effect_type: String = str(effect.get("type", ""))
		if not UPGRADE_EFFECT_TYPES.has(effect_type):
			errors.append("upgrade %s has unknown effect '%s'" % [owner_id, effect_type])
			continue
		var values: Array = []
		for value in effect.get("values", []):
			values.append(float(value))
		effects.append({"type": effect_type, "per_level": float(effect.get("per_level", 0)), "values": values})
	return effects


func _load_reception(rows: Array) -> void:
	reception_upgrades.clear()
	reception_order.clear()
	exit_key_id = ""
	for row in rows:
		var id: String = str(row.get("id", ""))
		if id.is_empty() or reception_upgrades.has(id):
			errors.append("reception item id missing or duplicated: '%s'" % id)
			continue
		var raw_prerequisites: Dictionary = row.get("prerequisites", {})
		var required_upgrades: Dictionary = {}
		var raw_upgrades: Dictionary = raw_prerequisites.get("upgrades", {})
		for key in raw_upgrades:
			required_upgrades[str(key)] = int(raw_upgrades[key])
		var required_machines: Array = []
		for machine_id in raw_prerequisites.get("machines_used", []):
			required_machines.append(str(machine_id))
			if not machines.has(str(machine_id)):
				errors.append("reception item %s requires unknown machine '%s'" % [id, machine_id])
		var item: Dictionary = {
			"id": id,
			"category": str(row.get("category", "")),
			"display_name_en": str(row.get("display_name_en", id)),
			"description_en": str(row.get("description_en", "")),
			"max_level": int(row.get("max_level", 1)),
			"base_cost": int(row.get("base_cost", 0)),
			"cost_growth": float(row.get("cost_growth", 1.0)),
			"effects": _parse_effects(id, row.get("effects", [])),
			"robot_machine_id": str(row.get("robot_machine_id", "")),
			"is_store_exit_key": bool(row.get("is_store_exit_key", false)),
			"prerequisites": {"upgrades": required_upgrades, "machines_used": required_machines},
		}
		if not RECEPTION_CATEGORIES.has(item["category"]):
			errors.append("reception item %s has unknown category '%s'" % [id, item["category"]])
		if item["max_level"] < 1 or item["base_cost"] < 1 or item["cost_growth"] < 1.0:
			errors.append("reception item %s needs max_level >= 1, base_cost >= 1 and cost_growth >= 1" % id)
		if item["robot_machine_id"] != "" and not machines.has(item["robot_machine_id"]):
			errors.append("reception item %s works unknown machine '%s'" % [id, item["robot_machine_id"]])
		if item["is_store_exit_key"]:
			if exit_key_id != "":
				errors.append("there must be exactly one store exit key")
			exit_key_id = id
		reception_upgrades[id] = item
		reception_order.append(id)
	if exit_key_id == "":
		errors.append("the reception table has no store exit key")
	for id in reception_order:
		for required_id in reception_upgrades[id]["prerequisites"]["upgrades"]:
			if not reception_upgrades.has(required_id):
				errors.append("reception item %s requires unknown item '%s'" % [id, required_id])
