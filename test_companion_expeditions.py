import time
from player import Player, EXPEDITION_TYPES

def test_companion_expeditions():
    p = Player("Wędrowiec")
    p.party = ["maslak", "eczme", "pianek"]
    p.active_companion = "eczme"

    # Próba wysłania aktywnego towarzysza -> błąd
    res = p.start_expedition("eczme", "meadow")
    assert res is False, "Nie można wysłać aktywnego towarzysza w walce"

    # Wysłanie Maślaka na Zwiady
    res = p.start_expedition("maslak", "meadow")
    assert res is True
    assert "maslak" in p.expeditions
    assert p.is_expedition_ready("maslak") is False

    # Ponowna próba wysłania zajętego Maślaka -> błąd
    assert p.start_expedition("maslak", "mine") is False

    # Symulacja upływu czasu
    p.expeditions["maslak"]["start_time"] = time.time() - 9999
    assert p.is_expedition_ready("maslak") is True

    # Odbiór nagrody
    gold_before = p.gold
    claim_res = p.claim_expedition("maslak")
    assert claim_res is not None
    assert claim_res["comp_id"] == "maslak"
    assert claim_res["gold"] > 0
    assert p.gold > gold_before
    assert "maslak" not in p.expeditions

    print("[OK] test_companion_expeditions PASSED")

if __name__ == "__main__":
    test_companion_expeditions()
    print("[SUCCESS] ALL COMPANION EXPEDITION TESTS PASSED!")
