import time
import random
from items import get_item, Equipment

EXPEDITION_TYPES = {
    "meadow": {
        "id": "meadow",
        "name": "Zwiady w Ziołowych Zaroślach",
        "icon": "",
        "duration": 300, # 5 minut
        "desc": "Zbieranie ziół, leśnych grzybów i drobnego złota.",
        "reward_herbs": ["herb_amanita", "herb_moss"],
        "gold_range": (150, 350)
    },
    "mine": {
        "id": "mine",
        "name": "Wyprawa do Starej Kopalni",
        "icon": "",
        "duration": 900, # 15 minut
        "desc": "Poszukiwanie rdzeni skalnych, rudy i magicznych klejnotów.",
        "reward_items": ["ing_core"],
        "reward_gems": ["gem_ruby", "gem_sapphire", "gem_topaz", "gem_emerald", "gem_amethyst"],
        "gold_range": (500, 1200)
    },
    "catacombs": {
        "id": "catacombs",
        "name": "Zapomniane Katakumby",
        "icon": "",
        "duration": 1800, # 30 minut
        "desc": "Niebezpieczna ekspedycja po ektoplazmę, jady, wielkie skarby i rzadkie zioła.",
        "reward_items": ["ing_ectoplasm", "ing_venom"],
        "reward_herbs": ["herb_flower", "herb_mystery"],
        "gold_range": (1500, 3500)
    }
}

TALENT_DEFINITIONS = {
    "berserker": {
        "name": "Ścieżka Berserkera",
        "icon": "",
        "color": "#e74c3c",
        "desc": "Agresja i krytyki: +4% ATK gdy HP < 50% oraz +6% dmg kryta na każdy punkt.",
        "max_points": 10
    },
    "defender": {
        "name": "Ścieżka Obrońcy",
        "icon": "",
        "color": "#3498db",
        "desc": "Niezłomność: odbija 5% obrażeń wroga (Thorns) i regeneruje 1% Max HP co turę na punkt.",
        "max_points": 10
    },
    "rogue": {
        "name": "Ścieżka Awanturnika",
        "icon": "",
        "color": "#f1c40f",
        "desc": "Zwinność: +10% dmg kliknięcia bojowego, +3% do złota i +2% kradzieży życia (Lifesteal) na punkt.",
        "max_points": 10
    }
}

