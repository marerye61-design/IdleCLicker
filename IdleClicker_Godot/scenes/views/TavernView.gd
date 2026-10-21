extends Control

const NPCLoreDB = preload("res://scripts/data/NPCLoreDB.gd")
const BountiesDB = preload("res://scripts/data/BountiesDB.gd")

@onready var tab_btn_roster: Button = %TabBtnRoster
@onready var tab_btn_expeditions: Button = %TabBtnExpeditions
@onready var tab_btn_bounties: Button = %TabBtnBounties

@onready var roster_container: Control = %RosterContainer
@onready var expeditions_container: Control = %ExpeditionsContainer
@onready var bounties_container: Control = %BountiesContainer

# Sekcja Towarzyszy & NPC
@onready var comp_cards_box: HBoxContainer = %CompCardsBox
@onready var comp_detail_portrait: TextureRect = %CompDetailPortrait
@onready var comp_detail_name: Label = %CompDetailName
@onready var comp_detail_role: Label = %CompDetailRole
@onready var comp_detail_passive: Label = %CompDetailPassive
@onready var comp_detail_status: Label = %CompDetailStatus
@onready var comp_detail_dialog: RichTextLabel = %CompDetailDialog
@onready var comp_questions_box: Container = %CompQuestionsBox

@onready var btn_comp_action: Button = %BtnCompAction
@onready var btn_inn_rest: Button = %BtnInnRest
@onready var btn_inn_stash: Button = %BtnInnStash
@onready var btn_inn_lease: Button = %BtnInnLease

# Sekcja Ekspedycji
@onready var exp_list_box: VBoxContainer = %ExpListBox

# Sekcja Zleceń (Tablica)
@onready var bounty_list_box: VBoxContainer = %BountyListBox

var player: Player
var selected_comp_id: String = "innkeeper"
var current_bounties: Array = []

func _on_view_resized():
	if not is_inside_tree(): return
	var win_size: Vector2 = get_viewport().get_visible_rect().size
	var is_portrait = win_size.y > win_size.x
	if tab_btn_roster and tab_btn_expeditions and tab_btn_bounties:
		if is_portrait:
			tab_btn_roster.text = "Towarzysze"
			tab_btn_expeditions.text = "Ekspedycje"
			tab_btn_bounties.text = "Zlecenia"
		else:
			tab_btn_roster.text = "Rozmowa i Towarzysze"
			tab_btn_expeditions.text = "Ekspedycje Towarzyszy"
			tab_btn_bounties.text = "Tablica Ogłoszeń (Zlecenia)"

func _ready():
	player = GameManager.player
	player.stats_changed.connect(_refresh_ui)
	player.hp_changed.connect(_on_hp_changed)
	GameManager.second_ticked.connect(_on_second_tick)

	tab_btn_roster.pressed.connect(func(): _switch_tab("roster"))
	tab_btn_expeditions.pressed.connect(func(): _switch_tab("expeditions"))
	tab_btn_bounties.pressed.connect(func(): _switch_tab("bounties"))

	btn_comp_action.pressed.connect(_on_comp_action_pressed)
	btn_inn_rest.pressed.connect(_on_inn_rest_pressed)
	btn_inn_stash.pressed.connect(_on_inn_stash_pressed)
	btn_inn_lease.pressed.connect(_on_inn_lease_pressed)

	get_tree().root.size_changed.connect(_on_view_resized)
	_on_view_resized()

	current_bounties = BountiesDB.generate_daily_bounties(player.level)

	_setup_companion_cards()
	_switch_tab("roster")
	_refresh_ui()

func _switch_tab(tab_name: String):
	roster_container.visible = (tab_name == "roster")
	expeditions_container.visible = (tab_name == "expeditions")
	bounties_container.visible = (tab_name == "bounties")

	tab_btn_roster.modulate = Color.YELLOW if tab_name == "roster" else Color.WHITE
	tab_btn_expeditions.modulate = Color.YELLOW if tab_name == "expeditions" else Color.WHITE
	tab_btn_bounties.modulate = Color.YELLOW if tab_name == "bounties" else Color.WHITE

func _on_second_tick():
	if expeditions_container.visible:
		_render_expeditions()

