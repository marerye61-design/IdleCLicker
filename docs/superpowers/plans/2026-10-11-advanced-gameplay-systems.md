# Zaawansowane Systemy Rozgrywki: Aktywna Walka, Ekspedycje Towarzyszy, Drzewko Talentów i Potwory Elitarne – Plan Implementacji

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wzbogacić rozgrywkę o 4 kluczowe filary: 
1. Potwory elitarne z modyfikatorami i zwiększonym łupem.
2. Aktywny udział w walce (klikanie bojowe we wroga + aktywne umiejętności Ultimate z cooldownem dla wszystkich 6 towarzyszy).
3. Drzewko talentów (Specjalizacje: Berserker, Obrońca, Łotrzyk) w Ołtarzu Bohaterów z punktami co 5 poziomów.
4. Ekspedycje towarzyszy w Tawernie (wysyłanie wolnych kompanów na misje czasowe IDLE po rzadkie surowce i złoto).

**Architecture:**
- `combat.py`: Klasa `Enemy` wspiera atrybut `is_elite`, `affix` (Płonący, Pancerny, Złocisty, Pradawny) oraz losowanie elitarnych przeciwników w generatorze ekspedycji.
- `player.py`: Nowe pola: `talent_points`, `talents` (słownik odblokowanych rang), `expeditions` (aktywne wyprawy kompanów), `combat_shield`, metody migracji w `Player.migrate()`.
- `main.py`: 
  - Canvas walki: obsługa kliknięcia we wroga (Combat Click), przycisk aktywacji zdolności towarzysza (`[⚡ ZDOLNOŚĆ KOMPANA]`), paski/wskaźniki cooldownu i tarczy.
  - Ołtarz Bohaterów: sekcja Drzewka Talentów z możliwością inwestowania punktów w 3 ścieżki.
  - Tawerna: nowe okno/przycisk "Wyprawy Kompanów" z wyborem misji, odliczaniem czasu i odbiorem nagród.
- Zasady: ZERO zmian w manie, ZERO zmian w bossach 3–8, 100% spójności z `IdleClicker_CustomTkinter`.

**Tech Stack:** Python 3.11+, CustomTkinter / Tkinter, PIL, Pygame Mixer.

**Spec:** Ustalenia dotyczące 4 mechanik podnoszących frajdę i głębię decyzyjną gry.

## Global Constraints
- Zachować 100% kompatybilności wstecznej zapisów poprzez `Player.migrate()`.
- Zapewnić pełną synchronizację z `IdleClicker_CustomTkinter` i pomyślną kompilację `py_compile`.
- NIE dotykać systemu many ani bossów 3–8.
- Aktualizować na bieżąco `CHANGELOG_DRAFT.md`.

## Review Focus
1. Potwory elitarne generują się wyłącznie na wyprawach (nie naruszają dedykowanych bossów lochów).
2. Aktywne kliknięcie podczas walki działa tylko przy aktywnej walce i żywym wrogu.
3. Umiejętności towarzyszy poprawnie respektują cooldown (np. 4 tury) i resetują się między walkami.
4. Ekspedycje towarzyszy nie pozwalają wysłać aktywnego kompana walczącego u boku gracza.
5. Inwestowanie punktów talentów poprawnie weryfikuje posiadane punkty i aplikuje bonusy do statystyk gracza.

---

### Task 1: Potwory Elitarne i Modyfikatory Bojowe (`combat.py`, `main.py`)
**Files:**
- Modify: `combat.py`
- Modify: `main.py`
- Test: `test_interactive_combat.py`

**Interfaces:**
- Produces: `enemy.is_elite: bool`, `enemy.affix: str`, `enemy.affix_label: str`, mnożniki statystyk i nagród w `combat.py`
- UI: Wyświetlanie złotego tytułu i gwiazdek w widoku walki w `main.py`

