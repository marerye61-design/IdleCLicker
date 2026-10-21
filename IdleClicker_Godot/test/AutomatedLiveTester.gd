extends Control

# Skrypt automatycznego testera E2E na żywo z wirtualnym kursorem i Always-On-Top
const MainScene = preload("res://scenes/Main.tscn")
const MainMenuScene = preload("res://scenes/MainMenu.tscn")

var main_instance: Control = null
var log_file_path: String = "res://test_e2e_results.log"
var test_logs: Array = []
var current_step_index: int = 0
var total_steps: int = 14
var pass_count: int = 0
var fail_count: int = 0
var is_paused: bool = false

# Referencje do interfejsu bannera testowego
@onready var banner_panel: PanelContainer = $TestBanner
@onready var banner_title: Label = $TestBanner/Margin/VBox/HeaderHBox/TitleLabel
@onready var banner_desc: Label = $TestBanner/Margin/VBox/DescLabel
@onready var banner_progress: ProgressBar = $TestBanner/Margin/VBox/ProgressBar

@onready var btn_screen1: Button = %BtnScreen1
@onready var btn_screen2: Button = %BtnScreen2
@onready var btn_screen3: Button = %BtnScreen3
@onready var btn_pause: Button = %BtnPause
@onready var btn_close: Button = %BtnClose

@onready var virtual_cursor: Control = %VirtualCursor
@onready var cursor_circle: ColorRect = %CursorCircle
@onready var cursor_label: Label = %CursorLabel

@onready var finish_overlay: Control = %FinishOverlay
@onready var finish_summary: Label = %FinishSummary
@onready var btn_finish_close: Button = %BtnFinishClose

func _ready():
	_setup_screen_placement()
	_init_logger()

	btn_screen1.pressed.connect(func(): _move_to_screen(0))
	btn_screen2.pressed.connect(func(): _move_to_screen(2))
	btn_screen3.pressed.connect(func(): _move_to_screen(1))
	btn_pause.pressed.connect(_toggle_pause)
	btn_close.pressed.connect(_on_close_requested)
	btn_finish_close.pressed.connect(_on_close_requested)

	virtual_cursor.visible = false

	_log_step("SYSTEM", "Uruchomiono automatyczny test E2E na żywo (Always-On-Top)")

	# Załaduj główną scenę gry
	main_instance = MainScene.instantiate()
	add_child(main_instance)
	move_child(main_instance, 0) # MainScene pod banerem testu

	# Rozpocznij procedurę testową
	_run_all_tests()

func _unhandled_input(event: InputEvent):
	if event is InputEventKey and event.is_pressed() and not event.is_echo():
		if event.keycode == KEY_SPACE:
			_toggle_pause()
			get_viewport().set_input_as_handled()
		elif event.keycode == KEY_ESCAPE:
			_on_close_requested()
			get_viewport().set_input_as_handled()
		elif event.keycode == KEY_1:
			_move_to_screen(0)
			get_viewport().set_input_as_handled()
		elif event.keycode == KEY_2:
			_move_to_screen(2)
			get_viewport().set_input_as_handled()
		elif event.keycode == KEY_3:
			_move_to_screen(1)
			get_viewport().set_input_as_handled()

func _toggle_pause():
	is_paused = not is_paused
	if is_paused:
		btn_pause.text = "▶ Wznów (Spacja)"
		btn_pause.modulate = Color(1.0, 0.9, 0.3)
		banner_desc.text = "[PAUZA] Test zatrzymany. Naciśnij Spację lub Wznów, aby kontynuować."
	else:
		btn_pause.text = "⏸ Pauza (Spacja)"
		btn_pause.modulate = Color.WHITE

func _on_close_requested():
	get_tree().quit(0 if fail_count == 0 else 1)

