extends SceneTree
## Headless rule tests. Run with:
##   godot --headless --path . -s tests/run_tests.gd
## Case numbers refer to section 23 of GachaNight_MASTER_DESIGN.md.

const GameCore = preload("res://scripts/core/game_core.gd")
const Machine = preload("res://scripts/services/machine_service.gd")
const SaveService = preload("res://scripts/services/save_service.gd")
const Format = preload("res://scripts/core/format.gd")

## Frozen tables, so rebalancing the game never changes what these tests assert.
const FIXTURE_DATA: String = "res://tests/data"
const M1: String = "machine_001"
const M2: String = "machine_002"

var _checks: int = 0
var _failures: Array = []
var _current: String = ""


func _init() -> void:
	var tests: Array = [
		"test_shipped_data", "test_data_tables", "test_start_of_run", "test_sell_credits_directly",
		"test_single_resolution", "test_low_funds_lock", "test_machine_002_and_return_to_001",
		"test_collection_per_figure", "test_completed_collection_blocks_keep",
		"test_discovery_is_permanent", "test_prestige_locked_until_machine_002",
		"test_sofa_cancel_changes_nothing", "test_rebirth_transaction",
		"test_rebirth_validation", "test_permanent_upgrades_affect_next_run",
		"test_save_and_load_mid_run", "test_save_backup_fallback", "test_luck_weights",
		"test_roll_distribution", "test_random_play_never_softlocks", "test_reception_purchases",
		"test_reception_resets_on_rebirth", "test_robots", "test_robots_respect_money",
		"test_express_lane", "test_exit_key_and_door", "test_special_machines", "test_number_format",
	]
	for test_name in tests:
		_current = test_name
		call(test_name)
	print("")
	if _failures.is_empty():
		print("ALL PASSED: %d checks in %d tests" % [_checks, tests.size()])
		quit(0)
	else:
		for failure in _failures:
			print("FAIL  %s" % failure)
		print("FAILED: %d of %d checks" % [_failures.size(), _checks])
		quit(1)


# --- Helpers ----------------------------------------------------------------

func check(condition: bool, message: String) -> void:
	_checks += 1
	if not condition:
		_failures.append("%s: %s" % [_current, message])


func check_eq(actual: Variant, expected: Variant, message: String) -> void:
	check(actual == expected, "%s (expected %s, got %s)" % [message, str(expected), str(actual)])


func save_path_for(name: String) -> String:
	return "user://test_%s.json" % name


func wipe(path: String) -> void:
	for suffix in ["", ".bak", ".tmp", ".unreadable"]:
		if FileAccess.file_exists(path + suffix):
			DirAccess.remove_absolute(path + suffix)


func new_core(name: String, fresh: bool = true) -> RefCounted:
	var path: String = save_path_for(name)
	if fresh:
		wipe(path)
	var core: RefCounted = GameCore.new()
	check(core.setup(path, FIXTURE_DATA), "core setup for %s" % name)
	return core


## A core past the bathroom: power on, floor coins collected, given coin balance.
func ready_core(name: String, coins: int) -> RefCounted:
	var core: RefCounted = new_core(name)
	core.turn_power_on()
	for index in range(3):
		core.collect_floor_coin(index)
	core.run.coins = coins
	return core


## Makes the next rolls of a machine land on one figure.
func force(core: RefCounted, machine_id: String, figure_id: String) -> void:
	var weights: Array = Machine.effective_weights(core.data, core.perm, core.run, machine_id)
	var total: float = 0.0
	for entry in weights:
		total += entry["weight"]
	var cumulative: float = 0.0
	for entry in weights:
		if entry["figure_id"] == figure_id:
			var roll: float = (cumulative + entry["weight"] / 2.0) / total
			core.rand_fn = func() -> float: return roll
			return
		cumulative += entry["weight"]
	check(false, "figure %s is not in %s" % [figure_id, machine_id])


func spin(core: RefCounted, machine_id: String, figure_id: String, choice: String) -> Dictionary:
	force(core, machine_id, figure_id)
	var played: Dictionary = core.play_machine(machine_id)
	if not played["ok"]:
		return played
	return core.resolve_prize(played["prize"]["transaction_id"], choice)


# --- Tests ------------------------------------------------------------------

## The real tables the game ships: they must load and keep the design's fixed values.
func test_shipped_data() -> void:
	var core: RefCounted = GameCore.new()
	wipe(save_path_for("shipped"))
	check(core.setup(save_path_for("shipped")), "shipped tables load")
	check_eq(core.data.errors, [], "shipped tables validate")
	check_eq(core.data.rarities.size(), 5, "exactly five rarities")
	check_eq(core.data.machine_order.size(), 4, "four machines")
	check_eq(core.data.machines[M1]["price_per_attempt"], 1, "machine 001 costs 1")
	check_eq(core.data.machines[M1]["prize_table"].size(), 5, "machine 001 has exactly 5 figures")
	check_eq(core.data.machines[M2]["price_per_attempt"], 50, "machine 002 costs 50")
	check(core.data.machines[M2]["min_sell_value"] >= 30, "machine 002 sells for >= 30")
	check(core.data.machines[M2]["unlocks_prestige"], "machine 002 unlocks prestige")
	check(core.data.exit_key_id != "", "the reception table has the exit key")
	for machine_id in core.data.machine_order:
		check(core.data.machines[machine_id]["min_sell_value"] >= 1, "%s never sells for less than 1" % machine_id)
		check(core.data.robot_item_for_machine(machine_id) != "", "%s has a robot item" % machine_id)
	for figure_id in core.data.figure_order:
		check(FileAccess.file_exists("res://assets/sprites/figures/%s.png" % figure_id), "%s has a sprite" % figure_id)


