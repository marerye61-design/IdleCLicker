# Moduł obsługujący Magiczne Klejnoty i Gniazda (Gems & Sockets)
import random

class Gem:
    def __init__(self, gem_id, name, icon, color, description, base_stats, value=500):
        self.gem_id = gem_id
        self.name = name
        self.icon = icon
        self.color = color
        self.description = description
        self.stats = base_stats
        self.value = value

    def get_stats_for_level(self, item_level_req=1):
        """Zwraca statystyki klejnotu przeskalowane proporcjonalnie do poziomu przedmiotu."""
        L = float(max(1, item_level_req))
        calc_stats = {}
        
        if self.gem_id == "gem_ruby":
            calc_stats["atk"] = 4 + int(L * 0.45)
        elif self.gem_id == "gem_emerald":
            calc_stats["hp_max"] = 25 + int(L * 3.5)
            calc_stats["def"] = 3 + int(L * 0.35)
        elif self.gem_id == "gem_sapphire":
            calc_stats["double_strike_pct"] = min(15, 3 + int(L / 25.0))
        elif self.gem_id == "gem_amethyst":
            calc_stats["crit_chance"] = min(12, 2 + int(L / 30.0))
        elif self.gem_id == "gem_topaz":
            calc_stats["bonus_gold_pct"] = min(40, 10 + int(L / 10.0))
            calc_stats["bonus_loot_pct"] = min(20, 3 + int(L / 25.0))
        else:
            calc_stats = dict(self.stats)
            
        return calc_stats

    def get_stat_summary(self, item_level_req=1):
        """Generuje czytelny opis statystyk klejnotu dla danego poziomu przedmiotu."""
        calc_stats = self.get_stats_for_level(item_level_req)
        parts = []
        if "atk" in calc_stats: parts.append(f"+{calc_stats['atk']} ATK")
        if "def" in calc_stats: parts.append(f"+{calc_stats['def']} DEF")
        if "hp_max" in calc_stats: parts.append(f"+{calc_stats['hp_max']} HP")
        if "crit_chance" in calc_stats: parts.append(f"+{calc_stats['crit_chance']}% Kryt")
        if "double_strike_pct" in calc_stats: parts.append(f"+{calc_stats['double_strike_pct']}% Podwójny Cios")
        if "bonus_gold_pct" in calc_stats: parts.append(f"+{calc_stats['bonus_gold_pct']}% Złoto")
        if "bonus_loot_pct" in calc_stats: parts.append(f"+{calc_stats['bonus_loot_pct']}% Szansa na Łup")
        return ", ".join(parts)

GEMS_DB = {
    "gem_ruby": Gem(
        "gem_ruby", 
        "Rubin Siły", 
        "🔴", 
        "#e74c3c", 
        "Płonący klejnot pulsujący czystą siłą bojową. Zwiększa obrażenia zależnie od potęgi przedmiotu.",
        {"atk": 4},
        value=600
    ),
    "gem_emerald": Gem(
        "gem_emerald", 
        "Szmaragd Żywotności", 
        "🟢", 
        "#2ecc71", 
        "Głęboko zielony kamień natury, wzmacniający odporność i maksymalne punkty życia.",
        {"hp_max": 25, "def": 3},
        value=600
    ),
    "gem_sapphire": Gem(
        "gem_sapphire", 
        "Szafir Prędkości", 
        "🔵", 
        "#3498db", 
        "Lśniący błękitem kryształ niebios. Zapewnia szansę na błyskawiczne wyprowadzenie drugiego ciosu z rzędu.",
        {"double_strike_pct": 3},
        value=750
    ),
    "gem_topaz": Gem(
        "gem_topaz", 
        "Topaz Chciwości", 
        "🟡", 
        "#f1c40f", 
        "Złocisty kamień przyciągający bogactwa i cenniejsze łupy z pokonanych potworów.",
        {"bonus_gold_pct": 10, "bonus_loot_pct": 3},
        value=700
    ),
    "gem_amethyst": Gem(
        "gem_amethyst", 
        "Ametyst Zguby", 
        "🟣", 
        "#9b59b6", 
        "Mroczny fioletowy klejnot nasycony magią cienia. Znacząco podnosi szansę na trafienia krytyczne.",
        {"crit_chance": 2},
        value=800
    )
}

def get_gem(gem_id):
    return GEMS_DB.get(gem_id, None)

def get_random_gem_id():
    return random.choice(list(GEMS_DB.keys()))

def roll_gem_drop(is_boss=False, player_level=1):
    """
    Zasady dropu:
    - 10% szansy z bossa lochu (od 1 poziomu)
    - 3% szansy ze zwykłych potworów (TYLKO od 15 poziomu gracza)
    """
    if is_boss:
        if random.random() < 0.10:
            return get_random_gem_id()
    else:
        if player_level >= 15 and random.random() < 0.03:
            return get_random_gem_id()
    return None

def ensure_item_sockets(item_dict, default_socket_count=1):
    """Gwarantuje obecność listy sockets w słowniku przedmiotu."""
    if "sockets" not in item_dict:
        item_dict["sockets"] = [None] * default_socket_count
    return item_dict["sockets"]

def get_sockets_summary(item_dict, item_level_req=1):
    """Zwraca czytelny ciąg tekstowy gniazd np. [🔴 Rubin (+10 ATK)] [○ Puste]."""
    if "sockets" not in item_dict or not item_dict["sockets"]:
        return "Brak gniazd"
    
    parts = []
    for g_id in item_dict["sockets"]:
        if g_id and g_id in GEMS_DB:
            gem = GEMS_DB[g_id]
            stat_txt = gem.get_stat_summary(item_level_req)
            parts.append(f"[{gem.icon} {gem.name} ({stat_txt})]")
        else:
            parts.append("[○ Puste Gniazdo]")
    return " ".join(parts)
