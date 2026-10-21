extends Control

const ForgeUIEffects = preload("res://scripts/ui/ForgeUIEffects.gd")

@onready var hero_portrait: TextureRect = %HeroPortrait
@onready var level_lbl: Label = %LevelLabel
@onready var exp_bar: ProgressBar = %ExpBar
@onready var exp_lbl: Label = %ExpLabel

# Statystyki Bojowe
@onready var stat_atk_lbl: Label = %StatAtkLabel
@onready var stat_def_lbl: Label = %StatDefLabel
@onready var stat_crit_lbl: Label = %StatCritLabel
@onready var stat_double_lbl: Label = %StatDoubleLabel
@onready var stat_hp_lbl: Label = %StatHpLabel
@onready var stat_click_lbl: Label = %StatClickLabel
@onready var stat_gps_lbl: Label = %StatGpsLabel
@onready var stat_bestiary_lbl: Label = %StatBestiaryLabel

# Rozdział Punktów Statystyk
@onready var stat_points_lbl: Label = %StatPointsLabel
@onready var lbl_atk_invest: Label = %LblAtkInvest
@onready var btn_atk_plus1: Button = %BtnAtkPlus1
@onready var btn_atk_plus5: Button = %BtnAtkPlus5

@onready var lbl_def_invest: Label = %LblDefInvest
@onready var btn_def_plus1: Button = %BtnDefPlus1
@onready var btn_def_plus5: Button = %BtnDefPlus5

@onready var lbl_hp_invest: Label = %LblHpInvest
@onready var btn_hp_plus1: Button = %BtnHpPlus1
@onready var btn_hp_plus5: Button = %BtnHpPlus5

@onready var lbl_crit_invest: Label = %LblCritInvest
@onready var btn_crit_plus1: Button = %BtnCritPlus1
@onready var btn_crit_plus5: Button = %BtnCritPlus5

@onready var lbl_loot_invest: Label = %LblLootInvest
@onready var btn_loot_plus1: Button = %BtnLootPlus1
@onready var btn_loot_plus5: Button = %BtnLootPlus5

# Talenty
@onready var talent_points_lbl: Label = %TalentPointsLabel
@onready var btn_talent_berserker: Button = %BtnTalentBerserker
@onready var btn_talent_defender: Button = %BtnTalentDefender
@onready var btn_talent_rogue: Button = %BtnTalentRogue
@onready var talent_berserker_lbl: Label = %TalentBerserkerLabel
@onready var talent_defender_lbl: Label = %TalentDefenderLabel
@onready var talent_rogue_lbl: Label = %TalentRogueLabel

# Responsywne panele i mobilny pasek zakładek
@onready var main_layout: HBoxContainer = %MainLayout if has_node("%MainLayout") else null
@onready var mobile_tab_bar: HBoxContainer = %MobileTabBar if has_node("%MobileTabBar") else null
@onready var btn_tab_stats: Button = %BtnTabStats if has_node("%BtnTabStats") else null
@onready var btn_tab_talents: Button = %BtnTabTalents if has_node("%BtnTabTalents") else null
@onready var left_panel: PanelContainer = %LeftPanel if has_node("%LeftPanel") else null
@onready var right_panel: PanelContainer = %RightPanel if has_node("%RightPanel") else null

var player: Player
var _current_mobile_tab: int = 0
var _is_portrait_layout: bool = false

func _apply_orientation_layout(is_portrait: bool):
	_is_portrait_layout = is_portrait
	if mobile_tab_bar == null or left_panel == null or right_panel == null:
		return

	if is_portrait:
		mobile_tab_bar.visible = true
		if main_layout:
			main_layout.offset_top = 66.0
		_select_mobile_tab(_current_mobile_tab)
	else:
		mobile_tab_bar.visible = false
		if main_layout:
			main_layout.offset_top = 16.0
		left_panel.visible = true
		right_panel.visible = true

