extends Control

@onready var buildings_container: VBoxContainer = %BuildingsContainer
@onready var total_gps_lbl: Label = %TotalGpsLabel

var player: Player

func _ready():
	player = GameManager.player
	player.stats_changed.connect(_refresh_ui)
	player.gold_changed.connect(func(g): _refresh_ui())
	_refresh_ui()

func _refresh_ui():
	if player == null: return
	var gps = player.recalculate_gold_per_sec()
	total_gps_lbl.text = "Łączny Pasywny Przychód: +%d złota / sek" % gps

	for c in buildings_container.get_children():
		c.queue_free()

	for b_id in BuildingsDB.BUILDINGS.keys():
		var b = BuildingsDB.BUILDINGS[b_id]
		var count = player.buildings.get(b_id, 0)
		var cost = BuildingsDB.get_cost(b_id, count)
		var mult = BuildingsDB.get_synergy_multiplier(b_id, player.party, player.active_companion)

		var card = PanelContainer.new()
		var h = HBoxContainer.new()
		card.add_child(h)

		var info = VBoxContainer.new()
		info.size_flags_horizontal = SIZE_EXPAND_FILL
		h.add_child(info)

		var name_lbl = Label.new()
		name_lbl.text = "%s (Posiadasz: %d)" % [b["name"], count]
		name_lbl.add_theme_color_override("font_color", Color("#f4d03f"))
		name_lbl.add_theme_font_size_override("font_size", 15)
		info.add_child(name_lbl)

		var desc_lbl = Label.new()
		desc_lbl.text = b["description"]
		desc_lbl.add_theme_font_size_override("font_size", 12)
		info.add_child(desc_lbl)

		var stats_lbl = Label.new()
		var single_gps = int(float(b["gold_per_sec"]) * mult)
		var synergy_txt = ""
		if mult >= 1.40:
			synergy_txt = " [Synergia: +40% (Aktywny)]"
		elif mult >= 1.25:
			synergy_txt = " [Synergia: +25% (W drużynie)]"
		stats_lbl.text = "Produkcja: +%d złoto/s (Bazowo: +%d/s)%s" % [single_gps, b["gold_per_sec"], synergy_txt]
		stats_lbl.add_theme_font_size_override("font_size", 12)
		stats_lbl.add_theme_color_override("font_color", Color("#2ecc71"))
		info.add_child(stats_lbl)

		var btn_buy = Button.new()
		btn_buy.custom_minimum_size = Vector2(170, 44)
		btn_buy.text = "Kup (%d złota)" % cost
		btn_buy.disabled = (player.gold < cost)
		btn_buy.pressed.connect(func(): _buy_building(b_id, cost))
		h.add_child(btn_buy)

		buildings_container.add_child(card)

func _buy_building(b_id: String, cost: int):
	if player.gold >= cost:
		player.gold -= cost
		player.buildings[b_id] = player.buildings.get(b_id, 0) + 1
		player.recalculate_gold_per_sec()
		SoundManager.play_coin()
		player.gold_changed.emit(player.gold)
		player.stats_changed.emit()
		_refresh_ui()
