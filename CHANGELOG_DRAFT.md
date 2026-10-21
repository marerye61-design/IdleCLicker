# Szkic Zmian dla Nadchodzącej Wersji (Prace w toku)

### 📜 Tawerna & Tablica Ogłoszeń
- **Poprawka krytyczna (Crash Fix)**: Naprawiono błąd `AttributeError` uniemożliwiający odbiór nagród z Tablicy Ogłoszeń, gdy nagrodą rzeczową była mikstura zdrowia (usunięto nieistniejącą metodę `item.to_dict()`).
- **Codzienne wyzwania i dziennik nagród**: Dodano trzy odnawiane codziennie cele oraz historię 100 ostatnich nagród z walk, lochów, zadań, zleceń i innych źródeł złota.
- **Jednokrotna rejestracja nagród questów**: Usunięto błąd podwójnego zapisywania wpisu w historii nagród i dziennych wyzwaniach przy odbiorze zadań oferujących jednocześnie złoto i przedmiot. Dodano pełną obsługę nagród doświadczenia (EXP) w zadaniach fabularnych.

### ⚔️ Ekwipunek & Przedmioty
- **Zachowanie unikalnych cech i krytyka rynsztunku**: Naprawiono błąd w konstruktorze `Equipment`, który nadpisywał unikalne statystyki bazowe ze wzoru skalowania. Wszystkie bronie (np. Klucz Yomena, Ognisty Topór, Mroźne Ostrze, Ostrze Nieskończoności) w pełni zachowują swoje wbudowane szanse na krytyk (`crit_chance`) i punkty życia (`hp_max`), a pancerze bonusy do ataku (`atk`).
- **Aktywacja prefiksów i sufiksów przedmiotów**: Naprawiono błąd obliczania statystyk gracza (`get_total_atk`, `get_total_def`, `get_total_crit`, `get_max_hp`), w którym odrzucano modyfikatory założonych przedmiotów. Wszystkie prefiksy (np. "Ostry", "Mityczny", "Solidny", "Boski") teraz poprawnie wpływają na obrażenia, pancerz, krytyk i HP.
- **Bonus Drużynowy dla Domci**: Dodano brakujący wpis w `get_party_bonus()` dla Domci (+10 ATK, +35 HP skalowane z poziomem gracza), dzięki czemu wszyscy 6 kompanów zapewnia unikalne statystyki bojowe oraz w pełni korzysta ze stałego perku `perk_party_synergy`.
- **Sortowanie plecaka**: Dodano sortowanie ekwipunku według nazwy A–Z/Z–A z zapamiętaniem wybranego kierunku.
- **Wielokrotne zaznaczanie i hurtowa sprzedaż z CTRL (Multi-Item Bulk Sell)**: Wprowadzono możliwość jednoczesnego zaznaczania wielu przedmiotów w plecaku poprzez przytrzymanie klawisza CTRL. Zaznaczone sloty zyskują pulsującą, rozżarzoną ramkę ze złotym znacznikiem wyboru (`✓`). Panel boczny sumuje łączną wartość skupu wybranych przedmiotów i pozwala na ich błyskawiczną, jednoczesną sprzedaż jednym kliknięciem (`Sprzedaj wszystko (+X zł)`). Dodano także przycisk szybkiego zaznaczania zwykłego złomu (`Zaznacz zwykłe`) oraz czyszczenia zaznaczenia.
- **Złote Ramki Pixel-Art dla Wszystkich Przedmiotów i Sklepów (Global Item Framing)**: Dodano jednolite, zdobne złote ramki pixel-art z charakterystycznymi narożnymi klamrami i ciemnym tłem `#0c0a10` (znane z wyposażenia adamantowego) do każdego przedmiotu w całej grze – we wszystkich sklepach, plecaku, kuźni oraz łupach z potworów. Zunifikowano komplet 48 ikon przedmiotów:
  - Rynsztunek Nowicjusza/Drewniany (Drewniana Pałka, Skórzana Zbroja, Skórzany Hełm, Mały Pierścień).
  - Rynsztunek Żelazny (Żelazny Miecz, Żelazna Zbroja, Żelazny Hełm, Żelazny Pierścień).
  - Rynsztunek Stalowy (Stalowy Miecz, Stalowa Płyta, Stalowy Hełm, Srebrny Amulet) – usunięto stare, niepasujące obramowania runiczne i okrągłe winiety, izolując czyste sylwetki pancerza i oręża.
  - Rynsztunek Mithrilowy (Mithrilowe Ostrze, Mithrilowa Kolczuga, Mithrilowy Hełm, Rubinowy Wisiorek) z pełnym wycentrowaniem i korektą proporcji.
  - Ekwipunek i relikwie towarzyszy (Damian, Pianek, Eczme, Domcia, Yomen, Maślak).
  - Mikstury i eliksiry (Mikstura Zdrowia, Many, Psychodeliczny Eliksir) – zlikwidowano archaiczne brązowe ramki, wyśrodkowano flakony i nadano im przejrzyste tło.
  - Magiczne klejnoty (Ametyst, Szmaragd, Rubin, Szafir, Topaz) oraz składniki z potworów (Rdzeń, Ektoplazma, Kieł, Jad).
  - Zioła z ogrodu (Amanita, Krwawy Kwiat, Srebrzysty Mech, Mistyczne Ziółko, Korzeń).
  Wszystkie grafiki zostały wycentrowane, znormalizowane do formatu 160×160 RGB, zsynchronizowane 1:1 w repozytoriach gry oraz zaktualizowane w pamięci podręcznej tekstur silnika Godot 4 (`.ctex`).

