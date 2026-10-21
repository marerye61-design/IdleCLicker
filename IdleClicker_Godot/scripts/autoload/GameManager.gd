extends Node

signal second_ticked
signal notification_posted(msg: String)
signal view_change_requested(view_key: String)

var player: Player
var current_view: String = "combat"
var save_timer: float = 0.0
var tick_timer: float = 0.0

# 30-sekundowy cooldown na odświeżanie przeciwników w ekspedycji
var refresh_cooldown_remaining: float = 0.0

func _ready():
	SaveSystem.init_saves_dir()

func ensure_player_loaded():
	if player != null:
		return
	player = Player.new()
	var loaded = SaveSystem.load_game(player)
	if not loaded:
		player.migrate()
	player.update_offline_progress()

func start_new_game(char_name: String):
	player = Player.new(char_name)
	player.migrate()
	var fname = SaveSystem.sanitize_filename(char_name) + ".json"
	SaveSystem.save_game(player, fname)
	current_view = "combat"
	get_tree().change_scene_to_file("res://scenes/Main.tscn")

func load_existing_save(filename: String) -> bool:
	player = Player.new()
	var loaded = SaveSystem.load_game(player, filename)
	if not loaded:
		push_error("Nie udało się wczytać zapisu: %s" % filename)
		return false
	player.update_offline_progress()
	current_view = "combat"
	get_tree().change_scene_to_file("res://scenes/Main.tscn")
	return true

func return_to_main_menu():
	save_now()
	get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")

func _process(delta: float):
	if player == null:
		return

	# Odliczanie cooldownu na odświeżanie wrogów
	if refresh_cooldown_remaining > 0.0:
		refresh_cooldown_remaining = maxf(0.0, refresh_cooldown_remaining - delta)

	tick_timer += delta
	if tick_timer >= 1.0:
		tick_timer -= 1.0
		_on_second_tick()

	save_timer += delta
	if save_timer >= 60.0:
		save_timer = 0.0
		save_now()

func _on_second_tick():
	if player == null:
		return

	# Generowanie pasywnego złota na sekundę
	var gps = player.recalculate_gold_per_sec()
	if gps > 0:
		player.add_gold(gps, "Pasywny przychód", false)

	# Pasywna regeneracja many
	var mana_reg = player.stats.get("mana_regen", 1)
	player.mana = mini(player.max_mana, player.mana + mana_reg)

	# Pasywna regeneracja zdrowia w karczmie (Tawerna)
	if current_view == "tavern" and player.hp < player.get_max_hp():
		var max_h = player.get_max_hp()
		var tavern_regen = maxi(5, int(max_h * 0.08))
		player.hp = mini(max_h, player.hp + tavern_regen)
		player.hp_changed.emit(player.hp, max_h)

	second_ticked.emit()

func switch_view(view_key: String):
	current_view = view_key
	view_change_requested.emit(view_key)

func save_now():
	if player != null:
		SaveSystem.save_game(player)

func post_notification(msg: String):
	notification_posted.emit(msg)
	print("[Powiadomienie] %s" % msg)

func can_refresh_enemies() -> bool:
	return refresh_cooldown_remaining <= 0.0

func trigger_refresh_enemies():
	refresh_cooldown_remaining = 30.0

func get_refresh_cooldown() -> int:
	return int(ceil(refresh_cooldown_remaining))
