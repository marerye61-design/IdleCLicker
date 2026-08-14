class Quest:
    def __init__(self, quest_id, name, description, requirements, rewards, unlock_level=1, npc_id="innkeeper", dialog_offer="", dialog_accept_reaction="", dialog_complete=""):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.requirements = requirements  # np. {'kills': {'Leśny Wilk': 8, 'Słaby Goblin': 6}}
        self.rewards = rewards  # np. {'gold': 300, 'item': 'wep_maslak', 'party': 'maslak'}
        self.unlock_level = unlock_level
        self.npc_id = npc_id
        self.dialog_offer = dialog_offer
        self.dialog_accept_reaction = dialog_accept_reaction
        self.dialog_complete = dialog_complete
        
        # STATUS: 'LOCKED', 'AVAILABLE', 'IN_PROGRESS', 'COMPLETED', 'CLAIMED'
        self.status = 'LOCKED'
        self.progress = {'kills': {}}

    def update_status(self, player_level):
        if self.status == 'LOCKED' and player_level >= self.unlock_level:
            self.status = 'AVAILABLE'

    def accept(self):
        if self.status == 'AVAILABLE':
            self.status = 'IN_PROGRESS'
            if not hasattr(self, 'progress') or not self.progress:
                self.progress = {'kills': {}}
            return True
        return False

    def check_completion(self, player):
        if self.status != 'IN_PROGRESS':
            return False
        
        prog = getattr(self, 'progress', {}).get('kills', {})
        
        for req, value in self.requirements.items():
            if req == 'clicks' and player.stats.get('total_clicks', 0) < value:
                return False
            if req == 'gold' and player.gold < value:
                return False
            if req == 'level' and getattr(player, 'level', 1) < value:
                return False
            if req == 'kills':
                for monster_name, count in value.items():
                    if prog.get(monster_name, 0) < count:
                        return False
                
        self.status = 'COMPLETED'
        return True

    def complete(self, player):
        """ Ta metoda sprawdza warunki w trakcie gry (w tle) """
        return self.check_completion(player)

    def get_progress_str(self):
        if self.status == 'LOCKED':
            return f"Wymagany {self.unlock_level} poziom bohatera"
        if self.status == 'AVAILABLE':
            return "Zlecenie gotowe do przyjęcia w Tawernie lub Dzienniku"
        if self.status == 'CLAIMED':
            return "✔ Zadanie ukończone i nagroda odebrana"
            
        prog = getattr(self, 'progress', {}).get('kills', {})
        if 'kills' in self.requirements:
            parts = []
            for monster, target in self.requirements['kills'].items():
                cur = prog.get(monster, 0)
                done_marker = "✓" if cur >= target else ""
                parts.append(f"{monster}: {min(cur, target)}/{target} {done_marker}".strip())
            return " | ".join(parts)
            
        if self.status == 'COMPLETED':
            return "Zadanie wykonane! Odbierz nagrodę."
            
        return "W trakcie wykonywania..."

    def claim_reward(self, player):
        if self.status == 'COMPLETED':
            self.status = 'CLAIMED'
            print(f"\n[!] Odebrano nagrodę za: {self.name}!")
            if 'gold' in self.rewards:
                player.gold += self.rewards['gold']
            if 'item' in self.rewards:
                player.add_to_inventory(self.rewards['item'])
            if 'party' in self.rewards:
                member = self.rewards['party']
                if member not in player.party:
                    player.party.append(member)
                if getattr(player, 'active_companion', None) is None:
                    player.active_companion = member
            return True
        return False

    @property
    def is_completed(self):
        return self.status in ['COMPLETED', 'CLAIMED']
    @is_completed.setter
    def is_completed(self, value):
        if value:
            self.status = 'CLAIMED'
        else:
            self.status = 'AVAILABLE'


