extends RefCounted
## Robots: a cheap numeric simulation. Each machine accumulates progress and
## performs whole spins; nothing is instanced per spin.

const Economy = preload("res://scripts/services/economy_service.gd")
const Machine = preload("res://scripts/services/machine_service.gd")
const Reception = preload("res://scripts/services/reception_service.gd")

## Upper bound of spins per machine per tick, to keep slow frames bounded.
const MAX_SPINS_PER_TICK: int = 400


static func spins_per_second(data: RefCounted, perm: RefCounted, run: RefCounted, machine_id: String) -> float:
	var count: int = Reception.robot_count(data, run, machine_id)
	if count <= 0:
		return 0.0
	return count * Economy.robot_speed_multiplier(data, perm, run) / data.robot_base_spin_seconds


## Advances every robot. roll_fn returns rolls in [0, 1). Returns a summary:
## {spins, coins_spent, coins_earned, discovered: [], completed: [{figure_id, prestige}],
##  prestige_unlocked, by_machine: {machine_id: spins}}.
static func tick(data: RefCounted, perm: RefCounted, run: RefCounted, delta: float, roll_fn: Callable) -> Dictionary:
	var summary: Dictionary = {
		"spins": 0, "coins_spent": 0, "coins_earned": 0, "discovered": [], "completed": [],
		"prestige_unlocked": false, "by_machine": {},
	}
	if not run.power_switch_on or delta <= 0.0:
		return summary
	for machine_id in data.machine_order:
		var rate: float = spins_per_second(data, perm, run, machine_id)
		if rate <= 0.0:
			continue
		var state: Dictionary = run.robot_state(machine_id)
		if state["paused"]:
			continue
		var progress: float = float(state["progress"]) + rate * delta
		var due: int = mini(int(floor(progress)), MAX_SPINS_PER_TICK)
		var done: int = 0
		for index in range(due):
			var result: Dictionary = Machine.auto_spin(data, perm, run, machine_id, float(roll_fn.call()), state["mode"])
			if not result["ok"]:
				break
			done += 1
			summary["coins_spent"] += result["price"]
			summary["coins_earned"] += result["coins_gained"]
			if result["newly_discovered"]:
				summary["discovered"].append(result["figure_id"])
			if result["completed"]:
				summary["completed"].append({"figure_id": result["figure_id"], "prestige": result["prestige"]})
			if result["prestige_unlocked_now"]:
				summary["prestige_unlocked"] = true
		# A robot that cannot pay waits with its spin ready instead of banking time.
		state["progress"] = clampf(progress - due, 0.0, 1.0) if done == due else 1.0
		if done > 0:
			summary["spins"] += done
			summary["by_machine"][machine_id] = done
	return summary
