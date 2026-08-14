# Rules for IdleClicker Development

## 📝 Automatyczny Rejestr Zmian (Changelog Tracker)

1. **Rejestrowanie Zmian Na Bieżąco**:
   - Za każdym razem, gdy wprowadzane są jakiekolwiek zmiany w kodzie, mechanikach, grafikach, balansie czy UI, należy zwięźle i treściwie dopisać punkt do pliku `CHANGELOG_DRAFT.md`.
2. **Konsolidacja i Brak Duplikatów / Cofnięć**:
   - Jeżeli nowa zmiana poprawia, modyfikuje lub cofa poprzednią tymczasową poprawkę w ramach tego samego cyklu wydania, należy uaktualnić lub scalić istniejący wpis w `CHANGELOG_DRAFT.md` zamiast dodawać powielone czy sprzeczne punkty. Opis ma przedstawiać ostateczny, skonsolidowany efekt zmian.
3. **Kategorie w `CHANGELOG_DRAFT.md`**:
   - Zmiany powinny być ustrukturyzowane i kategoryzowane (np. `⚔️ Ekwipunek & Grafika`, `🏰 Lochy`, `🎮 Mechanika & UX`, `🚀 Launcher & System`).
4. **Automatyczne Czyszczenie przy Publikacji (Release)**:
   - Podczas budowania nowej wersji i publikacji wydania na GitHub, skrypt `upload_release.py` odczytuje treść z `CHANGELOG_DRAFT.md` jako opis wydania, a następnie czyści plik `CHANGELOG_DRAFT.md`, przygotowując go pod kolejną wersję gry.
