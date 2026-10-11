extends SceneTree
## Balance simulation: a scripted player with a time model plays the story on
## the real rules and reports when each milestone happens. Run with:
##   godot --headless --path . -s tests/sim_balance.gd
## Optional: `-- --seed=N --quiet`. Exit code 0 when the story lands inside
## the target window (design: 2-3 hours over several rebirths).
##
## The player is competent but not optimal: it plays the most profitable
## machine it can afford, keeps figures when it has a cushion, visits
## reception regularly and sleeps when the run stalls.

const GameCore = preload("res://scripts/core/game_core.gd")
const Machine = preload("res://scripts/services/machine_service.gd")
const Format = preload("res://scripts/core/format.gd")

const TARGET_MIN_MINUTES: float = 120.0
const TARGET_MAX_MINUTES: float = 180.0
const MIN_REBIRTHS: int = 3
const MAX_SIM_MINUTES: float = 480.0

# Time model, in seconds.
const SPIN_ANIMATION: float = 0.85
const DECISION: float = 1.3
const RUN_START: float = 22.0       # wake up, coins, switch, walk to the machines
const RECEPTION_TRIP: float = 14.0  # walk to the counter and back
const RECEPTION_BUY: float = 2.0
const SOFA_TRIP: float = 30.0       # walk, choose upgrades, sleep
const RECEPTION_EVERY: float = 50.0
const MIN_RUN_BEFORE_SLEEP: float = 480.0

const RECEPTION_PRIORITY: Array = ["price_tag_gun", "faster_servos", "lucky_sticker", "loyalty_card", "turbo_crank", "express_lane"]
const PRESTIGE_PRIORITY: Array = [
	"better_appraisal", "ready_pockets", "quick_capsules", "starting_tip", "robot_training",
	"prestige_knowledge", "lucky_bearings", "efficient_spending",
]

var core: RefCounted
var clock: float = 0.0
var run_clock: float = 0.0
var next_reception: float = 0.0
var milestones: Array = []
var seen: Dictionary = {}
var quiet: bool = false
var coin_history: Array = []  # [run_clock, coins] samples for the stall check


func _init() -> void:
	var seed_value: int = 1987
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--seed="):
			seed_value = int(argument.trim_prefix("--seed="))
		elif argument == "--quiet":
			quiet = true
	var path: String = "user://sim_balance.json"
	for suffix in ["", ".bak", ".tmp"]:
		if FileAccess.file_exists(path + suffix):
			DirAccess.remove_absolute(path + suffix)
	core = GameCore.new()
	core.setup(path)
	core.autosave_enabled = false
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.seed = seed_value
	core.rand_fn = func() -> float: return rng.randf()
	_start_run()
	while not core.perm.story_completed and clock < MAX_SIM_MINUTES * 60.0:
		_step()
	_report(seed_value)


# --- Player -----------------------------------------------------------------

func _start_run() -> void:
	run_clock = 0.0
	next_reception = RECEPTION_EVERY
	coin_history.clear()
	_pass(RUN_START)
	core.turn_power_on()
	for index in range(3):
		core.collect_floor_coin(index)


func _step() -> void:
	if run_clock >= next_reception:
		next_reception = run_clock + RECEPTION_EVERY
		_visit_reception()
		if core.run.key_owned_this_run:
			_pass(20.0)
			core.use_exit_door()
			_mark("story completed")
			return
	if _should_sleep():
		_sleep()
		return
	var machine_id: String = _choose_machine()
	var played: Dictionary = core.play_machine(machine_id)
	if not played["ok"]:
		_pass(1.0)
		return
	_mark("first use of %s" % machine_id)
	var animation: float = SPIN_ANIMATION / core.crank_speed_multiplier()
	if played["auto_sold"]:
		_pass(animation + 0.3)
		return
	var price: int = played["price"]
	var view: Dictionary = core.pending_prize_view()
	var wants_keep: bool = view["keep"]["ok"] and core.run.coins >= price * 4
	core.resolve_prize(view["transaction_id"], "keep" if wants_keep else "sell")
	_pass(animation + DECISION)


## Expected coins back per coin spent on a machine, selling everything.
func _return_rate(machine_id: String) -> float:
	var weights: Array = Machine.effective_weights(core.data, core.perm, core.run, machine_id)
	var total: float = 0.0
	var value: float = 0.0
	for entry in weights:
		total += entry["weight"]
		value += entry["weight"] * core.figure_view(entry["figure_id"])["sell_value"]
	return value / total / float(core.machine_price(machine_id))


func _incomplete_figures(machine_id: String) -> int:
	var count: int = 0
	for entry in core.data.machines[machine_id]["prize_table"]:
		if not core.figure_view(entry["figure_id"])["completed"]:
			count += 1
	return count


func _choose_machine() -> String:
	var coins: int = core.run.coins
	var best: String = "machine_001"
	var best_gain: float = 0.0
	for machine_id in core.data.machine_order:
		var price: int = core.machine_price(machine_id)
		if price > coins:
			continue
		# Try every machine once it is comfortably affordable: the key needs it.
		if not core.run.machines_used.has(machine_id) and coins >= price * 2:
			return machine_id
		var rate: float = _return_rate(machine_id)
		if price * 3 <= coins and rate > 1.0:
			var gain: float = (rate - 1.0) * price
			if gain > best_gain:
				best_gain = gain
				best = machine_id
	# With a big cushion, spend on unfinished collections for prestige even at a loss.
	for index in range(core.data.machine_order.size() - 1, -1, -1):
		var machine_id: String = core.data.machine_order[index]
		if _incomplete_figures(machine_id) > 0 and core.machine_price(machine_id) * 60 <= coins:
			if core.machine_price(machine_id) > core.machine_price(best):
				return machine_id
			break
	return best


