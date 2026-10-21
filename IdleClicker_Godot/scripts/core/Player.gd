class_name Player
extends RefCounted

signal stats_changed
signal gold_changed(new_gold: int)
signal hp_changed(cur_hp: int, max_hp: int)
signal level_up(new_lvl: int)

var name: String = "Bohater"
var gold: int = 0
var mana: int = 100
var max_mana: int = 100
var hp: int = 85
var max_hp: int = 85

var level: int = 1
var exp: int = 0
var stat_points: int = 0
var talent_points: int = 0
var talents: Dictionary = {"berserker": 0, "defender": 0, "rogue": 0}

var inventory: Array = []
var inventory_stash: Array = []
var equipment: Dictionary = {
	"weapon": null,
	"armor": null,
	"helmet": null,
	"accessory": null
}

var stats: Dictionary = {
	"total_clicks": 0,
	"base_atk": 8,
	"base_def": 4,
	"gold_per_click": 1,
	"gold_per_sec": 0,
	"mana_regen": 1,
	"bonus_loot_pct": 0,
	"crit_chance": 0
}

var party: Array = [] # Lista odblokowanych towarzyszy (np. ["maslak", "damian"])
var active_companion: Variant = null # ID 1 aktywnego towarzysza w walce

var quests: Array = []
var buildings: Dictionary = {}
var bestiary: Dictionary = {}
var dungeon_tickets: int = 3
var max_dungeon_tickets: int = 3

var achievements: Dictionary = {}
var permanent_perks: Array = []
var achievement_stats: Dictionary = {
	"total_kills": 0,
	"total_crits": 0,
	"boss_ptys_kills": 0,
	"boss_kollman_kills": 0,
	"dungeons_cleared": 0,
	"upgrades_done": 0,
	"max_upgrade_level": 0,
	"gems_socketed": 0,
	"herbs_harvested": 0,
	"potions_brewed": 0,
	"psychedelic_brewed": 0,
	"total_gold_earned": 0,
	"party_count": 0
}

var herb_garden: Array = [
	{"type": "herb_amanita", "planted_at": 0.0, "growth_time": 30, "unlocked": false},
	{"type": "herb_moss", "planted_at": 0.0, "growth_time": 45, "unlocked": false},
	{"type": "herb_flower", "planted_at": 0.0, "growth_time": 60, "unlocked": false},
	{"type": "herb_mystery", "planted_at": 0.0, "growth_time": 120, "unlocked": false}
]
var garden_plot_0_leased: bool = false

var active_buffs: Dictionary = {} # {buff_id: remaining_fights}
var combat_shield: int = 0
var expeditions: Dictionary = {} # {comp_id: {"exp_type": ..., "start_time": ..., "duration": ...}}
var seen_cinematics: Dictionary = {}
var last_update_time: float = 0.0

func _init(init_name: String = "Bohater"):
	name = init_name
	last_update_time = Time.get_unix_time_from_system()
	for i in range(5):
		inventory.append({"id": "pot_hp", "lvl": 0})
	quests = QuestsDB.get_all_quests_init()
	for plot in herb_garden:
		plot["planted_at"] = Time.get_unix_time_from_system()

func get_exp_required() -> int:
	return int(70.0 * pow(float(level), 1.92))

func add_exp(amount: int):
	if permanent_perks.has("perk_exp_master"):
		amount = int(amount * 1.05)
	exp += amount
	var req = get_exp_required()
	while exp >= req:
		exp -= req
		level += 1
		stat_points += 3
		if level >= 10 and level % 5 == 0:
			talent_points += 1
		# Pasywny wzrost HP przy awansie
		hp = mini(get_max_hp(), hp + 6)
		update_quests_status()
		level_up.emit(level)
		stats_changed.emit()
		req = get_exp_required()

func get_bestiary_bonus() -> float:
	var total_kills = 0
	for count in bestiary.values():
		total_kills += count
	var bonus = float(total_kills / 50) * 0.01
	return minf(1.0, bonus)

