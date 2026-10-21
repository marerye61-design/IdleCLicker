extends Control

signal finished

@onready var narrative_container: VBoxContainer = %NarrativeContainer
@onready var narrative_label: Label = %NarrativeLabel
@onready var prompt_type_label: Label = %PromptTypeLabel

@onready var reveal_container: VBoxContainer = %RevealContainer
@onready var boss_portrait: TextureRect = %BossPortrait
@onready var boss_quote_label: Label = %BossQuoteLabel
@onready var prompt_fight_label: Label = %PromptFightLabel

var full_narrative: String = ""
var boss_quote: String = ""
var quote_color: Color = Color.WHITE
var current_char_idx: int = 0
var typing_speed: float = 0.03
var typing_timer: float = 0.0

enum State { TYPING, TYPING_DONE, REVEALED }
var current_state: State = State.TYPING

const BOSS_DATA: Dictionary = {
	"boss_ptys": {
		"narrative": "Zanurzasz się w gęsty, mroczny las...\nWśród starych dębów dostrzegasz opuszczony fort.\nW jego ruinach, na tronie z czaszek, czeka na Ciebie potężny kształt...",
		"quote": "\"Czekałem na Ciebie, słabeuszu. Podejdź no tu...\"",
		"quote_color": Color("#e74c3c"),
		"portrait": "res://assets/boss_ptys.jpg"
	},
	"boss_kollman": {
		"narrative": "Wspinasz się po stromych turniach Górskiej Przełęczy...\nWichura świszczy między iglicami, a w powietrzu czuć zapach ozonu i rozgrzanej skóry rękawic.\nNa wąskiej skalnej półce czeka wojowniczy mag, zaciskając bandaże na dłoniach...",
		"quote": "\"Trzymaj szczelną gardę, bo zaraz dostaniesz lewy prosty z pioruna i sprowadzenie do parteru! Zatańczymy w oktagonie, leszczu!\"",
		"quote_color": Color("#f1c40f"),
		"portrait": "res://assets/boss_kollman.jpg"
	}
}

func setup_boss(boss_id: String, boss_name: String = ""):
	var info = BOSS_DATA.get(boss_id, {
		"narrative": "Przemierzasz niezbadane ostępy podziemi...\nW powietrzu unosi się złowrogi chłód.\nNagle z mroku wyłania się potężny przeciwnik: %s!" % (boss_name if not boss_name.is_empty() else "Władca Podziemi"),
		"quote": "\"Twoja wędrówka dobiegła końca!\"",
		"quote_color": Color("#e74c3c"),
		"portrait": "res://assets/boss_ptys.jpg" if boss_id == "boss_ptys" else "res://assets/boss_kollman.jpg"
	})

	full_narrative = info["narrative"]
	boss_quote = info["quote"]
	quote_color = info["quote_color"]

	var portrait_path = info.get("portrait", "")
	if ResourceLoader.exists(portrait_path):
		boss_portrait.texture = load(portrait_path)

	boss_quote_label.text = boss_quote
	boss_quote_label.add_theme_color_override("font_color", quote_color)

	narrative_container.visible = true
	reveal_container.visible = false
	narrative_label.text = ""
	current_char_idx = 0
	current_state = State.TYPING
	visible = true

func _process(delta: float):
	if not visible: return

	if current_state == State.TYPING:
		typing_timer += delta
		if typing_timer >= typing_speed:
			typing_timer = 0.0
			if current_char_idx < full_narrative.length():
				current_char_idx += 1
				narrative_label.text = full_narrative.substr(0, current_char_idx)
			else:
				current_state = State.TYPING_DONE
				prompt_type_label.text = "[ Kliknij w dowolnym miejscu, aby kontynuować ▶ ]"
				prompt_type_label.add_theme_color_override("font_color", Color("#f4d03f"))

func _gui_input(event: InputEvent):
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		_advance()
		accept_event()

func _unhandled_input(event: InputEvent):
	if not visible: return
	if event is InputEventKey and event.is_pressed() and not event.is_echo():
		if event.keycode == KEY_SPACE or event.keycode == KEY_ENTER:
			_advance()
			get_viewport().set_input_as_handled()

func _advance():
	if current_state == State.TYPING:
		# Pomiń animację pisania
		current_char_idx = full_narrative.length()
		narrative_label.text = full_narrative
		current_state = State.TYPING_DONE
		prompt_type_label.text = "[ Kliknij w dowolnym miejscu, aby kontynuować ▶ ]"
		prompt_type_label.add_theme_color_override("font_color", Color("#f4d03f"))
	elif current_state == State.TYPING_DONE:
		# Przejdź do ujawnienia bossa
		narrative_container.visible = false
		reveal_container.visible = true
		current_state = State.REVEALED
	elif current_state == State.REVEALED:
		# Koniec cutscenki -> walka
		visible = false
		finished.emit()
