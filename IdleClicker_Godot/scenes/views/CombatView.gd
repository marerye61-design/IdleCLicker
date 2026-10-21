extends Control

const FloatingTextScene = preload("res://scenes/components/FloatingDamageText.tscn")

@onready var choice_container: HBoxContainer = %ChoiceContainer
@onready var btn_refresh: Button = %BtnRefresh

# Bohater UI
@onready var player_portrait: TextureRect = %PlayerPortrait
@onready var player_name_lbl: Label = %PlayerNameLabel
@onready var player_hp_bar: ProgressBar = %PlayerHpBar
@onready var player_hp_lbl: Label = %PlayerHpLabel
@onready var player_shield_lbl: Label = %PlayerShieldLabel
@onready var player_buffs_lbl: Label = %PlayerBuffsLabel

# Wróg UI
@onready var enemy_portrait: TextureRect = %EnemyPortrait
@onready var enemy_name_lbl: Label = %EnemyNameLabel
@onready var enemy_hp_bar: ProgressBar = %EnemyHpBar
@onready var enemy_hp_lbl: Label = %EnemyHpLabel
@onready var enemy_affix_lbl: Label = %EnemyAffixLabel

# Sterowanie i logi
@onready var btn_attack: Button = %BtnAttack
@onready var btn_ultimate: Button = %BtnUltimate
@onready var btn_potion: Button = %BtnPotion
@onready var check_autobattle: CheckButton = %CheckAutoBattle
@onready var combat_log: RichTextLabel = %CombatLog
@onready var combat_status_lbl: Label = %CombatStatusLabel

# Kontenery responsywne
@onready var arena_container: BoxContainer = %ArenaContainer if has_node("%ArenaContainer") else null
@onready var combatants_row: HBoxContainer = %CombatantsRow if has_node("%CombatantsRow") else null
@onready var player_panel: PanelContainer = %PlayerPanel if has_node("%PlayerPanel") else null
@onready var enemy_panel: PanelContainer = %EnemyPanel if has_node("%EnemyPanel") else null
@onready var center_panel: VBoxContainer = %CenterPanel if has_node("%CenterPanel") else null
@onready var controls_box: GridContainer = %ControlsBox if has_node("%ControlsBox") else null
@onready var selection_label: Label = $MainLayout/TopSelectionBar/SelectionLabel if has_node("MainLayout/TopSelectionBar/SelectionLabel") else null

@onready var player_spawn_point: Marker2D = %PlayerSpawnPoint
@onready var enemy_spawn_point: Marker2D = %EnemySpawnPoint
@onready var boss_cinematic: Control = %BossCinematic

var player: Player
var current_enemy: Dictionary = {}
var expedition_choices: Array = []
var turn_counter: int = 1
var companion_cooldown: int = 0
var enemy_stunned: bool = false
var enemy_blinded: bool = false
var is_looping: bool = true
var is_defeated: bool = false

var auto_timer: float = 0.0
const AUTO_ATTACK_INTERVAL: float = 0.85

var _is_portrait_layout: bool = false

