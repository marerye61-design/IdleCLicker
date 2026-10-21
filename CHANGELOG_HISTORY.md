# 📜 Pełna Historia Zmian Gry IdleClicker (Changelog History)

Ten dokument zawiera podsumowanie wszystkich dotychczasowych wersji i zaimplementowanych mechanik, stanowiąc bazę wiedzy dla deweloperów i modeli AI.

---

## 🚀 Wersja 0.19 (Najnowsza)
- **🤖 Port Godot 4 & Wydanie Android APK**:
  - Pełny natywny port silnika gry w Godot 4 (`IdleClicker_Godot`) z zachowaniem 100% mechanik, balansu i lore.
  - Oficjalna paczka instalacyjna `IdleClicker.apk` na Androida (podpis v2/v3, 44.2 MB).
- **📱 Adaptacja do Orientacji Pionowej (Portrait Mode)**:
  - Baza 720×1280 (sensor portrait), responsywny podgląd desktopowy (450×800).
  - Ergonomiczny dolny pasek nawigacji `BottomNav` z 12 dotykowymi kafelkami, uwalniający 100% szerokości ekranu na aktywny moduł.
  - Dwurzędowy pasek statusu `TopHUD` (rząd 1: awatar, poziom, złoto, klikacz; rząd 2: paski HP, MP, EXP, towarzysz).
  - Mobilna arena walki `CombatView` z układem wrogów obok siebie i siatką akcji 2×2 pod kciukiem.
  - Plecak `InventoryView` z 5-kolumnową siatką dotykową i poziomą wstęgą rynsztunku.
  - Pełnoekranowe mobilne przełączniki zakładek w `StatsView` i `AlchemyView`.
- **⚔️ Złote Ramki Pixel-Art dla Wszystkich Przedmiotów i Sklepów**:
  - Zunifikowane, eleganckie złote ramki pixel-art `#0c0a10` dla kompletu 48 ikon (rynsztunek, mikstury, zioła, klejnoty, relikwie).
  - Wycentrowanie i wyczyszczenie grafik mithrilowych, stalowych i mikstur.
- **🛡️ Rebalans Bossów i Wczesnej Gry**:
  - Przeliczenie statystyk bossów (Giga Ork Ptyś 2075 HP / 52 ATK, Arcymag Kollman 6550 HP / 140 ATK, skalowanie 8 lochów do 1.25M HP).
  - Dedykowane portrety bossów w walce i konsoli F12.
  - Odblokowanie punktów talentów od 10 poziomu (co 5 poziomów) z bezpieczną migracją.
  - Zbalansowanie początkowych statystyk gracza (85 HP / 8 ATK / 4 DEF).
- **🌿 Progresja Ogrodu Ziół u Domci & Barnaba**:
  - Blokada startowa ogrodu i kociołka; odblokowywanie Grządki #1 poprzez dzierżawę u Karczmarza za 150 złota.
  - Kolejne grządki jako nagrody fabularne kompanów (Eczme poz. 10+, Pianek poz. 20+, Domcia poz. 40+).
- **🏰 Menu Główne, System Profili & Dark Fantasy Forge UI**:
  - Dedykowany launcher/ekran główny z obsługą wielu niezależnych profili zapisu (`user://saves/`).
  - Proceduralny shader płomieni kuźni `forge_flame.gdshader`, emiter iskier `EmberSparks` i sprężyste mikro-reakcje.
  - Obsługa porażki w walce (0 HP), ewakuacja do karczmy i darmowy odpoczynek przy kominku.
  - Hurtowa sprzedaż zaznaczonych przedmiotów z klawiszem CTRL.

---

## 🏔️ Wersja 0.18
- **🔮 Magiczne Klejnoty & Kuźnia Kowala**:
  - 5 rodzajów klejnotów: Rubin (+ATK), Szmaragd (+HP/DEF), Szafir (+Podwójny Cios), Ametyst (+Kryt), Topaz (+Złoto/Drop).
  - Dynamiczne skalowanie mocy klejnotu na podstawie wymaganego poziomu przedmiotu (`level_req`).
  - Wykuwanie 1. i 2. gniazda u Kowala za złoto i składniki z potworów (Kły, Jad, Ektoplazma, Rdzeń).
- **🔊 Silnik Dźwiękowy Retro (16-bit SFX)**:
  - Dedykowany moduł `sound_manager.py` (Pygame mixer) odtwarzający dźwięki walki, ciosów krytycznych, leczenia, awansu poziomu i wejścia do lochu.
  - Przełącznik wyciszenia w menu bocznym (`🔊 / 🔇`).
- **🧪 Alchemia & Ogród Ziół u Domci**:
  - Ogród z 5 gatunkami ziół (Amanita, Mech, Kwiat, Korzeń, Ziółko) rosnącymi w czasie rzeczywistym z odliczaniem na żywo.
  - Kociołek alchemiczny warzący eliksiry bojowe na 10 kolejnych walk.
  - Efekt psychodeliczny po zażyciu Ziółka (60-sekundowa tęczowa fala, spowolnienie czasu i +50% do krytyka).
- **🏆 Księga Osiągnięć i Trofeów**:
  - Ponad 20 wyzwań w 6 kategoriach ze stałymi perkami konta.
- **🛏️ Odpoczynek i Regeneracja w Tawernie**:
  - 20-sekundowa regeneracja punktów życia przy kominku z animowanym paskiem zdrowia w czasie rzeczywistym.
- **🎮 Wygodne Wczytywanie Zapisu**:
  - Wczytywanie gry dwuklikiem oraz klawiszem Enter.

---

## 🏔️ Wersja 0.17
- **🏰 Nowy Loch 'Górska Przełęcz' (Loch 2, Lvl 15+)** z bossem **Kollmanem 'Wojowniczym Magiem'**.
- **🎬 Kinowe Wprowadzenia Bossów (Intro Cutscenes)** z opcją interaktywnego przewijania dialogów.
- **💥 Unikalne Animacje Ataków Bossów**: Zamach kolczastą maczugą Ptysia oraz wirująca kula ognia Kollmana miotana w stronę gracza.
- **📜 Nowe Zadania Fabularne NPC (Lvl 1 - 50)** u 6 towarzyszy w tawernie z nagrodami w postaci potężnego ekwipunku legendarnego.
- **⚖️ Balans Doświadczenia (EXP)**: Czas osiągnięcia 100 poziomu zbalansowany do ok. 14 godzin aktywnej gry.

---

## 🎨 Wersja 0.15 & 0.16
- **Przejście na CustomTkinter**: Nowoczesne zaokrąglone krawędzie, płynniejszy interfejs.
- **🛡️ Globalny System Przechwytywania Błędów (`Crash Handler`)**: Bezpieczne logowanie wyjątków do `error_log.txt`.
- **4-Stronicowy Ekwipunek (Pojemność 80 Slotów)** z paginacją `[◀] [1] [2] [3] [4] [▶]`.
- **🎁 Bezpieczny Depozyt Nagród u Karczmarza Barnaby** dla łupów zdobytych przy pełnym plecaku.
- **📋 Tablica Ogłoszeń Karczmarza** z 3 losowymi zleceniami dziennymi.

---

## ⚔️ Wersje 0.10 - 0.14
- Podstawowy silnik turowy, system poziomów bohatera (Siła, Zręczność, Żywotność, Szczęście).
- Sklep wielopoziomowy ze zbrojami, hełmami, butami i bronią.
- System losowych modyfikatorów przedmiotów (przedrostki i przyrostki).
- Podstawowy launcher z mechanizmem automatycznych aktualizacji z GitHub Releases.