### 🔮 Magiczne Klejnoty & Kuźnia
- **Uruchomienie Podwójnego Ciosu z Szafirów**: Naprawiono martwy kod w silniku walki – szansa na Podwójny Cios (`get_double_strike_chance`) z wprawionych Szafirów oraz Wywaru Szybkich Stóp jest teraz w pełni uwzględniana w turze walki gracza.
- **Działanie Topazów (Złoto i Drop)**: Dodano uwzględnianie bonusu do złota (`bonus_gold_pct`) i dropu (`bonus_loot_pct`) z wprawionych Topazów w nagrodach z potworów oraz lochów.

### 🧪 Alchemia & Ogród
- **Progresja Ogrodu Ziół i Stopniowe Odblokowywanie**: Zioła i ogród nie są już odblokowane od samego początku. Grządki oraz Kociołek Alchemiczny rozpoczynają grę zablokowane i wymagają rozwoju postaci.
- **Płatna Dzierżawa Grządki u Karczmarza Barnaby**: Grządka #1 (Amanita Lasu) jest odblokowywana w Tawernie poprzez nową opcję dialogową u Karczmarza Barnaby za opłatą 150 złota, użyczającego skrawka ziemi przed karczmą.
- **Odblokowywanie Grządek z Zadań Fabularnych**: Kolejne grządki odblokowują się stopniowo z poziomem jako nagrody za zadania kompanów: Grządka #2 (Srebrzysty Mech) po zadaniu Eczmego (Poz. 10+), Grządka #3 (Krwawy Kwiat) po zadaniu Pianka (Poz. 20+), a Grządka #4 (Mistyczne Ziółko) po zadaniu Domci (Poz. 40+).
- **Interfejs Zablokowanych Grządek i Wygaszonego Kociołka**: W widoku Ogrodu zablokowane grządki posiadają czytelny stan kłódki wraz z podpowiedzią wymagań i przyciskami szybkiego przejścia do Tawerny/Zadań. Kociołek Alchemiczny informuje gracza o konieczności wydzierżawienia pierwszej grządki.
- **Synchronizacja opisów eliksirów z mechaniką walki**: Zaktualizowano opisy i wartości receptur w Kociołku Alchemicznym, aby idealnie odpowiadały rzeczywistym wzmocnieniom (+35% ATK dla Berserkera, +35% DEF dla Kamiennej Skóry, +15% podwójnego ciosu dla Wywaru Szybkości oraz +50% kryta dla Wywaru z Ziółka).
- **Masowe warzenie w Kociołku (Bulk Brew)**: Dodano możliwość jednoczesnego uwarzenia wszystkich dostępnych porcji eliksiru ("Wszystkie") na podstawie posiadanych ziół i trofeów, oszczędzając czas gracza.
- **Korekta Perku Dotyk Alchemika**: Skorygowano mechanikę stałego perku `perk_alchemist_touch` do właściwej 15% szansy na podwójny plon ziół z grządek ogrodu.
- **Działanie Naparu Złotego Rogu**: Aktywowano premię +40% do złota z eliksiru `elixir_fortune` podczas walk i nagród z lochów.
- **Bezpieczeństwo Ziółka**: Zabezpieczono pętlę animacji psychodelicznej (`start_psychedelic_trip`) przed wielokrotnym nakładaniem się timerów Tkintera przy szybkim wielokrotnym zażyciu ziółek.

### 🏘️ Rynek & Synergia Towarzyszy
- **Więź Kompanów z Budowlami Miasta**: Każdy budynek pasywny w rynku zyskał synergię z odpowiadającym mu towarzyszem (Cukiernia ➔ Maślak, Strażnica ➔ Damian, Plantacja ➔ Domcia, Boisko ➔ Eczme, Siłownia ➔ Pianek, Warsztat ➔ Yomen).
- **Mnożniki produkcji złota**: Posiadanie towarzysza w drużynie zwiększa przychód z jego budowli o **+25%**, a wybranie go jako aktywnego kompana zwiększa przychód łącznie o **+40%**. W sklepie budynków dodano czytelne etykiety synergii.

### 🎮 Mechanika & Balans
- **Rozwój Postaci w Ołtarzu Bohaterów**:
  - Dodano możliwość inwestowania punktów rozwoju w **Maksymalne Zdrowie** (+10 HP za punkt).
  - Wprowadzono przyciski szybkiego rozdawania punktów (`+1`, `+5`, `+10`), ułatwiające rozwój na wyższych poziomach.
