from player import Player, TALENT_DEFINITIONS

def test_talent_investment_and_bonuses():
    p = Player("Mistrz")
    p.level = 20
    p.migrate() # Powinien otrzymać (20 - 5) // 5 = 3 punkty talentów (odblokowanie od 10 poziomu)
    assert p.talent_points == 3

    # Inwestycja w Berserkera
    res = p.invest_talent("berserker")
    assert res is True
    assert p.talents["berserker"] == 1
    assert p.talent_points == 2
    assert p.get_talent_bonus("low_hp_atk") == 0.04
    assert p.get_talent_bonus("crit_dmg_mult") == 0.06

    # Inwestycja w Defendera
    p.invest_talent("defender")
    assert p.talents["defender"] == 1
    assert p.talent_points == 1
    assert p.get_talent_bonus("thorns_pct") == 0.05
    assert p.get_talent_bonus("regen_turn_pct") == 0.01

    # Inwestycja w Rogue
    p.invest_talent("rogue")
    assert p.talents["rogue"] == 1
    assert p.talent_points == 0
    assert p.get_talent_bonus("click_dmg") == 0.10
    assert p.get_talent_bonus("bonus_gold") == 0.03
    assert p.get_talent_bonus("lifesteal_pct") == 0.02
    # Testy wywołań 2-argumentowych
    assert p.get_talent_bonus("berserker", "lifesteal_pct") == 0.02
    assert p.get_talent_bonus("rogue", "dodge_pct") == 0.03
    assert p.get_talent_bonus("defender", "thorns_pct") == 0.05
    assert p.get_talent_bonus("defender", "regen_turn_pct") == 0.01

    # Brak punktów -> brak możliwości inwestycji
    assert p.invest_talent("rogue") is False

    print("[OK] test_talent_investment_and_bonuses PASSED")

if __name__ == "__main__":
    test_talent_investment_and_bonuses()
    print("[SUCCESS] ALL TALENT TESTS PASSED!")
