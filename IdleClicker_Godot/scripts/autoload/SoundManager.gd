extends Node

var sounds: Dictionary = {}
var sound_players: Array = []
const POOL_SIZE: int = 8

# Dozwolone są wyłącznie dźwięki ataku
const ALLOWED_ATTACK_SOUNDS: Array = ["sword_swing", "hit", "crit_hit", "enemy_hit"]

func _ready():
	_load_sound("sword_swing", "res://assets/sounds/sword_swing.wav")
	_load_sound("hit", "res://assets/sounds/hit.wav")
	_load_sound("crit_hit", "res://assets/sounds/crit_hit.wav")
	_load_sound("enemy_hit", "res://assets/sounds/enemy_hit.wav")

	for i in range(POOL_SIZE):
		var p = AudioStreamPlayer.new()
		add_child(p)
		sound_players.append(p)

func _load_sound(sound_name: String, path: String):
	if ResourceLoader.exists(path):
		var s = load(path)
		if s is AudioStream:
			sounds[sound_name] = s

func play(sound_name: String, pitch_range: float = 0.05):
	if not ALLOWED_ATTACK_SOUNDS.has(sound_name):
		return

	if not sounds.has(sound_name):
		return

	var stream = sounds[sound_name]
	for p in sound_players:
		if not p.playing:
			p.stream = stream
			p.pitch_scale = randf_range(1.0 - pitch_range, 1.0 + pitch_range)
			p.play()
			return

	# Fallback if all players are busy: use the first one
	var fallback = sound_players[0]
	fallback.stream = stream
	fallback.pitch_scale = 1.0
	fallback.play()

# Dźwięki ataku (jedyne aktywne w grze)
func play_swing(): play("sword_swing")
func play_hit(): play("hit")
func play_crit(): play("crit_hit")
func play_enemy_hit(): play("enemy_hit")

# Pozostałe dźwięki wyłączone zgodnie z życzeniem gracza
func play_click(): pass
func play_coin(): pass
func play_level_up(): pass
func play_potion(): pass
func play_quest_accept(): pass
func play_quest_complete(): pass
func play_dungeon(): pass
func play_boss(): pass
func play_equip(): pass
func play_pickup(): pass
func play_heal(): pass
