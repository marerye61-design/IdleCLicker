# Rules for IdleClicker Development (AI Agents & Human Devs)

> **Witaj!** Zanim wprowadzisz jakiekolwiek zmiany w kodzie gry, zapoznaj się z pełną dokumentacją w pliku [`CODEX.md`](CODEX.md) oraz [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## 📝 1. Automatyczny Rejestr Zmian (Changelog Tracker)

1. **Rejestrowanie Zmian Na Bieżąco**:
   - Za każdym razem, gdy wprowadzane są jakiekolwiek zmiany w kodzie, mechanikach, grafikach, balansie czy UI, należy zwięźle i treściwie dopisać punkt do pliku `CHANGELOG_DRAFT.md`.
2. **Konsolidacja i Brak Duplikatów / Cofnięć**:
   - Jeżeli nowa zmiana poprawia, modyfikuje lub cofa poprzednią tymczasową poprawkę w ramach tego samego cyklu wydania, należy uaktualnić lub scalić istniejący wpis w `CHANGELOG_DRAFT.md` zamiast dodawać powielone czy sprzeczne punkty. Opis ma przedstawiać ostateczny, skonsolidowany efekt zmian.
3. **Kategorie w `CHANGELOG_DRAFT.md`**:
   - Zmiany powinny być ustrukturyzowane i kategoryzowane (np. `🔮 Magiczne Klejnoty & Kuźnia`, `🧪 Alchemia & Ogród`, `⚔️ Ekwipunek & Przedmioty`, `🏰 Lochy & Bossowie`, `📜 Tawerna & Tablica Ogłoszeń`, `🎮 Mechanika & UX`, `🚀 Launcher & System`).
4. **Automatyczne Czyszczenie przy Publikacji (Release)**:
   - Podczas budowania nowej wersji i publikacji wydania na GitHub, skrypt `upload_release.py` / `publish_github_release_*.py` odczytuje treść z `CHANGELOG_DRAFT.md` jako opis wydania, a następnie czyści plik `CHANGELOG_DRAFT.md`, przygotowując go pod kolejną wersję gry.

---

## 🔄 2. Zasada Podwójnej Synchronizacji Katalogów
- Zawsze utrzymuj 100% spójności pomiędzy katalogami `IdleClicker_CustomTkinter` i `IdleClicker`.
- Po wprowadzeniu i przetestowaniu zmian skompiluj pliki (`python -m py_compile ...`) w obu repozytoriach.

---

## 🛡️ 3. Spójność Zapisów Gry i Migracje
- Wszelkie rozszerzenia pól klasy `Player` muszą posiadać bezpieczną inicjalizację w metodzie `Player.migrate()` w pliku `player.py`.