func test_data_tables() -> void:
	var core: RefCounted = new_core("data")
	check_eq(core.data.errors.size(), 0, "data tables validate")
	check_eq(core.data.rarities.size(), 5, "case 16: exactly five rarities")
	check_eq(core.data.machines[M1]["price_per_attempt"], 1, "case 1: machine 001 costs 1")
	check_eq(core.data.machines[M1]["prize_table"].size(), 5, "case 1: machine 001 has exactly 5 figures")
	check_eq(core.data.machines[M2]["price_per_attempt"], 50, "case 2: machine 002 costs 50")
	for entry in core.data.machines[M1]["prize_table"]:
		check(core.figure_view(entry["figure_id"])["sell_value"] >= 1, "case 1: %s sells for >= 1" % entry["figure_id"])
	for entry in core.data.machines[M2]["prize_table"]:
		check(core.figure_view(entry["figure_id"])["sell_value"] >= 30, "case 2: %s sells for >= 30" % entry["figure_id"])
	for figure_id in core.data.figure_order:
		check(core.data.rarities.has(core.data.figures[figure_id]["rarity_id"]), "case 16: %s uses a known rarity" % figure_id)


func test_start_of_run() -> void:
	var core: RefCounted = new_core("start")
	check_eq(core.run.coins, 0, "run starts with coins on the floor, not in the pocket")
	check_eq(core.can_play_machine(M1)["reason"], "power_off", "machines need the power switch")
	check(core.turn_power_on()["ok"], "power turns on")
	check(not core.turn_power_on()["ok"], "power cannot be turned on twice")
	for index in range(3):
		check(core.collect_floor_coin(index)["ok"], "floor coin %d collected" % index)
	check(not core.collect_floor_coin(0)["ok"], "a floor coin is collected only once")
	check(not core.collect_floor_coin(7)["ok"], "unknown floor coin rejected")
	check_eq(core.run.coins, 3, "first cycle starts with 3 coins")
	check_eq(core.discovered_count(), 0, "case 13: catalog starts with 0 discoveries")
	check_eq(core.data.figure_order.size(), 30, "case 13: catalog lists every planned figure")


func test_sell_credits_directly() -> void:
	var core: RefCounted = ready_core("sell", 3)
	force(core, M1, "g001_toy_03")
	var played: Dictionary = core.play_machine(M1)
	check(played["ok"], "spin accepted")
	check_eq(core.run.coins, 2, "price paid exactly once")
	check_eq(played["prize"]["sell_value"], 4, "prize shows its sale value")
	var sold: Dictionary = core.resolve_prize(played["prize"]["transaction_id"], "sell")
	check(sold["ok"], "sell accepted")
	check_eq(core.run.coins, 6, "case 5: sale credited immediately")
	check_eq(core.run.copies_held("g001_toy_03"), 0, "selling does not add a copy")


func test_single_resolution() -> void:
	var core: RefCounted = ready_core("single", 10)
	force(core, M1, "g001_toy_02")
	var played: Dictionary = core.play_machine(M1)
	var transaction_id: int = played["prize"]["transaction_id"]
	check_eq(core.play_machine(M1)["reason"], "prize_pending", "no new spin while a prize is pending")
	check_eq(core.run.coins, 9, "rejected spin does not charge")
	check_eq(core.resolve_prize(transaction_id + 99, "sell")["reason"], "transaction_mismatch", "wrong transaction rejected")
	check_eq(core.resolve_prize(transaction_id, "juggle")["reason"], "unknown_choice", "unknown choice rejected")
	check(core.resolve_prize(transaction_id, "keep")["ok"], "keep accepted")
	check_eq(core.resolve_prize(transaction_id, "keep")["reason"], "no_pending_prize", "case 6: second keep rejected")
	check_eq(core.resolve_prize(transaction_id, "sell")["reason"], "no_pending_prize", "case 6: cannot sell after keeping")
	check_eq(core.run.copies_held("g001_toy_02"), 1, "case 6: exactly one copy")
	check_eq(core.run.coins, 9, "case 6: no coins from the rejected sale")


