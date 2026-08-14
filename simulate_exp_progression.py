import os
import sys
import csv
import math
import random
import numpy as np
import matplotlib.pyplot as plt

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from player import Player
from combat import TEMPLATES, calculate_player_dmg, calculate_enemy_dmg
from items import ITEMS_DB, Equipment

def get_best_gear_for_level(level):
    best_wep = max([i for i in ITEMS_DB.values() if isinstance(i, Equipment) and i.slot == "weapon" and i.level_req <= level], key=lambda x: x.stats.get("atk", 0), default=None)
    best_arm = max([i for i in ITEMS_DB.values() if isinstance(i, Equipment) and i.slot == "armor" and i.level_req <= level], key=lambda x: x.stats.get("def", 0), default=None)
    best_helm = max([i for i in ITEMS_DB.values() if isinstance(i, Equipment) and i.slot == "helmet" and i.level_req <= level], key=lambda x: x.stats.get("def", 0), default=None)
    best_acc = max([i for i in ITEMS_DB.values() if isinstance(i, Equipment) and i.slot == "accessory" and i.level_req <= level], key=lambda x: x.stats.get("atk", 0) + x.stats.get("def", 0), default=None)
    return best_wep, best_arm, best_helm, best_acc

def simulate_exp_curve(max_level=100, battles_per_level=200):
    print(f"--- ROZPOCZĘCIE SYMULACJI EXP I CZASU LEVELOWANIA (1 -> {max_level}) ---")
    
    player = Player("Symulator_EXP")
    results = []
    
    cumulative_seconds = 0.0
    cumulative_kills = 0
    
    # Timing constants from main.py
    # Player attack: 288ms anim + 270ms wait = 0.558s
    # Enemy attack: 180ms anim + 330ms wait = 0.510s
    # Victory + loop restart: 1000ms + 1500ms = 2.500s
    TIME_PLAYER_TURN = 0.558
    TIME_ENEMY_TURN = 0.510
    TIME_BETWEEN_FIGHTS = 2.500

    for lvl in range(1, max_level + 1):
        player.level = lvl
        player.stat_points = (lvl - 1) * 3
        # Invest stat points realistically: 2 ATK, 1 DEF
        # Base stats already scale with level, stat_points add to stats dictionary
        player.stats["base_atk"] = 12 + int((lvl - 1) * 2.0)
        player.stats["base_def"] = 10 + int((lvl - 1) * 1.0)
        
        # Equip best gear
        wep, arm, helm, acc = get_best_gear_for_level(lvl)
        if wep: player.equipment["weapon"] = {"id": wep.item_id, "lvl": 0}
        if arm: player.equipment["armor"] = {"id": arm.item_id, "lvl": 0}
        if helm: player.equipment["helmet"] = {"id": helm.item_id, "lvl": 0}
        if acc: player.equipment["accessory"] = {"id": acc.item_id, "lvl": 0}
        
        # Companion - Eczme as standard active companion
        player.active_companion = "eczme"
        
        p_atk = player.get_total_atk()
        p_def = player.get_total_def()
        p_hp = player.get_max_hp()
        p_crit = player.get_total_crit()
        
        exp_req = player.get_exp_required()
        
        # Available monsters at this level
        available = [t for t in TEMPLATES if lvl >= t.min_level - 5]
        if not available:
            available = [TEMPLATES[0]]
            
        # Simulate fights against randomly picked available templates of monster level = lvl
        sim_exp_gained = []
        sim_turns_taken = []
        sim_fight_durations = []
        sim_wins = 0
        
        for _ in range(battles_per_level):
            template = random.choice(available)
            enemy = template.generate(lvl)
            
            p_cur_hp = p_hp
            e_cur_hp = enemy.hp
            
            p_turns = 0
            e_turns = 0
            
            while p_cur_hp > 0 and e_cur_hp > 0:
                # Player turn
                p_turns += 1
                dmg, is_crit = calculate_player_dmg(player, enemy)
                e_cur_hp -= dmg
                if e_cur_hp <= 0:
                    sim_wins += 1
                    sim_exp_gained.append(enemy.exp_reward)
                    fight_time = (p_turns * TIME_PLAYER_TURN) + (e_turns * TIME_ENEMY_TURN) + TIME_BETWEEN_FIGHTS
                    sim_turns_taken.append(p_turns + e_turns)
                    sim_fight_durations.append(fight_time)
                    break
                
                # Enemy turn
                e_turns += 1
                e_dmg = calculate_enemy_dmg(enemy, player)
                p_cur_hp -= e_dmg
                if p_cur_hp <= 0:
                    # Player defeated, receives 0 exp
                    fight_time = (p_turns * TIME_PLAYER_TURN) + (e_turns * TIME_ENEMY_TURN) + 1.0
                    sim_turns_taken.append(p_turns + e_turns)
                    sim_fight_durations.append(fight_time)
                    break
                    
        avg_exp_per_kill = np.mean(sim_exp_gained) if sim_exp_gained else 1
        avg_fight_time = np.mean(sim_fight_durations) if sim_fight_durations else 3.0
        avg_turns = np.mean(sim_turns_taken) if sim_turns_taken else 1.0
        win_rate = (sim_wins / battles_per_level) * 100.0
        
        # Calculate kills and time needed for this level up
        kills_needed = math.ceil(exp_req / avg_exp_per_kill)
        # Adjust for winrate (if winrate < 100%, need extra fights)
        effective_fights_needed = kills_needed / (win_rate / 100.0) if win_rate > 0 else kills_needed * 2
        level_time_seconds = effective_fights_needed * avg_fight_time
        
        cumulative_seconds += level_time_seconds
        cumulative_kills += kills_needed
        
        # Bestiary bonus builds up
        player.bestiary["monsters"] = cumulative_kills
        
        results.append({
            "level": lvl,
            "exp_required": exp_req,
            "avg_exp_per_kill": round(avg_exp_per_kill, 1),
            "kills_needed": kills_needed,
            "effective_fights_needed": round(effective_fights_needed, 1),
            "win_rate_pct": round(win_rate, 1),
            "avg_turns_per_fight": round(avg_turns, 2),
            "avg_fight_time_sec": round(avg_fight_time, 2),
            "level_time_sec": round(level_time_seconds, 1),
            "level_time_min": round(level_time_seconds / 60.0, 2),
            "level_time_hours": round(level_time_seconds / 3600.0, 3),
            "cumulative_kills": cumulative_kills,
            "cumulative_time_min": round(cumulative_seconds / 60.0, 2),
            "cumulative_time_hours": round(cumulative_seconds / 3600.0, 2),
            "player_atk": p_atk,
            "player_def": p_def,
            "player_hp": p_hp
        })
        
        if lvl % 10 == 0 or lvl in [1, 5, 15, 25, 50, 75, 100]:
            print(f"Lvl {lvl:3d}: Wymagane EXP: {exp_req:10,d} | EXP/Kill: {avg_exp_per_kill:6.1f} | Zabójstw: {kills_needed:5d} | Czas poziomu: {level_time_seconds/60.0:6.2f} min | Czas łączny: {cumulative_seconds/3600.0:6.2f} h")

    return results

