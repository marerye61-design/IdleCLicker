# Implementacja Poprawek, Balansu i Nowych Funkcji Gry

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Naprawa błędów statystyk ekwipunku, synchronizacja opisów alchemii i perków, naprawa podwójnych nagród questów, dodanie synergii towarzyszy z budynkami rynku, rozszerzenie Ołtarza Bohaterów o masowe rozdawanie punktów i Max HP, masowe warzenie mikstur oraz aktualizacja dokumentacji i rejestru zmian.

**Architecture:** Modyfikacje w modelach danych (`items.py`, `player.py`, `quests.py`, `alchemy.py`, `market.py`) z zachowaniem pełnej wstecznej kompatybilności zapisów (`Player.migrate()`), rozszerzenie interfejsu GUI w `main.py` oraz pełna synchronizacja pomiędzy katalogami `IdleClicker` i `IdleClicker_CustomTkinter`.

**Tech Stack:** Python 3.11+, CustomTkinter, Tkinter, Pygame mixer, Pillow.

**Spec:** Zgłoszenie użytkownika z audytu: zachowanie unikalnych statystyk ekwipunku, synchronizacja opisów eliksirów, 15% szansa na zbiór w perku alchemicznym, naprawa podwójnych wpisów questów, aktualizacja wersji w migracji, synergia towarzyszy z budynkami, masowe dodawanie statystyk, masowe warzenie. Z wykluczeniem systemu many i zmian w bossach 3-8.

## Global Constraints
- Utrzymanie 100% spójności pomiędzy `IdleClicker` a `IdleClicker_CustomTkinter`.
- Aktualizacja `CHANGELOG_DRAFT.md` zgodnie z zasadami projektu.
- Wszelkie rozszerzenia pól `Player` muszą mieć bezpieczną inicjalizację w `Player.migrate()`.
- Kompilacja `python -m py_compile` na wszystkich zmodyfikowanych plikach w obu repozytoriach.

## Review Focus
- Czy przedmioty z `crit_chance` (np. `wep_yomen`, `wep_void_blade`) zachowują krytyk po przejściu przez konstruktor `Equipment`?
- Czy zadania dające złoto i przedmiot nie tworzą zdublowanego wpisu w `reward_history`?
- Czy starsze zapisy po jednokrotnym wczytaniu mają `version == "1.1"` i nie pytają ponownie o starszą wersję?
- Czy synergia towarzyszy z budynkami poprawnie zwiększa pasywne złoto na sekundę i odświeża statystyki gracza?
- Czy masowe dodawanie statystyk w Ołtarzu nie przekracza limitów (30% kryta, 50% łupu)?

---

### Task 1: Zachowanie unikalnych statystyk przedmiotów w `items.py`

**Files:**
- Modify: `items.py:18-47`
- Test: `test_equipment_stats.py`

**Interfaces:**
- Consumes: `Equipment.__init__(item_id, name, description, value, slot, stats, level_req=1, rarity="Zwykły")`
- Produces: `Equipment.stats` zachowujące unikalne cechy z `stats` (`crit_chance`, `atk`, `def`, `hp_max`) połączone z bazowymi formułami `new_stats`.

- [ ] **Step 1: Napisz test jednostkowy weryfikujący zachowanie `crit_chance` i `hp_max` na broniach i zbrojach**
- [ ] **Step 2: Uruchom test, aby upewnić się, że zawodzi (FAIL: brak kryta w wep_yomen)**
- [ ] **Step 3: Popraw `Equipment.__init__` w `items.py`, aby scalał dodatkowe atrybuty z `stats` z `new_stats`**
- [ ] **Step 4: Uruchom test i zweryfikuj, że przechodzi (PASS)**

---

### Task 2: Synchronizacja opisów eliksirów w `alchemy.py` i poprawka perku alchemika w `main.py`

**Files:**
- Modify: `alchemy.py:90-154`
- Modify: `main.py:4075, 4125, 4250`

**Interfaces:**
- `RECIPES_DB`: Opisy eliksirów odzwierciedlające faktyczne buffy (+35% ATK, +35% DEF, +15% podwójny cios, +50% krytyk).
- `main.py`: `perk_alchemist_touch` z losowaniem 15% szansy (`random.random() < 0.15`).

- [ ] **Step 1: Zaktualizuj opisy w `alchemy.py` (`RECIPES_DB`)**
- [ ] **Step 2: Zmień warunek `count` w `harvest_all`, `harvest_single` oraz `make_harvest` w `main.py` na 15% szansy**
- [ ] **Step 3: Przetestuj działanie perku i receptur skryptem weryfikacyjnym**

---

