import time
from items import get_item, Equipment

class Player:
    def __init__(self, name="Bohater"):
        self.name = name
        self.gold = 0
        self.mana = 100
        self.max_mana = 100
        self.hp = 120
        self.max_hp = 120
        
        # Na start 5 mikstur życia
        self.inventory = [{"id": "pot_hp", "lvl": 0} for _ in range(5)]
        self.equipment = {
            "weapon": None,
            "armor": None,
            "helmet": None,
            "accessory": None
        }
        
        self.stats = {
            "total_clicks": 0,
            "base_atk": 12,
            "base_def": 10,
            "gold_per_click": 1,
            "gold_per_sec": 0,
            "mana_regen": 1,
            "bonus_loot_pct": 0,
            "crit_chance": 0
        }
        
        self.version = "1.1" # Wersja dla kompatybilności zapisów
        self.level = 1
        self.exp = 0
        self.stat_points = 0
        self.party = [] # lista odblokowanych towarzyszy w druzynie
        self.active_companion = None # ID dokładnie 1 aktywnego towarzysza walczącego w drużynie
        
        self.quests = []
        self.buildings = {} # {building_id: count}
        self.bestiary = {} # {enemy_name: count}
        self.dungeon_tickets = 3
        self.max_dungeon_tickets = 3
        self.last_dungeon_ticket_refresh = time.time()
        
        self.seen_cinematics = {}
        self.last_update_time = time.time()

    def migrate(self):
        """ Iteracja 4: Odporność na stare wersje zapisów (Backward compatibility) """
        if not hasattr(self, 'level'):
            self.level = 1; self.exp = 0; self.stat_points = 0
        if not hasattr(self, 'party'):
            self.party = []
        if not hasattr(self, 'active_companion'):
            self.active_companion = None
        if not hasattr(self, 'quests'):
            self.quests = []
        if not hasattr(self, 'bestiary'):
            self.bestiary = {}
        if not hasattr(self, 'seen_cinematics'):
            self.seen_cinematics = {}
            
        # Aktualizacja starych statystyk bazowych do nowego balansu (łatwiejszy początek)
        if getattr(self, 'stats', {}).get("base_atk", 0) < 12:
            self.stats["base_atk"] = 12
        if getattr(self, 'stats', {}).get("base_def", 0) < 10:
            self.stats["base_def"] = 10
        if "crit_chance" not in self.stats:
            self.stats["crit_chance"] = 0
        if getattr(self, 'max_hp', 0) < 120:
            self.max_hp = 120
            self.hp = 120
            
        # Aktualizacja pasywnego złota po nerfie budynków (30% mniej, nowy mnożnik)
        from market import BUILDINGS_DB
        self.stats["gold_per_sec"] = 0
        for b_id, count in getattr(self, 'buildings', {}).items():
            if b_id in BUILDINGS_DB:
                self.stats["gold_per_sec"] += BUILDINGS_DB[b_id].gold_per_sec * count
            
        # Migracja przedmiotów (Krok 3 - Kowalstwo) - zamiana stringów na słowniki z poziomem
        new_inv = []
        for item in getattr(self, 'inventory', []):
            if isinstance(item, str):
                new_inv.append({"id": item, "lvl": 0})
            else:
                new_inv.append(item)
        self.inventory = new_inv
        
        for k, v in self.equipment.items():
            if isinstance(v, str):
                self.equipment[k] = {"id": v, "lvl": 0}
            
        from quests import QUESTS_DB
        q_map = {q.quest_id: q for q in QUESTS_DB}
        
        # Jeśli gracz nie ma jeszcze listy zadań, inicjalizujemy całą bazę
        if not self.quests:
            from quests import get_all_quests
            self.quests = get_all_quests()
        else:
            for q in self.quests:
                if q.quest_id in q_map:
                    ref = q_map[q.quest_id]
                    q.name = ref.name
                    q.description = ref.description
                    q.requirements = ref.requirements
                    q.rewards = ref.rewards
                    q.unlock_level = ref.unlock_level
                    q.npc_id = getattr(ref, 'npc_id', 'innkeeper')
                    q.dialog_offer = getattr(ref, 'dialog_offer', '')
                    q.dialog_accept_reaction = getattr(ref, 'dialog_accept_reaction', '')
                    q.dialog_complete = getattr(ref, 'dialog_complete', '')
                if not hasattr(q, 'status'):
                    q.status = 'CLAIMED' if getattr(q, 'is_completed', False) else 'LOCKED'
                if not hasattr(q, 'progress') or not isinstance(q.progress, dict):
                    q.progress = {'kills': {}}

    def get_bestiary_bonus(self):
        """
        Zwraca mnożnik statystyk na podstawie zabitych potworów.
        Każde pełne 50 pokonanych potworów dowolnego typu daje +1% (0.01) do obrażeń całkowitych.
        Limit wynosi +100% (1.0).
        """
        total_kills = sum(self.bestiary.values())
        bonus = (total_kills // 50) * 0.01
        return min(1.0, bonus)

    def get_exp_required(self):
        # Nowy, zbalansowany wzór: ~19h łącznego czasu do 100 poziomu, brak załamań, skalowalność 100+
        return int(70 * (self.level ** 1.92))

    def add_exp(self, amount):
        self.exp += amount
        while self.exp >= self.get_exp_required():
            self.exp -= self.get_exp_required()
            self.level += 1
            self.stat_points += 3
            print(f"\n*** AWANS NA {self.level} POZIOM! Otrzymujesz pasywnie +2 ATK, +1 DEF, +10 Max HP. ***\n")
            # Heal player on level up
            self.hp = self.get_max_hp()
            
        req = self.get_exp_required()
        remaining = req - self.exp
        print(f" (EXP: {self.exp}/{req} | Brakuje: {remaining} do poziomu {self.level + 1})")

    def select_active_companion(self, npc_id):
        """ Wybiera 1 aktywnego towarzysza do drużyny w walce """
        if npc_id is None or npc_id in self.party:
            self.active_companion = npc_id
            return True
        return False

    def get_party_bonus(self):
        """ Zwraca bonusy TYLKO dla 1 aktywnego towarzysza walczącego w drużynie """
        bonus_atk = 0
        bonus_def = 0
        bonus_hp = 0
        
        c = getattr(self, 'active_companion', None)
        if not c:
            return {"atk": 0, "def": 0, "hp": 0}
            
        if c == "maslak":
            bonus_atk += int(10 + self.level * 2.0)
            bonus_hp += int(20 + self.level * 3.0)
        elif c == "damian":
            bonus_def += int(15 + self.level * 1.8)
            bonus_hp += int(40 + self.level * 4.0)
        elif c == "eczme":
            bonus_atk += int(20 + self.level * 3.0) # Eczme to silny atakujący (damage dealer)
        elif c == "pianek":
            bonus_def += int(25 + self.level * 2.5) # Pianek to pancerny czołg (tank)
            bonus_hp += int(60 + self.level * 5.0)
        elif c == "yomen":
            bonus_atk += int(15 + self.level * 2.2)
            bonus_def += int(10 + self.level * 1.2)
        elif c == "domcia":
            bonus_atk += int(12 + self.level * 1.5)
            bonus_def += int(12 + self.level * 1.5)
            bonus_hp += int(80 + self.level * 6.0) # Domcia to wsparcie ziołolecznictwa (support healer)
            
        return {"atk": bonus_atk, "def": bonus_def, "hp": bonus_hp}

    def get_total_atk(self):
        # Pasywny przyrost bez broni wynosi +2.0 ATK / poziom
        atk = self.stats["base_atk"] + int((self.level - 1) * 2.0)
        for item_dict in self.equipment.values():
            if item_dict:
                item = get_item(item_dict["id"])
                if item and hasattr(item, "stats"):
                    base = item.stats.get("atk", 0)
                    atk += int(base * (1.0 + 0.15 * item_dict.get("lvl", 0)))
        atk += self.get_party_bonus()["atk"]
        
        # Iteracja 5 (Bestiariusz) - mnożnik
        atk_multiplier = 1.0 + self.get_bestiary_bonus()
        return int(atk * atk_multiplier)

    def get_total_def(self):
        # Pasywny przyrost bez pancerza wynosi +1.0 DEF / poziom
        df = self.stats["base_def"] + int((self.level - 1) * 1.0)
        for item_dict in self.equipment.values():
            if item_dict:
                item = get_item(item_dict["id"])
                if item and hasattr(item, "stats"):
                    base = item.stats.get("def", 0)
                    df += int(base * (1.0 + 0.15 * item_dict.get("lvl", 0)))
        df += self.get_party_bonus()["def"]
        return df

    def get_total_crit(self):
        # Maks 30 ze statystyk (bazowe punkty), ale mogą być przekroczone przez przedmioty
        crit = min(30, self.stats.get("crit_chance", 0))
        for item_dict in self.equipment.values():
            if item_dict:
                item = get_item(item_dict["id"])
                if item and hasattr(item, "stats"):
                    base_crit = item.stats.get("crit_chance", 0)
                    crit += base_crit
        return crit

    def get_max_hp(self):
        # Pasywny przyrost HP wynosi +10 HP / poziom
        hp = self.max_hp + (self.level - 1) * 10
        for item_dict in self.equipment.values():
            if item_dict:
                item = get_item(item_dict["id"])
                if item and hasattr(item, "stats"):
                    base = item.stats.get("hp_max", 0)
                    hp += int(base * (1.0 + 0.15 * item_dict.get("lvl", 0)))
        hp += self.get_party_bonus()["hp"]
        return hp
        
    def add_to_inventory(self, item_id, modifier=None):
        self.inventory.append({"id": item_id, "lvl": 0, "modifier": modifier})
        
    def equip(self, item_dict):
        if item_dict in self.inventory:
            item = get_item(item_dict)
            if not item: return False
            slot = getattr(item, "slot", None)
            if slot and slot in self.equipment:
                # Jesli cos juz mamy w slocie, sciagamy to do plecaka
                if self.equipment[slot] is not None:
                    self.inventory.append(self.equipment[slot])
                # Zakladamy nowy przedmiot i usuwamy go z plecaka
                self.equipment[slot] = item_dict
                self.inventory.remove(item_dict)
                return True
            else:
                print("Tego przedmiotu nie można założyć.")
                return False
        else:
            print("Nie masz tego przedmiotu w ekwipunku.")
            return False
            
    def click(self):
        atk = self.get_total_atk()
        earned = self.stats["gold_per_click"] + atk
        self.gold += earned
        self.stats["total_clicks"] += 1
        return earned
        
    def update_offline_progress(self, is_offline=True):
        current_time = time.time()
        elapsed = current_time - self.last_update_time
        if elapsed > 0:
            earned_gold = int(elapsed * self.stats["gold_per_sec"])
            
            if not is_offline:
                self.gold += earned_gold
            
            # Odzyskiwanie many (działa w tle i w grze)
            self.mana = min(self.max_mana, self.mana + int(elapsed * self.stats["mana_regen"]))
            
            self.last_update_time = current_time
            if is_offline and elapsed >= 5:
                print("[Offline] Podczas twojej nieobecności zregenerowałeś manę. Budowle pasywne nie zarabiają, gdy gra jest wyłączona.")
