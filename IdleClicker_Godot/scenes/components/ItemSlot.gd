extends PanelContainer

signal slot_clicked(item_data: Dictionary, slot_index: int, is_ctrl: bool)

@onready var icon_rect: TextureRect = $MarginContainer/IconRect
@onready var lvl_label: Label = $LvlLabel
@onready var count_label: Label = $CountLabel
@onready var selection_overlay: Panel = %SelectionOverlay

var current_item: Dictionary = {}
var slot_index: int = -1
var is_selected: bool = false

func setup(item_data: Dictionary, index: int = -1, item_count: int = 1):
	current_item = item_data
	slot_index = index

	if icon_rect == null:
		icon_rect = get_node_or_null("MarginContainer/IconRect")
	if lvl_label == null:
		lvl_label = get_node_or_null("LvlLabel")
	if count_label == null:
		count_label = get_node_or_null("CountLabel")
	if selection_overlay == null:
		selection_overlay = get_node_or_null("%SelectionOverlay")

	if item_data.is_empty():
		if icon_rect: icon_rect.texture = null
		if lvl_label: lvl_label.text = ""
		if count_label: count_label.text = ""
		if selection_overlay: selection_overlay.visible = false
		is_selected = false
		modulate = Color(0.6, 0.6, 0.6, 0.5)
		return

	modulate = Color.WHITE
	var resolved = ItemsDB.resolve_item(item_data)
	var icon_path = resolved.get("icon", "")
	if ResourceLoader.exists(icon_path):
		icon_rect.texture = load(icon_path)
	else:
		icon_rect.texture = null

	var lvl = item_data.get("lvl", 0)
	if lvl > 0:
		lvl_label.text = "+%d" % lvl
	else:
		lvl_label.text = ""

	if item_count > 1:
		count_label.text = "x%d" % item_count
	else:
		count_label.text = ""

	# Kolorowanie ramki wg rzadkości
	var rarity = resolved.get("rarity", "Zwykły")
	match rarity:
		"Rzadki":
			self_modulate = Color("#3498db")
		"Legendarny":
			self_modulate = Color("#f39c12")
		"Mityczny":
			self_modulate = Color("#9b59b6")
		_:
			self_modulate = Color("#7f8c8d")

	set_selected(is_selected)

func set_selected(val: bool):
	is_selected = val
	if selection_overlay == null:
		selection_overlay = get_node_or_null("%SelectionOverlay")
	if selection_overlay:
		selection_overlay.visible = val

func _gui_input(event: InputEvent):
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		var is_ctrl = event.is_command_or_control_pressed() or Input.is_key_pressed(KEY_CTRL)
		slot_clicked.emit(current_item, slot_index, is_ctrl)
