extends RefCounted
## Sofa prestige: provisional selection, quote, and the rebirth transaction.
## A selection maps upgrade_id -> number of levels to add.


static func is_unlocked(perm: RefCounted) -> bool:
	return perm.tutorial_m2_used


static func available(perm: RefCounted, run: RefCounted) -> int:
	return perm.banked_prestige + run.pending_prestige


static func cost_of(data: RefCounted, perm: RefCounted, upgrade_id: String, levels: int) -> int:
	var curve: Array = data.prestige_upgrades[upgrade_id]["prestige_cost_curve"]
	var current: int = perm.upgrade_level(upgrade_id)
	var total: int = 0
	for level in range(current, current + levels):
		total += int(curve[level])
	return total


## Validates a selection without changing anything.
static func quote(data: RefCounted, perm: RefCounted, run: RefCounted, selection: Dictionary) -> Dictionary:
	var points: int = available(perm, run)
	var result: Dictionary = {"ok": false, "reason": "", "cost": 0, "available": points, "remaining": points}
	if not is_unlocked(perm):
		result["reason"] = "prestige_locked"
		return result
	var cost: int = 0
	for upgrade_id in selection:
		var levels: int = int(selection[upgrade_id])
		if levels == 0:
			continue
		if not data.prestige_upgrades.has(upgrade_id):
			result["reason"] = "unknown_upgrade"
			return result
		var upgrade: Dictionary = data.prestige_upgrades[upgrade_id]
		if levels < 0 or perm.upgrade_level(upgrade_id) + levels > int(upgrade["max_level"]):
			result["reason"] = "invalid_level"
			return result
		for required_id in upgrade["prerequisites"]:
			var reached: int = perm.upgrade_level(required_id) + int(selection.get(required_id, 0))
			if reached < int(upgrade["prerequisites"][required_id]):
				result["reason"] = "missing_prerequisite"
				return result
		cost += cost_of(data, perm, upgrade_id, levels)
	result["cost"] = cost
	result["remaining"] = points - cost
	if cost > points:
		result["reason"] = "not_enough_prestige"
		return result
	result["ok"] = true
	return result


## Applies an already validated selection to the permanent state.
## new_banked = old_banked + pending - approved_spend.
static func apply(perm: RefCounted, run: RefCounted, selection: Dictionary, cost: int) -> void:
	perm.banked_prestige = perm.banked_prestige + run.pending_prestige - cost
	for upgrade_id in selection:
		var levels: int = int(selection[upgrade_id])
		if levels > 0:
			perm.prestige_upgrade_levels[upgrade_id] = perm.upgrade_level(upgrade_id) + levels
	perm.total_rebirths += 1
