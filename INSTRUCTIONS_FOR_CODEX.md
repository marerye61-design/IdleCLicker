# Skrót instrukcji dla asystentów

Dokument źródłowy zasad repozytorium to [AGENTS.md](AGENTS.md). Przed zmianą kodu przeczytaj również [CODEX.md](CODEX.md) i [ARCHITECTURE.md](ARCHITECTURE.md). Ten plik jest krótką ściągą, nie niezależnym zestawem zasad.

## Zasady pracy

- Zachowuj spójność `IdleClicker` i `IdleClicker_CustomTkinter`; po zmianach porównaj zmodyfikowane pliki i skompiluj je w obu katalogach.
- Każdą zmianę kodu, UI, balansu lub mechanik odnotuj w `CHANGELOG_DRAFT.md`, konsolidując istniejące wpisy z tego cyklu.
- Nowe lub zmienione pola `Player` inicjalizuj bezpiecznie w `Player.migrate()`.
- Tkinter aktualizuj wyłącznie w głównym wątku; timery i animacje planuj przez `root.after()`.
- Do obniżenia widgetu Canvas używaj `tk.Misc.lower(widget)`, nie `canvas.lower()`.
- Zachowuj kompatybilność starych zapisów i nie usuwaj danych gracza przy migracji.

## Projekt

- Python 3.11+, CustomTkinter/Tkinter, Pillow, pygame.
- `main.py` prowadzi aplikację i UI; `player.py` przechowuje stan gracza i migracje; systemy gry mają osobne moduły.
- Zapisy znajdują się w `%APPDATA%\IdleClicker\saves\`; ich format to pickle.
- Uruchomienie developerskie: `python main.py`.
- Kontrola składni: `python -m py_compile main.py player.py combat.py gems.py alchemy.py bounties.py`.
- Budowanie paczki: `python scratch/run_pyinstaller_build.py`.