func _apply_orientation_layout(is_portrait: bool):
	if is_portrait == _is_portrait_layout:
		return
	_is_portrait_layout = is_portrait

	if arena_container == null or combatants_row == null:
		return

	if is_portrait:
		arena_container.vertical = true
		combatants_row.visible = true
		if player_panel and player_panel.get_parent() != combatants_row:
			player_panel.reparent(combatants_row)
		if enemy_panel and enemy_panel.get_parent() != combatants_row:
			enemy_panel.reparent(combatants_row)
		if center_panel and center_panel.get_parent() != arena_container:
			center_panel.reparent(arena_container)
		arena_container.move_child(combatants_row, 0)
		arena_container.move_child(center_panel, 1)

		if player_panel:
			player_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			player_panel.custom_minimum_size = Vector2(0, 0)
		if enemy_panel:
			enemy_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			enemy_panel.custom_minimum_size = Vector2(0, 0)
		if player_portrait:
			player_portrait.custom_minimum_size = Vector2(96, 96)
		if enemy_portrait:
			enemy_portrait.custom_minimum_size = Vector2(96, 96)

		if controls_box:
			controls_box.columns = 2
		if btn_refresh:
			btn_refresh.custom_minimum_size.x = 110
		if selection_label:
			selection_label.visible = false
	else:
		arena_container.vertical = false
		combatants_row.visible = false
		if player_panel and player_panel.get_parent() != arena_container:
			player_panel.reparent(arena_container)
		if center_panel and center_panel.get_parent() != arena_container:
			center_panel.reparent(arena_container)
		if enemy_panel and enemy_panel.get_parent() != arena_container:
			enemy_panel.reparent(arena_container)
		arena_container.move_child(player_panel, 0)
		arena_container.move_child(center_panel, 1)
		arena_container.move_child(enemy_panel, 2)

		if player_panel:
			player_panel.size_flags_horizontal = 0
			player_panel.custom_minimum_size = Vector2(240, 0)
		if enemy_panel:
			enemy_panel.size_flags_horizontal = 0
			enemy_panel.custom_minimum_size = Vector2(240, 0)
		if player_portrait:
			player_portrait.custom_minimum_size = Vector2(160, 160)
		if enemy_portrait:
			enemy_portrait.custom_minimum_size = Vector2(160, 160)

		if controls_box:
			controls_box.columns = 4
		if btn_refresh:
			btn_refresh.custom_minimum_size.x = 180
		if selection_label:
			selection_label.visible = true

func _on_view_resized():
	if not is_inside_tree(): return
	var win_size: Vector2 = get_viewport().get_visible_rect().size
	var is_portrait = win_size.y > win_size.x
	_apply_orientation_layout(is_portrait)

func _ready():
	player = GameManager.player
	player.stats_changed.connect(_update_player_ui)
	player.hp_changed.connect(func(c, m): _update_player_ui())
	GameManager.second_ticked.connect(_on_second_tick)

	btn_attack.pressed.connect(_on_attack_pressed)
	btn_ultimate.pressed.connect(_on_ultimate_pressed)
	btn_potion.pressed.connect(_on_potion_pressed)
	btn_refresh.pressed.connect(_on_refresh_pressed)

	get_tree().root.size_changed.connect(_on_view_resized)
	_on_view_resized()

	_refresh_choices()
	if not expedition_choices.is_empty():
		_start_combat_with_enemy(expedition_choices[0])

	_update_player_ui()
	_update_ultimate_button()
	_update_refresh_button()

func _refresh_ui():
	if player == null:
		return
	_on_view_resized()
	_update_player_ui()
	_update_ultimate_button()
	_update_refresh_button()

	if player.hp <= 0:
		btn_attack.disabled = true
		btn_ultimate.disabled = true
		check_autobattle.button_pressed = false
		combat_status_lbl.text = "Nie masz sił do walki (0 HP)! Wróć do karczmy, by się zregenerować, lub użyj mikstury."
		for child in choice_container.get_children():
			if child is Button:
				child.disabled = true
	else:
		if is_defeated:
			is_defeated = false
			_refresh_choices()
			if not expedition_choices.is_empty():
				_start_combat_with_enemy(expedition_choices[0])
		btn_attack.disabled = false
		for child in choice_container.get_children():
			if child is Button:
				child.disabled = false
		if current_enemy.is_empty() and not expedition_choices.is_empty():
			_start_combat_with_enemy(expedition_choices[0])
		elif not current_enemy.is_empty():
			combat_status_lbl.text = "Runda %d - Starcie z %s!" % [turn_counter, current_enemy.get("name", "przeciwnikiem")]

func _process(delta: float):
	_update_refresh_button()
	if check_autobattle.button_pressed and not is_defeated and not current_enemy.is_empty() and current_enemy.get("hp", 0) > 0 and player.hp > 0:
		auto_timer += delta
		if auto_timer >= AUTO_ATTACK_INTERVAL:
			auto_timer = 0.0
			_on_attack_pressed()