### Task 3: Naprawa podwójnych nagród w zadaniach fabularnych w `quests.py`

**Files:**
- Modify: `quests.py:77-94`

**Interfaces:**
- `Quest.claim_reward(player)`: Rejestracja pojedynczego wpisu w historii, przyznanie exp jeśli zdefiniowano w nagrodach.

- [ ] **Step 1: Zmodyfikuj `claim_reward` w `quests.py` tak, aby nie rejestrować nagrody podwójnie gdy występuje złoto i przedmiot**
- [ ] **Step 2: Dodaj obsługę `if 'exp' in self.rewards: player.add_exp(self.rewards['exp'])`**
- [ ] **Step 3: Uruchom test jednostkowy weryfikujący liczbę wpisów w `player.reward_history`**

---

### Task 4: Wsteczna kompatybilność wersji zapisu w `player.py`

**Files:**
- Modify: `player.py:79-126`

**Interfaces:**
- `Player.migrate()`: Ustawia `self.version = "1.1"` dla wczytywanych starszych stanów gry.

- [ ] **Step 1: Dodaj aktualizację `self.version = "1.1"` w `Player.migrate()`**
- [ ] **Step 2: Przetestuj migrację obiektu z wersją "1.0"**

---

### Task 5: Synergia towarzyszy z budynkami rynku w `market.py`, `player.py` i `main.py`

**Files:**
- Modify: `market.py:1-59`
- Modify: `player.py:140-146, 215-221`
- Modify: `main.py:3053-3086`

**Interfaces:**
- `market.py`: `BUILDING_COMPANIONS = {"b1": "maslak", "b2": "damian", "b3": "domcia", "b4": "eczme", "b5": "pianek", "b6": "yomen"}`
- `player.py`: Obliczanie `gold_per_sec` uwzględniające bonus +25% za zwerbowanego towarzysza i dodatkowe +15% za aktywnego w drużynie.
- `main.py`: Wyświetlanie etykiety synergii w sklepie z budynkami.

- [ ] **Step 1: Dodaj powiązanie budynków z towarzyszami i metodę `get_building_multiplier(player, b_id)` w `market.py`**
- [ ] **Step 2: Zaktualizuj przeliczanie `stats["gold_per_sec"]` w `player.py` (`recalculate_gold_per_sec`) przy wyborze aktywnego towarzysza i w migracji**
- [ ] **Step 3: Wyświetl informację o bonusie w widoku rynku budynków w `main.py`**
- [ ] **Step 4: Napisz test weryfikujący naliczanie zysku pasywnego z synergii**

---

### Task 6: Usprawnienia UX w `main.py`: Rozwój Postaci (Ołtarz) i Masowe Warzenie

**Files:**
- Modify: `main.py:2393-2428` (Ołtarz Bohaterów: przyciski +5, +10, Max HP)
- Modify: `main.py:4165-4226` (Masowe warzenie w kociołku)
- Modify: `main.py:126-142` (Bezpieczny scroll myszy w `ScrollableFrame`)

**Interfaces:**
- `show_stats`: Dodanie przycisków wielokrotnego dodawania punktów i rozwoju Max HP (+10 HP).
- `show_alchemy`: Dodanie możliwości uwarzenia maksymalnej liczby mikstur z dostępnych składników.
- `ScrollableFrame`: Usprawnienie scrolla bez psucia globalnych zdarzeń.

- [ ] **Step 1: Zaktualizuj `ScrollableFrame` o bezpieczne wiązanie zdarzeń myszy**
- [ ] **Step 2: Rozbuduj `show_stats` o opcję +10 Max HP oraz przyciski wielokrotnego dodawania (+5, +10)**
- [ ] **Step 3: Dodaj przycisk "Uwarz Wszystkie" w kociołku alchemicznym**

---

### Task 7: Aktualizacja dokumentacji i synchronizacja katalogów

**Files:**
- Modify: `ARCHITECTURE.md`
- Modify: `CHANGELOG_DRAFT.md`
- Synchronize: Wszystkie zmodyfikowane pliki do `c:\Users\Qonara\Documents\IdleClicker_CustomTkinter\`

- [ ] **Step 1: Zaktualizuj `ARCHITECTURE.md` (aktualne statystyki, usunięcie przestarzałych pól, opis synergii)**
- [ ] **Step 2: Uzupełnij `CHANGELOG_DRAFT.md` o skonsolidowany opis wszystkich zmian**
- [ ] **Step 3: Skopiuj wszystkie zmienione pliki do folderu `IdleClicker_CustomTkinter`**
- [ ] **Step 4: Wykonaj `python -m py_compile` na obu katalogach i potwierdź brak błędów**
