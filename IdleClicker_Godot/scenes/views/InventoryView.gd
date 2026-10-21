extends Control

const ForgeUIEffects = preload("res://scripts/ui/ForgeUIEffects.gd")
const ItemSlotScene = preload("res://scenes/components/ItemSlot.tscn")

@onready var slot_weapon: PanelContainer = %SlotWeapon
@onready var slot_armor: PanelContainer = %SlotArmor
@onready var slot_helmet: PanelContainer = %SlotHelmet
@onready var slot_accessory: PanelContainer = %SlotAccessory

@onready var inv_grid: GridContainer = %InventoryGrid
@onready var inv_capacity_lbl: Label = %CapacityLabel
@onready var btn_sort: Button = %BtnSort
@onready var btn_select_all_trash: Button = %BtnSelectAllTrash
@onready var btn_deselect_all: Button = %BtnDeselectAll
@onready var multi_select_hint: Label = %MultiSelectHint

# Panel szczegółów przedmiotu
@onready var details_panel: PanelContainer = %DetailsPanel
@onready var detail_icon: TextureRect = %DetailIcon
@onready var detail_name_lbl: Label = %DetailNameLabel
@onready var detail_type_lbl: Label = %DetailTypeLabel
@onready var detail_stats_lbl: Label = %DetailStatsLabel
@onready var detail_desc_lbl: Label = %DetailDescLabel
@onready var detail_value_lbl: Label = %DetailValueLabel
@onready var btn_equip: Button = %BtnEquip
@onready var btn_use: Button = %BtnUse
@onready var btn_sell: Button = %BtnSell
@onready var btn_unequip: Button = %BtnUnequip
@onready var btn_cancel_selection: Button = %BtnCancelSelection

var player: Player
var selected_item_data: Dictionary = {}
var selected_inv_index: int = -1
var selected_eq_slot: String = ""
var selected_inv_indices: Array[int] = []
var slot_nodes: Array[Control] = []

func _get_game_manager() -> Node:
	if not is_inside_tree():
		return null
	return get_node_or_null("/root/GameManager")

func _get_sound_manager() -> Node:
	if not is_inside_tree():
		return null
	return get_node_or_null("/root/SoundManager")

func _post_notification(text: String):
	var gm = _get_game_manager()
	if gm and gm.has_method("post_notification"):
		gm.post_notification(text)

func _play_sound(method_name: String):
	var sm = _get_sound_manager()
	if sm and sm.has_method(method_name):
		sm.call(method_name)

func _ensure_node_references():
	if details_panel == null: details_panel = get_node_or_null("%DetailsPanel")
	if detail_name_lbl == null: detail_name_lbl = get_node_or_null("%DetailNameLabel")
	if detail_icon == null: detail_icon = get_node_or_null("%DetailIcon")
	if detail_type_lbl == null: detail_type_lbl = get_node_or_null("%DetailTypeLabel")
	if detail_desc_lbl == null: detail_desc_lbl = get_node_or_null("%DetailDescLabel")
	if detail_stats_lbl == null: detail_stats_lbl = get_node_or_null("%DetailStatsLabel")
	if detail_value_lbl == null: detail_value_lbl = get_node_or_null("%DetailValueLabel")
	if btn_equip == null: btn_equip = get_node_or_null("%BtnEquip")
	if btn_use == null: btn_use = get_node_or_null("%BtnUse")
	if btn_unequip == null: btn_unequip = get_node_or_null("%BtnUnequip")
	if btn_sell == null: btn_sell = get_node_or_null("%BtnSell")
	if btn_cancel_selection == null: btn_cancel_selection = get_node_or_null("%BtnCancelSelection")
	if btn_deselect_all == null: btn_deselect_all = get_node_or_null("%BtnDeselectAll")
	if btn_select_all_trash == null: btn_select_all_trash = get_node_or_null("%BtnSelectAllTrash")
	if btn_sort == null: btn_sort = get_node_or_null("%BtnSort")
	if inv_capacity_lbl == null: inv_capacity_lbl = get_node_or_null("%CapacityLabel")
	if inv_grid == null: inv_grid = get_node_or_null("%InventoryGrid")
	if slot_weapon == null: slot_weapon = get_node_or_null("%SlotWeapon")
	if slot_armor == null: slot_armor = get_node_or_null("%SlotArmor")
	if slot_helmet == null: slot_helmet = get_node_or_null("%SlotHelmet")
	if slot_accessory == null: slot_accessory = get_node_or_null("%SlotAccessory")