func _update_refresh_button():
	var cd = GameManager.get_refresh_cooldown()
	if GameManager.can_refresh_enemies():
		btn_refresh.disabled = false
		btn_refresh.text = "Odśwież" if _is_portrait_layout else "Odśwież Przeciwników"
		btn_refresh.modulate = Color(1.0, 0.95, 0.5)
	else:
		btn_refresh.disabled = true
		btn_refresh.text = "Odśwież (%ds)" % cd if _is_portrait_layout else "Odśwież Przeciwników (%ds)" % cd
		btn_refresh.modulate = Color(0.65, 0.65, 0.65)

func _on_second_tick():
	_update_refresh_button()

func _refresh_choices():
	expedition_choices = EnemiesDB.get_expedition_choices(player.level, 3)
	for child in choice_container.get_children():
		child.queue_free()

	for i in range(expedition_choices.size()):
		var e = expedition_choices[i]
		var b = Button.new()
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.custom_minimum_size = Vector2(0, 38)
		b.text = "P.%d %s" % [e["level"], e["name"]] if _is_portrait_layout else "Poz. %d %s" % [e["level"], e["name"]]
		if e.get("is_elite", false):
			b.modulate = Color(1.0, 0.85, 0.3)
		b.disabled = (is_defeated or player.hp <= 0)
		b.pressed.connect(func(): _start_combat_with_enemy(e))
		choice_container.add_child(b)

func _on_refresh_pressed():
	if not GameManager.can_refresh_enemies():
		GameManager.post_notification("Odświeżenie wrogów odnawia się! Pozostało: %ds" % GameManager.get_refresh_cooldown())
		return
	SoundManager.play_click()
	GameManager.trigger_refresh_enemies()
	_refresh_choices()
	_update_refresh_button()
	GameManager.post_notification("Przetasowano listę przeciwników na szlaku!")
	_log("[color=yellow]Odświeżono listę przeciwników na szlaku (cooldown: 30s)![/color]")

func _start_combat_with_enemy(enemy_data: Dictionary, force_skip_cinematic: bool = false):
	if is_defeated or player.hp <= 0:
		GameManager.post_notification("Nie możesz walczyć z 0 HP! Wróć do karczmy, by się zregenerować.")
		return
	is_defeated = false
	btn_attack.disabled = false
	var e_id = enemy_data.get("id", "")
	var is_boss_enemy = enemy_data.get("is_boss", false) or e_id.begins_with("boss_")

	if is_boss_enemy and not force_skip_cinematic and not player.seen_cinematics.get(e_id, false):
		boss_cinematic.setup_boss(e_id, enemy_data.get("name", ""))
		if not boss_cinematic.finished.is_connected(_on_boss_cinematic_finished):
			boss_cinematic.finished.connect(_on_boss_cinematic_finished.bind(enemy_data), CONNECT_ONE_SHOT)
		return

	_setup_combat_state(enemy_data)

func _on_boss_cinematic_finished(enemy_data: Dictionary):
	var e_id = enemy_data.get("id", "")
	player.seen_cinematics[e_id] = true
	_setup_combat_state(enemy_data)

func _setup_combat_state(enemy_data: Dictionary):
	current_enemy = enemy_data.duplicate(true)
	turn_counter = 1
	enemy_stunned = false
	enemy_blinded = false

	# Aktualizacja UI wroga
	enemy_name_lbl.text = current_enemy["name"]
	if current_enemy.get("is_elite", false):
		enemy_name_lbl.modulate = Color("#f39c12")
		enemy_affix_lbl.text = current_enemy.get("affix_label", "")
		enemy_affix_lbl.visible = true
	else:
		enemy_name_lbl.modulate = Color.WHITE
		enemy_affix_lbl.text = ""
		enemy_affix_lbl.visible = false

	var tex_path = current_enemy.get("portrait_path", "res://assets/portraits/hero.jpg")
	if ResourceLoader.exists(tex_path):
		enemy_portrait.texture = load(tex_path)

	_update_enemy_hp()
	combat_status_lbl.text = "Runda 1 - Starcia z %s!" % current_enemy["name"]
	_log("[color=#3498db]--- Rozpoczęto walkę z [b]%s[/b] (Poz. %d, %d HP) ---[/color]" % [current_enemy["name"], current_enemy["level"], current_enemy["hp"]])

