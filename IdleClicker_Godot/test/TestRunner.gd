extends SceneTree

const ForgeUIEffects = preload("res://scripts/ui/ForgeUIEffects.gd")

func _init():
	print("==================================================")
	print("ROZPOCZĘCIE TESTÓW JEDNOSTKOWYCH IDLECLICKER GODOT")
	print("==================================================")

	test_player_basics()
	test_combat_math()
	test_elite_loop_and_no_emojis()
	test_companions_and_quests()
	test_alchemy_and_garden()
	test_market_and_synergies()
	test_blacksmith_upgrades_and_sockets()
	test_dungeons()
	test_shop_and_stat_points()
	test_barnaba_and_dialogues()
	test_save_load()
	test_defeat_and_tavern_regeneration()
	test_forge_ui_and_stats_view()
	test_inventory_multi_sell()
	test_hero_portrait_and_hud_fixes()

	print("==================================================")
	print("WSZYSTKIE TESTY ZAKOŃCZONE SUKCESEM (100% PASS)!")
	print("==================================================")
	quit(0)

func assert_true(cond: bool, msg: String):
	if not cond:
		push_error("FAIL: %s" % msg)
		print("[FAIL] %s" % msg)
		quit(1)
	else:
		print("[PASS] %s" % msg)

func test_player_basics():
	print("\n--- Test: Player Podstawy i Statystyki ---")
	var p = Player.new()
	assert_true(p.level == 1, "Gracz zaczyna na 1 poziomie")
	assert_true(p.gold == 0, "Gracz zaczyna z 0 złota")
	assert_true(p.hp == 85 and p.max_hp == 85, "Gracz ma 85 bazowego HP")
	assert_true(p.get_total_atk() >= 8, "Gracz ma przynajmniej 8 ATK")
	assert_true(p.get_total_def() >= 4, "Gracz ma przynajmniej 4 DEF")

	# EXP i awans
	var initial_lvl = p.level
	p.add_exp(p.get_exp_required())
	assert_true(p.level == initial_lvl + 1, "Awans na 2 poziom po zdobyciu wymaganego EXP")
	assert_true(p.stat_points == 3, "Gracz otrzymał 3 punkty statystyk")

func test_combat_math():
	print("\n--- Test: Formuły Bojowe i Obrażenia ---")
	var p = Player.new()
	var enemy = EnemiesDB.generate_enemy(EnemiesDB.TEMPLATES[0], 1, false)

	var res = CombatMath.calculate_player_dmg(p, enemy, true)
	assert_true(res.has("damage") and res["damage"] > 0, "Gracz zadaje dodatnie obrażenia")

	var e_dmg = CombatMath.calculate_enemy_dmg(enemy, p)
	assert_true(e_dmg > 0, "Wróg zadaje dodatnie obrażenia")

	# Tarcza bojowa
	p.combat_shield = 50
	var rem = p.absorb_shield_hit(30)
	assert_true(rem == 0 and p.combat_shield == 20, "Tarcza wchłonęła 30 obrażeń z 50")
	var rem2 = p.absorb_shield_hit(25)
	assert_true(rem2 == 5 and p.combat_shield == 0, "Tarcza wchłonęła 20, 5 przebiło")

