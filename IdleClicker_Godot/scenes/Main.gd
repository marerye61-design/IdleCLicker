extends Control

const ForgeUIEffects = preload("res://scripts/ui/ForgeUIEffects.gd")

@onready var hero_level_lbl: Label = %HeroLevelLabel
@onready var exp_bar: ProgressBar = %ExpBar
@onready var hp_bar: ProgressBar = %HpBar
@onready var hp_lbl: Label = %HpLabel
@onready var mana_bar: ProgressBar = %ManaBar
@onready var mana_lbl: Label = %ManaLabel
@onready var gold_lbl: Label = %GoldLabel
@onready var companion_lbl: Label = %CompanionLabel
@onready var notification_lbl: Label = %NotificationLabel
@onready var notification_toast: PanelContainer = %NotificationToast
@onready var hero_avatar: TextureRect = %HeroAvatar
@onready var btn_hero_click: Button = %BtnHeroClick

@onready var hud_hbox: HBoxContainer = %HUDHBox if has_node("%HUDHBox") else $RootVBox/TopHUD/HUDMargin/HUDHBox
@onready var hud_vbox: VBoxContainer = %HUDVBox if has_node("%HUDVBox") else null
@onready var hud_row2: HBoxContainer = %HUDRow2 if has_node("%HUDRow2") else null
@onready var top_hud: PanelContainer = %TopHUD if has_node("%TopHUD") else $RootVBox/TopHUD
@onready var hud_margin: MarginContainer = %HUDMargin if has_node("%HUDMargin") else $RootVBox/TopHUD/HUDMargin
@onready var nav_sidebar: PanelContainer = $RootVBox/MainBody/NavSidebar
@onready var bottom_nav: PanelContainer = %BottomNav if has_node("%BottomNav") else null

@onready var exp_box: HBoxContainer = %ExpBox if has_node("%ExpBox") else null
@onready var hp_box: HBoxContainer = %HpBox if has_node("%HpBox") else null
@onready var mana_box: HBoxContainer = %ManaBox if has_node("%ManaBox") else null

# Przyciski nawigacji bocznej
@onready var nav_combat: Button = %NavCombat
@onready var nav_dungeons: Button = %NavDungeons
@onready var nav_stats: Button = %NavStats
@onready var nav_inventory: Button = %NavInventory
@onready var nav_tavern: Button = %NavTavern
@onready var nav_alchemy: Button = %NavAlchemy
@onready var nav_market: Button = %NavMarket
@onready var nav_shop: Button = %NavShop
@onready var nav_blacksmith: Button = %NavBlacksmith
@onready var nav_achievements: Button = %NavAchievements
@onready var nav_debug: Button = %NavDebug
@onready var nav_save: Button = %NavSave
@onready var nav_exit_to_menu: Button = %NavExitToMenu

# Przyciski nawigacji dolnej (mobilny pasek w orientacji pionowej)
@onready var bnav_combat: Button = %BNavCombat if has_node("%BNavCombat") else null
@onready var bnav_dungeons: Button = %BNavDungeons if has_node("%BNavDungeons") else null
@onready var bnav_stats: Button = %BNavStats if has_node("%BNavStats") else null
@onready var bnav_inventory: Button = %BNavInventory if has_node("%BNavInventory") else null
@onready var bnav_tavern: Button = %BNavTavern if has_node("%BNavTavern") else null
@onready var bnav_alchemy: Button = %BNavAlchemy if has_node("%BNavAlchemy") else null
@onready var bnav_market: Button = %BNavMarket if has_node("%BNavMarket") else null
@onready var bnav_shop: Button = %BNavShop if has_node("%BNavShop") else null
@onready var bnav_blacksmith: Button = %BNavBlacksmith if has_node("%BNavBlacksmith") else null
@onready var bnav_achievements: Button = %BNavAchievements if has_node("%BNavAchievements") else null
@onready var bnav_save: Button = %BNavSave if has_node("%BNavSave") else null
@onready var bnav_exit_to_menu: Button = %BNavExitToMenu if has_node("%BNavExitToMenu") else null