- **Aktywacja stałych perków konta**:
  - `perk_exp_master`: +5% do całego zdobywanego doświadczenia (EXP) ze wszystkich źródeł (walka, zadania, zlecenia, lochy).
  - `perk_greed`: +10% więcej złota ze wszystkich źródeł (walka, lochy, kliknięcia, pasywne budynki).
  - `perk_boss_hunter`: +5% złota i EXP za pokonanie bossów w lochach.
- **Spójne liczenie złota i EXP**: Historia nagród, wyzwania i osiągnięcie bogactwa uwzględniają walki, lochy, kliknięcia, przychód pasywny, zadania, zlecenia, sprzedaż i nagrody za osiągnięcia. Bonus łupu nie zwiększa EXP.
- **Perk Chciwości ze wszystkich nagród**: +10% złota obejmuje także zadania, zlecenia, sprzedaż, osiągnięcia i wyzwania; formuły walki/lochów nie naliczają go drugi raz.
- **Nagrody lochowe i eliksiry**: Eliksir szczęścia działa do końca całej walki z bossem, wliczając dodatkową nagrodę za ukończony loch.
- **Zabezpieczenie Pancerza w Walce**: Formuła redukcji obrażeń potworów (`calculate_enemy_dmg`) zabezpiecza `p_def >= 0`, zapobiegając ujemnym współczynnikom redukcji.

### 🚀 Optymalizacja & Stabilność
- **Aktualizacja wersji zapisu w migracji**: Metoda `Player.migrate()` podnosi wersję zapisu do "1.1", eliminując uciążliwe ponowne monity o stary zapis przy każdym kolejnym ładowaniu gry.
- **Bezpieczne przewijanie w ScrollableFrame**: Dodano zabezpieczenia `winfo_exists` i bezpieczne usuwanie obsługi kółka myszy, zapobiegając awariom przy niszczeniu widżetów i konfliktom między oknami.
- **Atomowy zapis gry (Crash-Proof Saves)**: Zapis stanu gry w `save_game()` odbywa się teraz w sposób atomowy poprzez plik tymczasowy (`.tmp` + `os.replace`), zabezpieczając gracza przed uszkodzeniem pliku zapisu w razie nagłego wyłączenia gry.
- **Odzyskiwanie zapisów**: Przed podmianą zapisu tworzona jest kopia `.bak`; przy błędzie odczytu gra oferuje jej przywrócenie. Nowe ustawienia i liczniki są migrowane dla starszych postaci.
- **Optymalizacja bufora logów**: Ograniczono historię `log_text` w panelu głównym do ostatnich 400 wpisów, eliminując spadki FPS i alokację pamięci podczas długich sesji gry.
- **Płynność animacji bossów**: Wprowadzono pamięć podręczną (cache kątowy) obróconych klatek grafik maczugi Ptysia i kuli ognia Kollmana, eliminując narzut obracania obrazów przez Pillow w każdej klatce 60 FPS.
- **Limit pamięci animacji**: Cache klatek bossów przechowuje maksymalnie 24 ostatnie kąty.
- **Wydzielenie formuł nagród**: Obliczenia nagród walk i lochów przeniesiono do `reward_math.py`, oddzielając je od logiki widoków.
- **Zamknięcie deskryptorów plików grafik**: Zoptymalizowano `load_portraits` i `load_item_icons` za pomocą menedżera kontekstu `with Image.open(...)`, zapobiegając wyciekom uchwytów plików w systemie Windows.

### 🔊 Dźwięki & Audio
- **Wyciszenie dźwięków GUI**: Zgodnie z preferencjami gracza wyłączono wszystkie piszczące i natarczywe dźwięki interfejsu (kliknięcia UI, monety, awanse, mikstury, wejścia do lochów). W grze aktywne pozostały wyłącznie realistyczne efekty cięć i ciosów w trakcie pojedynków (`sword_swing`, `hit`, `crit_hit`, `enemy_hit`).

