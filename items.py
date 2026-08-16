class Item:
    def __init__(self, item_id, name, description, value):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.value = value
        
    def __str__(self):
        return f"{self.name} - {self.description} (Wartość: {self.value} sztota)"

class Equipment(Item):
    def __init__(self, item_id, name, description, value, slot, stats, level_req=1, rarity="Zwykły"):
        super().__init__(item_id, name, description, value)
        self.slot = slot  # 'weapon', 'armor', 'helmet', 'accessory'
        self.level_req = level_req
        self.rarity = rarity # 'Zwykły', 'Legendarny'
        
        # === KOMPLETNY REBALANS (Skalowanie do 500 poziomu) ===
        mult = 1.0
        if rarity == "Zwykły": mult = 1.0
        elif rarity == "Rzadki": mult = 1.5
        elif rarity == "Legendarny": mult = 2.5
        elif rarity == "Mityczny": mult = 4.0
        
        # Balans dla wczesnego artefaktu Eczmego (dokładnie ~3.5x mocniejszy od startowego sygnetu)
        if item_id == "acc_eczme":
            mult = 1.45
        
        L = float(max(1, self.level_req))
        new_stats = {}
        if slot == "weapon":
            new_stats["atk"] = int((5 + L ** 1.5) * mult)
        elif slot == "armor":
            new_stats["def"] = int((5 + L ** 1.45) * mult)
            new_stats["hp_max"] = int((20 + L ** 1.65) * mult)
        elif slot == "helmet":
            new_stats["def"] = int((3 + L ** 1.35) * mult)
            new_stats["hp_max"] = int((10 + L ** 1.55) * mult)
        elif slot == "accessory":
            new_stats["atk"] = int((2 + L ** 1.4) * mult)
            new_stats["def"] = int((3 + L ** 1.35) * mult)
            new_stats["hp_max"] = int((10 + L ** 1.55) * mult)
            
        self.stats = new_stats  # Nadpisujemy ręczne statystyki tymi ze wzorów

    def __str__(self):
        stat_str = ", ".join([f"{k.upper()}: +{v}" for k, v in self.stats.items()])
        rarity_str = f"[{self.rarity.upper()}] " if self.rarity != "Zwykły" else ""
        return f"{rarity_str}{self.name} [{self.slot.upper()}] (Wymaga poz. {self.level_req}) - {self.description} | Statystyki: {stat_str} (Wartość: {self.value})"

class Consumable(Item):
    def __init__(self, item_id, name, description, value, effect):
        super().__init__(item_id, name, description, value)
        self.effect = effect  # np. {'hp_pct': 100}