func _update_player_ui():
	if player == null: return
	if player_portrait and player_portrait.texture == null:
		var hero_tex_path = "res://assets/portraits/hero.jpg"
		if ResourceLoader.exists(hero_tex_path):
			player_portrait.texture = load(hero_tex_path)
	player_name_lbl.text = "%s (Poz. %d)" % [player.name, player.level]
	player_hp_bar.max_value = player.get_max_hp()
	player_hp_bar.value = player.hp
	player_hp_lbl.text = "%d / %d HP" % [player.hp, player.get_max_hp()]

	if player.combat_shield > 0:
		player_shield_lbl.text = "Tarcza: +%d" % player.combat_shield
		player_shield_lbl.visible = true
	else:
		player_shield_lbl.visible = false

	var buffs: Array = []
	for b_id in player.active_buffs.keys():
		buffs.append("%s (%d)" % [b_id.replace("elixir_", ""), player.active_buffs[b_id]])
	if buffs.is_empty():
		player_buffs_lbl.text = ""
	else:
		player_buffs_lbl.text = "Buffy: " + ", ".join(buffs)

	# Liczba mikstur
	var pot_count = 0
	for it in player.inventory:
		if it.get("id") == "pot_hp":
			pot_count += 1
	btn_potion.text = "Użyj Mikstury (%d)" % pot_count
	btn_potion.disabled = (pot_count == 0 or player.hp >= player.get_max_hp())

func _update_enemy_hp():
	enemy_hp_bar.max_value = current_enemy.get("max_hp", 100)
	enemy_hp_bar.value = current_enemy.get("hp", 0)
	enemy_hp_lbl.text = "%d / %d HP" % [current_enemy.get("hp", 0), current_enemy.get("max_hp", 100)]

func _update_ultimate_button():
	var ult = CombatMath.get_companion_ultimate(player.active_companion if player.active_companion != null else "")
	if ult.is_empty():
		btn_ultimate.visible = false
		return

	btn_ultimate.visible = true
	if companion_cooldown <= 0:
		btn_ultimate.disabled = false
		btn_ultimate.text = ult["name"]
	else:
		btn_ultimate.disabled = true
		btn_ultimate.text = "%s (%d)" % [ult["name"], companion_cooldown]

func _on_attack_pressed():
	if is_defeated or current_enemy.is_empty() or current_enemy.get("hp", 0) <= 0 or player.hp <= 0:
		return

	# Tura gracza
	SoundManager.play_swing()
	var attack_res = CombatMath.calculate_player_dmg(player, current_enemy, (turn_counter == 1))
	var dmg: int = attack_res["damage"]
	var is_crit: bool = attack_res["is_crit"]

	if is_crit:
		SoundManager.play_crit()
		player.record_achievement_stat("total_crits", 1, "add")
		_spawn_floating_text(enemy_spawn_point.global_position, "KRYT! -%d" % dmg, Color("#f1c40f"), true)
		_log("[color=#f1c40f]Cios krytyczny! Zadajesz %d obrażeń![/color]" % dmg)
	else:
		SoundManager.play_hit()
		_spawn_floating_text(enemy_spawn_point.global_position, "-%d" % dmg, Color.WHITE, false)
		_log("Zadajesz [b]%d[/b] obrażeń." % dmg)

	# Lifesteal (Awanturnik / Berserker)
	var lifesteal_pct = player.get_talent_bonus("lifesteal_pct")
	if lifesteal_pct > 0.0:
		var heal = int(float(dmg) * lifesteal_pct)
		if heal > 0:
			player.hp = mini(player.get_max_hp(), player.hp + heal)
			_spawn_floating_text(player_spawn_point.global_position, "+%d HP" % heal, Color("#2ecc71"), false)

	current_enemy["hp"] = maxi(0, current_enemy["hp"] - dmg)
	_update_enemy_hp()

	# Podwójne uderzenie (Szafir)
	var double_strike = player.get_double_strike_chance()
	if current_enemy["hp"] > 0 and randi_range(1, 100) <= double_strike:
		var extra_dmg = int(dmg * 0.75)
		current_enemy["hp"] = maxi(0, current_enemy["hp"] - extra_dmg)
		_spawn_floating_text(enemy_spawn_point.global_position, "2x! -%d" % extra_dmg, Color("#3498db"), false)
		_log("[color=#3498db]Podwójne uderzenie! Zadajesz dodatkowe %d obrażeń![/color]" % extra_dmg)
		_update_enemy_hp()

	# Sprawdzenie śmierci wroga
	if current_enemy["hp"] <= 0:
		_on_enemy_defeated()
		return

	# Tura wroga
	_enemy_turn()
	turn_counter += 1
	if companion_cooldown > 0:
		companion_cooldown -= 1
	_update_ultimate_button()

