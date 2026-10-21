class_name EnemiesDB

# Baza danych wrogów, szablonów, afiksów elitarnych oraz bossów

const ELITE_AFFIXES: Dictionary = {
	"flame": {
		"name": "Płonący",
		"hp_mult": 1.25,
		"atk_mult": 1.35,
		"def_mult": 1.0,
		"gold_mult": 2.0,
		"exp_mult": 2.0,
		"desc": "+35% do ATK i podwójne nagrody!"
	},
	"armored": {
		"name": "Pancerny",
		"hp_mult": 1.5,
		"atk_mult": 1.0,
		"def_mult": 1.8,
		"gold_mult": 2.2,
		"exp_mult": 2.0,
		"desc": "+80% do DEF, +50% HP i potężny łup!"
	},
	"golden": {
		"name": "Złocisty Złodziej",
		"hp_mult": 1.2,
		"atk_mult": 1.1,
		"def_mult": 1.0,
		"gold_mult": 4.0,
		"exp_mult": 1.5,
		"desc": "Niesie ogromny skarb: 4x WIĘCEJ ZŁOTA!"
	},
	"ancient": {
		"name": "Pradawny",
		"hp_mult": 1.6,
		"atk_mult": 1.25,
		"def_mult": 1.3,
		"gold_mult": 2.5,
		"exp_mult": 3.5,
		"desc": "Mityczna bestia dająca 3.5x WIĘCEJ EXP!"
	}
}

const TEMPLATES: Array = [
	# Wczesna faza (Poziomy 1 - 10)
	{"id": "e_goblin", "name": "Słaby Goblin", "base_hp": 34, "hp_per_lvl": 4.5, "base_atk": 7.0, "atk_per_lvl": 1.4, "base_def": 2, "def_per_lvl": 0.4, "img_key": "e_goblin", "min_level": 1},
	{"id": "e_wolf", "name": "Leśny Wilk", "base_hp": 42, "hp_per_lvl": 5.0, "base_atk": 8.0, "atk_per_lvl": 1.5, "base_def": 2, "def_per_lvl": 0.4, "img_key": "e_wolf", "min_level": 1},
	{"id": "e_bandit", "name": "Bandyta", "base_hp": 52, "hp_per_lvl": 5.5, "base_atk": 9.0, "atk_per_lvl": 1.6, "base_def": 3, "def_per_lvl": 0.5, "img_key": "e_bandit", "min_level": 2},
	{"id": "e_spider", "name": "Wielki Pająk", "base_hp": 62, "hp_per_lvl": 6.0, "base_atk": 10.0, "atk_per_lvl": 1.8, "base_def": 3, "def_per_lvl": 0.6, "img_key": "e_spider", "min_level": 3},

	# Środkowa faza (Poziomy 10 - 25)
	{"id": "e_undead", "name": "Nieumarły Żołnierz", "base_hp": 90, "hp_per_lvl": 8.5, "base_atk": 16.0, "atk_per_lvl": 2.2, "base_def": 6, "def_per_lvl": 1.0, "img_key": "e_undead", "min_level": 8},
	{"id": "e_fiend", "name": "Bies", "base_hp": 110, "hp_per_lvl": 9.5, "base_atk": 18.0, "atk_per_lvl": 2.4, "base_def": 7, "def_per_lvl": 1.1, "img_key": "e_fiend", "min_level": 12},
	{"id": "e_orc", "name": "Ork Wojownik", "base_hp": 135, "hp_per_lvl": 11.0, "base_atk": 22.0, "atk_per_lvl": 2.8, "base_def": 8, "def_per_lvl": 1.2, "img_key": "e_orc", "min_level": 15},
	{"id": "e_wraith", "name": "Zjawa", "base_hp": 125, "hp_per_lvl": 10.5, "base_atk": 25.0, "atk_per_lvl": 3.0, "base_def": 7, "def_per_lvl": 1.1, "img_key": "e_wraith", "min_level": 18},

	# Zaawansowana faza (Poziomy 25 - 50)
	{"id": "e_gargoyle", "name": "Gargulec", "base_hp": 240, "hp_per_lvl": 15.0, "base_atk": 42.0, "atk_per_lvl": 3.6, "base_def": 14, "def_per_lvl": 1.8, "img_key": "e_gargoyle", "min_level": 25},
	{"id": "e_treant", "name": "Mroczny Ent", "base_hp": 300, "hp_per_lvl": 18.0, "base_atk": 38.0, "atk_per_lvl": 3.4, "base_def": 18, "def_per_lvl": 2.0, "img_key": "e_treant", "min_level": 30},
	{"id": "e_knight", "name": "Przeklęty Rycerz", "base_hp": 280, "hp_per_lvl": 16.0, "base_atk": 48.0, "atk_per_lvl": 4.0, "base_def": 20, "def_per_lvl": 2.2, "img_key": "e_knight", "min_level": 35},

	# Pół-bossowie (Poziomy 50 - 75)
	{"id": "e_ogre", "name": "Ogr Miażdżyciel", "base_hp": 520, "hp_per_lvl": 24.0, "base_atk": 85.0, "atk_per_lvl": 5.0, "base_def": 30, "def_per_lvl": 2.8, "img_key": "e_ogre", "min_level": 45},
	{"id": "e_cultist", "name": "Mroczny Kultysta", "base_hp": 460, "hp_per_lvl": 22.0, "base_atk": 95.0, "atk_per_lvl": 5.5, "base_def": 25, "def_per_lvl": 2.5, "img_key": "e_cultist", "min_level": 50},

	# Bossowie End-game (Poziomy 75+)
	{"id": "e_golem", "name": "Golem Ziemi", "base_hp": 900, "hp_per_lvl": 35.0, "base_atk": 160.0, "atk_per_lvl": 7.0, "base_def": 55, "def_per_lvl": 4.0, "img_key": "e_golem", "min_level": 70},
	{"id": "e_dragon", "name": "Smok Cienia", "base_hp": 1300, "hp_per_lvl": 48.0, "base_atk": 210.0, "atk_per_lvl": 8.8, "base_def": 65, "def_per_lvl": 4.5, "img_key": "e_dragon", "min_level": 85}
]