@onready var view_container: PanelContainer = %ViewContainer
@onready var debug_console: Control = %DebugConsole

var player: Player
var loaded_views: Dictionary = {}
var current_view_node: Node = null

const VIEWS: Dictionary = {
	"combat": "res://scenes/views/CombatView.tscn",
	"dungeons": "res://scenes/views/DungeonsView.tscn",
	"stats": "res://scenes/views/StatsView.tscn",
	"inventory": "res://scenes/views/InventoryView.tscn",
	"tavern": "res://scenes/views/TavernView.tscn",
	"alchemy": "res://scenes/views/AlchemyView.tscn",
	"market": "res://scenes/views/MarketView.tscn",
	"shop": "res://scenes/views/ShopView.tscn",
	"blacksmith": "res://scenes/views/BlacksmithView.tscn",
	"achievements": "res://scenes/views/AchievementsView.tscn"
}

func _ready():
	GameManager.ensure_player_loaded()
	player = GameManager.player
	player.stats_changed.connect(_update_hud)
	player.gold_changed.connect(func(_g): _update_hud())
	player.hp_changed.connect(func(_c, _m): _update_hud())
	GameManager.second_ticked.connect(_on_second_tick)
	GameManager.notification_posted.connect(_show_notification)
	GameManager.view_change_requested.connect(_switch_view)

	nav_combat.pressed.connect(func(): _switch_view("combat"))
	nav_dungeons.pressed.connect(func(): _switch_view("dungeons"))
	nav_stats.pressed.connect(func(): _switch_view("stats"))
	nav_inventory.pressed.connect(func(): _switch_view("inventory"))
	nav_tavern.pressed.connect(func(): _switch_view("tavern"))
	nav_alchemy.pressed.connect(func(): _switch_view("alchemy"))
	nav_market.pressed.connect(func(): _switch_view("market"))
	nav_shop.pressed.connect(func(): _switch_view("shop"))
	nav_blacksmith.pressed.connect(func(): _switch_view("blacksmith"))
	nav_achievements.pressed.connect(func(): _switch_view("achievements"))
	nav_debug.pressed.connect(_toggle_debug_console)
	nav_save.pressed.connect(_on_save_pressed)
	nav_exit_to_menu.pressed.connect(_on_exit_to_menu_pressed)

	# Zastosuj sprężyste mikro-reakcje najechania i kute podświetlenie kuźni
	var all_nav_buttons = [
		nav_combat, nav_dungeons, nav_stats, nav_inventory, nav_tavern,
		nav_alchemy, nav_market, nav_shop, nav_blacksmith, nav_achievements,
		nav_debug, nav_save, nav_exit_to_menu
	]
	for btn in all_nav_buttons:
		ForgeUIEffects.apply_button_effect(btn, 1.05, Color(1.15, 0.9, 0.4))

	var bnav_map = {
		bnav_combat: "combat", bnav_dungeons: "dungeons", bnav_stats: "stats",
		bnav_inventory: "inventory", bnav_tavern: "tavern", bnav_alchemy: "alchemy",
		bnav_market: "market", bnav_shop: "shop", bnav_blacksmith: "blacksmith",
		bnav_achievements: "achievements"
	}
	for b in bnav_map.keys():
		if b:
			var target_view = bnav_map[b]
			b.pressed.connect(func(): _switch_view(target_view))
			ForgeUIEffects.apply_button_effect(b, 1.05, Color(1.15, 0.9, 0.4))
	if bnav_save:
		bnav_save.pressed.connect(_on_save_pressed)
		ForgeUIEffects.apply_button_effect(bnav_save, 1.05, Color(1.15, 0.9, 0.4))
	if bnav_exit_to_menu:
		bnav_exit_to_menu.pressed.connect(_on_exit_to_menu_pressed)
		ForgeUIEffects.apply_button_effect(bnav_exit_to_menu, 1.05, Color(1.15, 0.9, 0.4))

	ForgeUIEffects.apply_button_effect(btn_hero_click, 1.06, Color(1.2, 0.75, 0.2))

	debug_console.boss_fight_requested.connect(_on_boss_fight_requested)
	btn_hero_click.pressed.connect(_on_hero_click_pressed)

	get_tree().root.size_changed.connect(_on_window_resized)
	_on_window_resized()
	_update_hud(false)
	_switch_view("combat")

