extends Control

@onready var tab_btn_upgrade: Button = %TabBtnUpgrade
@onready var tab_btn_gems: Button = %TabBtnGems
@onready var upgrade_container: Control = %UpgradeContainer
@onready var gems_container: Control = %GemsContainer
@onready var upgrade_list_box: VBoxContainer = %UpgradeListBox
@onready var gems_list_box: VBoxContainer = %GemsListBox
@onready var gold_lbl: Label = %GoldLabel

var player: Player
var current_tab: String = "upgrade"

func _on_view_resized():
	if not is_inside_tree(): return
	var win_size: Vector2 = get_viewport().get_visible_rect().size
	var is_portrait = win_size.y > win_size.x
	if tab_btn_upgrade and tab_btn_gems:
		if is_portrait:
			tab_btn_upgrade.text = "Ulepszanie (+1 do +9)"
			tab_btn_gems.text = "Gniazda & Klejnoty"
		else:
			tab_btn_upgrade.text = "Ulepszanie Przedmiotów (+1 do +9)"
			tab_btn_gems.text = "Magiczne Gniazda & Klejnoty"

func _ready():
	player = GameManager.player
	player.stats_changed.connect(_refresh_ui)
	player.gold_changed.connect(func(g): _refresh_ui())

	tab_btn_upgrade.pressed.connect(func(): _switch_tab("upgrade"))
	tab_btn_gems.pressed.connect(func(): _switch_tab("gems"))

	get_tree().root.size_changed.connect(_on_view_resized)
	_on_view_resized()

	_switch_tab("upgrade")
	_refresh_ui()

func _switch_tab(tab_name: String):
	current_tab = tab_name
	upgrade_container.visible = (tab_name == "upgrade")
	gems_container.visible = (tab_name == "gems")

	tab_btn_upgrade.modulate = Color.YELLOW if tab_name == "upgrade" else Color.WHITE
	tab_btn_gems.modulate = Color.YELLOW if tab_name == "gems" else Color.WHITE

func _refresh_ui():
	if player == null: return
	gold_lbl.text = "Twoje złoto: %d" % player.gold

	if current_tab == "upgrade":
		_render_upgrades()
	else:
		_render_sockets()

func _render_upgrades():
	for c in upgrade_list_box.get_children():
		c.queue_free()

	var all_items: Array = []
	for slot in player.equipment.keys():
		var eq = player.equipment[slot]
		if eq != null:
			all_items.append({"item": eq, "location": "[Założone: %s]" % slot.to_upper()})

	for it in player.inventory:
		var res = ItemsDB.resolve_item(it)
		if res.get("type") == "equipment":
			all_items.append({"item": it, "location": "[Plecak]"})

	if all_items.is_empty():
		var empty_lbl = Label.new()
		empty_lbl.text = "Nie posiadasz żadnego sprzętu do ulepszenia."
		upgrade_list_box.add_child(empty_lbl)
		return

	for entry in all_items:
		var item_dict = entry["item"]
		var loc = entry["location"]
		var resolved = ItemsDB.resolve_item(item_dict)

		var card = PanelContainer.new()
		var h = HBoxContainer.new()
		card.add_child(h)

		var info = VBoxContainer.new()
		info.size_flags_horizontal = SIZE_EXPAND_FILL
		h.add_child(info)

		var lvl = item_dict.get("lvl", 0)
		var name_lbl = Label.new()
		name_lbl.text = "%s %s" % [resolved.get("display_name", resolved["name"]), loc]
		name_lbl.add_theme_color_override("font_color", Color("#f4d03f"))
		info.add_child(name_lbl)

		var stats = resolved.get("stats", {})
		var base_stats_val = float(stats.get("atk", 0) + stats.get("def", 0)) + (float(stats.get("hp_max", 0)) / 10.0)
		var cost = maxi(10, int(base_stats_val * 50.0 * pow(1.9, float(lvl))))

		if player.active_companion == "yomen":
			cost = maxi(5, int(float(cost) * 0.85))
		if player.permanent_perks.has("perk_master_smith"):
			cost = maxi(5, int(float(cost) * 0.90))

		var cur_stats_strs = []
		for k in stats.keys():
			cur_stats_strs.append("%s: +%d" % [k.to_upper(), stats[k]])

		var desc_lbl = Label.new()
		desc_lbl.text = "Aktualnie: " + ", ".join(cur_stats_strs)
		desc_lbl.add_theme_font_size_override("font_size", 12)
		info.add_child(desc_lbl)

		var btn_upg = Button.new()
		btn_upg.custom_minimum_size = Vector2(160, 44)
		if lvl >= 9:
			btn_upg.text = "MAX (+9)"
			btn_upg.disabled = true
		else:
			btn_upg.text = "Ulepsz (%d złota)" % cost
			btn_upg.disabled = (player.gold < cost)
			btn_upg.pressed.connect(func(): _upgrade_item(item_dict, cost))
		h.add_child(btn_upg)

		upgrade_list_box.add_child(card)

func _upgrade_item(item_dict: Dictionary, cost: int):
	if player.gold >= cost:
		player.gold -= cost
		item_dict["lvl"] = item_dict.get("lvl", 0) + 1
		player.record_achievement_stat("upgrades_done", 1, "add")
		player.record_achievement_stat("max_upgrade_level", item_dict["lvl"], "max")
		SoundManager.play_hit()
		SoundManager.play_coin()
		player.gold_changed.emit(player.gold)
		player.stats_changed.emit()
		_refresh_ui()

