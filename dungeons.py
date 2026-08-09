import time
import random
import msvcrt
from flavor_texts import get_random_flavor_text
from items import ITEMS_DB

class Dungeon:
    def __init__(self, d_id, name, level_req, duration, exp_reward, gold_reward, drop_pool):
        self.d_id = d_id
        self.name = name
        self.level_req = level_req
        self.duration = duration # w sekundach
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.drop_pool = drop_pool

DUNGEONS = [
    # Wczesne / Środkowe Lochy
    Dungeon("d1", "Złowrogi Las", 5, 180, 500, 250, ["wep_maslak", "helm_pianek"]),
    Dungeon("d2", "Opuszczona Kopalnia", 15, 180, 2500, 1000, ["arm_damian", "acc_domcia"]),
    Dungeon("d3", "Twierdza Cieni", 30, 180, 12000, 5000, ["wep_yomen", "arm_eczme"]),
    
    # Nowe Lochy (End-Game)
    Dungeon("d4", "Wulkaniczne Czeluście", 45, 180, 45000, 18000, ["wep_fire_axe", "acc_fire_ruby"]),
    Dungeon("d5", "Kryształowe Jaskinie", 60, 180, 150000, 50000, ["arm_crystal", "helm_crystal"]),
    Dungeon("d6", "Zamarznięta Pustka", 75, 180, 400000, 120000, ["wep_frost_mourne", "acc_frost_amulet"]),
    Dungeon("d7", "Świątynia Upadłych Bogów", 90, 180, 1200000, 350000, ["arm_fallen_god", "helm_fallen_god"]),
    Dungeon("d8", "Wymiar Czasoprzestrzeni", 100, 180, 3500000, 1000000, ["wep_void_blade", "acc_void_core"])
]

def run_dungeon(player, dungeon):
    if player.level < dungeon.level_req:
        print(f"Loch {dungeon.name} wymaga {dungeon.level_req} poziomu!")
        time.sleep(2)
        return False

    print(f"\n[{dungeon.name}] - Wkroczyłeś do lochu.")
    print("Drużyna wyrusza na 3-minutową eksplorację.")
    print("Naciśnij 'q', aby się wycofać (stracisz nagrody).")
    
    elapsed = 0
    next_flavor = 10
    
    while elapsed < dungeon.duration:
        # Sprawdzanie przerwania przez gracza
        if msvcrt.kbhit():
            char = msvcrt.getch().decode('utf-8', errors='ignore')
            if char.lower() == 'q':
                print("Wycofałeś się z lochu!")
                time.sleep(1)
                return False
                
        # Co sekunde
        time.sleep(1)
        elapsed += 1
        
        if elapsed >= next_flavor:
            print(f"[{elapsed}/{dungeon.duration}s] " + get_random_flavor_text(player.party))
            next_flavor += random.randint(10, 15)
            
    print("\n--- UKOŃCZONO LOCH ---")
    print(f"Otrzymujesz {dungeon.exp_reward} EXP oraz {dungeon.gold_reward} złota!")
    player.add_exp(dungeon.exp_reward)
    player.gold += dungeon.gold_reward
    
    # 10% szansy na przedmiot
    if random.random() < 0.10 and dungeon.drop_pool:
        drop_id = random.choice(dungeon.drop_pool)
        player.add_to_inventory(drop_id)
        item_name = ITEMS_DB[drop_id].name
        print(f"*** Niesamowite! Znalazłeś unikalny przedmiot: {item_name}! ***")
        
    time.sleep(3)
    return True
