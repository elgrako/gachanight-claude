extends RefCounted
## Derived economy values.
## Modifier order: base -> permanent prestige -> reception -> collection bonus.
## Floors keep the economy safe: sales never drop below 1 and prices never reach 0.

const GameData = preload("res://scripts/core/game_data.gd")

const MAX_PRICE_DISCOUNT_PCT: float = 50.0
const MAX_LUCK_PCT: float = 300.0
const MAX_CRANK_SPEED_PCT: float = 300.0


static func prestige_effect(data: RefCounted, perm: RefCounted, effect_type: String) -> float:
	var total: float = 0.0
	for upgrade_id in data.upgrade_order:
		var level: int = perm.upgrade_level(upgrade_id)
		if level <= 0:
			continue
		for effect in data.prestige_upgrades[upgrade_id]["permanent_effects"]:
			if effect["type"] == effect_type:
				total += GameData.effect_value(effect, level)
	return total


static func reception_effect(data: RefCounted, run: RefCounted, effect_type: String) -> float:
	var total: float = 0.0
	for item_id in run.reception_levels:
		if not data.reception_upgrades.has(item_id):
			continue
		var level: int = run.reception_level(item_id)
		for effect in data.reception_upgrades[item_id]["effects"]:
			if effect["type"] == effect_type:
				total += GameData.effect_value(effect, level)
	return total


## Sum of an effect over the items bought for one machine.
static func machine_effect(data: RefCounted, run: RefCounted, machine_id: String, effect_type: String) -> float:
	var total: float = 0.0
	for item_id in run.reception_levels:
		if not data.reception_upgrades.has(item_id) or data.reception_upgrades[item_id]["machine_id"] != machine_id:
			continue
		var level: int = run.reception_level(item_id)
		for effect in data.reception_upgrades[item_id]["effects"]:
			if effect["type"] == effect_type:
				total += GameData.effect_value(effect, level)
	return total


static func collection_effect(data: RefCounted, run: RefCounted, effect_type: String) -> float:
	var total: float = 0.0
	for figure_id in run.active_collection_bonuses:
		if not data.figures.has(figure_id):
			continue
		var figure: Dictionary = data.figures[figure_id]
		if figure["collection_bonus_id"] == effect_type:
			total += float(figure["collection_bonus_params"].get("value", 0))
	return total


## Product of (1 + pct/100) over the three sources, for multiplicative stats.
static func multiplier(data: RefCounted, perm: RefCounted, run: RefCounted, effect_type: String) -> float:
	return (1.0 + prestige_effect(data, perm, effect_type) / 100.0) \
		* (1.0 + reception_effect(data, run, effect_type) / 100.0) \
		* (1.0 + collection_effect(data, run, effect_type) / 100.0)


## Sum of the three sources, for additive stats.
static func additive(data: RefCounted, perm: RefCounted, run: RefCounted, effect_type: String) -> float:
	return prestige_effect(data, perm, effect_type) + reception_effect(data, run, effect_type) \
		+ collection_effect(data, run, effect_type)


static func sell_value(data: RefCounted, perm: RefCounted, run: RefCounted, figure_id: String) -> int:
	var base: float = float(data.figures[figure_id]["base_sell_value"])
	return maxi(1, int(floor(base * multiplier(data, perm, run, "sell_value_pct") + 0.0001)))


static func machine_price(data: RefCounted, perm: RefCounted, run: RefCounted, machine_id: String) -> int:
	var base: float = float(data.machines[machine_id]["price_per_attempt"])
	var discount: float = clampf(additive(data, perm, run, "price_discount_pct"), 0.0, MAX_PRICE_DISCOUNT_PCT)
	return maxi(1, int(ceil(base * (1.0 - discount / 100.0) - 0.0001)))


static func luck_pct(data: RefCounted, perm: RefCounted, run: RefCounted) -> float:
	return clampf(additive(data, perm, run, "luck_pct"), 0.0, MAX_LUCK_PCT)


static func robot_speed_multiplier(data: RefCounted, perm: RefCounted, run: RefCounted) -> float:
	return multiplier(data, perm, run, "robot_speed_pct")


## How much faster the manual prize animation plays (1.0 = normal).
static func crank_speed_multiplier(data: RefCounted, perm: RefCounted, run: RefCounted) -> float:
	return 1.0 + clampf(additive(data, perm, run, "crank_speed_pct"), 0.0, MAX_CRANK_SPEED_PCT) / 100.0


static func prestige_reward(data: RefCounted, perm: RefCounted, figure_id: String) -> int:
	var base: int = int(data.figures[figure_id]["prestige_reward"])
	var bonus: float = prestige_effect(data, perm, "prestige_gain_pct") / 100.0
	return maxi(base, int(floor(base * (1.0 + bonus) + 0.0001)))


static func auto_sells_duplicates(data: RefCounted, run: RefCounted) -> bool:
	return reception_effect(data, run, "auto_sell_duplicates") > 0.0


## Coins a new run starts with, before picking up the floor coins.
static func starting_coins(data: RefCounted, perm: RefCounted) -> int:
	return maxi(0, int(prestige_effect(data, perm, "start_coins")))


static func starts_with_floor_coins(data: RefCounted, perm: RefCounted) -> bool:
	return prestige_effect(data, perm, "start_with_floor_coins") > 0.0