func _visit_reception() -> void:
	_pass(RECEPTION_TRIP)
	var key_id: String = core.data.exit_key_id
	if core.reception_item_view(key_id)["can_buy"]:
		core.buy_reception_item(key_id)
		_mark("exit key bought")
		return
	var bought: bool = true
	while bought:
		bought = false
		var candidates: Array = RECEPTION_PRIORITY.duplicate()
		# Robots only where the machine pays for itself.
		for machine_id in core.data.machine_order:
			if _return_rate(machine_id) > 1.05:
				candidates.push_front(core.data.robot_item_for_machine(machine_id))
		for item_id in candidates:
			var view: Dictionary = core.reception_item_view(item_id)
			if view["can_buy"] and view["cost"] * 2 <= core.run.coins:
				core.buy_reception_item(item_id)
				_pass(RECEPTION_BUY)
				if view["robot_machine_id"] != "":
					_mark("first robot")
				bought = true
	# Robots on a machine that loses money would drain the run: pause them.
	for machine_id in core.data.machine_order:
		if core.robot_view(machine_id)["count"] > 0:
			core.set_robot_paused(machine_id, _return_rate(machine_id) <= 1.0)


func _should_sleep() -> bool:
	if not core.is_prestige_unlocked() or core.run.has_pending_prize():
		return false
	if run_clock < MIN_RUN_BEFORE_SLEEP or _cheapest_upgrade_cost() > core.prestige_available():
		return false
	# Stalled: coins have barely grown over the last four minutes.
	var reference: int = -1
	for sample in coin_history:
		if sample[0] >= run_clock - 240.0:
			reference = sample[1]
			break
	return reference > 0 and core.run.coins < reference * 1.3


func _cheapest_upgrade_cost() -> int:
	var cheapest: int = 1 << 60
	for upgrade_id in core.data.upgrade_order:
		var upgrade: Dictionary = core.data.prestige_upgrades[upgrade_id]
		var level: int = core.perm.upgrade_level(upgrade_id)
		if level < int(upgrade["max_level"]):
			cheapest = mini(cheapest, int(upgrade["prestige_cost_curve"][level]))
	return cheapest


func _sleep() -> void:
	var selection: Dictionary = {}
	var improved: bool = true
	while improved:
		improved = false
		for upgrade_id in PRESTIGE_PRIORITY:
			var candidate: Dictionary = selection.duplicate()
			candidate[upgrade_id] = int(candidate.get(upgrade_id, 0)) + 1
			if core.get_rebirth_quote(candidate)["ok"]:
				selection = candidate
				improved = true
	var points: int = core.prestige_available()
	_pass(SOFA_TRIP)
	var result: Dictionary = core.confirm_rebirth(selection)
	if result["ok"]:
		milestones.append([clock, "rebirth %d (run %s, %d prestige, spent %d)" % [
			core.perm.total_rebirths, Format.duration(run_clock), points, result["cost"],
		]])
		_start_run()


# --- Clock ------------------------------------------------------------------

## Time passes for the player while the robots keep working.
func _pass(seconds: float) -> void:
	var remaining: float = seconds
	while remaining > 0.0:
		var step: float = minf(remaining, 1.0)
		core.tick(step)
		remaining -= step
	clock += seconds
	run_clock += seconds
	if coin_history.is_empty() or run_clock - coin_history[coin_history.size() - 1][0] >= 15.0:
		coin_history.append([run_clock, core.run.coins])
	if core.run.coins >= 50:
		_mark("50 coins")
	if core.run.pending_prestige > 0:
		_mark("first collection completed")
	if core.is_prestige_unlocked():
		_mark("prestige unlocked")


func _mark(event: String) -> void:
	if not seen.has(event):
		seen[event] = true
		milestones.append([clock, event])


func _report(seed_value: int) -> void:
	var minutes: float = clock / 60.0
	var finished: bool = core.perm.story_completed
	var in_window: bool = finished and minutes >= TARGET_MIN_MINUTES and minutes <= TARGET_MAX_MINUTES \
		and core.perm.total_rebirths >= MIN_REBIRTHS
	if not quiet:
		print("GachaNight balance simulation (seed %d)" % seed_value)
		for milestone in milestones:
			print("  %s  %s" % [Format.duration(milestone[0]), milestone[1]])
		var levels: Array = []
		for upgrade_id in core.data.upgrade_order:
			levels.append("%s %d" % [upgrade_id, core.perm.upgrade_level(upgrade_id)])
		print("  prestige upgrades: %s" % ", ".join(levels))
		print("  discovered %d/%d figures" % [core.discovered_count(), core.data.figure_order.size()])
	print("RESULT seed=%d finished=%s minutes=%.1f rebirths=%d target=%d-%d min, >=%d rebirths -> %s" % [
		seed_value, finished, minutes, core.perm.total_rebirths, int(TARGET_MIN_MINUTES), int(TARGET_MAX_MINUTES),
		MIN_REBIRTHS, "OK" if in_window else "OUT OF TARGET",
	])
	quit(0 if in_window else 1)