func _render_sockets():
	for c in gems_list_box.get_children():
		c.queue_free()

	var socketable_items: Array = []
	for slot in player.equipment.keys():
		var eq = player.equipment[slot]
		if eq != null:
			if not eq.has("sockets"):
				var res = ItemsDB.resolve_item(eq)
				eq["sockets"] = [null, null] if res.get("rarity") in ["Legendarny", "Mityczny"] else []
			socketable_items.append({"item": eq, "location": "[Założone: %s]" % slot.to_upper()})

	for it in player.inventory:
		var res = ItemsDB.resolve_item(it)
		if res.get("type") == "equipment":
			if not it.has("sockets"):
				it["sockets"] = [null, null] if res.get("rarity") in ["Legendarny", "Mityczny"] else []
			socketable_items.append({"item": it, "location": "[Plecak]"})

	for entry in socketable_items:
		var item_dict = entry["item"]
		var loc = entry["location"]
		var resolved = ItemsDB.resolve_item(item_dict)

		var card = PanelContainer.new()
		var v = VBoxContainer.new()
		card.add_child(v)

		var header_h = HBoxContainer.new()
		v.add_child(header_h)

		var name_lbl = Label.new()
		name_lbl.text = "%s %s" % [resolved.get("display_name", resolved["name"]), loc]
		name_lbl.add_theme_color_override("font_color", Color("#f4d03f"))
		name_lbl.size_flags_horizontal = SIZE_EXPAND_FILL
		header_h.add_child(name_lbl)

		var sockets: Array = item_dict.get("sockets", [])
		var req_lvl = resolved.get("level_req", 1)
		var max_sockets = 2 if (resolved.get("rarity") in ["Legendarny", "Mityczny"] or req_lvl >= 15) else 1

		# Wykuwanie gniazda
		if sockets.size() < max_sockets:
			var is_second = (sockets.size() == 1)
			var forge_cost = 400 if is_second else 150
			var req_ing = "ing_ectoplasm" if is_second else "ing_fang"
			var req_ing_name = "Ektoplazma" if is_second else "Kieł Bestii"
			var has_ing = _has_inventory_item(req_ing)

			var forge_h = HBoxContainer.new()
			var forge_lbl = Label.new()
			forge_lbl.text = "Wykuj Gniazdo #%d (Koszt: %dg + 1x %s)" % [sockets.size() + 1, forge_cost, req_ing_name]
			forge_lbl.size_flags_horizontal = SIZE_EXPAND_FILL
			forge_h.add_child(forge_lbl)

			var btn_forge = Button.new()
			btn_forge.text = "Wykuj Gniazdo"
			btn_forge.disabled = (player.gold < forge_cost or not has_ing)
			btn_forge.pressed.connect(func(): _forge_socket(item_dict, forge_cost, req_ing))
			forge_h.add_child(btn_forge)
			v.add_child(forge_h)

		# Lista gniazd
		for s_idx in range(sockets.size()):
			var gem_id = sockets[s_idx]
			var sock_h = HBoxContainer.new()
			var sock_lbl = Label.new()
			sock_lbl.size_flags_horizontal = SIZE_EXPAND_FILL

			if gem_id != null and gem_id != "":
				var gem_def = GemsDB.get_gem(gem_id)
				var summary = GemsDB.get_stat_summary(gem_id, resolved.get("level_req", 1))
				sock_lbl.text = "Gniazdo #%d: %s (%s)" % [s_idx + 1, gem_def.get("name", gem_id), summary]
				sock_lbl.add_theme_color_override("font_color", gem_def.get("color", Color.WHITE))
				sock_h.add_child(sock_lbl)
			else:
				sock_lbl.text = "Gniazdo #%d: [Puste Gniazdo]" % [s_idx + 1]
				sock_h.add_child(sock_lbl)

				# Przycisk wprawienia klejnotu
				var available_gem = _find_first_inventory_gem()
				if available_gem != "":
					var gem_def = GemsDB.get_gem(available_gem)
					var btn_sock = Button.new()
					btn_sock.text = "Wpraw %s" % gem_def.get("name", available_gem)
					btn_sock.pressed.connect(func(): _socket_gem(item_dict, s_idx, available_gem))
					sock_h.add_child(btn_sock)
				else:
					var no_gem_lbl = Label.new()
					no_gem_lbl.text = "Brak klejnotów w plecaku"
					sock_h.add_child(no_gem_lbl)

			v.add_child(sock_h)

		gems_list_box.add_child(card)

func _has_inventory_item(item_id: String) -> bool:
	for it in player.inventory:
		if it.get("id") == item_id:
			return true
	return false

func _find_first_inventory_gem() -> String:
	for it in player.inventory:
		var item_id = it.get("id", "")
		if GemsDB.GEMS.has(item_id):
			return item_id
	return ""

func _forge_socket(item_dict: Dictionary, cost: int, ing_id: String):
	if player.gold >= cost and _has_inventory_item(ing_id):
		player.gold -= cost
		for i in range(player.inventory.size() - 1, -1, -1):
			if player.inventory[i].get("id") == ing_id:
				player.remove_from_inventory(i)
				break
		item_dict["sockets"].append(null)
		SoundManager.play_hit()
		SoundManager.play_coin()
		player.stats_changed.emit()
		_refresh_ui()

func _socket_gem(item_dict: Dictionary, socket_idx: int, gem_id: String):
	for i in range(player.inventory.size() - 1, -1, -1):
		if player.inventory[i].get("id") == gem_id:
			player.remove_from_inventory(i)
			break
	item_dict["sockets"][socket_idx] = gem_id
	player.record_achievement_stat("gems_socketed", 1, "add")
	SoundManager.play_hit()
	player.stats_changed.emit()
	_refresh_ui()
