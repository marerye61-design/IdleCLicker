extends Control

const ForgeUIEffects = preload("res://scripts/ui/ForgeUIEffects.gd")

@onready var garden_plots_box: VBoxContainer = %GardenPlotsBox
@onready var recipes_box: VBoxContainer = %RecipesBox

# Mobilne zakładki i panele
@onready var main_layout: HBoxContainer = %MainLayout if has_node("%MainLayout") else null
@onready var mobile_tab_bar: HBoxContainer = %MobileTabBar if has_node("%MobileTabBar") else null
@onready var btn_tab_garden: Button = %BtnTabGarden if has_node("%BtnTabGarden") else null
@onready var btn_tab_brewing: Button = %BtnTabBrewing if has_node("%BtnTabBrewing") else null
@onready var garden_panel: PanelContainer = %GardenPanel if has_node("%GardenPanel") else null
@onready var brewing_panel: PanelContainer = %BrewingPanel if has_node("%BrewingPanel") else null

var player: Player
var _current_mobile_tab: int = 0
var _is_portrait_layout: bool = false

func _apply_orientation_layout(is_portrait: bool):
	_is_portrait_layout = is_portrait
	if mobile_tab_bar == null or garden_panel == null or brewing_panel == null:
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
		garden_panel.visible = true
		brewing_panel.visible = true

func _select_mobile_tab(tab_idx: int):
	_current_mobile_tab = tab_idx
	if not _is_portrait_layout:
		if garden_panel: garden_panel.visible = true
		if brewing_panel: brewing_panel.visible = true
		return

	if tab_idx == 0:
		if garden_panel: garden_panel.visible = true
		if brewing_panel: brewing_panel.visible = false
		if btn_tab_garden: btn_tab_garden.modulate = Color(1.2, 0.9, 0.3)
		if btn_tab_brewing: btn_tab_brewing.modulate = Color.WHITE
	else:
		if garden_panel: garden_panel.visible = false
		if brewing_panel: brewing_panel.visible = true
		if btn_tab_garden: btn_tab_garden.modulate = Color.WHITE
		if btn_tab_brewing: btn_tab_brewing.modulate = Color(1.2, 0.9, 0.3)

func _on_view_resized():
	if not is_inside_tree(): return
	var win_size: Vector2 = get_viewport().get_visible_rect().size
	var is_portrait = win_size.y > win_size.x
	_apply_orientation_layout(is_portrait)

func _ready():
	player = GameManager.player
	player.stats_changed.connect(_refresh_ui)
	GameManager.second_ticked.connect(_on_second_tick)

	if btn_tab_garden:
		btn_tab_garden.pressed.connect(func(): _select_mobile_tab(0))
		ForgeUIEffects.apply_button_effect(btn_tab_garden, 1.05, Color(1.15, 0.9, 0.4))
	if btn_tab_brewing:
		btn_tab_brewing.pressed.connect(func(): _select_mobile_tab(1))
		ForgeUIEffects.apply_button_effect(btn_tab_brewing, 1.05, Color(1.15, 0.9, 0.4))

	get_tree().root.size_changed.connect(_on_view_resized)
	_on_view_resized()

	_refresh_ui()
	ForgeUIEffects.register_interactive_controls(self)

func _on_second_tick():
	_render_garden()

func _refresh_ui():
	_on_view_resized()
	_render_garden()
	_render_recipes()

