class Quest:
    def __init__(self, quest_id, name, description, requirements, rewards, unlock_level=1):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.requirements = requirements  # np. {'clicks': 100, 'gold': 500}
        self.rewards = rewards  # np. {'gold': 1000, 'item': 'wep_maslak'}
        self.unlock_level = unlock_level
        
        # STATUS: 'LOCKED', 'AVAILABLE', 'IN_PROGRESS', 'COMPLETED', 'CLAIMED'
        self.status = 'LOCKED'

    def update_status(self, player_level):
        if self.status == 'LOCKED' and player_level >= self.unlock_level:
            self.status = 'AVAILABLE'

    def accept(self):
        if self.status == 'AVAILABLE':
            self.status = 'IN_PROGRESS'
            self.progress = {'kills': {}}
            return True
        return False

    def check_completion(self, player):
        if self.status != 'IN_PROGRESS':
            return False
        
        prog = getattr(self, 'progress', {'kills': {}})
        
        for req, value in self.requirements.items():
            if req == 'clicks' and player.stats.get('total_clicks', 0) < value:
                return False
            if req == 'gold' and player.gold < value:
                return False
            if req == 'level' and getattr(player, 'level', 1) < value:
                return False
            if req == 'kills':
                for monster_name, count in value.items():
                    if prog.get('kills', {}).get(monster_name, 0) < count:
                        return False
                
        self.status = 'COMPLETED'
        return True

    def complete(self, player):
        """ Ta metoda sprawdza warunki w trakcie gry (w tle) """
        return self.check_completion(player)

    def claim_reward(self, player):
        if self.status == 'COMPLETED':
            self.status = 'CLAIMED'
            print(f"\n[!] Odebrano nagrodę za: {self.name}!")
            if 'gold' in self.rewards:
                player.gold += self.rewards['gold']
            if 'item' in self.rewards:
                player.add_to_inventory(self.rewards['item'])
            if 'party' in self.rewards:
                member = self.rewards['party']
                if member not in player.party:
                    player.party.append(member)
                if getattr(player, 'active_companion', None) is None:
                    player.active_companion = member
            return True
        return False

    # Na starcie kompatybilność, jeśli jest zaciągnięte ze starego save'a, upewnijmy się, że atrybuty istnieją.
    @property
    def is_completed(self):
        return self.status in ['COMPLETED', 'CLAIMED']
    @is_completed.setter
    def is_completed(self, value):
        if value:
            self.status = 'CLAIMED'
        else:
            self.status = 'AVAILABLE'


# Baza zadań od NPC w Tawernie
QUESTS_DB = [
    Quest(
        "q_party_maslak", 
        "Polowanie z Maślakiem", 
        "Maślak szuka kogoś doświadczonego w walce. Udowodnij swoją wartość i zabij 10 Leśnych Wilków.", 
        {"kills": {"Leśny Wilk": 10}}, 
        {"gold": 200, "item": "wep_maslak", "party": "maslak"},
        unlock_level=1
    ),
    Quest(
        "q_party_damian", 
        "Zlecenie Mytnika Damiana", 
        "Damian potrzebuje złota na naprawę swojego kurczącego się pancerza. Zdobądź 1000 złota.", 
        {"gold": 1000}, 
        {"gold": 500, "item": "arm_damian", "party": "damian"},
        unlock_level=2
    ),
    Quest(
        "q_party_eczme",
        "Trening Siatkówki Eczme",
        "Eczme szuka kogoś o silnym uderzeniu i szybkim refleksie. Osiągnij 5 poziom doświadczenia.",
        {"level": 5},
        {"gold": 1000, "party": "eczme"},
        unlock_level=5
    ),
    Quest(
        "q_party_pianek",
        "Siłownia u Pianka",
        "Pianek docenia tylko naprawdę wytrzymałych twardzieli. Osiągnij 8 poziom.",
        {"level": 8},
        {"gold": 1500, "item": "helm_pianek", "party": "pianek"},
        unlock_level=8
    ),
    Quest(
        "q_party_yomen",
        "Wielki Przekręt Yomena",
        "Yomen szuka zaufanego wspólnika do nowego kanałowego interesu. Osiągnij 12 poziom.",
        {"level": 12},
        {"gold": 2500, "item": "wep_yomen", "party": "yomen"},
        unlock_level=12
    ),
    Quest(
        "q_party_domcia",
        "Zielarski Zbiór Domci",
        "Domcia szuka towarzysza z dobrą aurą do poszukiwań rzadkich ziół. Osiągnij 15 poziom.",
        {"level": 15},
        {"gold": 4000, "item": "acc_domcia", "party": "domcia"},
        unlock_level=15
    ),
]

def get_all_quests():
    import copy
    return copy.deepcopy(QUESTS_DB)