var _is_hud_portrait: bool = false

func _apply_hud_layout(is_portrait: bool):
	if is_portrait == _is_hud_portrait:
		return
	_is_hud_portrait = is_portrait

	if top_hud == null or hud_row2 == null or hud_hbox == null:
		return

	if is_portrait:
		top_hud.custom_minimum_size.y = 86
		hud_row2.visible = true
		if hp_box and hp_box.get_parent() != hud_row2:
			hp_box.reparent(hud_row2)
		if mana_box and mana_box.get_parent() != hud_row2:
			mana_box.reparent(hud_row2)
		if exp_box and exp_box.get_parent() != hud_row2:
			exp_box.reparent(hud_row2)
		if companion_lbl and companion_lbl.get_parent() != hud_row2:
			companion_lbl.reparent(hud_row2)
	else:
		top_hud.custom_minimum_size.y = 58
		hud_row2.visible = false
		if exp_box and exp_box.get_parent() != hud_hbox:
			exp_box.reparent(hud_hbox)
			hud_hbox.move_child(exp_box, 2)
		if hp_box and hp_box.get_parent() != hud_hbox:
			hp_box.reparent(hud_hbox)
			hud_hbox.move_child(hp_box, 3)
		if mana_box and mana_box.get_parent() != hud_hbox:
			mana_box.reparent(hud_hbox)
			hud_hbox.move_child(mana_box, 4)
		if companion_lbl and companion_lbl.get_parent() != hud_hbox:
			companion_lbl.reparent(hud_hbox)
			hud_hbox.move_child(companion_lbl, 6)

func _on_window_resized():
	if not is_inside_tree(): return
	var win_size: Vector2 = get_viewport().get_visible_rect().size
	var is_portrait = win_size.y > win_size.x
	var is_compact = win_size.x < 1180
	var is_ultra_compact = win_size.x < 980 or is_portrait

	if nav_sidebar:
		nav_sidebar.visible = not is_portrait
	if bottom_nav:
		bottom_nav.visible = is_portrait

	_apply_hud_layout(is_portrait)

	if hud_hbox:
		if is_ultra_compact:
			hud_hbox.add_theme_constant_override("separation", 6)
			if hud_margin:
				hud_margin.add_theme_constant_override("margin_left", 6)
				hud_margin.add_theme_constant_override("margin_right", 6)
			exp_bar.custom_minimum_size.x = 55
			hp_bar.custom_minimum_size.x = 65
			mana_bar.custom_minimum_size.x = 55
			btn_hero_click.custom_minimum_size.x = 95
			btn_hero_click.text = "+Złoto"
			if nav_sidebar:
				nav_sidebar.custom_minimum_size.x = 175
		elif is_compact:
			hud_hbox.add_theme_constant_override("separation", 10)
			if hud_margin:
				hud_margin.add_theme_constant_override("margin_left", 10)
				hud_margin.add_theme_constant_override("margin_right", 10)
			exp_bar.custom_minimum_size.x = 75
			hp_bar.custom_minimum_size.x = 85
			mana_bar.custom_minimum_size.x = 70
			btn_hero_click.custom_minimum_size.x = 110
			btn_hero_click.text = "Klik Złoto"
			if nav_sidebar:
				nav_sidebar.custom_minimum_size.x = 195
		else:
			hud_hbox.add_theme_constant_override("separation", 16)
			if hud_margin:
				hud_margin.add_theme_constant_override("margin_left", 16)
				hud_margin.add_theme_constant_override("margin_right", 16)
			exp_bar.custom_minimum_size.x = 100
			hp_bar.custom_minimum_size.x = 110
			mana_bar.custom_minimum_size.x = 90
			btn_hero_click.custom_minimum_size.x = 130
			btn_hero_click.text = "Kliknij po Złoto"
			if nav_sidebar:
				nav_sidebar.custom_minimum_size.x = 215

	if notification_toast:
		var toast_w = min(460.0, win_size.x - 24.0)
		notification_toast.custom_minimum_size.x = toast_w
		notification_toast.offset_left = -toast_w / 2.0
		notification_toast.offset_right = toast_w / 2.0
		notification_toast.offset_top = 96.0 if is_portrait else 64.0
		notification_toast.offset_bottom = notification_toast.offset_top + 42.0

	_update_hud(false)

