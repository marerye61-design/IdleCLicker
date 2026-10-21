class_name ItemsDB

# Słownik wszystkich definicji przedmiotów w grze (statystyki, rzadkość, sloty, opisy)

const ITEMS: Dictionary = {
	"pot_hp": {
		"id": "pot_hp",
		"name": "Mikstura Pełnego Zdrowia",
		"description": "Natychmiastowo leczy 100% maksymalnego HP bohatera (w trakcie walki lub z poziomu ekwipunku).",
		"value": 50,
		"type": "consumable",
		"effect": {"hp_pct": 100},
		"icon": "res://assets/items/pot_hp.jpg"
	},
	"pot_mana": {
		"id": "pot_mana",
		"name": "Mikstura Many",
		"description": "Przywraca 100 punktów many.",
		"value": 40,
		"type": "consumable",
		"effect": {"mana": 100},
		"icon": "res://assets/items/pot_mana.jpg"
	},

	# === PODSTAWOWY EKWIPUNEK SKLEPOWY (ZWYKŁY) ===
	# Tier 1 (Poziom 1)
	"wep_wooden_club": {
		"id": "wep_wooden_club", "name": "Drewniana Pałka",
		"description": "Prosta broń dla nowicjuszy.", "value": 50,
		"type": "equipment", "slot": "weapon", "level_req": 1, "rarity": "Zwykły",
		"base_stats": {"atk": 3}, "icon": "res://assets/items/wep_wooden_club.jpg"
	},
	"arm_leather": {
		"id": "arm_leather", "name": "Skórzana Przeszywanica",
		"description": "Lekki pancerz ochronny.", "value": 200,
		"type": "equipment", "slot": "armor", "level_req": 1, "rarity": "Zwykły",
		"base_stats": {"def": 4, "hp_max": 10}, "icon": "res://assets/items/arm_leather.jpg"
	},
	"helm_leather": {
		"id": "helm_leather", "name": "Skórzany Hełm",
		"description": "Lekka ochrona głowy.", "value": 150,
		"type": "equipment", "slot": "helmet", "level_req": 1, "rarity": "Zwykły",
		"base_stats": {"def": 3}, "icon": "res://assets/items/helm_leather.jpg"
	},
	"acc_ring_small": {
		"id": "acc_ring_small", "name": "Miedziany Pierścień",
		"description": "Zapewnia ochronny urok.", "value": 250,
		"type": "equipment", "slot": "accessory", "level_req": 1, "rarity": "Zwykły",
		"base_stats": {"atk": 2, "def": 2}, "icon": "res://assets/items/acc_ring_small.jpg"
	},

	# Tier 1.5 (Poziom 5)
	"wep_iron_sword": {
		"id": "wep_iron_sword", "name": "Żelazny Miecz",
		"description": "Wytrzymały miecz ze stali.", "value": 400,
		"type": "equipment", "slot": "weapon", "level_req": 5, "rarity": "Zwykły",
		"base_stats": {"atk": 8}, "icon": "res://assets/items/wep_iron_sword.jpg"
	},
	"arm_iron_plate": {
		"id": "arm_iron_plate", "name": "Żelazna Płytówka",
		"description": "Solidna zbroja rycerska.", "value": 600,
		"type": "equipment", "slot": "armor", "level_req": 5, "rarity": "Zwykły",
		"base_stats": {"def": 10, "hp_max": 20}, "icon": "res://assets/items/arm_iron_plate.jpg"
	},
	"helm_iron": {
		"id": "helm_iron", "name": "Żelazny Szyszak",
		"description": "Gruby hełm chroniący przed ciosami w głowę.", "value": 350,
		"type": "equipment", "slot": "helmet", "level_req": 5, "rarity": "Zwykły",
		"base_stats": {"def": 6, "hp_max": 10}, "icon": "res://assets/items/helm_iron.jpg"
	},
	"acc_iron_ring": {
		"id": "acc_iron_ring", "name": "Żelazny Sygnet",
		"description": "Ciężki i solidny pierścień.", "value": 500,
		"type": "equipment", "slot": "accessory", "level_req": 5, "rarity": "Zwykły",
		"base_stats": {"atk": 4, "def": 4, "hp_max": 15}, "icon": "res://assets/items/acc_iron_ring.jpg"
	},

	# Tier 2 (Poziom 15)
	"wep_steel_sword": {
		"id": "wep_steel_sword", "name": "Stalowy Miecz Długi",
		"description": "Ostra, wyważona broń.", "value": 2500,
		"type": "equipment", "slot": "weapon", "level_req": 15, "rarity": "Zwykły",
		"base_stats": {"atk": 25}, "icon": "res://assets/items/wep_steel_sword.jpg"
	},
	"arm_steel_plate": {
		"id": "arm_steel_plate", "name": "Stalowy Kirys",
		"description": "Ciężki pancerz chroniący klatkę.", "value": 4000,
		"type": "equipment", "slot": "armor", "level_req": 15, "rarity": "Zwykły",
		"base_stats": {"def": 22, "hp_max": 50}, "icon": "res://assets/items/arm_steel_plate.jpg"
	},
	"helm_steel": {
		"id": "helm_steel", "name": "Stalowa Przyłbica",
		"description": "Pełna ochrona twarzy i głowy.", "value": 1800,
		"type": "equipment", "slot": "helmet", "level_req": 15, "rarity": "Zwykły",
		"base_stats": {"def": 10, "hp_max": 20}, "icon": "res://assets/items/helm_steel.jpg"
	},
	"acc_silver_amulet": {
		"id": "acc_silver_amulet", "name": "Srebrny Amulet",
		"description": "Błyszczący amulet ochronny.", "value": 3500,
		"type": "equipment", "slot": "accessory", "level_req": 15, "rarity": "Zwykły",
		"base_stats": {"atk": 8, "def": 8, "hp_max": 40}, "icon": "res://assets/items/acc_silver_amulet.jpg"
	},

	# Tier 3 (Poziom 30)
	"wep_mithril_blade": {
		"id": "wep_mithril_blade", "name": "Mithrilowe Ostrze",
		"description": "Niezwykle lekkie i ostre jak brzytwa.", "value": 20000,
		"type": "equipment", "slot": "weapon", "level_req": 30, "rarity": "Zwykły",
		"base_stats": {"atk": 70}, "icon": "res://assets/items/wep_mithril_blade.jpg"
	},
	"arm_mithril_mail": {
		"id": "arm_mithril_mail", "name": "Mithrilowa Kolczuga",
		"description": "Niezwykle lekka, a niemal niezniszczalna.", "value": 30000,
		"type": "equipment", "slot": "armor", "level_req": 30, "rarity": "Zwykły",
		"base_stats": {"def": 55, "hp_max": 120}, "icon": "res://assets/items/arm_mithril_mail.jpg"
	},
	"helm_mithril": {
		"id": "helm_mithril", "name": "Mithrilowy Hełm",
		"description": "Błyszcząca korona bojowa.", "value": 15000,
		"type": "equipment", "slot": "helmet", "level_req": 30, "rarity": "Zwykły",
		"base_stats": {"def": 25, "hp_max": 50}, "icon": "res://assets/items/helm_mithril.jpg"
	},
	"acc_ruby_pendant": {
		"id": "acc_ruby_pendant", "name": "Rubinowy Wisiorek",
		"description": "Pulsuje gorącą magią bojową.", "value": 25000,
		"type": "equipment", "slot": "accessory", "level_req": 30, "rarity": "Zwykły",
		"base_stats": {"atk": 20, "def": 20, "hp_max": 100}, "icon": "res://assets/items/acc_ruby_pendant.jpg"
	},

	# Tier 4 (Poziom 50)
	"wep_adamant_greatsword": {
		"id": "wep_adamant_greatsword", "name": "Adamantowy Wielki Miecz",
		"description": "Przecina najtwardsze skały i pancerze.", "value": 150000,
		"type": "equipment", "slot": "weapon", "level_req": 50, "rarity": "Zwykły",
		"base_stats": {"atk": 180}, "icon": "res://assets/items/wep_adamant_greatsword.jpg"
	},
	"arm_adamant_cuirass": {
		"id": "arm_adamant_cuirass", "name": "Adamantowa Zbroja",
		"description": "Legendarna płyta wykuta w głębinach ziemi.", "value": 200000,
		"type": "equipment", "slot": "armor", "level_req": 50, "rarity": "Zwykły",
		"base_stats": {"def": 140, "hp_max": 300}, "icon": "res://assets/items/arm_adamant_cuirass.jpg"
	},
	"helm_adamant": {
		"id": "helm_adamant", "name": "Adamantowa Korona Wojny",
		"description": "Napełnia nosiciela straszliwą potęgą.", "value": 100000,
		"type": "equipment", "slot": "helmet", "level_req": 50, "rarity": "Zwykły",
		"base_stats": {"def": 60, "hp_max": 150}, "icon": "res://assets/items/helm_adamant.jpg"
	},
	"acc_dragon_eye": {
		"id": "acc_dragon_eye", "name": "Oko Smoka",
		"description": "Starożytny artefakt emanujący mroczną energią.", "value": 180000,
		"type": "equipment", "slot": "accessory", "level_req": 50, "rarity": "Zwykły",
		"base_stats": {"atk": 50, "def": 50, "hp_max": 250}, "icon": "res://assets/items/acc_dragon_eye.jpg"
	},

	# Tier 5 (Poziom 75)
	"wep_shadow_slayer": {
		"id": "wep_shadow_slayer", "name": "Pogromca Cieni",
		"description": "Boski miecz wykuty ze skrystalizowanej gwiazdy.", "value": 1000000,
		"type": "equipment", "slot": "weapon", "level_req": 75, "rarity": "Zwykły",
		"base_stats": {"atk": 400}, "icon": "res://assets/items/wep_shadow_slayer.jpg"
	},
	"arm_dragon_scale": {
		"id": "arm_dragon_scale", "name": "Pancerz ze Smoczej Łuski",
		"description": "Absorbuje potężne uderzenia boskich bestii.", "value": 1500000,
		"type": "equipment", "slot": "armor", "level_req": 75, "rarity": "Zwykły",
		"base_stats": {"def": 320, "hp_max": 800}, "icon": "res://assets/items/arm_dragon_scale.jpg"
	},
	"helm_demon_crown": {
		"id": "helm_demon_crown", "name": "Korona Demonów",
		"description": "Płonąca aureola władcy otchłani.", "value": 800000,
		"type": "equipment", "slot": "helmet", "level_req": 75, "rarity": "Zwykły",
		"base_stats": {"def": 140, "hp_max": 400}, "icon": "res://assets/items/helm_demon_crown.jpg"
	},
	"acc_god_talisman": {
		"id": "acc_god_talisman", "name": "Talisman Boskiej Mocy",
		"description": "Absolutna potęga niebios i piekła.", "value": 1200000,
		"type": "equipment", "slot": "accessory", "level_req": 75, "rarity": "Zwykły",
		"base_stats": {"atk": 120, "def": 120, "hp_max": 600}, "icon": "res://assets/items/acc_god_talisman.jpg"
	},

	# === UNIKALNY EKWIPUNEK LEGENDARNY (NAGRODY Z ZADAŃ TOWARZYSZY) ===
	"wep_maslak": {
		"id": "wep_maslak", "name": "Święty Kij Maślaka",
		"description": "HISTORIA: Młody Maślak zgubił ten sękaty kij w Złowrogim Lesie uciekając przed pszczołami. Obrobiony słodkim lukrem z jego cukierni i żywicą, zyskał niezwykłą twardość.",
		"value": 1500, "type": "equipment", "slot": "weapon", "level_req": 1, "rarity": "Legendarny",
		"base_stats": {"atk": 16, "hp_max": 40}, "icon": "res://assets/items/wep_maslak.jpg"
	},
	"acc_eczme": {
		"id": "acc_eczme", "name": "Owijki 'PowerKeeper'",
		"description": "HISTORIA: Kłębek magicznej taśmy izolacyjnej, używanej przez Eczmego na każdym treningu. Skumulowana w niej potęga wzmacnia każde uderzenie.",
		"value": 5000, "type": "equipment", "slot": "accessory", "level_req": 10, "rarity": "Legendarny",
		"base_stats": {"atk": 25, "def": 15, "hp_max": 80}, "icon": "res://assets/items/acc_eczme.jpg"
	},
	"helm_pianek": {
		"id": "helm_pianek", "name": "Potowa Opaska Pianka",
		"description": "HISTORIA: Kultowa opaska z czoła Pianka, przesiąknięta potem z tysięcy serii martwego ciągu. Wibracje czystego pakowania budzą lęk w sercach wrogów.",
		"value": 10000, "type": "equipment", "slot": "helmet", "level_req": 20, "rarity": "Legendarny",
		"base_stats": {"def": 35, "hp_max": 150, "atk": 20}, "icon": "res://assets/items/helm_pianek.jpg"
	},
	"arm_damian": {
		"id": "arm_damian", "name": "Zbroja Mytnika Damiana",
		"description": "HISTORIA: Zbroja, w której Damian pobierał 'dobrowolne' opłaty od strażników. Wyklepana przez kowala za dławienie dłużników, nosi ślady strzał nieprzekonanych wędrowców.",
		"value": 25000, "type": "equipment", "slot": "armor", "level_req": 30, "rarity": "Legendarny",
		"base_stats": {"def": 120, "hp_max": 350, "atk": 20}, "icon": "res://assets/items/arm_damian.jpg"
	},
	"acc_domcia": {
		"id": "acc_domcia", "name": "Mistyczny Naszyjnik Domci",
		"description": "HISTORIA: Naszyjnik wypleciony z najrzadszych ziół. Podobno w środku ukryty jest skruszony magiczny kamień.",
		"value": 50000, "type": "equipment", "slot": "accessory", "level_req": 40, "rarity": "Legendarny",
		"base_stats": {"atk": 65, "def": 65, "hp_max": 450}, "icon": "res://assets/items/acc_domcia.jpg"
	},
	"wep_yomen": {
		"id": "wep_yomen", "name": "Klucz Czternastka Yomena",
		"description": "HISTORIA: Ulubione narzędzie Yomena ze ścieków. Legenda głosi, że tym kluczem dokręcił uszczelki w maszynie BeeMWe i rozłupał czaszki dziesięciu goblinów.",
		"value": 120000, "type": "equipment", "slot": "weapon", "level_req": 50, "rarity": "Legendarny",
		"base_stats": {"atk": 380, "hp_max": 350, "crit_chance": 8}, "icon": "res://assets/items/wep_yomen.jpg"
	},
	"arm_eczme": {
		"id": "arm_eczme", "name": "Nakolanniki Przeznaczenia Eczme",
		"description": "HISTORIA: Legendarne ochraniacze Eczme z meczy siatkówki w podziemiach. Pozwalały mu robić rzuty na kamienne podłoże i odbijać 5-kilowe kule bez zadrapania.",
		"value": 45000, "type": "equipment", "slot": "armor", "level_req": 30, "rarity": "Legendarny",
		"base_stats": {"def": 68, "hp_max": 140, "atk": 8}, "icon": "res://assets/items/arm_eczme.jpg"
	},

	# === NOWE LOCHY (45 - 100) ===
	"wep_fire_axe": {
		"id": "wep_fire_axe", "name": "Ognisty Topór Czeluści",
		"description": "Ocieka magmą. Z każdym uderzeniem spopiela pancerz wroga.",
		"value": 100000, "type": "equipment", "slot": "weapon", "level_req": 45, "rarity": "Legendarny",
		"base_stats": {"atk": 165, "hp_max": 100, "crit_chance": 5}, "icon": "res://assets/items/wep_adamant_greatsword.jpg"
	},
	"acc_fire_ruby": {
		"id": "acc_fire_ruby", "name": "Oko Wulkanu",
		"description": "Pulsujący klejnot wyrwany z serca wulkanu.",
		"value": 120000, "type": "equipment", "slot": "accessory", "level_req": 45, "rarity": "Legendarny",
		"base_stats": {"atk": 60, "def": 40, "hp_max": 200}, "icon": "res://assets/items/acc_ruby_pendant.jpg"
	},
	"arm_crystal": {
		"id": "arm_crystal", "name": "Kryształowy Pancerz",
		"description": "Odbija ataki magiczne z niezwykłą precyzją.",
		"value": 250000, "type": "equipment", "slot": "armor", "level_req": 60, "rarity": "Legendarny",
		"base_stats": {"def": 180, "hp_max": 350}, "icon": "res://assets/items/arm_mithril_mail.jpg"
	},
	"helm_crystal": {
		"id": "helm_crystal", "name": "Diadem Jaskini",
		"description": "Zwiększa jasność umysłu w mroku kryształowych jaskiń.",
		"value": 200000, "type": "equipment", "slot": "helmet", "level_req": 60, "rarity": "Legendarny",
		"base_stats": {"def": 85, "hp_max": 200, "atk": 25}, "icon": "res://assets/items/helm_mithril.jpg"
	},
	"wep_frost_mourne": {
		"id": "wep_frost_mourne", "name": "Mroźne Ostrze",
		"description": "Zamraża krew w żyłach każdego, kogo dotknie.",
		"value": 750000, "type": "equipment", "slot": "weapon", "level_req": 75, "rarity": "Legendarny",
		"base_stats": {"atk": 380, "hp_max": 400, "crit_chance": 10}, "icon": "res://assets/items/wep_shadow_slayer.jpg"
	},
	"acc_frost_amulet": {
		"id": "acc_frost_amulet", "name": "Amulet Wiecznej Zimy",
		"description": "Gwarantuje odporność na wszelkie skrajne temperatury.",
		"value": 800000, "type": "equipment", "slot": "accessory", "level_req": 75, "rarity": "Legendarny",
		"base_stats": {"atk": 100, "def": 100, "hp_max": 600}, "icon": "res://assets/items/acc_silver_amulet.jpg"
	},
	"arm_fallen_god": {
		"id": "arm_fallen_god", "name": "Pancerz Upadłego Boga",
		"description": "Pozostałość po dawnych stwórcach tego świata.",
		"value": 2500000, "type": "equipment", "slot": "armor", "level_req": 90, "rarity": "Mityczny",
		"base_stats": {"def": 450, "hp_max": 1200, "atk": 50}, "icon": "res://assets/items/arm_dragon_scale.jpg"
	},
	"helm_fallen_god": {
		"id": "helm_fallen_god", "name": "Aureola Zniszczenia",
		"description": "Kto ją nosi, postrzega śmiertelników jako pył.",
		"value": 1800000, "type": "equipment", "slot": "helmet", "level_req": 90, "rarity": "Mityczny",
		"base_stats": {"def": 250, "hp_max": 800, "atk": 80}, "icon": "res://assets/items/helm_demon_crown.jpg"
	},
	"wep_void_blade": {
		"id": "wep_void_blade", "name": "Ostrze Nieskończoności",
		"description": "Nie ma fizycznej formy. Rozcina samo kontinuum czasoprzestrzeni.",
		"value": 10000000, "type": "equipment", "slot": "weapon", "level_req": 100, "rarity": "Mityczny",
		"base_stats": {"atk": 1200, "hp_max": 1000, "crit_chance": 20}, "icon": "res://assets/items/wep_shadow_slayer.jpg"
	},
	"acc_void_core": {
		"id": "acc_void_core", "name": "Rdzeń Czasoprzestrzeni",
		"description": "Zatrzymuje czas wokół posiadacza.",
		"value": 12000000, "type": "equipment", "slot": "accessory", "level_req": 100, "rarity": "Mityczny",
		"base_stats": {"atk": 400, "def": 400, "hp_max": 3000}, "icon": "res://assets/items/acc_god_talisman.jpg"
	},

	# === MAGICZNE KLEJNOTY ===
	"gem_ruby": {
		"id": "gem_ruby", "name": "Rubin Siły",
		"description": "Płonący klejnot bojowy (+15 ATK w gnieździe ekwipunku).",
		"value": 600, "type": "gem", "icon": "res://assets/items/gem_ruby.jpg"
	},
	"gem_emerald": {
		"id": "gem_emerald", "name": "Szmaragd Żywotności",
		"description": "Kamień natury (+80 Max HP, +8 DEF w gnieździe ekwipunku).",
		"value": 600, "type": "gem", "icon": "res://assets/items/gem_emerald.jpg"
	},
	"gem_sapphire": {
		"id": "gem_sapphire", "name": "Szafir Prędkości",
		"description": "Kryształ niebios (+5% Szansy na Podwójny Atak w gnieździe).",
		"value": 750, "type": "gem", "icon": "res://assets/items/gem_sapphire.jpg"
	},
	"gem_topaz": {
		"id": "gem_topaz", "name": "Topaz Chciwości",
		"description": "Złocisty klejnot fortuny (+15% Złota, +5% Szansy na Łup).",
		"value": 700, "type": "gem", "icon": "res://assets/items/gem_topaz.jpg"
	},
	"gem_amethyst": {
		"id": "gem_amethyst", "name": "Ametyst Zguby",
		"description": "Klejnot magii cienia (+3% Szansy na Cios Krytyczny).",
		"value": 800, "type": "gem", "icon": "res://assets/items/gem_amethyst.jpg"
	},

	# === ZIOŁA I SKŁADNIKI ALCHEMICZNE ===
	"herb_amanita": {
		"id": "herb_amanita", "name": "Amanita Lasu",
		"description": "Czerwony grzyb leśny o właściwościach stymulujących siłę.",
		"value": 40, "type": "herb", "growth_time": 30, "icon": "res://assets/items/herb_amanita.jpg"
	},
	"herb_moss": {
		"id": "herb_moss", "name": "Srebrzysty Mech",
		"description": "Lśniący chłodny mech skalny, kluczowy do wywarów leczniczych.",
		"value": 50, "type": "herb", "growth_time": 45, "icon": "res://assets/items/herb_moss.jpg"
	},
	"herb_flower": {
		"id": "herb_flower", "name": "Krwawy Kwiat",
		"description": "Szkarłatny kwiat z zarośli o zapachu siarki i witalności.",
		"value": 60, "type": "herb", "growth_time": 60, "icon": "res://assets/items/herb_flower.jpg"
	},
	"herb_root": {
		"id": "herb_root", "name": "Smoczy Korzeń",
		"description": "Rzadki, twardy korzeń gromadzący energię ziemi i bogactwa.",
		"value": 80, "type": "herb", "growth_time": 90, "icon": "res://assets/items/herb_root.jpg"
	},
	"herb_mystery": {
		"id": "herb_mystery", "name": "Ziółko",
		"description": "Efekt nieznany. Zażycie z plecaka daje 60s mistycznej fali deformacji świata i spowolnienia czasu.",
		"value": 150, "type": "herb", "growth_time": 120, "icon": "res://assets/items/herb_mystery.jpg"
	},
	"ing_fang": {
		"id": "ing_fang", "name": "Kieł Bestii",
		"description": "Ostry kieł drapieżnika. Upuszczany przez wilki i bestie.",
		"value": 30, "type": "ingredient", "icon": "res://assets/items/ing_fang.jpg"
	},
	"ing_venom": {
		"id": "ing_venom", "name": "Gruczoł Jadowy",
		"description": "Lepki jad pająków i pełzających potworów.",
		"value": 45, "type": "ingredient", "icon": "res://assets/items/ing_venom.jpg"
	},
	"ing_ectoplasm": {
		"id": "ing_ectoplasm", "name": "Ektoplazma Upiora",
		"description": "Świetlista maź pozostająca po nieumarłych i zjawach.",
		"value": 60, "type": "ingredient", "icon": "res://assets/items/ing_ectoplasm.jpg"
	},
	"ing_core": {
		"id": "ing_core", "name": "Rdzeń Skalny",
		"description": "Ciężki, twardy fragment ożywionego golema lub gargulca.",
		"value": 75, "type": "ingredient", "icon": "res://assets/items/ing_core.jpg"
	}
}

