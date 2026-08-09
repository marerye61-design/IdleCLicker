import random
import math

class Enemy:
    def __init__(self, e_id, name, level, hp, atk, defence, exp_reward, gold_reward, img_key):
        self.e_id = e_id
        self.name = name
        self.level = level
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.defence = defence
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.img_key = img_key

class EnemyTemplate:
    def __init__(self, e_id, name, base_hp, hp_per_lvl, base_atk, atk_per_lvl, base_def, def_per_lvl, img_key, min_level=1):
        self.e_id = e_id
        self.name = name
        self.base_hp = base_hp
        self.hp_per_lvl = hp_per_lvl
        self.base_atk = base_atk
        self.atk_per_lvl = atk_per_lvl
        self.base_def = base_def
        self.def_per_lvl = def_per_lvl
        self.img_key = img_key
        self.min_level = min_level

    def generate(self, level):
        # Mnożnik endgame - potwory po 30 poziomie zyskują dodatkową moc, by wymusić Ulepszanie Przedmiotów
        scale_factor = 1.0 if level < 30 else 1.0 + (level - 30) * 0.03
        
        hp = int((self.base_hp + self.hp_per_lvl * (level - 1)) * scale_factor)
        atk = int((self.base_atk + self.atk_per_lvl * (level - 1)) * scale_factor)
        defence = int((self.base_def + self.def_per_lvl * (level - 1)) * scale_factor)
        
        # Nagrody skalują się z poziomem potwora i jego "trudnością" (statystykami)
        exp = int(level * 5 * random.uniform(0.9, 1.1) + hp * 0.2 + atk * 1)
        gold = int(level * 3 * random.uniform(0.9, 1.1) + defence * 1 + atk * 0.5)
        
        # Bezpieczniki dla najsłabszych potworów by nagroda była chociaż odrobinę sensowna
        exp = max(1, exp)
        gold = max(1, gold)
        
        return Enemy(self.e_id, self.name, level, hp, atk, defence, exp, gold, self.img_key)

TEMPLATES = [
    # Wczesna faza (Poziomy 1 - 10)
    EnemyTemplate("e_goblin", "Słaby Goblin", 20, 3.5, 5.0, 1.2, 1, 0.3, "e_goblin", 1),
    EnemyTemplate("e_wolf", "Leśny Wilk", 24, 4.0, 6.0, 1.3, 1, 0.3, "e_wolf", 1),
    EnemyTemplate("e_bandit", "Bandyta", 30, 4.5, 7.0, 1.4, 2, 0.4, "e_bandit", 2),
    EnemyTemplate("e_spider", "Wielki Pająk", 35, 5.0, 8.0, 1.5, 2, 0.5, "e_spider", 3),
    
    # Środkowa faza (Poziomy 10 - 25)
    EnemyTemplate("e_undead", "Nieumarły Żołnierz", 50, 7.0, 14.0, 2.0, 4, 0.8, "e_undead", 8),
    EnemyTemplate("e_fiend", "Bies", 60, 8.0, 16.0, 2.2, 5, 0.9, "e_fiend", 12),
    EnemyTemplate("e_orc", "Ork Wojownik", 75, 9.0, 19.0, 2.5, 6, 1.0, "e_orc", 15),
    EnemyTemplate("e_wraith", "Zjawa", 70, 8.5, 22.0, 2.8, 5, 0.9, "e_wraith", 18),
    
    # Zaawansowana faza (Poziomy 25 - 50)
    EnemyTemplate("e_gargoyle", "Gargulec", 130, 12.0, 35.0, 3.2, 10, 1.5, "e_gargoyle", 25),
    EnemyTemplate("e_treant", "Mroczny Ent", 170, 15.0, 30.0, 3.0, 15, 1.8, "e_treant", 30),
    EnemyTemplate("e_knight", "Przeklęty Rycerz", 150, 13.0, 40.0, 3.5, 16, 2.0, "e_knight", 35),
    
    # Pół-bossowie (Poziomy 50 - 75)
    EnemyTemplate("e_ogre", "Ogr Miażdżyciel", 320, 20.0, 75.0, 4.5, 25, 2.5, "e_ogre", 45),
    EnemyTemplate("e_cultist", "Mroczny Kultysta", 270, 18.0, 85.0, 5.0, 20, 2.2, "e_cultist", 50),
    
    # Bossowie End-game (Poziomy 75+)
    EnemyTemplate("e_golem", "Golem Ziemi", 550, 30.0, 140.0, 6.5, 45, 3.5, "e_golem", 70),
    EnemyTemplate("e_dragon", "Smok Cienia", 750, 40.0, 180.0, 8.0, 50, 4.0, "e_dragon", 85),
]

def get_expedition_choices(player_level, count=3):
    choices = []
    # Filtrujemy potwory, których gracz nie powinien jeszcze spotkać
    available = [t for t in TEMPLATES if player_level >= t.min_level - 5]
    if not available:
        available = [TEMPLATES[0]]

    # Pick random templates, allowing duplicates
    for _ in range(count):
        template = random.choice(available)
        
        # Skalowanie w dół i w górę (+2 poziomy maksymalnie dla rozsądnego balansu)
        min_lvl = max(1, player_level - 5)
        max_lvl = player_level + 2
        lvl = random.randint(min_lvl, max_lvl)
        
        choices.append(template.generate(lvl))
        
    # Sort them by level for a nicer UI experience
    choices.sort(key=lambda x: x.level)
    return choices

def calculate_player_dmg(player, enemy=None):
    p_atk = player.get_total_atk()
    if not enemy:
        return max(1, p_atk)
    
    # Obrażenia gracza = ATK gracza redukowana częściowo przez DEF potwora (min. 25% ATK)
    base_dmg = p_atk - int(enemy.defence * 0.4)
    min_dmg = max(1, int(p_atk * 0.25))
    final_dmg = max(min_dmg, base_dmg)
    
    variance = random.uniform(0.9, 1.1)
    return max(1, int(final_dmg * variance))

def calculate_enemy_dmg(enemy, player):
    e_atk = enemy.atk
    p_def = player.get_total_def()
    
    # Formuła procentowej redukcji pancerza (Armory Mitigation Formula)
    # Pancerz gracza zmniejsza obrażenia procentowo: REDUKCJA = DEF / (DEF + 80 + level * 4)
    mitigation_k = 80 + player.level * 4
    mitigation_pct = p_def / (p_def + mitigation_k)
    
    # Maksymalny cap redukcji pancerza wynosi 75% (potwory ZAWSZE zadają przynajmniej 25% swoich obrażeń!)
    mitigation_pct = min(0.75, mitigation_pct)
    
    raw_dmg = e_atk * (1.0 - mitigation_pct)
    variance = random.uniform(0.9, 1.1)
    final_dmg = int(raw_dmg * variance)
    
    return max(1, final_dmg)