func get_party_bonus() -> Dictionary:
	var b_atk = 0
	var b_def = 0
	var b_hp = 0

	match active_companion:
		"maslak":
			b_atk += int(10 + level * 2.0)
			b_hp += int(20 + level * 3.0)
		"damian":
			b_def += int(15 + level * 1.8)
			b_hp += int(40 + level * 4.0)
		"eczme":
			b_atk += int(20 + level * 3.0)
		"pianek":
			b_def += int(25 + level * 2.5)
			b_hp += int(60 + level * 5.0)
		"yomen":
			b_atk += int(15 + level * 2.2)
			b_def += int(10 + level * 1.2)
		"domcia":
			b_atk += int(10 + level * 1.5)
			b_hp += int(35 + level * 3.5)

	if permanent_perks.has("perk_party_synergy"):
		b_atk = int(b_atk * 1.10)
		b_def = int(b_def * 1.10)
		b_hp = int(b_hp * 1.10)

	return {"atk": b_atk, "def": b_def, "hp": b_hp}

func get_gems_bonus() -> Dictionary:
	var gem_mult = 1.10 if permanent_perks.has("perk_gem_resonance") else 1.0
	var bonus = {
		"atk": 0, "def": 0, "hp_max": 0, "crit_chance": 0,
		"double_strike_pct": 0, "bonus_gold_pct": 0, "bonus_loot_pct": 0
	}

	for item_dict in equipment.values():
		if item_dict != null and item_dict.has("sockets"):
			var resolved = ItemsDB.resolve_item(item_dict)
			var item_lvl = resolved.get("level_req", 1)
			for gem_id in item_dict["sockets"]:
				if gem_id != null and gem_id != "":
					var scaled_stats = GemsDB.get_stats_for_level(gem_id, item_lvl)
					for s_key in scaled_stats.keys():
						if bonus.has(s_key):
							bonus[s_key] += int(float(scaled_stats[s_key]) * gem_mult)
	return bonus

func get_total_atk() -> int:
	var atk = stats.get("base_atk", 8) + int(float(level - 1) * 1.2)
	for item_dict in equipment.values():
		if item_dict != null:
			var resolved = ItemsDB.resolve_item(item_dict)
			var item_stats = resolved.get("stats", {})
			atk += item_stats.get("atk", 0)

	atk += get_party_bonus()["atk"]
	atk += get_gems_bonus()["atk"]

	var atk_mult: float = 1.0 + get_bestiary_bonus()
	if permanent_perks.has("perk_slayer"):
		atk_mult += 0.05
	if active_buffs.get("elixir_berserk", 0) > 0:
		atk_mult += 0.35

	return int(float(atk) * atk_mult)

func get_total_def() -> int:
	var df = stats.get("base_def", 4) + int(float(level - 1) * 0.6)
	for item_dict in equipment.values():
		if item_dict != null:
			var resolved = ItemsDB.resolve_item(item_dict)
			var item_stats = resolved.get("stats", {})
			df += item_stats.get("def", 0)

	df += get_party_bonus()["def"]
	df += get_gems_bonus()["def"]

	# Pasywka Pianka: "Żelazna Pompa" (+25% DEF gdy HP < 60%)
	if active_companion == "pianek" and get_max_hp() > 0:
		if float(hp) / float(get_max_hp()) < 0.60:
			df = int(df * 1.25)

	if active_buffs.get("elixir_stone_skin", 0) > 0:
		df = int(df * 1.35)

	return df

func get_total_crit() -> int:
	var crit = mini(30, stats.get("crit_chance", 0))
	for item_dict in equipment.values():
		if item_dict != null:
			var resolved = ItemsDB.resolve_item(item_dict)
			var item_stats = resolved.get("stats", {})
			crit += item_stats.get("crit_chance", 0)

	crit += get_gems_bonus()["crit_chance"]

	if permanent_perks.has("perk_crit_master"):
		crit += 3
	if active_buffs.get("elixir_psychedelic", 0) > 0:
		crit += 50

	return crit

func get_max_hp() -> int:
	var total_hp = max_hp + int(float(level - 1) * 6.0)
	for item_dict in equipment.values():
		if item_dict != null:
			var resolved = ItemsDB.resolve_item(item_dict)
			var item_stats = resolved.get("stats", {})
			total_hp += item_stats.get("hp_max", 0)

	total_hp += get_party_bonus()["hp"]
	total_hp += get_gems_bonus()["hp_max"]
	return total_hp

func get_double_strike_chance() -> int:
	var chance = get_gems_bonus().get("double_strike_pct", 0)
	if active_buffs.get("elixir_swiftness", 0) > 0:
		chance += 15
	return chance

func get_combat_click_dmg() -> int:
	var base = maxi(2, int(get_total_atk() * 0.18))
	var rogue_click = get_talent_bonus("click_dmg")
	return int(float(base) * (1.0 + rogue_click))

