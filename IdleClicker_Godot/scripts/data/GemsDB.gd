class_name GemsDB

# Moduł Magicznych Klejnotów i Gniazd

const GEMS: Dictionary = {
	"gem_ruby": {
		"id": "gem_ruby",
		"name": "Rubin Siły",
		"color": Color("#e74c3c"),
		"description": "Płonący klejnot bojowy zwiększający obrażenia (ATK) zależnie od potęgi przedmiotu.",
		"value": 600,
		"icon": "res://assets/items/gem_ruby.jpg"
	},
	"gem_emerald": {
		"id": "gem_emerald",
		"name": "Szmaragd Żywotności",
		"color": Color("#2ecc71"),
		"description": "Głęboko zielony kamień natury, wzmacniający odporność (DEF) i maksymalne punkty życia (HP).",
		"value": 600,
		"icon": "res://assets/items/gem_emerald.jpg"
	},
	"gem_sapphire": {
		"id": "gem_sapphire",
		"name": "Szafir Prędkości",
		"color": Color("#3498db"),
		"description": "Lśniący błękitem kryształ niebios dający szansę na błyskawiczny Podwójny Atak.",
		"value": 750,
		"icon": "res://assets/items/gem_sapphire.jpg"
	},
	"gem_topaz": {
		"id": "gem_topaz",
		"name": "Topaz Chciwości",
		"color": Color("#f1c40f"),
		"description": "Złocisty kamień przyciągający dodatkowe złoto i cenniejsze łupy z wrogów.",
		"value": 700,
		"icon": "res://assets/items/gem_topaz.jpg"
	},
	"gem_amethyst": {
		"id": "gem_amethyst",
		"name": "Ametyst Zguby",
		"color": Color("#9b59b6"),
		"description": "Mroczny fioletowy klejnot nasycony magią cienia, podnoszący szansę na trafienia krytyczne.",
		"value": 800,
		"icon": "res://assets/items/gem_amethyst.jpg"
	}
}

static func get_gem(gem_id: String) -> Dictionary:
	return GEMS.get(gem_id, {})

static func get_stats_for_level(gem_id: String, item_level_req: int = 1) -> Dictionary:
	var L: float = float(maxi(1, item_level_req))
	var stats: Dictionary = {}
	match gem_id:
		"gem_ruby":
			stats["atk"] = 4 + int(L * 0.45)
		"gem_emerald":
			stats["hp_max"] = 25 + int(L * 3.5)
			stats["def"] = 3 + int(L * 0.35)
		"gem_sapphire":
			stats["double_strike_pct"] = mini(15, 3 + int(L / 25.0))
		"gem_amethyst":
			stats["crit_chance"] = mini(12, 2 + int(L / 30.0))
		"gem_topaz":
			stats["bonus_gold_pct"] = mini(40, 10 + int(L / 10.0))
			stats["bonus_loot_pct"] = mini(20, 3 + int(L / 25.0))
	return stats

static func get_stat_summary(gem_id: String, item_level_req: int = 1) -> String:
	var s: Dictionary = get_stats_for_level(gem_id, item_level_req)
	var parts: Array = []
	if s.has("atk"): parts.append("+%d ATK" % s["atk"])
	if s.has("def"): parts.append("+%d DEF" % s["def"])
	if s.has("hp_max"): parts.append("+%d HP" % s["hp_max"])
	if s.has("crit_chance"): parts.append("+%d%% Kryt" % s["crit_chance"])
	if s.has("double_strike_pct"): parts.append("+%d%% Podwójny Cios" % s["double_strike_pct"])
	if s.has("bonus_gold_pct"): parts.append("+%d%% Złoto" % s["bonus_gold_pct"])
	if s.has("bonus_loot_pct"): parts.append("+%d%% Szansa na Łup" % s["bonus_loot_pct"])
	return ", ".join(parts)

static func roll_gem_drop(is_boss: bool = false, player_level: int = 1) -> Variant:
	var base_chance = 0.10 if is_boss else 0.03
	if not is_boss and player_level < 15:
		return null
	if randf() <= base_chance:
		var gem_keys = GEMS.keys()
		return gem_keys[randi() % gem_keys.size()]
	return null
