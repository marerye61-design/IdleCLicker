extends Control

const ForgeUIEffects = preload("res://scripts/ui/ForgeUIEffects.gd")

@onready var btn_new_game: Button = %BtnNewGame
@onready var btn_load_game: Button = %BtnLoadGame
@onready var btn_delete_save: Button = %BtnDeleteSave
@onready var btn_exit: Button = %BtnExit

# Dialogi / Panele nakładane (Overlays)
@onready var new_game_overlay: Control = %NewGameOverlay
@onready var new_game_name_edit: LineEdit = %NewGameNameEdit
@onready var new_game_error_lbl: Label = %NewGameErrorLbl
@onready var btn_confirm_new_game: Button = %BtnConfirmNewGame
@onready var btn_cancel_new_game: Button = %BtnCancelNewGame

@onready var load_game_overlay: Control = %LoadGameOverlay
@onready var load_save_cards_container: VBoxContainer = %LoadSaveCardsContainer
@onready var btn_cancel_load: Button = %BtnCancelLoad

@onready var delete_save_overlay: Control = %DeleteSaveOverlay
@onready var delete_save_cards_container: VBoxContainer = %DeleteSaveCardsContainer
@onready var btn_close_delete: Button = %BtnCloseDelete

@onready var confirm_delete_overlay: Control = %ConfirmDeleteOverlay
@onready var confirm_delete_label: Label = %ConfirmDeleteLabel
@onready var btn_confirm_delete_yes: Button = %BtnConfirmDeleteYes
@onready var btn_confirm_delete_no: Button = %BtnConfirmDeleteNo

var pending_delete_filename: String = ""

func _ready():
	SaveSystem.init_saves_dir()
	_hide_all_overlays()
	_refresh_menu()
	ForgeUIEffects.register_interactive_controls(self)

	btn_new_game.pressed.connect(_on_btn_new_game_pressed)
	btn_load_game.pressed.connect(_on_btn_load_game_pressed)
	btn_delete_save.pressed.connect(_on_btn_delete_save_pressed)
	btn_exit.pressed.connect(_on_btn_exit_pressed)

	btn_confirm_new_game.pressed.connect(_on_confirm_new_game)
	btn_cancel_new_game.pressed.connect(_hide_all_overlays)
	new_game_name_edit.text_submitted.connect(func(_t): _on_confirm_new_game())

	btn_cancel_load.pressed.connect(_hide_all_overlays)
	btn_close_delete.pressed.connect(_hide_all_overlays)

	btn_confirm_delete_yes.pressed.connect(_on_confirm_delete_yes)
	btn_confirm_delete_no.pressed.connect(func(): confirm_delete_overlay.visible = false)

func _hide_all_overlays():
	new_game_overlay.visible = false
	load_game_overlay.visible = false
	delete_save_overlay.visible = false
	confirm_delete_overlay.visible = false
	new_game_error_lbl.text = ""

func _refresh_menu():
	var saves = SaveSystem.get_all_saves()
	if saves.is_empty():
		btn_load_game.disabled = true
		btn_load_game.text = "Wczytaj Grę (Brak)"
		btn_delete_save.disabled = true
	else:
		btn_load_game.disabled = false
		btn_load_game.text = "Wczytaj Grę (%d)" % saves.size()
		btn_delete_save.disabled = false

func _on_btn_new_game_pressed():
	SoundManager.play_click()
	_hide_all_overlays()
	new_game_name_edit.text = ""
	new_game_error_lbl.text = ""
	new_game_overlay.visible = true
	new_game_name_edit.grab_focus()

func _on_confirm_new_game():
	var char_name = new_game_name_edit.text.strip_edges()
	if char_name.is_empty():
		new_game_error_lbl.text = "Imię bohatera nie może być puste!"
		return

	SoundManager.play_click()
	_hide_all_overlays()
	GameManager.start_new_game(char_name)

func _on_btn_load_game_pressed():
	SoundManager.play_click()
	_hide_all_overlays()
	_populate_load_saves_list()
	load_game_overlay.visible = true