func _setup_companion_cards():
	for c in comp_cards_box.get_children():
		c.queue_free()

	for comp_id in NPCLoreDB.NPCS.keys():
		var data = NPCLoreDB.NPCS[comp_id]
		var card = Button.new()
		card.custom_minimum_size = Vector2(125, 110)
		card.clip_contents = true

		var req_lvl = int(data.get("unlock_level", 1))
		var is_locked = (player.level < req_lvl)
		var is_in_party = player.party.has(comp_id)

		var badge = ""
		if comp_id == "innkeeper":
			badge = "[Gospodarz]"
		elif is_in_party:
			badge = "[W drużynie]"
		else:
			badge = "[Poz. %d]" % req_lvl

		var vbox = VBoxContainer.new()
		vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		vbox.alignment = BoxContainer.ALIGNMENT_CENTER
		vbox.add_theme_constant_override("separation", 2)
		vbox.mouse_filter = Control.MOUSE_FILTER_IGNORE

		var icon_rect = TextureRect.new()
		icon_rect.custom_minimum_size = Vector2(50, 50)
		icon_rect.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		icon_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		icon_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE

		var icon_path = data.get("img", "")
		if ResourceLoader.exists(icon_path):
			icon_rect.texture = load(icon_path)
		vbox.add_child(icon_rect)

		var name_lbl = Label.new()
		name_lbl.text = data["name"].split(",")[0]
		name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_lbl.add_theme_font_size_override("font_size", 11)
		name_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		vbox.add_child(name_lbl)

		var badge_lbl = Label.new()
		badge_lbl.text = badge
		badge_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		badge_lbl.add_theme_font_size_override("font_size", 10)
		badge_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		if is_in_party:
			badge_lbl.modulate = Color(0.3, 0.9, 0.4)
		elif comp_id == "innkeeper":
			badge_lbl.modulate = Color(0.95, 0.85, 0.4)
		elif is_locked:
			badge_lbl.modulate = Color(0.7, 0.4, 0.4)
		else:
			badge_lbl.modulate = Color(0.4, 0.8, 1.0)
		vbox.add_child(badge_lbl)

		card.add_child(vbox)

		if comp_id == selected_comp_id:
			card.modulate = Color(1.2, 1.2, 0.8)
		elif is_locked and comp_id != "innkeeper":
			card.modulate = Color(0.65, 0.65, 0.65, 0.85)
		else:
			card.modulate = Color.WHITE

		card.pressed.connect(_on_companion_card_clicked.bind(comp_id))
		comp_cards_box.add_child(card)

func _on_companion_card_clicked(comp_id: String):
	selected_comp_id = comp_id
	_update_companion_detail()

func _refresh_ui():
	if player.hp <= 0:
		player.hp = maxi(1, int(player.get_max_hp() * 0.10))
		player.hp_changed.emit(player.hp, player.get_max_hp())

	_setup_companion_cards()
	_update_companion_detail()
	_render_expeditions()
	_render_bounties()

func _on_hp_changed(cur_hp: int, max_hp: int):
	if selected_comp_id == "innkeeper":
		btn_inn_rest.disabled = (player.gold < 20 or (cur_hp >= max_hp and player.mana >= player.max_mana))
		if cur_hp < max_hp:
			var regen_val = maxi(5, int(max_hp * 0.08))
			comp_detail_status.text = "Status: Regenerujesz zdrowie przy kominku (+%d HP/s)" % regen_val
		else:
			comp_detail_status.text = "Status: Za ladą gospody"