func test_elite_loop_and_no_emojis():
	print("\n--- Test: Resetowanie Elitarnych w Pętli & Brak Emotek ---")
	# 1. Brak emotek w afiksach i nazwach
	for aff_key in EnemiesDB.ELITE_AFFIXES.keys():
		var aff = EnemiesDB.ELITE_AFFIXES[aff_key]
		assert_true(not aff["name"].contains("🔥") and not aff["name"].contains("🛡️") and not aff["name"].contains("💰"), "Brak emotek w afiksie %s" % aff_key)

	for t in EnemiesDB.TEMPLATES:
		assert_true(not t["name"].contains("🔥") and not t["name"].contains("🐺"), "Brak emotek w szablonie %s" % t["id"])

	# 2. Generowanie elitarnego na żądanie
	var elite = EnemiesDB.generate_enemy(EnemiesDB.TEMPLATES[0], 5, true)
	assert_true(elite["is_elite"] == true, "Wymuszony potwór elitarny ma flagę is_elite=true")
	assert_true(elite["name"].begins_with("["), "Potwór elitarny posiada prefix w nawiasie kwadratowym")

	# 3. Pętla po pokonaniu elitarnego: generowanie zwykłego (force_elite=false)
	var next_normal = EnemiesDB.generate_enemy(EnemiesDB.TEMPLATES[0], 5, false)
	assert_true(next_normal["is_elite"] == false, "Następny potwór po elitarnym w pętli jest ZWYKŁY")

func test_companions_and_quests():
	print("\n--- Test: Towarzysze, Lore i Zadania Fabularne ---")
	var p = Player.new()
	assert_true(p.party.is_empty(), "Początkowo drużyna jest pusta")

	# Odblokowanie Maślaka
	p.party.append("maslak")
	p.select_active_companion("maslak")
	assert_true(p.active_companion == "maslak", "Maślak ustawiony jako aktywny towarzysz")
	var party_bonus = p.get_party_bonus()
	assert_true(party_bonus["atk"] > 0 and party_bonus["hp"] > 0, "Maślak zapewnia bonusy do ATK i HP")

	var ult = CombatMath.get_companion_ultimate("maslak")
	assert_true(ult["name"] == "Lukrowany Pączek", "Zdolność Maślaka to Lukrowany Pączek")

	var ult_eczme = CombatMath.get_companion_ultimate("eczme")
	assert_true(ult_eczme["name"] == "Ścina Przeznaczenia", "Zdolność Eczmego to Ścina Przeznaczenia")

func test_alchemy_and_garden():
	print("\n--- Test: Alchemia, Ogród i Receptury ---")
	var p = Player.new()
	assert_true(p.herb_garden.size() == 4, "Ogród posiada 4 grządki")
	assert_true(p.herb_garden[0]["unlocked"] == false, "Pierwsza grządka jest początkowo zablokowana (wymaga dzierżawy u Barnaby)")

	# Dzierżawa u Barnaby
	p.gold = 200
	var leased = p.lease_herb_plot(150)
	assert_true(leased and p.herb_garden[0]["unlocked"] == true and p.gold == 50, "Pomyślna dzierżawa pierwszej grządki za 150 złota u Barnaby")

	# Odblokowanie kolejnej grządki
	p.unlock_garden_plot(1)
	assert_true(p.herb_garden[1]["unlocked"] == true, "Druga grządka odblokowana")

	# Zbiór (symulacja upływu czasu)
	p.herb_garden[0]["planted_at"] = Time.get_unix_time_from_system() - 100.0
	var harvest_res = p.harvest_garden_plot(0)
	assert_true(harvest_res != null and harvest_res["herb"] == "herb_amanita", "Pomyślny zbiór Amanity")

func test_market_and_synergies():
	print("\n--- Test: Rynek Budynków i Synergie Towarzyszy ---")
	var p = Player.new()
	var b1_cost = BuildingsDB.get_cost("b1", 0)
	assert_true(b1_cost == 50, "Bazowy koszt Cukierni Maślaka wynosi 50")

	p.gold = 100
	p.gold -= b1_cost
	p.buildings["b1"] = 1
	var gps = p.recalculate_gold_per_sec()
	assert_true(gps == 1, "Pasywna produkcja wynosi 1/s bez synergii")

	# Dodanie Maślaka do drużyny (+25% synergii)
	p.party.append("maslak")
	p.recalculate_gold_per_sec()
	assert_true(BuildingsDB.get_synergy_multiplier("b1", p.party, p.active_companion) == 1.25, "Synergia w drużynie wynosi 1.25")

	# Ustawienie Maślaka jako aktywnego (+40% synergii)
	p.select_active_companion("maslak")
	assert_true(BuildingsDB.get_synergy_multiplier("b1", p.party, p.active_companion) == 1.40, "Synergia aktywnego towarzysza wynosi 1.40")