@onready var main_layout: BoxContainer = %MainLayout if has_node("%MainLayout") else null
@onready var eq_panel: PanelContainer = %EquipmentPanel if has_node("%EquipmentPanel") else null
@onready var eq_title: Label = %Title if has_node("%Title") else null
@onready var slots_box: BoxContainer = %SlotsBox if has_node("%SlotsBox") else null
@onready var slot_weapon_box: BoxContainer = %SlotWeaponBox if has_node("%SlotWeaponBox") else null
@onready var slot_armor_box: BoxContainer = %SlotArmorBox if has_node("%SlotArmorBox") else null
@onready var slot_helmet_box: BoxContainer = %SlotHelmetBox if has_node("%SlotHelmetBox") else null
@onready var slot_accessory_box: BoxContainer = %SlotAccessoryBox if has_node("%SlotAccessoryBox") else null

var _is_portrait_layout: bool = false

func _apply_orientation_layout(is_portrait: bool):
	if is_portrait == _is_portrait_layout:
		return
	_is_portrait_layout = is_portrait

	if main_layout == null or inv_grid == null:
		return

	if is_portrait:
		main_layout.vertical = true
		if slots_box:
			slots_box.vertical = false
			slots_box.alignment = BoxContainer.ALIGNMENT_CENTER
		var eq_boxes = [slot_weapon_box, slot_armor_box, slot_helmet_box, slot_accessory_box]
		for b in eq_boxes:
			if b:
				b.vertical = true
				b.alignment = BoxContainer.ALIGNMENT_CENTER
				var lbl = b.get_node_or_null("Label")
				if lbl:
					lbl.custom_minimum_size = Vector2(0, 0)
					lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		if eq_panel:
			eq_panel.custom_minimum_size = Vector2(0, 0)
		if eq_title:
			eq_title.visible = false
		inv_grid.columns = 5
		if details_panel:
			details_panel.custom_minimum_size = Vector2(0, 160)
		if detail_icon:
			detail_icon.custom_minimum_size = Vector2(64, 64)
	else:
		main_layout.vertical = false
		if slots_box:
			slots_box.vertical = true
			slots_box.alignment = BoxContainer.ALIGNMENT_BEGIN
		var eq_boxes = [slot_weapon_box, slot_armor_box, slot_helmet_box, slot_accessory_box]
		for b in eq_boxes:
			if b:
				b.vertical = false
				b.alignment = BoxContainer.ALIGNMENT_BEGIN
				var lbl = b.get_node_or_null("Label")
				if lbl:
					lbl.custom_minimum_size = Vector2(80, 0)
					lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		if eq_panel:
			eq_panel.custom_minimum_size = Vector2(220, 0)
		if eq_title:
			eq_title.visible = true
		inv_grid.columns = 10
		if details_panel:
			details_panel.custom_minimum_size = Vector2(260, 0)
		if detail_icon:
			detail_icon.custom_minimum_size = Vector2(96, 96)

func _on_view_resized():
	if not is_inside_tree(): return
	var win_size: Vector2 = get_viewport().get_visible_rect().size
	var is_portrait = win_size.y > win_size.x
	_apply_orientation_layout(is_portrait)

