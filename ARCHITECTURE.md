# 🏛️ Architektura Systemów Gry IdleClicker

Dokument ten opisuje strukturę danych, przepływ logiki oraz kluczowe formuły matematyczne w grze.

---

## 🧭 1. Architektura Widoków i Przepływ UI (`main.py`)

Główna aplikacja oparta jest o klasę `IdleRPGApp` zarządzającą panelem `view_panel`:

```
┌──────────────────────────────────────────────────────────────┐
│                    GŁÓWNE OKNO APLIKACJI                     │
├───────────────────┬──────────────────────────────────────────┤
│   PANEL BOCZNY    │               VIEW_PANEL                 │
│   (Sidebar)       │           (Dynamiczne Widoki)            │
│                   ├──────────────────────────────────────────┤
│ - Awatar & Nick   │ • show_tavern()       - Tawerna & NPC    │
│ - Poziom & Pasek  │ • show_equipment()    - Plecak (4 str.)  │
│ - Pasek HP (❤)   │ • show_expedition()   - Polowania        │
│ - Statystyki      │ • show_dungeons()     - 8 Lochów         │
│ - Złoto & Przyciski│ • show_blacksmith()   - Kuźnia & Klejnoty│
│ - Wyciszenie 🔊/🔇│ • show_alchemy()      - Ogród & Warzenie │
│ - Zapisz / Wyjdź  │ • show_achievements() - Osiągnięcia      │
│                   │ • show_bestiary()     - Statystyki dusz  │
│                   │ • show_stats()        - Ołtarz Bohaterów │
│                   │ • show_buildings_shop() - Rynek Miasta   │
└───────────────────┴──────────────────────────────────────────┘
```

---

## ⚔️ 2. Matematyka Walki i Formuły (`combat.py` & `player.py`)

### A. Obliczanie Obrażeń Gracza:
$$\text{Raw ATK} = \text{Base ATK} + (\text{Level} - 1) \times 2 + \sum \text{Equipment ATK} + \text{Party ATK} + \text{Gem ATK}$$
$$\text{Total ATK} = \lfloor \text{Raw ATK} \times (1 + \text{BestiaryBonus} + \text{Perks} + \text{Buffs}) \rfloor$$
- **Redukcja obrony wroga:** $\text{Base DMG} = \max(\lfloor 0.25 \times \text{Total ATK} \rfloor, \text{Total ATK} - \lfloor 0.4 \times \text{Enemy DEF} \rfloor)$
- **RNG:** Mnożnik losowy $0.85$ do $1.15$.
- **Cios Krytyczny (KRYT):**
  - Szansa całkowita: $\min(30, \text{Base Crit}) + \sum \text{Equipment Crit} + \text{Gem Amethyst} + \text{Perks} + \text{Buffs}$.
  - Mnożnik obrażeń krytycznych: $\times 1.75$.
- **Podwójny Cios (Double Strike):**
  - Szansa z Klejnotu Szafiru + Wywar Szybkich Stóp + pasywka Domci (+8%).
  - Wykonuje natychmiastowy drugi atak w tej samej turze.

### B. Redukcja Obrażeń Gracza (Armory Mitigation Formula):
$$\text{Mitigation} = \min\left(0.75, \frac{\text{Total DEF}}{\text{Total DEF} + 80 + 4 \times \text{Level}}\right)$$
$$\text{Damage Taken} = \max\left(1, \lfloor \text{Enemy ATK} \times (1.0 - \text{Mitigation}) \times \text{Variance} \rfloor\right)$$
- Z pasywką Damiana (`-10%` finalnych obrażeń).
- Z pasywką Pianka (`+25% DEF` przy zdrowiu $<60\%$).

---

## 🔮 3. Dynamiczne Skalowanie Klejnotów (`gems.py`)

Klejnoty skalują swoje wartości w oparciu o poziom wymagany przedmiotu (`L = item.level_req`):

