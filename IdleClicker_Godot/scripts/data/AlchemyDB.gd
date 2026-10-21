class_name AlchemyDB

# Moduł Ogród Ziół u Domci i Warzenie Mikstur w Kociołku

const HERBS: Dictionary = {
	"herb_amanita": {
		"id": "herb_amanita",
		"name": "Amanita Lasu",
		"color": Color("#e67e22"),
		"description": "Czerwony grzyb leśny o właściwościach stymulujących siłę i agresję.",
		"growth_time": 30,
		"value": 40,
		"icon": "res://assets/items/herb_amanita.jpg"
	},
	"herb_moss": {
		"id": "herb_moss",
		"name": "Srebrzysty Mech",
		"color": Color("#2ecc71"),
		"description": "Lśniący chłodny mech skalny, kluczowy do wywarów leczniczych i ochronnych.",
		"growth_time": 45,
		"value": 50,
		"icon": "res://assets/items/herb_moss.jpg"
	},
	"herb_flower": {
		"id": "herb_flower",
		"name": "Krwawy Kwiat",
		"color": Color("#e74c3c"),
		"description": "Szkarłatny kwiat z zarośli o zapachu siarki i witalności.",
		"growth_time": 60,
		"value": 60,
		"icon": "res://assets/items/herb_flower.jpg"
	},
	"herb_root": {
		"id": "herb_root",
		"name": "Smoczy Korzeń",
		"color": Color("#f1c40f"),
		"description": "Rzadki, twardy korzeń gromadzący energię ziemi i bogactwa.",
		"growth_time": 90,
		"value": 80,
		"icon": "res://assets/items/herb_root.jpg"
	},
	"herb_mystery": {
		"id": "herb_mystery",
		"name": "Ziółko",
		"color": Color("#9b59b6"),
		"description": "Mistyczna roślina o niezwykłym aromacie. (Można zażyć z ekwipunku lub uwarzyć w kociołku)",
		"growth_time": 120,
		"value": 150,
		"icon": "res://assets/items/herb_mystery.jpg"
	}
}

const MONSTER_INGREDIENTS: Dictionary = {
	"ing_fang": {
		"id": "ing_fang",
		"name": "Kieł Bestii",
		"color": Color("#dcdde1"),
		"description": "Ostry kieł drapieżnika. Upuszczany przez wilki i dzikie bestie.",
		"value": 30,
		"icon": "res://assets/items/ing_fang.jpg"
	},
	"ing_venom": {
		"id": "ing_venom",
		"name": "Gruczoł Jadowy",
		"color": Color("#8c7ae6"),
		"description": "Lepki jad pająków i pełzających potworów.",
		"value": 45,
		"icon": "res://assets/items/ing_venom.jpg"
	},
	"ing_ectoplasm": {
		"id": "ing_ectoplasm",
		"name": "Ektoplazma Upiora",
		"color": Color("#00d2d3"),
		"description": "Świetlista maź pozostająca po nieumarłych i zjawach.",
		"value": 60,
		"icon": "res://assets/items/ing_ectoplasm.jpg"
	},
	"ing_core": {
		"id": "ing_core",
		"name": "Rdzeń Skalny",
		"color": Color("#e15f41"),
		"description": "Ciężki, twardy fragment ożywionego golema lub gargulca.",
		"value": 75,
		"icon": "res://assets/items/ing_core.jpg"
	}
}

const RECIPES: Dictionary = {
	"elixir_berserk": {
		"id": "elixir_berserk",
		"name": "Eliksir Berserkera",
		"color": Color("#e74c3c"),
		"description": "+35% do całkowitych Obrażeń Bohatera na 10 kolejnych walk.",
		"ingredients": {"herb_amanita": 2, "ing_fang": 1},
		"duration_fights": 10,
		"buff_type": "atk_pct",
		"buff_val": 35
	},
	"elixir_stone_skin": {
		"id": "elixir_stone_skin",
		"name": "Mikstura Kamiennej Skóry",
		"color": Color("#7f8c8d"),
		"description": "+35% do Pancerza (DEF) na 10 kolejnych walk.",
		"ingredients": {"herb_moss": 2, "ing_core": 1},
		"duration_fights": 10,
		"buff_type": "def_pct",
		"buff_val": 35
	},
	"elixir_swiftness": {
		"id": "elixir_swiftness",
		"name": "Wywar Szybkich Stóp",
		"color": Color("#3498db"),
		"description": "+15% Szansy na Podwójny Cios na 10 kolejnych walk.",
		"ingredients": {"herb_flower": 2, "ing_venom": 1},
		"duration_fights": 10,
		"buff_type": "double_strike_pct",
		"buff_val": 15
	},
	"elixir_fortune": {
		"id": "elixir_fortune",
		"name": "Napar Złotego Rogu",
		"color": Color("#f1c40f"),
		"description": "+40% Złota z pokonanych potworów na 10 kolejnych walk.",
		"ingredients": {"herb_root": 1, "herb_moss": 2},
		"duration_fights": 10,
		"buff_type": "bonus_gold_pct",
		"buff_val": 40
	},
	"elixir_full_heal": {
		"id": "elixir_full_heal",
		"name": "Mikstura Pełnego Zdrowia",
		"color": Color("#2ecc71"),
		"description": "Darmowa mikstura lecznicza (dodaje 1 szt. do ekwipunku).",
		"ingredients": {"herb_amanita": 1, "herb_moss": 1},
		"is_item_reward": "pot_hp"
	},
	"elixir_psychedelic": {
		"id": "elixir_psychedelic",
		"name": "Ziółko (Mocny Wywar)",
		"color": Color("#9b59b6"),
		"description": "Zażycie wywołuje mistyczną falę, dając +50% Szansy na Trafienie Krytyczne na 10 kolejnych walk!",
		"ingredients": {"herb_mystery": 1, "ing_ectoplasm": 1},
		"duration_fights": 10,
		"buff_type": "psychedelic_slowmo",
		"buff_val": 50
	}
}

static func roll_monster_ingredient_drop(enemy_name: String) -> Variant:
	var e_low = enemy_name.to_lower()
	var r = randf()
	if e_low.find("wilk") != -1 or e_low.find("ogar") != -1 or e_low.find("besti") != -1:
		if r < 0.35: return "ing_fang"
	elif e_low.find("pajak") != -1 or e_low.find("pająk") != -1:
		if r < 0.35: return "ing_venom"
	elif e_low.find("upior") != -1 or e_low.find("upiór") != -1 or e_low.find("szkielet") != -1 or e_low.find("zjaw") != -1 or e_low.find("demon") != -1:
		if r < 0.30: return "ing_ectoplasm"
	elif e_low.find("golem") != -1 or e_low.find("gargulec") != -1 or e_low.find("troll") != -1:
		if r < 0.30: return "ing_core"
	elif r < 0.15:
		var keys = MONSTER_INGREDIENTS.keys()
		return keys[randi() % keys.size()]
	return null
