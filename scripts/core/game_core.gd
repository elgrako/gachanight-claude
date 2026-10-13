extends RefCounted
## Scene-independent game rules. Presentation calls this API and listens to its
## signals; it never writes coins, copies or prestige directly.

const GameData = preload("res://scripts/core/game_data.gd")
const PermanentState = preload("res://scripts/core/permanent_state.gd")
const RunState = preload("res://scripts/core/run_state.gd")
const Economy = preload("res://scripts/services/economy_service.gd")
const Collection = preload("res://scripts/services/collection_service.gd")
const Machine = preload("res://scripts/services/machine_service.gd")
const Prestige = preload("res://scripts/services/prestige_service.gd")
const Reception = preload("res://scripts/services/reception_service.gd")
const Automation = preload("res://scripts/services/automation_service.gd")
const SaveService = preload("res://scripts/services/save_service.gd")

const DEFAULT_SAVE_PATH: String = "user://gachanight_save.json"
const DEFAULT_SETTINGS: Dictionary = {
	"master_volume": 0.8, "music_volume": 0.6, "mouse_sensitivity": 1.0, "fullscreen": false, "head_bob": true,
}

signal coins_changed(coins: int)
signal figure_discovered(figure_id: String)
signal prize_pending(prize: Dictionary)
signal prize_resolved(result: Dictionary)
signal figure_collection_completed(figure_id: String, prestige: int)
signal collection_bonus_activated(figure_id: String)
signal prestige_available_changed(available: int)
signal prestige_unlocked
signal rebirth_confirmed
signal run_started
signal power_changed(is_on: bool)
signal floor_coin_collected(index: int)
signal reception_item_bought(item_id: String, level: int)
signal robot_state_changed(machine_id: String)
signal automation_ticked(summary: Dictionary)
signal modifiers_changed
signal store_key_bought
signal story_completed
signal settings_changed

var data: RefCounted
var perm: RefCounted
var run: RefCounted
var save_path: String = DEFAULT_SAVE_PATH
var autosave_enabled: bool = true
var load_source: String = "none"
## Optional source of rolls in [0, 1), for deterministic tests and simulations.
var rand_fn: Callable = Callable()

var _rng: RandomNumberGenerator = RandomNumberGenerator.new()


## data_dir lets tests run the rules on their own frozen tables.
func setup(p_save_path: String = DEFAULT_SAVE_PATH, data_dir: String = "res://data") -> bool:
	data = GameData.new()
	if not data.load_all(data_dir):
		for message in data.errors:
			push_error("GachaNight data: %s" % message)
		return false
	save_path = p_save_path
	_rng.randomize()
	perm = PermanentState.new()
	var loaded: Dictionary = SaveService.load_save(save_path)
	load_source = loaded["source"]
	if loaded["ok"]:
		perm.from_dict(loaded["data"].get("permanent", {}))
		run = RunState.new()
		run.from_dict(loaded["data"].get("run", {}))
		_sanitize_loaded_state()
	else:
		_start_new_run()
	return true


func save() -> bool:
	return SaveService.save(save_path, {"permanent": perm.to_dict(), "run": run.to_dict()})


func add_playtime(seconds: float) -> void:
	run.run_playtime_seconds += seconds
	perm.total_playtime_seconds += seconds


# --- Start of run -----------------------------------------------------------

## The opening is over: the player dozed off on the sofa.
func finish_intro() -> void:
	perm.intro_seen = true
	_autosave()


## The manager's note was read.
func read_note() -> void:
	perm.note_read = true
	_autosave()


func turn_power_on() -> Dictionary:
	if run.power_switch_on:
		return {"ok": false, "reason": "already_on"}
	run.power_switch_on = true
	power_changed.emit(true)
	_autosave()
	return {"ok": true, "reason": ""}


func collect_floor_coin(index: int) -> Dictionary:
	if index < 0 or index >= RunState.FLOOR_COIN_COUNT:
		return {"ok": false, "reason": "unknown_coin"}
	if run.floor_coins_collected[index]:
		return {"ok": false, "reason": "already_collected"}
	run.floor_coins_collected[index] = true
	run.coins += 1
	floor_coin_collected.emit(index)
	coins_changed.emit(run.coins)
	_autosave()
	return {"ok": true, "reason": ""}


# --- Machines and prizes ----------------------------------------------------

