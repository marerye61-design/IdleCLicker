from player import Player
from market import BUILDINGS_DB, get_building_synergy_multiplier

def test_companion_building_synergy():
    p = Player("Synergy_Tester")
    p.migrate()
    p.gold = 1000000

    # Buy 1 of each building
    for b_id in BUILDINGS_DB:
        p.buildings[b_id] = 1

    # Without companions
    p.party = []
    p.active_companion = None
    p.recalculate_gold_per_sec()
    base_gps = p.stats["gold_per_sec"]
    expected_base = sum(b.gold_per_sec for b in BUILDINGS_DB.values())
    assert base_gps == expected_base, f"Expected base gps {expected_base}, got {base_gps}"

    # Recruit maslak to party (b1 Cukiernia Maślaka gives base 1 gps)
    p.party.append("maslak")
    p.recalculate_gold_per_sec()
    # b1 base 1 * 1.25 = 1 (int), but let's test on b6 (Warsztat Yomena base 3500)
    p.party.append("yomen")
    p.recalculate_gold_per_sec()
    # Yomen base 3500 * 1.25 = 4375 (+875)
    gps_with_party = p.stats["gold_per_sec"]
    assert gps_with_party == base_gps + 875, f"Expected {base_gps + 875}, got {gps_with_party}"

    # Make Yomen active companion (1.40 multiplier -> 3500 * 1.40 = 4900 -> +1400)
    p.select_active_companion("yomen")
    gps_with_active = p.stats["gold_per_sec"]
    assert gps_with_active == base_gps + 1400, f"Expected {base_gps + 1400}, got {gps_with_active}"

    print("Building synergy tests passed successfully!")

if __name__ == "__main__":
    test_companion_building_synergy()