| Klejnot | Wzór Bonusu | Wartość na 1. lvl | Wartość na 50. lvl |
| :--- | :--- | :---: | :---: |
| 🔴 **Rubin** | $+ (4 + \lfloor L \times 0.45 \rfloor)\text{ ATK}$ | $+4\text{ ATK}$ | $+26\text{ ATK}$ |
| 🟢 **Szmaragd** | $+ (25 + \lfloor L \times 3.5 \rfloor)\text{ HP}$, $+ (3 + \lfloor L \times 0.35 \rfloor)\text{ DEF}$ | $+28\text{ HP}, +3\text{ DEF}$ | $+200\text{ HP}, +20\text{ DEF}$ |
| 🔵 **Szafir** | $+ \min(15, 3 + \lfloor L / 25 \rfloor)\%\text{ Double Strike}$ | $+3\%$ | $+5\%$ |
| 🟣 **Ametyst** | $+ \min(12, 2 + \lfloor L / 30 \rfloor)\%\text{ Szansa na Kryt}$ | $+2\%$ | $+3\%$ |
| 🟡 **Topaz** | $+ \min(40, 10 + \lfloor L / 10 \rfloor)\%\text{ Gold}$, $+ \min(20, 3 + \lfloor L / 25 \rfloor)\%\text{ Drop}$ | $+10\%\text{ G}, +3\%\text{ D}$ | $+15\%\text{ G}, +5\%\text{ D}$ |

---

## 🧪 4. System Alchemii & Ogrodu (`alchemy.py`)

- **Zioła w Ogrodzie:**
  1. `herb_amanita` (Czas wzrostu: 30s)
  2. `herb_moss` (Czas wzrostu: 45s)
  3. `herb_flower` (Czas wzrostu: 60s)
  4. `herb_root` (Czas wzrostu: 90s)
  5. `herb_mystery` - **Ziółko** (Czas wzrostu: 120s)
- **Eliksiry Bojowe:** Trwają przez **10 kolejnych walk** (licznik zmniejsza się po każdym zwycięstwie).
  - *Eliksir Berserkera*: +35% ATK
  - *Mikstura Kamiennej Skóry*: +35% DEF
  - *Wywar Szybkich Stóp*: +15% Szansy na Podwójny Cios
  - *Napar Złotego Rogu*: +40% Złota z walk i lochów
  - *Ziółko (Mocny Wywar)*: +50% Szansy na Krytyk + fala psychodeliczna
- **Masowe Warzenie:** Możliwość uwarzenia 1x lub wszystkich dostępnych mikstur na podstawie zebranych składników.

---

## 🏘️ 5. Rynek i Synergia Towarzyszy (`market.py`)

Budynki w rynku generują pasywny dochód złota na sekundę (`gold_per_sec`). Każdy budynek powiązany jest z jednym z 6 towarzyszy:
- **Cukiernia Maślaka (`b1`)** ➔ Maślak
- **Strażnica Damiana (`b2`)** ➔ Damian
- **Plantacja Ziół Domci (`b3`)** ➔ Domcia
- **Boisko Siatkarskie Eczme (`b4`)** ➔ Eczme
- **Siłownia Pianka (`b5`)** ➔ Pianek
- **Warsztat 'BeeMWe' Yomena (`b6`)** ➔ Yomen

**Mnożniki synergii:**
- Towarzysz w drużynie (`player.party`): **+25% produkcji złota** ($\times 1.25$).
- Towarzysz aktywny w walce (`player.active_companion`): **+40% produkcji złota** ($\times 1.40$).

---

## 💾 6. Model Danych Gracza (`Player`)

```python
class Player:
    name: str
    level: int
    exp: int
    gold: int
    hp: float
    max_hp: int
    stat_points: int
    stats: dict                 # {"base_atk": 12, "base_def": 10, "crit_chance": 0, "bonus_loot_pct": 0, ...}
    party: list[str]            # Odblokowani towarzysze w drużynie
    active_companion: str|None  # Dokładnie 1 aktywny towarzysz
    equipment: dict[str, dict]  # {"weapon": {"id": "wep_maslak", "lvl": 0, "sockets": [None, None]}, ...}
    inventory: list[dict]       # Do 80 slotów (4 strony po 20)
    inventory_stash: list[dict] # Depozyt u Barnaby na nadmiarowe nagrody
    herb_garden: list[dict]     # Stan 4 grządek i timestampy
    active_buffs: dict          # {"elixir_berserk": 10}
    permanent_perks: list[str]  # Stałe perki konta z osiągnięć
    bestiary: dict[str, int]    # Liczba pokonanych potworów
    buildings: dict[str, int]   # {building_id: count}
    reward_history: list[dict]  # Ostatnie 100 wpisów nagród
    daily_challenges: dict      # Zadania dzienne i postęp
    settings: dict              # {"autosave_seconds": 60, "reduced_effects": False, "inventory_sort": "recent"}
    version: str                # "1.1"
```