func _render_garden():
	for c in garden_plots_box.get_children():
		c.queue_free()

	for i in range(player.herb_garden.size()):
		var plot = player.herb_garden[i]
		var card = PanelContainer.new()
		var h = HBoxContainer.new()
		card.add_child(h)

		var herb_def = AlchemyDB.HERBS.get(plot["type"], {})
		var herb_name = herb_def.get("name", "Nieznane Zioło")
		var is_unlocked = plot.get("unlocked", false)

		var info_box = VBoxContainer.new()
		info_box.size_flags_horizontal = SIZE_EXPAND_FILL
		h.add_child(info_box)

		var title = Label.new()
		title.text = "Grządka #%d: %s" % [i + 1, herb_name if is_unlocked else "Zablokowana"]
		title.add_theme_color_override("font_color", herb_def.get("color", Color.WHITE) if is_unlocked else Color.GRAY)
		info_box.add_child(title)

		if is_unlocked:
			var elapsed = Time.get_unix_time_from_system() - plot.get("planted_at", 0.0)
			var total_time = float(plot.get("growth_time", 30))
			var pbar = ProgressBar.new()
			pbar.max_value = total_time
			pbar.value = minf(total_time, elapsed)
			pbar.custom_minimum_size = Vector2(0, 16)
			pbar.show_percentage = false
			info_box.add_child(pbar)

			var rem = int(maxf(0.0, total_time - elapsed))
			var btn_harvest = Button.new()
			btn_harvest.custom_minimum_size = Vector2(130, 36)
			if rem <= 0:
				btn_harvest.text = "Zbierz!"
				btn_harvest.pressed.connect(func(): _harvest_plot(i))
			else:
				btn_harvest.text = "Rośnie (%ds)" % rem
				btn_harvest.disabled = true
			h.add_child(btn_harvest)
		else:
			var lock_lbl = Label.new()
			if i == 0:
				lock_lbl.text = "Wymaga wydzierżawienia ziemi u Karczmarza Barnaby w Tawernie (150 złota)."
				lock_lbl.add_theme_color_override("font_color", Color(0.95, 0.8, 0.4))
			else:
				lock_lbl.text = "Wymaga zwerbowania towarzysza z zadania fabularnego."
				lock_lbl.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7))
			lock_lbl.add_theme_font_size_override("font_size", 12)
			info_box.add_child(lock_lbl)

		garden_plots_box.add_child(card)

func _harvest_plot(plot_idx: int):
	var res = player.harvest_garden_plot(plot_idx)
	if res != null:
		SoundManager.play_potion()
		_refresh_ui()

func _render_recipes():
	for c in recipes_box.get_children():
		c.queue_free()

	for r_id in AlchemyDB.RECIPES.keys():
		var r = AlchemyDB.RECIPES[r_id]
		var card = PanelContainer.new()
		var h = HBoxContainer.new()
		card.add_child(h)

		var info = VBoxContainer.new()
		info.size_flags_horizontal = SIZE_EXPAND_FILL
		h.add_child(info)

		var name_lbl = Label.new()
		name_lbl.text = r["name"]
		name_lbl.add_theme_color_override("font_color", r.get("color", Color.WHITE))
		name_lbl.add_theme_font_size_override("font_size", 14)
		info.add_child(name_lbl)

		var desc_lbl = Label.new()
		desc_lbl.text = r["description"]
		desc_lbl.add_theme_font_size_override("font_size", 12)
		info.add_child(desc_lbl)

		# Składniki
		var reqs: Dictionary = r.get("ingredients", {})
		var req_strs: Array = []
		var can_brew = true
		for item_id in reqs.keys():
			var needed = reqs[item_id]
			var owned = _count_inventory_item(item_id)
			var item_def = ItemsDB.get_raw_def(item_id)
			var item_name = item_def.get("name", item_id)
			req_strs.append("%s: %d/%d" % [item_name, owned, needed])
			if owned < needed:
				can_brew = false

		var ing_lbl = Label.new()
		ing_lbl.text = "Wymagane: " + ", ".join(req_strs)
		ing_lbl.add_theme_font_size_override("font_size", 11)
		ing_lbl.add_theme_color_override("font_color", Color("#2ecc71") if can_brew else Color("#e74c3c"))
		info.add_child(ing_lbl)

		var btn_brew = Button.new()
		btn_brew.custom_minimum_size = Vector2(120, 40)
		btn_brew.text = "Uwarz"
		btn_brew.disabled = not can_brew
		btn_brew.pressed.connect(func(): _brew_recipe(r_id))
		h.add_child(btn_brew)

		recipes_box.add_child(card)

func _count_inventory_item(item_id: String) -> int:
	var c = 0
	for it in player.inventory:
		if it.get("id") == item_id:
			c += 1
	return c

func _brew_recipe(r_id: String):
	var r = AlchemyDB.RECIPES.get(r_id, {})
	if r.is_empty(): return

	var reqs = r.get("ingredients", {})
	# Usuwamy składniki
	for item_id in reqs.keys():
		var count_to_remove = reqs[item_id]
		var removed = 0
		var i = player.inventory.size() - 1
		while i >= 0 and removed < count_to_remove:
			if player.inventory[i].get("id") == item_id:
				player.remove_from_inventory(i)
				removed += 1
			i -= 1

	if r.has("is_item_reward"):
		player.add_to_inventory(r["is_item_reward"])
	else:
		player.active_buffs[r_id] = r.get("duration_fights", 10)

	player.record_achievement_stat("potions_brewed", 1, "add")
	if r_id == "elixir_psychedelic":
		player.record_achievement_stat("psychedelic_brewed", 1, "add")

	SoundManager.play_potion()
	player.stats_changed.emit()
	_refresh_ui()