func _select_mobile_tab(tab_idx: int):
	_current_mobile_tab = tab_idx
	if not _is_portrait_layout:
		if left_panel: left_panel.visible = true
		if right_panel: right_panel.visible = true
		return

	if tab_idx == 0:
		if left_panel: left_panel.visible = true
		if right_panel: right_panel.visible = false
		if btn_tab_stats: btn_tab_stats.modulate = Color(1.2, 0.9, 0.3)
		if btn_tab_talents: btn_tab_talents.modulate = Color.WHITE
	else:
		if left_panel: left_panel.visible = false
		if right_panel: right_panel.visible = true
		if btn_tab_stats: btn_tab_stats.modulate = Color.WHITE
		if btn_tab_talents: btn_tab_talents.modulate = Color(1.2, 0.9, 0.3)

func _on_view_resized():
	if not is_inside_tree(): return
	var win_size: Vector2 = get_viewport().get_visible_rect().size
	var is_portrait = win_size.y > win_size.x
	_apply_orientation_layout(is_portrait)

func _get_game_manager() -> Node:
	return get_node_or_null("/root/GameManager")

func _get_sound_manager() -> Node:
	return get_node_or_null("/root/SoundManager")

func _ready():
	var gm = _get_game_manager()
	if gm and gm.player:
		player = gm.player
		player.stats_changed.connect(_refresh_ui)

	# Inwestycja punktów statystyk
	btn_atk_plus1.pressed.connect(func(): _invest_stat("base_atk", 1))
	btn_atk_plus5.pressed.connect(func(): _invest_stat("base_atk", 5))

	btn_def_plus1.pressed.connect(func(): _invest_stat("base_def", 1))
	btn_def_plus5.pressed.connect(func(): _invest_stat("base_def", 5))

	btn_hp_plus1.pressed.connect(func(): _invest_stat("max_hp", 1))
	btn_hp_plus5.pressed.connect(func(): _invest_stat("max_hp", 5))

	btn_crit_plus1.pressed.connect(func(): _invest_stat("crit_chance", 1))
	btn_crit_plus5.pressed.connect(func(): _invest_stat("crit_chance", 5))

	btn_loot_plus1.pressed.connect(func(): _invest_stat("bonus_loot_pct", 1))
	btn_loot_plus5.pressed.connect(func(): _invest_stat("bonus_loot_pct", 5))

	# Inwestycja talentów
	btn_talent_berserker.pressed.connect(func(): _invest_talent("berserker"))
	btn_talent_defender.pressed.connect(func(): _invest_talent("defender"))
	btn_talent_rogue.pressed.connect(func(): _invest_talent("rogue"))

	if btn_tab_stats:
		btn_tab_stats.pressed.connect(func(): _select_mobile_tab(0))
		ForgeUIEffects.apply_button_effect(btn_tab_stats, 1.05, Color(1.15, 0.9, 0.4))
	if btn_tab_talents:
		btn_tab_talents.pressed.connect(func(): _select_mobile_tab(1))
		ForgeUIEffects.apply_button_effect(btn_tab_talents, 1.05, Color(1.15, 0.9, 0.4))

	get_tree().root.size_changed.connect(_on_view_resized)
	_on_view_resized()

	_refresh_ui()
	ForgeUIEffects.register_interactive_controls(self)