func machine_price(machine_id: String) -> int:
	return Economy.machine_price(data, perm, run, machine_id)


func can_play_machine(machine_id: String) -> Dictionary:
	return Machine.can_play(data, perm, run, machine_id)


## One play by the player. `extra_luck_pct` is what their timing earned on
## this play (capsule machines); robots and the simulated player pass nothing.
func play_machine(machine_id: String, extra_luck_pct: float = 0.0) -> Dictionary:
	var result: Dictionary = Machine.play(data, perm, run, machine_id, _roll(), extra_luck_pct)
	if not result["ok"]:
		return result
	result["slot"] = Machine.prize_slot(data, machine_id, result["figure_id"])
	coins_changed.emit(run.coins)
	if result["newly_discovered"]:
		figure_discovered.emit(result["figure_id"])
	if result["prestige_unlocked_now"]:
		prestige_unlocked.emit()
	if not result["auto_sold"]:
		prize_pending.emit(result["prize"])
	_autosave()
	return result


func resolve_prize(transaction_id: int, choice: String) -> Dictionary:
	var result: Dictionary = Machine.resolve(data, perm, run, transaction_id, choice)
	if not result["ok"]:
		return result
	if result["choice"] == "sell":
		coins_changed.emit(run.coins)
	elif result["completed"]:
		_announce_completion(result["figure_id"], result["prestige"])
	prize_resolved.emit(result)
	_autosave()
	return result


## The pending prize plus everything the prize panel needs, or {} when there is none.
func pending_prize_view() -> Dictionary:
	if not run.has_pending_prize():
		return {}
	var view: Dictionary = run.pending_prize.duplicate()
	view["figure"] = figure_view(view["figure_id"])
	view["keep"] = Collection.can_keep(data, run, run.pending_prize)
	return view


func crank_speed_multiplier() -> float:
	return Economy.crank_speed_multiplier(data, perm, run)


# --- Catalog and bonuses ----------------------------------------------------

func figure_view(figure_id: String) -> Dictionary:
	var figure: Dictionary = data.figures[figure_id]
	var rarity: Dictionary = data.rarities[figure["rarity_id"]]
	return {
		"id": figure_id,
		"discovered": perm.discoveries.has(figure_id),
		"name_en": figure["name_en"],
		"rarity_id": figure["rarity_id"],
		"rarity_name_en": rarity["name_en"],
		"rarity_color": rarity["color"],
		"copies_held": run.copies_held(figure_id),
		"copies_required": Collection.copies_required(data, figure_id),
		"completed": Collection.is_completed(data, run, figure_id),
		"sell_value": Economy.sell_value(data, perm, run, figure_id),
		"prestige_reward": Economy.prestige_reward(data, perm, figure_id),
		"bonus_text_en": bonus_text(figure_id),
		"machine_ids": data.figure_machine_ids(figure_id),
		"look": figure["look"],
	}


func bonus_text(figure_id: String) -> String:
	var figure: Dictionary = data.figures[figure_id]
	return effect_text(figure["collection_bonus_id"], float(figure["collection_bonus_params"].get("value", 0)))


static func effect_text(effect_type: String, value: float) -> String:
	match effect_type:
		"sell_value_pct":
			return "+%d%% sale value" % int(value)
		"price_discount_pct":
			return "-%d%% machine prices" % int(value)
		"luck_pct":
			return "+%d%% luck" % int(value)
		"robot_speed_pct":
			return "+%d%% robot speed" % int(value)
		"crank_speed_pct":
			return "+%d%% prize speed" % int(value)
		"prestige_gain_pct":
			return "+%d%% prestige" % int(value)
		"machine_luck_pct":
			return "+%d%% luck here" % int(value)
		"qte_zone_pct":
			return "+%d%% sweet spot" % int(value)
		"qte_slow_pct":
			return "-%d%% wheel speed" % int(value)
	return ""


func active_bonus_views() -> Array:
	var result: Array = []
	for figure_id in run.active_collection_bonuses:
		if data.figures.has(figure_id):
			result.append({"figure_id": figure_id, "source_en": data.figures[figure_id]["name_en"], "text_en": bonus_text(figure_id)})
	return result


