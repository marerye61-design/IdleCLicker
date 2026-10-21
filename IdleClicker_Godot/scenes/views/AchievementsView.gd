extends Control

@onready var perks_container: VBoxContainer = %PerksContainer
@onready var ach_list_box: VBoxContainer = %AchListBox

var player: Player

func _ready():
	player = GameManager.player
	player.stats_changed.connect(_refresh_ui)
	_refresh_ui()

func _refresh_ui():
	if player == null: return

	# Stałe perki
	for c in perks_container.get_children():
		c.queue_free()

	if player.permanent_perks.is_empty():
		var no_perks = Label.new()
		no_perks.text = "Brak odblokowanych stałych perków. Wykonuj osiągnięcia, aby zyskać trwałe ulepszenia!"
		no_perks.add_theme_font_size_override("font_size", 12)
		perks_container.add_child(no_perks)
	else:
		var p_text = Label.new()
		p_text.text = "Aktywne Stałe Perki: " + ", ".join(player.permanent_perks)
		p_text.add_theme_color_override("font_color", Color("#2ecc71"))
		p_text.add_theme_font_size_override("font_size", 13)
		perks_container.add_child(p_text)

	# Lista osiągnięć
	for c in ach_list_box.get_children():
		c.queue_free()

	for ach_id in AchievementsDB.ACHIEVEMENTS.keys():
		var ach = AchievementsDB.ACHIEVEMENTS[ach_id]
		var stat_cur = player.achievement_stats.get(ach["stat_key"], 0)
		var target = ach["target"]
		var ach_state = player.achievements.get(ach_id, {"completed": (stat_cur >= target), "claimed": false})
		var is_comp = ach_state.get("completed", stat_cur >= target)
		var is_claimed = ach_state.get("claimed", false)

		var card = PanelContainer.new()
		var h = HBoxContainer.new()
		card.add_child(h)

		var info = VBoxContainer.new()
		info.size_flags_horizontal = SIZE_EXPAND_FILL
		h.add_child(info)

		var title_lbl = Label.new()
		title_lbl.text = "[%s] %s" % [ach["category"].to_upper(), ach["title"]]
		title_lbl.add_theme_color_override("font_color", Color("#f4d03f") if is_comp else Color.WHITE)
		title_lbl.add_theme_font_size_override("font_size", 14)
		info.add_child(title_lbl)

		var desc_lbl = Label.new()
		desc_lbl.text = "%s (%d / %d)" % [ach["desc"], mini(stat_cur, target), target]
		desc_lbl.add_theme_font_size_override("font_size", 12)
		info.add_child(desc_lbl)

		var rew_parts: Array = []
		var rews = ach.get("rewards", {})
		if rews.has("gold"): rew_parts.append("+%d złota" % rews["gold"])
		if rews.has("exp"): rew_parts.append("+%d EXP" % rews["exp"])
		if rews.has("perk_desc"): rew_parts.append(rews["perk_desc"])

		var rew_lbl = Label.new()
		rew_lbl.text = "Nagroda: " + ", ".join(rew_parts)
		rew_lbl.add_theme_font_size_override("font_size", 11)
		rew_lbl.add_theme_color_override("font_color", Color("#3498db"))
		info.add_child(rew_lbl)

		var btn_claim = Button.new()
		btn_claim.custom_minimum_size = Vector2(140, 40)
		if is_claimed:
			btn_claim.text = "[Odebrano]"
			btn_claim.disabled = true
		elif is_comp:
			btn_claim.text = "Odbierz Nagrodę!"
			btn_claim.pressed.connect(func(): _claim_ach(ach_id))
		else:
			btn_claim.text = "%d / %d" % [stat_cur, target]
			btn_claim.disabled = true
		h.add_child(btn_claim)

		ach_list_box.add_child(card)

func _claim_ach(ach_id: String):
	if player.claim_achievement(ach_id):
		SoundManager.play_level_up()
		_refresh_ui()