func test_low_funds_lock() -> void:
	var core: RefCounted = ready_core("lowfunds", 3)
	force(core, M1, "g001_toy_01")
	var first: Dictionary = core.play_machine(M1)
	check(core.pending_prize_view()["keep"]["ok"], "3 coins: 2 left after paying, Keep allowed")
	core.resolve_prize(first["prize"]["transaction_id"], "keep")
	var second: Dictionary = core.play_machine(M1)
	check_eq(core.run.coins, 1, "1 coin left after paying")
	check_eq(core.pending_prize_view()["keep"]["reason"], "low_funds", "case 3: Keep disabled at <= 1 coin")
	check_eq(core.resolve_prize(second["prize"]["transaction_id"], "keep")["reason"], "low_funds", "case 3: core rejects Keep")
	check(core.run.has_pending_prize(), "rejected Keep leaves the prize pending")
	check(core.resolve_prize(second["prize"]["transaction_id"], "sell")["ok"], "Sell still works")
	check(core.run.coins >= 1, "case 4: player can afford machine 001 again")


func test_machine_002_and_return_to_001() -> void:
	var core: RefCounted = ready_core("m2", 49)
	check_eq(core.can_play_machine(M2)["reason"], "not_enough_coins", "49 coins cannot pay machine 002")
	core.run.coins = 50
	var sold: Dictionary = spin(core, M2, "g002_toy_01", "sell")
	check(sold["ok"], "machine 002 spin sold")
	check_eq(core.run.coins, 30, "case 2: worst prize sells for 30")
	check(core.can_play_machine(M1)["ok"], "case 2: can return to machine 001")
	check(not core.can_play_machine(M2)["ok"], "cannot afford machine 002 again yet")


func test_collection_per_figure() -> void:
	var core: RefCounted = ready_core("collection", 100)
	var completed: Array = []
	var bonuses: Array = []
	core.figure_collection_completed.connect(func(figure_id: String, _prestige: int) -> void: completed.append(figure_id))
	core.collection_bonus_activated.connect(func(figure_id: String) -> void: bonuses.append(figure_id))
	for copy in range(2):
		spin(core, M1, "g001_toy_03", "keep")
	check_eq(core.run.pending_prestige, 0, "case 9: no partial prestige")
	check_eq(core.active_bonus_views().size(), 0, "case 9: no partial bonus")
	var last: Dictionary = spin(core, M1, "g001_toy_03", "keep")
	check(last["completed"], "third rare copy completes its collection")
	check_eq(core.run.pending_prestige, 4, "case 10: prestige granted once")
	check_eq(completed, ["g001_toy_03"], "case 10: one completion event")
	check_eq(bonuses, ["g001_toy_03"], "case 10: one bonus activation")
	check(not core.figure_view("g001_toy_01")["completed"], "case 8: other figures stay incomplete")
	check_eq(core.figure_view("g001_toy_01")["copies_held"], 0, "case 8: other counters untouched")
	check_eq(core.perm.banked_prestige, 0, "pending prestige is not banked before the sofa")
	var single: Dictionary = spin(core, M1, "g001_toy_05", "keep")
	check(single["completed"], "a figure with copies_required 1 completes with one copy")
	check_eq(core.run.pending_prestige, 20, "legendary adds its own reward")


func test_completed_collection_blocks_keep() -> void:
	var core: RefCounted = ready_core("blocked", 100)
	for copy in range(2):
		spin(core, M1, "g001_toy_04", "keep")
	check(core.figure_view("g001_toy_04")["completed"], "epic collection completed with 2 copies")
	force(core, M1, "g001_toy_04")
	var played: Dictionary = core.play_machine(M1)
	check(played["ok"], "completed figures can still drop")
	check_eq(core.pending_prize_view()["keep"]["reason"], "collection_completed", "case 11: Keep disabled")
	check_eq(core.resolve_prize(played["prize"]["transaction_id"], "keep")["reason"], "collection_completed", "case 11: core rejects Keep")
	var coins_before: int = core.run.coins
	check(core.resolve_prize(played["prize"]["transaction_id"], "sell")["ok"], "case 11: Sell works")
	check(core.run.coins > coins_before, "duplicate sold for coins")
	check_eq(core.run.copies_held("g001_toy_04"), 2, "counter stays at its threshold")
	check_eq(core.run.pending_prestige, 8, "no extra prestige for duplicates")
	check_eq(core.active_bonus_views().size(), 1, "no extra bonus for duplicates")


func test_discovery_is_permanent() -> void:
	var core: RefCounted = ready_core("discovery", 60)
	var discovered: Array = []
	core.figure_discovered.connect(func(figure_id: String) -> void: discovered.append(figure_id))
	spin(core, M1, "g001_toy_02", "sell")
	spin(core, M1, "g001_toy_02", "sell")
	check_eq(discovered, ["g001_toy_02"], "discovery fires once per figure")
	check(core.figure_view("g001_toy_02")["discovered"], "case 14: a sold figure is discovered")
	check(not core.figure_view("g001_toy_01")["discovered"], "unseen figures stay hidden")
	spin(core, M1, "g001_toy_01", "keep")
	spin(core, M2, "g002_toy_01", "sell")
	check(core.confirm_rebirth({})["ok"], "rebirth accepted")
	check(core.figure_view("g001_toy_02")["discovered"], "case 14: discovery survives rebirth")
	check_eq(core.figure_view("g001_toy_01")["copies_held"], 0, "case 15: copies are not restored")
	var reloaded: RefCounted = new_core("discovery", false)
	check(reloaded.figure_view("g001_toy_02")["discovered"], "case 14: discovery survives restart")
	check_eq(reloaded.discovered_count(), 3, "three figures discovered in total")


