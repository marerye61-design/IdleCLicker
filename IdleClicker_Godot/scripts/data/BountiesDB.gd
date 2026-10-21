class_name BountiesDB

# Tablica Ogłoszeń w Tawernie (Zlecenia na potwory i wyprawy towarzyszy)

const EXPEDITIONS_DATA: Dictionary = {
	"meadow": {
		"id": "meadow",
		"name": "Zwiady w Ziołowych Zaroślach",
		"duration": 300,
		"desc": "Zbieranie ziół, leśnych grzybów i drobnego złota.",
		"min_gold": 150,
		"max_gold": 350,
		"possible_items": ["herb_amanita", "herb_moss"]
	},
	"mine": {
		"id": "mine",
		"name": "Wyprawa do Starej Kopalni",
		"duration": 900,
		"desc": "Poszukiwanie rdzeni skalnych, rudy i magicznych klejnotów.",
		"min_gold": 500,
		"max_gold": 1200,
		"possible_items": ["ing_core", "gem_ruby", "gem_sapphire", "gem_topaz"]
	},
	"catacombs": {
		"id": "catacombs",
		"name": "Zapomniane Katakumby",
		"duration": 1800,
		"desc": "Niebezpieczna ekspedycja po ektoplazmę, jady, wielkie skarby i rzadkie zioła.",
		"min_gold": 1500,
		"max_gold": 3500,
		"possible_items": ["ing_ectoplasm", "ing_venom", "herb_flower", "herb_mystery"]
	}
}

static func generate_daily_bounties(player_level: int) -> Array:
	var lvl = maxi(1, player_level)
	var monster_pool: Array = []

	if lvl < 10:
		monster_pool = [["Słaby Goblin", 5, 8], ["Leśny Wilk", 4, 7], ["Bandyta", 4, 6]]
	elif lvl < 25:
		monster_pool = [["Wielki Pająk", 6, 10], ["Nieumarły Żołnierz", 5, 8], ["Bies", 4, 7]]
	elif lvl < 45:
		monster_pool = [["Ork Wojownik", 7, 12], ["Zjawa", 6, 10], ["Gargulec", 5, 8]]
	else:
		monster_pool = [["Mroczny Ent", 8, 14], ["Przeklęty Rycerz", 6, 10], ["Ogr Miażdżyciel", 5, 8]]

	monster_pool.shuffle()

	var m1 = monster_pool[0]
	var count1 = randi_range(m1[1], m1[2])
	var gold1 = int((lvl * 45 + 120) * (float(count1) / 5.0))
	var exp1 = int((lvl * 35 + 90) * (float(count1) / 5.0))
	var b1 = {
		"id": "bounty_1",
		"title": "Polowanie: %s" % m1[0],
		"description": "Karczmarz Barnaba poszukuje śmiałka, który przetrzebi okolicę z %sów." % m1[0].to_lower(),
		"target_type": "kill",
		"target_name": m1[0],
		"target_count": count1,
		"current_count": 0,
		"gold_reward": gold1,
		"exp_reward": exp1,
		"item_reward": null,
		"status": "AVAILABLE"
	}

	var m2 = monster_pool[1]
	var count2 = randi_range(m2[1], m2[2])
	var gold2 = int((lvl * 55 + 150) * (float(count2) / 5.0))
	var exp2 = int((lvl * 45 + 110) * (float(count2) / 5.0))
	var item2 = "pot_hp" if randf() < 0.5 else null
	var b2 = {
		"id": "bounty_2",
		"title": "Zlecenie: %s" % m2[0],
		"description": "Kupcy proszą o ochronę traktu przed napaściami %sów." % m2[0].to_lower(),
		"target_type": "kill",
		"target_name": m2[0],
		"target_count": count2,
		"current_count": 0,
		"gold_reward": gold2,
		"exp_reward": exp2,
		"item_reward": item2,
		"status": "AVAILABLE"
	}

	var b3 = {
		"id": "bounty_3",
		"title": "Wyprawa w Głąb Lochu",
		"description": "Zbadaj mroczne korytarze i przetrwaj pełną eksplorację dowolnego lochu.",
		"target_type": "dungeon",
		"target_name": "Loch",
		"target_count": 1,
		"current_count": 0,
		"gold_reward": int(lvl * 60 + 200),
		"exp_reward": int(lvl * 50 + 150),
		"item_reward": "pot_hp",
		"status": "AVAILABLE"
	}

	return [b1, b2, b3]
