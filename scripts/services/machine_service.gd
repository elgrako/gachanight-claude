extends RefCounted
## Universal prize flow: pay once, roll, reveal, then a single Sell or Keep resolution.

const Economy = preload("res://scripts/services/economy_service.gd")
const Collection = preload("res://scripts/services/collection_service.gd")


## The most luck a well-timed play can add, in percent.
const MAX_TIMING_LUCK_PCT: float = 60.0


## Prize table with luck applied. Luck favours higher rarities but never
## removes any entry. It adds up from three places: the general luck, what was
## bought for this machine, and `extra_luck_pct`, earned by the player's
## timing on this one play.
static func effective_weights(data: RefCounted, perm: RefCounted, run: RefCounted, machine_id: String, extra_luck_pct: float = 0.0) -> Array:
	var luck: float = clampf(Economy.luck_pct(data, perm, run) + Economy.machine_effect(data, run, machine_id, "machine_luck_pct")
		+ clampf(extra_luck_pct, 0.0, MAX_TIMING_LUCK_PCT), 0.0, Economy.MAX_LUCK_PCT) / 100.0
	var result: Array = []
	for entry in data.machines[machine_id]["prize_table"]:
		var order: int = data.rarity_order(data.figures[entry["figure_id"]]["rarity_id"])
		result.append({"figure_id": entry["figure_id"], "weight": float(entry["weight"]) * (1.0 + luck * order)})
	return result


## Picks a figure for a roll in [0, 1).
static func pick_figure(weights: Array, roll: float) -> String:
	var total: float = 0.0
	for entry in weights:
		total += entry["weight"]
	var target: float = clampf(roll, 0.0, 0.999999) * total
	var cumulative: float = 0.0
	for entry in weights:
		cumulative += entry["weight"]
		if target < cumulative:
			return entry["figure_id"]
	return weights[weights.size() - 1]["figure_id"]


## Position of a figure in its machine's prize table (the plinko slot it lands in).
static func prize_slot(data: RefCounted, machine_id: String, figure_id: String) -> int:
	var table: Array = data.machines[machine_id]["prize_table"]
	for index in range(table.size()):
		if table[index]["figure_id"] == figure_id:
			return index
	return 0


static func can_play(data: RefCounted, perm: RefCounted, run: RefCounted, machine_id: String) -> Dictionary:
	if not data.machines.has(machine_id):
		return {"ok": false, "reason": "unknown_machine", "price": 0}
	var price: int = Economy.machine_price(data, perm, run, machine_id)
	if run.has_pending_prize():
		return {"ok": false, "reason": "prize_pending", "price": price}
	if not run.power_switch_on:
		return {"ok": false, "reason": "power_off", "price": price}
	if run.coins < price:
		return {"ok": false, "reason": "not_enough_coins", "price": price}
	return {"ok": true, "reason": "", "price": price}


## A spin by the player. Leaves a pending prize, unless Express Lane sells a
## duplicate of a completed collection on the spot ("auto_sold").
static func play(data: RefCounted, perm: RefCounted, run: RefCounted, machine_id: String, roll: float, extra_luck_pct: float = 0.0) -> Dictionary:
	var check: Dictionary = can_play(data, perm, run, machine_id)
	if not check["ok"]:
		return check
	var result: Dictionary = _pay_and_roll(data, perm, run, machine_id, check["price"], roll, extra_luck_pct)
	var figure_id: String = result["figure_id"]
	var value: int = Economy.sell_value(data, perm, run, figure_id)
	if Economy.auto_sells_duplicates(data, run) and Collection.is_completed(data, run, figure_id):
		run.coins += value
		result.merge({"auto_sold": true, "coins_gained": value, "prize": {}})
		return result
	var prize: Dictionary = {
		"transaction_id": run.next_transaction_id,
		"machine_id": machine_id,
		"figure_id": figure_id,
		"sell_value": value,
		# Evaluated once, after paying: selling later does not reopen Keep.
		"low_funds_lock": run.coins <= Collection.LOW_FUNDS_THRESHOLD,
		"state": "REVEALED",
	}
	run.next_transaction_id += 1
	run.pending_prize = prize
	result.merge({"auto_sold": false, "coins_gained": 0, "prize": prize.duplicate()})
	return result


## A spin by a robot. Resolved immediately and never touches the pending prize
## slot. mode "collect" keeps until the collection is complete, then sells.
static func auto_spin(data: RefCounted, perm: RefCounted, run: RefCounted, machine_id: String, roll: float, mode: String) -> Dictionary:
	if not data.machines.has(machine_id) or not run.power_switch_on:
		return {"ok": false, "reason": "unavailable"}
	var price: int = Economy.machine_price(data, perm, run, machine_id)
	if run.coins < price:
		return {"ok": false, "reason": "not_enough_coins"}
	var result: Dictionary = _pay_and_roll(data, perm, run, machine_id, price, roll)
	var figure_id: String = result["figure_id"]
	var may_keep: bool = mode == "collect" and run.coins > Collection.LOW_FUNDS_THRESHOLD \
		and not Collection.is_completed(data, run, figure_id)
	if may_keep:
		var kept: Dictionary = Collection.keep(data, perm, run, figure_id)
		result.merge({"choice": "keep", "coins_gained": 0, "completed": kept["completed"], "prestige": kept["prestige"]})
	else:
		var value: int = Economy.sell_value(data, perm, run, figure_id)
		run.coins += value
		result.merge({"choice": "sell", "coins_gained": value, "completed": false, "prestige": 0})
	return result


## Resolves the pending prize exactly once. choice is "sell" or "keep".
static func resolve(data: RefCounted, perm: RefCounted, run: RefCounted, transaction_id: int, choice: String) -> Dictionary:
	if not run.has_pending_prize():
		return {"ok": false, "reason": "no_pending_prize"}
	var prize: Dictionary = run.pending_prize
	if int(prize["transaction_id"]) != transaction_id:
		return {"ok": false, "reason": "transaction_mismatch"}
	var figure_id: String = prize["figure_id"]
	if choice == "sell":
		var value: int = maxi(1, int(prize["sell_value"]))
		run.pending_prize = {}
		run.coins += value
		return {"ok": true, "reason": "", "choice": "sell", "figure_id": figure_id, "coins_gained": value}
	if choice == "keep":
		var allowed: Dictionary = Collection.can_keep(data, run, prize)
		if not allowed["ok"]:
			return allowed
		run.pending_prize = {}
		var kept: Dictionary = Collection.keep(data, perm, run, figure_id)
		kept.merge({"ok": true, "reason": "", "choice": "keep", "figure_id": figure_id})
		return kept
	return {"ok": false, "reason": "unknown_choice"}


static func _pay_and_roll(data: RefCounted, perm: RefCounted, run: RefCounted, machine_id: String, price: int, roll: float, extra_luck_pct: float = 0.0) -> Dictionary:
	run.coins -= price
	run.total_spins += 1
	run.machines_used[machine_id] = true
	var figure_id: String = pick_figure(effective_weights(data, perm, run, machine_id, extra_luck_pct), roll)
	var newly_discovered: bool = not perm.discoveries.has(figure_id)
	perm.discoveries[figure_id] = true
	var prestige_unlocked_now: bool = false
	if data.machines[machine_id]["unlocks_prestige"] and not perm.tutorial_m2_used:
		perm.tutorial_m2_used = true
		prestige_unlocked_now = true
	return {
		"ok": true, "reason": "", "price": price, "machine_id": machine_id, "figure_id": figure_id,
		"newly_discovered": newly_discovered, "prestige_unlocked_now": prestige_unlocked_now,
	}