### 🤖 Port Godot 4 & Poprawki Systemowe
- **Naprawa Sklepu Fantasy i Tawerny**: Skorygowano wywołania właściwości stylów motywów na metody Godot 4 (`add_theme_constant_override`, `add_theme_font_size_override`), co przywróciło pełną widoczność asortymentu w Sklepie Fantasy (`ShopView`) oraz wyeliminowało błędy renderowania w Tawernie (`TavernView`).
- **Karty Towarzyszy i Dialogi Lore**: Zreorganizowano karty kompanów w Tawernie, wprowadzając estetyczne miniatury portretów oraz czytelne etykiety (`[Gospodarz]`, `[W drużynie]`, `[Poz. X]`). Przywrócono pełną interakcję z Barnabą oraz towarzyszami wraz z wszystkimi tematami rozmów.
- **Odświeżanie Przeciwników (30s Cooldown)**: Wprowadzono przycisk odświeżania listy wrogów na szlaku z dynamicznym odliczaniem co sekundę (`Odśwież Przeciwników (30s)`), blokujący nadużywanie tasowania.
- **Powiadomienia o Łupach w Walce**: Pokonanie potworów wyświetla teraz powiadomienia na górnym pasku HUD oraz kolorowe pływające napisy informujące o wszystkich zdobytych trofeach (składniki alchemiczne, magiczne klejnoty, mikstury pełnego zdrowia).
- **Cutscenka Bossów (Giga Ork Ptyś & Kollman)**: Wprowadzono nastrojową, dwufazową cutscenkę maszynopisową (`BossCinematic`) z klimatyczną narracją i cytatami bossów, a także dedykowane animacje ataku (miażdżąca maczuga Ptysia `ptys_mace.png` oraz wirująca kula ognia Kollmana `kollman_fireball.png`).
- **Dzierżawa Grządki #1 u Barnaby**: Utrwalono status dzierżawy `garden_plot_0_leased`, gwarantując, że pierwsza grządka ogrodu ziół pozostaje zablokowana do momentu jej oficjalnego wykupienia u Karczmarza za 150 sztuk złota.
- **Obsługa Porażki w Walce i Regeneracja w Karczmie (Death & Tavern Recovery)**: Usunięto błąd, w którym po utracie całego zdrowia gracz otrzymywał sztuczne 1 HP i mógł dalej walczyć, co przy każdym ciosie potwora w nieskończoność wywoływało komunikat "Zostałeś pokonany". Teraz śmiertelny cios poprawnie zeruje punkty życia (0 HP), natychmiast blokuje przyciski walki, zdolności i auto-walkę, a po krótkiej animacji (1.4s) automatycznie przenosi bohatera do Karczmy Barnaby. W karczmie gospodarz udziela pierwszej pomocy, a przebywanie w bezpiecznej gospodzie aktywuje darmową, pasywną regenerację zdrowia (+8% Max HP/s przy kominku) obok opcji natychmiastowego pełnego odpoczynku za 20 złota.
- **Automatyczny Tester Systemowy na Żywo (Live E2E Test Suite na Ekranie 3)**: Wdrożono autonomiczny moduł testowy (`AutomatedLiveTester.tscn`), który uruchamia pełną grę w oknie na 3. monitorze, wyświetla dynamiczny pasek postępu testu i krok po kroku automatycznie testuje wszystkie 14 systemów gry (HUD, walka, śmierć i ewakuacja do karczmy, regeneracja przy kominku, towarzysze, ołtarz talentów, ekwipunek, alchemia, rynek, sklep, kuźnia, lochy, zapis gry oraz menu główne). Wyniki są na bieżąco zapisywane do pliku `test_e2e_results.log`. Przy okazji wykryto i naprawiono brakującą metodę `Player.click()` oraz błąd formatowania tekstu w `StatsView`.
- **Menu Główne & Wybór Zapisu (Main Menu & Multi-Profile Saves)**: Zaimplementowano dedykowaną scenę startową (`MainMenu.tscn` oraz `MainMenu.gd`) w klimatycznej oprawie dark fantasy (`menu_bg.jpg`, złote liternictwo, ciemne drewniane panele). Rozbudowano `SaveSystem.gd` o pełną obsługę wielu niezależnych profili graczy (`user://saves/<nazwa>.json`), dynamiczną listę zapisów z podglądem imienia, poziomu, złota i daty modyfikacji, tworzenie nowej postaci, usuwanie zapisu z oknem potwierdzenia oraz przycisk powrotu do Menu Głównego w bocznym panelu nawigacji. Zapewniono 100% bezpieczeństwa danych poprzez automatyczną migrację starszego pliku `user://savegame.json` do nowego katalogu profili.
- **Klimatyczny Interfejs Dark Fantasy & Mikro-reakcje Kuźni (Forge Pixel-Art Dark Fantasy UI)**: Całkowity redesign interfejsu gry na motyw ciemnego kutego żelaza, palonego drewna i rozżarzonego kowadła kuźni (`Ma objąć całą ramę gry`). Stworzono proceduralny shader 2D (`forge_flame.gdshader`) generujący pikselowy żar i buchające języki ognia w tle kafelków, emitter unoszących się iskier (`EmberSparks.tscn`) oraz system sprężystych mikro-interakcji (`ForgeUIEffects.gd`). Wszystkie kafelki, przyciski nawigacji, karty talentów i panele reagują na najechanie kursora dynamicznym powiększeniem (1.04-1.06x), rozbłyskiem żaru kutego złota i wzmożoną intensywnością płomieni, a kliknięcia mają satysfakcjonujące uderzenie młota kowalskiego. Przebudowano górny pasek TopHUD (kute paski rubinowego HP, szafirowej many i złotego EXP z płynną interpolacją Tween), boczny panel nawigacji z nitami i aktywnym żarem wybranej zakładki oraz Ołtarz Bohaterów i Drzewko Talentów (`StatsView`) z ozdobnymi ramami portretu, runicznymi przyciskami inwestycji i ognistymi kafelkami specjalizacji.

### 🎮 Ustawienia & UX
- **Konfiguracja gry**: Dodano ustawiany autosave (30/60/120 s) i tryb ograniczonych animacji; ustawienia są zachowywane w zapisie gracza.
- **Instrukcje dla asystentów**: Skrócono `INSTRUCTIONS_FOR_CODEX.md` do ściągi wskazującej dokumenty źródłowe, by ograniczyć rozbieżności zasad.