func _on_ultimate_pressed():
	if is_defeated or player.hp <= 0 or companion_cooldown > 0 or player.active_companion == null:
		return

	var ult = CombatMath.get_companion_ultimate(player.active_companion)
	if ult.is_empty():
		return

	companion_cooldown = ult.get("cooldown", 4)
	_update_ultimate_button()

	_log("[color=#9b59b6][b]%s[/b] używa: [b]%s[/b]![/color]" % [player.active_companion.capitalize(), ult["name"]])

	if ult.has("dmg_mult"):
		var ult_dmg = int(float(player.get_total_atk()) * ult["dmg_mult"])
		if ult.get("force_crit", false):
			SoundManager.play_crit()
			_spawn_floating_text(enemy_spawn_point.global_position, "KRYT! -%d" % ult_dmg, Color("#f1c40f"), true)
		else:
			SoundManager.play_hit()
			_spawn_floating_text(enemy_spawn_point.global_position, "-%d" % ult_dmg, Color("#e74c3c"), true)
		current_enemy["hp"] = maxi(0, current_enemy["hp"] - ult_dmg)
		_update_enemy_hp()

	if ult.has("stun_turns"):
		enemy_stunned = true
		_spawn_floating_text(enemy_spawn_point.global_position, "OGŁUSZENIE!", Color("#9b59b6"), false)
		_log("[color=#9b59b6]Wróg został ogłuszony na 1 turę![/color]")

	if ult.has("blind_turns"):
		enemy_blinded = true
		_spawn_floating_text(enemy_spawn_point.global_position, "OŚLEPIENIE!", Color("#9b59b6"), false)
		_log("[color=#9b59b6]Gęsty dym ziół oślepia wroga![/color]")

	if ult.has("heal_pct"):
		var heal = int(float(player.get_max_hp()) * (float(ult["heal_pct"]) / 100.0))
		player.hp = mini(player.get_max_hp(), player.hp + heal)
		_spawn_floating_text(player_spawn_point.global_position, "+%d HP" % heal, Color("#2ecc71"), false)
		_update_player_ui()

	if ult.has("shield_pct"):
		var shield = int(float(player.get_max_hp()) * (float(ult["shield_pct"]) / 100.0))
		player.combat_shield += shield
		_spawn_floating_text(player_spawn_point.global_position, "TARCZA +%d" % shield, Color("#3498db"), false)
		_update_player_ui()

	if ult.get("bonus_gold", false):
		var bonus_g = player.add_gold(int(player.level * 20 + 50), "Pączek Maślaka")
		_spawn_floating_text(player_spawn_point.global_position, "+%d złota" % bonus_g, Color("#f1c40f"), false)

	if current_enemy["hp"] <= 0:
		_on_enemy_defeated()

