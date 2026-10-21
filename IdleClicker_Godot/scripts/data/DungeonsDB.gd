class_name DungeonsDB

# Baza danych lochów podziemnych i ich bossów

const DUNGEONS: Array = [
	{
		"id": "d1", "name": "Złowrogi Las", "level_req": 5, "duration": 40,
		"exp_reward": 500, "gold_reward": 250,
		"drop_pool": ["wep_maslak", "helm_pianek"],
		"boss_id": "boss_ptys", "bg_image": "res://assets/dungeon_d1_bg.jpg"
	},
	{
		"id": "d2", "name": "Górska Przełęcz", "level_req": 15, "duration": 50,
		"exp_reward": 2500, "gold_reward": 1000,
		"drop_pool": ["arm_damian", "acc_domcia"],
		"boss_id": "boss_kollman", "bg_image": "res://assets/dungeon_d2_bg.jpg"
	},
	{
		"id": "d3", "name": "Twierdza Cieni", "level_req": 30, "duration": 60,
		"exp_reward": 12000, "gold_reward": 5000,
		"drop_pool": ["wep_yomen", "arm_eczme"],
		"boss_id": "boss_wraith_lord", "bg_image": "res://assets/dungeon_d3_bg.jpg"
	},
	{
		"id": "d4", "name": "Wulkaniczne Czeluście", "level_req": 45, "duration": 60,
		"exp_reward": 45000, "gold_reward": 18000,
		"drop_pool": ["wep_fire_axe", "acc_fire_ruby"],
		"boss_id": "boss_magma_lord", "bg_image": "res://assets/dungeon_bg.jpg"
	},
	{
		"id": "d5", "name": "Kryształowe Jaskinie", "level_req": 60, "duration": 60,
		"exp_reward": 150000, "gold_reward": 50000,
		"drop_pool": ["arm_crystal", "helm_crystal"],
		"boss_id": "boss_crystal_golem", "bg_image": "res://assets/dungeon_bg.jpg"
	},
	{
		"id": "d6", "name": "Zamarznięta Pustka", "level_req": 75, "duration": 60,
		"exp_reward": 400000, "gold_reward": 120000,
		"drop_pool": ["wep_frost_mourne", "acc_frost_amulet"],
		"boss_id": "boss_frost_lich", "bg_image": "res://assets/dungeon_bg.jpg"
	},
	{
		"id": "d7", "name": "Świątynia Upadłych Bogów", "level_req": 90, "duration": 60,
		"exp_reward": 1200000, "gold_reward": 350000,
		"drop_pool": ["arm_fallen_god", "helm_fallen_god"],
		"boss_id": "boss_fallen_avatar", "bg_image": "res://assets/dungeon_bg.jpg"
	},
	{
		"id": "d8", "name": "Wymiar Czasoprzestrzeni", "level_req": 100, "duration": 60,
		"exp_reward": 3500000, "gold_reward": 1000000,
		"drop_pool": ["wep_void_blade", "acc_void_core"],
		"boss_id": "boss_void_emperor", "bg_image": "res://assets/dungeon_bg.jpg"
	}
]