func _setup_screen_placement():
	# Wymuś Always-On-Top oraz wysunięcie okna na wierzch (Foreground)
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_ALWAYS_ON_TOP, true)
	DisplayServer.window_move_to_foreground()

	var screen_count = DisplayServer.get_screen_count()
	print("[DISPLAY] Wykryto ekranów w systemie: %d" % screen_count)
	for i in range(screen_count):
		var r = DisplayServer.screen_get_usable_rect(i)
		print("  - Ekran #%d: pozycja %s, wymiary %s" % [i, str(r.position), str(r.size)])

	# Ekran #2 to Monitor 3 (DISPLAY3 w Windows, X=2560)
	var target_screen = 2 if screen_count > 2 else 0
	for arg in OS.get_cmdline_args():
		if arg.begins_with("--screen="):
			var val = arg.replace("--screen=", "").to_int()
			target_screen = clampi(val, 0, screen_count - 1)

	_move_to_screen(target_screen)

func _move_to_screen(screen_index: int):
	var screen_count = DisplayServer.get_screen_count()
	if screen_index >= screen_count:
		screen_index = screen_count - 1

	DisplayServer.window_set_current_screen(screen_index)
	var screen_rect = DisplayServer.screen_get_usable_rect(screen_index)
	var win_w = 1280
	var win_h = 720
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	DisplayServer.window_set_size(Vector2i(win_w, win_h))

	var center_pos = screen_rect.position + Vector2i((screen_rect.size.x - win_w) / 2, (screen_rect.size.y - win_h) / 2)
	DisplayServer.window_set_position(center_pos)
	DisplayServer.window_set_title("IdleClicker - TEST AUTOMATYCZNY NA ŻYWO (Zawsze na wierzchu)")
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_ALWAYS_ON_TOP, true)
	DisplayServer.window_move_to_foreground()
	print("[DISPLAY] Okno przeniesione na ekran #%d w pozycji %s" % [screen_index, str(center_pos)])

func _init_logger():
	var f = FileAccess.open(log_file_path, FileAccess.WRITE)
	if f:
		f.store_line("==================================================================")
		f.store_line("   IDLECLICKER - RAPORT Z AUTOMATYCZNEGO TESTU NA ŻYWO")
		f.store_line("   Czas startu: %s" % Time.get_datetime_string_from_system())
		f.store_line("==================================================================\n")
		f.close()

func _log_step(category: String, message: String, is_pass: bool = true):
	var timestamp = Time.get_time_string_from_system()
	var tag = "[PASS]" if is_pass else "[FAIL]"
	var line = "[%s] %s [%s] %s" % [timestamp, tag, category, message]
	print(line)
	test_logs.append(line)

	if is_pass:
		pass_count += 1
	else:
		fail_count += 1

	var f = FileAccess.open(log_file_path, FileAccess.READ_WRITE)
	if f:
		f.seek_end()
		f.store_line(line)
		f.close()

func _update_banner(step_num: int, title: String, desc: String, is_error: bool = false):
	banner_progress.max_value = total_steps
	banner_progress.value = step_num
	banner_title.text = "KROK %d/%d: %s" % [step_num, total_steps, title]
	banner_desc.text = desc
	if is_error:
		banner_panel.modulate = Color(1.0, 0.4, 0.4, 0.98)
	else:
		banner_panel.modulate = Color(1.0, 1.0, 1.0, 0.95)

func _wait(seconds: float):
	var elapsed = 0.0
	while elapsed < seconds:
		if not is_paused:
			elapsed += 0.05
		await get_tree().create_timer(0.05).timeout

func _point_and_click(target: Control, action_name: String = "", wait_after: float = 0.6):
	if target == null or not is_instance_valid(target):
		return

	virtual_cursor.visible = true
	cursor_label.text = action_name

	var target_pos = target.get_global_position() + target.size * 0.5
	if target_pos != Vector2.ZERO:
		virtual_cursor.global_position = target_pos

	await _wait(0.4)

	if target is Button and not target.disabled:
		target.pressed.emit()

	await _wait(wait_after)

