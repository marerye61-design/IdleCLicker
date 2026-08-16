import random

class Bounty:
    def __init__(self, b_id, title, description, target_type, target_name, target_count, gold_reward, exp_reward, item_reward=None):
        self.b_id = b_id
        self.title = title
        self.description = description
        self.target_type = target_type # 'kill', 'dungeon', 'upgrade'
        self.target_name = target_name
        self.target_count = target_count
        self.current_count = 0
        self.gold_reward = gold_reward
        self.exp_reward = exp_reward
        self.item_reward = item_reward
        self.status = "AVAILABLE" # 'AVAILABLE', 'IN_PROGRESS', 'COMPLETED', 'CLAIMED'

    def accept(self):
        if self.status == "AVAILABLE":
            self.status = "IN_PROGRESS"
            return True
        return False

    def add_progress(self, count=1):
        if self.status == "IN_PROGRESS":
            self.current_count = min(self.target_count, self.current_count + count)
            if self.current_count >= self.target_count:
                self.status = "COMPLETED"
                return True
        return False

    def is_completed(self):
        return self.current_count >= self.target_count

    def claim_reward(self, player):
        if self.status == "COMPLETED":
            self.status = "CLAIMED"
            player.gold += self.gold_reward
            player.add_exp(self.exp_reward)
            if self.item_reward:
                from items import get_item
                item = get_item(self.item_reward)
                if item:
                    player.add_to_inventory(item.to_dict(), is_reward=True)
            return True
        return False

def generate_daily_bounties(player_level):
    """ Generuje 3 zbalansowane zlecenia z tablicy ogłoszeń dopasowane do poziomu gracza """
    lvl = max(1, player_level)
    
    # Pula potworów w zależności od przedziału poziomu
    if lvl < 10:
        monster_pool = [("Słaby Goblin", 5, 8), ("Leśny Wilk", 4, 7), ("Bandyta", 4, 6)]
    elif lvl < 25:
        monster_pool = [("Wielki Pająk", 6, 10), ("Nieumarły Żołnierz", 5, 8), ("Bies", 4, 7)]
    elif lvl < 45:
        monster_pool = [("Ork Wojownik", 7, 12), ("Zjawa", 6, 10), ("Gargulec", 5, 8)]
    else:
        monster_pool = [("Mroczny Ent", 8, 14), ("Przeklęty Rycerz", 6, 10), ("Ogr Miażdżyciel", 5, 8)]
        
    random.shuffle(monster_pool)
    
    # 1. Zlecenie na potwora A
    m1_name, min_c, max_c = monster_pool[0]
    count1 = random.randint(min_c, max_c)
    gold1 = int((lvl * 45 + 120) * (count1 / 5.0))
    exp1 = int((lvl * 35 + 90) * (count1 / 5.0))
    b1 = Bounty(
        "bounty_1",
        f"Polowanie: {m1_name}",
        f"Karczmarz Barnaba poszukuje śmiałka, który przetrzebi okolicę z {m1_name.lower()}ów.",
        "kill",
        m1_name,
        count1,
        gold1,
        exp1
    )
    
    # 2. Zlecenie na potwora B
    m2_name, min_c2, max_c2 = monster_pool[1]
    count2 = random.randint(min_c2, max_c2)
    gold2 = int((lvl * 55 + 150) * (count2 / 5.0))
    exp2 = int((lvl * 45 + 110) * (count2 / 5.0))
    item2 = "pot_hp" if random.random() < 0.5 else None
    b2 = Bounty(
        "bounty_2",
        f"Zlecenie: {m2_name}",
        f"Kupcy proszą o ochronę traktu przed napaściami {m2_name.lower()}ów.",
        "kill",
        m2_name,
        count2,
        gold2,
        exp2,
        item_reward=item2
    )
    
    # 3. Zlecenie na aktywność (Loch lub Kowal)
    if random.random() < 0.5:
        b3 = Bounty(
            "bounty_3",
            "Wyprawa w Głąb Lochu",
            "Zbadaj mroczne korytarze i przetrwaj pełną eksplorację dowolnego lochu.",
            "dungeon",
            "any_dungeon",
            1,
            int(lvl * 80 + 250),
            int(lvl * 60 + 200),
            item_reward="pot_hp"
        )
    else:
        b3 = Bounty(
            "bounty_3",
            "Wzmocnienie Ekwipunku",
            "Odwiedź miejskiego Kowala i przekuj dowolny element swojego rynsztunku.",
            "upgrade",
            "blacksmith_upgrade",
            1,
            int(lvl * 60 + 180),
            int(lvl * 50 + 150)
        )
        
    return [b1, b2, b3]