func _enemy_turn():
	if enemy_stunned:
		enemy_stunned = false
		_log("[color=#9b59b6]Wróg jest ogłuszony i nie może zaatakować![/color]")
		return

	if enemy_blinded:
		enemy_blinded = false
		_log("[color=#9b59b6]Wróg słyszy kolory i pudłuje![/color]")
		_spawn_floating_text(player_spawn_point.global_position, "PUDŁO!", Color("#3498db"), false)
		return

	# Dedykowane animacje ataku bossów (Ptyś maczuga, Kollman kula ognia)
	var e_id = current_enemy.get("id", "")
	var e_name_lower = current_enemy.get("name", "").to_lower()
	if e_id == "boss_ptys" or e_name_lower.contains("ptyś") or e_name_lower.contains("ptys"):
		_animate_ptys_mace()
	elif e_id == "boss_kollman" or e_name_lower.contains("kollman"):
		_animate_kollman_fireball()
	else:
		_animate_enemy_attack()

	# Unik (Awanturnik)
	var dodge_chance = int(player.get_talent_bonus("dodge_pct") * 100.0)
	if dodge_chance > 0 and randi_range(1, 100) <= dodge_chance:
		_spawn_floating_text(player_spawn_point.global_position, "UNIK!", Color("#3498db"), false)
		_log("[color=#3498db]Błyskawiczny unik! Uniknąłeś ciosu przeciwnika.[/color]")
		return

	var raw_dmg = CombatMath.calculate_enemy_dmg(current_enemy, player)
	var final_dmg = player.absorb_shield_hit(raw_dmg)

	if final_dmg > 0:
		player.hp = maxi(0, player.hp - final_dmg)
		SoundManager.play_enemy_hit()
		_spawn_floating_text(player_spawn_point.global_position, "-%d" % final_dmg, Color("#e74c3c"), false)
		_log("[color=#e74c3c]%s zadaje ci %d obrażeń![/color]" % [current_enemy["name"], final_dmg])
	else:
		_spawn_floating_text(player_spawn_point.global_position, "TARCZA!", Color("#3498db"), false)
		_log("[color=#3498db]Tarcza całkowicie pochłonęła atak wroga![/color]")

	# Odbicie obrażeń Thorns (Obrońca)
	var thorns_pct = player.get_talent_bonus("thorns_pct")
	if thorns_pct > 0.0 and raw_dmg > 0:
		var reflected = maxi(1, int(float(raw_dmg) * thorns_pct))
		current_enemy["hp"] = maxi(0, current_enemy["hp"] - reflected)
		_spawn_floating_text(enemy_spawn_point.global_position, "THORNS! -%d" % reflected, Color("#3498db"), false)
		_log("[color=#3498db]Niezłomna tarcza odbija %d obrażeń we wroga![/color]" % reflected)
		_update_enemy_hp()
		if current_enemy["hp"] <= 0:
			_on_enemy_defeated()
			return

	# Regeneracja co turę (Obrońca)
	var regen_pct = player.get_talent_bonus("regen_turn_pct")
	if regen_pct > 0.0 and player.hp > 0:
		var reg = int(float(player.get_max_hp()) * regen_pct)
		if reg > 0:
			player.hp = mini(player.get_max_hp(), player.hp + reg)

	_update_player_ui()

	if player.hp <= 0:
		_on_player_defeated()

func _animate_ptys_mace():
	var mace = TextureRect.new()
	mace.texture = load("res://assets/ptys_mace.png")
	mace.custom_minimum_size = Vector2(80, 80)
	mace.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	mace.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	mace.pivot_offset = Vector2(40, 40)
	mace.global_position = enemy_spawn_point.global_position - Vector2(40, 40)
	add_child(mace)

	var tween = create_tween()
	mace.rotation_degrees = 45.0
	tween.tween_property(mace, "global_position", player_spawn_point.global_position - Vector2(40, 40), 0.22).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.parallel().tween_property(mace, "rotation_degrees", -60.0, 0.22)
	tween.tween_callback(func():
		SoundManager.play_enemy_hit()
		_spawn_floating_text(player_spawn_point.global_position, "MIAŻDŻĄCY CIOS!", Color("#e74c3c"), true)
	)
	tween.tween_property(mace, "modulate:a", 0.0, 0.15)
	tween.tween_callback(mace.queue_free)