func test_prestige_locked_until_machine_002() -> void:
	var core: RefCounted = ready_core("unlock", 200)
	var unlock_events: Array = []
	core.prestige_unlocked.connect(func() -> void: unlock_events.append(true))
	spin(core, M1, "g001_toy_05", "keep")
	check_eq(core.run.pending_prestige, 16, "points can be pending before the unlock")
	check(not core.is_prestige_unlocked(), "case 17: sofa locked before machine 002")
	check_eq(core.get_rebirth_quote({})["reason"], "prestige_locked", "case 17: quote rejected")
	check_eq(core.confirm_rebirth({})["reason"], "prestige_locked", "case 17: rebirth rejected")
	check_eq(core.run.pending_prestige, 16, "rejected rebirth keeps the run")
	spin(core, M2, "g002_toy_01", "sell")
	spin(core, M2, "g002_toy_01", "sell")
	check(core.is_prestige_unlocked(), "case 18: first use of machine 002 unlocks the sofa")
	check_eq(unlock_events.size(), 1, "unlock is announced once")
	check(core.confirm_rebirth({})["ok"], "rebirth works after the unlock")
	check(core.is_prestige_unlocked(), "case 18: sofa stays unlocked in later runs")
	check_eq(core.perm.banked_prestige, 16, "earlier pending points were banked")


func test_sofa_cancel_changes_nothing() -> void:
	var core: RefCounted = ready_core("cancel", 100)
	spin(core, M2, "g002_toy_01", "sell")
	core.perm.banked_prestige = 5
	var before_perm: Dictionary = core.perm.to_dict()
	var before_run: Dictionary = core.run.to_dict()
	var quoted: Dictionary = core.get_rebirth_quote({"better_appraisal": 2})
	check(quoted["ok"], "selection is affordable")
	check_eq(quoted["cost"], 4, "two levels cost 1 + 3")
	check_eq(quoted["remaining"], 1, "quote shows the remaining balance")
	check_eq(core.perm.to_dict(), before_perm, "case 20: quoting spends and applies nothing")
	check_eq(core.run.to_dict(), before_run, "case 20: quoting does not touch the run")


func test_rebirth_transaction() -> void:
	var core: RefCounted = ready_core("rebirth", 300)
	spin(core, M2, "g002_toy_01", "sell")
	spin(core, M1, "g001_toy_05", "keep")
	core.perm.banked_prestige = 4
	check_eq(core.prestige_available(), 20, "4 banked + 16 pending")
	var selection: Dictionary = {"better_appraisal": 3, "ready_pockets": 1}
	check_eq(core.get_rebirth_quote(selection)["cost"], 12, "cost is 1+3+6 plus 2")
	var done: Dictionary = core.confirm_rebirth({"better_appraisal": 3, "starting_tip": 2})
	check(done["ok"], "rebirth confirmed")
	check_eq(done["cost"], 18, "case 21: 10 + 8 spent")
	check_eq(core.perm.banked_prestige, 2, "case 21: unspent points are banked")
	check_eq(core.run.pending_prestige, 0, "pending prestige reset")
	check_eq(core.perm.upgrade_level("better_appraisal"), 3, "case 21: upgrade applied")
	check_eq(core.perm.total_rebirths, 1, "rebirth counted")
	check_eq(core.run.coins, 100, "case 22: coins reset to the starting amount")
	check(not core.run.power_switch_on, "case 22: power is off again")
	check_eq(core.run.copies_held("g001_toy_05"), 0, "case 22: copies reset")
	check_eq(core.active_bonus_views().size(), 0, "case 22: collection bonuses removed")
	check(not core.figure_view("g001_toy_05")["completed"], "case 22: completion flags cleared")
	check(core.figure_view("g001_toy_05")["discovered"], "case 22: discoveries kept")
	core.turn_power_on()
	core.run.coins = 10
	var again: Dictionary = spin(core, M1, "g001_toy_05", "keep")
	check(again["completed"], "case 12: the collection can be completed again")
	check_eq(core.run.pending_prestige, 16, "case 12: and rewards once more")
	# Case 23: 20 points, spend 15, keep 5 across a restart.
	var bank: RefCounted = ready_core("bank", 100)
	spin(bank, M2, "g002_toy_01", "sell")
	bank.perm.banked_prestige = 20
	var purchase: Dictionary = bank.confirm_rebirth({"better_appraisal": 3, "efficient_spending": 1, "ready_pockets": 1})
	check_eq(purchase.get("cost", -1), 15, "case 23: 10 + 3 + 2 spent")
	check_eq(bank.perm.banked_prestige, 5, "case 23: 5 points remain")
	var restarted: RefCounted = new_core("bank", false)
	check_eq(restarted.perm.banked_prestige, 5, "case 23: banked points survive a restart")
	check_eq(restarted.perm.upgrade_level("better_appraisal"), 3, "upgrades survive a restart")