# Baza zadań fabularnych od NPC w Tawernie (Rozpiętość 1 - 50 Lvl)
QUESTS_DB = [
    Quest(
        "q_party_maslak", 
        "Święty Spokój w Zaroślach", 
        "Wataha wilków i bezczelne gobliny zakłócają spokój w leśnych ostępach, niszcząc zapasy słodkości i lukru Maślaka.", 
        {"kills": {"Leśny Wilk": 8, "Słaby Goblin": 6}}, 
        {"gold": 300, "item": "wep_maslak", "party": "maslak"},
        unlock_level=1,
        npc_id="maslak",
        dialog_offer=(
            "*Wypuszcza z fajki aromatyczne kółko o zapachu cynamonu, po czym ostrożnie odkłada nadgryzionego pączka na talerzyk*\n\n"
            "Niech słodki spokój będzie z twoją duszą, wędrowcze. Widzę w twoich oczach ten sam niepokój, który dręczy moje serce... Wyobraź sobie: piękny poranek, rosa na mchu, idealnie wysmażone ciasto z lukrem, a tu nagle z krzaków wyskakuje wataha wrzeszczących goblinów i wygłodniałych wilków!\n\n"
            "Płoszą mi pszczoły miodne, depczą krzaki poziomek i wywracają kociołki z karmelem! Jak w takich warunkach mnich ma medytować nad sensem wszechświata?!\n\n"
            "Jeśli zapuścisz się w Złowrogi Las, usuniesz 8 Leśnych Wilków oraz 6 Słabych Goblinów, przywrócisz harmonijne wibracje w kniei. W zamian oddam ci mój rodowy 'Święty Kij Maślaka' – obrobiony żywicą i lukrem, twardszy niż stal – a sam z radością zasilę twoją drużynę!"
        ),
        dialog_accept_reaction=(
            "*Uśmiecha się promiennie i wciska ci w dłoń ciepłego pączka na drogę*\n\n"
            "Niech lukier chroni twoją głowę, a spokój prowadzi twoje ciosy! Pamiętaj: wilki atakują watahą, a gobliny boją się głośnych okrzyków. Wracaj w jednym kawałku, bracie!"
        ),
        dialog_complete=(
            "*Uśmiecha się od ucha do ucha i częstuje ciepłym pączkiem*\n\n"
            "Ha! Wreszcie w lesie zapanował święty spokój! Ptaki śpiewają, pszczoły bzyczą, a karmel stygnie w ciszy. Trzymaj mój stary kij i bierz błogosławieństwo. Od teraz kroczymy razem!"
        )
    ),
    Quest(
        "q_party_eczme",
        "Trening Szybkiej Zagrywki",
        "Eczme potrzebuje ruchomych celów o wysokiej zwinności, aby doszlifować swój morderczy serwis z wyskoku. Pająki i bandyci nadadzą się idealnie.",
        {"kills": {"Wielki Pająk": 14, "Bandyta": 12}},
        {"gold": 1200, "item": "acc_eczme", "party": "eczme"},
        unlock_level=10,
        npc_id="eczme",
        dialog_offer=(
            "*Z zawrotną prędkością odbija 5-kilową skórzaną piłkę o kamienny filar, wykonując dynamiczny wyskok i obrót w powietrzu*\n\n"
            "OOO! Witaj w klubie, mistrzu! Patrzę na twoją pracę nóg i widzę potencjał, ale brakuje ci zrywu i refleksu przy bloku! Za dwa tygodnie ruszają Mistrzostwa Podziemi w Bojowej Siatkówce, a tutejsze manekiny ze słomy nadają się co najwyżej na podpałkę!\n\n"
            "Potrzebuję sparingu z czymś, co nie stoi w miejscu i potrafi zaskoczyć rotacją! Pająki skaczą po ścianach pod dziwnym kątem, a bandyci robią zwody i grają nieczysto – idealny poligon treningowy.\n\n"
            "Wytrop w podziemiach 14 Wielkich Pająków i 12 Bandytów. Przetestuj na nich szybkie uderzenia z wyskoku, a podaruję ci moje elitarne Owijki 'PowerKeeper' i osobiście dołączę do twojego składu jako ofensywny skrzydłowy!"
        ),
        dialog_accept_reaction=(
            "*Przybija ci tak mocną piątkę, że aż iskry idą z rękawicy*\n\n"
            "O TO CHODZI! Dynamika, agresja i czysty sportowy duch! Pamiętaj: trzymaj nisko środek ciężkości, nie daj się zapędzić pająkom w róg i uderzaj z góry! Pokaż im, kto tu rządzi na parkiecie!"
        ),
        dialog_complete=(
            "*Klaszcze z zachwytu i kręci piłką na palcu*\n\n"
            "Piękne uderzenie! Masz niesamowity timing na bloku! Bierz te owijki PowerKeeper i lecimy rozgromić lochy w mistrzowskim stylu!"
        )
    ),
    Quest(
        "q_party_pianek",
        "Rozgrzewka na Czystą Masę",
        "Pianek uważa, że walka z twardymi nieumarłymi żołnierzami i biesami to najlepsze ćwiczenie wielostawowe na potężny rozrost mięśni.",
        {"kills": {"Nieumarły Żołnierz": 16, "Bies": 14}},
        {"gold": 3000, "item": "helm_pianek", "party": "pianek"},
        unlock_level=20,
        npc_id="pianek",
        dialog_offer=(
            "*Robi głębokie przysiady z dwiema dębowymi beczkami pełnymi piwa na barkach, głośno sapiąc i licząc powtórzenia*\n\n"
            "...DZIEWIĘĆDZIESIĄT DZIEWIĘĆ... STO! *BUM! Odkłada beczki, aż zatrzęsły się kufle na stołach*\n\n"
            "ARGH! Siema, młody! Patrzę na twoje barki i widzę, że omijasz dzień nóg i pleców! W tych lochach słabeusze kończą jako przekąska dla szczurów. Żeby przetrwać na głębszych poziomach, musisz pompować czystą, gęstą MASĘ!\n\n"
            "Niektórzy mędrcy biegają z pergaminami i rzucają zaklęcia, ale prawdziwa siła pochodzi ze zmiażdżenia wroga gołymi łapami! Nieumarli Żołnierze mają kości gęste jak żeliwo, a Biesy stawiają opór jak sztanga z 250 kilogramami na gryfie!\n\n"
            "Rozbij 16 Nieumarłych Żołnierzy i zmiażdż 14 Biesów na dobrą rozgrzewkę przed właściwym treningiem. Zrób to, a dostaniesz moją legendarną 'Potową Opaskę Pianka' – przesiąkniętą czystą mocą – i idę z tobą robić formę życia w najgłębszych pieczarach!"
        ),
        dialog_accept_reaction=(
            "*Śmieje się tubalnym głosem i klepie cię po plecach z siłą młota pneumatycznego*\n\n"
            "PIĘKNIE! Wypij duszkiem trzy surowe jaja, napnij najszerszy grzbietu i nie opuszczaj gardy! Nieumarłych łam w kolanach, a Biesom nie dawaj złapać oddechu! DO ROBOTY, POMPA SAMA SIĘ NIE ZROBI!"
        ),
        dialog_complete=(
            "*Śmieje się donośnie i napina bicepsy*\n\n"
            "DOBRA POMPA! Widzę, że nie pękasz na robocie! Zakładaj tę opaskę, bierz białko i idziemy pakować żelastwo w najgłębszych czeluściach!"
        )
    ),
    Quest(
        "q_party_damian", 
        "Krucjata w Stanie Wskazującym", 
        "Damian zauważył, że hordy orków i mściwe zjawy bezczeszczą pradawny trakt rycerski. Czas wymierzyć im honorową sprawiedliwość!", 
        {"kills": {"Ork Wojownik": 20, "Zjawa": 15}}, 
        {"gold": 6000, "item": "arm_damian", "party": "damian"},
        unlock_level=30,
        npc_id="damian",
        dialog_offer=(
            "*Stuka ciężkim kuflem o blat, rozlewając pianę na swój błyszczący, choć mocno opięty na brzuchu napierśnik*\n\n"
            "Na święty honor Zakonu Złotej Róży i pamięć wielkich królów! *czka cicho, po czym prostuje się z dumną powagą*\n\n"
            "Wybacz, szlachetny wędrowcze, tutejszy miód pitny ma moc równą uderzeniu tarana oblężniczego... Lecz choć ciało odpoczywa w gospodzie, serce rycerza rwie się do walki z bezprawiem!\n\n"
            "Bezczelne hordy zielonoskórych Orków i wyjce ze Zjaw zbezcześciły Królewski Trakt! Napadają na karawany kupieckie, straszą białogłowy i – co najgorsze – kradną beczki z winem transportowane do stolicy!\n\n"
            "Mój rodowy pancerz co prawda nieco 'skurczył się' w praniu po ostatniej pieczeni z dzika, ale obowiązek rycerski wzywa! Wyrusz na trakt, ukarz mieczem 20 Orków Wojowników i odeślij w zaświaty 15 potępionych Zjaw. Gdy tego dokonasz, odstąpię ci moją rodową płytówkę 'Zbroję Mytnika Damiana' i osobiście dołączę do twojego orszaku jako wierny obrońca wiary i kufla!"
        ),
        dialog_accept_reaction=(
            "*Dopija kufel duszkiem, salutuje ci chwiejnie, lecz z niesamowitym namaszczeniem*\n\n"
            "Za honor, męstwo i wieczną chwałę! Na orków bierz szeroki zamach zza ucha, a zjawy atakuj zimną stalą w samo serce, nim rzucą urok mrozu! Niech pieśni o twoich czynach rozbrzmiewają we wszystkich karczmach królestwa!"
        ),
        dialog_complete=(
            "*Ociera łzę wzruszenia z policzka i salutuje dumnie*\n\n"
            "Za honor i braterstwo! Trakt znów jest bezpieczny, a kupcy mogą spać spokojnie. Bierz ten pancerz – wyklepany na glanc, a ja zasilam twoje szeregi!"
        )
    ),
    Quest(
        "q_party_domcia",
        "Oczyszczenie Czakr z Pnączy",
        "Mroczne Enty i kamienne Gargulce zablokowały dostęp do pradawnych polan z leczniczymi ziołami i świętą Amanitą.",
        {"kills": {"Mroczny Ent": 22, "Gargulec": 18}},
        {"gold": 12000, "item": "acc_domcia", "party": "domcia"},
        unlock_level=40,
        npc_id="domcia",
        dialog_offer=(
            "*Wypuszcza spiralny, fioletowy kłąb dymu z rzeźbionej fajki, wpatrując się w ciebie z mistycznym, łagodnym uśmiechem*\n\n"
            "Woooo... Usiądź, przyjacielu. Twoja aura ma barwę płynnego złota, ale wokół nas czuć gęsty, mroczny dysonans kosmiczny...\n\n"
            "Pradawny las płacze. Z głębi zbutwiałych mokradeł wypełzły Mroczne Enty, oplatając swymi zatrutymi korzeniami polanę Świętej Amanity. Jakby tego było mało, z ruin zleciały się kamienne Gargulce – zimne, bezduszne maszkary, które blokują naturalny przepływ energii rezonansowej w korzeniach wszechświata...\n\n"
            "Przez nie moje ziółka schną, a grzybki tracą swoje trzecie oko. Nie da się stworzyć eliksiru spokoju, gdy drzewa krzyczą z bólu!\n\n"
            "Idź do prastarej puszczy, uspokój 22 Mroczne Enty i skrusz 18 kamiennych Gargulców. Przywróć harmonię żywiołów, a podaruję ci mój najcenniejszy 'Mistyczny Naszyjnik Domci' i będę strzec twojego zdrowia oraz czakr w najmroczniejszych zakątkach tego świata."
        ),
        dialog_accept_reaction=(
            "*Kłania się powoli, przekazując ci szczyptę świecącego pyłku ze suszonych ziół*\n\n"
            "Czuj przepływ wiatru w liściach i nie walcz z gniewem w sercu. Płonący ogień kruszy kamień gargulców, a czysta intencja rozrywa mroczne pnącza entów. Pokój z tobą, kosmiczny wędrowcze."
        ),
        dialog_complete=(
            "*Kłania się z mistycznym uśmiechem i wręcza ci lśniący talizman*\n\n"
            "Czujesz to? Natura znowu oddycha. Masz piękną, złotą aurę. Zakładaj ten talizman, od teraz czuwam nad twoim zdrowiem na każdym szlaku."
        )
    ),
    Quest(
        "q_party_yomen",
        "Kanałowy Przegląd Techniczny",
        "Przeklęci Rycerze i potężne Ogry zagnieździły się w podziemiach, blokując Yomenowi dostęp do zapasów rzadkich uszczelek i zębatek.",
        {"kills": {"Przeklęty Rycerz": 25, "Ogr Miażdżyciel": 18}},
        {"gold": 25000, "item": "wep_yomen", "party": "yomen"},
        unlock_level=50,
        npc_id="yomen",
        dialog_offer=(
            "*Z zapałem dokręca mosiężny zawór, wyciera usmarowane olejem dłonie o skórzany fartuch i poprawia potrójne gogle na czole*\n\n"
            "SZTO! Siema szefie! Dobrze, że jesteś, bo mam temat grubszego kalibru! *rozgląda się nerwowo, po czym ścisza głos*\n\n"
            "Na najniższym poziomie podziemi, tam pod rurami kanalizacyjnymi, odkryłem zapomnianą komorę technologiczną. Stoi tam potężna maszyna ze stali i miedzi z innego wymiaru – cylindry jak dęby, podwójny gaźnik i kompresja, o jakiej ci magowie ze stolicy mogą tylko pomarzyć!\n\n"
            "Problem w tym, że te zakute łby w zbrojach – Przeklęci Rycerze – uznały komorę za swoją kaplicę, a gigantyczne Ogry Miażdżyciele używają rur wydechowych jako maczug do łupania orzechów! Uszczelka pod głowicą puszcza, a ja nie mogę podejść ze smarem!\n\n"
            "Zrób tam porządek: wyeliminuj 25 Przeklętych Rycerzy i rozłup czaszki 18 Ogrom Miażdżycielom. Oczyść maszynownię, a oddam ci mój ulubiony 'Klucz Czternastkę Yomena' – wyważony tak, że jednym ruchem dokręca śrubę, a drugim rozrywa pancerz na strzępy – i trzymamy technologiczną sztamę do końca świata!"
        ),
        dialog_accept_reaction=(
            "*Klaszcze w dłonie z dzikim błyskiem w oku i rzuca ci zapasową puszkę ze smarem*\n\n"
            "HA! Wiedziałem, że można na ciebie liczyć! Pamiętaj: w rycerzy celuj w łączenia blach na kolanach, a ogrom nie dawaj zamachnąć się maczugą! Jak wrócisz, odpalamy machinę i ruszamy siać postrach w lochach!"
        ),
        dialog_complete=(
            "*Klaszcze z zachwytu i kręci kluczem w powietrzu*\n\n"
            "Kompresja powróciła! Wszystkie uszczelki trzymają, a turbina świszczy aż miło! Bierz ten klucz – dokręca śruby i łupie czerepy. Od dziś trzymamy sztamę!"
        )
    ),
]

def get_all_quests():
    import copy
    return copy.deepcopy(QUESTS_DB)

