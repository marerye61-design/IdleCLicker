import sys
import os
import csv
import copy
import random

# Import logic from the game
from player import Player
from combat import TEMPLATES, get_expedition_choices, calculate_player_dmg, calculate_enemy_dmg
from items import ITEMS_DB, get_item, Equipment
from modifiers import MODIFIERS_DB

def run_equipment_simulation():
    print("Symulacja Ekwipunku...")
    results = []
    
    for item_id, base_item in ITEMS_DB.items():
        if not isinstance(base_item, Equipment):
            continue
            
        for mod_id, mod in MODIFIERS_DB.items():
            if base_item.slot in mod.allowed_slots:
                # Test +0
                test_dict = {"id": item_id, "modifier": mod_id, "lvl": 0}
                final_item = get_item(test_dict)
                if final_item:
                    results.append({
                        "Item Name": final_item.name,
                        "Base Item": base_item.name,
                        "Modifier": mod.prefix,
                        "Slot": final_item.slot,
                        "Level Req": final_item.level_req,
                        "Rarity": final_item.rarity,
                        "ATK": final_item.stats.get("atk", 0),
                        "DEF": final_item.stats.get("def", 0),
                        "HP": final_item.stats.get("hp_max", 0),
                        "Value": final_item.value
                    })
                    
    with open('sim_equipment_stats.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Item Name", "Base Item", "Modifier", "Slot", "Level Req", "Rarity", "ATK", "DEF", "HP", "Value"])
        writer.writeheader()
        writer.writerows(results)
    print("-> sim_equipment_stats.csv wygenerowane.")


def run_upgrade_simulation():
    print("Symulacja Ulepszeń...")
    results = []
    
    # Przetestujmy tylko "czyste" przedmioty (bez modyfikatorów) żeby ocenić bazową opłacalność
    for item_id, base_item in ITEMS_DB.items():
        if not isinstance(base_item, Equipment):
            continue
            
        total_cost = 0
        
        for lvl in range(0, 10):
            test_dict = {"id": item_id, "lvl": lvl}
            final_item = get_item(test_dict)
            if not final_item: continue
            
            atk = final_item.stats.get("atk", 0)
            df = final_item.stats.get("def", 0)
            hp = final_item.stats.get("hp_max", 0)
            total_stats = atk + df + (hp / 10.0) # Zwykle 10 HP to waga 1 ATK/DEF
            
            # efficiency
            if lvl == 0:
                cost = 0
                efficiency = 0
            else:
                # oblicz koszt poprzedniego poziomu by dodać do total_cost
                base_stats_val = base_item.stats.get("atk", 0) + base_item.stats.get("def", 0) + (base_item.stats.get("hp_max", 0) / 10.0)
                prev_cost = int(base_stats_val * 50 * (1.9 ** (lvl - 1)))
                if prev_cost < 10: prev_cost = 10
                total_cost += prev_cost
                
                if total_stats > 0:
                    efficiency = total_cost / total_stats # Ile złota za 1 pkt statystyki sumarycznie
                else:
                    efficiency = 0
                    
            results.append({
                "Item ID": item_id,
                "Name": final_item.name,
                "Rarity": final_item.rarity,
                "Upgrade Level": lvl,
                "ATK": atk,
                "DEF": df,
                "HP": hp,
                "Total Cumulative Cost (Gold)": total_cost,
                "Gold per Stat Point": round(efficiency, 2)
            })

    with open('sim_upgrades_efficiency.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Item ID", "Name", "Rarity", "Upgrade Level", "ATK", "DEF", "HP", "Total Cumulative Cost (Gold)", "Gold per Stat Point"])
        writer.writeheader()
        writer.writerows(results)
    print("-> sim_upgrades_efficiency.csv wygenerowane.")

def run_combat_simulation():
    print("Symulacja Walk Monte Carlo...")
    results = []
    
    test_levels = [5, 20, 50, 75, 90, 100]
    battles_per_enemy = 500
    
    for level in test_levels:
        player = Player("Symulator")
        player.level = level
        # Szukamy ekwipunku dla tego poziomu
        best_wep = max([i for i in ITEMS_DB.values() if isinstance(i, Equipment) and i.slot=="weapon" and i.level_req <= level], key=lambda x: x.stats.get("atk", 0), default=None)
        best_arm = max([i for i in ITEMS_DB.values() if isinstance(i, Equipment) and i.slot=="armor" and i.level_req <= level], key=lambda x: x.stats.get("def", 0), default=None)
        best_helm = max([i for i in ITEMS_DB.values() if isinstance(i, Equipment) and i.slot=="helmet" and i.level_req <= level], key=lambda x: x.stats.get("def", 0), default=None)
        best_acc = max([i for i in ITEMS_DB.values() if isinstance(i, Equipment) and i.slot=="accessory" and i.level_req <= level], key=lambda x: x.stats.get("atk", 0) + x.stats.get("def", 0), default=None)
        
        if best_wep: player.equipment["weapon"] = {"id": best_wep.item_id, "lvl": 0}
        if best_arm: player.equipment["armor"] = {"id": best_arm.item_id, "lvl": 0}
        if best_helm: player.equipment["helmet"] = {"id": best_helm.item_id, "lvl": 0}
        if best_acc: player.equipment["accessory"] = {"id": best_acc.item_id, "lvl": 0}
        
        # Companion - Eczme is damage dealer
        player.active_companion = "eczme"
        
        p_atk = player.get_total_atk()
        p_def = player.get_total_def()
        p_max_hp = player.get_max_hp()
        p_crit = player.get_total_crit()
        
        # Wybierzmy wrogów odpowiednich dla tego poziomu (+/- 5 lvli, wybierzemy 3 najsilniejszych)
        available = [t for t in TEMPLATES if level >= t.min_level - 5]
        if not available: available = [TEMPLATES[0]]
        
        test_enemies = available[-3:] # Top 3 toughest available templates
        
        for template in test_enemies:
            wins = 0
            losses = 0
            
            total_turns_wins = 0
            total_hp_lost_wins = 0
            
            total_enemy_hp_left_losses = 0
            total_turns_losses = 0
            
            total_exp = 0
            total_gold = 0
            
            total_pdmg_dealt = 0
            total_edmg_dealt = 0
            
            for _ in range(battles_per_enemy):
                enemy = template.generate(level)
                player.hp = p_max_hp
                turns = 0
                
                # Walka bez używania mikstur
                while player.hp > 0 and enemy.hp > 0:
                    turns += 1
                    # Player attacks
                    pdmg, is_crit = calculate_player_dmg(player, enemy)
                    total_pdmg_dealt += pdmg
                    enemy.hp -= pdmg
                    if enemy.hp <= 0:
                        wins += 1
                        total_hp_lost_wins += (p_max_hp - player.hp)
                        total_exp += enemy.exp_reward
                        total_gold += enemy.gold_reward
                        total_turns_wins += turns
                        break
                        
                    # Enemy attacks
                    edmg = calculate_enemy_dmg(enemy, player)
                    total_edmg_dealt += edmg
                    player.hp -= edmg
                    
                    if player.hp <= 0:
                        losses += 1
                        total_enemy_hp_left_losses += enemy.hp
                        total_turns_losses += turns
            
            # Zbieranie statystyk dla tego wroga
            win_rate = (wins / battles_per_enemy) * 100
            
            avg_turns_win = (total_turns_wins / wins) if wins > 0 else 0
            avg_hp_lost_win = (total_hp_lost_wins / wins) if wins > 0 else 0
            avg_player_hp_left_win = p_max_hp - avg_hp_lost_win
            
            avg_turns_loss = (total_turns_losses / losses) if losses > 0 else 0
            avg_enemy_hp_left_loss = (total_enemy_hp_left_losses / losses) if losses > 0 else 0
            
            total_turns_all = total_turns_wins + total_turns_losses
            avg_dps = (total_pdmg_dealt / total_turns_all) if total_turns_all > 0 else 0
            avg_eps = (total_edmg_dealt / total_turns_all) if total_turns_all > 0 else 0
            
            results.append({
                "Player Lvl": level,
                "Player ATK": p_atk,
                "Player DEF": p_def,
                "Player HP": p_max_hp,
                "Player CRIT": p_crit,
                "Enemy Name": f"{template.name} (Lvl {level})",
                "Enemy HP": template.generate(level).hp,
                "Win Rate %": round(win_rate, 2),
                "Avg Turns (Win)": round(avg_turns_win, 2),
                "Avg Player HP Left (Win)": round(avg_player_hp_left_win, 2),
                "Avg Enemy HP Left (Loss)": round(avg_enemy_hp_left_loss, 2),
                "Player Avg DMG/Turn": round(avg_dps, 2),
                "Enemy Avg DMG/Turn": round(avg_eps, 2)
            })

    with open('sim_combat_winrates.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Player Lvl", "Player ATK", "Player DEF", "Player HP", "Player CRIT",
            "Enemy Name", "Enemy HP", 
            "Win Rate %", "Avg Turns (Win)", "Avg Player HP Left (Win)", 
            "Avg Enemy HP Left (Loss)", "Player Avg DMG/Turn", "Enemy Avg DMG/Turn"
        ])
        writer.writeheader()
        writer.writerows(results)
    print("-> sim_combat_winrates.csv wygenerowane (Rozszerzone).")

if __name__ == "__main__":
    print("Rozpoczęcie symulacji...")
    run_equipment_simulation()
    run_upgrade_simulation()
    run_combat_simulation()
    print("Zakończono. Wszystkie dane wyeksportowano.")
