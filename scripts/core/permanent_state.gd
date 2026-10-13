extends RefCounted
## State that survives rebirths (design section 19.4).

var discoveries: Dictionary = {}  # figure_id -> true
var prestige_upgrade_levels: Dictionary = {}  # upgrade_id -> int
var banked_prestige: int = 0
var total_rebirths: int = 0
var tutorial_m2_used: bool = false
var story_completed: bool = false
var free_play_unlocked: bool = false
## The opening was played: the first evening, up to dozing off on the sofa.
var intro_seen: bool = false
## The manager's note at the reception was read.
var note_read: bool = false
var total_playtime_seconds: float = 0.0
## Total playtime when the story was first completed (0 until then).
var story_playtime_seconds: float = 0.0
var settings: Dictionary = {}


func upgrade_level(upgrade_id: String) -> int:
	return int(prestige_upgrade_levels.get(upgrade_id, 0))


func to_dict() -> Dictionary:
	return {
		"discoveries": discoveries.keys(),
		"prestige_upgrade_levels": prestige_upgrade_levels.duplicate(),
		"banked_prestige": banked_prestige,
		"total_rebirths": total_rebirths,
		"tutorial_m2_used": tutorial_m2_used,
		"story_completed": story_completed,
		"free_play_unlocked": free_play_unlocked,
		"intro_seen": intro_seen,
		"note_read": note_read,
		"total_playtime_seconds": total_playtime_seconds,
		"story_playtime_seconds": story_playtime_seconds,
		"settings": settings.duplicate(true),
	}


func from_dict(source: Dictionary) -> void:
	discoveries.clear()
	for figure_id in source.get("discoveries", []):
		discoveries[str(figure_id)] = true
	prestige_upgrade_levels.clear()
	var levels: Dictionary = source.get("prestige_upgrade_levels", {})
	for upgrade_id in levels:
		prestige_upgrade_levels[str(upgrade_id)] = int(levels[upgrade_id])
	banked_prestige = maxi(0, int(source.get("banked_prestige", 0)))
	total_rebirths = maxi(0, int(source.get("total_rebirths", 0)))
	tutorial_m2_used = bool(source.get("tutorial_m2_used", false))
	story_completed = bool(source.get("story_completed", false))
	free_play_unlocked = bool(source.get("free_play_unlocked", false))
	intro_seen = bool(source.get("intro_seen", false))
	note_read = bool(source.get("note_read", false))
	total_playtime_seconds = maxf(0.0, float(source.get("total_playtime_seconds", 0.0)))
	story_playtime_seconds = maxf(0.0, float(source.get("story_playtime_seconds", 0.0)))
	settings = source.get("settings", {}).duplicate(true)
