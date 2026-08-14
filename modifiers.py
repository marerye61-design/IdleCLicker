class Modifier:
    def __init__(self, mod_id, prefix, allowed_slots, stat_mults=None, stat_flats=None):
        self.mod_id = mod_id
        self.prefix = prefix
        self.allowed_slots = allowed_slots # e.g. ["weapon"], ["armor", "helmet"]
        self.stat_mults = stat_mults if stat_mults else {}
        self.stat_flats = stat_flats if stat_flats else {}
        
    def generate_description(self):
        desc_parts = []
        for stat, mult in self.stat_mults.items():
            val = int(mult * 100) - 100
            if val > 0:
                desc_parts.append(f"+{val}% {stat.upper()}")
            elif val < 0:
                desc_parts.append(f"{val}% {stat.upper()}")
                
        for stat, flat in self.stat_flats.items():
            if flat > 0:
                desc_parts.append(f"+{flat} {stat.upper()}")
            elif flat < 0:
                desc_parts.append(f"{flat} {stat.upper()}")
                
        return f"({self.prefix}: {', '.join(desc_parts)})"

MODIFIERS_DB = {}

def add_mod(mod_id, prefix, slots, mults, flats):
    MODIFIERS_DB[mod_id] = Modifier(mod_id, prefix, slots, mults, flats)

# === BROŃ (20 Modyfikatorów) ===
add_mod("w_ostry", "Ostry", ["weapon"], {"atk": 1.1}, {})
add_mod("w_ciezki", "Ciężki", ["weapon"], {"atk": 1.25}, {"atk": 5})
add_mod("w_zabojczy", "Zabójczy", ["weapon"], {"atk": 1.4}, {"crit_chance": 15})
add_mod("w_krwawy", "Krwawy", ["weapon"], {"atk": 1.15}, {"hp_max": 20})
add_mod("w_ognisty", "Ognisty", ["weapon"], {"atk": 1.2}, {"atk": 10})
add_mod("w_lodowy", "Lodowy", ["weapon"], {"atk": 1.1}, {"def": 10})
add_mod("w_trujacy", "Trujący", ["weapon"], {"atk": 1.3}, {"hp_max": -10})
add_mod("w_potezny", "Potężny", ["weapon"], {"atk": 1.5}, {})
add_mod("w_leki", "Lekki", ["weapon"], {"atk": 0.9}, {"def": 5})
add_mod("w_szybki", "Szybki", ["weapon"], {"atk": 1.05}, {"atk": 5, "crit_chance": 5})
add_mod("w_wampiryczny", "Wampiryczny", ["weapon"], {"atk": 1.1}, {"hp_max": 50})
add_mod("w_przeklety", "Przeklęty", ["weapon"], {"atk": 2.0}, {"hp_max": -50})
add_mod("w_swiety", "Święty", ["weapon"], {"atk": 1.2}, {"hp_max": 30, "def": 10})
add_mod("w_mroczny", "Mroczny", ["weapon"], {"atk": 1.3}, {"def": -10, "crit_chance": 10})
add_mod("w_starozytny", "Starożytny", ["weapon"], {"atk": 1.4}, {"atk": 20})
add_mod("w_mistyczny", "Mistyczny", ["weapon"], {"atk": 1.35}, {"hp_max": 40})
add_mod("w_magiczny", "Magiczny", ["weapon"], {"atk": 1.15}, {"atk": 15})
add_mod("w_krolewski", "Królewski", ["weapon"], {"atk": 1.25}, {"def": 15})
add_mod("w_demoniczny", "Demoniczny", ["weapon"], {"atk": 1.6}, {"def": -20})
add_mod("w_boski", "Boski", ["weapon"], {"atk": 1.8}, {"hp_max": 100, "def": 20})