def save_csv(results, filename="sim_exp_progression.csv"):
    fieldnames = list(results[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"-> Zapisano dane do pliku: {filename}")

def generate_charts(results, output_path="sim_exp_progression_charts.png"):
    levels = [r["level"] for r in results]
    exp_req = [r["exp_required"] for r in results]
    exp_kill = [r["avg_exp_per_kill"] for r in results]
    kills_needed = [r["kills_needed"] for r in results]
    lvl_time_min = [r["level_time_min"] for r in results]
    cum_time_hours = [r["cumulative_time_hours"] for r in results]
    avg_fight_time = [r["avg_fight_time_sec"] for r in results]
    
    # Set dark aesthetic matching the game theme
    plt.style.use('dark_background')
    fig, axs = plt.subplots(2, 2, figsize=(18, 12), dpi=300)
    fig.patch.set_facecolor('#1a100b')
    
    for ax in axs.flat:
        ax.set_facecolor('#261710')
        ax.grid(True, linestyle='--', alpha=0.3, color='#f4d03f')
        ax.tick_params(colors='#e0cfb8', labelsize=10)
        for spine in ax.spines.values():
            spine.set_color('#8b5a2b')
            spine.set_linewidth(1.5)

    # --- Wykres 1: Wymagany EXP oraz Średni EXP z Potwora ---
    ax1 = axs[0, 0]
    line1 = ax1.plot(levels, exp_req, color='#e74c3c', linewidth=2.5, label='Wymagane EXP na poziom (lewa oś)')
    ax1.set_xlabel('Poziom Gracza (Level)', color='#f4d03f', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Wymagane EXP', color='#e74c3c', fontsize=12, fontweight='bold')
    ax1.ticklabel_format(style='plain', axis='y')
    
    ax1_twin = ax1.twinx()
    ax1_twin.set_facecolor('#261710')
    line2 = ax1_twin.plot(levels, exp_kill, color='#f1c40f', linewidth=2.5, linestyle='-.', label='Średnie EXP z 1 Potwora (prawa oś)')
    ax1_twin.set_ylabel('EXP z Potwora na tym samym poziomie', color='#f1c40f', fontsize=12, fontweight='bold')
    ax1_twin.tick_params(colors='#f1c40f', labelsize=10)
    for spine in ax1_twin.spines.values():
        spine.set_color('#8b5a2b')
        
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', framealpha=0.8, facecolor='#1a100b', edgecolor='#f4d03f')
    ax1.set_title('1. Skalowanie Doświadczenia (Wymagania vs Zysk)', color='#f4d03f', fontsize=14, fontweight='bold', pad=12)

    # --- Wykres 2: Liczba zabójstw potworów potrzebna na dany poziom ---
    ax2 = axs[0, 1]
    ax2.plot(levels, kills_needed, color='#3498db', linewidth=2.5, label='Liczba potworów na poziom')
    ax2.fill_between(levels, kills_needed, color='#3498db', alpha=0.2)
    ax2.set_xlabel('Poziom Gracza (Level)', color='#f4d03f', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Liczba Zabitych Potworów (Kills)', color='#3498db', fontsize=12, fontweight='bold')
    ax2.set_title('2. Liczba Pokonanych Potworów na Level Up', color='#f4d03f', fontsize=14, fontweight='bold', pad=12)
    ax2.legend(loc='upper left', framealpha=0.8, facecolor='#1a100b', edgecolor='#f4d03f')

    # Add milestone markers on ax2
    milestones = [10, 25, 50, 75, 100]
    for m in milestones:
        if m <= len(results):
            k = results[m-1]["kills_needed"]
            ax2.scatter(m, k, color='#f39c12', s=60, zorder=5)
            ax2.annotate(f"{k} kills", (m, k), textcoords="offset points", xytext=(0, 10),
                         ha='center', fontsize=9, color='#f1c40f', fontweight='bold')

    # --- Wykres 3: Czas wbijania pojedynczego poziomu (w minutach) ---
    ax3 = axs[1, 0]
    ax3.plot(levels, lvl_time_min, color='#2ecc71', linewidth=2.5, label='Czas na poziom (minuty)')
    ax3.fill_between(levels, lvl_time_min, color='#2ecc71', alpha=0.2)
    ax3.set_xlabel('Poziom Gracza (Level)', color='#f4d03f', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Czas trwania poziomu [Minuty]', color='#2ecc71', fontsize=12, fontweight='bold')
    ax3.set_title('3. Czas Potrzebny na Awans (Pojedynczy Poziom)', color='#f4d03f', fontsize=14, fontweight='bold', pad=12)
    ax3.legend(loc='upper left', framealpha=0.8, facecolor='#1a100b', edgecolor='#f4d03f')
    
    for m in milestones:
        if m <= len(results):
            t = results[m-1]["level_time_min"]
            ax3.scatter(m, t, color='#e67e22', s=60, zorder=5)
            ax3.annotate(f"{t:.1f} min", (m, t), textcoords="offset points", xytext=(0, 10),
                         ha='center', fontsize=9, color='#e67e22', fontweight='bold')

    # --- Wykres 4: Skumulowany łączny czas gry do osiągnięcia danego poziomu (w godzinach) ---
    ax4 = axs[1, 1]
    ax4.plot(levels, cum_time_hours, color='#9b59b6', linewidth=3.0, label='Łączny czas gry (Godziny)')
    ax4.fill_between(levels, cum_time_hours, color='#9b59b6', alpha=0.25)
    ax4.set_xlabel('Poziom Gracza (Level)', color='#f4d03f', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Łączny Czas Gry [Godziny]', color='#9b59b6', fontsize=12, fontweight='bold')
    ax4.set_title('4. Całkowity Czas Gry od 1 do Max Lvl (Krzywa Progresji)', color='#f4d03f', fontsize=14, fontweight='bold', pad=12)
    ax4.legend(loc='upper left', framealpha=0.8, facecolor='#1a100b', edgecolor='#f4d03f')

    for m in milestones:
        if m <= len(results):
            ch = results[m-1]["cumulative_time_hours"]
            ax4.scatter(m, ch, color='#f1c40f', s=60, zorder=5)
            ax4.annotate(f"Lvl {m}: {ch:.1f}h", (m, ch), textcoords="offset points", xytext=(-15, 12),
                         ha='center', fontsize=9, color='#f1c40f', fontweight='bold')

    plt.suptitle("⚔️ IDLE RPG - SYMULACJA PROGRESJI EXP I CZASU GRY (POZIOMY 1 -> 100) ⚔️",
                 fontsize=18, fontweight='bold', color='#f4d03f', y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"-> Wygenerowano wykres: {output_path}")

if __name__ == "__main__":
    results = simulate_exp_curve(max_level=100, battles_per_level=100)
    save_csv(results, "sim_exp_progression.csv")
    generate_charts(results, "sim_exp_progression_charts.png")
