extends Control

signal boss_fight_requested(boss_id: String)

@onready var status_label: Label = %StatusLabel
@onready var btn_close_top: Button = %BtnCloseTop
@onready var btn_close_bottom: Button = %BtnCloseBottom

# Sekcja 1
@onready var btn_add_gold_10k: Button = %BtnAddGold10k
@onready var btn_add_gold_1m: Button = %BtnAddGold1M
@onready var btn_heal_full: Button = %BtnHealFull
@onready var btn_add_level_1: Button = %BtnAddLevel1
@onready var btn_add_level_10: Button = %BtnAddLevel10
@onready var btn_add_stat_pts: Button = %BtnAddStatPts

# Sekcja 2
@onready var btn_boss_ptys: Button = %BtnBossPtys
@onready var btn_boss_kollman: Button = %BtnBossKollman
@onready var btn_boss_morgar: Button = %BtnBossMorgar

# Sekcja 3
@onready var btn_add_gems: Button = %BtnAddGems
@onready var btn_add_socket_item: Button = %BtnAddSocketItem
@onready var btn_add_alchemy: Button = %BtnAddAlchemy
@onready var btn_grow_garden: Button = %BtnGrowGarden
@onready var btn_all_achievements: Button = %BtnAllAchievements

@onready var window_panel: PanelContainer = %WindowPanel if has_node("%WindowPanel") else null

var player: Player

func _on_console_resized():
	if not is_inside_tree() or window_panel == null: return
	var win_size: Vector2 = get_viewport().get_visible_rect().size
	window_panel.custom_minimum_size.x = min(740.0, win_size.x - 24.0)
	window_panel.custom_minimum_size.y = min(560.0, win_size.y - 32.0)

func _ready():
	player = GameManager.player
	get_tree().root.size_changed.connect(_on_console_resized)
	_on_console_resized()

	btn_close_top.pressed.connect(hide)
	btn_close_bottom.pressed.connect(hide)

	btn_add_gold_10k.pressed.connect(func(): _add_gold(10000))
	btn_add_gold_1m.pressed.connect(func(): _add_gold(1000000))
	btn_heal_full.pressed.connect(_heal_full)
	btn_add_level_1.pressed.connect(func(): _add_levels(1))
	btn_add_level_10.pressed.connect(func(): _add_levels(10))
	btn_add_stat_pts.pressed.connect(func(): _add_stat_pts(50))

	btn_boss_ptys.pressed.connect(func(): _trigger_boss("boss_ptys"))
	btn_boss_kollman.pressed.connect(func(): _trigger_boss("boss_kollman"))
	btn_boss_morgar.pressed.connect(func(): _trigger_boss("boss_wraith_lord"))

	btn_add_gems.pressed.connect(_add_gems)
	btn_add_socket_item.pressed.connect(_add_socket_item)
	btn_add_alchemy.pressed.connect(_add_alchemy)
	btn_grow_garden.pressed.connect(_grow_garden)
	btn_all_achievements.pressed.connect(_complete_achievements)

func _set_status(msg: String):
	status_label.text = msg
	GameManager.post_notification(msg)

func _add_gold(amount: int):
	player.gold += amount
	player.gold_changed.emit(player.gold)
	player.stats_changed.emit()
	_set_status("Dodano +%d złota! Posiadasz: %d" % [amount, player.gold])

func _heal_full():
	player.hp = player.get_max_hp()
	player.mana = player.max_mana
	player.hp_changed.emit(player.hp, player.get_max_hp())
	player.stats_changed.emit()
	_set_status("Bohater w pełni uleczony (100% HP i Many)!")

func _add_levels(count: int):
	for i in range(count):
		var req = player.get_exp_required()
		player.add_exp(req - player.exp)
	_set_status("Awansowano o +%d poziomów! Obecny poziom: %d" % [count, player.level])

func _add_stat_pts(amount: int):
	player.stat_points += amount
	player.stats_changed.emit()
	_set_status("Dodano +%d Punktów Rozwoju! Razem masz: %d" % [amount, player.stat_points])

func _trigger_boss(boss_id: String):
	hide()
	if player != null and player.seen_cinematics.has(boss_id):
		player.seen_cinematics.erase(boss_id)
	boss_fight_requested.emit(boss_id)

func _add_gems():
	var added = 0
	for gid in GemsDB.GEMS.keys():
		if not player.is_inventory_full():
			player.add_to_inventory(gid, true)
			added += 1
	player.stats_changed.emit()
	_set_status("Dodano komplet magicznych klejnotów (%d szt.)!" % added)

func _add_socket_item():
	if player.is_inventory_full():
		_set_status("Ekwipunek jest pełny!")
		return
	var item_d = {"id": "wep_mithril_blade", "lvl": 3, "sockets": [null, null]}
	player.add_to_inventory(item_d, true)
	player.stats_changed.emit()
	_set_status("Dodano Mithrilowe Ostrze +3 z 2 wolnymi gniazdami na klejnoty!")

func _add_alchemy():
	for hid in AlchemyDB.HERBS.keys():
		player.add_to_inventory(hid, true)
	for mid in AlchemyDB.MONSTER_INGREDIENTS.keys():
		player.add_to_inventory(mid, true)
	player.stats_changed.emit()
	_set_status("Dodano składniki alchemiczne (zioła i odczynniki z potworów)!")

func _grow_garden():
	var now = Time.get_unix_time_from_system()
	for p in player.herb_garden:
		p["planted_at"] = now - 9999
	player.stats_changed.emit()
	_set_status("Wszystkie zioła w ogrodzie Domci natychmiast dojrzały i są gotowe do zbioru!")

func _complete_achievements():
	player.achievement_stats["total_kills"] = 1000
	player.achievement_stats["total_crits"] = 100
	player.achievement_stats["boss_ptys_kills"] = 5
	player.achievement_stats["boss_kollman_kills"] = 5
	player.achievement_stats["dungeons_cleared"] = 20
	player.achievement_stats["upgrades_done"] = 20
	player.achievement_stats["max_upgrade_level"] = 9
	player.achievement_stats["gems_socketed"] = 10
	player.achievement_stats["herbs_harvested"] = 50
	player.achievement_stats["potions_brewed"] = 25
	player.achievement_stats["total_gold_earned"] = 200000
	player.stats_changed.emit()
	_set_status("Statystyki zaktualizowane: Wszystkie osiągnięcia są gotowe do odbioru!")