static func get_portrait_path(img_key: String) -> String:
	var candidates: Array = [
		"res://assets/portraits/%s.jpg" % img_key,
		"res://assets/%s.jpg" % img_key,
		"res://assets/portraits/%s.png" % img_key,
		"res://assets/%s.png" % img_key
	]
	for p in candidates:
		if ResourceLoader.exists(p):
			return p
	return "res://assets/portraits/hero.jpg"

static func generate_enemy(template: Dictionary, level: int, force_elite: Variant = null) -> Dictionary:
	var boss_mult: float = 1.0
	if template["id"].find("boss") != -1:
		boss_mult = 2.5

	var L: float = float(level)
	var hp: int = int((template["base_hp"] + pow(L, 1.42) * template["hp_per_lvl"]) * boss_mult)
	var atk: int = int((template["base_atk"] + pow(L, 1.42) * template["atk_per_lvl"]) * boss_mult)
	var defence: int = int((template["base_def"] + pow(L, 1.42) * template["def_per_lvl"]) * boss_mult)

	var exp_reward: int = maxi(1, int((hp * 0.2 + atk * 0.5) * (10.0 if boss_mult > 1.0 else 1.0)))
	var gold_reward: int = maxi(1, int((hp * 0.1 + atk * 0.2) * (10.0 if boss_mult > 1.0 else 1.0)))

	var is_elite: bool = false
	var affix_key: Variant = null
	var affix_label: String = ""
	var enemy_name: String = template["name"]

	if template["id"].find("boss") == -1:
		var should_be_elite: bool = false
		if force_elite == true:
			should_be_elite = true
		elif force_elite == false:
			should_be_elite = false
		else:
			should_be_elite = (randf() < 0.20)

		if should_be_elite:
			is_elite = true
			var keys = ELITE_AFFIXES.keys()
			affix_key = keys[randi() % keys.size()]
			var aff = ELITE_AFFIXES[affix_key]
			hp = int(hp * aff["hp_mult"])
			atk = int(atk * aff["atk_mult"])
			defence = int(defence * aff["def_mult"])
			gold_reward = int(gold_reward * aff["gold_mult"])
			exp_reward = int(exp_reward * aff["exp_mult"])
			enemy_name = "[%s] %s" % [aff["name"], template["name"]]
			affix_label = aff["desc"]

	return {
		"id": template["id"],
		"template_id": template["id"],
		"name": enemy_name,
		"base_name": template["name"],
		"level": level,
		"hp": hp,
		"max_hp": hp,
		"atk": atk,
		"defence": defence,
		"exp_reward": exp_reward,
		"gold_reward": gold_reward,
		"img_key": template["img_key"],
		"portrait_path": get_portrait_path(template["img_key"]),
		"is_elite": is_elite,
		"affix": affix_key,
		"affix_label": affix_label
	}

static func get_expedition_choices(player_level: int, count: int = 3) -> Array:
	var available: Array = []
	for t in TEMPLATES:
		if player_level >= (t["min_level"] - 5):
			available.append(t)
	if available.is_empty():
		available.append(TEMPLATES[0])

	var choices: Array = []
	for i in range(count):
		var template = available[randi() % available.size()]
		var min_lvl = maxi(1, player_level - 5)
		var max_lvl = player_level + 5
		var lvl = randi_range(min_lvl, max_lvl)
		choices.append(generate_enemy(template, lvl))

	choices.sort_custom(func(a, b): return a["level"] < b["level"])
	return choices