### 💀 Elitarne Potwory & Afiksy
- **Rzadkie warianty elitarne**: Potwory spotykane podczas standardowych ekspedycji mają teraz 20% szansy na wylosowanie wariantu elitarnego z unikalnym afiksem, czerwoną ramką oraz banerem statusu.
- **Unikalne cechy afiksów**:
  - `Płonący` (+35% ATK, ogniste wykończenie).
  - `Pancerny` (+50% DEF, gruba powłoka obronna).
  - `Złocisty Złodziej` (+150% łupu złota po pokonaniu).
  - `Pradawny` (+60% HP, zwiększona wytrzymałość).
- **Zwiększone nagrody**: Pokonanie elitarnego wroga zapewnia podwojone doświadczenie (+100% EXP) oraz +80% więcej złota.
- **Normalizacja pętli walki po elicie**: Po pokonaniu potwora elitarnego kolejna walka w pętli (`loop_combat`) automatycznie generuje standardowego przeciwnika (bez afiksów i premii statystyk), zapobiegając niekończącemu się zapętleniu na elicie.
- **30-sekundowy cooldown odświeżania przeciwników**: Wprowadzono 30-sekundowy czas odnowienia na ręczne odświeżanie listy przeciwników w widoku Wypraw, wzbogacony o dynamiczny licznik sekund na przycisku.
- **Pełne oczyszczenie interfejsu i potworów z emotek**: Usunięto emotki ze wszystkich elementów gry (nazwy potworów, przyciski nawigacji, nagłówki, dymki obrażeń, karty zadań, tablica zleceń, sklep i kuźnia), eliminując zniekształcone glify na silniku graficznym Windows i przywracając spójną, mroczną stylistykę dark fantasy.

### ⚔️ Interaktywna Walka & Umiejętności Towarzyszy
- **Naprawa Pętli Walki i Odświeżania Zdrowia (Combat Loop Fix)**: Naprawiono błąd `TypeError` w wywołaniach `get_talent_bonus()`, który zatrzymywał pętlę walki po pierwszym uderzeniu gracza (blokując aktualizację pasków zdrowia oraz uniemożliwiając potworom kontratak). Wprowadzono pełną obsługę wywołań 1- i 2-argumentowych dla wszystkich ścieżek (kradzież życia, unik, kolce, regeneracja).
- **Separacja Pływających Napisów Bojowych (Anti-Overlap Floating Texts)**: Wdrożono dynamiczny system korygowania pozycji pionowej napisów bojowych zapobiegający ich nakładaniu się na siebie przy jednoczesnych trafieniach, pancerzu, unikach czy kradzieży życia. Dodano wyraźny cień kontrastowy pod każdym tekstem bojowym dla doskonałej czytelności.
- **Bezpieczne Rozwijanie Talentów (Buy Talent Fix)**: Zabezpieczono okno statystyk przed błędem `TypeError` przy inwestowaniu punktów w ścieżki talentów, obsługując poprawnie rezultaty transakcji.
- **Klik bojowy (Combat Click)**: Podczas walki gracz może aktywnie klikać w portret przeciwnika, zadając dodatkowe obrażenia zależne od ataku bazowego gracza i poziomu, co znacząco przyspiesza starcia dla zaangażowanych graczy.
- **Zdolności ostateczne towarzyszy (Companion Ultimates) dopasowane do ich lore**: Aktywny w drużynie towarzysz wnosi do walki własną potężną umiejętność ściśle odzwierciedlającą jego charakter, historię i styl bycia:
  - **Eczme**: *Ścina Przeznaczenia* (220% ATK + 1 tura Ogłuszenia wroga uderzeniem ciężkiej Skórzanej Kuli Przeznaczenia w twarz przeciwnika).
  - **Pianek**: *Napięcie Bicepsa* (180% ATK ciśniętym kowadłem + stalowa bariera ochronna z napiętych muskułów na 30% Max HP).
  - **Domcia**: *Fioletowy Horyzont* (30% leczenia Max HP + gęsty dym z zarodników Amanity i ziół, przez który wróg "słyszy kolory" i traci turę na pudło).
  - **Damian**: *Rycerski Toast* (200% ATK potężnego ciosu po opróżnieniu kufla mocnego ale + 20% tarczy Niezłomnej Zbroi).
  - **Maślak**: *Lukrowany Pączek* (Częstuje bohatera słodkim wypiekiem przywracającym 35% Max HP oraz podrzuca dodatkowe złoto prosto ze skrytki).
  - **Yomen**: *Rzut Czternastką* (Szczurzy alchemik ciska zardzewiałym kluczem z olejem silnikowym za potężne 260% ATK z gwarantowanym trafieniem krytycznym).