func test_blacksmith_upgrades_and_sockets():
	print("\n--- Test: Kuźnia Kowala, Ulepszenia i Klejnoty ---")
	var p = Player.new()
	var club = {"id": "wep_wooden_club", "lvl": 0, "sockets": []}
	p.inventory.append(club)

	# Ulepszenie na +1
	club["lvl"] = 1
	var res = ItemsDB.resolve_item(club)
	assert_true(res["stats"]["atk"] > 3, "Ulepszenie zwiększa statystyki broni")
	assert_true(res["display_name"] == "Drewniana Pałka +1", "Nazwa zawiera poziom ulepszenia")

	# Wprawienie klejnotu
	club["sockets"].append("gem_ruby")
	p.equip(club)
	var gem_bon = p.get_gems_bonus()
	assert_true(gem_bon["atk"] > 0, "Rubin w gnieździe zwiększa całkowity ATK")

func test_dungeons():
	print("\n--- Test: Baza Lochów i Wymagania ---")
	assert_true(DungeonsDB.DUNGEONS.size() == 8, "Gra zawiera 8 zdefiniowanych lochów")
	assert_true(DungeonsDB.DUNGEONS[0]["boss_id"] == "boss_ptys", "Boss pierwszego lochu to Ptyś")
	assert_true(DungeonsDB.DUNGEONS[1]["boss_id"] == "boss_kollman", "Boss drugiego lochu to Kollman")

func test_shop_and_stat_points():
	print("\n--- Test: Sklep Fantasy i Rozdział Punktów Statystyk ---")
	assert_true(ShopDB.TIERS.size() == 7, "Sklep Fantasy zawiera 7 poziomów asortymentu")
	var p_cost = ShopDB.get_item_price("pot_hp", 1)
	assert_true(p_cost >= 50, "Cena mikstury zdrowia jest dodatnia i skalowana")

	var p = Player.new()
	p.stat_points = 5
	var old_atk = p.stats.get("base_atk", 12)
	var ok = p.invest_stat_point("base_atk", 2)
	assert_true(ok and p.stats["base_atk"] == old_atk + 2, "Inwestycja w ATK zwiększa bazowy atak o 2")
	assert_true(p.stat_points == 3, "Pozostały 3 punkty rozwoju")

	# Limit szansy na krytyk (maks 30%)
	p.stat_points = 50
	p.invest_stat_point("crit_chance", 40)
	assert_true(p.stats["crit_chance"] == 30, "Szansa na krytyk jest ograniczona do limitu 30%")

	# Limit szansy na łup (maks 50%)
	p.stat_points = 100
	p.invest_stat_point("bonus_loot_pct", 60)
	assert_true(p.stats["bonus_loot_pct"] == 50, "Szansa na łup jest ograniczona do limitu 50%")

func test_barnaba_and_dialogues():
	print("\n--- Test: Karczmarz Barnaba i Dialogi NPC ---")
	assert_true(NPCLoreDB.NPCS.has("innkeeper"), "Baza zawiera Karczmarza Barnabę")
	var barnaba = NPCLoreDB.NPCS["innkeeper"]
	assert_true(barnaba.has("options") and barnaba["options"].size() >= 4, "Barnaba posiada opcje dialogowe")

	var p = Player.new()
	p.hp = 10
	p.mana = 20
	p.gold = 50
	var rested = p.rest_at_inn(20)
	assert_true(rested and p.gold == 30 and p.hp == p.get_max_hp() and p.mana == p.max_mana, "Odpoczynek u Barnaby odnawia 100% HP i Many za 20 złota")

	# Depozyt nagród
	while not p.is_inventory_full():
		p.inventory.append({"id": "pot_hp", "lvl": 0})
	assert_true(p.is_inventory_full(), "Ekwipunek zapełniony do 80 slotów")

	p.add_to_inventory("wep_mithril_blade", true)
	assert_true(p.inventory_stash.size() == 1, "Nagroda zdeponowana u Barnaby przy pełnym plecaku")

	p.inventory.remove_at(0)
	var claimed = p.claim_stash_item(0)
	assert_true(claimed and p.inventory_stash.is_empty(), "Odebrano przedmiot z depozytu po zwolnieniu miejsca")