func _animate_kollman_fireball():
	var fb = TextureRect.new()
	fb.texture = load("res://assets/kollman_fireball.png")
	fb.custom_minimum_size = Vector2(64, 64)
	fb.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	fb.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	fb.pivot_offset = Vector2(32, 32)
	fb.global_position = enemy_spawn_point.global_position - Vector2(32, 32)
	add_child(fb)

	var tween = create_tween()
	tween.tween_property(fb, "global_position", player_spawn_point.global_position - Vector2(32, 32), 0.24).set_trans(Tween.TRANS_EXPO).set_ease(Tween.EASE_IN)
	tween.parallel().tween_property(fb, "rotation_degrees", 720.0, 0.24)
	tween.tween_callback(func():
		SoundManager.play_enemy_hit()
		_spawn_floating_text(player_spawn_point.global_position, "KULA OGNIA!", Color("#f1c40f"), true)
	)
	tween.tween_property(fb, "modulate:a", 0.0, 0.12)
	tween.tween_callback(fb.queue_free)

func _animate_enemy_attack():
	var tween = create_tween()
	var orig_x = enemy_portrait.position.x
	tween.tween_property(enemy_portrait, "position:x", orig_x - 30.0, 0.10).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(enemy_portrait, "position:x", orig_x, 0.12).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)

func _on_enemy_defeated():
	SoundManager.play_coin()
	var exp_gained = current_enemy["exp_reward"]
	var gold_gained = current_enemy["gold_reward"]

	# Bonus złota z talentów / klejnotów
	var gold_mult = 1.0 + player.get_talent_bonus("bonus_gold") + (float(player.get_gems_bonus().get("bonus_gold_pct", 0)) / 100.0)
	gold_gained = int(float(gold_gained) * gold_mult)

	player.add_exp(exp_gained)
	var actual_gold = player.add_gold(gold_gained, "Walka")

	_log("[color=#2ecc71]ZWYCIĘSTWO! Pokonano %s![/color]" % current_enemy["name"])
	_log("[color=#f1c40f]+%d złota | +%d EXP[/color]" % [actual_gold, exp_gained])

	# Statystyki i bestiariusz
	player.record_achievement_stat("total_kills", 1, "add")
	var base_name = current_enemy.get("base_name", current_enemy["name"])
	player.bestiary[base_name] = player.bestiary.get(base_name, 0) + 1

	var e_id = current_enemy.get("id", "")
	var is_boss_mob = current_enemy.get("is_boss", false) or e_id.begins_with("boss_")
	if is_boss_mob:
		if e_id == "boss_ptys" or base_name.to_lower().contains("ptyś"):
			player.record_achievement_stat("boss_ptys_kills", 1, "add")
			GameManager.post_notification("Giga Ork Ptyś został pokonany!")
		elif e_id == "boss_kollman" or base_name.to_lower().contains("kollman"):
			player.record_achievement_stat("boss_kollman_kills", 1, "add")
			GameManager.post_notification("Kollman został pokonany!")

	# Sprawdzenie celów zadań fabularnych
	for q in player.quests:
		if q.get("status") == "IN_PROGRESS" and q.has("requirements") and q["requirements"].has("kills"):
			var kill_reqs = q["requirements"]["kills"]
			if kill_reqs.has(base_name):
				var kills = q["progress"]["kills"]
				kills[base_name] = kills.get(base_name, 0) + 1
				if kills[base_name] >= kill_reqs[base_name]:
					_log("[color=#f4d03f]Cel zadania osiągnięty dla: %s![/color]" % base_name)
				q.check_completion(player)

	# 1. Składnik alchemiczny (drop) z powiadomieniem
	var drop = AlchemyDB.roll_monster_ingredient_drop(base_name)
	if drop != null:
		var ing_name = AlchemyDB.MONSTER_INGREDIENTS[drop]["name"]
		player.add_to_inventory(drop)
		_log("[color=#00d2d3]Zdobyto składnik alchemiczny: %s![/color]" % ing_name)
		GameManager.post_notification("Zdobyto łup: %s!" % ing_name)
		_spawn_floating_text(enemy_spawn_point.global_position, "ŁUP: %s!" % ing_name, Color("#00d2d3"), true)

	# 2. Drop Magicznych Klejnotów z powiadomieniem (3% ze zwykłych potworów od 15 lvl, 10% z bossa lochu)
	var gem_drop_id = GemsDB.roll_gem_drop(is_boss_mob, player.level)
	if gem_drop_id != null:
		var gem_data = GemsDB.get_gem(gem_drop_id)
		var gem_name = gem_data.get("name", gem_drop_id)
		player.add_to_inventory(gem_drop_id)
		_log("[color=#f1c40f]RZADKI DROP KLEJNOTU! Zdobyłeś %s![/color]" % gem_name)
		GameManager.post_notification("Zdobyto rzadki klejnot: %s!" % gem_name)
		_spawn_floating_text(enemy_spawn_point.global_position, "KLEJNOT: %s!" % gem_name, Color("#f1c40f"), true)

	# 3. Szansa na Miksturę Zdrowia (Maślak pasywka 5% lub losowy drop 3%)
	var pot_chance = 0.03
	if player.party.has("maslak") or player.active_companion == "maslak":
		pot_chance += 0.05
	if randf() <= pot_chance and not player.is_inventory_full():
		player.add_to_inventory("pot_hp")
		_log("[color=#2ecc71]Zdobyto Miksturę Pełnego Zdrowia![/color]")
		GameManager.post_notification("Zdobyto Miksturę Zdrowia!")
		_spawn_floating_text(enemy_spawn_point.global_position, "+1 MIKSTURA HP!", Color("#2ecc71"), false)

	# Zmniejszenie czasu trwania eliksirów
	var expired = player.tick_active_buffs()
	for exp_b in expired:
		_log("[color=gray]Działanie mikstury %s dobiegło końca.[/color]" % exp_b)

	# Reset tarczy
	player.combat_shield = 0

	# Pętla walki: jeśli pokonano potwora elitarnego, następny przeciwnik jest ZWYKŁY (force_elite = false)
	var was_elite = current_enemy.get("is_elite", false)
	var template_id = current_enemy.get("template_id", current_enemy["id"])

	# Szukamy szablonu tego potwora
	var tmpl: Dictionary = {}
	for t in EnemiesDB.TEMPLATES:
		if t["id"] == template_id:
			tmpl = t
			break

	if not tmpl.is_empty():
		var next_enemy = EnemiesDB.generate_enemy(tmpl, current_enemy["level"], false if was_elite else null)
		_start_combat_with_enemy(next_enemy, true)
	else:
		_refresh_choices()
		if not expedition_choices.is_empty():
			_start_combat_with_enemy(expedition_choices[0], true)