func _update_companion_detail():
	var data = NPCLoreDB.NPCS.get(selected_comp_id, {})
	if data.is_empty(): return

	comp_detail_name.text = data["name"]
	comp_detail_role.text = data["role"]

	var icon_path = data.get("img", "")
	if ResourceLoader.exists(icon_path):
		comp_detail_portrait.texture = load(icon_path)
	else:
		comp_detail_portrait.texture = null

	if data.has("passive_name"):
		comp_detail_passive.visible = true
		comp_detail_passive.text = "Zdolność Bojowa: %s - %s" % [data["passive_name"], data.get("passive_desc", "")]
	else:
		comp_detail_passive.visible = true
		comp_detail_passive.text = "Gospodarz gospody 'Pod Skrzydłem Upadłego Anioła'. Zawsze chętnie posłuży radą, strawą i bezpiecznym schronieniem."

	# Odświeżenie pytań dialogowych
	for child in comp_questions_box.get_children():
		child.queue_free()

	var options = data.get("options", {})
	for opt_text in options.keys():
		var btn = Button.new()
		btn.text = opt_text
		btn.custom_minimum_size = Vector2(0, 32)
		btn.pressed.connect(_on_dialogue_option_selected.bind(opt_text, options[opt_text]))
		comp_questions_box.add_child(btn)

	# Dialog powitalny
	if selected_comp_id == "innkeeper" and player.hp < player.get_max_hp():
		comp_detail_dialog.text = "[b]Karczmarz Barnaba:[/b] Na wszystkie bóstwa, ledwo uszedłeś z życiem! Ściągnąłem cię ze szlaku i położyłem przy kominku. Odpocznij chwilę w cieple gospody, by w spokoju zregenerować siły, lub wynajmij pokój za 20 złota, aby natychmiast stanąć na nogi!"
	else:
		comp_detail_dialog.text = "[b]%s:[/b] %s" % [data["name"], data.get("greeting", "Witaj.")]

	# Przyciski akcji
	if selected_comp_id == "innkeeper":
		btn_comp_action.visible = false
		btn_inn_rest.visible = true
		btn_inn_rest.disabled = (player.gold < 20 or (player.hp >= player.get_max_hp() and player.mana >= player.max_mana))

		var stash_cnt = player.inventory_stash.size()
		if stash_cnt > 0:
			btn_inn_stash.visible = true
			btn_inn_stash.text = "Odbierz nagrody z depozytu (%d szt.)" % stash_cnt
			btn_inn_stash.disabled = player.is_inventory_full()
		else:
			btn_inn_stash.visible = false

		# Dzierżawa ziemi
		var plot0_unlocked = player.herb_garden.size() > 0 and player.herb_garden[0].get("unlocked", false)
		btn_inn_lease.visible = true
		if not plot0_unlocked:
			btn_inn_lease.text = "[DZIERŻAWA] Wydzierżaw grządkę na zioła (150 złota)"
			btn_inn_lease.disabled = player.gold < 150
		else:
			btn_inn_lease.text = "[OGRÓD ZIÓŁ] Grządka #1 wydzierżawiona (Aktywna)"
			btn_inn_lease.disabled = true

		if player.hp < player.get_max_hp():
			var regen_val = maxi(5, int(player.get_max_hp() * 0.08))
			comp_detail_status.text = "Status: Regenerujesz zdrowie przy kominku (+%d HP/s)" % regen_val
		else:
			comp_detail_status.text = "Status: Za ladą gospody"
		return

	# Dla towarzyszy:
	btn_inn_rest.visible = false
	btn_inn_stash.visible = false
	btn_inn_lease.visible = false
	btn_comp_action.visible = true

	var is_in_party = player.party.has(selected_comp_id)
	var is_active = (player.active_companion == selected_comp_id)

	var quest_info: Dictionary = {}
	var q_id = data.get("quest_id", "")
	for q in player.quests:
		if q["id"] == q_id:
			quest_info = q
			break

	if is_in_party:
		comp_detail_status.text = "Status: W drużynie (Aktywny w walce)" if is_active else "Status: W drużynie (Gotowy do akcji)"
		if is_active:
			btn_comp_action.text = "Aktywny w walce"
			btn_comp_action.disabled = true
		else:
			btn_comp_action.text = "Wybierz jako aktywnego w walce"
			btn_comp_action.disabled = false
	else:
		if quest_info.is_empty():
			comp_detail_status.text = "Brak informacji o rekrutacji."
			btn_comp_action.visible = false
			return

		var q_status = quest_info.get("status", "LOCKED")
		if player.level < quest_info.get("unlock_level", 1):
			comp_detail_status.text = "Wymaga %d poziomu bohatera" % quest_info["unlock_level"]
			btn_comp_action.visible = false
		elif q_status == "AVAILABLE":
			comp_detail_status.text = "Zadanie rekrutacyjne gotowe do przyjęcia!"
			btn_comp_action.text = "Przyjmij Zadanie Rekrutacji"
			btn_comp_action.disabled = false
		elif q_status == "IN_PROGRESS":
			comp_detail_status.text = "Zadanie w trakcie realizacji..."
			var prog_str = _get_quest_progress_text(quest_info)
			comp_detail_dialog.text += "\n\n[b]Postęp Zlecenia:[/b]\n%s" % prog_str
			btn_comp_action.visible = false
		elif q_status == "COMPLETED":
			comp_detail_status.text = "Zadanie ukończone! Odbierz nagrodę i zwerbuj."
			btn_comp_action.text = "Zwerbuj Towarzysza do Drużyny!"
			btn_comp_action.disabled = false

