from items import ITEMS_DB, get_item

def test_equipment_preserves_unique_stats():
    # wep_yomen was defined with stats={"atk": 380, "hp_max": 350, "crit_chance": 8}
    wep_yomen = ITEMS_DB["wep_yomen"]
    assert "crit_chance" in wep_yomen.stats, f"wep_yomen missing crit_chance, stats={wep_yomen.stats}"
    assert wep_yomen.stats["crit_chance"] == 8
    assert "hp_max" in wep_yomen.stats, f"wep_yomen missing hp_max, stats={wep_yomen.stats}"

    # wep_void_blade was defined with crit_chance: 20, hp_max: 1000
    wep_void = ITEMS_DB["wep_void_blade"]
    assert "crit_chance" in wep_void.stats, f"wep_void_blade missing crit_chance, stats={wep_void.stats}"
    assert wep_void.stats["crit_chance"] == 20

    # helm_pianek was defined with def: 35, hp_max: 150, atk: 20
    helm_pianek = ITEMS_DB["helm_pianek"]
    assert "atk" in helm_pianek.stats, f"helm_pianek missing atk, stats={helm_pianek.stats}"
    assert helm_pianek.stats["atk"] == 20

    # arm_damian was defined with def: 120, hp_max: 350, atk: 20
    arm_damian = ITEMS_DB["arm_damian"]
    assert "atk" in arm_damian.stats, f"arm_damian missing atk, stats={arm_damian.stats}"
    assert arm_damian.stats["atk"] == 20

    print("All equipment stat assertions passed!")

if __name__ == "__main__":
    test_equipment_preserves_unique_stats()
