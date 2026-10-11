extends Node
## Autoload "Audio": sound effects, store hum and music. Reacts to core
## signals for anything the rules decide; the world and UI call play() for
## presentation-only sounds.

const AUDIO_DIR: String = "res://assets/audio/"
const EFFECTS: Array = [
	"coin", "crank", "capsule", "sell", "keep", "complete", "switch", "click", "buy", "error",
	"robot", "plinko", "unlock", "rebirth", "door",
]
const POOL_SIZE: int = 8
const ROBOT_SOUND_INTERVAL: float = 0.3

var _streams: Dictionary = {}
var _pool: Array = []
var _next_player: int = 0
var _music: AudioStreamPlayer
var _ambient: AudioStreamPlayer
var _robot_cooldown: float = 0.0
var _core: RefCounted


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for effect in EFFECTS:
		_streams[effect] = _load(effect, false)
	for index in range(POOL_SIZE):
		var player: AudioStreamPlayer = AudioStreamPlayer.new()
		add_child(player)
		_pool.append(player)
	_music = AudioStreamPlayer.new()
	add_child(_music)
	_ambient = AudioStreamPlayer.new()
	_ambient.stream = _load("ambient", true)
	_ambient.volume_db = -14.0
	add_child(_ambient)
	_core = Game.core
	if _core == null or _core.run == null:
		return
	_core.floor_coin_collected.connect(func(_index: int) -> void: play("coin", 0.0, 0.08))
	_core.power_changed.connect(_on_power_changed)
	_core.prize_resolved.connect(func(result: Dictionary) -> void: play("sell" if result["choice"] == "sell" else "keep"))
	_core.figure_collection_completed.connect(func(_figure_id: String, _prestige: int) -> void: play("complete"))
	_core.prestige_unlocked.connect(func() -> void: play("unlock"))
	_core.reception_item_bought.connect(func(_item_id: String, _level: int) -> void: play("buy"))
	_core.rebirth_confirmed.connect(func() -> void: play("rebirth"))
	_core.automation_ticked.connect(_on_automation_ticked)
	_core.settings_changed.connect(apply_settings)
	apply_settings()
	if _core.run.power_switch_on:
		_start_store_sound(false)


func _process(delta: float) -> void:
	_robot_cooldown = maxf(0.0, _robot_cooldown - delta)


func play(effect: String, volume_db: float = 0.0, pitch_jitter: float = 0.0) -> void:
	var stream: AudioStream = _streams.get(effect)
	if stream == null:
		return
	var player: AudioStreamPlayer = _pool[_next_player]
	_next_player = (_next_player + 1) % POOL_SIZE
	player.stream = stream
	player.volume_db = volume_db
	player.pitch_scale = 1.0 + randf_range(-pitch_jitter, pitch_jitter)
	player.play()


func play_music(track: String) -> void:
	var stream: AudioStream = _load(track, true)
	if stream == null:
		return
	_music.stream = stream
	_music.play()


func stop_music() -> void:
	_music.stop()


func resume_store_music() -> void:
	if _core != null and _core.run.power_switch_on:
		play_music("music")


func apply_settings() -> void:
	var master: float = clampf(float(_core.setting("master_volume")), 0.0, 1.0)
	var music: float = clampf(float(_core.setting("music_volume")), 0.0, 1.0)
	AudioServer.set_bus_mute(0, master <= 0.001)
	AudioServer.set_bus_volume_db(0, linear_to_db(maxf(master, 0.001)))
	_music.volume_db = linear_to_db(maxf(music, 0.001)) - 8.0


func _on_power_changed(is_on: bool) -> void:
	if is_on:
		play("switch")
		_start_store_sound(true)
	else:
		_ambient.stop()
		_music.stop()


func _start_store_sound(delayed: bool) -> void:
	_ambient.play()
	if delayed:
		# The tune joins once the lights have finished coming on.
		await get_tree().create_timer(1.6).timeout
		if not _core.run.power_switch_on:
			return
	play_music("music")


func _on_automation_ticked(_summary: Dictionary) -> void:
	if _robot_cooldown <= 0.0:
		_robot_cooldown = ROBOT_SOUND_INTERVAL
		play("robot", -16.0, 0.15)


func _load(effect: String, looped: bool) -> AudioStream:
	var path: String = "%s%s.wav" % [AUDIO_DIR, effect]
	if not ResourceLoader.exists(path):
		return null
	var stream: AudioStream = load(path)
	if looped and stream is AudioStreamWAV:
		stream = stream.duplicate()
		stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
		stream.loop_begin = 0
		stream.loop_end = int(stream.get_length() * stream.mix_rate)
	return stream