func _populate_load_saves_list():
	for child in load_save_cards_container.get_children():
		child.queue_free()

	var saves = SaveSystem.get_all_saves()
	if saves.is_empty():
		var empty_lbl = Label.new()
		empty_lbl.text = "Brak dostępnych zapisów gry."
		empty_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		load_save_cards_container.add_child(empty_lbl)
		return

	for s in saves:
		var card = _create_save_card(s, false)
		load_save_cards_container.add_child(card)

func _on_btn_delete_save_pressed():
	SoundManager.play_click()
	_hide_all_overlays()
	_populate_delete_saves_list()
	delete_save_overlay.visible = true

func _populate_delete_saves_list():
	for child in delete_save_cards_container.get_children():
		child.queue_free()

	var saves = SaveSystem.get_all_saves()
	if saves.is_empty():
		var empty_lbl = Label.new()
		empty_lbl.text = "Brak zapisów do usunięcia."
		empty_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		delete_save_cards_container.add_child(empty_lbl)
		_refresh_menu()
		return

	for s in saves:
		var card = _create_save_card(s, true)
		delete_save_cards_container.add_child(card)

func _create_save_card(save_info: Dictionary, is_delete_mode: bool) -> Control:
	var panel = PanelContainer.new()
	panel.custom_minimum_size = Vector2(0, 60)

	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 12)
	margin.add_theme_constant_override("margin_right", 12)
	margin.add_theme_constant_override("margin_top", 8)
	margin.add_theme_constant_override("margin_bottom", 8)
	panel.add_child(margin)

	var hbox = HBoxContainer.new()
	hbox.add_theme_constant_override("separation", 12)
	margin.add_child(hbox)

	var vbox = VBoxContainer.new()
	vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hbox.add_child(vbox)

	var title_lbl = Label.new()
	title_lbl.text = "%s (Poz. %d)" % [save_info.get("name", "Bohater"), save_info.get("level", 1)]
	title_lbl.add_theme_color_override("font_color", Color(0.96, 0.82, 0.25, 1.0))
	title_lbl.add_theme_font_size_override("font_size", 16)
	vbox.add_child(title_lbl)

	var details_lbl = Label.new()
	details_lbl.text = "Złoto: %d | Ostatni zapis: %s" % [save_info.get("gold", 0), save_info.get("date_str", "---")]
	details_lbl.add_theme_color_override("font_color", Color(0.75, 0.72, 0.68, 1.0))
	details_lbl.add_theme_font_size_override("font_size", 12)
	vbox.add_child(details_lbl)

	var btn = Button.new()
	btn.custom_minimum_size = Vector2(110, 38)
	btn.size_flags_vertical = Control.SIZE_SHRINK_CENTER

	if not is_delete_mode:
		btn.text = "Wczytaj"
		btn.modulate = Color(0.35, 1.0, 0.45)
		btn.pressed.connect(func():
			SoundManager.play_click()
			_hide_all_overlays()
			GameManager.load_existing_save(save_info.get("filename", ""))
		)
	else:
		btn.text = "Usuń"
		btn.modulate = Color(1.0, 0.4, 0.4)
		btn.pressed.connect(func():
			SoundManager.play_click()
			pending_delete_filename = save_info.get("filename", "")
			confirm_delete_label.text = "Czy na pewno chcesz bezpowrotnie usunąć zapis bohatera\n'%s' (Poz. %d)?" % [save_info.get("name", "Bohater"), save_info.get("level", 1)]
			confirm_delete_overlay.visible = true
		)

	hbox.add_child(btn)
	ForgeUIEffects.apply_card_effect(panel)
	ForgeUIEffects.apply_button_effect(btn, 1.05)
	return panel

func _on_confirm_delete_yes():
	SoundManager.play_click()
	confirm_delete_overlay.visible = false
	if not pending_delete_filename.is_empty():
		SaveSystem.delete_save(pending_delete_filename)
		pending_delete_filename = ""
	_populate_delete_saves_list()
	_refresh_menu()

func _on_btn_exit_pressed():
	SoundManager.play_click()
	get_tree().quit()
