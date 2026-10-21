from player import Player
from quests import Quest

def test_quest_claim_single_reward_record():
    p = Player("Tester_Quest")
    p.migrate()
    initial_history_len = len(p.reward_history)

    # Quest with gold, item, and exp
    q = Quest(
        "q_test", "Test Quest", "Desc",
        {},
        {"gold": 500, "item": "pot_hp", "exp": 200}
    )
    q.status = 'COMPLETED'
    success = q.claim_reward(p)
    assert success is True

    # Check history count: should have added EXACTLY 1 entry, not 2!
    added_entries = len(p.reward_history) - initial_history_len
    assert added_entries == 1, f"Expected 1 reward_history entry, got {added_entries}"
    last_entry = p.reward_history[-1]
    assert last_entry["source"] == "Zadanie"
    assert last_entry["gold"] > 0
    assert last_entry["item"] == "pot_hp"
    assert last_entry["exp"] == 200
    assert p.level == 2 and p.exp == 130, f"Expected player level 2 and exp 130, got level {p.level}, exp {p.exp}"

    print("Quest reward assertions passed!")

if __name__ == "__main__":
    test_quest_claim_single_reward_record()