# Słownik wszystkich dostępnych przedmiotów w grze
ITEMS_DB = {
    "pot_hp": Consumable("pot_hp", "Mikstura Pełnego Zdrowia", "Natychmiastowo leczy 100% maksymalnego HP bohatera (w trakcie walki lub z poziomu ekwipunku).", 50, {"hp_pct": 100}),
    
    # === PODSTAWOWY EKWIPUNEK SKLEPOWY (ZWYKŁY) ===
    # Tier 1 (Poziom 1)
    "wep_wooden_club": Equipment("wep_wooden_club", "Drewniana Pałka", "Prosta broń dla nowicjuszy.", 50, "weapon", {"atk": 3}, level_req=1, rarity="Zwykły"),
    "arm_leather": Equipment("arm_leather", "Skórzana Przeszywanica", "Lekki pancerz ochronny.", 200, "armor", {"def": 4, "hp_max": 10}, level_req=1, rarity="Zwykły"),
    "helm_leather": Equipment("helm_leather", "Skórzany Hełm", "Lekka ochrona głowy.", 150, "helmet", {"def": 3}, level_req=1, rarity="Zwykły"),
    "acc_ring_small": Equipment("acc_ring_small", "Miedziany Pierścień", "Zapewnia ochronny urok.", 250, "accessory", {"atk": 2, "def": 2}, level_req=1, rarity="Zwykły"),

    # Tier 1.5 (Poziom 5)
    "wep_iron_sword": Equipment("wep_iron_sword", "Żelazny Miecz", "Wytrzymały miecz ze stali.", 400, "weapon", {"atk": 8}, level_req=5, rarity="Zwykły"),
    "arm_iron_plate": Equipment("arm_iron_plate", "Żelazna Płytówka", "Solidna zbroja rycerska.", 600, "armor", {"def": 10, "hp_max": 20}, level_req=5, rarity="Zwykły"),
    "helm_iron": Equipment("helm_iron", "Żelazny Szyszak", "Gruby hełm chroniący przed ciosami w głowę.", 350, "helmet", {"def": 6, "hp_max": 10}, level_req=5, rarity="Zwykły"),
    "acc_iron_ring": Equipment("acc_iron_ring", "Żelazny Sygnet", "Ciężki i solidny pierścień.", 500, "accessory", {"atk": 4, "def": 4, "hp_max": 15}, level_req=5, rarity="Zwykły"),

    # Tier 2 (Poziom 15)
    "wep_steel_sword": Equipment("wep_steel_sword", "Stalowy Miecz Długi", "Ostra, wyważona broń.", 2500, "weapon", {"atk": 25}, level_req=15, rarity="Zwykły"),
    "arm_steel_plate": Equipment("arm_steel_plate", "Stalowy Kirys", "Ciężki pancerz chroniący klatkę.", 4000, "armor", {"def": 22, "hp_max": 50}, level_req=15, rarity="Zwykły"),
    "helm_steel": Equipment("helm_steel", "Stalowa Przyłbica", "Pełna ochrona twarzy i głowy.", 1800, "helmet", {"def": 10, "hp_max": 20}, level_req=15, rarity="Zwykły"),
    "acc_silver_amulet": Equipment("acc_silver_amulet", "Srebrny Amulet", "Błyszczący amulet ochronny.", 3500, "accessory", {"atk": 8, "def": 8, "hp_max": 40}, level_req=15, rarity="Zwykły"),

    # Tier 3 (Poziom 30)
    "wep_mithril_blade": Equipment("wep_mithril_blade", "Mithrilowe Ostrze", "Niezwykle lekkie i ostre jak brzytwa.", 20000, "weapon", {"atk": 70}, level_req=30, rarity="Zwykły"),
    "arm_mithril_mail": Equipment("arm_mithril_mail", "Mithrilowa Kolczuga", "Niezwykle lekka, a niemal niezniszczalna.", 30000, "armor", {"def": 55, "hp_max": 120}, level_req=30, rarity="Zwykły"),
    "helm_mithril": Equipment("helm_mithril", "Mithrilowy Hełm", "Błyszcząca korona bojowa.", 15000, "helmet", {"def": 25, "hp_max": 50}, level_req=30, rarity="Zwykły"),
    "acc_ruby_pendant": Equipment("acc_ruby_pendant", "Rubinowy Wisiorek", "Pulsuje gorącą magią bojową.", 25000, "accessory", {"atk": 20, "def": 20, "hp_max": 100}, level_req=30, rarity="Zwykły"),

    # Tier 4 (Poziom 50)
    "wep_adamant_greatsword": Equipment("wep_adamant_greatsword", "Adamantowy Wielki Miecz", "Przecina najtwardsze skały i pancerze.", 150000, "weapon", {"atk": 180}, level_req=50, rarity="Zwykły"),
    "arm_adamant_cuirass": Equipment("arm_adamant_cuirass", "Adamantowa Zbroja", "Legendarna płyta wykuta w głębinach ziemi.", 200000, "armor", {"def": 140, "hp_max": 300}, level_req=50, rarity="Zwykły"),
    "helm_adamant": Equipment("helm_adamant", "Adamantowa Korona Wojny", "Napełnia nosiciela straszliwą potęgą.", 100000, "helmet", {"def": 60, "hp_max": 150}, level_req=50, rarity="Zwykły"),
    "acc_dragon_eye": Equipment("acc_dragon_eye", "Oko Smoka", "Starożytny artefakt emanujący mroczną energią.", 180000, "accessory", {"atk": 50, "def": 50, "hp_max": 250}, level_req=50, rarity="Zwykły"),

    # Tier 5 (Poziom 75)
    "wep_shadow_slayer": Equipment("wep_shadow_slayer", "Pogromca Cieni", "Boski miecz wykuty ze skrystalizowanej gwiazdy.", 1000000, "weapon", {"atk": 400}, level_req=75, rarity="Zwykły"),
    "arm_dragon_scale": Equipment("arm_dragon_scale", "Pancerz ze Smoczej Łuski", "Absorbuje potężne uderzenia boskich bestii.", 1500000, "armor", {"def": 320, "hp_max": 800}, level_req=75, rarity="Zwykły"),
    "helm_demon_crown": Equipment("helm_demon_crown", "Korona Demonów", "Płonąca aureola władcy otchłani.", 800000, "helmet", {"def": 140, "hp_max": 400}, level_req=75, rarity="Zwykły"),
    "acc_god_talisman": Equipment("acc_god_talisman", "Talisman Boskiej Mocy", "Absolutna potęga niebios i piekła.", 1200000, "accessory", {"atk": 120, "def": 120, "hp_max": 600}, level_req=75, rarity="Zwykły"),

    # === UNIKALNY EKWIPUNEK LEGENDARNY (NAGRODY Z ZADAŃ TOWARZYSZY) ===
    # Lvl 1: Ponad 5x silniejszy od Pałki (ATK 3 -> ATK 16, HP 40)
    "wep_maslak": Equipment(
        "wep_maslak", 
        "Święty Kij Maślaka", 
        "HISTORIA: Młody Maślak zgubił ten sękaty kij w Złowrogim Lesie uciekając przed pszczołami. Obrobiony słodkim lukrem z jego cukierni i żywicą, zyskał niezwykłą twardość.", 
        1500, "weapon", {"atk": 16, "hp_max": 40}, level_req=1, rarity="Legendarny"
    ),
    # Lvl 10: Ponad 3x silniejszy od Sygnetu (ATK 4/DEF 4 -> ATK 25/DEF 15/HP 80)
    "acc_eczme": Equipment(
        "acc_eczme",
        "Owijki 'PowerKeeper'",
        "HISTORIA: Kłębek magicznej taśmy izolacyjnej, używanej przez Eczmego na każdym treningu. Skumulowana w niej potęga wzmacnia każde uderzenie.",
        5000, "accessory", {"atk": 25, "def": 15, "hp_max": 80}, level_req=10, rarity="Legendarny"
    ),
    # Lvl 20: Ponad 3x silniejszy od Przyłbicy (DEF 10 -> DEF 35, HP 150, ATK 20)
    "helm_pianek": Equipment(
        "helm_pianek", 
        "Potowa Opaska Pianka", 
        "HISTORIA: Kultowa opaska z czoła Pianka, przesiąknięta potem z tysięcy serii martwego ciągu. Wibracje czystego pakowania budzą lęk w sercach wrogów.", 
        10000, "helmet", {"def": 35, "hp_max": 150, "atk": 20}, level_req=20, rarity="Legendarny"
    ),
    # Lvl 30: Ponad 2x silniejszy od Mithrilowej Kolczugi (DEF 55/HP 120 -> DEF 120/HP 350)
    "arm_damian": Equipment(
        "arm_damian", 
        "Zbroja Mytnika Damiana", 
        "HISTORIA: Zbroja, w której Damian pobierał 'dobrowolne' opłaty od strażników. Wyklepana przez kowala za dławienie dłużników, nosi ślady strzał nieprzekonanych wędrowców.", 
        25000, "armor", {"def": 120, "hp_max": 350, "atk": 20}, level_req=30, rarity="Legendarny"
    ),
    # Lvl 40: Ponad 3x silniejszy od Rubinowego Wisiorka (ATK 20/DEF 20 -> ATK 65/DEF 65/HP 450)
    "acc_domcia": Equipment(
        "acc_domcia", 
        "Mistyczny Naszyjnik Domci", 
        "HISTORIA: Naszyjnik wypleciony z najrzadszych ziół. Podobno w środku ukryty jest skruszony magiczny kamień.", 
        50000, "accessory", {"atk": 65, "def": 65, "hp_max": 450}, level_req=40, rarity="Legendarny"
    ),
    # Lvl 50: Ponad 2.1x silniejszy od Adamantowego Miecza (ATK 180 -> ATK 380, HP 350, Kryt 8%)
    "wep_yomen": Equipment(
        "wep_yomen", 
        "Klucz Czternastka Yomena", 
        "HISTORIA: Ulubione narzędzie Yomena ze ścieków. Legenda głosi, że tym kluczem dokręcił uszczelki w maszynie BeeMWe i rozłupał czaszki dziesięciu goblinów.", 
        120000, "weapon", {"atk": 380, "hp_max": 350, "crit_chance": 8}, level_req=50, rarity="Legendarny"
    ),
    "arm_eczme": Equipment(
        "arm_eczme", 
        "Nakolanniki Przeznaczenia Eczme", 
        "HISTORIA: Legendarne ochraniacze Eczme z meczy siatkówki w podziemiach. Pozwalały mu robić rzuty na kamienne podłoże i odbijać 5-kilowe kule bez zadrapania.", 
        45000, "armor", {"def": 68, "hp_max": 140, "atk": 8}, level_req=30, rarity="Legendarny"
    ),

    # NOWE LOCHY (45 - 100)
    "wep_fire_axe": Equipment(
        "wep_fire_axe", "Ognisty Topór Czeluści", "Ocieka magmą. Z każdym uderzeniem spopiela pancerz wroga.", 
        100000, "weapon", {"atk": 165, "hp_max": 100, "crit_chance": 5}, level_req=45, rarity="Legendarny"
    ),
    "acc_fire_ruby": Equipment(
        "acc_fire_ruby", "Oko Wulkanu", "Pulsujący klejnot wyrwany z serca wulkanu.", 
        120000, "accessory", {"atk": 60, "def": 40, "hp_max": 200}, level_req=45, rarity="Legendarny"
    ),
    
    "arm_crystal": Equipment(
        "arm_crystal", "Kryształowy Pancerz", "Odbija ataki magiczne z niezwykłą precyzją.", 
        250000, "armor", {"def": 180, "hp_max": 350}, level_req=60, rarity="Legendarny"
    ),
    "helm_crystal": Equipment(
        "helm_crystal", "Diadem Jaskini", "Zwiększa jasność umysłu w mroku kryształowych jaskiń.", 
        200000, "helmet", {"def": 85, "hp_max": 200, "atk": 25}, level_req=60, rarity="Legendarny"
    ),

    "wep_frost_mourne": Equipment(
        "wep_frost_mourne", "Mroźne Ostrze", "Zamraża krew w żyłach każdego, kogo dotknie.", 
        750000, "weapon", {"atk": 380, "hp_max": 400, "crit_chance": 10}, level_req=75, rarity="Legendarny"
    ),
    "acc_frost_amulet": Equipment(
        "acc_frost_amulet", "Amulet Wiecznej Zimy", "Gwarantuje odporność na wszelkie skrajne temperatury.", 
        800000, "accessory", {"atk": 100, "def": 100, "hp_max": 600}, level_req=75, rarity="Legendarny"
    ),

    "arm_fallen_god": Equipment(
        "arm_fallen_god", "Pancerz Upadłego Boga", "Pozostałość po dawnych stwórcach tego świata.", 
        2500000, "armor", {"def": 450, "hp_max": 1200, "atk": 50}, level_req=90, rarity="Mityczny"
    ),
    "helm_fallen_god": Equipment(
        "helm_fallen_god", "Aureola Zniszczenia", "Kto ją nosi, postrzega śmiertelników jako pył.", 
        1800000, "helmet", {"def": 250, "hp_max": 800, "atk": 80}, level_req=90, rarity="Mityczny"
    ),

    "wep_void_blade": Equipment(
        "wep_void_blade", "Ostrze Nieskończoności", "Nie ma fizycznej formy. Rozcina samo kontinuum czasoprzestrzeni.", 
        10000000, "weapon", {"atk": 1200, "hp_max": 1000, "crit_chance": 20}, level_req=100, rarity="Mityczny"
    ),
    "acc_void_core": Equipment(
        "acc_void_core", "Rdzeń Czasoprzestrzeni", "Zatrzymuje czas wokół posiadacza.", 
        12000000, "accessory", {"atk": 400, "def": 400, "hp_max": 3000}, level_req=100, rarity="Mityczny"
    ),
    
    # === MAGICZNE KLEJNOTY (GEMS) ===
    "gem_ruby": Item("gem_ruby", "Rubin Siły", "🔴 Płonący klejnot bojowy (+15 ATK w gnieździe ekwipunku).", 600),
    "gem_emerald": Item("gem_emerald", "Szmaragd Żywotności", "🟢 Kamień natury (+80 Max HP, +8 DEF w gnieździe ekwipunku).", 600),
    "gem_sapphire": Item("gem_sapphire", "Szafir Prędkości", "🔵 Kryształ niebios (+5% Szansy na Podwójny Atak w gnieździe).", 750),
    "gem_topaz": Item("gem_topaz", "Topaz Chciwości", "🟡 Złocisty klejnot fortuny (+15% Złota, +5% Szansy na Łup).", 700),
    "gem_amethyst": Item("gem_amethyst", "Ametyst Zguby", "🟣 Klejnot magii cienia (+3% Szansy na Cios Krytyczny).", 800),

    # === ZIOŁA I SKŁADNIKI ALCHEMICZNE (HERBS & INGREDIENTS) ===
    "herb_amanita": Item("herb_amanita", "Amanita Lasu", "🍄 Czerwony grzyb leśny o właściwościach stymulujących siłę.", 40),
    "herb_moss": Item("herb_moss", "Srebrzysty Mech", "🌿 Lśniący chłodny mech skalny, kluczowy do wywarów leczniczych.", 50),
    "herb_flower": Item("herb_flower", "Krwawy Kwiat", "🌸 Szkarłatny kwiat z zarośli o zapachu siarki i witalności.", 60),
    "herb_root": Item("herb_root", "Smoczy Korzeń", "🌾 Rzadki, twardy korzeń gromadzący energię ziemi i bogactwa.", 80),
    "herb_mystery": Item("herb_mystery", "Ziółko", "🌀 Efekt nieznany. (Kliknij 'Zażyj Ziółko' w plecaku, aby doświadczyć 60s mistycznej fali deformacji świata i spowolnienia czasu)", 150),
    
    "ing_fang": Item("ing_fang", "Kieł Bestii", "🦷 Ostry kieł drapieżnika. Upuszczany przez wilki i bestie.", 30),
    "ing_venom": Item("ing_venom", "Gruczoł Jadowy", "🧪 Lepki jad pająków i pełzających potworów.", 45),
    "ing_ectoplasm": Item("ing_ectoplasm", "Ektoplazma Upiora", "👻 Świetlista maź pozostająca po nieumarłych i zjawach.", 60),
    "ing_core": Item("ing_core", "Rdzeń Skalny", "💎 Ciężki, twardy fragment ożywionego golema lub gargulca.", 75)
}