func test_rebirth_validation() -> void:
	var core: RefCounted = ready_core("validation", 100)
	spin(core, M2, "g002_toy_01", "sell")
	core.perm.banked_prestige = 3
	check_eq(core.get_rebirth_quote({"better_appraisal": 3})["reason"], "not_enough_prestige", "cannot overspend")
	check_eq(core.get_rebirth_quote({"ready_pockets": 2})["reason"], "invalid_level", "cannot exceed max level")
	check_eq(core.get_rebirth_quote({"better_appraisal": -1})["reason"], "invalid_level", "negative levels rejected")
	check_eq(core.get_rebirth_quote({"nope": 1})["reason"], "unknown_upgrade", "unknown upgrade rejected")
	check_eq(core.get_rebirth_quote({"lucky_bearings": 1})["reason"], "missing_prerequisite", "prerequisite enforced")
	core.perm.banked_prestige = 4
	check(core.get_rebirth_quote({"lucky_bearings": 1, "better_appraisal": 1})["ok"], "prerequisite met within the same selection")
	check_eq(core.confirm_rebirth({"better_appraisal": 5})["reason"], "not_enough_prestige", "rejected rebirth")
	check_eq(core.perm.banked_prestige, 4, "case 32: rejected rebirth charges nothing")
	check_eq(core.perm.total_rebirths, 0, "rejected rebirth does not restart")
	force(core, M1, "g001_toy_01")
	core.play_machine(M1)
	check_eq(core.confirm_rebirth({})["reason"], "prize_pending", "cannot rebirth with a prize pending")


func test_permanent_upgrades_affect_next_run() -> void:
	var core: RefCounted = ready_core("upgrades", 100)
	spin(core, M2, "g002_toy_01", "sell")
	core.perm.banked_prestige = 10
	check_eq(core.figure_view("g002_toy_01")["sell_value"], 30, "base sale value")
	check(core.confirm_rebirth({"better_appraisal": 2, "ready_pockets": 1, "starting_tip": 1})["ok"], "rebirth with upgrades")
	check_eq(core.figure_view("g002_toy_01")["sell_value"], 45, "case 24: +50% sale value next run")
	check_eq(core.figure_view("g001_toy_01")["sell_value"], 1, "case 24: cheapest sale stays >= 1")
	check_eq(core.run.coins, 13, "Ready Pockets (3) + Starting Tip (10)")
	check(not core.collect_floor_coin(0)["ok"], "floor coins are already in the pocket")
	core.turn_power_on()
	core.run.coins = 200
	for copy in range(4):
		spin(core, M1, "g001_toy_02", "keep")
	check_eq(core.machine_price(M2), 48, "collection discount lowers machine 002 to 48")
	check_eq(core.machine_price(M1), 1, "machine 001 never drops below 1")


func test_save_and_load_mid_run() -> void:
	var core: RefCounted = ready_core("midrun", 80)
	spin(core, M1, "g001_toy_04", "keep")
	spin(core, M1, "g001_toy_04", "keep")
	spin(core, M2, "g002_toy_02", "keep")
	force(core, M1, "g001_toy_03")
	var played: Dictionary = core.play_machine(M1)
	var coins: int = core.run.coins
	var reloaded: RefCounted = new_core("midrun", false)
	check_eq(reloaded.load_source, "main", "save file found")
	check_eq(reloaded.run.coins, coins, "case 31: coins restored")
	check_eq(reloaded.run.copies_held("g001_toy_04"), 2, "case 31: copies restored")
	check(reloaded.figure_view("g001_toy_04")["completed"], "case 31: completion restored")
	check_eq(reloaded.run.pending_prestige, 8, "case 31: pending prestige not duplicated")
	check_eq(reloaded.active_bonus_views().size(), 1, "case 31: bonus restored once")
	check(reloaded.run.power_switch_on, "case 31: power state restored")
	check(reloaded.is_prestige_unlocked(), "case 31: prestige unlock restored")
	var view: Dictionary = reloaded.pending_prize_view()
	check_eq(view.get("figure_id", ""), "g001_toy_03", "case 7: the same prize is pending after a restart")
	check_eq(view.get("transaction_id", -1), played["prize"]["transaction_id"], "case 7: same transaction")
	check(reloaded.resolve_prize(view["transaction_id"], "sell")["ok"], "case 7: it resolves once")
	check_eq(reloaded.run.coins, coins + 4, "case 7: one sale, not two")
	check(not reloaded.resolve_prize(view["transaction_id"], "sell")["ok"], "case 7: no second resolution")


