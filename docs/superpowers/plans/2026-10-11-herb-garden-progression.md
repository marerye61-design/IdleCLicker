# Progresja Ogrodu Ziół i Alchemii – Plan Implementacji

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Zablokować początkowy dostęp do Ogrodu Ziół i Kociołka, wprowadzając stopniowe odblokowywanie: Grządka #1 poprzez płatną dzierżawę u Karczmarza Barnaby (150 złota) z dedykowanym dialogiem, a kolejne Grządki #2–#4 jako nagrody za zadania fabularne towarzyszy (Eczme, Pianek, Domcia).

**Architecture:** 
- `Player` przechowuje status odblokowania każdej grządki (`unlocked: True/False` lub listę indeksów) z pełną migracją w `Player.migrate()`.
- `quests.py` rozszerza nagrody zadań `q_party_eczme`, `q_party_pianek`, `q_party_domcia` o klucz `'garden_plot'`, automatycznie odblokowujący grządkę w `claim_reward()`.
- `npc_lore.py` oraz `main.py` wprowadzają opcję dzierżawy u Barnaby za 150 złota.
- `main.py` w `show_alchemy()` renderuje czytelne karty zablokowanych grządek z informacją o wymaganiach oraz zabezpiecza Kociołek przed użyciem bez żadnej aktywnej grządki.

**Tech Stack:** Python 3.11+, CustomTkinter / Tkinter, Pygame Mixer.

**Spec:** Ustalenia z konwersacji z użytkownikiem (brak ziół na start, odblokowanie Grządki #1 u Barnaby za opłatą i dialog, Grządki #2–#4 stopniowo z zadaniami).

## Global Constraints
- Zachować 100% kompatybilności wstecznej zapisów poprzez `Player.migrate()`.
- Zapewnić pełną synchronizację z `IdleClicker_CustomTkinter` i pomyślną kompilację `py_compile`.
- NIE dotykać systemu many ani bossów 3–8.
- Aktualizować na bieżąco `CHANGELOG_DRAFT.md`.

## Review Focus
1. Nowo tworzona postać zaczyna z wszystkimi 4 grządkami zablokowanymi (`unlocked=False`).
2. Gracz bez wystarczającej ilości złota (<150) nie może wydzierżawić grządki u Barnaby.
3. Po zakupie u Barnaby odejmowane jest 150 złota, Grządka #1 staje się natychmiast odblokowana i rozpoczyna wzrost ziół.
4. Odbiór zadań `q_party_eczme`, `q_party_pianek`, `q_party_domcia` bezbłędnie odblokowuje odpowiednio Grządki #2, #3, #4.
5. Starsze zapisy graczy (`Player.migrate()`) poprawnie zachowują lub odblokowują grządki na podstawie dotychczasowych osiągnięć i członków drużyny bez utraty danych.

---

### Task 1: Model Danych Ogrodu i Migracja w `Player`
**Files:**
- Modify: `player.py`
- Test: `test_herb_garden_progression.py`

**Interfaces:**
- Consumes: `HERBS_DB` z `alchemy.py`
- Produces: `player.herb_garden` z polem `"unlocked": bool`, metody `player.unlock_garden_plot(idx)`, `player.is_plot_unlocked(idx)`, `player.get_unlocked_plots_count()`

- [ ] **Step 1: Napisać test jednostkowy weryfikujący blokadę na starcie i metody odblokowywania**
- [ ] **Step 2: Uruchomić test i upewnić się, że zawodzi (brak metod/pola unlocked)**
- [ ] **Step 3: Zaimplementować strukturę z polem `"unlocked"` i metody w `player.py` oraz bezpieczną migrację w `Player.migrate()`**
- [ ] **Step 4: Uruchomić test i upewnić się, że przechodzi pomyślnie**

---

### Task 2: Integracja Nagród Zadań w `quests.py`
**Files:**
- Modify: `quests.py`
- Test: `test_herb_garden_progression.py`

**Interfaces:**
- Consumes: `player.unlock_garden_plot(idx)` z Task 1
- Produces: `rewards['garden_plot']` dla zadań `q_party_eczme` (plot 1), `q_party_pianek` (plot 2), `q_party_domcia` (plot 3) oraz obsługę w `Quest.claim_reward()`

- [ ] **Step 1: Napisać test sprawdzający odblokowanie grządek po odebraniu nagrody z questów**
- [ ] **Step 2: Zaktualizować definicje zadań w `QUESTS_DB` i metodę `claim_reward` w `quests.py`**
- [ ] **Step 3: Uruchomić test i potwierdzić pomyślne wykonanie**

---

### Task 3: Dialog i Dzierżawa Grządki u Karczmarza Barnaby w Tawernie
**Files:**
- Modify: `npc_lore.py`
- Modify: `main.py`
- Test: `test_herb_garden_progression.py`

**Interfaces:**
- Consumes: `player.unlock_garden_plot(0)`, `player.gold`
- Produces: Nowa opcja dialogowa u Barnaby w `NPC_DB["innkeeper"]`, obsługa akcji zakupu w `main.py:show_npc_dialog`

- [ ] **Step 1: Dodać opcję dialogową w `npc_lore.py`**
- [ ] **Step 2: Zaimplementować obsługę transakcji zakupu dzierżawy (150 złota) w oknie dialogu NPC w `main.py`**
- [ ] **Step 3: Napisać i uruchomić test logiki zakupu u Barnaby**

---

### Task 4: UI Ogrodu Ziół i Kociołka Alchemicznego (`main.py`)
**Files:**
- Modify: `main.py`
- Test: `test_herb_garden_progression.py`

**Interfaces:**
- Consumes: `player.is_plot_unlocked(idx)`, `player.get_unlocked_plots_count()`
- Produces: Widok zablokowanych kart w `show_alchemy()` (ikona kłódki, opis wymaganego questa/dzierżawy, przycisk przejścia do Tawerny), blokada "Zbierz wszystkie" dla zablokowanych grządek, informacja w Kociołku gdy 0 grządek.

- [ ] **Step 1: Zmodyfikować `show_alchemy()` w `main.py` o renderowanie zablokowanych grządek i Kociołka**
- [ ] **Step 2: Zaktualizować `harvest_all()` i timery, aby ignorowały zablokowane grządki**
- [ ] **Step 3: Przetestować wizualnie i logicznie odświeżanie widoku**

---

### Task 5: Synchronizacja, Rejestr Zmian (`CHANGELOG_DRAFT.md`) i Kompilacja
**Files:**
- Modify: `CHANGELOG_DRAFT.md`
- Sync: `IdleClicker` -> `IdleClicker_CustomTkinter`

- [ ] **Step 1: Zaktualizować `CHANGELOG_DRAFT.md` zgodnie z Zasadą 1**
- [ ] **Step 2: Przetestować cały zestaw testów jednostkowych**
- [ ] **Step 3: Skopiować zmienione pliki do `IdleClicker_CustomTkinter` i skompilować `py_compile` w obu repozytoriach**