from modifiers import MODIFIERS_DB
import copy

def get_item(item_data):
    if not item_data:
        return None
        
    if isinstance(item_data, str):
        item_id = item_data
        modifier_id = None
    elif isinstance(item_data, dict):
        item_id = item_data.get("id")
        modifier_id = item_data.get("modifier")
    else:
        return None
        
    base_item = ITEMS_DB.get(item_id)
    if not base_item or not isinstance(base_item, Equipment) or not modifier_id:
        return base_item
        
    mod = MODIFIERS_DB.get(modifier_id)
    if not mod or base_item.slot not in mod.allowed_slots:
        return base_item
        
    modified_item = copy.deepcopy(base_item)
    
    # Zmiana statystyk
    for stat, mult in mod.stat_mults.items():
        if stat in modified_item.stats:
            modified_item.stats[stat] = int(modified_item.stats[stat] * mult)
            
    for stat, flat in mod.stat_flats.items():
        modified_item.stats[stat] = modified_item.stats.get(stat, 0) + flat
        
    # Zmiana nazwy, wartości i opisu
    modified_item.name = f"{mod.prefix} {base_item.name}"
    modified_item.description = f"{base_item.description} {mod.generate_description()}"
    modified_item.value = int(modified_item.value * 1.5)
    
    return modified_item