func _ready():
	_ensure_node_references()
	var gm = _get_game_manager()
	if gm and gm.player:
		player = gm.player
		player.stats_changed.connect(_refresh_ui)

	btn_sort.pressed.connect(_on_sort_pressed)
	btn_equip.pressed.connect(_on_equip_pressed)
	btn_use.pressed.connect(_on_use_pressed)
	btn_sell.pressed.connect(_on_sell_pressed)
	btn_unequip.pressed.connect(_on_unequip_pressed)

	btn_select_all_trash.pressed.connect(_on_select_all_trash_pressed)
	btn_deselect_all.pressed.connect(_clear_selection)
	btn_cancel_selection.pressed.connect(_clear_selection)

	_setup_eq_slot(slot_weapon, "weapon")
	_setup_eq_slot(slot_armor, "armor")
	_setup_eq_slot(slot_helmet, "helmet")
	_setup_eq_slot(slot_accessory, "accessory")

	get_tree().root.size_changed.connect(_on_view_resized)
	_on_view_resized()

	_refresh_ui()
	ForgeUIEffects.register_interactive_controls(self)

func _setup_eq_slot(slot_node: PanelContainer, slot_name: String):
	slot_node.gui_input.connect(func(event):
		if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			var eq_item = player.equipment.get(slot_name)
			if eq_item != null:
				_select_equipped_item(eq_item, slot_name)
	)

func _refresh_ui():
	_ensure_node_references()
	_on_view_resized()
	if player == null: return

	# Ekwipunek założony
	_render_eq_slot(slot_weapon, "weapon")
	_render_eq_slot(slot_armor, "armor")
	_render_eq_slot(slot_helmet, "helmet")
	_render_eq_slot(slot_accessory, "accessory")

	# Siatka plecaka
	slot_nodes.clear()
	for c in inv_grid.get_children():
		c.queue_free()

	for i in range(80):
		var slot_inst = ItemSlotScene.instantiate()
		inv_grid.add_child(slot_inst)
		slot_nodes.append(slot_inst)

		if i < player.inventory.size():
			slot_inst.setup(player.inventory[i], i)
			slot_inst.slot_clicked.connect(_on_inventory_slot_clicked)
			slot_inst.set_selected(selected_inv_indices.has(i))
		else:
			slot_inst.setup({}, i)

	inv_capacity_lbl.text = "Pojemność plecaka: %d / 80" % player.inventory.size()
	_update_slots_visual_selection()
	_update_details_view()

func _render_eq_slot(slot_node: PanelContainer, slot_name: String):
	var item = player.equipment.get(slot_name)
	var icon_rect = slot_node.get_node_or_null("MarginContainer/IconRect")
	var lvl_lbl = slot_node.get_node_or_null("LvlLabel")

	if item != null and not item.is_empty():
		var resolved = ItemsDB.resolve_item(item)
		if icon_rect and ResourceLoader.exists(resolved.get("icon", "")):
			icon_rect.texture = load(resolved["icon"])
		if lvl_lbl:
			var lvl = item.get("lvl", 0)
			lvl_lbl.text = "+%d" % lvl if lvl > 0 else ""
	else:
		if icon_rect: icon_rect.texture = null
		if lvl_lbl: lvl_lbl.text = ""

func _on_inventory_slot_clicked(item_data: Dictionary, index: int, is_ctrl: bool = false):
	if item_data.is_empty():
		if not is_ctrl:
			_clear_selection()
		return

	if is_ctrl:
		# Przełącz zaznaczenie tego przedmiotu
		if selected_inv_indices.has(index):
			selected_inv_indices.erase(index)
		else:
			selected_inv_indices.append(index)
			if index < slot_nodes.size() and slot_nodes[index] != null:
				ForgeUIEffects.pulse_node(slot_nodes[index], 1.08)
	else:
		# Zwykłe kliknięcie: zaznacz tylko ten jeden przedmiot
		selected_inv_indices.clear()
		selected_inv_indices.append(index)

	selected_eq_slot = ""

	if selected_inv_indices.size() == 1:
		selected_inv_index = selected_inv_indices[0]
		selected_item_data = player.inventory[selected_inv_index] if selected_inv_index < player.inventory.size() else {}
	elif selected_inv_indices.size() > 1:
		selected_inv_index = -1
		selected_item_data = {}
	else:
		selected_inv_index = -1
		selected_item_data = {}

	_update_slots_visual_selection()
	_update_details_view()