func click() -> int:
	var atk = get_total_atk()
	var earned = stats.get("gold_per_click", 1) + atk
	if permanent_perks.has("perk_greed"):
		earned = int(earned * 1.10)
	gold += earned
	stats["total_clicks"] = stats.get("total_clicks", 0) + 1
	record_achievement_stat("total_gold_earned", earned, "add")
	gold_changed.emit(gold)
	stats_changed.emit()
	return earned

func absorb_shield_hit(damage_amount: int) -> int:
	var dmg = maxi(0, damage_amount)
	if combat_shield > 0:
		if combat_shield >= dmg:
			combat_shield -= dmg
			return 0
		else:
			var rem = dmg - combat_shield
			combat_shield = 0
			return rem
	return dmg

func recalculate_gold_per_sec() -> int:
	var total_gps = 0
	for b_id in buildings.keys():
		var count = buildings[b_id]
		if BuildingsDB.BUILDINGS.has(b_id) and count > 0:
			var base_gps = BuildingsDB.BUILDINGS[b_id]["gold_per_sec"] * count
			var mult = BuildingsDB.get_synergy_multiplier(b_id, party, active_companion)
			total_gps += int(base_gps * mult)
	stats["gold_per_sec"] = total_gps
	return total_gps

func add_gold(amount: int, source: String = "Nagroda", apply_greed: bool = true) -> int:
	if apply_greed and permanent_perks.has("perk_greed"):
		amount = int(amount * 1.10)
	gold += amount
	record_achievement_stat("total_gold_earned", amount, "add")
	gold_changed.emit(gold)
	return amount

func select_active_companion(npc_id: Variant) -> bool:
	if npc_id == null or party.has(npc_id):
		active_companion = npc_id
		recalculate_gold_per_sec()
		stats_changed.emit()
		return true
	return false

func invest_talent(path: String) -> bool:
	if talent_points <= 0:
		return false
	var cur = talents.get(path, 0)
	if cur >= 10:
		return false
	talent_points -= 1
	talents[path] = cur + 1
	stats_changed.emit()
	return true

func get_talent_bonus(bonus_type: String) -> float:
	match bonus_type:
		"low_hp_atk":
			return float(talents.get("berserker", 0)) * 0.04
		"crit_dmg_mult":
			return float(talents.get("berserker", 0)) * 0.06
		"thorns_pct":
			return float(talents.get("defender", 0)) * 0.05
		"regen_turn_pct":
			return float(talents.get("defender", 0)) * 0.01
		"click_dmg":
			return float(talents.get("rogue", 0)) * 0.10
		"bonus_gold":
			return float(talents.get("rogue", 0)) * 0.03
		"lifesteal_pct":
			return float(maxi(talents.get("rogue", 0), talents.get("berserker", 0))) * 0.02
		"dodge_pct":
			return float(talents.get("rogue", 0)) * 0.03
	return 0.0

func tick_active_buffs() -> Array:
	var expired = []
	for buff_id in active_buffs.keys():
		active_buffs[buff_id] -= 1
		if active_buffs[buff_id] <= 0:
			expired.append(buff_id)
	for e in expired:
		active_buffs.erase(e)
	if not expired.is_empty():
		stats_changed.emit()
	return expired

func is_inventory_full() -> bool:
	return inventory.size() >= 80

func add_to_inventory(item_id: Variant, is_reward: bool = false) -> bool:
	var item_dict: Dictionary = {}
	if item_id is Dictionary:
		item_dict = item_id.duplicate(true)
	elif item_id is String:
		item_dict = {"id": item_id, "lvl": 0}
	else:
		return false

	if not is_inventory_full():
		inventory.append(item_dict)
		return true
	elif is_reward:
		inventory_stash.append(item_dict)
		return true
	return false

func claim_stash_item(index: int = 0) -> bool:
	if is_inventory_full():
		return false
	if index >= 0 and index < inventory_stash.size():
		var item = inventory_stash[index]
		inventory_stash.remove_at(index)
		inventory.append(item)
		stats_changed.emit()
		return true
	return false

func invest_stat_point(stat_name: String, amount: int = 1) -> bool:
	if stat_points <= 0 or amount <= 0:
		return false
	amount = mini(amount, stat_points)

	if stat_name == "bonus_loot_pct":
		var current = stats.get("bonus_loot_pct", 0)
		var allowed = maxi(0, 50 - current)
		if allowed <= 0: return false
		amount = mini(amount, allowed)
	elif stat_name == "crit_chance":
		var current = stats.get("crit_chance", 0)
		var allowed = maxi(0, 30 - current)
		if allowed <= 0: return false
		amount = mini(amount, allowed)

	if stat_name == "max_hp":
		max_hp += (amount * 8)
		hp = mini(get_max_hp(), hp + (amount * 8))
	else:
		stats[stat_name] = stats.get(stat_name, 0) + amount

	stat_points -= amount
	stats_changed.emit()
	return true