func _on_dialogue_option_selected(question: String, response: String):
	var data = NPCLoreDB.NPCS.get(selected_comp_id, {})
	var npc_name = data.get("name", "NPC")
	comp_detail_dialog.text = "[b]%s:[/b] %s\n\n[color=#f4d03f][b]%s:[/b] %s[/color]" % [player.name, question, npc_name, response]

func _on_inn_rest_pressed():
	if player.rest_at_inn(20):
		GameManager.post_notification("Odpocząłeś w gospodzie. Zdrowie i Mana w pełni odnowione!")
		_refresh_ui()
	else:
		GameManager.post_notification("Brak wystarczającej ilości złota (koszt: 20 złota).")

func _on_inn_stash_pressed():
	var transferred = 0
	while not player.is_inventory_full() and not player.inventory_stash.is_empty():
		player.claim_stash_item(0)
		transferred += 1

	if transferred > 0:
		GameManager.post_notification("Odebrano %d przedmiotów z depozytu Barnaby!" % transferred)
		_refresh_ui()
	else:
		GameManager.post_notification("Twój ekwipunek jest pełny! Zwolnij miejsce w plecaku.")

func _on_inn_lease_pressed():
	if player.lease_herb_plot(150):
		comp_detail_dialog.text = "[b]Karczmarz Barnaba:[/b] Wspaniale! Ten kawałek pola przed gospodą jest teraz twój. Gleba jest tam żyzna, idealna pod Amanitę Lasu. Zadbaj o nią, a odpłaci ci się obfitymi plonami!"
		GameManager.post_notification("Wydzierżawiono Grządkę #1 u Karczmarza Barnaby za 150 złota! Ogród ziół został otwarty.")
		_refresh_ui()
	else:
		comp_detail_dialog.text = "[b]Karczmarz Barnaba:[/b] Przykro mi, wędrowcze, ale brakuje ci złota! Dzierżawa ziemi i przygotowanie grządki pod uprawę to koszt 150 sztuk złota. Wróć, gdy uzbierasz odpowiednią sumę."
		GameManager.post_notification("Brak złota na dzierżawę grządki (koszt: 150 złota).")

func _on_comp_action_pressed():
	var data = NPCLoreDB.NPCS.get(selected_comp_id, {})
	if data.is_empty(): return

	var is_in_party = player.party.has(selected_comp_id)
	if is_in_party:
		player.active_companion = selected_comp_id
		GameManager.post_notification("%s walczy teraz u twojego boku!" % data["name"])
		_refresh_ui()
		return

	# Zadanie rekrutacyjne
	var q_id = data.get("quest_id", "")
	for q in player.quests:
		if q["id"] == q_id:
			if q["status"] == "AVAILABLE":
				q["status"] = "IN_PROGRESS"
				GameManager.post_notification("Przyjęto zadanie rekrutacji: %s!" % q["name"])
				_refresh_ui()
			elif q["status"] == "COMPLETED":
				_claim_quest_and_recruit(q, data)
			break

func _claim_quest_and_recruit(quest: Dictionary, data: Dictionary):
	quest["status"] = "CLAIMED"
	var rewards = quest.get("rewards", {})

	if rewards.has("gold"):
		player.gold += rewards["gold"]
	if rewards.has("item"):
		player.add_to_inventory(rewards["item"], true)
	if rewards.has("garden_plot"):
		var p_idx = rewards["garden_plot"]
		if p_idx < player.herb_garden.size():
			player.herb_garden[p_idx]["unlocked"] = true
	if rewards.has("party"):
		player.add_companion_to_party(rewards["party"])

	GameManager.post_notification("Towarzysz %s dołączył do twojej drużyny!" % data["name"])
	_refresh_ui()