## Current totals from every source, for the "active bonuses" summary.
func modifier_summary() -> Dictionary:
	return {
		"sell_multiplier": Economy.multiplier(data, perm, run, "sell_value_pct"),
		"price_discount_pct": clampf(Economy.additive(data, perm, run, "price_discount_pct"), 0.0, Economy.MAX_PRICE_DISCOUNT_PCT),
		"luck_pct": Economy.luck_pct(data, perm, run),
		"robot_speed_multiplier": Economy.robot_speed_multiplier(data, perm, run),
	}


func discovered_count() -> int:
	var count: int = 0
	for figure_id in data.figure_order:
		if perm.discoveries.has(figure_id):
			count += 1
	return count


# --- Reception --------------------------------------------------------------

## Everything the terminal needs to draw one item.
func reception_item_view(item_id: String) -> Dictionary:
	var item: Dictionary = data.reception_upgrades[item_id]
	var check: Dictionary = Reception.can_buy(data, run, item_id)
	return {
		"id": item_id,
		"category": item["category"],
		"display_name_en": item["display_name_en"],
		"description_en": item["description_en"],
		"level": run.reception_level(item_id),
		"max_level": item["max_level"],
		"cost": check["cost"],
		"can_buy": check["ok"],
		"reason": check["reason"],
		"missing_en": Reception.missing_prerequisites(data, run, item_id),
		"robot_machine_id": item["robot_machine_id"],
		"machine_id": item["machine_id"],
		"is_store_exit_key": item["is_store_exit_key"],
	}


## The upgrades sold at one machine, each as its terminal view plus what one
## level gives ("effect_en") and what the levels owned give ("total_en").
func machine_upgrade_views(machine_id: String) -> Array:
	var views: Array = []
	for item_id in data.reception_order:
		var item: Dictionary = data.reception_upgrades[item_id]
		if item["machine_id"] != machine_id:
			continue
		var view: Dictionary = reception_item_view(item_id)
		var effect: Dictionary = item["effects"][0] if not item["effects"].is_empty() else {}
		view["effect_en"] = effect_text(effect["type"], effect["per_level"]) if not effect.is_empty() else ""
		view["total_en"] = effect_text(effect["type"], GameData.effect_value(effect, view["level"])) if not effect.is_empty() and view["level"] > 0 else ""
		views.append(view)
	return views


## What the upgrades bought for a machine add up to, for one effect.
func machine_effect(machine_id: String, effect_type: String) -> float:
	return Economy.machine_effect(data, run, machine_id, effect_type)


func buy_reception_item(item_id: String) -> Dictionary:
	var result: Dictionary = Reception.buy(data, run, item_id)
	if not result["ok"]:
		return result
	coins_changed.emit(run.coins)
	reception_item_bought.emit(item_id, result["level"])
	modifiers_changed.emit()
	if result["robot_machine_id"] != "":
		robot_state_changed.emit(result["robot_machine_id"])
	if result["bought_key"]:
		store_key_bought.emit()
	_autosave()
	return result


# --- Robots -----------------------------------------------------------------

func robot_view(machine_id: String) -> Dictionary:
	var state: Dictionary = run.robots.get(machine_id, {"mode": "collect", "paused": false, "progress": 0.0})
	return {
		"machine_id": machine_id,
		"count": Reception.robot_count(data, run, machine_id),
		"mode": state["mode"],
		"paused": state["paused"],
		"spins_per_second": Automation.spins_per_second(data, perm, run, machine_id),
	}


func set_robot_mode(machine_id: String, mode: String) -> Dictionary:
	if Reception.robot_count(data, run, machine_id) <= 0:
		return {"ok": false, "reason": "no_robot"}
	if not RunState.ROBOT_MODES.has(mode):
		return {"ok": false, "reason": "unknown_mode"}
	run.robot_state(machine_id)["mode"] = mode
	robot_state_changed.emit(machine_id)
	_autosave()
	return {"ok": true, "reason": ""}


func set_robot_paused(machine_id: String, paused: bool) -> Dictionary:
	if Reception.robot_count(data, run, machine_id) <= 0:
		return {"ok": false, "reason": "no_robot"}
	run.robot_state(machine_id)["paused"] = paused
	robot_state_changed.emit(machine_id)
	_autosave()
	return {"ok": true, "reason": ""}


