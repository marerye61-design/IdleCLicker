# 📜 Pełna Historia Zmian Gry IdleClicker (Changelog History)

Ten dokument zawiera podsumowanie wszystkich dotychczasowych wersji i zaimplementowanych mechanik, stanowiąc bazę wiedzy dla deweloperów i modeli AI.

---

## 🚀 Wersja 0.18 (Najnowsza)
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