func _unhandled_input(event: InputEvent):
	if event is InputEventKey and event.is_pressed() and not event.is_echo():
		if event.keycode == KEY_F12 or event.keycode == KEY_QUOTELEFT:
			_toggle_debug_console()
			get_viewport().set_input_as_handled()

func _toggle_debug_console():
	debug_console.visible = not debug_console.visible
	if debug_console.visible:
		SoundManager.play_click()

func _on_boss_fight_requested(boss_id: String):
	_switch_view("combat")
	if current_view_node and current_view_node.has_method("_start_combat_with_enemy"):
		var boss_data = EnemiesDB.get_hardcoded_boss(boss_id, player.level)
		current_view_node._start_combat_with_enemy(boss_data)
		_show_notification("Rozpoczęto bezpośrednią walkę z bossem: %s!" % boss_data.get("name", boss_id))

func _on_second_tick():
	_update_hud(true)

func _update_hud(animated: bool = true):
	if player == null: return
	var win_size: Vector2 = get_viewport().get_visible_rect().size
	var is_compact = win_size.x < 1180
	var is_ultra_compact = win_size.x < 980 or (win_size.y > win_size.x)

	if hero_avatar and hero_avatar.texture == null:
		var hero_path = "res://assets/portraits/hero.jpg"
		if ResourceLoader.exists(hero_path):
			hero_avatar.texture = load(hero_path)

	if is_ultra_compact:
		hero_level_lbl.text = "Poz. %d" % player.level
		hp_lbl.text = "%d HP" % player.hp
		mana_lbl.text = "%d MP" % player.mana
		gold_lbl.text = "%d zł" % player.gold
	elif is_compact:
		hero_level_lbl.text = "%s (P.%d)" % [player.name, player.level]
		hp_lbl.text = "%d/%d" % [player.hp, player.get_max_hp()]
		mana_lbl.text = "%d/%d" % [player.mana, player.max_mana]
		var gps = player.stats.get("gold_per_sec", 0)
		gold_lbl.text = "%d zł (+%d/s)" % [player.gold, gps]
	else:
		hero_level_lbl.text = "%s (Poz. %d)" % [player.name, player.level]
		hp_lbl.text = "%d / %d HP" % [player.hp, player.get_max_hp()]
		mana_lbl.text = "%d / %d Many" % [player.mana, player.max_mana]
		var gps = player.stats.get("gold_per_sec", 0)
		gold_lbl.text = "%d złota (+%d/s)" % [player.gold, gps]

	var req_exp = player.get_exp_required()
	exp_bar.max_value = req_exp
	if animated:
		ForgeUIEffects.animate_bar_value(exp_bar, player.exp, 0.4)
	else:
		exp_bar.value = player.exp

	hp_bar.max_value = player.get_max_hp()
	if animated:
		ForgeUIEffects.animate_bar_value(hp_bar, player.hp, 0.3)
	else:
		hp_bar.value = player.hp

	mana_bar.max_value = player.max_mana
	if animated:
		ForgeUIEffects.animate_bar_value(mana_bar, player.mana, 0.3)
	else:
		mana_bar.value = player.mana

	if player.active_companion != null:
		var c_name = NPCLoreDB.NPCS.get(player.active_companion, {}).get("name", str(player.active_companion))
		companion_lbl.text = "Towarzysz: %s" % c_name if not is_compact else c_name
	else:
		companion_lbl.text = "Towarzysz: Brak" if not is_compact else "Brak"