### 🌳 Drzewko Talentów & Specjalizacje Bohatera
- **Punkty Talentów**: Postać otrzymuje 1 punkt talentu co 5 poziomów doświadczenia (np. poz. 5, 10, 15...). Gracze ze starszych zapisów gry otrzymują zaległe punkty w migracji.
- **Trzy ścieżki specjalizacji w Ołtarzu Bohaterów**:
  - **Ścieżka Berserkera**: Kradzież życia z ciosów (+4%), potężne wzmocnienie obrażeń krytycznych (+25%) oraz Ostatni Bastion (+35% ataku gdy HP spada poniżej 50%).
  - **Ścieżka Obrońcy**: Pancerz Cierni odbijający 12% obrażeń we wroga, Hart Ciała regenerujący 3% Max HP co rundę oraz Twierdza Nieugięta aktywująca barierę ochronną w wysokości 25% Max HP na początku walki.
  - **Ścieżka Łotrzyka**: Zwinność Kota dająca 6% szansy na całkowity unik ataku wroga, Sokoli Wzrok (+8% szansy na podwójny cios) oraz Chciwe Palce (+30% złota i szansy na rzadki łup).

### 🗺️ Wyprawy Towarzyszy (Idle Companion Expeditions)
- **Ekspedycje zwiadowcze w Tawernie**: Nowy system w Tawernie pozwalający na wysyłanie wolnych towarzyszy (niebędących aktualnie w 1-osobowej aktywnej drużynie) na samodzielne misje zwiadowcze.
- **Trzy poziomy trudności wypraw**:
  - *Zwiady w Zaroślach* (5 minut): Złoto i rzadkie zioła do alchemii (Amanita, Srebrzysty Mech, Krwawy Kwiat).
  - *Stara Kopalnia* (15 minut): Złoto i szlachetne klejnoty do kuźni (Rubiny, Szafiry, Topazy).
  - *Zapomniane Katakumby* (30 minut): Duże złoża złota, mikstury oraz szansa na mistyczne składniki i klejnoty.
- **Śledzenie w czasie rzeczywistym**: Okno wypraw na żywo odlicza czas do powrotu drużyny, a przycisk w Tawernie dynamicznie informuje o zakończonych ekspedycjach oczekujących na odbiór nagród.

### 🎮 Silnik Godot 4 (Pełna Konwersja Projektu)
- **Autonomiczny port gry w silniku Godot 4**: Stworzono kompletną, natywną implementację gry IdleClicker w Godot 4 (`IdleClicker_Godot`) z zachowaniem 100% spójności mechanik, balansu i lore oryginalnego kodu Python.
- **Modułowa architektura GDScript**:
  - `Player.gd` – rdzenny model postaci obsługujący statystyki, awans, ekwipunek, 80-slotowy plecak, synergie towarzyszy, drzewko talentów oraz bezpieczną migrację zapisów.
  - `ItemsDB.gd` & `GemsDB.gd` – pełna baza sprzętu (T1–T5, legendarne nagrody kompanów >=2x mocniejsze od sklepowych, rynsztunek lochów 45–100) i magicznych klejnotów ze skalowaniem statystyk.
  - `EnemiesDB.gd` & `CombatMath.gd` – walka interaktywna, losowanie afiksów elitarnych (20%), lochy 1–8 z dedykowanymi bossami (Ptyś, Kollman, Morgar, Ignis, Kryształowy Kolos, Kel-Thuzar, Awatar Upadłego Bóstwa, Cesarz Czasoprzestrzeni).
  - `CombatView` – arena starć z animowanymi, kontrastowymi napisami obrażeń (FloatingDamageText), paskami HP, automatyczną walką i resetem elitarnego wroga po zwycięstwie w pętli.
  - `TavernView` – autentyczne dialogi NPC, zadania rekrutacyjne, wyprawy czasowe oraz zlecenia z tablicy ogłoszeń.
  - `AlchemyView` – 4 grządki w ogrodzie ziół z dynamicznym wzrostem oraz kociołek z 6 recepturami eliksirów.
  - `MarketView` – rynek budynków z pasywnym dochodem i mnożnikami synergii towarzyszy (+25% / +40%).
  - `BlacksmithView` – mistrzowska kuźnia kowala z ulepszeniami (+1 do +9), wykuwaniem gniazd i wprawianiem klejnotów.
  - `AchievementsView` – księga osiągnięć z trwałymi perkami konta.
  - `SoundManager.gd` – natywna obsługa puli dźwięków (cięcia mieczem, uderzenia, trafienia krytyczne, mikstury, monety, awans, lochy, bossowie).
  - `SaveSystem.gd` – serializacja stanu gry w formacie JSON (`user://savegame.json`).
