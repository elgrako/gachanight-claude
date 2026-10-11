extends RefCounted
## Per-figure collections: one counter per figure id, completed once per run.

const Economy = preload("res://scripts/services/economy_service.gd")

const LOW_FUNDS_THRESHOLD: int = 1


static func copies_required(data: RefCounted, figure_id: String) -> int:
	return maxi(1, int(data.figures[figure_id]["copies_required"]))


static func is_completed(data: RefCounted, run: RefCounted, figure_id: String) -> bool:
	return run.figure_collections_completed.has(figure_id) \
		or run.copies_held(figure_id) >= copies_required(data, figure_id)


## Whether a revealed prize may be kept. Reasons: "collection_completed", "low_funds".
static func can_keep(data: RefCounted, run: RefCounted, prize: Dictionary) -> Dictionary:
	if is_completed(data, run, prize["figure_id"]):
		return {"ok": false, "reason": "collection_completed"}
	if prize.get("low_funds_lock", false):
		return {"ok": false, "reason": "low_funds"}
	return {"ok": true, "reason": ""}


## Adds one kept copy. The caller must have checked can_keep.
static func keep(data: RefCounted, perm: RefCounted, run: RefCounted, figure_id: String) -> Dictionary:
	var required: int = copies_required(data, figure_id)
	var held: int = mini(required, run.copies_held(figure_id) + 1)
	run.figure_copies_held[figure_id] = held
	var result: Dictionary = {"copies_held": held, "copies_required": required, "completed": false, "prestige": 0}
	if held >= required and not run.figure_collections_completed.has(figure_id):
		# Flag first so nothing below can grant the reward twice.
		run.figure_collections_completed[figure_id] = true
		var reward: int = Economy.prestige_reward(data, perm, figure_id)
		run.pending_prestige += reward
		if not run.active_collection_bonuses.has(figure_id):
			run.active_collection_bonuses.append(figure_id)
		result["completed"] = true
		result["prestige"] = reward
	return result
