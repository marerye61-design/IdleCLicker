# Moduł Księgi Osiągnięć i Trofeów (Achievements & Trophies)

ACHIEVEMENTS_DB = {
    # === WALKA (COMBAT) ===
    "kill_10": {
        "id": "kill_10",
        "category": "walka",
        "icon": "🗡️",
        "title": "Pierwsza Krew",
        "desc": "Pokonaj 10 dowolnych potworów w walce.",
        "stat_key": "total_kills",
        "target": 10,
        "rewards": {"gold": 200, "exp": 100}
    },
    "kill_50": {
        "id": "kill_50",
        "category": "walka",
        "icon": "⚔️",
        "title": "Pogromca Potworów",
        "desc": "Pokonaj 50 potworów w walce.",
        "stat_key": "total_kills",
        "target": 50,
        "rewards": {"gold": 1000, "exp": 500}
    },
    "kill_250": {
        "id": "kill_250",
        "category": "walka",
        "icon": "💀",
        "title": "Żniwiarz Cienia",
        "desc": "Pokonaj 250 potworów w walce.",
        "stat_key": "total_kills",
        "target": 250,
        "rewards": {
            "gold": 10000, 
            "exp": 5000,
            "perk_id": "perk_slayer",
            "perk_desc": "⚡ Stały Perk: +5% do wszystkich Obrażeń Bohatera"
        }
    },
    "crit_50": {
        "id": "crit_50",
        "category": "walka",
        "icon": "🎯",
        "title": "Precyzja Zabójcy",
        "desc": "Zadaj 50 trafień krytycznych wrogom.",
        "stat_key": "total_crits",
        "target": 50,
        "rewards": {
            "gold": 5000, 
            "exp": 2500,
            "perk_id": "perk_crit_master",
            "perk_desc": "⚡ Stały Perk: +3% Szansy na Trafienie Krytyczne"
        }
    },

    # === LOCHY & BOSSOWIE (DUNGEONS) ===
    "boss_ptys": {
        "id": "boss_ptys",
        "category": "lochy",
        "icon": "👹",
        "title": "Zguba Orków",
        "desc": "Pokonaj potężnego bossa Giga Orka Ptysia w 1. lochu.",
        "stat_key": "boss_ptys_kills",
        "target": 1,
        "rewards": {"gold": 1500, "exp": 1000}
    },
    "boss_kollman": {
        "id": "boss_kollman",
        "category": "lochy",
        "icon": "🔥",
        "title": "Ugaszony Płomień",
        "desc": "Pokonaj Wojowniczego Maga Kollmana w 2. lochu.",
        "stat_key": "boss_kollman_kills",
        "target": 1,
        "rewards": {
            "gold": 8000, 
            "exp": 6000,
            "perk_id": "perk_boss_hunter",
            "perk_desc": "⚡ Stały Perk: +5% Złota i EXP ze wszystkich lochów"
        }
    },
    "dungeon_15": {
        "id": "dungeon_15",
        "category": "lochy",
        "icon": "🏰",
        "title": "Weteran Podziemi",
        "desc": "Ukończ 15 wypraw do lochów.",
        "stat_key": "dungeons_cleared",
        "target": 15,
        "rewards": {
            "gold": 15000, 
            "exp": 10000,
            "perk_id": "perk_exp_master",
            "perk_desc": "⚡ Stały Perk: +5% do całego zdobywanego Doświadczenia (EXP)"
        }
    },

    # === RZEMIOSŁO & KOWAL (BLACKSMITH & GEMS) ===
    "upgrade_1": {
        "id": "upgrade_1",
        "category": "rzemioslo",
        "icon": "🔨",
        "title": "Młot i Kowadło",
        "desc": "Dokonaj pierwszego ulepszenia ekwipunku u Kowala.",
        "stat_key": "upgrades_done",
        "target": 1,
        "rewards": {"gold": 300, "exp": 150}
    },
    "upgrade_plus9": {
        "id": "upgrade_plus9",
        "category": "rzemioslo",
        "icon": "🌟",
        "title": "Mistrzowskie Dzieło",
        "desc": "Ulepsz dowolny przedmiot do maksymalnego poziomu +9.",
        "stat_key": "max_upgrade_level",
        "target": 9,
        "rewards": {
            "gold": 25000, 
            "exp": 15000,
            "perk_id": "perk_master_smith",
            "perk_desc": "⚡ Stały Perk: -10% Kosztu Kucia u miejskiego Kowala"
        }
    },
    "socket_5": {
        "id": "socket_5",
        "category": "rzemioslo",
        "icon": "🔮",
        "title": "Jubiler Magii",
        "desc": "Wpraw łącznie 5 magicznych klejnotów w gniazda ekwipunku.",
        "stat_key": "gems_socketed",
        "target": 5,
        "rewards": {
            "gold": 12000, 
            "exp": 8000,
            "perk_id": "perk_gem_resonance",
            "perk_desc": "⚡ Stały Perk: +10% do statystyk wszystkich wprawionych klejnotów"
        }
    },

    # === ALCHEMIA & OGRÓD (ALCHEMY & GARDEN) ===
    "harvest_10": {
        "id": "harvest_10",
        "category": "alchemia",
        "icon": "🌿",
        "title": "Młody Zielarz",
        "desc": "Zbierz 10 ziół z Ogrodu Domci.",
        "stat_key": "herbs_harvested",
        "target": 10,
        "rewards": {"gold": 500, "exp": 300}
    },
    "brew_10": {
        "id": "brew_10",
        "category": "alchemia",
        "icon": "🧪",
        "title": "Kociołek Magii",
        "desc": "Uwarz 10 eliksirów w Kociołku Alchemicznym.",
        "stat_key": "potions_brewed",
        "target": 10,
        "rewards": {"gold": 2500, "exp": 1500}
    },
    "brew_psychedelic": {
        "id": "brew_psychedelic",
        "category": "alchemia",
        "icon": "🌀",
        "title": "Podróżnik Świadomości",
        "desc": "Uwarz i wypij Ekstrakt Nieznanej Głębi u Domci.",
        "stat_key": "psychedelic_brewed",
        "target": 1,
        "rewards": {
            "gold": 8000, 
            "exp": 5000,
            "perk_id": "perk_alchemist_touch",
            "perk_desc": "⚡ Stały Perk: +15% Szansy na podwójny plon ziół z ogrodu"
        }
    },

    # === DRUŻYNA (PARTY) ===
    "recruit_1": {
        "id": "recruit_1",
        "category": "druzyna",
        "icon": "🤝",
        "title": "Wierny Kompan",
        "desc": "Zwerbuj pierwszego towarzysza do swojej drużyny.",
        "stat_key": "party_count",
        "target": 1,
        "rewards": {"gold": 1000, "exp": 500}
    },
    "recruit_6": {
        "id": "recruit_6",
        "category": "druzyna",
        "icon": "👑",
        "title": "Kompletna Kompania",
        "desc": "Zwerbuj wszystkich 6 towarzyszy w gospodzie Barnaby.",
        "stat_key": "party_count",
        "target": 6,
        "rewards": {
            "gold": 30000, 
            "exp": 20000,
            "perk_id": "perk_party_synergy",
            "perk_desc": "⚡ Stały Perk: +10% do siły wszystkich pasywek towarzyszy"
        }
    },

    # === BOGACTWO (WEALTH) ===
    "gold_1000": {
        "id": "gold_1000",
        "category": "bogactwo",
        "icon": "🪙",
        "title": "Pełna Sakiewka",
        "desc": "Zgromadź łącznie 1 000 sztuk złota.",
        "stat_key": "total_gold_earned",
        "target": 1000,
        "rewards": {"gold": 500, "exp": 200}
    },
    "gold_100000": {
        "id": "gold_100000",
        "category": "bogactwo",
        "icon": "💰",
        "title": "Magnez Złota",
        "desc": "Zgromadź łącznie 100 000 sztuk złota.",
        "stat_key": "total_gold_earned",
        "target": 100000,
        "rewards": {
            "gold": 25000, 
            "exp": 15000,
            "perk_id": "perk_greed",
            "perk_desc": "⚡ Stały Perk: +10% więcej Złota ze wszystkich źródeł"
        }
    }
}
