# 🧙‍♂️ CODEX & Instrukcje dla Asystenta AI (ChatGPT / OpenAI Codex / Claude / Copilot)

> **Drogi Asystencie AI!** Ten dokument zawiera kompletny przewodnik po architekturze, zasadach tworzenia kodu, konwencjach oraz pułapkach technicznych gry **IdleClicker (Fantasy Edition)**. Przeczytaj go uważnie przed przystąpieniem do jakichkolwiek modyfikacji!

---

## 📌 1. O Projekcie (Project Overview)
- **Tytuł:** IdleClicker (Fantasy Edition)
- **Gatunek:** Idle RPG / Dark Fantasy Clicker / Dungeon Crawler
- **Język i Środowisko:** Python 3.11+ / Python 3.14 (64-bit) na systemie Windows
- **Główne Biblioteki:**
  - `customtkinter` & standardowy `tkinter` (Interfejs graficzny)
  - `pygame` (Moduł miksera audio `pygame.mixer` do 16-bitowych retro dźwięków)
  - `Pillow (PIL)` (Obsługa grafik, portretów, ikon przedmiotów i teł)
  - `PyInstaller` (Kompilacja do samodzielnych plików `.exe`)
- **Repozytorium GitHub:** `marerye61-design/IdleCLicker` (Domyślny branch: `master`)

---

## 📜 2. Święte Zasady Projektu (Core Rules & Workflow)

### 📝 A. Automatyczny Rejestr Zmian (`CHANGELOG_DRAFT.md`)
1. **Rejestrowanie na bieżąco**: Po każdej zmianie w kodzie, mechanikach, UI, balansie czy audio, **bezwzględnie dopisz zwięzły punkt** do pliku `CHANGELOG_DRAFT.md`.
2. **Brak duplikatów i cofnięć**: Jeśli modyfikujesz lub poprawiasz wcześniejszą zmianę, zaktualizuj/scal istniejący wpis zamiast tworzyć sprzeczne punkty.
3. **Kategorie**: Używaj standardowych kategorii (np. `🔮 Magiczne Klejnoty & Gniazda`, `🧪 Alchemia & Ogród`, `⚔️ Ekwipunek & Przedmioty`, `🏰 Lochy & Bossowie`, `📜 Tawerna & Tablica Ogłoszeń`, `🎮 Mechanika & Balans`).
4. **Czyszczenie przy publikacji**: Przy tworzeniu i publikacji nowej wersji (np. przez skrypt wydania), treść z `CHANGELOG_DRAFT.md` staje się opisem wydania na GitHubie, a plik zostaje wyczyszczony pod kolejną wersję.

### 🔄 B. Synchronizacja Dwóch Katalogów Roboczych
Projekt posiada dwa powiązane foldery robocze:
- `c:\Users\Qonara\Documents\IdleClicker_CustomTkinter` (Główny katalog deweloperski)
- `c:\Users\Qonara\Documents\IdleClicker` (Katalog powiązany z repozytorium git)
**Zawsze kopiuj i kompiluj zmienione pliki do obu katalogów**, aby zachować pełną spójność!

### 🛡️ C. Bezpieczeństwo Zapisów Gry (Saves & Migrations)
- Zapisy gry gracza są serializowane przez moduł `pickle` i przechowywane w katalogu `%APPDATA%\IdleClicker\saves\`.
- **Nigdy nie usuwaj istniejących pól z klasy `Player`** bez dodania odpowiedniej migracji w metodzie `Player.migrate()` w pliku `player.py`. Wszelkie nowe pola muszą mieć bezpieczne wartości domyślne (np. `getattr(self, 'gems', {})`).

---

## ⚠️ 3. Kluczowe Pułapki Techniczne (Technical Gotchas & Pitfalls)

### 1. Tkinter Canvas Stacking Bug (`Canvas.lower()`)
- **Problem:** Wywołanie `canvas.lower()` w Tkinterze odnosi się do metody tagów canvasu (`tag_lower()`), a nie hierarchii okien widgetów, co powoduje błąd `TclError: bad window path name`.
- **Rozwiązanie:** Aby przenieść canvas w tło okna, **zawsze używaj**:
  ```python
  import tkinter as tk
  tk.Misc.lower(self.my_canvas)  # PRAWIDŁOWO
  # LUB: self.my_canvas.tk.call('lower', self.my_canvas._w)
  ```

### 2. Animacje i Wielowątkowość (UI Thread Safety)
- Tkinter nie jest thread-safe! **Nigdy nie modyfikuj widżetów Tkintera bezpośrednio z pobocznego wątku (`threading.Thread`)**.
- Wszelkie aktualizacje UI, timery, animacje czy pętle leczenia wykonuj za pomocą metody `root.after(ms, callback)`.

### 3. Zbieżność Stylu Dark Fantasy (UI Guidelines)
- **Czcionka:** Główny font to `"Georgia"` (np. `("Georgia", 11, "bold")` lub `("Georgia", 14)`).
- **Paleta Barw:**
  - Tło główne / ramki: `#2c1a12`, `#1a100b`, `#1c100b`, `#0d0705`
  - Złoto / Nagłówki: `#f4d03f`, `#f1c40f`, `#d35400`
  - Sukces / HP / Uleczenie: `#27ae60`, `#2ecc71`, `#22c55e`
  - Porażka / Przerwanie / Krytyk: `#7f1d1d`, `#c0392b`, `#e74c3c`
  - Panele tekstowe: `bg="#2c1a12"`, `fg="#ffffff"`, `insertbackground="white"`