## Advances the robots. Called every frame by the Game autoload; saving is left
## to the periodic autosave so a busy store does not write a file per spin.
func tick(delta: float) -> Dictionary:
	var summary: Dictionary = Automation.tick(data, perm, run, delta, _roll)
	if summary["spins"] <= 0:
		return summary
	coins_changed.emit(run.coins)
	for figure_id in summary["discovered"]:
		figure_discovered.emit(figure_id)
	if summary["prestige_unlocked"]:
		prestige_unlocked.emit()
	for completion in summary["completed"]:
		_announce_completion(completion["figure_id"], completion["prestige"])
	automation_ticked.emit(summary)
	return summary


# --- Prestige ---------------------------------------------------------------

func is_prestige_unlocked() -> bool:
	return Prestige.is_unlocked(perm)


func prestige_available() -> int:
	return Prestige.available(perm, run)


func get_rebirth_quote(selection: Dictionary) -> Dictionary:
	return Prestige.quote(data, perm, run, selection)


## Sleep & Rebirth: charges the selection, applies it and restarts the run as one step.
func confirm_rebirth(selection: Dictionary) -> Dictionary:
	if run.has_pending_prize():
		return {"ok": false, "reason": "prize_pending"}
	var quoted: Dictionary = Prestige.quote(data, perm, run, selection)
	if not quoted["ok"]:
		return quoted
	Prestige.apply(perm, run, selection, quoted["cost"])
	_start_new_run()
	quoted["saved"] = save()
	rebirth_confirmed.emit()
	run_started.emit()
	coins_changed.emit(run.coins)
	power_changed.emit(run.power_switch_on)
	prestige_available_changed.emit(prestige_available())
	modifiers_changed.emit()
	return quoted


# --- Ending -----------------------------------------------------------------

## Using the front door. Reasons: "no_key". first_time is true only for the
## run that completes the story.
func use_exit_door() -> Dictionary:
	if not run.key_owned_this_run:
		return {"ok": false, "reason": "no_key", "first_time": false}
	var first_time: bool = not perm.story_completed
	perm.story_completed = true
	perm.free_play_unlocked = true
	if first_time:
		perm.story_playtime_seconds = perm.total_playtime_seconds
		story_completed.emit()
	save()
	return {"ok": true, "reason": "", "first_time": first_time}


# --- Settings ---------------------------------------------------------------

func setting(key: String) -> Variant:
	return perm.settings.get(key, DEFAULT_SETTINGS.get(key))


func set_setting(key: String, value: Variant) -> void:
	if not DEFAULT_SETTINGS.has(key):
		return
	perm.settings[key] = value
	settings_changed.emit()


# --- Internals --------------------------------------------------------------

func _announce_completion(figure_id: String, prestige: int) -> void:
	figure_collection_completed.emit(figure_id, prestige)
	collection_bonus_activated.emit(figure_id)
	prestige_available_changed.emit(prestige_available())
	modifiers_changed.emit()


func _start_new_run() -> void:
	run = RunState.new()
	run.coins = Economy.starting_coins(data, perm)
	if Economy.starts_with_floor_coins(data, perm):
		run.coins += RunState.FLOOR_COIN_COUNT
		run.floor_coins_collected = [true, true, true]


func _sanitize_loaded_state() -> void:
	# A save may reference content removed from the data tables; never crash on it.
	if run.has_pending_prize() and not data.figures.has(run.pending_prize["figure_id"]):
		run.coins += maxi(1, int(run.pending_prize["sell_value"]))
		run.pending_prize = {}
	for figure_id in run.figure_copies_held.keys():
		if not data.figures.has(figure_id):
			run.figure_copies_held.erase(figure_id)
	for upgrade_id in perm.prestige_upgrade_levels.keys():
		if not data.prestige_upgrades.has(upgrade_id):
			continue
		var max_level: int = int(data.prestige_upgrades[upgrade_id]["max_level"])
		perm.prestige_upgrade_levels[upgrade_id] = clampi(perm.upgrade_level(upgrade_id), 0, max_level)
	for item_id in run.reception_levels.keys():
		if not data.reception_upgrades.has(item_id):
			run.reception_levels.erase(item_id)
			continue
		var item_max: int = int(data.reception_upgrades[item_id]["max_level"])
		run.reception_levels[item_id] = clampi(run.reception_level(item_id), 0, item_max)
	for machine_id in run.robots.keys():
		if not data.machines.has(machine_id):
			run.robots.erase(machine_id)


func _roll() -> float:
	if rand_fn.is_valid():
		return float(rand_fn.call())
	return _rng.randf()


func _autosave() -> void:
	if autosave_enabled:
		save()