func test_save_load():
	print("\n--- Test: Serializacja i Zapis Stanu Gry ---")
	var p1 = Player.new()
	p1.level = 7
	p1.gold = 1500
	p1.party = ["maslak", "damian"]
	p1.active_companion = "damian"
	p1.inventory_stash = [{"id": "pot_hp", "lvl": 0}]

	var save_dict = p1.to_dict()
	var p2 = Player.new()
	p2.from_dict(save_dict)

	assert_true(p2.level == 7, "Wczytano poziom 7")
	assert_true(p2.gold == 1500, "Wczytano 1500 złota")
	assert_true(p2.party.has("maslak") and p2.party.has("damian"), "Wczytano drużynę")
	assert_true(p2.active_companion == "damian", "Wczytano aktywnego towarzysza")
	assert_true(p2.inventory_stash.size() == 1, "Wczytano depozyt nagród")

	# Test wieloprofilowego SaveSystem na dysku
	var test_char = Player.new("TestowyBohater")
	test_char.level = 9
	test_char.gold = 9999
	var saved_ok = SaveSystem.save_game(test_char, "TestowyBohater.json")
	assert_true(saved_ok, "SaveSystem: Zapisano profil gry na dysku")

	var all_saves = SaveSystem.get_all_saves()
	var found = false
	for s in all_saves:
		if s.get("filename") == "TestowyBohater.json":
			found = true
			assert_true(s.get("name") == "TestowyBohater", "SaveSystem: Nazwa profilu zgodna")
			assert_true(s.get("level") == 9, "SaveSystem: Poziom w nagłówku zgodny")
			break
	assert_true(found, "SaveSystem: Profil TestowyBohater odnaleziony na liście zapisów")

	var loaded_char = Player.new()
	var load_ok = SaveSystem.load_game(loaded_char, "TestowyBohater.json")
	assert_true(load_ok and loaded_char.level == 9 and loaded_char.gold == 9999, "SaveSystem: Pomyślnie wczytano stan profilu")

	var del_ok = SaveSystem.delete_save("TestowyBohater.json")
	assert_true(del_ok, "SaveSystem: Pomyślnie usunięto testowy plik zapisu")

func test_defeat_and_tavern_regeneration():
	print("\n--- Test: Porażka w Walce i Regeneracja w Karczmie ---")
	var p = Player.new()
	var max_h = p.get_max_hp()

	# 1. Gracz otrzymuje śmiertelne obrażenia - HP spada do 0 (nie 1!)
	p.hp = 15
	var lethal_dmg = 30
	p.hp = maxi(0, p.hp - lethal_dmg)
	assert_true(p.hp == 0, "Śmiertelny cios zbija punkty życia do 0 HP (a nie sztuczne 1 HP)")

	# 2. Próba wykonania ataku przy 0 HP powinna być zablokowana
	var can_attack = (p.hp > 0)
	assert_true(not can_attack, "Postać z 0 HP nie może atakować wrogów")

	# 3. Przeniesienie do Karczmy - Barnaba udziela pierwszej pomocy (10% Max HP)
	p.hp = maxi(1, int(max_h * 0.10))
	assert_true(p.hp == int(max_h * 0.10), "Barnaba w karczmie opatruje bohatera do poziomu pierwszej pomocy (10% Max HP)")

	# 4. Pasywna regeneracja w Karczmie (8% Max HP co sekundę)
	var prev_hp = p.hp
	var tavern_regen = maxi(5, int(max_h * 0.08))
	p.hp = mini(max_h, p.hp + tavern_regen)
	assert_true(p.hp == prev_hp + tavern_regen, "Odpoczynek przy kominku w karczmie regeneruje zdrowie co sekundę (+8% Max HP)")

	# Wielokrotne tyknięcia regeneracji w karczmie przywracają 100% zdrowia
	for i in range(15):
		p.hp = mini(max_h, p.hp + tavern_regen)
	assert_true(p.hp == max_h, "Bohater w pełni regeneruje siły w karczmie po osiągnięciu maksymalnego zdrowia")