func rest_at_inn(cost: int = 20) -> bool:
	if gold < cost:
		return false
	gold -= cost
	hp = get_max_hp()
	mana = max_mana
	gold_changed.emit(gold)
	hp_changed.emit(hp, get_max_hp())
	stats_changed.emit()
	return true

func remove_from_inventory(index: int) -> bool:
	if index >= 0 and index < inventory.size():
		inventory.remove_at(index)
		return true
	return false

func remove_multiple_from_inventory(indices: Array) -> Array:
	var removed = []
	var sorted_indices = indices.duplicate()
	sorted_indices.sort_custom(func(a, b): return int(a) > int(b))
	for idx_raw in sorted_indices:
		var idx = int(idx_raw)
		if idx >= 0 and idx < inventory.size():
			removed.append(inventory[idx])
			inventory.remove_at(idx)
	return removed

func equip(item_dict: Dictionary) -> bool:
	var resolved = ItemsDB.resolve_item(item_dict)
	if resolved.is_empty() or resolved.get("type", "") != "equipment":
		return false

	var slot = resolved.get("slot", "")
	if not equipment.has(slot):
		return false

	var idx = inventory.find(item_dict)
	if idx == -1:
		return false

	var old_item = equipment[slot]
	equipment[slot] = item_dict
	inventory.remove_at(idx)
	if old_item != null:
		inventory.append(old_item)

	stats_changed.emit()
	return true

func unequip(slot: String) -> bool:
	if not equipment.has(slot) or equipment[slot] == null:
		return false
	if is_inventory_full():
		return false

	var item = equipment[slot]
	equipment[slot] = null
	inventory.append(item)
	stats_changed.emit()
	return true

func use_consumable(index: int) -> bool:
	if index < 0 or index >= inventory.size():
		return false
	var it = inventory[index]
	var resolved = ItemsDB.resolve_item(it)
	if resolved.get("type", "") == "consumable":
		if resolved["id"] == "pot_hp":
			hp = get_max_hp()
			inventory.remove_at(index)
			hp_changed.emit(hp, get_max_hp())
			return true
		elif resolved["id"] == "pot_mana":
			mana = mini(max_mana, mana + 100)
			inventory.remove_at(index)
			return true
	elif resolved.get("id", "") == "herb_mystery":
		# Zażycie ziółka z plecaka
		active_buffs["elixir_psychedelic"] = 10
		inventory.remove_at(index)
		stats_changed.emit()
		return true
	return false

func record_achievement_stat(key: String, value: int = 1, mode: String = "add"):
	if not achievement_stats.has(key):
		achievement_stats[key] = 0
	if mode == "add":
		achievement_stats[key] += value
	elif mode == "max":
		achievement_stats[key] = maxi(achievement_stats[key], value)
	elif mode == "set":
		achievement_stats[key] = value

	# Sprawdzenie ukończenia osiągnięć
	for ach_id in AchievementsDB.ACHIEVEMENTS.keys():
		var ach = AchievementsDB.ACHIEVEMENTS[ach_id]
		if ach["stat_key"] == key:
			var cur_stat = achievement_stats[key]
			if cur_stat >= ach["target"]:
				if not achievements.has(ach_id):
					achievements[ach_id] = {"completed": true, "claimed": false}
				else:
					achievements[ach_id]["completed"] = true

func claim_achievement(ach_id: String) -> bool:
	if not achievements.has(ach_id) or not achievements[ach_id].get("completed", false):
		return false
	if achievements[ach_id].get("claimed", false):
		return false

	achievements[ach_id]["claimed"] = true
	var ach = AchievementsDB.ACHIEVEMENTS[ach_id]
	var rew = ach.get("rewards", {})
	if rew.has("gold"):
		add_gold(rew["gold"])
	if rew.has("exp"):
		add_exp(rew["exp"])
	if rew.has("perk_id"):
		if not permanent_perks.has(rew["perk_id"]):
			permanent_perks.append(rew["perk_id"])
			stats_changed.emit()
	return true