class Player:
    def __init__(self, name="Bohater"):
        self.name = name
        self.gold = 0
        self.mana = 100
        self.max_mana = 100
        self.hp = 85
        self.max_hp = 85
        
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
            "base_atk": 8,
            "base_def": 4,
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
        
        self.inventory_stash = [] # Przechowane przedmioty u Karczmarza Barnaby (gdy ekwipunek był pełny)
        self.seen_cinematics = {}
        
        # === NOWE SYSTEMY: OSIĄGNIĘCIA, ALCHEMIA I BUFFY ===
        self.achievements = {} # {ach_id: {"completed": bool, "claimed": bool, "progress": int}}
        self.permanent_perks = [] # lista ID odblokowanych stałych perków z osiągnięć
        self.achievement_stats = {
            "total_kills": 0,
            "total_crits": 0,
            "boss_ptys_kills": 0,
            "boss_kollman_kills": 0,
            "dungeons_cleared": 0,
            "upgrades_done": 0,
            "max_upgrade_level": 0,
            "gems_socketed": 0,
            "herbs_harvested": 0,
            "potions_brewed": 0,
            "psychedelic_brewed": 0,
            "total_gold_earned": 0
        }
        self.herb_garden = [
            {"type": "herb_amanita", "planted_at": time.time(), "growth_time": 45, "unlocked": False},
            {"type": "herb_moss", "planted_at": time.time(), "growth_time": 60, "unlocked": False},
            {"type": "herb_flower", "planted_at": time.time(), "growth_time": 75, "unlocked": False},
            {"type": "herb_mystery", "planted_at": time.time(), "growth_time": 120, "unlocked": False}
        ]
        self.active_buffs = {} # {buff_id: remaining_fights}
        self.combat_shield = 0
        self.talent_points = 0
        self.talents = {"berserker": 0, "defender": 0, "rogue": 0}
        self.expeditions = {}
        self.settings = {"autosave_seconds": 60, "reduced_effects": False, "inventory_sort": "recent"}
        self.reward_history = []
        self.daily_challenges = {"date": "", "items": []}
        self.last_update_time = time.time()

    def migrate(self):
        """ Iteracja 4: Odporność na stare wersje zapisów (Backward compatibility) """
        self.version = "1.1"
        if not hasattr(self, 'inventory_stash'):
            self.inventory_stash = []
        if not hasattr(self, 'achievements'):
            self.achievements = {}
        if not hasattr(self, 'permanent_perks'):
            self.permanent_perks = []
        if not hasattr(self, 'achievement_stats'):
            self.achievement_stats = {
                "total_kills": 0, "total_crits": 0, "boss_ptys_kills": 0, "boss_kollman_kills": 0,
                "dungeons_cleared": 0, "upgrades_done": 0, "max_upgrade_level": 0, "gems_socketed": 0,
                "herbs_harvested": 0, "potions_brewed": 0, "psychedelic_brewed": 0, "total_gold_earned": 0
            }
        if not hasattr(self, 'herb_garden') or not self.herb_garden:
            self.herb_garden = [
                {"type": "herb_amanita", "planted_at": time.time(), "growth_time": 45, "unlocked": False},
                {"type": "herb_moss", "planted_at": time.time(), "growth_time": 60, "unlocked": False},
                {"type": "herb_flower", "planted_at": time.time(), "growth_time": 75, "unlocked": False},
                {"type": "herb_mystery", "planted_at": time.time(), "growth_time": 120, "unlocked": False}
            ]
        else:
            has_explicit_locks = any("unlocked" in p for p in self.herb_garden)
            if not has_explicit_locks:
                is_fresh = getattr(self, 'level', 1) <= 1 and not getattr(self, 'party', []) and getattr(self, 'achievement_stats', {}).get("herbs_harvested", 0) == 0
                if is_fresh:
                    for p in self.herb_garden:
                        p["unlocked"] = False
                else:
                    party = getattr(self, 'party', [])
                    if len(self.herb_garden) > 0:
                        self.herb_garden[0]["unlocked"] = True
                        self.garden_plot_0_leased = True
                    if len(self.herb_garden) > 1:
                        self.herb_garden[1]["unlocked"] = ("eczme" in party)
                    if len(self.herb_garden) > 2:
                        self.herb_garden[2]["unlocked"] = ("pianek" in party or "damian" in party)
                    if len(self.herb_garden) > 3:
                        self.herb_garden[3]["unlocked"] = ("domcia" in party)
            else:
                for p in self.herb_garden:
                    p.setdefault("unlocked", False)
            party = getattr(self, 'party', [])
            if not getattr(self, 'garden_plot_0_leased', False) and len(self.herb_garden) > 0:
                self.herb_garden[0]["unlocked"] = False
            if len(self.herb_garden) > 1 and "eczme" not in party:
                self.herb_garden[1]["unlocked"] = False
            if len(self.herb_garden) > 2 and ("pianek" not in party and "damian" not in party):
                self.herb_garden[2]["unlocked"] = False
            if len(self.herb_garden) > 3 and "domcia" not in party:
                self.herb_garden[3]["unlocked"] = False
        if not hasattr(self, 'active_buffs'):
            self.active_buffs = {}
        if not hasattr(self, 'settings') or not isinstance(self.settings, dict):
            self.settings = {"autosave_seconds": 60, "reduced_effects": False, "inventory_sort": "recent"}
        else:
            defaults = {"autosave_seconds": 60, "reduced_effects": False, "inventory_sort": "recent"}
            for key, value in defaults.items():
                self.settings.setdefault(key, value)
        if not hasattr(self, 'reward_history') or not isinstance(self.reward_history, list):
            self.reward_history = []
        if not hasattr(self, 'daily_challenges') or not isinstance(self.daily_challenges, dict):
            self.daily_challenges = {"date": "", "items": []}
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
        if not hasattr(self, 'bounties'):
            self.bounties = []
        earned_talents = max(0, (getattr(self, 'level', 1) - 5) // 5) if getattr(self, 'level', 1) >= 10 else 0
        spent_talents = sum(getattr(self, 'talents', {}).values()) if hasattr(self, 'talents') and isinstance(self.talents, dict) else 0
        if not hasattr(self, 'talent_points') or (self.talent_points == 0 and spent_talents == 0 and earned_talents > 0) or (getattr(self, 'talent_points', 0) + spent_talents > earned_talents):
            self.talent_points = max(0, earned_talents - spent_talents)
        if not hasattr(self, 'talents') or not isinstance(self.talents, dict):
            self.talents = {"berserker": 0, "defender": 0, "rogue": 0}
        else:
            for k in ["berserker", "defender", "rogue"]:
                self.talents.setdefault(k, 0)
        if not hasattr(self, 'expeditions') or not isinstance(self.expeditions, dict):
            self.expeditions = {}
            
        # Bezpieczna normalizacja / migracja statystyk bazowych
        if getattr(self, 'level', 1) == 1 and getattr(self, 'stats', {}).get("base_atk", 8) == 12 and getattr(self, 'stats', {}).get("base_def", 4) == 10 and getattr(self, 'max_hp', 85) == 120:
            self.stats["base_atk"] = 8
            self.stats["base_def"] = 4
            self.max_hp = 85
            self.hp = 85
        else:
            if getattr(self, 'stats', {}).get("base_atk", 0) <= 0:
                self.stats["base_atk"] = 8
            if getattr(self, 'stats', {}).get("base_def", 0) <= 0:
                self.stats["base_def"] = 4
            if getattr(self, 'max_hp', 0) <= 0:
                self.max_hp = 85
                self.hp = 85
        if "crit_chance" not in self.stats:
            self.stats["crit_chance"] = 0
        if "bonus_loot_pct" not in self.stats:
            self.stats["bonus_loot_pct"] = 0
            
        # Aktualizacja pasywnego złota z uwzględnieniem synergii towarzyszy
        self.recalculate_gold_per_sec()
            
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
        if getattr(self, 'permanent_perks', None) and "perk_exp_master" in self.permanent_perks:
            amount = int(amount * 1.05)
        self.exp += amount
        while self.exp >= self.get_exp_required():
            self.exp -= self.get_exp_required()
            self.level += 1
            self.stat_points += 3
            if self.level >= 10 and self.level % 5 == 0:
                self.talent_points += 1
                print(f"*** OTRZYMUJESZ 1 PUNKT TALENTU! (Poziom {self.level}) ***\n")
            print(f"\n*** AWANS NA {self.level} POZIOM! Otrzymujesz pasywnie +1.2 ATK, +0.6 DEF, +6 Max HP. ***\n")
            # Zwiększamy HP jedynie o +6 z nowego poziomu, bez pełnego leczenia
            self.hp = min(self.get_max_hp(), self.hp + 6)
            
        req = self.get_exp_required()
        remaining = req - self.exp
        print(f" (EXP: {self.exp}/{req} | Brakuje: {remaining} do poziomu {self.level + 1})")

    def recalculate_gold_per_sec(self):
        """Przelicza pasywny przychód złota/s z budynków z uwzględnieniem synergii towarzyszy."""
        from market import BUILDINGS_DB, get_building_synergy_multiplier
        total_gps = 0
        for b_id, count in getattr(self, 'buildings', {}).items():
            if b_id in BUILDINGS_DB and count > 0:
                base_gps = BUILDINGS_DB[b_id].gold_per_sec * count
                mult = get_building_synergy_multiplier(self, b_id)
                total_gps += int(base_gps * mult)
        if not hasattr(self, 'stats'):
            self.stats = {}
        self.stats["gold_per_sec"] = total_gps
        return total_gps

    def select_active_companion(self, npc_id):
        """ Wybiera 1 aktywnego towarzysza do drużyny w walce """
        if npc_id is None or npc_id in self.party:
            self.active_companion = npc_id
            self.recalculate_gold_per_sec()
            return True
        return False

    def is_plot_unlocked(self, plot_idx):
        """Sprawdza, czy grządka o danym indeksie jest odblokowana."""
        if not hasattr(self, 'herb_garden') or plot_idx < 0 or plot_idx >= len(self.herb_garden):
            return False
        return self.herb_garden[plot_idx].get("unlocked", False)

    def unlock_garden_plot(self, plot_idx):
        """Odblokowuje grządkę o danym indeksie i rozpoczyna cykl wzrostu."""
        if not hasattr(self, 'herb_garden') or plot_idx < 0 or plot_idx >= len(self.herb_garden):
            return False
        plot = self.herb_garden[plot_idx]
        if not plot.get("unlocked", False):
            plot["unlocked"] = True
            plot["planted_at"] = time.time()
            return True
        return False

    def get_unlocked_plots_count(self):
        """Zwraca liczbę odblokowanych grządek w ogrodzie."""
        if not hasattr(self, 'herb_garden'):
            return 0
        return sum(1 for p in self.herb_garden if p.get("unlocked", False))

    def get_combat_click_dmg(self):
        """Zwraca obrażenia zadawane kliknięciem we wroga podczas walki."""
        base = max(2, int(self.get_total_atk() * 0.18))
        rogue_click = self.get_talent_bonus("click_dmg")
        return int(base * (1.0 + rogue_click))

    def absorb_shield_hit(self, damage_amount=1):
        """Pochłania obrażenia wroga z puli punktów tarczy bojowej i zwraca pozostałe nieskorelowane obrażenia."""
        dmg = max(0, int(damage_amount))
        cur_shield = getattr(self, 'combat_shield', 0)
        if cur_shield > 0:
            if cur_shield >= dmg:
                self.combat_shield -= dmg
                return 0
            else:
                rem_dmg = dmg - cur_shield
                self.combat_shield = 0
                return rem_dmg
        return dmg

    def get_companion_ultimate_info(self):
        """Zwraca definicję unikalnej zdolności specjalnej aktywnego towarzysza ściśle powiązanej z jego lore i charakterem."""
        comp = getattr(self, 'active_companion', None)
        if not comp:
            return None
        SKILLS = {
            "eczme": {
                "id": "eczme_spike",
                "name": "Ścina Przeznaczenia",
                "icon": "",
                "cooldown": 4,
                "desc": "Potężny atak 5-kilogramową Skórzaną Kulą Przeznaczenia (220% ATK) prosto w twarz wroga, ogłuszający go na 1 turę!",
                "dmg_mult": 2.2,
                "stun_turns": 1
            },
            "pianek": {
                "id": "pianek_flex",
                "name": "Napięcie Bicepsa",
                "icon": "",
                "cooldown": 4,
                "desc": "Maksymalna pompa białkowa! Pianek rzuca kowadłem we wroga (180% ATK) i napina mięśnie, dając bohaterowi barierę tarczy na 30% Max HP!",
                "dmg_mult": 1.8,
                "shield_pct": 30
            },
            "domcia": {
                "id": "domcia_smoke",
                "name": "Fioletowy Horyzont",
                "icon": "",
                "cooldown": 4,
                "desc": "Gęsty obłok ziół i zarodników Amanity: leczy bohatera o 30% Max HP, a zdezorientowany wróg zaczyna 'słyszeć kolory' i pudłuje w kolejnej turze!",
                "heal_pct": 30,
                "blind_turns": 1
            },
            "damian": {
                "id": "damian_tankard",
                "name": "Rycerski Toast",
                "icon": "",
                "cooldown": 4,
                "desc": "Damian wypija kufel mocnego ale i uderza z furią (200% ATK), po czym rozkłada Niezłomną Tarczę zmniejszającą otrzymywane obrażenia!",
                "dmg_mult": 2.0,
                "shield_pct": 20
            },
            "maslak": {
                "id": "maslak_donut",
                "name": "Lukrowany Pączek",
                "icon": "",
                "cooldown": 3,
                "desc": "Maślak częstuje pysznym, ciepłym pączkiem: przywraca bohaterowi 35% Max HP i wyciąga ze skrytki dodatkowe złoto!",
                "heal_pct": 35,
                "bonus_gold": True
            },
            "yomen": {
                "id": "yomen_wrench",
                "name": "Rzut Czternastką",
                "icon": "",
                "cooldown": 4,
                "desc": "Szczurzy alchemik ciska zardzewiałym kluczem czternastką i mieszanką oleju silnikowego, zadając 260% ATK gwarantowanym krytykiem!",
                "dmg_mult": 2.6,
                "force_crit": True
            }
        }
        return SKILLS.get(comp)

    def invest_talent(self, path):
        """Inwestuje 1 punkt talentu w wybraną ścieżkę specjalizacji."""
        if getattr(self, 'talent_points', 0) <= 0:
            return False
        if not hasattr(self, 'talents'):
            self.talents = {"berserker": 0, "defender": 0, "rogue": 0}
        cur = self.talents.get(path, 0)
        if cur >= 10:
            return False
        self.talent_points -= 1
        self.talents[path] = cur + 1
        return True

    def get_talent_bonus(self, arg1, arg2=None):
        """Zwraca wartość procentową/ułamkową bonusu z drzewka talentów.
        Wspiera wywołania z 1 argumentem: get_talent_bonus('crit_dmg_mult')
        oraz z 2 argumentami: get_talent_bonus('berserker', 'lifesteal_pct').
        """
        talents = getattr(self, 'talents', {})
        if arg2 is not None:
            tree = arg1
            bonus_type = arg2
        else:
            tree = None
            bonus_type = arg1

        if bonus_type == "low_hp_atk":
            return talents.get("berserker", 0) * 0.04
        elif bonus_type == "crit_dmg_mult":
            return talents.get("berserker", 0) * 0.06
        elif bonus_type == "thorns_pct":
            return talents.get("defender", 0) * 0.05
        elif bonus_type == "regen_turn_pct":
            return talents.get("defender", 0) * 0.01
        elif bonus_type == "click_dmg":
            return talents.get("rogue", 0) * 0.10
        elif bonus_type == "bonus_gold":
            return talents.get("rogue", 0) * 0.03
        elif bonus_type == "lifesteal_pct":
            pts = talents.get(tree, 0) if (tree and tree in talents and talents.get(tree, 0) > 0) else max(talents.get("rogue", 0), talents.get("berserker", 0))
            return pts * 0.02
        elif bonus_type == "dodge_pct":
            pts = talents.get(tree, 0) if (tree and tree in talents and talents.get(tree, 0) > 0) else talents.get("rogue", 0)
            return pts * 0.03
        return 0.0

    def start_expedition(self, comp_id, exp_type):
        """Wysyła nieaktywnego towarzysza na misję czasową."""
        if comp_id not in self.party:
            return False
        if comp_id == self.active_companion:
            return False
        if not hasattr(self, 'expeditions'):
            self.expeditions = {}
        if comp_id in self.expeditions:
            return False
        if exp_type not in EXPEDITION_TYPES:
            return False
        self.expeditions[comp_id] = {
            "exp_type": exp_type,
            "start_time": time.time(),
            "duration": EXPEDITION_TYPES[exp_type]["duration"]
        }
        return True

    def is_expedition_ready(self, comp_id):
        """Sprawdza, czy wyprawa danego towarzysza została ukończona."""
        if not hasattr(self, 'expeditions') or comp_id not in self.expeditions:
            return False
        exp = self.expeditions[comp_id]
        elapsed = time.time() - exp.get("start_time", 0)
        return elapsed >= exp.get("duration", 0)

    def get_expedition_remaining_sec(self, comp_id):
        """Zwraca liczbę sekund do powrotu towarzysza z wyprawy."""
        if not hasattr(self, 'expeditions') or comp_id not in self.expeditions:
            return 0
        exp = self.expeditions[comp_id]
        elapsed = time.time() - exp.get("start_time", 0)
        return max(0, int(exp.get("duration", 0) - elapsed))

    def claim_expedition(self, comp_id):
        """Odbiera nagrody z ukończonej wyprawy towarzysza."""
        if not hasattr(self, 'expeditions') or comp_id not in self.expeditions:
            return None
        exp_data = self.expeditions[comp_id]
        if not self.is_expedition_ready(comp_id):
            return None
        exp_type = exp_data.get("exp_type", "meadow")
        info = EXPEDITION_TYPES.get(exp_type, EXPEDITION_TYPES["meadow"])
        
        gold_min, gold_max = info.get("gold_range", (100, 200))
        gold_reward = random.randint(gold_min, gold_max)
        rogue_gold = self.get_talent_bonus("bonus_gold")
        if rogue_gold > 0:
            gold_reward = int(gold_reward * (1.0 + rogue_gold))
        self.add_gold(gold_reward, "Ekspedycja")
        
        rewards_list = []
        if "reward_herbs" in info and info["reward_herbs"]:
            h = random.choice(info["reward_herbs"])
            self.add_to_inventory(h, is_reward=True)
            rewards_list.append(h)
        if "reward_items" in info and info["reward_items"]:
            it = random.choice(info["reward_items"])
            self.add_to_inventory(it, is_reward=True)
            rewards_list.append(it)
        if "reward_gems" in info and info["reward_gems"]:
            g = random.choice(info["reward_gems"])
            self.add_to_inventory(g, is_reward=True)
            rewards_list.append(g)
            
        del self.expeditions[comp_id]
        return {
            "comp_id": comp_id,
            "exp_name": info["name"],
            "gold": gold_reward,
            "items": rewards_list
        }

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
            bonus_atk += int(10 + self.level * 1.5)
            bonus_hp += int(35 + self.level * 3.5)
        if getattr(self, 'permanent_perks', None) and "perk_party_synergy" in self.permanent_perks:
            bonus_atk = int(bonus_atk * 1.10)
            bonus_def = int(bonus_def * 1.10)
            bonus_hp = int(bonus_hp * 1.10)
            
        return {"atk": bonus_atk, "def": bonus_def, "hp": bonus_hp}

    def get_gems_bonus(self):
        """Kalkulacja bonusów z klejnotów wprawionych we wszystkich założonych przedmiotach (skalowanych z tierem sprzętu)."""
        from gems import GEMS_DB
        gem_mult = 1.10 if getattr(self, 'permanent_perks', None) and "perk_gem_resonance" in self.permanent_perks else 1.0
        
        bonus = {
            "atk": 0, "def": 0, "hp_max": 0, "crit_chance": 0, 
            "double_strike_pct": 0, "bonus_gold_pct": 0, "bonus_loot_pct": 0
        }
        
        for item_dict in self.equipment.values():
            if item_dict and isinstance(item_dict, dict) and "sockets" in item_dict:
                item_obj = get_item(item_dict.get("id"))
                item_lvl = getattr(item_obj, "level_req", 1) if item_obj else 1
                for gem_id in item_dict["sockets"]:
                    if gem_id and gem_id in GEMS_DB:
                        gem = GEMS_DB[gem_id]
                        scaled_stats = gem.get_stats_for_level(item_lvl)
                        for s_key, s_val in scaled_stats.items():
                            if s_key in bonus:
                                bonus[s_key] += int(s_val * gem_mult)
        return bonus

    def get_total_atk(self):
        # Pasywny przyrost bez broni wynosi +1.2 ATK / poziom
        atk = self.stats["base_atk"] + int((self.level - 1) * 1.2)
        for item_dict in self.equipment.values():
            if item_dict:
                item = get_item(item_dict)
                if item and hasattr(item, "stats"):
                    base = item.stats.get("atk", 0)
                    atk += int(base * (1.0 + 0.15 * item_dict.get("lvl", 0)))
        atk += self.get_party_bonus()["atk"]
        atk += self.get_gems_bonus()["atk"]
        
        # Iteracja 5 (Bestiariusz) - mnożnik
        atk_multiplier = 1.0 + self.get_bestiary_bonus()
        
        # Stały perk z osiągnięć: Żniwiarz Cienia (+5% ATK)
        if getattr(self, 'permanent_perks', None) and "perk_slayer" in self.permanent_perks:
            atk_multiplier += 0.05
            
        # Aktywny eliksir: Eliksir Berserkera (+35% ATK)
        if getattr(self, 'active_buffs', None) and self.active_buffs.get("elixir_berserk", 0) > 0:
            atk_multiplier += 0.35
            
        return int(atk * atk_multiplier)

    def get_total_def(self):
        # Pasywny przyrost bez pancerza wynosi +0.6 DEF / poziom
        df = self.stats["base_def"] + int((self.level - 1) * 0.6)
        for item_dict in self.equipment.values():
            if item_dict:
                item = get_item(item_dict)
                if item and hasattr(item, "stats"):
                    base = item.stats.get("def", 0)
                    df += int(base * (1.0 + 0.15 * item_dict.get("lvl", 0)))
        df += self.get_party_bonus()["def"]
        df += self.get_gems_bonus()["def"]
        
        # Pasywka Pianka: "Żelazna Pompa" (+25% DEF gdy zdrowie spadnie poniżej 60%)
        if getattr(self, 'active_companion', None) == "pianek":
            if self.get_max_hp() > 0 and (self.hp / self.get_max_hp()) < 0.60:
                df = int(df * 1.25)
                
        # Aktywny eliksir: Mikstura Kamiennej Skóry (+35% DEF)
        if getattr(self, 'active_buffs', None) and self.active_buffs.get("elixir_stone_skin", 0) > 0:
            df = int(df * 1.35)
            
        return df

    def get_total_crit(self):
        # Maks 30 ze statystyk (bazowe punkty), ale mogą być przekroczone przez przedmioty i klejnoty
        crit = min(30, self.stats.get("crit_chance", 0))
        for item_dict in self.equipment.values():
            if item_dict:
                item = get_item(item_dict)
                if item and hasattr(item, "stats"):
                    base_crit = item.stats.get("crit_chance", 0)
                    crit += base_crit
        crit += self.get_gems_bonus()["crit_chance"]
        
        # Stały perk z osiągnięć: Precyzja Zabójcy (+3% KRYT)
        if getattr(self, 'permanent_perks', None) and "perk_crit_master" in self.permanent_perks:
            crit += 3
            
        # Aktywny eliksir: Ekstrakt Nieznanej Głębi (+50% KRYT)
        if getattr(self, 'active_buffs', None) and self.active_buffs.get("elixir_psychedelic", 0) > 0:
            crit += 50
            
        return crit

    def get_max_hp(self):
        # Pasywny przyrost HP wynosi +6 HP / poziom
        hp = self.max_hp + int((self.level - 1) * 6)
        for item_dict in self.equipment.values():
            if item_dict:
                item = get_item(item_dict)
                if item and hasattr(item, "stats"):
                    base = item.stats.get("hp_max", 0)
                    hp += int(base * (1.0 + 0.15 * item_dict.get("lvl", 0)))
        hp += self.get_party_bonus()["hp"]
        hp += self.get_gems_bonus()["hp_max"]
        return hp

    def get_double_strike_chance(self):
        chance = self.get_gems_bonus().get("double_strike_pct", 0)
        if getattr(self, 'active_buffs', None) and self.active_buffs.get("elixir_swiftness", 0) > 0:
            chance += 15
        return chance

    def record_achievement_stat(self, key, value=1, mode="add"):
        """Aktualizuje statystyki do osiągnięć."""
        if not hasattr(self, 'achievement_stats'):
            self.achievement_stats = {}
        if mode == "add":
            self.achievement_stats[key] = self.achievement_stats.get(key, 0) + value
        elif mode == "max":
            self.achievement_stats[key] = max(self.achievement_stats.get(key, 0), value)
        elif mode == "set":
            self.achievement_stats[key] = value

    def record_reward(self, source, gold=0, exp=0, item=None):
        """Store a compact, bounded history of rewards for the journal and daily challenges."""
        entry = {"time": time.time(), "source": str(source), "gold": int(gold), "exp": int(exp), "item": item}
        self.reward_history.append(entry)
        del self.reward_history[:-100]
        if gold > 0:
            self.record_achievement_stat("total_gold_earned", int(gold), mode="add")
        self.update_daily_challenge_progress(source, gold, exp, item)

    def add_gold(self, amount, source="Nagroda", apply_greed=True, exp=0, item=None):
        amount = int(amount)
        if apply_greed and getattr(self, "permanent_perks", None) and "perk_greed" in self.permanent_perks:
            amount = int(amount * 1.10)
        self.gold += amount
        self.record_reward(source, gold=amount, exp=exp, item=item)
        return amount

    def ensure_daily_challenges(self):
        from datetime import date
        today = date.today().isoformat()
        if getattr(self, "daily_challenges", {}).get("date") != today:
            self.daily_challenges = {
                "date": today,
                "items": [
                    {"id": "daily_kills", "label": "Pokonaj 5 potworów", "target": 5, "progress": 0, "reward": 250, "kind": "kill", "claimed": False},
                    {"id": "daily_gold", "label": "Zdobądź 1000 złota", "target": 1000, "progress": 0, "reward": 300, "kind": "gold", "claimed": False},
                    {"id": "daily_dungeon", "label": "Ukończ loch", "target": 1, "progress": 0, "reward": 500, "kind": "dungeon", "claimed": False},
                ],
            }
        return self.daily_challenges["items"]

    def update_daily_challenge_progress(self, source, gold=0, exp=0, item=None):
        for challenge in self.ensure_daily_challenges():
            if challenge["kind"] == "kill" and source == "Walka":
                challenge["progress"] = min(challenge["target"], challenge["progress"] + 1)
            elif challenge["kind"] == "gold":
                challenge["progress"] = min(challenge["target"], challenge["progress"] + max(0, int(gold)))
            elif challenge["kind"] == "dungeon" and source == "Loch":
                challenge["progress"] = min(challenge["target"], challenge["progress"] + 1)

    def tick_active_buffs(self):
        """Zmniejsza licznik walk dla aktywnych eliksirów po ukończonym starciu."""
        if not hasattr(self, 'active_buffs') or not self.active_buffs:
            return
        expired = []
        for buff_id in list(self.active_buffs.keys()):
            self.active_buffs[buff_id] -= 1
            if self.active_buffs[buff_id] <= 0:
                expired.append(buff_id)
        for e in expired:
            del self.active_buffs[e]
        return expired
        
    def get_max_inventory_slots(self):
        # 4 strony x 20 slotów = 80 miejsc
        return 80

    def is_inventory_full(self):
        return len(self.inventory) >= self.get_max_inventory_slots()
        
    def add_to_inventory(self, item_id, modifier=None, is_reward=False):
        if isinstance(item_id, dict):
            item_dict = item_id
        else:
            item_dict = {"id": item_id, "lvl": 0, "modifier": modifier}
            
        if not self.is_inventory_full():
            self.inventory.append(item_dict)
            return True, "added"
        else:
            if is_reward:
                if not hasattr(self, 'inventory_stash'):
                    self.inventory_stash = []
                self.inventory_stash.append(item_dict)
                return False, "stashed"
            else:
                return False, "full"
        
    def equip(self, item_dict):
        if item_dict in self.inventory:
            item = get_item(item_dict)
            if not item: return False
            slot = getattr(item, "slot", None)
            if slot and slot in self.equipment:
                # Zamiana / założenie:
                old_eq = self.equipment[slot]
                self.equipment[slot] = item_dict
                self.inventory.remove(item_dict)
                if old_eq is not None:
                    self.inventory.append(old_eq)
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
        if getattr(self, 'permanent_perks', None) and "perk_greed" in self.permanent_perks:
            earned = int(earned * 1.10)
        self.gold += earned
        self.stats["total_clicks"] += 1
        self.record_reward("Kliknięcie", gold=earned)
        return earned
        
    def update_offline_progress(self, is_offline=True):
        current_time = time.time()
        elapsed = current_time - self.last_update_time
        if elapsed > 0:
            earned_gold = int(elapsed * self.stats["gold_per_sec"])
            
            if not is_offline:
                if getattr(self, 'permanent_perks', None) and "perk_greed" in self.permanent_perks:
                    earned_gold = int(earned_gold * 1.10)
                self.gold += earned_gold
                if earned_gold > 0:
                    self.record_reward("Przychód pasywny", gold=earned_gold)
            
            # Odzyskiwanie many (działa w tle i w grze)
            self.mana = min(self.max_mana, self.mana + int(elapsed * self.stats["mana_regen"]))
            
            self.last_update_time = current_time
            if is_offline and elapsed >= 5:
                print("[Offline] Podczas twojej nieobecności zregenerowałeś manę. Budowle pasywne nie zarabiają, gdy gra jest wyłączona.")
