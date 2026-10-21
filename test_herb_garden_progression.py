import time
from player import Player
from quests import QUESTS_DB, Quest

def test_garden_initial_state_and_unlock():
    p = Player()
    # Nowa postać: wszystkie 4 grządki powinny być zablokowane
    assert len(p.herb_garden) == 4, "Powinno być 4 grządki"
    assert p.get_unlocked_plots_count() == 0, f"Oczekiwano 0 odblokowanych grządek, jest {p.get_unlocked_plots_count()}"
    assert not p.is_plot_unlocked(0), "Grządka 0 powinna być zablokowana"
    assert not p.is_plot_unlocked(1), "Grządka 1 powinna być zablokowana"
    assert not p.is_plot_unlocked(2), "Grządka 2 powinna być zablokowana"
    assert not p.is_plot_unlocked(3), "Grządka 3 powinna być zablokowana"

    # Odblokowanie grządki 0 (Barnaba)
    p.unlock_garden_plot(0)
    assert p.is_plot_unlocked(0), "Grządka 0 powinna być odblokowana"
    assert p.get_unlocked_plots_count() == 1, "Powinna być 1 odblokowana grządka"
    assert p.herb_garden[0]["unlocked"] is True
    assert p.herb_garden[0]["planted_at"] > 0

    # Odblokowanie kolejnych
    p.unlock_garden_plot(1)
    p.unlock_garden_plot(2)
    p.unlock_garden_plot(3)
    assert p.get_unlocked_plots_count() == 4
    print("[OK] test_garden_initial_state_and_unlock PASSED")

def test_garden_migration_safety():
    # Starszy zapis: grządki bez klucza 'unlocked'
    old_data = {
        "name": "Weteran",
        "level": 25,
        "party": ["maslak", "eczme", "pianek"],
        "herb_garden": [
            {"type": "herb_amanita", "planted_at": time.time(), "growth_time": 45},
            {"type": "herb_moss", "planted_at": time.time(), "growth_time": 60},
            {"type": "herb_flower", "planted_at": time.time(), "growth_time": 75},
            {"type": "herb_mystery", "planted_at": time.time(), "growth_time": 120}
        ]
    }
    p = Player("Weteran")
    p.__dict__.update(old_data)
    p.migrate()

    # Ponieważ gracz ma pianka i eczme w drużynie, powinien mieć odblokowane grządki 0, 1, 2
    assert p.is_plot_unlocked(0), "Grządka 0 powinna być odblokowana dla weterana"
    assert p.is_plot_unlocked(1), "Grządka 1 (Eczme) powinna być odblokowana"
    assert p.is_plot_unlocked(2), "Grządka 2 (Pianek) powinna być odblokowana"
    assert not p.is_plot_unlocked(3), "Grządka 3 (Domcia) powinna być zablokowana bez Domci"
    assert p.get_unlocked_plots_count() == 3
    print("[OK] test_garden_migration_safety PASSED")

def test_quest_rewards_unlock_plots():
    p = Player("Poszukiwacz")
    # Gracz odblokowuje grządkę 0 u Barnaby
    p.unlock_garden_plot(0)
    assert p.get_unlocked_plots_count() == 1

    # Wyszukaj questy Eczmego, Pianka, Domci
    q_map = {q.quest_id: q for q in QUESTS_DB}
    
    q_eczme = q_map.get("q_party_eczme")
    assert q_eczme is not None
    assert q_eczme.rewards.get("garden_plot") == 1, "Quest Eczmego powinien nagradzać grządką 1"

    # Wykonaj quest Eczmego
    q_eczme.status = "COMPLETED"
    q_eczme.claim_reward(p)
    assert p.is_plot_unlocked(1), "Grządka 1 powinna być odblokowana po queście Eczmego"
    assert p.get_unlocked_plots_count() == 2

    # Quest Pianka
    q_pianek = q_map.get("q_party_pianek")
    assert q_pianek.rewards.get("garden_plot") == 2, "Quest Pianka powinien nagradzać grządką 2"
    q_pianek.status = "COMPLETED"
    q_pianek.claim_reward(p)
    assert p.is_plot_unlocked(2), "Grządka 2 powinna być odblokowana po queście Pianka"
    assert p.get_unlocked_plots_count() == 3

    # Quest Domci
    q_domcia = q_map.get("q_party_domcia")
    assert q_domcia.rewards.get("garden_plot") == 3, "Quest Domci powinien nagradzać grządką 3"
    q_domcia.status = "COMPLETED"
    q_domcia.claim_reward(p)
    assert p.is_plot_unlocked(3), "Grządka 3 powinna być odblokowana po queście Domci"
    assert p.get_unlocked_plots_count() == 4

    print("[OK] test_quest_rewards_unlock_plots PASSED")

def test_barnaba_lease():
    p = Player("Ogrodnik")
    p.gold = 100
    LEASE_COST = 150
    # Nie stać na dzierżawę
    can_afford = (p.gold >= LEASE_COST)
    assert not can_afford
    assert not p.is_plot_unlocked(0)

    # Gracz zdobywa złoto
    p.gold = 250
    can_afford = (p.gold >= LEASE_COST)
    assert can_afford
    p.gold -= LEASE_COST
    p.unlock_garden_plot(0)

    assert p.gold == 100
    assert p.is_plot_unlocked(0)
    assert p.get_unlocked_plots_count() == 1
    print("[OK] test_barnaba_lease PASSED")

if __name__ == "__main__":
    test_garden_initial_state_and_unlock()
    test_garden_migration_safety()
    test_quest_rewards_unlock_plots()
    test_barnaba_lease()
    print("[SUCCESS] ALL GARDEN PROGRESSION TESTS PASSED!")