func unlock_garden_plot(plot_idx: int) -> bool:
	if plot_idx >= 0 and plot_idx < herb_garden.size():
		var plot = herb_garden[plot_idx]
		if not plot.get("unlocked", false):
			plot["unlocked"] = true
			plot["planted_at"] = Time.get_unix_time_from_system()
			return true
	return false

func harvest_garden_plot(plot_idx: int) -> Variant:
	if plot_idx < 0 or plot_idx >= herb_garden.size():
		return null
	var plot = herb_garden[plot_idx]
	if not plot.get("unlocked", false):
		return null

	var elapsed = Time.get_unix_time_from_system() - plot.get("planted_at", 0.0)
	if elapsed < plot.get("growth_time", 30):
		return null

	var herb_type = plot.get("type", "herb_amanita")
	var count = 1
	if permanent_perks.has("perk_alchemist_touch") and randf() < 0.15:
		count = 2

	for c in range(count):
		add_to_inventory(herb_type)

	plot["planted_at"] = Time.get_unix_time_from_system()
	record_achievement_stat("herbs_harvested", count, "add")
	return {"herb": herb_type, "count": count}

func update_offline_progress():
	var now = Time.get_unix_time_from_system()
	var elapsed = now - last_update_time
	if elapsed > 0:
		var gps = recalculate_gold_per_sec()
		# Odzyskiwanie many
		mana = mini(max_mana, mana + int(elapsed * stats.get("mana_regen", 1)))
	last_update_time = now

func to_dict() -> Dictionary:
	return {
		"name": name,
		"gold": gold,
		"mana": mana,
		"max_mana": max_mana,
		"hp": hp,
		"max_hp": max_hp,
		"level": level,
		"exp": exp,
		"stat_points": stat_points,
		"talent_points": talent_points,
		"talents": talents,
		"inventory": inventory,
		"inventory_stash": inventory_stash,
		"equipment": equipment,
		"stats": stats,
		"party": party,
		"active_companion": active_companion,
		"quests": quests,
		"buildings": buildings,
		"bestiary": bestiary,
		"dungeon_tickets": dungeon_tickets,
		"achievements": achievements,
		"permanent_perks": permanent_perks,
		"achievement_stats": achievement_stats,
		"herb_garden": herb_garden,
		"garden_plot_0_leased": garden_plot_0_leased,
		"seen_cinematics": seen_cinematics,
		"active_buffs": active_buffs,
		"last_update_time": last_update_time
	}

func from_dict(d: Dictionary):
	name = d.get("name", "Bohater")
	gold = d.get("gold", 0)
	mana = d.get("mana", 100)
	max_mana = d.get("max_mana", 100)
	hp = d.get("hp", 85)
	max_hp = d.get("max_hp", 85)
	level = d.get("level", 1)
	exp = d.get("exp", 0)
	stat_points = d.get("stat_points", 0)
	talent_points = d.get("talent_points", 0)
	talents = d.get("talents", {"berserker": 0, "defender": 0, "rogue": 0})
	inventory = d.get("inventory", [])
	inventory_stash = d.get("inventory_stash", [])
	equipment = d.get("equipment", {"weapon": null, "armor": null, "helmet": null, "accessory": null})
	stats = d.get("stats", {})
	party = d.get("party", [])
	active_companion = d.get("active_companion", null)
	quests = d.get("quests", QuestsDB.get_all_quests_init())
	buildings = d.get("buildings", {})
	bestiary = d.get("bestiary", {})
	dungeon_tickets = d.get("dungeon_tickets", 3)
	achievements = d.get("achievements", {})
	permanent_perks = d.get("permanent_perks", [])
	achievement_stats = d.get("achievement_stats", {})
	herb_garden = d.get("herb_garden", [])
	garden_plot_0_leased = d.get("garden_plot_0_leased", false)
	seen_cinematics = d.get("seen_cinematics", {})
	active_buffs = d.get("active_buffs", {})
	last_update_time = d.get("last_update_time", Time.get_unix_time_from_system())
	migrate()