func _on_player_defeated():
	if is_defeated:
		return
	is_defeated = true
	player.hp = 0
	player.hp_changed.emit(0, player.get_max_hp())
	auto_timer = 0.0
	check_autobattle.button_pressed = false
	btn_attack.disabled = true
	btn_ultimate.disabled = true
	for child in choice_container.get_children():
		if child is Button:
			child.disabled = true
	btn_refresh.disabled = true

	SoundManager.play_enemy_hit()
	_update_player_ui()
	_log("[color=#e74c3c][b]ZOSTAŁEŚ POKONANY![/b] Padasz z wycieńczenia... Karczmarz Barnaba zabiera cię do bezpiecznej karczmy![/color]")
	combat_status_lbl.text = "Porażka! Odpocznij w karczmie i zregeneruj siły."
	GameManager.post_notification("Zostałeś pokonany! Powrót do Karczmy Barnaby...")

	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree():
		return

	GameManager.switch_view("tavern")

func _on_potion_pressed():
	if is_defeated:
		return
	for i in range(player.inventory.size()):
		if player.inventory[i].get("id") == "pot_hp":
			if player.use_consumable(i):
				SoundManager.play_potion()
				_spawn_floating_text(player_spawn_point.global_position, "PEŁNE ZDROWIE!", Color("#2ecc71"), false)
				_log("[color=#2ecc71]Użyto Mikstury Pełnego Zdrowia! Twoje HP zostało zregenerowane.[/color]")
				if player.hp > 0:
					btn_attack.disabled = false
				_update_player_ui()
				return

func _spawn_floating_text(pos: Vector2, text: String, color: Color, is_crit: bool):
	var txt = FloatingTextScene.instantiate()
	txt.position = pos
	add_child(txt)
	txt.setup(text, color, is_crit)

func _log(text: String):
	combat_log.append_text(text + "\n")