static func get_raw_def(item_id: String) -> Dictionary:
	return ITEMS.get(item_id, {})

static func resolve_item(item_data) -> Dictionary:
	if item_data == null:
		return {}

	var item_id: String = ""
	var lvl: int = 0
	var sockets: Array = []
	var modifier: Variant = null

	if item_data is String:
		item_id = item_data
	elif item_data is Dictionary:
		item_id = item_data.get("id", "")
		lvl = item_data.get("lvl", 0)
		sockets = item_data.get("sockets", [])
		modifier = item_data.get("modifier", null)
	else:
		return {}

	if not ITEMS.has(item_id):
		return {}

	var base_def: Dictionary = ITEMS[item_id].duplicate(true)
	var resolved: Dictionary = base_def.duplicate(true)
	resolved["lvl"] = lvl
	resolved["sockets"] = sockets.duplicate(true)
	resolved["modifier"] = modifier

	# Jeśli przedmiot to sprzęt (Equipment), przeliczamy skalowane statystyki
	if resolved.get("type", "") == "equipment":
		var rarity = resolved.get("rarity", "Zwykły")
		var mult: float = 1.0
		if rarity == "Zwykły": mult = 1.0
		elif rarity == "Rzadki": mult = 1.5
		elif rarity == "Legendarny": mult = 2.5
		elif rarity == "Mityczny": mult = 4.0

		if item_id == "acc_eczme":
			mult = 1.45

		var slot = resolved.get("slot", "")
		var L: float = float(maxi(1, resolved.get("level_req", 1)))
		var scaled_stats: Dictionary = {}

		if slot == "weapon":
			scaled_stats["atk"] = int((5.0 + pow(L, 1.5)) * mult)
		elif slot == "armor":
			scaled_stats["def"] = int((5.0 + pow(L, 1.45)) * mult)
			scaled_stats["hp_max"] = int((20.0 + pow(L, 1.65)) * mult)
		elif slot == "helmet":
			scaled_stats["def"] = int((3.0 + pow(L, 1.35)) * mult)
			scaled_stats["hp_max"] = int((10.0 + pow(L, 1.55)) * mult)
		elif slot == "accessory":
			scaled_stats["atk"] = int((2.0 + pow(L, 1.4)) * mult)
			scaled_stats["def"] = int((3.0 + pow(L, 1.35)) * mult)
			scaled_stats["hp_max"] = int((10.0 + pow(L, 1.55)) * mult)

		# Zachowaj bazowe unikalne statystyki (np. crit_chance)
		var base_stats = base_def.get("base_stats", {})
		for k in base_stats.keys():
			if not scaled_stats.has(k):
				scaled_stats[k] = base_stats[k]

		# Uwzględnij poziom ulepszenia kowala (+15% bazowych statystyk za każdy poziom)
		var final_stats: Dictionary = {}
		var upg_mult: float = 1.0 + 0.15 * float(lvl)
		for k in scaled_stats.keys():
			final_stats[k] = int(float(scaled_stats[k]) * upg_mult)

		resolved["stats"] = final_stats

		# Nazwa z ulepszeniem
		if lvl > 0:
			resolved["display_name"] = "%s +%d" % [resolved["name"], lvl]
		else:
			resolved["display_name"] = resolved["name"]

	return resolved

static func get_item_name(item_id: String) -> String:
	if ITEMS.has(item_id):
		return ITEMS[item_id].get("name", item_id)
	return item_id