- **Sklep Fantasy z Ekwipunkiem (Tiers 0–6)**: Dodano pełny Sklep Fantasy z podziałem na 7 poziomów asortymentu (Alchemik ze skalowanymi miksturami oraz zestawy: Nowicjusza, Żelazny, Stalowy, Mithrilowy, Adamantowy i Boski), z dynamiczną weryfikacją poziomu gracza, kosztu w złocie oraz pojemności plecaka.
- **Konsola Debugowania i Cheaty (F12 / ~)**: Zaimplementowano okno konsoli debugowania (`DebugConsole`) dostępne pod skrótem klawiszowym `F12`, tyldą `~` oraz przyciskiem nawigacyjnym "DEBUG KONSOLA". Umożliwia natychmiastowe testy: dodawanie złota (+10k / +1M), poziomów (+1 / +10), pełne leczenie HP i Many, +50 punktów rozwoju, przyznawanie kompletu klejnotów, broni z gniazdami, składników alchemii, natychmiastowe dojrzewanie ziół w ogrodzie, bezpośrednie uruchamianie walk z bossami (Ptyś, Kollman, Morgar) oraz ukończenie osiągnięć.
- **Rozdział Punktów Rozwoju (Stat Points)**: W widoku postaci (`StatsView`) dodano panel inwestowania punktów rozwoju (+3 za każdy poziom) w Atak (+1), Pancerz (+1), Zdrowie (+10), Szansę na Krytyk (+1%, limit 30%) oraz Szansę na Łup (+1%, limit 50%) z przyciskami szybkiego rozdawania `+1` i `+5`.
- **Naprawa Poziomów Wymaganych w Tawernie**: Usunięto błąd domknięcia zmiennej w pętli GDScript, przez który wybór towarzysza wskazywał błędne wymagania poziomu (np. poziom 50 zamiast 10). Karty postaci otrzymały czytelne etykiety wymaganych poziomów ("Poz. 1", "Poz. 10", "Poz. 20", itd.).
- **Karczmarz Barnaba i Interaktywne Dialogi NPC**: Tawerna została wzbogacona o gospodarza Barnabę oraz interaktywny system dialogów dla wszystkich 6 kompanów. Gracz może zadawać pytania fabularne o przeszłość, świat i sekrety bohaterów z natychmiastowymi odpowiedziami w oknie rozmowy, odpocząć w gospodzie (pełne leczenie za 20 złota) oraz odebrać zdeponowane nagrody, gdy plecak był pełny.
- **Wyciszenie piskliwych dźwięków interfejsu (GUI Clicks)**: Całkowicie wyłączono odtwarzanie wysokotonowego dźwięku kliknięć `ui_click` przy nawigacji po menu, przyciskach, kartach oraz plecaku (zarówno w porcie Godot 4, jak i bazie Python), zachowując pełne udźwiękowienie akcji bojowych, ciosów, mikstur, lochów i złota.
- **Gwarancja jakości i testy**: Zbudowano i pomyślnie zweryfikowano pakiet testów jednostkowych `test/TestRunner.gd` (oraz scenę `test/TestRunner.tscn`) w trybie headless, potwierdzając 100% zgodności reguł rozgrywki bez błędów kompilacji.
- **Portret Bohatera i Awatar HUD**: Przywrócono wyświetlanie portretu bohatera (`res://assets/portraits/hero.jpg`) w arenie walki (`CombatView`) oraz wprowadzono stylizowaną ramę awatara w lewym górnym rogu paska HUD (`TopHUD` w `Main.tscn`), z dynamicznym fallbackiem ładującym teksturę.
- **Statyczny Panel Rozmowy w Tawernie**: Wyeliminowano niepożądany efekt podskakiwania, pulsowania i powiększania kafelka "Rozmowa i Towarzysze" przy najechaniu myszą – panel został przekształcony w statyczny `DetailPanel`, a w `ForgeUIEffects.gd` dodano filtr zabezpieczający okna dialogowe i panele informacyjne przed przypisywaniem efektów kart.
- **Responsywny Pasek HUD i Pływający Toast Notyfikacji**: Rozwiązano problem deformacji i rozciągania górnego interfejsu gry w trybie okienkowym (np. po przyjęciu zadania rekrutacji lub długich wiadomościach). Etykietę komunikatów przeniesiono z paska `HUDHBox` do niezależnego, animowanego powiadomienia `NotificationToast` na górze ekranu. Dodano responsywny system dynamicznie dostosowujący szerokość pasków, marginesy i formatowanie tekstu w oknach <1180px oraz <980px/pionowych.
- **Korekta Grządki #2 w Ogrodzie Ziół**: Usunięto błąd przedwczesnego odblokowywania Grządki #2 (Srebrzysty Mech) przed zwerbowaniem Eczmego. W metodzie `migrate()` w `Player.gd` oraz w silniku Python dodano ścisłą walidację blokującą grządki towarzyszy, dopóki gracz nie odblokuje danego kompana lub nie odbierze jego zadania rekrutacyjnego (`q_party_eczme`).
- **Responsywna Konsola Debugowania (ScrollContainer)**: Zabezpieczono okno `DebugConsole` (F12) przed obcinaniem zawartości w trybie okienkowym i mniejszych rozdzielczościach poprzez dodanie kontenera przewijania `ConsoleScroll`, gwarantując pełną dostępność wszystkich cheatów i przycisków testowych.
- **Pełna Adaptacja Gry do Orientacji Pionowej (Portrait Mode & Mobile UX dla Androida)**:
  - Wdrożono natywną orientację pionową (baza 720×1280 z trybem skalowania `expand`, orientacją sensor portrait oraz desktopowym podglądem 450×800) i skonfigurowano preset eksportu Androida (`screen/orientation=5`), gwarantując wygodną i ergonomiczną rozgrywkę jedną ręką na smartfonach.
  - **Ergonomiczny Dolny Pasek Nawigacji (`BottomNav`)**: W orientacji pionowej boczny pasek nawigacji (215px) jest automatycznie ukrywany, a na dole ekranu pojawia się dotykowy, przewijany pasek `BottomNav` z 12 szybkimi skrótami (Walka, Lochy, Postać, Plecak, Tawerna, Alchemia, Rynek, Sklep, Kuźnia, Księga, Zapisz, Menu) ze sprężystymi mikro-reakcjami, dzięki czemu aktywny ekran gry zyskuje 100% pełnej szerokości wyświetlacza.
  - **Dwurzędowy Pasek Statusu (`TopHUD`)**: W trybie pionowym górny pasek płynnie reorganizuje się w dwa czytelne rzędy (Rząd 1: awatar, poziom, stan złota i przycisk zysku; Rząd 2: paski i wartości HP, Many, EXP oraz towarzysz), zapobiegając stłoczeniu elementów.
  - **Responsywna Arena Walki (`CombatView`)**: W trybie pionowym panele Gracza i Przeciwnika zajmują górny rząd obok siebie (po 50% szerokości ekranu ze zoptymalizowanymi portretami 96×96), log walki wykorzystuje pełną wysokość środkowej sekcji, a przyciski bojowe (Atakuj, Zdolność, Mikstura, Auto-Walka) tworzą dużą, wygodną pod kciuk siatkę 2×2.
  - **Pojemny Plecak Mobilny (`InventoryView`)**: W trybie pionowym siatka ekwipunku automatycznie przełącza się z 10 na 5 kolumn z dużymi celami dotykowymi, założony rynsztunek przyjmuje postać kompaktowej poziomej wstęgi 4 slotów, a panel szczegółów przedmiotu dopasowuje się do dołu ekranu.
  - **Mobilne Zakładki Pełnoekranowe (`StatsView` & `AlchemyView`)**: Panele dzielone na pół (Parametry Bohatera / Drzewo Talentów oraz Ogród Ziół / Kociołek Alchemiczny) otrzymały w trybie pionowym szybkie przełączniki zakładek, pozwalając na wykorzystanie pełnej szerokości ekranu telefonu na każdy z modułów.
  - **Nowe Wydanie Android APK (`build/IdleClicker.apk`)**: Zbudowano i pomyślnie podpisano kluczem debugowym zaktualizowaną paczkę instalacyjną Androida (44.2 MB) z pełną weryfikacją schematów podpisów v2 i v3 (`apksigner`).