func _switch_view(view_key: String):
	if not VIEWS.has(view_key):
		return

	GameManager.current_view = view_key
	SoundManager.play_click()

	# Wyróżnij aktywny przycisk nawigacji żarem kutego złota
	var nav_buttons = {
		"combat": nav_combat, "dungeons": nav_dungeons, "stats": nav_stats,
		"inventory": nav_inventory, "tavern": nav_tavern, "alchemy": nav_alchemy,
		"market": nav_market, "shop": nav_shop, "blacksmith": nav_blacksmith, "achievements": nav_achievements
	}
	for k in nav_buttons.keys():
		var btn = nav_buttons[k]
		if btn:
			if k == view_key:
				btn.modulate = Color(1.2, 0.9, 0.3, 1.0)
				ForgeUIEffects.pulse_node(btn, 1.06)
			else:
				btn.modulate = Color.WHITE

	var bnav_buttons = {
		"combat": bnav_combat, "dungeons": bnav_dungeons, "stats": bnav_stats,
		"inventory": bnav_inventory, "tavern": bnav_tavern, "alchemy": bnav_alchemy,
		"market": bnav_market, "shop": bnav_shop, "blacksmith": bnav_blacksmith, "achievements": bnav_achievements
	}
	for k in bnav_buttons.keys():
		var b_btn = bnav_buttons[k]
		if b_btn:
			if k == view_key:
				b_btn.modulate = Color(1.2, 0.9, 0.3, 1.0)
				ForgeUIEffects.pulse_node(b_btn, 1.06)
			else:
				b_btn.modulate = Color.WHITE

	if current_view_node != null:
		view_container.remove_child(current_view_node)

	if not loaded_views.has(view_key):
		var scene_res = load(VIEWS[view_key])
		var inst = scene_res.instantiate()
		ForgeUIEffects.register_interactive_controls(inst)
		loaded_views[view_key] = inst

	current_view_node = loaded_views[view_key]
	view_container.add_child(current_view_node)

	if current_view_node.has_method("_refresh_ui"):
		current_view_node._refresh_ui()

func _on_hero_click_pressed():
	SoundManager.play_coin()
	ForgeUIEffects.pulse_node(btn_hero_click, 1.08)
	ForgeUIEffects.pulse_node(gold_lbl, 1.15)
	var earned = player.click()
	_update_hud(true)
	_show_notification("+%d złota z kliknięcia!" % earned)

func _on_save_pressed():
	SoundManager.play_click()
	GameManager.save_now()
	_show_notification("Stan gry został pomyślnie zapisany!")

func _on_exit_to_menu_pressed():
	SoundManager.play_click()
	GameManager.return_to_main_menu()

var notification_tween: Tween

func _show_notification(text: String):
	if notification_lbl == null:
		return
	notification_lbl.text = text

	if notification_toast != null:
		notification_toast.visible = true
		if notification_tween and notification_tween.is_valid():
			notification_tween.kill()

		notification_toast.modulate.a = 0.0
		notification_tween = create_tween()
		notification_tween.tween_property(notification_toast, "modulate:a", 1.0, 0.16)
		notification_tween.tween_interval(2.6)
		notification_tween.tween_property(notification_toast, "modulate:a", 0.0, 0.35)
		notification_tween.tween_callback(func():
			if is_instance_valid(notification_toast):
				notification_toast.visible = false
		)
	else:
		notification_lbl.modulate.a = 1.0
		if notification_tween and notification_tween.is_valid():
			notification_tween.kill()
		notification_tween = create_tween()
		notification_tween.tween_interval(2.5)
		notification_tween.tween_property(notification_lbl, "modulate:a", 0.0, 0.8)