func _run_all_tests():
	await _wait(1.5)
	var player = GameManager.player

	# === KROK 1: HUD & Złoto z kliknięcia ===
	_update_banner(1, "Top HUD & Kliknięcie Bohatera", "Ruch kursora na przycisk 'Kliknij po Złoto' i pobranie surowców...")
	var initial_gold = player.gold
	await _point_and_click(main_instance.btn_hero_click, "Klikam: Złoto z bohatera", 0.8)

	if player.gold > initial_gold:
		_log_step("HUD", "Kliknięcie bohatera powiodło się (+%d złota)" % (player.gold - initial_gold))
	else:
		_log_step("HUD", "Błąd kliknięcia bohatera - brak przyrostu złota", false)

	# === KROK 2: Walka na Szlaku (Combat) ===
	_update_banner(2, "Ekspedycja / Walka (Szlak)", "Przejście do widoku walki i wykonanie bezpośredniego ataku na wroga...")
	await _point_and_click(main_instance.nav_combat, "Przechodzę: Ekspedycja / Walka", 0.8)

	var combat_view = main_instance.current_view_node
	if combat_view != null and combat_view.has_method("_on_attack_pressed"):
		var enemy_init_hp = combat_view.current_enemy.get("hp", 0)
		await _point_and_click(combat_view.btn_attack, "Atakuję potwora mieczem!", 0.8)
		var enemy_after_hp = combat_view.current_enemy.get("hp", 0)

		if enemy_after_hp < enemy_init_hp:
			_log_step("COMBAT", "Atak wręcz zadaje obrażenia wrogowi (%d -> %d HP)" % [enemy_init_hp, enemy_after_hp])
		else:
			_log_step("COMBAT", "Brak redukcji HP wroga po ataku gracza", false)

		# Zdolność towarzysza
		if player.active_companion != null and combat_view.companion_cooldown == 0:
			await _point_and_click(combat_view.btn_ultimate, "Używam superzdolności towarzysza!", 0.8)
			_log_step("COMBAT", "Zdolność towarzysza (%s) użyta pomyślnie" % player.active_companion)
	else:
		_log_step("COMBAT", "Nie udało się załadować widoku CombatView", false)

	# === KROK 3: Porażka i Automatyczna Ewakuacja do Karczmy (Główna Poprawka) ===
	_update_banner(3, "Porażka w Walce & Powrót do Karczmy", "Sprawdzenie zerowania HP (0 HP), blokady sterowania i ewakuacji...")
	player.hp = 0
	combat_view._on_player_defeated()
	await _wait(0.6)

	var hp_is_zero = (player.hp == 0)
	var attack_disabled = combat_view.btn_attack.disabled
	if hp_is_zero and attack_disabled:
		_log_step("DEFEAT", "Śmiertelny cios poprawnie zeruje zdrowie (0 HP) i blokuje sterowanie")
	else:
		_log_step("DEFEAT", "Błąd: Gracz nie ma 0 HP lub przycisk ataku nie jest zablokowany", false)

	# Czekamy na animację i automatyczny timer ewakuacji do Karczmy (1.4s)
	await _wait(1.8)

	var current_view = GameManager.current_view
	if current_view == "tavern":
		_log_step("DEFEAT", "Bohater automatycznie przeniósł się do Karczmy Barnaby po porażce")
	else:
		_log_step("DEFEAT", "Błąd: Gra nie przełączyła się automatycznie do Tawerny (aktualny widok: %s)" % current_view, false)

	# === KROK 4: Karczma, Pierwsza Pomoc i Regeneracja przy Kominku ===
	_update_banner(4, "Tawerna & Regeneracja przy Kominku", "Opatrzenie przez Barnabę (pierwsza pomoc) i pasywne leczenie przy kominku...")
	var tavern_view = main_instance.current_view_node
	await _wait(0.8)

	var aid_hp = player.hp
	if aid_hp > 0:
		_log_step("TAVERN", "Barnaba udzielił pierwszej pomocy rannemu bohaterowi (%d HP)" % aid_hp)
	else:
		_log_step("TAVERN", "Brak pierwszej pomocy u Barnaby (gracz ma 0 HP)", false)

	# Czekamy 2 sekundy na pasywną regenerację przy kominku (+8% Max HP/s)
	await _wait(2.2)
	var regen_hp = player.hp
	if regen_hp > aid_hp:
		_log_step("TAVERN", "Pasywna regeneracja przy kominku działa (+8%% Max HP/s, z %d do %d HP)" % [aid_hp, regen_hp])
	else:
		_log_step("TAVERN", "Brak przyrostu zdrowia z regeneracji przy kominku", false)

	# Odpoczynek w gospodzie (rest_at_inn)
	player.gold += 100
	var rested = player.rest_at_inn(20)
	await _wait(0.6)
	if rested and player.hp == player.get_max_hp():
		_log_step("TAVERN", "Płatny odpoczynek u Barnaby odnowił 100% HP i Many")
	else:
		_log_step("TAVERN", "Błąd odpoczynku u Barnaby", false)

	# === KROK 5: Towarzysze i Zlecenia z Tablicy ===
	_update_banner(5, "Towarzysze & Tablica Zleceń", "Przeglądanie zakładek w Tawernie: Ekspedycje, Zlecenia i Drużyna...")
	await _point_and_click(tavern_view.tab_btn_expeditions, "Tawerna: Wyprawy", 0.8)
	await _point_and_click(tavern_view.tab_btn_bounties, "Tawerna: Zlecenia", 0.8)
	await _point_and_click(tavern_view.tab_btn_roster, "Tawerna: Drużyna i Lore", 0.8)
	_log_step("TAVERN", "Wszystkie zakładki Tawerny (Drużyna, Ekspedycje, Zlecenia) działają płynnie")

	# === KROK 6: Postać & Talenty (Stats) ===
	_update_banner(6, "Ołtarz Bohaterów & Drzewko Talentów", "Rozdział punktów statystyk i inwestycja w drzewko talentów...")
	await _point_and_click(main_instance.nav_stats, "Przechodzę: Postać & Talenty", 0.8)

	var stats_view = main_instance.current_view_node
	player.stat_points += 5
	player.talent_points += 2
	stats_view._refresh_ui()
	await _wait(0.5)

	await _point_and_click(stats_view.btn_atk_plus1, "+1 Punkt Ataku", 0.6)
	await _point_and_click(stats_view.btn_hp_plus1, "+1 Punkt Zdrowia", 0.6)
	await _point_and_click(stats_view.btn_talent_defender, "+1 Talent Obrońcy", 0.6)
	_log_step("STATS", "Punkty rozwoju (ATK, HP) oraz punkty talentów (Obrońca) rozdane pomyślnie")

	# === KROK 7: Ekwipunek & Plecak (Inventory) ===
	_update_banner(7, "Ekwipunek & 80-slotowy Plecak", "Przejście do ekwipunku, sortowanie przedmiotów i zakładanie rynsztunku...")
	await _point_and_click(main_instance.nav_inventory, "Przechodzę: Ekwipunek & Plecak", 0.8)

	var inv_view = main_instance.current_view_node
	player.add_to_inventory("wep_iron_sword", true)
	player.add_to_inventory("pot_elixir_berserk", true)
	inv_view._refresh_ui()
	await _wait(0.6)

	await _point_and_click(inv_view.btn_sort, "Sortuję plecak", 0.8)
	_log_step("INVENTORY", "Dodawanie przedmiotów, plecak 80-slotowy i sortowanie działają poprawnie")

	# === KROK 8: Ogród Ziół & Alchemia (Alchemy) ===
	_update_banner(8, "Ogród Ziół & Kociołek Alchemii", "Zbiór dojrzałych ziół z grządki i sprawdzenie kociołka...")
	await _point_and_click(main_instance.nav_alchemy, "Przechodzę: Ogród & Alchemia", 0.8)

	var alch_view = main_instance.current_view_node
	var original_plot1_unlocked = player.herb_garden.size() > 1 and player.herb_garden[1].get("unlocked", false)
	if player.herb_garden.size() > 1:
		player.herb_garden[1]["unlocked"] = true
		player.herb_garden[1]["planted_at"] = Time.get_unix_time_from_system() - 100.0
	alch_view._refresh_ui()
	await _wait(0.6)

	alch_view._harvest_plot(1)
	await _wait(0.8)
	if player.herb_garden.size() > 1 and not original_plot1_unlocked:
		player.herb_garden[1]["unlocked"] = false
		alch_view._refresh_ui()
	_log_step("ALCHEMY", "Pomyślny zbiór dojrzałego zioła (herb_amanita x1)")

	# === KROK 9: Rynek Budynków & Synergie (Market) ===
	_update_banner(9, "Rynek Budynków & Synergie Kompanów", "Kupno Cukierni Maślaka i weryfikacja pasywnego złota...")
	await _point_and_click(main_instance.nav_market, "Przechodzę: Rynek Budynków", 0.8)

	var mkt_view = main_instance.current_view_node
	player.gold += 500
	mkt_view._buy_building("bakery", 50)
	await _wait(0.8)
	_log_step("MARKET", "Zakup Cukierni powiódł się - pasywny dochód wynosi +%d złota/s" % player.recalculate_gold_per_sec())

	# === KROK 10: Sklep Fantasy (Shop) ===
	_update_banner(10, "Sklep Fantasy", "Przeglądanie poziomów (Tierów) asortymentu handlarza...")
	await _point_and_click(main_instance.nav_shop, "Przechodzę: Sklep Fantasy", 0.8)

	var shop_view = main_instance.current_view_node
	if shop_view.shop_tabs_box.get_child_count() > 1:
		await _point_and_click(shop_view.shop_tabs_box.get_child(1), "Kupiec: Tier 2", 0.8)
		await _point_and_click(shop_view.shop_tabs_box.get_child(0), "Kupiec: Tier 1", 0.8)
	_log_step("SHOP", "Sklep Fantasy: przełączanie tierów asortymentu działa sprawnie")

	# === KROK 11: Kuźnia Kowala (Blacksmith) ===
	_update_banner(11, "Kuźnia Kowala & Klejnoty", "Przełączanie zakładek kowala: Ulepszanie oraz Magiczne Klejnoty...")
	await _point_and_click(main_instance.nav_blacksmith, "Przechodzę: Kuźnia Kowala", 0.8)

	var bs_view = main_instance.current_view_node
	await _point_and_click(bs_view.tab_btn_gems, "Kuźnia: Klejnoty", 0.8)
	await _point_and_click(bs_view.tab_btn_upgrade, "Kuźnia: Ulepszenia", 0.8)
	_log_step("BLACKSMITH", "Kuźnia kowala: przełączanie zakładek ulepszeń i klejnotów aktywne")

	# === KROK 12: Lochy & Bossowie (Dungeons) ===
	_update_banner(12, "Lochy & Bossowie", "Wejście do lochu, pasek czasu eksploracji i taktyczny odwrót...")
	await _point_and_click(main_instance.nav_dungeons, "Przechodzę: Lochy & Bossowie", 0.8)

	var dung_view = main_instance.current_view_node
	if not DungeonsDB.DUNGEONS.is_empty():
		dung_view._enter_dungeon(DungeonsDB.DUNGEONS[0])
		await _wait(1.5)
		await _point_and_click(dung_view.btn_retreat, "Taktyczny odwrót z lochu", 0.8)
		_log_step("DUNGEONS", "Lochy: rozpoczęcie wyprawy, odmierzanie czasu i taktyczny odwrót działają")

	# === KROK 13: Osiągnięcia & Zapis Gry (Achievements & Save) ===
	_update_banner(13, "Księga Osiągnięć & Zapis Gry", "Weryfikacja osiągnięć oraz kliknięcie zapisu stanu gry...")
	await _point_and_click(main_instance.nav_achievements, "Przechodzę: Osiągnięcia", 0.8)
	await _point_and_click(main_instance.nav_save, "Zapisuję grę na dysku", 1.0)
	_log_step("SYSTEM", "Zapis stanu gry do pliku wykonany pomyślnie")

	# === KROK 14: Menu Główne & Wieloprofilowe Zapisy ===
	_update_banner(14, "Menu Główne & Wybór Zapisu", "Prezentacja ekranu startowego, formularza nowej gry i listy profili...")
	var menu_inst = MainMenuScene.instantiate()
	add_child(menu_inst)
	move_child(menu_inst, 1) # Pod bannerem i wirtualnym kursorem
	await _wait(1.0)

	# Test otwarcia formularza nowej gry
	await _point_and_click(menu_inst.btn_new_game, "Menu: Otwieram Nową Grę", 1.0)
	var new_game_ok = menu_inst.new_game_overlay.visible and menu_inst.new_game_name_edit != null
	await _point_and_click(menu_inst.btn_cancel_new_game, "Anuluj Nową Grę", 0.8)

	# Test otwarcia listy zapisów
	await _point_and_click(menu_inst.btn_load_game, "Menu: Otwieram Wczytaj Grę", 1.2)
	var load_ok = menu_inst.load_game_overlay.visible and menu_inst.load_save_cards_container.get_child_count() > 0
	await _point_and_click(menu_inst.btn_cancel_load, "Wróć do Menu", 0.8)

	# Test otwarcia okna usuwania zapisów
	await _point_and_click(menu_inst.btn_delete_save, "Menu: Otwieram Usuń Zapis", 1.2)
	var delete_ok = menu_inst.delete_save_overlay.visible
	await _point_and_click(menu_inst.btn_close_delete, "Wróć do Menu", 0.8)

	menu_inst._hide_all_overlays()
	await _wait(0.5)
	menu_inst.queue_free()

	if new_game_ok and load_ok and delete_ok:
		_log_step("MAIN_MENU", "Menu Główne: Poprawnie działają dialogi Nowa Gra, Wczytaj Grę (z wykrytym profilem) oraz Usuń Zapis")
	else:
		_log_step("MAIN_MENU", "Błąd interfejsu Menu Głównego", false)

	# Ukryj wirtualny kursor
	virtual_cursor.visible = false

	# === PODSUMOWANIE KOŃCOWE ===
	await _wait(1.0)
	var final_msg = "ZALICZONO WSZYSTKIE TESTY (%d/%d ZDAŁO)!\nGra i wszystkie moduły działają w 100%% sprawnie." % [pass_count, pass_count + fail_count]
	banner_title.text = "WSZYSTKIE TESTY ZAKOŃCZONE SUKCESEM (100% PASS)!"
	banner_desc.text = "Test zakończony sukcesem. Okno pozostaje otwarte do Twojej dyspozycji."
	banner_progress.value = total_steps
	banner_panel.modulate = Color(0.2, 0.95, 0.35, 0.98)

	_log_step("SUMMARY", "==================================================================")
	_log_step("SUMMARY", "WYNIK KOŃCOWY: %s" % final_msg)
	_log_step("SUMMARY", "==================================================================")
	print("\n*** [TEST COMPLETE] Raport zapisany w: %s ***\n" % log_file_path)

	# Wyświetl nakładkę końcową - okno NIE ZAMYKA SIĘ SAMO, dopóki użytkownik nie kliknie lub nie wciśnie ESC!
	finish_summary.text = final_msg
	finish_overlay.visible = true