func _select_equipped_item(item_data: Dictionary, slot_name: String):
	selected_inv_indices.clear()
	selected_item_data = item_data
	selected_inv_index = -1
	selected_eq_slot = slot_name
	_update_slots_visual_selection()
	_update_details_view()

func _clear_selection():
	selected_inv_indices.clear()
	selected_inv_index = -1
	selected_item_data = {}
	selected_eq_slot = ""
	_update_slots_visual_selection()
	_update_details_view()

func _update_slots_visual_selection():
	for i in range(slot_nodes.size()):
		var slot = slot_nodes[i]
		if is_instance_valid(slot):
			slot.set_selected(selected_inv_indices.has(i))

	if btn_deselect_all:
		btn_deselect_all.visible = (selected_inv_indices.size() > 0)
	if btn_cancel_selection:
		btn_cancel_selection.visible = (selected_inv_indices.size() > 1)

func _update_details_view():
	_ensure_node_references()
	if details_panel == null: return

	if selected_inv_indices.size() > 1:
		# Tryb wielokrotnego zaznaczenia do hurtowej sprzedaży
		details_panel.visible = true
		detail_name_lbl.text = "Zaznaczone (%d szt.)" % selected_inv_indices.size()
		detail_icon.texture = null
		detail_type_lbl.text = "[HURTOWA SPRZEDAŻ]"

		var total_sell_value: int = 0
		var preview_names: Array[String] = []
		for idx in selected_inv_indices:
			if idx >= 0 and idx < player.inventory.size():
				var it = player.inventory[idx]
				var res = ItemsDB.resolve_item(it)
				var val = maxi(1, int(res.get("value", 10) * 0.5))
				total_sell_value += val
				if preview_names.size() < 4:
					preview_names.append(res.get("display_name", res.get("name", "Przedmiot")))

		var desc = "Wybrane przedmioty:\n• " + "\n• ".join(preview_names)
		if selected_inv_indices.size() > preview_names.size():
			desc += "\n...oraz %d innych" % (selected_inv_indices.size() - preview_names.size())
		desc += "\n\nPrzytrzymaj CTRL i klikaj, aby dodać lub usunąć przedmioty z zaznaczenia."
		detail_desc_lbl.text = desc
		detail_stats_lbl.text = "Wybrano łącznie %d przedmiotów do skupu." % selected_inv_indices.size()
		detail_value_lbl.text = "Cena skupu: +%d złota" % total_sell_value

		btn_equip.visible = false
		btn_use.visible = false
		btn_unequip.visible = false
		btn_sell.visible = true
		btn_sell.text = "Sprzedaj wszystko (+%d zł)" % total_sell_value
		btn_cancel_selection.visible = true
		return

	if selected_item_data.is_empty():
		details_panel.visible = false
		return

	# Tryb pojedynczego przedmiotu
	details_panel.visible = true
	var resolved = ItemsDB.resolve_item(selected_item_data)

	detail_name_lbl.text = resolved.get("display_name", resolved.get("name", "Przedmiot"))
	var icon_path = resolved.get("icon", "")
	if ResourceLoader.exists(icon_path):
		detail_icon.texture = load(icon_path)
	else:
		detail_icon.texture = null

	var item_type = resolved.get("type", "")
	detail_type_lbl.text = "[%s] Rzadkość: %s" % [item_type.to_upper(), resolved.get("rarity", "Zwykły")]
	detail_desc_lbl.text = resolved.get("description", "")
	var single_sell_val = maxi(1, int(resolved.get("value", 10) * 0.5))
	detail_value_lbl.text = "Wartość: %d zł (sprzedaż: %d zł)" % [resolved.get("value", 10), single_sell_val]

	var stats_parts: Array = []
	if resolved.has("stats"):
		for k in resolved["stats"].keys():
			stats_parts.append("%s: +%d" % [k.to_upper(), resolved["stats"][k]])
	if stats_parts.is_empty():
		detail_stats_lbl.text = "Brak statystyk bojowych."
	else:
		detail_stats_lbl.text = "Statystyki: " + ", ".join(stats_parts)

	btn_cancel_selection.visible = false

	# Widoczność przycisków akcji
	if selected_eq_slot != "":
		# Przedmiot założony
		btn_equip.visible = false
		btn_use.visible = false
		btn_sell.visible = false
		btn_unequip.visible = true
		btn_unequip.disabled = player.is_inventory_full()
	else:
		# Przedmiot w plecaku
		btn_unequip.visible = false
		btn_sell.visible = true
		btn_sell.text = "Sprzedaj (+%d zł)" % single_sell_val
		if item_type == "equipment":
			btn_equip.visible = true
			btn_use.visible = false
		elif item_type == "consumable" or resolved.get("id") == "herb_mystery":
			btn_equip.visible = false
			btn_use.visible = true
		else:
			btn_equip.visible = false
			btn_use.visible = false

