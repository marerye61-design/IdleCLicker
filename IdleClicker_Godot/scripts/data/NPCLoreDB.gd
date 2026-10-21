class_name NPCLoreDB

# Baza danych lore i dialogów NPC w Tawernie (dokładny port npc_lore.py)

const NPCS: Dictionary = {
	"innkeeper": {
		"name": "Karczmarz Barnaba",
		"role": "Gospodarz Tawerny 'Pod Skrzydłem Upadłego Anioła'",
		"img": "res://assets/portraits/innkeeper.jpg",
		"unlock_level": 1,
		"quest_id": "",
		"greeting": "*Wyciera kufel lnianą ścierką i spogląda na ciebie zza lady z ciepłym uśmiechem*\n\nWitaj, wędrowcze, w gospodzie 'Pod Skrzydłem Upadłego Anioła'! Co ci podać? Zimne piwo, ciepłą strawę, czy może szukasz sprawdzonych wieści ze świata?",
		"options": {
			"Kim jesteś, gospodarzu?": "Zowią mnie Barnaba. Prowadzę ten przybytek od ponad trzydziestu lat. Widziałem królów tracących korony i żebraków stających się legendami. Ta tawerna stoi na skrzyżowaniu pradawnych szlaków – dla każdego, kto ma dość walki i szuka bezpiecznego dachu nad głową, moje drzwi stoją otworem. O ile oczywiście nie wszczyna burd przy stole!",
			"Co słychać w okolicy? (Plotki i Wieści)": "Dzikie bestie w Złowrogim Lesie stają się coraz bardziej zuchwałe. Wilki podchodzą pod sam trakt, a z głębi puszczy dochodzi ryk Giga Orka Ptyśka... Jeśli planujesz zapuszczać się do lochów, upewnij się, że masz przy sobie zapas mikstur i solidnie okuty pancerz. Pamiętaj też, że kowal w mieście potrafi zdziałać cuda z każdym kawałkiem żelastwa!",
			"Opowiedz mi o swoich gościach.": "Ach, moja wesoła kompania! *śmieje się cicho* Maślak przesiaduje w kącie z fajką i pączkami, Damian po piątym kuflu przysięga zbawić świat, Pianek bije rekordy w podnoszeniu beczek, Yomen ciągle majstruje przy rurach w piwnicy, Eczme trenuje ściny na korytarzu, a Domcia leczy skołatane nerwy ziółkami. Każdy z nich ma swoje dziwactwa, ale w walce możesz na nich polegać bez wahania!",
			"Jak działa depozyt na nagrody?": "To proste! Jeśli twój plecak będzie w pełni zapełniony (wszystkie 80 slotów), żadna nagroda ze zleceń, zadań czy lochów nie przepadnie. Zostanie bezpiecznie zdeponowana u mnie za ladą. Gdy tylko zwolnisz miejsce, możesz do mnie podejść i odebrać swoje skarby!",
			"Czy masz skrawek ziemi pod uprawę ziół?": "Owszem! Za gospodą mam mały kawałek żyznej ziemi, który chętnie ci wydzierżawię za jedyne 150 sztuk złota. Możesz tam siać Amanitę Lasu i zbierać cenne plony do kociołka alchemicznego!"
		}
	},
	"maslak": {
		"name": "Maślak",
		"role": "Słodki Mnich & Mistyk Cukiernictwa",
		"img": "res://assets/portraits/maslak.jpg",
		"unlock_level": 1,
		"quest_id": "q_party_maslak",
		"passive_name": "Słodki Łup",
		"passive_desc": "+10 ATK, +20 HP. Lukrowany Pączek leczy 35% Max HP i daje dodatkowe złoto.",
		"greeting": "*Wypuszcza gęsty obłok dymu i uśmiecha się szeroko*\n\nPokój z tobą, wędrowcze! Skusisz się na lukrowanego pączka? A może wolisz zimnego Namysłowa?",
		"options": {
			"Witaj, kim jesteś?": "Zwą mnie Maślak. Kiedyś byłem pokornym bratem w Klasztorze Surowej Ascezy, ale... cóż, ich dieta składająca się z czerstwego chleba i wody jakoś mi nie podpasowała. Zrozumiałem, że prawdziwe oświecenie można znaleźć tylko w pysznych słodkościach, wybornym piwie i chwili relaksu z nabitą fajką. Zostałem więc wędrownym kapłanem dobrego humoru i pełnego brzucha!",
			"Opowiedz mi swoją historię.": "Jak się tu znalazłem? *pociąga łyk z butelki* To dość zabawna historia! Wędrowałem przez Mroczne Ziemie, szukając mitycznej 'Wielkiej Cukierni'. W końcu zgubiłem się w lesie pełnym wygłodniałych goblinów. Zamiast z nimi walczyć, usiadłem na pniu, wyciągnąłem moje wypieki i rozdałem im trochę 'magicznego ziółka' z klasztornego ogrodu. Gobliny były tak wniebowzięte, że nie tylko mnie nie zjadły, ale jeszcze same eskortowały mnie bezpiecznie do bram tej Tawerny! Kiedy karczmarz spróbował moich pączków i napoczął pierwszą beczkę Namysłowa, z miejsca zaproponował mi darmowy wikt i opierunek.",
			"Co to za miejsce?": "Ta tawerna to moje małe, przytulne sanktuarium pośrodku całego tego chaosu! Choć na zewnątrz czają się demony i szkielety, u nas zawsze znajdziesz gorący kominek, górę cukierków i litry zacnego piwa. Rozsiądź się, zrelaksuj i poczęstuj żelkami!"
		}
	},
	"eczme": {
		"name": "Eczme",
		"role": "Siatkarz Lochów & Mistrz Zagrywki",
		"img": "res://assets/portraits/eczme.jpg",
		"unlock_level": 10,
		"quest_id": "q_party_eczme",
		"passive_name": "Serwis z Wyskoku",
		"passive_desc": "+20 ATK, +25% DMG w 1. turze. Ścina Przeznaczenia (220% ATK + ogłuszenie na 1 turę).",
		"greeting": "Odbicie, wystawa, i... ŚCINA! Hej, uważaj z tą zbroją, żebyś nie przebił mi piłki!",
		"options": {
			"Witaj, kim jesteś?": "Nazywam się Eczme! Jestem kapitanem i zarazem jedynym ocalałym członkiem drużyny 'Mroczne Kolce'. Wszyscy myślą, że w lochach trzeba machać mieczem. Bzdura! Wystarczy odpowiednio mocno zaserwować skórzaną piłką prosto w twarz nekromanty. Złote medale? Ja wolę zdobywać skrzynie ze złotem!",
			"Opowiedz mi swoją historię.": "Pochodzę ze starożytnego Zakonu Szybkiej Piłki. Trenowaliśmy latami, odbijając pociski z katapult, żeby wyrobić sobie refleks. Kiedy nasz klasztor najechały trolle, mój serw z wyskoku uratował całą bibliotekę. Zrozumiałem wtedy, że mój talent marnuje się na dziedzińcu. Zszedłem do lochów! Tutejsze gobliny grają bardzo nieczysto, często gryzą w kostki przy bloku, ale hej, sport to zdrowie! Karczmarz pozwala mi tu mieszkać w zamian za to, że organizuję awanturnikom mecze siatkówki po godzinach.",
			"Ta piłka?": "To Skórzana Kula Przeznaczenia. Waży 5 kilo, jest wypchana trocinami i runami ochronnymi. Jak dostaniesz nią z plaska, to odechciewa ci się rzucać uroków. Idealna broń dystansowa na każdego bossa."
		}
	},
	"pianek": {
		"name": "Pianek",
		"role": "Pancerny Czołg & Król Pakowania",
		"img": "res://assets/portraits/pianek.jpg",
		"unlock_level": 20,
		"quest_id": "q_party_pianek",
		"passive_name": "Żelazna Pompa",
		"passive_desc": "+25 DEF, +60 HP, +25% DEF gdy HP < 60%. Napięcie Bicepsa daje tarczę 30% Max HP.",
		"greeting": "ARGH! *Głośno stęka, podnosząc beczkę pełną piwa jednym palcem* Cześć! Masz może... ten, no... trochę białka?",
		"options": {
			"Witaj, kim jesteś?": "Ja jestem Pianek. Najsilniejszy wojownik w całej wsi! Wszyscy mówili: 'Pianek, czytaj zwoje magii, ucz się'. Ale po co? Zwojem nie zgnieciesz łba goblinowi! Moja magia to moje bicepsy! Rozdałem wszystkie swoje punkty umiejętności w siłę. WSZYSTKIE. Może i nie umiem doliczyć do dziesięciu bez używania palców, ale za to potrafię rzucić niedźwiedziem na odległość trzystu kroków!",
			"Opowiedz mi swoją historię.": "Historia? Urodziłem się, poszedłem na siłownię i już stamtąd nie wyszedłem. Kiedyś przyszedł do mnie taki chuderlawy elf z długą brodą, machał patykiem i krzyczał zaklęcia. Powiedziałem: 'Elf, zostaw patyk, weź hantle'. Rzucił we mnie kulą ognia, to ja rzuciłem w niego kowadłem. Zgadnij, co zadziałało lepiej? Od tamtej pory podróżuję i szukam godnych przeciwników. Słyszałem, że w lochach mają dobre odżywki, dlatego tu jestem.",
			"Twoja broń?": "Ten topór? W sumie to nawet nie jest naostrzony. Nie musi być. Używam go bardziej jak gigantycznego młotka. Wiesz, co jest najlepsze w posiadaniu takiej siły? Nikt nie pyta cię o zdanie. Nikt nie każe ci myśleć. Mniej myślenia to mniej zmarszczek, bracie!"
		}
	},
	"damian": {
		"name": "Damian",
		"role": "Rycerz Cnoty & Mytnik po Godzinach",
		"img": "res://assets/portraits/damian.jpg",
		"unlock_level": 30,
		"quest_id": "q_party_damian",
		"passive_name": "Niezłomna Tarcza",
		"passive_desc": "+15 DEF, +40 HP, stała redukcja obrażeń o 10%. Rycerski Toast daje tarczę 20% Max HP.",
		"greeting": "*hic* Na honor i... polejcie mi jeszcze jeden kufel! Witajże, zacny wędrowcze!",
		"options": {
			"Witaj, kim jesteś?": "Zowią mnie Damian. Kiedyś byłem dumą Zakonu Złotej Róży. Ślubowałem bronić słabszych, tępić zło i zachować czystość ducha... Ale prawda jest taka, że to wszystko strasznie wysusza gardło. A rycerz bez zwilżonego gardła, to jak miecz bez klingi, prawda?",
			"Opowiedz mi swoją historię.": "Moja historia? *beka cicho* Ach, wybacz. Kiedyś prowadziłem krucjaty. Mój pancerz błyszczał tak mocno, że gobliny same ślepły od patrzenia. Mówili, że mam niezłomne zasady... i wciąż je mam! Nigdy nie uderzę nieuzbrojonego, nigdy nie zdradzę kompana i nigdy, absolutnie nigdy nie odmawiam darmowego kufla mocnego ale. Z czasem zauważyłem, że w karczmach można spotkać o wiele więcej zła do wyplenienia niż w zimnych lochach. I dlatego tu przesiaduję. Oczywiście, pancerz zrobił się ostatnio jakoś dziwnie ciaśniejszy w pasie... to pewnie ta magiczna wilgoć w tawernie sprawia, że stal się kurczy.",
			"Co robisz w tawernie?": "Ja? Ja tu pełnię wartę! Ktoś musi pilnować, żeby te wszystkie rzezimieszki zachowywały się kulturalnie. A że przy okazji karczmarz robi tu najlepsze pieczone prosię w okolicy... *klepie się po brzuchu* Cóż, trzeba dbać o zapasy energii na krucjaty!"
		}
	},
	"domcia": {
		"name": "Domcia",
		"role": "Wiedźma Ziół & Szamanka Natury",
		"img": "res://assets/portraits/domcia.jpg",
		"unlock_level": 40,
		"quest_id": "q_party_domcia",
		"passive_name": "Mistyczna Prędkość",
		"passive_desc": "+10 ATK, +35 HP. Fioletowy Horyzont leczy 30% Max HP i oślepia wroga na 1 turę.",
		"greeting": "Wooo, stary... Ale masz aurę. Złocista, jak poranny wschód. Usiądź, zapal z nami i poczuj wibracje lasu.",
		"options": {
			"Witaj, kim jesteś?": "Zowią mnie Domcia. Jestem... niezależnym badaczem świadomości. I botanikiem. Kiedy inni wojownicy machają żelastwem i krzyczą na potwory, ja szukam z nimi porozumienia na wyższym poziomie egzystencji. Głównie dzięki moim wyjątkowym grzybkom i specjalnym mieszankom ziół. Chcesz spróbować 'Fioletowego Horyzontu'? Rozluźnia napięte mięśnie i otwiera trzecie oko. Albo i czwarte, zależy ile spalisz.",
			"Opowiedz mi swoją historię.": "Stary, to była długa podróż. Kiedyś mieszkałem w stolicy. Hałas, pośpiech, strażnicy czepiający się o zbieranie dziwnego mchu... Koszmar, negatywne wibracje. Pewnego dnia wziąłem swój kociołek i po prostu poszedłem przed siebie do puszczy. Trafiłem na magiczną polanę pełną Amanity. Usiadłem, zacząłem suszyć, testować i mieszać. Zrozumiałem wtedy, że drogie mikstury od tych nadętych alchemików z gildii to straszna ściema. Moje organiczne ekstrakty nie tylko leczą punkty życia, ale pokazują ci, gdzie to życie tak naprawdę ma swoje źródło we wszechświecie. Wprowadziłem się do tej tawerny, założyłem w kącie swój gabinet 'Wital-Punkt' i puszczam dymka.",
			"Co robisz w tawernie?": "Rozjaśniam umysły, stary. Przesiaduję tu, puszczam kółka z dymu i obserwuję przepływ energii awanturników. Jak ktoś wróci z lochu cały w siniakach, to daję mu ciepły wywar z muchomora i ziół. Po pięciu minutach przestaje czuć ból w nogach, a za to zaczyna słyszeć kolory. Najlepsze naturalne lekarstwo, wierz mi."
		}
	},
	"yomen": {
		"name": "Yomen",
		"role": "Szczurzy Inżynier & Alchemik Ścieków",
		"img": "res://assets/portraits/yomen.jpg",
		"unlock_level": 50,
		"quest_id": "q_party_yomen",
		"passive_name": "Złota Rączka",
		"passive_desc": "+15 ATK, +10 DEF, -15% kosztu kucia u Kowala. Rzut Czternastką zadaje 260% ATK gwarantowanym krytykiem.",
		"greeting": "Siema mordeczki! Wbiłem przez okienko w piwnicy. Ma ktoś klucz czternastkę albo trochę uszczelniacza do chłodnic?",
		"options": {
			"Witaj, kim jesteś?": "Zowią mnie Yomen! Jestem mistrzem eliksirów, koneserem kanałów i niezaproszonym gościem na każdym spotkaniu w tej karczmie. Nieważne jak dobrze zamkniecie drzwi, i tak wejdę. Moja specjalność to mieszanie rzadkich ziół z olejem silnikowym.",
			"Opowiedz mi swoją historię.": "Siedziałem latami w mrocznych kanałach wielkiego miasta, warząc eliksiry w zardzewiałych beczkach. Zrozumiałem, że zwykli alchemicy to frajerzy – próbują ratować ludzi. Ja zacząłem ratować wspaniałe bestie. Kiedyś w ściekach znalazłem zapomnianą maszynę, relikt z innego wymiaru, zwaną potocznie 'BeeMWe'. Przysięgam na bogów chaosu, że uszczelniłem w niej każdy wyciek z pomocą wywaru z trupich czaszek i pajęczyn! Szukałem nowych części, więc zawędrowałem tu do tawerny. Nie zaprosili mnie, ale przecież nie odmawia się szczurzemu alchemikowi dostępu do darmowego piwa!",
			"Wybuchy?": "To nie wybuchy, to tylko 'wypadanie zapłonu' na jednym cylindrze! Nie przejmuj się. Dodam trochę proszku z rogu jednorożca do baku i zaraz odzyska kompresję."
		}
	}
}