func test_save_backup_fallback() -> void:
	var core: RefCounted = ready_core("backup", 7)
	core.save()
	core.run.coins = 9
	core.save()
	var path: String = save_path_for("backup")
	check(FileAccess.file_exists(path + ".bak"), "previous save kept as backup")
	var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	file.store_string("{ this is not json")
	file.close()
	var recovered: RefCounted = new_core("backup", false)
	check_eq(recovered.load_source, "backup", "corrupt save falls back to the backup")
	check_eq(recovered.run.coins, 7, "backup state restored")
	check(FileAccess.file_exists(path + ".unreadable"), "corrupt save is preserved, not deleted")
	var missing: Dictionary = SaveService.load_save(save_path_for("does_not_exist"))
	check(not missing["ok"], "no save means a new game")


func test_luck_weights() -> void:
	var core: RefCounted = ready_core("luck", 100)
	var base: Array = Machine.effective_weights(core.data, core.perm, core.run, M1)
	core.perm.prestige_upgrade_levels["lucky_bearings"] = 3
	var lucky: Array = Machine.effective_weights(core.data, core.perm, core.run, M1)
	check_eq(lucky[0]["weight"], base[0]["weight"], "common weight is never removed")
	check(lucky[4]["weight"] > base[4]["weight"], "luck raises the top rarity")
	check_eq(Machine.pick_figure(base, 0.0), "g001_toy_01", "roll 0 lands on the first entry")
	check_eq(Machine.pick_figure(base, 0.999999), "g001_toy_05", "roll ~1 lands on the last entry")
	check_eq(Machine.pick_figure(base, 5.0), "g001_toy_05", "out-of-range roll is clamped")


func test_roll_distribution() -> void:
	var core: RefCounted = ready_core("distribution", 0)
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.seed = 20261011
	var weights: Array = Machine.effective_weights(core.data, core.perm, core.run, M1)
	var counts: Dictionary = {}
	var rolls: int = 20000
	for index in range(rolls):
		var figure_id: String = Machine.pick_figure(weights, rng.randf())
		counts[figure_id] = int(counts.get(figure_id, 0)) + 1
	for entry in weights:
		var expected: float = entry["weight"] / 100.0
		var actual: float = float(counts.get(entry["figure_id"], 0)) / rolls
		check(absf(actual - expected) < 0.015, "%s frequency %.3f is near %.3f" % [entry["figure_id"], actual, expected])


func test_random_play_never_softlocks() -> void:
	var core: RefCounted = ready_core("softlock", 3)
	core.autosave_enabled = false
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.seed = 8086
	core.rand_fn = func() -> float: return rng.randf()
	var stuck: int = 0
	for step in range(5000):
		var machine_id: String = M2 if core.can_play_machine(M2)["ok"] and rng.randf() < 0.5 else M1
		var played: Dictionary = core.play_machine(machine_id)
		if not played["ok"]:
			stuck += 1
			break
		var transaction_id: int = played["prize"]["transaction_id"]
		# Greedy collector: always tries Keep first, the worst case for the economy.
		if not core.resolve_prize(transaction_id, "keep")["ok"]:
			core.resolve_prize(transaction_id, "sell")
		if core.run.coins < 1 or core.run.has_pending_prize():
			stuck += 1
			break
	check_eq(stuck, 0, "case 4: a greedy collector never runs out of money")
	check(core.run.coins >= 1, "case 4: machine 001 is always affordable")

func test_reception_purchases() -> void:
	var core: RefCounted = ready_core("reception", 25)
	check_eq(core.data.reception_upgrades.size() > 0, true, "reception table loaded")
	check_eq(core.buy_reception_item("nope")["reason"], "unknown_item", "unknown item rejected")
	check_eq(core.buy_reception_item("price_tag_gun")["reason"], "keep_one_coin", "a purchase must leave one coin")
	check_eq(core.run.coins, 25, "rejected purchase charges nothing")
	core.run.coins = 24
	check_eq(core.buy_reception_item("price_tag_gun")["reason"], "not_enough_coins", "cannot overspend")
	core.run.coins = 26
	core.perm.banked_prestige = 7
	core.run.pending_prestige = 3
	var bought: Dictionary = core.buy_reception_item("price_tag_gun")
	check(bought["ok"], "purchase accepted")
	check_eq(core.run.coins, 1, "case 19: reception charges coins")
	check_eq(core.perm.banked_prestige, 7, "case 19: banked prestige untouched")
	check_eq(core.run.pending_prestige, 3, "case 19: pending prestige untouched")
	check_eq(core.run.reception_level("price_tag_gun"), 1, "level raised")
	check_eq(core.reception_item_view("price_tag_gun")["cost"], 100, "next level costs base * growth")
	check_eq(core.figure_view("g002_toy_01")["sell_value"], 34, "+15% sale value applies at once")
	check(core.can_play_machine(M1)["ok"], "case 4: machine 001 is still affordable")
	core.run.coins = 100000
	check_eq(core.buy_reception_item("robot_machine_002")["reason"], "missing_prerequisite", "robot needs its machine tried first")
	check(core.reception_item_view("robot_machine_002")["missing_en"].size() == 1, "missing requirement is described")
	check(core.buy_reception_item("express_lane")["ok"], "unique item bought")
	check_eq(core.buy_reception_item("express_lane")["reason"], "max_level", "unique item cannot be bought twice")
	check_eq(core.get_rebirth_quote({})["reason"], "prestige_locked", "reception never unlocks or spends prestige")