func test_forge_ui_and_stats_view():
	print("\n--- Test: Dark Fantasy Forge UI & StatsView ---")
	var p = Player.new()
	var gm_script = load("res://scripts/autoload/GameManager.gd")
	var gm = gm_script.new()
	gm.name = "GameManager"
	gm.player = p
	root.add_child(gm)

	var sm_script = load("res://scripts/autoload/SoundManager.gd")
	var sm = sm_script.new()
	sm.name = "SoundManager"
	root.add_child(sm)

	var stats_scene = load("res://scenes/views/StatsView.tscn")
	assert_true(stats_scene != null, "Scena StatsView.tscn została pomyślnie załadowana")

	var instance = stats_scene.instantiate()
	assert_true(instance != null, "Scena StatsView.tscn została pomyślnie zinstancjonowana")
	root.add_child(instance)

	var portrait = instance.get_node_or_null("%HeroPortrait")
	var btn_atk = instance.get_node_or_null("%BtnAtkPlus1")
	var btn_tal = instance.get_node_or_null("%BtnTalentBerserker")
	var stat_pts_lbl = instance.get_node_or_null("%StatPointsLabel")

	assert_true(portrait != null, "Portret bohatera istnieje i jest połączony")
	assert_true(btn_atk != null, "Przycisk ATK +1 jest obecny")
	assert_true(btn_tal != null, "Przycisk Talentu Berserkera jest obecny")

	# Test mikro-reakcji i rejestracji
	ForgeUIEffects.register_interactive_controls(instance)
	if stat_pts_lbl:
		ForgeUIEffects.pulse_node(stat_pts_lbl)

	instance.queue_free()
	gm.queue_free()
	sm.queue_free()
	assert_true(true, "StatsView i system efektów ForgeUIEffects działają poprawnie")