### 4. Silnik Dźwiękowy (`SoundManager`)
- Dźwięki są odtwarzane przez singleton `sounds` zdefiniowany w `sound_manager.py`.
- Dostępne metody audio:
  - `sounds.play_sword()` – zamach mieczem
  - `sounds.play_hit()` – standardowe trafienie
  - `sounds.play_crit()` – uderzenie krytyczne (KRYT)
  - `sounds.play_enemy_hit()` – otrzymanie obrażeń przez gracza
  - `sounds.play_potion()` / `sounds.play_heal()` – wypicie mikstury / uleczenie
  - `sounds.play_coin()` – zdobycie złota
  - `sounds.play_level_up()` – awans na wyższy poziom
  - `sounds.play_ui_click()` – kliknięcie w interfejsie
  - `sounds.play_quest_accept()` – przyjęcie misji
  - `sounds.play_quest_complete()` – oddanie questa
  - `sounds.play_dungeon_enter()` – wejście do lochu
  - `sounds.play_boss_intro()` – gong/brass bossa

---

## 🏗️ 4. Przegląd Modułów Gry (Module Architecture)

| Plik | Rola i Zawartość |
| :--- | :--- |
| `main.py` | Główny kontroler gry, routing widoków (`view_panel`), okna dialogowe NPC, panel ekwipunku, kuźnia kowala, odpoczynek w tawernie, konsola debugowania. |
| `player.py` | Model gracza: statystyki, ekwipunek, gniazda klejnotów, bestiariusz, perki, ogród alchemiczny, migracje stanu zapisu. |
| `combat.py` | Silnik walki turowej: obliczanie obrażeń, ciosów krytycznych, podwójnego ataku, szansy na unik, generator potworów i animacje bossów. |
| `gems.py` | Baza danych 5 klejnotów (Rubin, Szmaragd, Szafir, Ametyst, Topaz) oraz formuły dynamicznego skalowania z poziomem przedmiotu (`level_req`). |
| `alchemy.py` | Ogród ziół (Amanita, Mech, Kwiat, Korzeń, Ziółko), czasy wzrostu, warzenie eliksirów (czas trwania: 10 walk) oraz 60-sekundowy efekt psychodeliczny Ziółka. |
| `achievements.py` | Baza 20+ osiągnięć i stałych pasywnych perków konta. |
| `bounties.py` | Tablica Ogłoszeń Karczmarza Barnaby: generowanie 3 losowych zleceń i zarządzanie nagrodami w depozycie. |
| `dungeons.py` | Baza 8 Lochów z unikalnymi bossami, wymaganym poziomem i reliktami. |
| `items.py` | Baza stałych przedmiotów sklepowych, reliktów i łupów. |
| `modifiers.py` | Prefiksy i sufiksy losowych przedmiotów dropiących z potworów. |
| `npc_lore.py` | Opisy fabularne NPC, monologi, zadania kompanów z tawerny. |
| `quests.py` | System zadań fabularnych. |
| `sound_manager.py` | System odtwarzania efektów audio przez Pygame mixer. |
| `IdleClickerLauncher.py` | Autonomiczny launcher z wbudowanym auto-updaterem sprawdzającym nowe wydania na GitHubie. |

---

## 🛠️ 5. Przydatne Komendy Deweloperskie (Cheat Sheet)

### Uruchomienie gry w trybie deweloperskim:
```powershell
python main.py
```

### Uruchomienie launchera:
```powershell
python IdleClickerLauncher.py
```

### Weryfikacja składni / test kompilacji:
```powershell
python -m py_compile main.py gems.py player.py alchemy.py combat.py dungeons.py
```

### Budowanie paczki `.exe` przez PyInstaller:
```powershell
python scratch/run_pyinstaller_build.py
```
*(Tworzy gotowy plik `IdleClicker_X.XX.zip` zawierający `IdleClicker.exe`, `IdleClickerLauncher.exe`, `version.txt` oraz folder `assets`).*

---

> 💡 **Wskazówka:** Przy wprowadzaniu nowych funkcji zachowaj styl Dark Fantasy Pixel Art, dbaj o intuicyjność interfejsu i pamiętaj o dopisaniu punktu do `CHANGELOG_DRAFT.md`!
