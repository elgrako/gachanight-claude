extends RefCounted
## Safe save files: write to a temp file, verify it, keep the previous save as .bak.
## An unreadable save is copied aside, never deleted.

const SCHEMA_VERSION: int = 1


static func save(path: String, payload: Dictionary) -> bool:
	var document: Dictionary = payload.duplicate(true)
	document["save_schema_version"] = SCHEMA_VERSION
	var text: String = JSON.stringify(document, "\t")
	var temp_path: String = path + ".tmp"
	var file: FileAccess = FileAccess.open(temp_path, FileAccess.WRITE)
	if file == null:
		return false
	file.store_string(text)
	file.close()
	if typeof(JSON.parse_string(FileAccess.get_file_as_string(temp_path))) != TYPE_DICTIONARY:
		return false
	if FileAccess.file_exists(path):
		DirAccess.copy_absolute(path, path + ".bak")
		DirAccess.remove_absolute(path)
	return DirAccess.rename_absolute(temp_path, path) == OK


## Returns {ok, data, source} where source is "none", "main" or "backup".
static func load_save(path: String) -> Dictionary:
	var main: Dictionary = _read(path)
	if main["ok"]:
		return {"ok": true, "data": main["data"], "source": "main"}
	if main["exists"]:
		DirAccess.copy_absolute(path, path + ".unreadable")
	var backup: Dictionary = _read(path + ".bak")
	if backup["ok"]:
		return {"ok": true, "data": backup["data"], "source": "backup"}
	return {"ok": false, "data": {}, "source": "none"}


static func _read(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {"ok": false, "exists": false, "data": {}}
	# JSON.parse reports failure through its return value instead of logging an engine error.
	var json: JSON = JSON.new()
	if json.parse(FileAccess.get_file_as_string(path)) != OK or typeof(json.data) != TYPE_DICTIONARY:
		return {"ok": false, "exists": true, "data": {}}
	var parsed: Dictionary = json.data
	var version: int = int(parsed.get("save_schema_version", 0))
	if version < 1 or version > SCHEMA_VERSION:
		return {"ok": false, "exists": true, "data": {}}
	return {"ok": true, "exists": true, "data": parsed}