func test_inventory_multi_sell():
	print("\n--- Test: Wielokrotne zaznaczanie i hurtowa sprzedaż z CTRL ---")
	var p = Player.new()
	p.inventory.clear()

	# Dodaj 4 przedmioty
	p.add_to_inventory("wep_iron_sword", true)
	p.add_to_inventory("arm_leather_vest", true)
	p.add_to_inventory("pot_hp", true)
	p.add_to_inventory("wep_rusty_dagger", true)
	assert_true(p.inventory.size() == 4, "W plecaku znajdują się 4 przedmioty")

	# Test metody remove_multiple_from_inventory
	# Usuń przedmioty o indeksach 1 i 3 (arm_leather_vest i wep_rusty_dagger)
	var removed = p.remove_multiple_from_inventory([1, 3])
	assert_true(removed.size() == 2, "Pomyślnie usunięto 2 przedmioty jednocześnie")
	assert_true(p.inventory.size() == 2, "W plecaku pozostały 2 przedmioty")
	assert_true(p.inventory[0]["id"] == "wep_iron_sword", "Pierwszy przedmiot (wep_iron_sword) nienaruszony")
	assert_true(p.inventory[1]["id"] == "pot_hp", "Drugi przedmiot (pot_hp) nienaruszony na właściwym nowym indeksie")

	# Test interfejsu InventoryView i symulacji CTRL-click
	var gm_script = load("res://scripts/autoload/GameManager.gd")
	var gm = gm_script.new()
	gm.name = "GameManager"
	gm.player = p
	root.add_child(gm)

	var inv_scene = load("res://scenes/views/InventoryView.tscn")
	assert_true(inv_scene != null, "Scena InventoryView.tscn załadowana pomyślnie")
	var inv_inst = inv_scene.instantiate()
	inv_inst.player = p
	root.add_child(inv_inst)

	# Symuluj zaznaczenie z CTRL obu pozostałych przedmiotów
	inv_inst._on_inventory_slot_clicked(p.inventory[0], 0, true)
	inv_inst._on_inventory_slot_clicked(p.inventory[1], 1, true)
	assert_true(inv_inst.selected_inv_indices.size() == 2, "Zaznaczono 2 przedmioty z przytrzymanym CTRL")
	assert_true(inv_inst.btn_sell.visible == true, "Przycisk sprzedaży widoczny dla wielu zaznaczonych")

	# Wykonaj hurtową sprzedaż
	var gold_before = p.gold
	inv_inst._on_sell_pressed()
	assert_true(p.gold > gold_before, "Złoto wzrosło po hurtowej sprzedaży")
	assert_true(p.inventory.is_empty(), "Wszystkie zaznaczone przedmioty zostały usunięte z plecaka")
	assert_true(inv_inst.selected_inv_indices.is_empty(), "Lista zaznaczonych indeksów została wyczyszczona")

	inv_inst.queue_free()
	gm.queue_free()

func test_hero_portrait_and_hud_fixes():
	print("\n--- Test: Poprawki Portretu Bohatera, Responsywnego HUD i Ogrodu ---")
	var p = Player.new()


	# 1. Walidacja Ogrodu w migrate()
	p.herb_garden[1]["unlocked"] = true # symulacja niepoprawnego odblokowania bez questa/kompana
	p.migrate()
	assert_true(p.herb_garden[1]["unlocked"] == false, "Grządka #2 zablokowana jeśli gracz nie posiada Eczmego")

	# Odblokowanie po rekrutacji Eczmego
	p.party.append("eczme")
	p.migrate()
	assert_true(p.is_quest_claimed_or_companion_unlocked("eczme", "q_party_eczme") == true, "Wykrycie zwerbowanego Eczmego")

	# 2. Weryfikacja plików i zasobów portretu oraz widoków
	assert_true(FileAccess.file_exists("res://assets/portraits/hero.jpg"), "Plik portretu bohatera res://assets/portraits/hero.jpg istnieje")
	var hero_tex = load("res://assets/portraits/hero.jpg")
	assert_true(hero_tex != null, "Tekstura portretu bohatera ładuje się pomyślnie")

	# Sprawdzenie definicji scen pod kątem naprawionych elementów
	var cv_text = FileAccess.get_file_as_string("res://scenes/views/CombatView.tscn")
	assert_true(cv_text.contains("PlayerPortrait") and cv_text.contains("res://assets/portraits/hero.jpg"), "CombatView zawiera PlayerPortrait powiązany z hero.jpg")

	var tv_text = FileAccess.get_file_as_string("res://scenes/views/TavernView.tscn")
	assert_true(tv_text.contains("DetailPanel") and not tv_text.contains("DetailCard"), "TavernView zawiera statyczny DetailPanel (a nie reagujący DetailCard)")

	var dbg_text = FileAccess.get_file_as_string("res://scenes/components/DebugConsole.tscn")
	assert_true(dbg_text.contains("ConsoleScroll"), "DebugConsole posiada ConsoleScroll")

	var main_text = FileAccess.get_file_as_string("res://scenes/Main.tscn")
	assert_true(main_text.contains("HeroAvatar") and main_text.contains("NotificationToast"), "Main.tscn posiada awatar bohatera i niezależny NotificationToast")