func _on_equip_pressed():
	if selected_inv_index >= 0 and selected_inv_index < player.inventory.size():
		var it = player.inventory[selected_inv_index]
		if player.equip(it):
			_play_sound("play_click")
			_clear_selection()
			_refresh_ui()

func _on_use_pressed():
	if selected_inv_index >= 0 and selected_inv_index < player.inventory.size():
		if player.use_consumable(selected_inv_index):
			_play_sound("play_potion")
			_clear_selection()
			_refresh_ui()

func _on_sell_pressed():
	if selected_inv_indices.size() > 1:
		# Wielokrotna sprzedaż hurtowa
		var total_gold = 0
		for idx in selected_inv_indices:
			if idx >= 0 and idx < player.inventory.size():
				var it = player.inventory[idx]
				var res = ItemsDB.resolve_item(it)
				total_gold += maxi(1, int(res.get("value", 10) * 0.5))

		var removed_items = player.remove_multiple_from_inventory(selected_inv_indices)
		var count = removed_items.size()

		if count > 0:
			player.add_gold(total_gold, "Sprzedaż hurtowa (%d szt.)" % count)
			_play_sound("play_coin")
			_post_notification("Sprzedano hurtowo %d przedmiotów za +%d złota!" % [count, total_gold])
			ForgeUIEffects.pulse_node(btn_sell, 1.15)

		_clear_selection()
		_refresh_ui()
	elif selected_inv_index >= 0 and selected_inv_index < player.inventory.size():
		var it = player.inventory[selected_inv_index]
		var resolved = ItemsDB.resolve_item(it)
		var val = maxi(1, int(resolved.get("value", 10) * 0.5))
		player.remove_from_inventory(selected_inv_index)
		player.add_gold(val, "Sprzedaż")
		_play_sound("play_coin")
		_post_notification("Sprzedano %s za +%d złota!" % [resolved.get("display_name", "przedmiot"), val])
		_clear_selection()
		_refresh_ui()

func _on_unequip_pressed():
	if selected_eq_slot != "":
		if player.unequip(selected_eq_slot):
			_play_sound("play_click")
			_clear_selection()
			_refresh_ui()

func _on_sort_pressed():
	_play_sound("play_click")
	player.inventory.sort_custom(func(a, b):
		var res_a = ItemsDB.resolve_item(a)
		var res_b = ItemsDB.resolve_item(b)
		return res_a.get("value", 0) > res_b.get("value", 0)
	)
	_clear_selection()
	_refresh_ui()

func _on_select_all_trash_pressed():
	selected_inv_indices.clear()
	for i in range(player.inventory.size()):
		var it = player.inventory[i]
		var res = ItemsDB.resolve_item(it)
		if res.get("rarity", "") == "Zwykły" and res.get("type", "") == "equipment":
			selected_inv_indices.append(i)

	selected_eq_slot = ""
	if selected_inv_indices.size() == 1:
		selected_inv_index = selected_inv_indices[0]
		selected_item_data = player.inventory[selected_inv_index]
	else:
		selected_inv_index = -1
		selected_item_data = {}

	if selected_inv_indices.is_empty():
		_post_notification("Brak zwykłego ekwipunku w plecaku.")
	else:
		_play_sound("play_click")

	_update_slots_visual_selection()
	_update_details_view()