func test_reception_resets_on_rebirth() -> void:
	var core: RefCounted = ready_core("reception_reset", 1000000)
	spin(core, M2, "g002_toy_01", "sell")
	spin(core, M1, "g001_toy_01", "sell")
	core.buy_reception_item("price_tag_gun")
	core.buy_reception_item("robot_machine_001")
	core.buy_reception_item("faster_servos")
	core.set_robot_mode(M1, "sell_all")
	check_eq(core.robot_view(M1)["count"], 1, "robot owned")
	check(core.confirm_rebirth({})["ok"], "rebirth accepted")
	check_eq(core.run.reception_level("price_tag_gun"), 0, "case 22: reception upgrades are lost")
	check_eq(core.robot_view(M1)["count"], 0, "case 22: robots are lost")
	check_eq(core.robot_view(M1)["mode"], "collect", "case 22: robot settings are lost")
	check_eq(core.figure_view("g002_toy_01")["sell_value"], 30, "case 22: sale value back to base")
	check_eq(core.run.machines_used.size(), 0, "case 22: machine progress resets")
	core.turn_power_on()
	check_eq(core.tick(60.0)["spins"], 0, "no robot works after the rebirth")


func test_robots() -> void:
	var core: RefCounted = ready_core("robots", 5000)
	core.autosave_enabled = false
	check_eq(core.set_robot_mode(M1, "sell_all")["reason"], "no_robot", "no robot to configure yet")
	spin(core, M1, "g001_toy_01", "sell")
	check(core.buy_reception_item("robot_machine_001")["ok"], "robot bought with coins")
	check_eq(core.robot_view(M1)["count"], 1, "one robot on machine 001")
	check_eq(core.robot_view(M1)["spins_per_second"], 0.4, "one spin every 2.5 seconds")
	check_eq(core.set_robot_mode(M1, "dance")["reason"], "unknown_mode", "unknown mode rejected")
	force(core, M1, "g001_toy_03")
	check_eq(core.tick(1.0)["spins"], 0, "not enough time for a spin yet")
	var summary: Dictionary = core.tick(9.0)
	check_eq(summary["spins"], 4, "ten seconds make four spins")
	check_eq(core.run.copies_held("g001_toy_03"), 3, "case 26: collect mode keeps up to the threshold")
	check_eq(summary["completed"].size(), 1, "the robot completed the collection once")
	check_eq(core.run.pending_prestige, 4, "case 26: prestige granted once")
	check_eq(summary["coins_earned"], 4, "case 26: the duplicate was sold")
	check(not core.run.has_pending_prize(), "robots never leave a pending prize")
	core.set_robot_paused(M1, true)
	check_eq(core.tick(30.0)["spins"], 0, "a paused robot does nothing")
	core.set_robot_paused(M1, false)
	core.set_robot_mode(M1, "sell_all")
	force(core, M1, "g001_toy_02")
	core.tick(10.0)
	check_eq(core.run.copies_held("g001_toy_02"), 0, "sell_all mode keeps nothing")
	# A robot works beside a prize the player has not resolved, without touching it.
	force(core, M2, "g002_toy_02")
	var played: Dictionary = core.play_machine(M2)
	force(core, M1, "g001_toy_01")
	check(core.tick(5.0)["spins"] > 0, "robots keep working during a human prize")
	check_eq(core.pending_prize_view().get("figure_id", ""), "g002_toy_02", "the human prize is untouched")
	check(core.resolve_prize(played["prize"]["transaction_id"], "keep")["ok"], "and still resolves once")
	check(core.buy_reception_item("faster_servos")["ok"], "servos bought")
	check_eq(core.robot_view(M1)["spins_per_second"], 0.55, "+25% from servos on top of the +10% collection bonus")


func test_robots_respect_money() -> void:
	var core: RefCounted = ready_core("robot_money", 5000)
	core.autosave_enabled = false
	spin(core, M2, "g002_toy_01", "sell")
	check(core.buy_reception_item("robot_machine_002")["ok"], "robot on machine 002")
	core.run.coins = 49
	check_eq(core.tick(100.0)["spins"], 0, "case 27: a robot never spends coins the player lacks")
	check_eq(core.run.coins, 49, "case 27: balance untouched")
	core.run.coins = 50
	force(core, M2, "g002_toy_05")
	# The robot waited with one spin ready; it does not bank the time it could not pay for.
	var summary: Dictionary = core.tick(0.01)
	check_eq(summary["spins"], 1, "one spin once it is affordable")
	check_eq(core.run.copies_held("g002_toy_05"), 0, "case 27: low funds force a sale, even in collect mode")
	check_eq(core.run.coins, 500, "the prize was sold")
	# Greedy robots on every machine never strand the player.
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.seed = 4004
	core.rand_fn = func() -> float: return rng.randf()
	spin(core, M1, "g001_toy_01", "sell")
	core.run.coins = 2000
	core.buy_reception_item("robot_machine_001")
	for step in range(2000):
		core.tick(1.0)
		if core.run.coins < 1:
			break
	check(core.run.coins >= 1, "case 4: robots never leave the player without a coin")


