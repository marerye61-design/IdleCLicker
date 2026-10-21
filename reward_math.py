"""Pure reward calculations shared by combat and dungeon completion."""


def calculate_combat_rewards(player, enemy):
    gems_bonus = player.get_gems_bonus()
    loot_pct = getattr(player, "stats", {}).get("bonus_loot_pct", 0)
    loot_pct += gems_bonus.get("bonus_loot_pct", 0)

    gold_multiplier = 1.0 + loot_pct / 100.0
    gold_multiplier += gems_bonus.get("bonus_gold_pct", 0) / 100.0
    if getattr(player, "active_buffs", {}).get("elixir_fortune", 0) > 0:
        gold_multiplier += 0.40
    if "perk_greed" in getattr(player, "permanent_perks", []):
        gold_multiplier += 0.10

    return {
        "exp": int(enemy.exp_reward),
        "gold": int(enemy.gold_reward * gold_multiplier),
        "loot_pct": loot_pct,
        "gems_bonus": gems_bonus,
    }


def calculate_dungeon_rewards(player, dungeon, loot_pct, gems_bonus):
    exp_multiplier = 1.05 if "perk_boss_hunter" in getattr(player, "permanent_perks", []) else 1.0
    gold_multiplier = exp_multiplier + loot_pct / 100.0
    gold_multiplier += gems_bonus.get("bonus_gold_pct", 0) / 100.0
    if getattr(player, "active_buffs", {}).get("elixir_fortune", 0) > 0:
        gold_multiplier += 0.40
    if "perk_greed" in getattr(player, "permanent_perks", []):
        gold_multiplier += 0.10

    return int(dungeon.exp_reward * exp_multiplier), int(dungeon.gold_reward * gold_multiplier)
