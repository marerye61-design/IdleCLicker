extends Control

@onready var dungeons_list_box: VBoxContainer = %DungeonsListBox
@onready var active_dungeon_panel: PanelContainer = %ActiveDungeonPanel
@onready var dungeon_title_lbl: Label = %ActiveDungeonTitle
@onready var dungeon_bg_rect: TextureRect = %ActiveDungeonBg
@onready var dungeon_progress_bar: ProgressBar = %DungeonProgressBar
@onready var dungeon_time_lbl: Label = %DungeonTimeLabel
@onready var dungeon_flavor_lbl: Label = %DungeonFlavorLabel
@onready var btn_retreat: Button = %BtnRetreat

var player: Player
var current_dungeon: Dictionary = {}
var dungeon_timer: float = 0.0
var dungeon_total_duration: float = 0.0
var is_exploring: bool = false
var flavor_tick: float = 0.0

const FLAVOR_TEXTS: Array = [
	"Drużyna ostrożnie bada wilgotne korytarze podziemi...",
	"Pianek sprawdza grubość kamiennych ścian, szukając ukrytych przejść.",
	"Maślak dzieli się zapasem lukrowanych pączków na pokrzepienie serc.",
	"Damian sprawdza stan zbroi i nasłuchuje kroków patroli wroga.",
	"Domcia wyczuwa zapach rzadkich ziół i mrocznej aury magii.",
	"Yomen majstruje przy zardzewiałej dźwigni pułapki, rozbrajając mechanizm.",
	"Eczme wypatruje wrogów na flankach, gotowy do natychmiastowego ataku!"
]

func _ready():
	player = GameManager.player
	player.stats_changed.connect(_render_list)
	btn_retreat.pressed.connect(_on_retreat_pressed)
	active_dungeon_panel.visible = false
	_render_list()

func _process(delta: float):
	if is_exploring:
		dungeon_timer += delta
		flavor_tick += delta
		if flavor_tick >= 8.0:
			flavor_tick = 0.0
			dungeon_flavor_lbl.text = FLAVOR_TEXTS[randi() % FLAVOR_TEXTS.size()]

		dungeon_progress_bar.value = dungeon_timer
		var remaining = int(maxf(0.0, dungeon_total_duration - dungeon_timer))
		dungeon_time_lbl.text = "Pozostało: %ds" % remaining

		if dungeon_timer >= dungeon_total_duration:
			_on_dungeon_completed()

func _render_list():
	for c in dungeons_list_box.get_children():
		c.queue_free()

	for d in DungeonsDB.DUNGEONS:
		var card = PanelContainer.new()
		var h = HBoxContainer.new()
		card.add_child(h)

		var info = VBoxContainer.new()
		info.size_flags_horizontal = SIZE_EXPAND_FILL
		h.add_child(info)

		var title_lbl = Label.new()
		title_lbl.text = "%s (Wymaga %d poz.)" % [d["name"], d["level_req"]]
		title_lbl.add_theme_color_override("font_color", Color("#f4d03f"))
		title_lbl.add_theme_font_size_override("font_size", 15)
		info.add_child(title_lbl)

		var desc_lbl = Label.new()
		desc_lbl.text = "Nagroda: %d EXP | %d złota (Czas: %ds)" % [d["exp_reward"], d["gold_reward"], d["duration"]]
		desc_lbl.add_theme_font_size_override("font_size", 12)
		info.add_child(desc_lbl)

		var btn_enter = Button.new()
		btn_enter.custom_minimum_size = Vector2(160, 44)
		if player.level < d["level_req"]:
			btn_enter.text = "Zablokowany"
			btn_enter.disabled = true
		else:
			btn_enter.text = "Wejdź do lochu"
			btn_enter.pressed.connect(func(): _enter_dungeon(d))
		h.add_child(btn_enter)

		dungeons_list_box.add_child(card)

func _enter_dungeon(d: Dictionary):
	current_dungeon = d
	dungeon_total_duration = float(d["duration"])
	dungeon_timer = 0.0
	flavor_tick = 0.0
	is_exploring = true

	dungeon_title_lbl.text = "Eksploracja: %s" % d["name"]
	if ResourceLoader.exists(d.get("bg_image", "")):
		dungeon_bg_rect.texture = load(d["bg_image"])
	dungeon_progress_bar.max_value = dungeon_total_duration
	dungeon_progress_bar.value = 0.0
	dungeon_flavor_lbl.text = FLAVOR_TEXTS[0]

	SoundManager.play_dungeon()
	active_dungeon_panel.visible = true

func _on_retreat_pressed():
	is_exploring = false
	active_dungeon_panel.visible = false
	GameManager.post_notification("Wycofano się z lochu bez strat.")

func _on_dungeon_completed():
	is_exploring = false
	active_dungeon_panel.visible = false

	SoundManager.play_boss()
	var exp_g = current_dungeon["exp_reward"]
	var gold_g = current_dungeon["gold_reward"]

	if player.permanent_perks.has("perk_boss_hunter"):
		exp_g = int(exp_g * 1.05)
		gold_g = int(gold_g * 1.05)

	player.add_exp(exp_g)
	player.add_gold(gold_g, "Loch")
	player.record_achievement_stat("dungeons_cleared", 1, "add")

	var boss_id = current_dungeon.get("boss_id", "")
	if boss_id == "boss_ptys":
		player.record_achievement_stat("boss_ptys_kills", 1, "add")
	elif boss_id == "boss_kollman":
		player.record_achievement_stat("boss_kollman_kills", 1, "add")

	# Szansa na drop unikalnego przedmiotu (10%)
	var drops = current_dungeon.get("drop_pool", [])
	if randf() < 0.15 and not drops.is_empty():
		var drop_item = drops[randi() % drops.size()]
		player.add_to_inventory(drop_item)
		var item_def = ItemsDB.get_raw_def(drop_item)
		GameManager.post_notification("Niesamowite! Zdobyto: %s!" % item_def.get("name", drop_item))

	SoundManager.play_quest_complete()
	GameManager.post_notification("Ukończono loch: %s! Zdobyto %d złota i %d EXP!" % [current_dungeon["name"], gold_g, exp_g])
	player.stats_changed.emit()

	# Wywołanie pojedynku z bossem lochu
	if not boss_id.is_empty():
		var main_node = get_tree().root.get_node_or_null("Main")
		if main_node and main_node.has_method("_on_boss_fight_requested"):
			main_node._on_boss_fight_requested(boss_id)
