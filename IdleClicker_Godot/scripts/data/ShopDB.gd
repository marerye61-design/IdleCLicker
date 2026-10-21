class_name ShopDB

# Baza asortymentu Sklepu Fantasy (dokładny port shop.py)

const TIERS: Dictionary = {
	0: {
		"name": "Alchemik",
		"label": "Mikstury",
		"req_level": 1,
		"items": ["pot_hp", "pot_mana"]
	},
	1: {
		"name": "Zestaw Nowicjusza",
		"label": "Poz. 1 - 5",
		"req_level": 1,
		"items": ["wep_wooden_club", "arm_leather", "helm_leather", "acc_ring_small"]
	},
	2: {
		"name": "Zestaw Żelazny",
		"label": "Poz. 5 - 15",
		"req_level": 5,
		"items": ["wep_iron_sword", "arm_iron_plate", "helm_iron", "acc_iron_ring"]
	},
	3: {
		"name": "Zestaw Stalowy",
		"label": "Poz. 15 - 30",
		"req_level": 15,
		"items": ["wep_steel_sword", "arm_steel_plate", "helm_steel", "acc_silver_amulet"]
	},
	4: {
		"name": "Zestaw Mithrilowy",
		"label": "Poz. 30 - 50",
		"req_level": 30,
		"items": ["wep_mithril_blade", "arm_mithril_mail", "helm_mithril", "acc_ruby_pendant"]
	},
	5: {
		"name": "Zestaw Adamantowy",
		"label": "Poz. 50 - 75",
		"req_level": 50,
		"items": ["wep_adamant_greatsword", "arm_adamant_cuirass", "helm_adamant", "acc_dragon_eye"]
	},
	6: {
		"name": "Zestaw Boski",
		"label": "Poz. 75+",
		"req_level": 75,
		"items": ["wep_shadow_slayer", "arm_dragon_scale", "helm_demon_crown", "acc_god_talisman"]
	}
}

static func get_item_price(item_id: String, player_level: int) -> int:
	if item_id == "pot_hp":
		return int(50.0 + pow(float(player_level), 1.3) * 15.0)
	elif item_id == "pot_mana":
		return int(40.0 + pow(float(player_level), 1.2) * 10.0)

	var item = ItemsDB.ITEMS.get(item_id, {})
	return item.get("value", 100)
