class_name BuildingsDB

# Baza budynków na Rynku generujących pasywne złoto na sekundę

const BUILDINGS: Dictionary = {
	"b1": {
		"id": "b1",
		"name": "Cukiernia Maślaka",
		"description": "Produkuje lukrowane pączki i dowozi je do klasztorów. Słodki zysk!",
		"base_cost": 50,
		"gold_per_sec": 1,
		"cost_multiplier": 1.25,
		"companion": "maslak"
	},
	"b2": {
		"id": "b2",
		"name": "Strażnica Damiana",
		"description": "Damian pobiera 'dobrowolne' myto od wędrowców w zamian za ochronę.",
		"base_cost": 500,
		"gold_per_sec": 7,
		"cost_multiplier": 1.25,
		"companion": "damian"
	},
	"b3": {
		"id": "b3",
		"name": "Plantacja Ziół Domci",
		"description": "Domcia hoduje rzadkie 'magiczne' grzybki i zioła na eksport.",
		"base_cost": 3000,
		"gold_per_sec": 35,
		"cost_multiplier": 1.25,
		"companion": "domcia"
	},
	"b4": {
		"id": "b4",
		"name": "Boisko Siatkarskie Eczme",
		"description": "Eczme organizuje turnieje w lochach. Wpisowe jest wysokie, a przeżywalność niska.",
		"base_cost": 15000,
		"gold_per_sec": 140,
		"cost_multiplier": 1.25,
		"companion": "eczme"
	},
	"b5": {
		"id": "b5",
		"name": "Siłownia Pianka",
		"description": "Pianek pobiera opłaty za patrzenie, jak podnosi ciężary i krzyczy.",
		"base_cost": 50000,
		"gold_per_sec": 700,
		"cost_multiplier": 1.25,
		"companion": "pianek"
	},
	"b6": {
		"id": "b6",
		"name": "Warsztat 'BeeMWe' Yomena",
		"description": "Yomen łata pęknięte uszczelki wywarem z czaszek. Zyski z napraw są ogromne!",
		"base_cost": 250000,
		"gold_per_sec": 3500,
		"cost_multiplier": 1.25,
		"companion": "yomen"
	}
}

static func get_cost(b_id: String, current_count: int) -> int:
	if not BUILDINGS.has(b_id):
		return 0
	var b = BUILDINGS[b_id]
	return int(b["base_cost"] * pow(b["cost_multiplier"], current_count))

static func get_synergy_multiplier(b_id: String, party: Array, active_companion: Variant) -> float:
	if not BUILDINGS.has(b_id):
		return 1.0
	var comp = BUILDINGS[b_id]["companion"]
	if active_companion == comp:
		return 1.40
	elif party.has(comp):
		return 1.25
	return 1.0