# === PANCERZ / HEŁM (20 Modyfikatorów) ===
add_mod("a_solidny", "Solidny", ["armor", "helmet"], {"def": 1.1}, {})
add_mod("a_gruby", "Gruby", ["armor", "helmet"], {"def": 1.2}, {"hp_max": 20})
add_mod("a_wzmocniony", "Wzmocniony", ["armor", "helmet"], {"def": 1.3}, {})
add_mod("a_zelazny", "Żelaznego Muru", ["armor", "helmet"], {"def": 1.4}, {"def": 10})
add_mod("a_lekki", "Lekki", ["armor", "helmet"], {"def": 0.9}, {"atk": 5})
add_mod("a_zreczny", "Zręczny", ["armor", "helmet"], {"def": 1.05}, {"atk": 10})
add_mod("a_zdrowy", "Zdrowy", ["armor", "helmet"], {"hp_max": 1.2}, {"hp_max": 50})
add_mod("a_zywotny", "Żywotny", ["armor", "helmet"], {"hp_max": 1.4}, {"hp_max": 100})
add_mod("a_niezniszczalny", "Niezniszczalny", ["armor", "helmet"], {"def": 1.6}, {"hp_max": 50})
add_mod("a_ochronny", "Ochronny", ["armor", "helmet"], {"def": 1.15}, {"hp_max": 30})
add_mod("a_kolczasty", "Kolczasty", ["armor", "helmet"], {"def": 1.1}, {"atk": 15})
add_mod("a_odbijajacy", "Odbijający", ["armor", "helmet"], {"def": 1.25}, {"atk": 20})
add_mod("a_swiety", "Święty", ["armor", "helmet"], {"def": 1.3}, {"hp_max": 150})
add_mod("a_mroczny", "Mroczny", ["armor", "helmet"], {"def": 1.4}, {"hp_max": -20})
add_mod("a_starozytny", "Starożytny", ["armor", "helmet"], {"def": 1.35}, {"def": 25})
add_mod("a_zapomniany", "Zapomniany", ["armor", "helmet"], {"def": 1.2}, {"def": 15, "hp_max": 40})
add_mod("a_krolewski", "Królewski", ["armor", "helmet"], {"def": 1.3}, {"atk": 10})
add_mod("a_tytanowy", "Tytanowy", ["armor", "helmet"], {"def": 1.5}, {"hp_max": 200})
add_mod("a_demoniczny", "Demoniczny", ["armor", "helmet"], {"def": 1.6}, {"hp_max": -50, "atk": 30})
add_mod("a_boski", "Boski", ["armor", "helmet"], {"def": 1.8}, {"hp_max": 300, "atk": 20})

# === AKCESORIA (20 Modyfikatorów) ===
add_mod("r_blyszczacy", "Błyszczący", ["accessory"], {"hp_max": 1.1}, {})
add_mod("r_cenny", "Cenny", ["accessory"], {"hp_max": 1.2}, {"atk": 5, "def": 5})
add_mod("r_szczesliwy", "Szczęśliwy", ["accessory"], {"atk": 1.1, "def": 1.1}, {})
add_mod("r_wojownika", "Wojownika", ["accessory"], {"atk": 1.3}, {"atk": 15})
add_mod("r_straznika", "Strażnika", ["accessory"], {"def": 1.3}, {"def": 15})
add_mod("r_zycia", "Życia", ["accessory"], {"hp_max": 1.5}, {"hp_max": 100})
add_mod("r_witalnosci", "Witalności", ["accessory"], {"hp_max": 1.3}, {"hp_max": 200})
add_mod("r_krwi", "Krwi", ["accessory"], {"atk": 1.2}, {"hp_max": 50})
add_mod("r_magiczny", "Magiczny", ["accessory"], {"atk": 1.15, "def": 1.15}, {})
add_mod("r_runiczny", "Runiczny", ["accessory"], {"atk": 1.2, "def": 1.2}, {"hp_max": 40})
add_mod("r_przeklety", "Przeklęty", ["accessory"], {"atk": 1.5, "def": 1.5}, {"hp_max": -100})
add_mod("r_swiety", "Święty", ["accessory"], {"def": 1.4}, {"hp_max": 150})
add_mod("r_mroczny", "Mroczny", ["accessory"], {"atk": 1.4}, {"def": -10})
add_mod("r_starozytny", "Starożytny", ["accessory"], {"atk": 1.25, "def": 1.25}, {"hp_max": 80})
add_mod("r_mistyczny", "Mistyczny", ["accessory"], {"atk": 1.3, "def": 1.3}, {})
add_mod("r_krolewski", "Królewski", ["accessory"], {"atk": 1.3, "def": 1.3, "hp_max": 1.3}, {})
add_mod("r_nieziemski", "Nieziemski", ["accessory"], {"atk": 1.4, "def": 1.4}, {"hp_max": 120})
add_mod("r_tytanowy", "Tytanowy", ["accessory"], {"def": 1.5}, {"hp_max": 250})
add_mod("r_demoniczny", "Demoniczny", ["accessory"], {"atk": 1.6}, {"def": -20, "hp_max": -50})
add_mod("r_boski", "Boski", ["accessory"], {"atk": 1.5, "def": 1.5, "hp_max": 1.5}, {"hp_max": 300, "atk": 50, "def": 50})