static func get_hardcoded_boss(boss_id: String, player_level: int) -> Dictionary:
	var lvl = maxi(1, player_level)
	var e: Dictionary = {}
	match boss_id:
		"boss_ptys":
			e = {
				"id": boss_id, "name": "[BOSS] Giga Ork 'Ptyś'", "level": lvl,
				"hp": 1850 + (lvl * 45), "max_hp": 1850 + (lvl * 45),
				"atk": 42 + int(lvl * 2.0), "defence": 18,
				"exp_reward": 2500, "gold_reward": 1000,
				"img_key": "boss_ptys", "is_elite": false, "affix": null, "affix_label": ""
			}
		"boss_kollman":
			e = {
				"id": boss_id, "name": "[BOSS] Kollman 'Wojowniczy Mag'", "level": lvl,
				"hp": 5200 + (lvl * 90), "max_hp": 5200 + (lvl * 90),
				"atk": 95 + int(lvl * 3.0), "defence": 40,
				"exp_reward": 7500, "gold_reward": 3000,
				"img_key": "boss_kollman", "is_elite": false, "affix": null, "affix_label": ""
			}
		"boss_wraith_lord":
			e = {
				"id": boss_id, "name": "[BOSS] Władca Cieni 'Morgar'", "level": lvl,
				"hp": 14000 + (lvl * 180), "max_hp": 14000 + (lvl * 180),
				"atk": 180 + int(lvl * 4.5), "defence": 80,
				"exp_reward": 20000, "gold_reward": 8000,
				"img_key": "e_wraith", "is_elite": false, "affix": null, "affix_label": ""
			}
		"boss_magma_lord":
			e = {
				"id": boss_id, "name": "[BOSS] Władca Magmy 'Ignis'", "level": lvl,
				"hp": 32000 + (lvl * 300), "max_hp": 32000 + (lvl * 300),
				"atk": 340 + int(lvl * 6.0), "defence": 150,
				"exp_reward": 55000, "gold_reward": 22000,
				"img_key": "e_fiend", "is_elite": false, "affix": null, "affix_label": ""
			}
		"boss_crystal_golem":
			e = {
				"id": boss_id, "name": "[BOSS] Kryształowy Kolos", "level": lvl,
				"hp": 75000 + (lvl * 500), "max_hp": 75000 + (lvl * 500),
				"atk": 600 + int(lvl * 7.5), "defence": 280,
				"exp_reward": 180000, "gold_reward": 60000,
				"img_key": "e_golem", "is_elite": false, "affix": null, "affix_label": ""
			}
		"boss_frost_lich":
			e = {
				"id": boss_id, "name": "[BOSS] Mroźny Licz 'Kel-Thuzar'", "level": lvl,
				"hp": 175000 + (lvl * 800), "max_hp": 175000 + (lvl * 800),
				"atk": 1050 + int(lvl * 10.0), "defence": 450,
				"exp_reward": 500000, "gold_reward": 150000,
				"img_key": "e_cultist", "is_elite": false, "affix": null, "affix_label": ""
			}
		"boss_fallen_avatar":
			e = {
				"id": boss_id, "name": "[BOSS] Awatar Upadłego Bóstwa", "level": lvl,
				"hp": 400000 + (lvl * 1500), "max_hp": 400000 + (lvl * 1500),
				"atk": 1950 + int(lvl * 15.0), "defence": 800,
				"exp_reward": 1500000, "gold_reward": 400000,
				"img_key": "e_knight", "is_elite": false, "affix": null, "affix_label": ""
			}
		"boss_void_emperor":
			e = {
				"id": boss_id, "name": "[BOSS] Cesarz Czasoprzestrzeni", "level": lvl,
				"hp": 950000 + (lvl * 3000), "max_hp": 950000 + (lvl * 3000),
				"atk": 3800 + int(lvl * 22.0), "defence": 1350,
				"exp_reward": 4000000, "gold_reward": 1200000,
				"img_key": "e_dragon", "is_elite": false, "affix": null, "affix_label": ""
			}
		_:
			e = {
				"id": "unknown_boss", "name": "[BOSS] Nieznany Byt", "level": lvl,
				"hp": 1500 + lvl * 50, "max_hp": 1500 + lvl * 50,
				"atk": 40 + lvl * 3, "defence": 18 + lvl,
				"exp_reward": 500, "gold_reward": 250,
				"img_key": "e_golem", "is_elite": false, "affix": null, "affix_label": ""
			}
	e["template_id"] = e["id"]
	e["base_name"] = e["name"]
	e["portrait_path"] = get_portrait_path(e["img_key"])
	return e
