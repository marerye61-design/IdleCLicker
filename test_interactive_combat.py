from combat import Enemy, EnemyTemplate, TEMPLATES, ELITE_AFFIXES, get_expedition_choices
from player import Player

def test_elite_enemy_generation():
    template = TEMPLATES[0] # goblin
    # Test bezpośredniej generacji elity
    normal_enemy = template.generate(5, force_elite=False)
    assert not normal_enemy.is_elite
    assert normal_enemy.affix is None

    elite_enemy = template.generate(5, force_elite=True)
    assert elite_enemy.is_elite is True
    assert elite_enemy.affix in ELITE_AFFIXES
    assert elite_enemy.hp > normal_enemy.hp or elite_enemy.atk > normal_enemy.atk
    assert elite_enemy.gold_reward > normal_enemy.gold_reward
    print("[OK] test_elite_enemy_generation PASSED")

def test_combat_click_and_shield():
    p = Player("Wojownik")
    p.stats["base_atk"] = 20
    # Uderzenie kliknięciem gracza
    click_dmg = p.get_combat_click_dmg()
    assert click_dmg >= 2, f"Click dmg powinien wynosić min 2, jest {click_dmg}"

    # Tarcza bojowa (pula punktów)
    p.combat_shield = 20
    rem = p.absorb_shield_hit(15)
    assert rem == 0, f"Powinno pochłonąć całe 15 pkt, reszta: {rem}"
    assert p.combat_shield == 5

    rem = p.absorb_shield_hit(12)
    assert rem == 7, f"Powinno przepuścić 7 pkt, reszta: {rem}"
    assert p.combat_shield == 0

    rem = p.absorb_shield_hit(10)
    assert rem == 10
    print("[OK] test_combat_click_and_shield PASSED")

def test_companion_ultimate_skills():
    p = Player("Lider")
    p.party = ["eczme", "pianek", "domcia", "damian", "maslak", "yomen"]
    
    # Eczme: Ścina Przeznaczenia (Siatkarz)
    p.select_active_companion("eczme")
    skill_eczme = p.get_companion_ultimate_info()
    assert skill_eczme is not None
    assert skill_eczme["id"] == "eczme_spike"
    assert "ogłusz" in skill_eczme["desc"].lower()

    # Pianek: Napięcie Bicepsa (Kowadło + Tarcza)
    p.select_active_companion("pianek")
    skill_pianek = p.get_companion_ultimate_info()
    assert skill_pianek["id"] == "pianek_flex"
    assert "kowadł" in skill_pianek["desc"].lower() or "tarczy" in skill_pianek["desc"].lower()

    # Domcia: Fioletowy Horyzont (Amanita + Oślepienie/Trans)
    p.select_active_companion("domcia")
    skill_domcia = p.get_companion_ultimate_info()
    assert skill_domcia["id"] == "domcia_smoke"
    assert "kolory" in skill_domcia["desc"].lower() or "amanity" in skill_domcia["desc"].lower()

    # Damian: Rycerski Toast (Kufel piwa + Tarcza)
    p.select_active_companion("damian")
    skill_damian = p.get_companion_ultimate_info()
    assert skill_damian["id"] == "damian_tankard"
    assert "kufel" in skill_damian["desc"].lower() or "niezłomną" in skill_damian["desc"].lower()

    # Maślak: Lukrowany Pączek (Pączek + Złoto)
    p.select_active_companion("maslak")
    skill_maslak = p.get_companion_ultimate_info()
    assert skill_maslak["id"] == "maslak_donut"
    assert "pączek" in skill_maslak["name"].lower()

    # Yomen: Rzut Czternastką (Klucz czternastka + Krytyk)
    p.select_active_companion("yomen")
    skill_yomen = p.get_companion_ultimate_info()
    assert skill_yomen["id"] == "yomen_wrench"
    assert "czternastk" in skill_yomen["desc"].lower()

    print("[OK] test_companion_ultimate_skills PASSED")

def test_combat_turn_simulation():
    import combat
    p = Player("Wojownik")
    p.level = 20
    p.migrate()
    p.invest_talent("berserker")
    p.invest_talent("defender")
    p.invest_talent("rogue")
    
    # Przeciwnik
    template = TEMPLATES[0]
    enemy = template.generate(5)
    enemy_hp = enemy.hp
    p_hp = p.hp

    # Tura 0: Atak gracza
    combat_turn = 0
    dmg, is_crit = combat.calculate_player_dmg(p, enemy, is_first_turn=True)
    enemy_hp -= dmg
    assert enemy_hp < enemy.hp, "Życie wroga powinno spaść po ataku gracza!"

    # Lifesteal
    ls_pct = p.get_talent_bonus("berserker", "lifesteal_pct")
    assert ls_pct == 0.02
    mult = ls_pct if ls_pct <= 1.0 else (ls_pct / 100.0)
    heal_amt = max(1, int(dmg * mult))
    p.hp = min(p.get_max_hp(), p.hp + heal_amt)

    combat_turn += 1
    assert combat_turn == 1

    # Tura 1: Ruch wroga
    raw_enemy_dmg = combat.calculate_enemy_dmg(enemy, p)
    dodge_chance = p.get_talent_bonus("rogue", "dodge_pct")
    assert dodge_chance == 0.03

    thorns_pct = p.get_talent_bonus("defender", "thorns_pct")
    assert thorns_pct == 0.05

    regen_pct = p.get_talent_bonus("defender", "regen_turn_pct")
    assert regen_pct == 0.01

    combat_turn += 1
    assert combat_turn == 2
    print("[OK] test_combat_turn_simulation PASSED")

def test_elite_loop_and_no_emojis():
    import combat
    import re
    template = TEMPLATES[1] # e_wolf
    elite = template.generate(10, force_elite=True)
    assert elite.is_elite is True
    assert elite.name.startswith("[")
    # Verify no emojis in elite name
    emoji_pattern = re.compile(r'[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\u2300-\u23ff\u2b50-\u2b55\u200d\ufe0f\u2705\u274c\u2764\u2728\u2714\u2713\u2726]')
    assert not emoji_pattern.search(elite.name), f"W nazwie elitarnego potwora nie może być emotek: {elite.name}"

    # Test symulacji pętli walki po pokonaniu potwora elitarnego
    # Następny wróg musi stać się zwykłym przeciwnikiem (bez afiksu i z normalnymi statystykami)
    next_enemy = None
    if elite.is_elite:
        tmpl = next((t for t in TEMPLATES if t.e_id == elite.e_id), None)
        assert tmpl is not None
        next_enemy = tmpl.generate(elite.level, force_elite=False)
    
    assert next_enemy is not None
    assert next_enemy.is_elite is False
    assert next_enemy.affix is None
    assert "[" not in next_enemy.name
    assert next_enemy.name == "Leśny Wilk"
    assert next_enemy.hp < elite.hp
    print("[OK] test_elite_loop_and_no_emojis PASSED")

if __name__ == "__main__":
    test_elite_enemy_generation()
    test_combat_click_and_shield()
    test_companion_ultimate_skills()
    test_combat_turn_simulation()
    test_elite_loop_and_no_emojis()
    print("[SUCCESS] ALL INTERACTIVE COMBAT TESTS PASSED!")
