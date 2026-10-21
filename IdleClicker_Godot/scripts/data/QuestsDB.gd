class_name QuestsDB

# Baza zadań fabularnych od towarzyszy w Tawernie

const QUESTS: Array = [
	{
		"id": "q_party_maslak",
		"name": "Święty Spokój w Zaroślach",
		"description": "Wataha wilków i bezczelne gobliny zakłócają spokój w leśnych ostępach, niszcząc zapasy słodkości i lukru Maślaka.",
		"unlock_level": 1,
		"npc_id": "maslak",
		"requirements": {"kills": {"Leśny Wilk": 8, "Słaby Goblin": 6}},
		"rewards": {"gold": 300, "item": "wep_maslak", "party": "maslak"},
		"dialog_offer": "*Wypuszcza z fajki aromatyczne kółko o zapachu cynamonu, po czym ostrożnie odkłada nadgryzionego pączka na talerzyk*\n\nNiech słodki spokój będzie z twoją duszą, wędrowcze. Widzę w twoich oczach ten sam niepokój, który dręczy moje serce... Wyobraź sobie: piękny poranek, rosa na mchu, idealnie wysmażone ciasto z lukrem, a tu nagle z krzaków wyskakuje wataha wrzeszczących goblinów i wygłodniałych wilków!\n\nPłoszą mi pszczoły miodne, depczą krzaki poziomek i wywracają kociołki z karmelem! Jak w takich warunkach mnich ma medytować nad sensem wszechświata?!\n\nJeśli zapuścisz się w Złowrogi Las, usuniesz 8 Leśnych Wilków oraz 6 Słabych Goblinów, przywrócisz harmonijne wibracje w kniei. W zamian oddam ci mój rodowy 'Święty Kij Maślaka' – obrobiony żywicą i lukrem, twardszy niż stal – a sam z radością zasilę twoją drużynę!",
		"dialog_accept_reaction": "*Uśmiecha się promiennie i wciska ci w dłoń ciepłego pączka na drogę*\n\nNiech lukier chroni twoją głowę, a spokój prowadzi twoje ciosy! Pamiętaj: wilki atakują watahą, a gobliny boją się głośnych okrzyków. Wracaj w jednym kawałku, bracie!",
		"dialog_complete": "*Uśmiecha się od ucha do ucha i częstuje ciepłym pączkiem*\n\nHa! Wreszcie w lesie zapanował święty spokój! Ptaki śpiewają, pszczoły bzyczą, a karmel stygnie w ciszy. Trzymaj mój stary kij i bierz błogosławieństwo. Od teraz kroczymy razem!"
	},
	{
		"id": "q_party_eczme",
		"name": "Trening Szybkiej Zagrywki",
		"description": "Eczme potrzebuje ruchomych celów o wysokiej zwinności, aby doszlifować swój morderczy serwis z wyskoku. Pająki i bandyci nadadzą się idealnie.",
		"unlock_level": 10,
		"npc_id": "eczme",
		"requirements": {"kills": {"Wielki Pająk": 14, "Bandyta": 12}},
		"rewards": {"gold": 1200, "item": "acc_eczme", "party": "eczme", "garden_plot": 1},
		"dialog_offer": "*Z zawrotną prędkością odbija 5-kilową skórzaną piłkę o kamienny filar, wykonując dynamiczny wyskok i obrót w powietrzu*\n\nOOO! Witaj w klubie, mistrzu! Patrzę na twoją pracę nóg i widzę potencjał, ale brakuje ci zrywu i refleksu przy bloku! Za dwa tygodnie ruszają Mistrzostwa Podziemi w Bojowej Siatkówce, a tutejsze manekiny ze słomy nadają się co najwyżej na podpałkę!\n\nPotrzebuję sparingu z czymś, co nie stoi w miejscu i potrafi zaskoczyć rotacją! Pająki skaczą po ścianach pod dziwnym kątem, a bandyci robią zwody i grają nieczysto – idealny poligon treningowy.\n\nWytrop w podziemiach 14 Wielkich Pająków i 12 Bandytów. Przetestuj na nich szybkie uderzenia z wyskoku, a podaruję ci moje elitarne Owijki 'PowerKeeper' i osobiście dołączę do twojego składu jako ofensywny skrzydłowy!",
		"dialog_accept_reaction": "*Przybija ci tak mocną piątkę, że aż iskry idą z rękawicy*\n\nO TO CHODZI! Dynamika, agresja i czysty sportowy duch! Pamiętaj: trzymaj nisko środek ciężkości, nie daj się zapędzić pająkom w róg i uderzaj z góry! Pokaż im, kto tu rządzi na parkiecie!",
		"dialog_complete": "*Klaszcze z zachwytu i kręci piłką na palcu*\n\nPiękne uderzenie! Masz niesamowity timing na bloku! Bierz te owijki PowerKeeper i lecimy rozgromić lochy w mistrzowskim stylu! (Odblokowano Grządkę #2 w Ogrodzie Ziół!)"
	},
	{
		"id": "q_party_pianek",
		"name": "Rozgrzewka na Czystą Masę",
		"description": "Pianek uważa, że walka z twardymi nieumarłymi żołnierzami i biesami to najlepsze ćwiczenie wielostawowe na potężny rozrost mięśni.",
		"unlock_level": 20,
		"npc_id": "pianek",
		"requirements": {"kills": {"Nieumarły Żołnierz": 16, "Bies": 14}},
		"rewards": {"gold": 3000, "item": "helm_pianek", "party": "pianek", "garden_plot": 2},
		"dialog_offer": "*Robi głębokie przysiady z dwiema dębowymi beczkami pełnymi piwa na barkach, głośno sapiąc i licząc powtórzenia*\n\n...DZIEWIĘĆDZIESIĄT DZIEWIĘĆ... STO! *BUM! Odkłada beczki, aż zatrzęsły się kufle na stołach*\n\nARGH! Siema, młody! Patrzę na twoje barki i widzę, że omijasz dzień nóg i pleców! W tych lochach słabeusze kończą jako przekąska dla szczurów. Żeby przetrwać na głębszych poziomach, musisz pompować czystą, gęstą MASĘ!\n\nNiektórzy mędrcy biegają z pergaminami i rzucają zaklęcia, ale prawdziwa siła pochodzi ze zmiażdżenia wroga gołymi łapami! Nieumarli Żołnierze mają kości gęste jak żeliwo, a Biesy stawiają opór jak sztanga z 250 kilogramami na gryfie!\n\nRozbij 16 Nieumarłych Żołnierzy i zmiażdż 14 Biesów na dobrą rozgrzewkę przed właściwym treningiem. Zrób to, a dostaniesz moją legendarną 'Potową Opaskę Pianka' – przesiąkniętą czystą mocą – i idę z tobą robić formę życia w najgłębszych pieczarach!",
		"dialog_accept_reaction": "*Śmieje się tubalnym głosem i klepie cię po plecach z siłą młota pneumatycznego*\n\nPIĘKNIE! Wypij duszkiem trzy surowe jaja, napnij najszerszy grzbietu i nie opuszczaj gardy! Nieumarłych łam w kolanach, a Biesom nie dawaj złapać oddechu! DO ROBOTY, POMPA SAMA SIĘ NIE ZROBI!",
		"dialog_complete": "*Śmieje się donośnie i napina bicepsy*\n\nDOBRA POMPA! Widzę, że nie pękasz na robocie! Zakładaj tę opaskę, bierz białko i idziemy pakować żelastwo w najgłębszych czeluściach! (Odblokowano Grządkę #3 w Ogrodzie Ziół!)"
	},
	{
		"id": "q_party_damian",
		"name": "Krucjata w Stanie Wskazującym",
		"description": "Damian zauważył, że hordy orków i mściwe zjawy bezczeszczą pradawny trakt rycerski. Czas wymierzyć im honorową sprawiedliwość!",
		"unlock_level": 30,
		"npc_id": "damian",
		"requirements": {"kills": {"Ork Wojownik": 20, "Zjawa": 15}},
		"rewards": {"gold": 6000, "item": "arm_damian", "party": "damian"},
		"dialog_offer": "*Stuka ciężkim kuflem o blat, rozlewając pianę na swój błyszczący, choć mocno opięty na brzuchu napierśnik*\n\nNa święty honor Zakonu Złotej Róży i pamięć wielkich królów! *czka cicho, po czym prostuje się z dumną powagą*\n\nWybacz, szlachetny wędrowcze, tutejszy miód pitny ma moc równą uderzeniu tarana oblężniczego... Lecz choć ciało odpoczywa w gospodzie, serce rycerza rwie się do walki z bezprawiem!\n\nBezczelne hordy zielonoskórych Orków i wyjce ze Zjaw zbezcześciły Królewski Trakt! Napadają na karawany kupieckie, straszą białogłowy i – co najgorsze – kradną beczki z winem transportowane do stolicy!\n\nMój rodowy pancerz co prawda nieco 'skurczył się' w praniu po ostatniej pieczeni z dzika, ale obowiązek rycerski wzywa! Wyrusz na trakt, ukarz mieczem 20 Orków Wojowników i odeślij w zaświaty 15 potępionych Zjaw. Gdy tego dokonasz, odstąpię ci moją rodową płytówkę 'Zbroję Mytnika Damiana' i osobiście dołączę do twojego orszaku jako wierny obrońca wiary i kufla!",
		"dialog_accept_reaction": "*Dopija kufel duszkiem, salutuje ci chwiejnie, lecz z niesamowitym namaszczeniem*\n\nZa honor, męstwo i wieczną chwałę! Na orków bierz szeroki zamach zza ucha, a zjawy atakuj zimną stalą w samo serce, nim rzucą urok mrozu! Niech pieśni o twoich czynach rozbrzmiewają we wszystkich karczmach królestwa!",
		"dialog_complete": "*Ociera łzę wzruszenia z policzka i salutuje dumnie*\n\nZa honor i braterstwo! Trakt znów jest bezpieczny, a kupcy mogą spać spokojnie. Bierz ten pancerz – wyklepany na glanc, a ja zasilam twoje szeregi!"
	},
	{
		"id": "q_party_domcia",
		"name": "Oczyszczenie Czakr z Pnączy",
		"description": "Mroczne Enty i kamienne Gargulce zablokowały dostęp do pradawnych polan z leczniczymi ziołami i świętą Amanitą.",
		"unlock_level": 40,
		"npc_id": "domcia",
		"requirements": {"kills": {"Mroczny Ent": 22, "Gargulec": 18}},
		"rewards": {"gold": 12000, "item": "acc_domcia", "party": "domcia", "garden_plot": 3},
		"dialog_offer": "*Wypuszcza spiralny, fioletowy kłąb dymu z rzeźbionej fajki, wpatrując się w ciebie z mistycznym, łagodnym uśmiechem*\n\nWoooo... Usiądź, przyjacielu. Twoja aura ma barwę płynnego złota, ale wokół nas czuć gęsty, mroczny dysonans kosmiczny...\n\nPradawny las płacze. Z głębi zbutwiałych mokradeł wypełzły Mroczne Enty, oplatając swymi zatrutymi korzeniami polanę Świętej Amanity. Jakby tego było mało, z ruin zleciały się kamienne Gargulce – zimne, bezduszne maszkary, które blokują naturalny przepływ energii rezonansowej w korzeniach wszechświata...\n\nPrzez nie moje ziółka schną, a grzybki tracą swoje trzecie oko. Nie da się stworzyć eliksiru spokoju, gdy drzewa krzyczą z bólu!\n\nIdź do prastarej puszczy, uspokój 22 Mroczne Enty i skrusz 18 kamiennych Gargulców. Przywróć harmonię żywiołów, a podaruję ci mój najcenniejszy 'Mistyczny Naszyjnik Domci' i będę strzec twojego zdrowia oraz czakr w najmroczniejszych zakątkach tego świata.",
		"dialog_accept_reaction": "*Kłania się powoli, przekazując ci szczyptę świecącego pyłku ze suszonych ziół*\n\nCzuj przepływ wiatru w liściach i nie walcz z gniewem w sercu. Płonący ogień kruszy kamień gargulców, a czysta intencja rozrywa mroczne pnącza entów. Pokój z tobą, kosmiczny wędrowcze.",
		"dialog_complete": "*Kłania się z mistycznym uśmiechem i wręcza ci lśniący talizman*\n\nCzujesz to? Natura znowu oddycha. Masz piękną, złotą aurę. Zakładaj ten talizman, od teraz czuwam nad twoim zdrowiem na każdym szlaku. (Odblokowano Grządkę #4 z mistycznym Ziółkiem w Ogrodzie Ziół!)"
	},
	{
		"id": "q_party_yomen",
		"name": "Kanałowy Przegląd Techniczny",
		"description": "Przeklęci Rycerze i potężne Ogry zagnieździły się w podziemiach, blokując Yomenowi dostęp do zapasów rzadkich uszczelek i zębatek.",
		"unlock_level": 50,
		"npc_id": "yomen",
		"requirements": {"kills": {"Przeklęty Rycerz": 25, "Ogr Miażdżyciel": 18}},
		"rewards": {"gold": 25000, "item": "wep_yomen", "party": "yomen"},
		"dialog_offer": "*Z zapałem dokręca mosiężny zawór, wyciera usmarowane olejem dłonie o skórzany fartuch i poprawia potrójne gogle na czole*\n\nSZTO! Siema szefie! Dobrze, że jesteś, bo mam temat grubszego kalibru! *rozgląda się nerwowo, po czym ścisza głos*\n\nNa najniższym poziomie podziemi, tam pod rurami kanalizacyjnymi, odkryłem zapomnianą komorę technologiczną. Stoi tam potężna maszyna ze stali i miedzi z innego wymiaru – cylindry jak dęby, podwójny gaźnik i kompresja, o jakiej ci magowie ze stolicy mogą tylko pomarzyć!\n\nProblem w tym, że te zakute łby w zbrojach – Przeklęci Rycerze – uznały komorę za swoją kaplicę, a gigantyczne Ogry Miażdżyciele używają rur wydechowych jako maczug do łupania orzechów! Uszczelka pod głowicą puszcza, a ja nie mogę podejść ze smarem!\n\nZrób tam porządek: wyeliminuj 25 Przeklętych Rycerzy i rozłup czaszki 18 Ogrom Miażdżycielom. Oczyść maszynownię, a oddam ci mój ulubiony 'Klucz Czternastkę Yomena' – wyważony tak, że jednym ruchem dokręca śrubę, a drugim rozrywa pancerz na strzępy – i trzymamy technologiczną sztamę do końca świata!",
		"dialog_accept_reaction": "*Klaszcze w dłonie z dzikim błyskiem w oku i rzuca ci zapasową puszkę ze smarem*\n\nHA! Wiedziałem, że można na ciebie liczyć! Pamiętaj: w rycerzy celuj w łączenia blach na kolanach, a ogrom nie dawaj zamachnąć się maczugą! Jak wrócisz, odpalamy machinę i ruszamy siać postrach w lochach!",
		"dialog_complete": "*Klaszcze z zachwytu i kręci kluczem w powietrzu*\n\nKompresja powróciła! Wszystkie uszczelki trzymają, a turbina świszczy aż miło! Bierz ten klucz – dokręca śruby i łupie czerepy. Od dziś trzymamy sztamę!"
	}
]

static func get_all_quests_init() -> Array:
	var list: Array = []
	for q in QUESTS:
		var item = q.duplicate(true)
		item["status"] = "LOCKED"
		item["progress"] = {"kills": {}}
		list.append(item)
	return list