func _get_quest_progress_text(q: Dictionary) -> String:
	var reqs = q.get("requirements", {}).get("kills", {})
	var lines = []
	for mob in reqs.keys():
		var needed = reqs[mob]
		var cur = q.get("progress", {}).get(mob, 0)
		lines.append("- %s: %d / %d" % [mob, cur, needed])
	return "\n".join(lines)

# === EKSPEDYCJE TOWARZYSZY ===
func _render_expeditions():
	for c in exp_list_box.get_children():
		c.queue_free()

	var available_companions = []
	for cid in player.party:
		if cid != player.active_companion and not player.expeditions.has(cid):
			available_companions.append(cid)

	# Aktywne ekspedycje
	for cid in player.expeditions.keys():
		var exp_data = player.expeditions[cid]
		var c_name = NPCLoreDB.NPCS.get(cid, {}).get("name", cid)
		var exp_type_name = BountiesDB.EXPEDITIONS_DATA.get(exp_data["type"], {}).get("name", "Misja")

		var now = Time.get_unix_time_from_system()
		var elapsed = now - exp_data["start_time"]
		var dur = exp_data["duration"]
		var remaining = maxi(0, int(dur - elapsed))

		var row = PanelContainer.new()
		var hbox = HBoxContainer.new()
		hbox.add_theme_constant_override("separation", 12)

		var lbl = Label.new()
		lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		if remaining <= 0:
			lbl.text = "%s zakończył misję: %s! Nagroda czeka na odbiór." % [c_name, exp_type_name]
			lbl.modulate = Color(0.3, 0.9, 0.4)
		else:
			lbl.text = "%s w trakcie misji: %s (Pozostało: %ds)" % [c_name, exp_type_name, remaining]

		hbox.add_child(lbl)

		var btn = Button.new()
		btn.custom_minimum_size = Vector2(160, 36)
		if remaining <= 0:
			btn.text = "Odbierz Nagrodę"
			btn.pressed.connect(_claim_expedition.bind(cid))
		else:
			btn.text = "W trakcie..."
			btn.disabled = true

		hbox.add_child(btn)
		row.add_child(hbox)
		exp_list_box.add_child(row)

	# Nowe zlecenia ekspedycji dla wolnych towarzyszy
	if available_companions.is_empty():
		if player.party.is_empty():
			var empty_lbl = Label.new()
			empty_lbl.text = "Nie posiadasz jeszcze żadnych towarzyszy w drużynie. Zrekrutuj ich w zakładce 'Rozmowa i Towarzysze'!"
			exp_list_box.add_child(empty_lbl)
		elif player.expeditions.size() == player.party.size() - (1 if player.active_companion else 0):
			var busy_lbl = Label.new()
			busy_lbl.text = "Wszyscy dostępni towarzysze są obecnie na ekspedycjach lub walczą u twego boku."
			exp_list_box.add_child(busy_lbl)
		return

	for exp_type in BountiesDB.EXPEDITIONS_DATA.keys():
		var ed = BountiesDB.EXPEDITIONS_DATA[exp_type]
		var card = PanelContainer.new()
		var hbox = HBoxContainer.new()
		hbox.add_theme_constant_override("separation", 12)

		var info_box = VBoxContainer.new()
		info_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL

		var title_lbl = Label.new()
		title_lbl.text = "%s (Czas trwania: %ds)" % [ed["name"], ed["duration"]]
		title_lbl.modulate = Color(0.95, 0.85, 0.4)
		info_box.add_child(title_lbl)

		var desc_lbl = Label.new()
		desc_lbl.text = ed["desc"]
		desc_lbl.add_theme_font_size_override("font_size", 12)
		info_box.add_child(desc_lbl)
		hbox.add_child(info_box)

		# Wybór wolnego towarzysza
		for cid in available_companions:
			var send_btn = Button.new()
			var c_name = NPCLoreDB.NPCS.get(cid, {}).get("name", cid)
			send_btn.text = "Wyślij %s" % c_name
			send_btn.custom_minimum_size = Vector2(130, 36)
			send_btn.pressed.connect(_start_expedition.bind(cid, exp_type))
			hbox.add_child(send_btn)

		card.add_child(hbox)
		exp_list_box.add_child(card)

