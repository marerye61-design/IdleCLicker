class_name CombatMath

# Klasa obliczeń bojowych (obrażenia, pancerz, krytyki, uniki, towarzysze)

static func calculate_player_dmg(player, enemy: Dictionary, is_first_turn: bool = false) -> Dictionary:
	var p_atk: int = player.get_total_atk()
	var e_def: int = enemy.get("defence", 0)

	var base_dmg: int = p_atk - int(e_def * 0.4)
	var min_dmg: int = maxi(1, int(p_atk * 0.25))
	var final_dmg: int = maxi(min_dmg, base_dmg)

	var variance: float = randf_range(0.85, 1.15)
	var dmg: int = int(float(final_dmg) * variance)

	# Pasywka Eczmego: "Serwis z Wyskoku" (+25% obrażeń w 1. turze)
	if is_first_turn and player.active_companion == "eczme":
		dmg = int(dmg * 1.25)

	# Bonus Berserkera: "Krwawy Szał" (gdy HP < 50%)
	if player.hp < int(player.get_max_hp() * 0.5):
		var low_hp_bonus: float = player.get_talent_bonus("low_hp_atk")
		if low_hp_bonus > 0.0:
			dmg = int(dmg * (1.0 + low_hp_bonus))

	var is_crit: bool = false
	var crit_chance: int = player.get_total_crit()
	if randi_range(1, 100) <= crit_chance:
		var crit_mult: float = 1.75 + player.get_talent_bonus("crit_dmg_mult")
		dmg = int(dmg * crit_mult)
		is_crit = true

	return {
		"damage": maxi(1, dmg),
		"is_crit": is_crit
	}

static func calculate_enemy_dmg(enemy: Dictionary, player) -> int:
	var e_atk: int = enemy.get("atk", 10)
	var p_def: int = maxi(0, player.get_total_def())

	var mitigation_k: float = 80.0 + float(player.level) * 4.0
	var mitigation_pct: float = float(p_def) / (float(p_def) + mitigation_k)
	mitigation_pct = minf(0.75, mitigation_pct)

	var raw_dmg: float = float(e_atk) * (1.0 - mitigation_pct)
	var variance: float = randf_range(0.9, 1.1)
	var final_dmg: int = int(raw_dmg * variance)

	# Pasywka Damiana: "Niezłomna Tarcza" (stała redukcja o 10%)
	if player.active_companion == "damian":
		final_dmg = int(final_dmg * 0.90)

	return maxi(1, final_dmg)

static func get_companion_ultimate(comp_id: String) -> Dictionary:
	match comp_id:
		"eczme":
			return {
				"id": "eczme_spike",
				"name": "Ścina Przeznaczenia",
				"cooldown": 4,
				"desc": "Potężny atak 5-kilogramową Skórzaną Kulą Przeznaczenia (220% ATK) prosto w twarz wroga, ogłuszający go na 1 turę!",
				"dmg_mult": 2.2,
				"stun_turns": 1
			}
		"pianek":
			return {
				"id": "pianek_flex",
				"name": "Napięcie Bicepsa",
				"cooldown": 4,
				"desc": "Maksymalna pompa białkowa! Pianek rzuca kowadłem we wroga (180% ATK) i napina mięśnie, dając bohaterowi barierę tarczy na 30% Max HP!",
				"dmg_mult": 1.8,
				"shield_pct": 30
			}
		"domcia":
			return {
				"id": "domcia_smoke",
				"name": "Fioletowy Horyzont",
				"cooldown": 4,
				"desc": "Gęsty obłok ziół i zarodników Amanity: leczy bohatera o 30% Max HP, a zdezorientowany wróg pudłuje w kolejnej turze!",
				"heal_pct": 30,
				"blind_turns": 1
			}
		"damian":
			return {
				"id": "damian_tankard",
				"name": "Rycerski Toast",
				"cooldown": 4,
				"desc": "Damian wypija kufel mocnego ale i uderza z furią (200% ATK), po czym rozkłada Niezłomną Tarczę na 20% Max HP!",
				"dmg_mult": 2.0,
				"shield_pct": 20
			}
		"maslak":
			return {
				"id": "maslak_donut",
				"name": "Lukrowany Pączek",
				"cooldown": 3,
				"desc": "Maślak częstuje pysznym, ciepłym pączkiem: przywraca bohaterowi 35% Max HP i wyciąga ze skrytki dodatkowe złoto!",
				"heal_pct": 35,
				"bonus_gold": true
			}
		"yomen":
			return {
				"id": "yomen_wrench",
				"name": "Rzut Czternastką",
				"cooldown": 4,
				"desc": "Szczurzy alchemik ciska zardzewiałym kluczem czternastką, zadając 260% ATK gwarantowanym krytykiem!",
				"dmg_mult": 2.6,
				"force_crit": true
			}
	return {}