func migrate():
	if not stats.has("base_atk") or stats["base_atk"] <= 0: stats["base_atk"] = 8
	if not stats.has("base_def") or stats["base_def"] <= 0: stats["base_def"] = 4
	if not stats.has("crit_chance"): stats["crit_chance"] = 0
	if not stats.has("bonus_loot_pct"): stats["bonus_loot_pct"] = 0
	if not stats.has("gold_per_click"): stats["gold_per_click"] = 1
	if not stats.has("gold_per_sec"): stats["gold_per_sec"] = 0
	if not stats.has("mana_regen"): stats["mana_regen"] = 1
	if max_hp <= 0: max_hp = 85

	# Normalizacja świeżej postaci poziomu 1 ze starych zawyżonych wartości
	if level == 1 and stats.get("base_atk", 8) == 12 and stats.get("base_def", 4) == 10 and max_hp == 120:
		stats["base_atk"] = 8
		stats["base_def"] = 4
		max_hp = 85
		hp = 85

	if hp < 1: hp = get_max_hp()

	# Bezpieczna migracja talentów: odblokowanie od poziomu 10 (1 punkt co 5 poziomów)
	var earned_talents: int = maxi(0, (level - 5) / 5) if level >= 10 else 0
	var spent_talents: int = 0
	for v in talents.values():
		spent_talents += int(v)
	if (talent_points == 0 and spent_talents == 0 and earned_talents > 0) or (talent_points + spent_talents > earned_talents):
		talent_points = maxi(0, earned_talents - spent_talents)
	if herb_garden.is_empty():
		herb_garden = [
			{"type": "herb_amanita", "planted_at": 0.0, "growth_time": 30, "unlocked": false},
			{"type": "herb_moss", "planted_at": 0.0, "growth_time": 45, "unlocked": false},
			{"type": "herb_flower", "planted_at": 0.0, "growth_time": 60, "unlocked": false},
			{"type": "herb_mystery", "planted_at": 0.0, "growth_time": 120, "unlocked": false}
		]
	if not garden_plot_0_leased and herb_garden.size() > 0:
		herb_garden[0]["unlocked"] = false

	# Synchronizuj i uaktualnij listę zadań z QuestsDB
	var q_map: Dictionary = {}
	for q_ref in QuestsDB.QUESTS:
		q_map[q_ref["id"]] = q_ref

	if quests.is_empty():
		quests = QuestsDB.get_all_quests_init()
	else:
		for q in quests:
			var qid = q.get("id", "")
			if q_map.has(qid):
				var ref = q_map[qid]
				q["name"] = ref["name"]
				q["description"] = ref["description"]
				q["requirements"] = ref["requirements"]
				q["rewards"] = ref["rewards"]
				q["unlock_level"] = int(ref["unlock_level"])
				q["npc_id"] = ref.get("npc_id", "innkeeper")
				q["dialog_offer"] = ref.get("dialog_offer", "")
				q["dialog_accept_reaction"] = ref.get("dialog_accept_reaction", "")
				q["dialog_complete"] = ref.get("dialog_complete", "")
			if not q.has("status"):
				q["status"] = "LOCKED"
			if not q.has("progress"):
				q["progress"] = {"kills": {}}

	update_quests_status()

	# Bezpieczna walidacja odblokowania grządek w ogrodzie (grządki kompanów wymagają ich rekrutacji/zadania)
	if not garden_plot_0_leased and herb_garden.size() > 0:
		herb_garden[0]["unlocked"] = false
	if herb_garden.size() > 1 and not is_quest_claimed_or_companion_unlocked("eczme", "q_party_eczme"):
		herb_garden[1]["unlocked"] = false
	if herb_garden.size() > 2 and not is_quest_claimed_or_companion_unlocked("pianek", "q_party_pianek"):
		herb_garden[2]["unlocked"] = false
	if herb_garden.size() > 3 and not is_quest_claimed_or_companion_unlocked("domcia", "q_party_domcia"):
		herb_garden[3]["unlocked"] = false

	recalculate_gold_per_sec()

func is_quest_claimed_or_companion_unlocked(companion_id: String, quest_id: String) -> bool:
	if party.has(companion_id):
		return true
	for q in quests:
		if q.get("id") == quest_id and q.get("status") == "CLAIMED":
			return true
	return false

func update_quests_status():
	for q in quests:
		var u_lvl = int(q.get("unlock_level", 1))
		if q.get("status") == "LOCKED" and level >= u_lvl:
			q["status"] = "AVAILABLE"

func lease_herb_plot(cost: int = 150) -> bool:
	if herb_garden.is_empty():
		return false
	if garden_plot_0_leased or herb_garden[0].get("unlocked", false):
		return false
	if gold < cost:
		return false
	gold -= cost
	garden_plot_0_leased = true
	herb_garden[0]["unlocked"] = true
	herb_garden[0]["planted_at"] = Time.get_unix_time_from_system()
	gold_changed.emit(gold)
	stats_changed.emit()
	return true
