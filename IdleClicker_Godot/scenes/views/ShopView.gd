extends Control

const ShopDB = preload("res://scripts/data/ShopDB.gd")
const ItemsDB = preload("res://scripts/data/ItemsDB.gd")

@onready var shop_subtitle: Label = %ShopSubtitle
@onready var shop_tabs_box: HBoxContainer = %ShopTabsBox
@onready var tier_name_label: Label = %TierNameLabel
@onready var tier_req_label: Label = %TierReqLabel
@onready var shop_items_box: VBoxContainer = %ShopItemsBox

var player: Player
var selected_tier: int = 1

func _ready():
	player = GameManager.player
	player.stats_changed.connect(_refresh_ui)
	player.gold_changed.connect(func(_g): _refresh_ui())
	player.level_up.connect(func(_lvl): _refresh_ui())

	_setup_tabs()
	_refresh_ui()

func _setup_tabs():
	for c in shop_tabs_box.get_children():
		c.queue_free()

	for tid in ShopDB.TIERS.keys():
		var t_data = ShopDB.TIERS[tid]
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(120, 38)

		var is_locked = (player.level < t_data["req_level"])
		var tab_title = t_data["label"]
		if is_locked:
			tab_title = "[Poz. %d] %s" % [t_data["req_level"], t_data["label"]]

		btn.text = tab_title
		btn.pressed.connect(_on_tab_selected.bind(tid))
		shop_tabs_box.add_child(btn)

func _on_tab_selected(tier_id: int):
	selected_tier = tier_id
	_refresh_ui()

func _refresh_ui():
	if player == null: return

	shop_subtitle.text = "Twoje złoto: %d | Twój Poziom: %d" % [player.gold, player.level]

	var t_data = ShopDB.TIERS.get(selected_tier, ShopDB.TIERS[1])
	tier_name_label.text = "Kategoria: %s (%s)" % [t_data["name"], t_data["label"]]

	var is_tier_locked = (player.level < t_data["req_level"])
	if is_tier_locked:
		tier_req_label.text = "Wymagany %d poziom bohatera" % t_data["req_level"]
		tier_req_label.modulate = Color(1.0, 0.4, 0.4)
	else:
		tier_req_label.text = "Status: Dostępny do zakupu"
		tier_req_label.modulate = Color(0.3, 0.9, 0.4)

	# Podświetlenie aktywnej zakładki
	var tab_idx = 0
	for btn in shop_tabs_box.get_children():
		var tid = ShopDB.TIERS.keys()[tab_idx]
		var locked = (player.level < ShopDB.TIERS[tid]["req_level"])
		if tid == selected_tier:
			btn.modulate = Color.YELLOW
		elif locked:
			btn.modulate = Color(0.6, 0.6, 0.6)
		else:
			btn.modulate = Color.WHITE
		tab_idx += 1

	_render_items(t_data)

func _render_items(t_data: Dictionary):
	for c in shop_items_box.get_children():
		c.queue_free()

	var req_lvl = t_data["req_level"]
	var is_tier_locked = (player.level < req_lvl)

	for item_id in t_data.get("items", []):
		var raw_item = ItemsDB.ITEMS.get(item_id, {})
		if raw_item.is_empty(): continue

		var price = ShopDB.get_item_price(item_id, player.level)
		var item_req_lvl = raw_item.get("level_req", req_lvl)
		var is_item_locked = (player.level < item_req_lvl)

		var row = PanelContainer.new()
		var hbox = HBoxContainer.new()
		hbox.add_theme_constant_override("separation", 14)

		# Ikona
		var icon_rect = TextureRect.new()
		icon_rect.custom_minimum_size = Vector2(56, 56)
		icon_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED

		var icon_path = raw_item.get("icon", "")
		if ResourceLoader.exists(icon_path):
			icon_rect.texture = load(icon_path)
		hbox.add_child(icon_rect)

		# Informacje
		var info_box = VBoxContainer.new()
		info_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL

		var name_lbl = Label.new()
		name_lbl.text = raw_item.get("name", item_id)
		name_lbl.add_theme_font_size_override("font_size", 14)
		name_lbl.modulate = Color(0.95, 0.85, 0.4) if not is_item_locked else Color(0.7, 0.7, 0.7)
		info_box.add_child(name_lbl)

		# Statystyki / Efekty
		var stats_lbl = Label.new()
		stats_lbl.add_theme_font_size_override("font_size", 12)

		if raw_item.has("base_stats"):
			var stat_parts = []
			for sk in raw_item["base_stats"].keys():
				stat_parts.append("%s: +%s" % [sk.to_upper(), str(raw_item["base_stats"][sk])])
			stats_lbl.text = "Statystyki: %s" % ", ".join(stat_parts)
			stats_lbl.modulate = Color(0.5, 1.0, 0.6)
		elif raw_item.has("effect"):
			var eff_parts = []
			for ek in raw_item["effect"].keys():
				eff_parts.append("%s: %s" % [ek.to_upper(), str(raw_item["effect"][ek])])
			stats_lbl.text = "Efekt: %s" % ", ".join(eff_parts)
			stats_lbl.modulate = Color(0.4, 0.8, 1.0)
		info_box.add_child(stats_lbl)

		var desc_lbl = Label.new()
		desc_lbl.text = raw_item.get("description", "")
		desc_lbl.add_theme_font_size_override("font_size", 11)
		desc_lbl.modulate = Color(0.8, 0.8, 0.8)
		info_box.add_child(desc_lbl)

		hbox.add_child(info_box)

		# Przycisk zakupu
		var buy_btn = Button.new()
		buy_btn.custom_minimum_size = Vector2(170, 40)

		if is_item_locked:
			buy_btn.text = "Wymaga Poz. %d" % item_req_lvl
			buy_btn.disabled = true
		elif player.is_inventory_full():
			buy_btn.text = "Plecak pełny"
			buy_btn.disabled = true
		elif player.gold < price:
			buy_btn.text = "Kup (%d złota)" % price
			buy_btn.disabled = true
		else:
			buy_btn.text = "Kup (%d złota)" % price
			buy_btn.pressed.connect(_buy_item.bind(item_id, price, raw_item.get("name", item_id)))

		hbox.add_child(buy_btn)
		row.add_child(hbox)
		shop_items_box.add_child(row)

func _buy_item(item_id: String, price: int, item_name: String):
	if player.gold < price:
		GameManager.post_notification("Brak wystarczającej ilości złota!")
		return
	if player.is_inventory_full():
		GameManager.post_notification("Twój ekwipunek jest pełny (80 slotów)!")
		return

	player.gold -= price
	player.add_to_inventory(item_id)
	SoundManager.play_pickup()
	GameManager.post_notification("Pomyślnie zakupiono %s za %d złota!" % [item_name, price])
	player.gold_changed.emit(player.gold)
	player.stats_changed.emit()
	_refresh_ui()
