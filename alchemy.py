# Moduł obsługujący Ogród Ziół u Domci i Warzenie Mikstur w Kociołku (Alchemy & Herbarium)
import time
import random

HERBS_DB = {
    "herb_amanita": {
        "id": "herb_amanita",
        "name": "Amanita Lasu",
        "icon": "🍄",
        "color": "#e67e22",
        "description": "Czerwony grzyb leśny o właściwościach stymulujących siłę i agresję.",
        "growth_time": 30, # sekundy
        "value": 40
    },
    "herb_moss": {
        "id": "herb_moss",
        "name": "Srebrzysty Mech",
        "icon": "🌿",
        "color": "#2ecc71",
        "description": "Lśniący chłodny mech skalny, kluczowy do wywarów leczniczych i ochronnych.",
        "growth_time": 45,
        "value": 50
    },
    "herb_flower": {
        "id": "herb_flower",
        "name": "Krwawy Kwiat",
        "icon": "🌸",
        "color": "#e74c3c",
        "description": "Szkarłatny kwiat z zarośli o zapachu siarki i witalności.",
        "growth_time": 60,
        "value": 60
    },
    "herb_root": {
        "id": "herb_root",
        "name": "Smoczy Korzeń",
        "icon": "🌾",
        "color": "#f1c40f",
        "description": "Rzadki, twardy korzeń gromadzący energię ziemi i bogactwa.",
        "growth_time": 90,
        "value": 80
    },
    "herb_mystery": {
        "id": "herb_mystery",
        "name": "Ziółko",
        "icon": "🌀",
        "color": "#9b59b6",
        "description": "Mistyczna roślina o niezwykłym aromacie. (Można zażyć z ekwipunku lub uwarzyć w kociołku)",
        "growth_time": 120,
        "value": 150
    }
}

MONSTER_INGREDIENTS_DB = {
    "ing_fang": {
        "id": "ing_fang",
        "name": "Kieł Bestii",
        "icon": "🦷",
        "color": "#dcdde1",
        "description": "Ostry kieł drapieżnika. Upuszczany przez wilki i dzikie bestie.",
        "value": 30
    },
    "ing_venom": {
        "id": "ing_venom",
        "name": "Gruczoł Jadowy",
        "icon": "🧪",
        "color": "#8c7ae6",
        "description": "Lepki jad pająków i pełzających potworów.",
        "value": 45
    },
    "ing_ectoplasm": {
        "id": "ing_ectoplasm",
        "name": "Ektoplazma Upiora",
        "icon": "👻",
        "color": "#00d2d3",
        "description": "Świetlista maź pozostająca po nieumarłych i zjawach.",
        "value": 60
    },
    "ing_core": {
        "id": "ing_core",
        "name": "Rdzeń Skalny",
        "icon": "💎",
        "color": "#e15f41",
        "description": "Ciężki, twardy fragment ożywionego golema lub gargulca.",
        "value": 75
    }
}

# Receptury eliksirów w Kociołku Alchemicznym
RECIPES_DB = {
    "elixir_berserk": {
        "id": "elixir_berserk",
        "name": "Eliksir Berserkera",
        "icon": "💥",
        "color": "#e74c3c",
        "description": "+25% do całkowitych Obrażeń Bohatera na 10 kolejnych walk.",
        "ingredients": {"herb_amanita": 2, "ing_fang": 1},
        "duration_fights": 10,
        "buff_type": "atk_pct",
        "buff_val": 25
    },
    "elixir_stone_skin": {
        "id": "elixir_stone_skin",
        "name": "Mikstura Kamiennej Skóry",
        "icon": "🛡️",
        "color": "#7f8c8d",
        "description": "+30% do Pancerza (DEF) na 10 kolejnych walk.",
        "ingredients": {"herb_moss": 2, "ing_core": 1},
        "duration_fights": 10,
        "buff_type": "def_pct",
        "buff_val": 30
    },
    "elixir_swiftness": {
        "id": "elixir_swiftness",
        "name": "Wywar Szybkich Stóp",
        "icon": "⚡",
        "color": "#3498db",
        "description": "+12% Szansy na Podwójny Cios na 10 kolejnych walk.",
        "ingredients": {"herb_flower": 2, "ing_venom": 1},
        "duration_fights": 10,
        "buff_type": "double_strike_pct",
        "buff_val": 12
    },
    "elixir_fortune": {
        "id": "elixir_fortune",
        "name": "Napar Złotego Rogu",
        "icon": "💰",
        "color": "#f1c40f",
        "description": "+40% Złota z pokonanych potworów na 10 kolejnych walk.",
        "ingredients": {"herb_root": 1, "herb_moss": 2},
        "duration_fights": 10,
        "buff_type": "bonus_gold_pct",
        "buff_val": 40
    },
    "elixir_full_heal": {
        "id": "elixir_full_heal",
        "name": "Mikstura Pełnego Zdrowia",
        "icon": "🧪",
        "color": "#2ecc71",
        "description": "Darmowa mikstura lecznicza (dodaje 1 szt. do ekwipunku).",
        "ingredients": {"herb_amanita": 1, "herb_moss": 1},
        "is_item_reward": "pot_hp"
    },
    "elixir_psychedelic": {
        "id": "elixir_psychedelic",
        "name": "Ziółko (Mocny Wywar)",
        "icon": "🌀",
        "color": "#9b59b6",
        "description": "Zażycie wywołuje 60-sekundową psychodeliczną falę deformacji świata i feerii barw, spowalniając czas i dając +35% Szansy na Trafienie Krytyczne!",
        "ingredients": {"herb_mystery": 1, "ing_ectoplasm": 1},
        "duration_fights": 10,
        "buff_type": "psychedelic_slowmo",
        "buff_val": 35
    }
}

def roll_monster_ingredient_drop(enemy_name):
    """Losuje składnik alchemiczny w zależności od pokonanego potwora (szansa ~20-35%)."""
    e_low = enemy_name.lower()
    r = random.random()
    if "wilk" in e_low or "ogar" in e_low or "besti" in e_low:
        if r < 0.35: return "ing_fang"
    elif "pająk" in e_low or "pajak" in e_low:
        if r < 0.35: return "ing_venom"
    elif "upiór" in e_low or "upior" in e_low or "szkielet" in e_low or "zjaw" in e_low or "demon" in e_low or "czarnoksiężnik" in e_low:
        if r < 0.30: return "ing_ectoplasm"
    elif "golem" in e_low or "gargulec" in e_low or "troll" in e_low:
        if r < 0.30: return "ing_core"
    elif r < 0.15:
        return random.choice(list(MONSTER_INGREDIENTS_DB.keys()))
    return None