### 🏰 Lochy & Bossowie
- **Rebalans Statystyk Bossów i Czasu Walki (TTK)**: Gruntownie przeliczono i podniesiono statystyki bossów, aby wyeliminować problem błyskawicznego padania w kilka sekund. Giga Ork Ptyś zyskał 2075 HP (wzrost z 725 HP) oraz 52 ATK, a Arcymag Kollman 6550 HP (wzrost z 2175 HP) oraz 140 ATK. Przeskalowano również parametry bossów ze wszystkich 8 lochów (do 1.25M HP i 28k ATK dla Cesarza Czasoprzestrzeni), zapewniając emocjonujące, wieloturowe pojedynki.
- **Dedykowane Portrety Bossów w Walce**: Naprawiono błąd w silniku walki i konsoli debugowania (F12), przez który bossowie nie posiadali własnych grafik i wyświetlali portret głównego bohatera. Zoptymalizowano wyszukiwanie portretów w `EnemiesDB` oraz zsynchronizowano pliki graficzne (`boss_ptys.jpg`, `boss_kollman.jpg`) we wszystkich katalogach gry.

### 🎮 Mechanika & Balans (Wczesna Gra & Gracz)
- **Korekta Początkowych Statystyk Bohatera**: Zmniejszono sztucznie zawyżone statystyki startowe (ze 120 HP / 12 ATK / 10 DEF do 85 HP / 8 ATK / 4 DEF), a pasywny przyrost na poziom skorygowano do +1.2 ATK, +0.6 DEF i +6 Max HP (inwestycja w zdrowie daje teraz +8 HP na punkt). Zbalansowano początkowe szablony przeciwników (np. Goblin 34 HP / 7 ATK, Wilk 42 HP / 10 ATK, Bandyta 52 HP / 14 ATK), eliminując trywialne zabijanie potworów jednym ciosem na 1. poziomie.
- **Bezpieczna Migracja Postaci**: Metoda `migrate()` w `Player` (Godot oraz Python) inteligentnie normalizuje świeże profile 1. poziomu oraz bezpiecznie przelicza zainwestowane punkty rozwoju.

### 🌳 Drzewko Talentów (Balans Progresji)
- **Odblokowanie Punktów Talentu od Poziomu 10**: Punkty talentu są teraz przyznawane począwszy od poziomu 10 (co 5 poziomów: 10, 15, 20...), zamiast zbyt wczesnego poziomu 5. Daje to graczowi czas na zapoznanie się z podstawowym ekwipunkiem, sklepem i mechanikami gry przed wejściem w zaawansowane specjalizacje bojowe. Migracja zapisów precyzyjnie przelicza punkty `(level - 5) // 5`, dbając o zachowanie uczciwej progresji starszych postaci.


