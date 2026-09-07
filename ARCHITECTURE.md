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
│ - Pasek HP (❤)   │ • show_expeditions()  - Polowania        │
│ - Statystyki      │ • show_dungeons()     - 8 Lochów         │
│ - Złoto & Przyciski│ • show_blacksmith()   - Kuźnia & Klejnoty│
│ - Wyciszenie 🔊/🔇│ • show_alchemy()      - Ogród & Warzenie │
│ - Zapisz / Wyjdź  │ • show_achievements() - Osiągnięcia      │
│                   │ • show_bestiary()     - Statystyki dusz  │
└───────────────────┴──────────────────────────────────────────┘
```

---

## ⚔️ 2. Matematyka Walki i Formuły (`combat.py` & `player.py`)

### A. Obliczanie Obrażeń Gracza:
$$\text{Base ATK} = \text{Player Strength} + \sum \text{Equipment ATK} + \text{Gem ATK}$$
- **RNG:** Mnożnik losowy $0.85$ do $1.15$.
- **Cios Krytyczny (KRYT):**
  - Szansa bazowa: $\text{Luck} \times 0.2\% + \text{Gem Amethyst} + \text{Perks}$. Maksymalny limit: $50\%$.
  - Mnożnik obrażeń krytycznych: $\times 1.75$.
- **Podwójny Cios (Double Strike):**
  - Szansa z Klejnotu Szafiru + pasywki Domci.
  - Wykonuje natychmiastowy drugi atak w tej samej turze.

### B. Redukcja Obrażeń (Pancerz DEF):
$$\text{Damage Taken} = \max\left(1, \text{Enemy ATK} - \text{Total DEF}\right)$$
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
- **Efekt Ziółka:** Uruchamia in-process animację falującą canvasu bez blokowania interakcji myszy na 60 sekund.

---

## 💾 5. Model Danych Gracza (`Player`)

```python
class Player:
    name: str
    level: int
    exp: int
    gold: int
    hp: float
    strength: int
    agility: int
    vitality: int
    luck: int
    equipment: dict[str, dict]  # np. {"weapon": {"id": "sword_1", "lvl": 0, "sockets": [None]}}
    inventory: list[dict]       # Do 80 slotów (4 strony po 20)
    inventory_stash: list[dict] # Depozyt u Barnaby
    herb_garden: dict           # Stan grządek i timestampy
    active_elixirs: dict        # {"elixir_berserk": 10}
    permanent_perks: list[str]  # Stałe perki konta z osiągnięć
    bestiary: dict[str, int]    # Liczba pokonanych potworów
```