func _refresh_ui():
	_on_view_resized()
	if player == null: return

	level_lbl.text = "%s (Poziom %d)" % [player.name, player.level]
	var req_exp = player.get_exp_required()
	exp_bar.max_value = req_exp
	ForgeUIEffects.animate_bar_value(exp_bar, player.exp)
	exp_lbl.text = "%d / %d EXP (%d do awansu)" % [player.exp, req_exp, req_exp - player.exp]

	stat_atk_lbl.text = "Atak (ATK): %d" % player.get_total_atk()
	stat_def_lbl.text = "Pancerz (DEF): %d" % player.get_total_def()
	stat_crit_lbl.text = "Szansa na Kryt: %d%%" % player.get_total_crit()
	stat_double_lbl.text = "Podwójny Cios: %d%%" % player.get_double_strike_chance()
	stat_hp_lbl.text = "Maksymalne Zdrowie (HP): %d" % player.get_max_hp()
	stat_click_lbl.text = "Obrażenia Kliknięcia: %d" % player.get_combat_click_dmg()
	stat_gps_lbl.text = "Pasywny Przychód Złota: +%d/s" % player.recalculate_gold_per_sec()

	var total_kills = 0
	for count in player.bestiary.values():
		total_kills += count
	stat_bestiary_lbl.text = "Pokonani wrogowie: %d (+%d%% do obrażeń)" % [total_kills, int(player.get_bestiary_bonus() * 100.0)]

	# Rozdział Punktów Statystyk
	var pts = player.stat_points
	stat_points_lbl.text = "Dostępne Punkty Rozwoju: %d (+3 za awans)" % pts
	stat_points_lbl.modulate = Color(0.3, 0.9, 0.4) if pts > 0 else Color(0.7, 0.7, 0.7)

	var has_pts_1 = (pts >= 1)
	var has_pts_5 = (pts >= 5)

	lbl_atk_invest.text = "Atak (+1 ATK): bazowo %d" % player.stats.get("base_atk", 8)
	btn_atk_plus1.disabled = not has_pts_1
	btn_atk_plus5.disabled = not has_pts_5

	lbl_def_invest.text = "Pancerz (+1 DEF): bazowo %d" % player.stats.get("base_def", 4)
	btn_def_plus1.disabled = not has_pts_1
	btn_def_plus5.disabled = not has_pts_5

	lbl_hp_invest.text = "Zdrowie (+8 HP): maks %d" % player.max_hp
	btn_hp_plus1.disabled = not has_pts_1
	btn_hp_plus5.disabled = not has_pts_5

	var cur_crit = player.stats.get("crit_chance", 0)
	lbl_crit_invest.text = "Krytyk (+1%%, max 30%%): %d%%" % cur_crit
	btn_crit_plus1.disabled = (not has_pts_1 or cur_crit >= 30)
	btn_crit_plus5.disabled = (not has_pts_5 or cur_crit >= 30)

	var cur_loot = player.stats.get("bonus_loot_pct", 0)
	lbl_loot_invest.text = "Łup (+1%%, max 50%%): %d%%" % cur_loot
	btn_loot_plus1.disabled = (not has_pts_1 or cur_loot >= 50)
	btn_loot_plus5.disabled = (not has_pts_5 or cur_loot >= 50)

	# Talenty
	talent_points_lbl.text = "Dostępne Punkty Talentu: %d (1 pkt co 5 poziomów od poz. 10)" % player.talent_points
	var can_invest = player.talent_points > 0

	var bers_pts = player.talents.get("berserker", 0)
	talent_berserker_lbl.text = "Ścieżka Berserkera (%d/10)\nAgresja i krytyki: +%d%% ATK (HP < 50%%), +%d%% dmg krytyka." % [bers_pts, bers_pts * 4, bers_pts * 6]
	btn_talent_berserker.disabled = (not can_invest or bers_pts >= 10)

	var def_pts = player.talents.get("defender", 0)
	talent_defender_lbl.text = "Ścieżka Obrońcy (%d/10)\nNiezłomność: odbija %d%% dmg wroga, regeneruje %d%% HP/turę." % [def_pts, def_pts * 5, def_pts * 1]
	btn_talent_defender.disabled = (not can_invest or def_pts >= 10)

	var rog_pts = player.talents.get("rogue", 0)
	talent_rogue_lbl.text = "Ścieżka Awanturnika (%d/10)\nZwinność: +%d%% click dmg, +%d%% złota, +%d%% lifesteal." % [rog_pts, rog_pts * 10, rog_pts * 3, rog_pts * 2]
	btn_talent_rogue.disabled = (not can_invest or rog_pts >= 10)

func _invest_stat(stat_name: String, amount: int):
	if player and player.invest_stat_point(stat_name, amount):
		var sm = _get_sound_manager()
		if sm and sm.has_method("play_level_up"):
			sm.play_level_up()
		ForgeUIEffects.pulse_node(stat_points_lbl, 1.15)
		_refresh_ui()

func _invest_talent(path: String):
	if player and player.invest_talent(path):
		var sm = _get_sound_manager()
		if sm and sm.has_method("play_level_up"):
			sm.play_level_up()
		ForgeUIEffects.pulse_node(talent_points_lbl, 1.15)
		_refresh_ui()
