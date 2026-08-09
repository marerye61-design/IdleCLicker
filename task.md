# Implementacja Nowych Mechanik i UI

- [/] **Krok 1: Poprawki UI (Suwak Paska Bocznego)**
  - [ ] Owinięcie 
av_frame w Pasku Bocznym (main.py) w ScrollableFrame.

- [ ] **Krok 2: Bestiariusz (Kolekcjoner Dusz)**
  - [ ] Dodanie licznika zabójstw w player.py (np. self.bestiary = {'enemy_id': count}).
  - [ ] Inkrementacja licznika przy end_combat(won=True).
  - [ ] Stworzenie nowej zakładki show_bestiary() z listą odkrytych potworów i nagrodami (pasywny bonus).
  - [ ] Dodanie uwzględniania bonusów z bestiariusza w walkach.

- [ ] **Krok 3: Kowalstwo i Refaktoryzacja Ekwipunku**
  - [ ] Zmiana struktury zapisu przedmiotów w inventory i equipment na wsparcie poziomów ulepszeń (migracja save'ów).
  - [ ] Zaktualizowanie player.py do poprawnego czytania zmodyfikowanych statystyk sprzętu (+1, +2...).
  - [ ] Stworzenie widoku Kowala (show_blacksmith()) w Tawernie.
  - [ ] Kalibracja Balansu: Ceny ulepszeń muszą rosnąć z każdym poziomem potęgując zapotrzebowanie na złoto, a przeciwnicy z wyższych poziomów będą mieli zwiększone HP by ulepszanie było konieczne.