- [ ] **Step 1: Napisać test jednostkowy dla generowania elitarnych potworów**
- [ ] **Step 2: Zaimplementować modyfikatory elitarne w `combat.py`**
- [ ] **Step 3: Zaktualizować interfejs walki w `main.py` o wizualne oznaczenie wrogów elitarnych**
- [ ] **Step 4: Potwierdzić przejście testu**

---

### Task 2: Aktywna Walka – Klikanie Bojowe i Zdolności Kompanów (`combat.py`, `player.py`, `main.py`)
**Files:**
- Modify: `player.py`
- Modify: `combat.py`
- Modify: `main.py`
- Test: `test_interactive_combat.py`

**Interfaces:**
- Produces: 
  - `main.py:on_enemy_clicked()` zadające obrażenia klikera
  - Zdolności 6 towarzyszy (Eczme: Serwis/Stun, Pianek: Tarcza, Domcia: Dym/Heal, Damian: Szarża/ArmorBreak, Maślak: Pączek/Gold, Yomen: Klucz/Slow)
  - `combat_shield` w `Player` chroniący przed ciosami

- [ ] **Step 1: Napisać test jednostkowy dla mechaniki kliknięcia bojowego, tarczy i zdolności kompanów**
- [ ] **Step 2: Zaimplementować logikę tarczy i efektów statusowych w `player.py` i `combat.py`**
- [ ] **Step 3: Dodać obsługę interakcji na Canvasie walki i przyciski zdolności w `main.py`**
- [ ] **Step 4: Przetestować i potwierdzić pomyślne wykonanie**

---

### Task 3: Drzewko Talentów w Ołtarzu Bohaterów (`player.py`, `main.py`)
**Files:**
- Modify: `player.py`
- Modify: `main.py`
- Test: `test_talents.py`

**Interfaces:**
- Produces: `player.talent_points: int`, `player.talents: dict`, `player.invest_talent(path, node_id)`, `player.get_talent_bonus(name)`
- UI: Interfejs Drzewka Talentów w `show_stats` w `main.py`

- [ ] **Step 1: Napisać test jednostkowy dla przyznawania punktów talentów i naliczania bonusów**
- [ ] **Step 2: Zaimplementować strukturę talentów i migrację w `player.py`**
- [ ] **Step 3: Dodać wizualny panel specjalizacji w oknie Ołtarza Bohaterów w `main.py`**
- [ ] **Step 4: Potwierdzić przejście testu**

---

### Task 4: Ekspedycje Towarzyszy w Tawernie (`player.py`, `main.py`)
**Files:**
- Modify: `player.py`
- Modify: `main.py`
- Test: `test_companion_expeditions.py`

**Interfaces:**
- Produces: `player.expeditions: dict`, `player.start_expedition(comp_id, exp_type)`, `player.claim_expedition(comp_id)`
- UI: Okno "Wyprawy Kompanów" w Tawernie w `main.py`

- [ ] **Step 1: Napisać test jednostkowy dla wysyłania na wyprawy, odliczania czasu i odbioru nagród**
- [ ] **Step 2: Zaimplementować mechanikę ekspedycji i definicje w `player.py` z migracją**
- [ ] **Step 3: Dodać interfejs wypraw w Tawernie w `main.py`**
- [ ] **Step 4: Potwierdzić przejście testu**

---

### Task 5: Weryfikacja Całości, Synchronizacja i CHANGELOG_DRAFT.md
**Files:**
- Modify: `CHANGELOG_DRAFT.md`
- Sync: `IdleClicker` -> `IdleClicker_CustomTkinter`

- [ ] **Step 1: Zaktualizować `CHANGELOG_DRAFT.md` o wszystkie 4 systemy**
- [ ] **Step 2: Uruchomić pełny zestaw testów regresyjnych**
- [ ] **Step 3: Zsynchronizować pliki do `IdleClicker_CustomTkinter` i skompilować `py_compile` w obu repozytoriach**