func test_express_lane() -> void:
	var core: RefCounted = ready_core("express", 100000)
	spin(core, M1, "g001_toy_05", "keep")
	core.buy_reception_item("express_lane")
	var coins: int = core.run.coins
	force(core, M1, "g001_toy_05")
	var played: Dictionary = core.play_machine(M1)
	check(played["auto_sold"], "duplicate of a completed collection is sold on the spot")
	check(not core.run.has_pending_prize(), "no panel for it")
	check_eq(core.run.coins, coins - 1 + played["coins_gained"], "sale credited once")
	force(core, M1, "g001_toy_01")
	check(not core.play_machine(M1)["auto_sold"], "an incomplete figure still asks Sell or Keep")


func test_exit_key_and_door() -> void:
	var core: RefCounted = ready_core("ending", 100)
	var completed_events: Array = []
	core.story_completed.connect(func() -> void: completed_events.append(true))
	var key_id: String = core.data.exit_key_id
	check_eq(key_id, "store_exit_key", "the table defines the exit key")
	check_eq(core.use_exit_door()["reason"], "no_key", "case 29: the door stays shut without the key")
	core.run.coins = 9000000000000
	check_eq(core.buy_reception_item(key_id)["reason"], "missing_prerequisite", "the key has progress requirements")
	for machine_id in core.data.machine_order:
		force(core, machine_id, core.data.machines[machine_id]["prize_table"][0]["figure_id"])
		var played: Dictionary = core.play_machine(machine_id)
		core.resolve_prize(played["prize"]["transaction_id"], "sell")
	var cost: int = core.reception_item_view(key_id)["cost"]
	core.run.coins = cost
	check_eq(core.buy_reception_item(key_id)["reason"], "keep_one_coin", "even the key leaves one coin")
	core.run.coins = cost + 1
	check(core.buy_reception_item(key_id)["ok"], "key bought with coins")
	check(core.run.key_owned_this_run, "key owned this run")
	check(not core.perm.story_completed, "case 28: buying the key does not end the story")
	check_eq(completed_events.size(), 0, "case 28: no ending yet")
	check_eq(core.buy_reception_item(key_id)["reason"], "max_level", "only one key")
	var opened: Dictionary = core.use_exit_door()
	check(opened["ok"] and opened["first_time"], "case 29: the door opens with the key")
	check(core.perm.story_completed and core.perm.free_play_unlocked, "case 30: story completed, Free Play unlocked")
	check(not core.use_exit_door()["first_time"], "case 29: the ending is announced once")
	check_eq(completed_events.size(), 1, "one completion event")
	var discovered: int = core.discovered_count()
	check(core.confirm_rebirth({})["ok"], "rebirth still works in Free Play")
	check(core.perm.story_completed and core.perm.free_play_unlocked, "case 30: flags survive a rebirth")
	check(not core.run.key_owned_this_run, "the key belongs to the run and is lost")
	check_eq(core.use_exit_door()["reason"], "no_key", "a new run needs a new key")
	check_eq(core.discovered_count(), discovered, "case 30: the catalog is kept")
	var reloaded: RefCounted = new_core("ending", false)
	check(reloaded.perm.story_completed and reloaded.perm.free_play_unlocked, "case 30: flags survive a restart")


func test_special_machines() -> void:
	var core: RefCounted = ready_core("special", 0)
	check_eq(core.data.machine_order.size(), 6, "six machines")
	var types: Array = []
	for machine_id in core.data.machine_order:
		types.append(core.data.machines[machine_id]["machine_type"])
	check_eq(types, ["gacha", "gacha", "gacha", "gacha", "claw", "plinko"], "machine order matches the design")
	core.run.coins = core.machine_price("machine_006")
	force(core, "machine_006", "g006_toy_04")
	var played: Dictionary = core.play_machine("machine_006")
	check(played["ok"], "plinko uses the same prize flow")
	check_eq(played["slot"], 3, "the result names the slot the ball must land in")
	check(core.resolve_prize(played["prize"]["transaction_id"], "sell")["ok"], "plinko prize sells")
	check(core.run.coins >= core.data.machines["machine_006"]["min_sell_value"], "worst case still pays the minimum")
	for machine_id in core.data.machine_order:
		var machine: Dictionary = core.data.machines[machine_id]
		check(machine["min_sell_value"] >= 1, "%s always pays for another spin of machine 001" % machine_id)


func test_number_format() -> void:
	check_eq(Format.number(0), "0", "zero")
	check_eq(Format.number(9999), "9999", "small numbers stay exact")
	check_eq(Format.number(15000), "15K", "thousands")
	check_eq(Format.number(1250000), "1.25M", "millions")
	check_eq(Format.number(25000000), "25M", "tens of millions")
	check_eq(Format.number(5000000000), "5B", "billions")
	check_eq(Format.coins(1), "1 coin", "singular")
	check_eq(Format.coins(2), "2 coins", "plural")