func _start_expedition(comp_id: String, exp_type: String):
	var ed = BountiesDB.EXPEDITIONS_DATA.get(exp_type, {})
	player.expeditions[comp_id] = {
		"type": exp_type,
		"start_time": Time.get_unix_time_from_system(),
		"duration": ed.get("duration", 60)
	}
	GameManager.post_notification("Wysłano %s na ekspedycję: %s!" % [NPCLoreDB.NPCS.get(comp_id, {}).get("name", comp_id), ed.get("name", "")])
	_refresh_ui()

func _claim_expedition(comp_id: String):
	var exp_data = player.expeditions.get(comp_id, {})
	if exp_data.is_empty(): return

	var exp_type = exp_data["type"]
	var ed = BountiesDB.EXPEDITIONS_DATA.get(exp_type, {})

	# Nagrody
	var r_gold = randi_range(ed["min_gold"], ed["max_gold"])
	player.gold += r_gold

	var items_received = []
	for p_item in ed.get("possible_items", []):
		if randf() <= 0.65 and not player.is_inventory_full():
			player.add_to_inventory(p_item, true)
			items_received.append(ItemsDB.get_item_name(p_item))

	player.expeditions.erase(comp_id)

	var msg = "%s powrócił z ekspedycji! Zdobyto: +%d złota" % [NPCLoreDB.NPCS.get(comp_id, {}).get("name", comp_id), r_gold]
	if not items_received.is_empty():
		msg += ", przedmioty: %s" % ", ".join(items_received)
	GameManager.post_notification(msg)
	_refresh_ui()

# === TABLICA OGŁOSZEŃ (BOUNTIES) ===
func _render_bounties():
	for c in bounty_list_box.get_children():
		c.queue_free()

	for bounty in current_bounties:
		var row = PanelContainer.new()
		var hbox = HBoxContainer.new()
		hbox.add_theme_constant_override("separation", 12)

		var vbox = VBoxContainer.new()
		vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL

		var target_name = bounty.get("target_name", "Potwór")
		var desc = bounty.get("description", bounty.get("desc", ""))
		var target_count = int(bounty.get("target_count", bounty.get("count_required", 5)))
		var gold_reward = int(bounty.get("gold_reward", bounty.get("reward_gold", 100)))
		var exp_reward = int(bounty.get("exp_reward", bounty.get("reward_exp", 50)))
		var status = bounty.get("status", "AVAILABLE")

		var title = Label.new()
		title.text = "[Zlecenie] %s: %s (Wymagane: %d szt.)" % [target_name, desc, target_count]
		title.modulate = Color(0.95, 0.85, 0.4)
		vbox.add_child(title)

		var cur_kills = player.bestiary.get(target_name, 0)
		var start_kills = bounty.get("start_kills", 0)
		var progress = clampi(cur_kills - start_kills, 0, target_count)

		var prog_lbl = Label.new()
		prog_lbl.text = "Postęp: %d / %d | Nagroda: +%d złota, +%d EXP" % [progress, target_count, gold_reward, exp_reward]
		prog_lbl.add_theme_font_size_override("font_size", 12)
		vbox.add_child(prog_lbl)
		hbox.add_child(vbox)

		var btn = Button.new()
		btn.custom_minimum_size = Vector2(160, 38)
		if status == "CLAIMED" or bounty.get("claimed", false):
			btn.text = "Ukończono"
			btn.disabled = true
		elif progress >= target_count:
			btn.text = "Odbierz Nagrodę"
			btn.pressed.connect(_claim_bounty.bind(bounty))
		else:
			btn.text = "W trakcie..."
			btn.disabled = true

		hbox.add_child(btn)
		row.add_child(hbox)
		bounty_list_box.add_child(row)

func _claim_bounty(bounty: Dictionary):
	bounty["status"] = "CLAIMED"
	bounty["claimed"] = true
	var gold_reward = int(bounty.get("gold_reward", bounty.get("reward_gold", 100)))
	var exp_reward = int(bounty.get("exp_reward", bounty.get("reward_exp", 50)))
	player.gold += gold_reward
	player.add_exp(exp_reward)
	GameManager.post_notification("Ukończono zlecenie na %s! +%d złota, +%d EXP" % [bounty.get("target_name", "Potwora"), gold_reward, exp_reward])
	_refresh_ui()
