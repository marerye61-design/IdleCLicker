import random

# Podmioty w liczbie POJEDYNCZEJ
singular_subjects = ["Twoja grupa", "Drużyna", "Ekipa", "Zgraja śmiałków", "Wyprawa"]

# Czynności w liczbie POJEDYNCZEJ (65 czynności)
singular_actions = [
    # Z wcześniejszej puli (15)
    "ostrożnie przemierza mroczne korytarze",
    "natrafia na starożytne runy wyryte w skale",
    "unika ukrytej pułapki z trucizną",
    "odpoczywa przez chwilę przy małym ognisku",
    "walczy z rojem małych, irytujących insektów",
    "nasłuchuje dziwnych pisków z głębi jaskini",
    "przeszukuje stary, porzucony plecak",
    "znajduje dziwną, świecącą w ciemności roślinę",
    "próbuje rozszyfrować mapę narysowaną krwią",
    "cicho przekrada się obok śpiącego potwora",
    "zauważa w oddali migoczące światło",
    "omija głęboką przepaść po starym moście",
    "odpiera nagły atak nietoperzy",
    "podziwia podziemny wodospad",
    "kieruje się w stronę podejrzanego hałasu",
    # Nowe 50
    "ślizga się na mokrym mchu porastającym skały",
    "przemyka obok uśpionego stada nietoperzy",
    "stara się odczytać wyblakłe ostrzeżenie na ścianie",
    "wyczuwa dziwny zapach siarki w powietrzu",
    "znajduje porzucony miecz wbity w czaszkę",
    "ignoruje dziwne szepty dochodzące ze szczelin",
    "potyka się o stertę pradawnych kości",
    "zapala nową pochodnię, by oświetlić gęsty mrok",
    "przygląda się dziwnym posągom z dziurami zamiast oczu",
    "wyciąga mapę i z zakłopotaniem drapie się w głowę",
    "omija na palcach śpiącego potwora z mackami",
    "węszy powietrze, czując woń spalenizny",
    "rozgarnia gęste pajęczyny bronią",
    "chowa się za skałą przed dziwnym, zielonym światłem",
    "gubi na chwilę kierunek w labiryncie",
    "zatrzymuje się, słysząc kroki w sąsiednim tunelu",
    "odnajduje stary, na wpół spalony dziennik",
    "podziwia kryształy wyrastające ze ścian",
    "wzdryga się na dźwięk upadającej kropli wody",
    "kopie mały kamyczek prosto w rzekę lawy",
    "próbuje nie obudzić pobliskich pająków",
    "wciąga głęboko zatęchłe powietrze z lochu",
    "wypatruje ukrytych przejść za zasłonami z grzybów",
    "walczy z chmarą irytujących, świecących robaków",
    "czyści zbroje z grubej warstwy pachu i pyłu",
    "skacze przez szeroką kałużę z nieznaną substancją",
    "z trudem przeciska się przez wąską szczelinę w ścianie",
    "unika ciosu wystrzelonej ze ściany strzały",
    "przeciera oczy, nie wierząc w ogrom podziemi",
    "bada podejrzanie wyglądającą skrzynię",
    "gasi płomień pochodni, widząc w oddali orków",
    "ostrożnie rozgląda się na wszystkie strony",
    "czuje lodowaty powiew wiatru na karku",
    "ściska mocniej broń, szykując się na kłopoty",
    "narzeka na słabe oświetlenie w jaskini",
    "podnosi z ziemi stary, wyblakły proporzec",
    "stąpa bardzo ostrożnie, by nie wywołać lawiny",
    "rzuca mały kamyk w głąb ciemnej studni",
    "obserwuje spadającą w otchłań pochodnię",
    "podziwia stalaktyty wiszące nad wielką przepaścią",
    "cicho szepcze, słysząc ryk potwora w oddali",
    "unosi sprzęt wyżej, gotowa na niespodziewany atak",
    "w pośpiechu szuka jakiejkolwiek ukrytej drogi ucieczki",
    "potyka się, łapiąc z trudem równowagę nad przepaścią",
    "zasłania uszy przed piskami potężnych stworzeń",
    "bada strukturę dziwnego, niebieskiego śluzu na ziemi",
    "pije wodę z podziemnego, krystalicznego źródła",
    "znajduje ślady ogromnych pazurów na kamiennej ścianie",
    "drapie się w głowę patrząc na zamknięte, wielkie wrota",
    "rozstawia małe, prowizoryczne obozowisko dla bezpieczeństwa"
]

# Podmioty w liczbie MNOGIEJ
plural_subjects = ["Bohaterowie", "Członkowie drużyny", "Kompani", "Poszukiwacze przygód", "Śmiałkowie"]

# Czynności w liczbie MNOGIEJ (65 czynności)
plural_actions = [
    # Z wcześniejszej puli (15)
    "ostrożnie przemierzają mroczne korytarze",
    "natrafiają na starożytne runy wyryte w skale",
    "unikają ukrytej pułapki z trucizną",
    "odpoczywają przez chwilę przy małym ognisku",
    "walczą z rojem małych, irytujących insektów",
    "nasłuchują dziwnych pisków z głębi jaskini",
    "przeszukują stary, porzucony plecak",
    "znajdują dziwną, świecącą w ciemności roślinę",
    "próbują rozszyfrować mapę narysowaną krwią",
    "cicho przekradają się obok śpiącego potwora",
    "zauważają w oddali migoczące światło",
    "omijają głęboką przepaść po starym moście",
    "odpierają nagły atak nietoperzy",
    "podziwiają podziemny wodospad",
    "kierują się w stronę podejrzanego hałasu",
    # Nowe 50
    "ślizgają się na mokrym mchu porastającym skały",
    "przemykają obok uśpionego stada nietoperzy",
    "starają się odczytać wyblakłe ostrzeżenie na ścianie",
    "wyczuwają dziwny zapach siarki w powietrzu",
    "znajdują porzucony miecz wbity w czaszkę",
    "ignorują dziwne szepty dochodzące ze szczelin",
    "potykają się o stertę pradawnych kości",
    "zapalają nową pochodnię, by oświetlić gęsty mrok",
    "przyglądają się dziwnym posągom z dziurami zamiast oczu",
    "wyciągają mapę i z zakłopotaniem drapią się po głowach",
    "omijają na palcach śpiącego potwora z mackami",
    "węszą powietrze, czując woń spalenizny",
    "rozgarniają gęste pajęczyny swoimi broniami",
    "chowają się za skałą przed dziwnym, zielonym światłem",
    "gubią na chwilę kierunek w mrocznym labiryncie",
    "zatrzymują się, słysząc kroki w sąsiednim tunelu",
    "odnajdują stary, na wpół spalony dziennik uciekiniera",
    "podziwiają kryształy wyrastające ze ścian",
    "wzdrygają się na dźwięk upadającej kropli wody",
    "kopią mały kamyczek prosto w rzekę lawy",
    "próbują nie obudzić pobliskich, wielkich pająków",
    "wciągają głęboko zatęchłe powietrze z lochu",
    "wypatrują ukrytych przejść za zasłonami z dziwnych grzybów",
    "walczą z chmarą irytujących, świecących robaków",
    "czyszczą zbroje z grubej warstwy pyłu z jaskini",
    "skaczą przez szeroką kałużę z nieznaną substancją",
    "z trudem przeciskają się przez wąską szczelinę w ścianie",
    "unikają ciosu wystrzelonej ze ściany starej strzały",
    "przecierają oczy, nie wierząc w ogrom tych podziemi",
    "badają podejrzanie wyglądającą skrzynię",
    "gaszą płomień pochodni, widząc w oddali patrole orków",
    "ostrożnie rozglądają się na wszystkie strony",
    "czują lodowaty powiew wiatru na karkach",
    "ściskają mocniej broń, szykując się na kłopoty",
    "narzekają na słabe oświetlenie w jaskini",
    "podnoszą z ziemi stary, wyblakły proporzec królestwa",
    "stąpają bardzo ostrożnie, by nie wywołać lawiny gruzu",
    "rzucają mały kamyk w głąb ciemnej, bezdennej studni",
    "obserwują spadającą w bezdenną otchłań pochodnię",
    "podziwiają stalaktyty wiszące nad wielką przepaścią",
    "cicho szepczą do siebie, słysząc ryk potwora w oddali",
    "unoszą sprzęt wyżej, gotowi na niespodziewany atak z mroku",
    "w pośpiechu szukają jakiejkolwiek ukrytej drogi ucieczki",
    "potykają się, łapiąc z trudem równowagę nad przepaścią",
    "zasłaniają uszy przed piskami potężnych, ślepych stworzeń",
    "badają strukturę dziwnego, niebieskiego śluzu na ziemi",
    "piją wodę z podziemnego, krystalicznie czystego źródła",
    "znajdują ślady ogromnych pazurów na kamiennej ścianie",
    "drapią się w głowę patrząc na zamknięte, wielkie wrota",
    "rozstawiają małe, prowizoryczne obozowisko dla bezpieczeństwa"
]

# Unikalne zdarzenia związane WYŁĄCZNIE z przypisaną do nich postacią (w drużynie)
character_events = {
    "eczme": [
        "Eczme próbuje pokazać jak szybko macha bronią, o mało co nie trafiając w ścianę.",
        "Eczme o mało co nie wpada do kałuży z dziwnym śluzem.",
        "Eczme wyciąga broń na widok własnego cienia."
    ],
    "damian": [
        "Damian ziewa, twierdząc, że to miejsce przypomina mu poniedziałek w pracy.",
        "Damian pyta, czy w tym lochu mają zasięg do internetu.",
        "Damian narzeka na wilgoć, obawiając się o swoje nowe ubranie."
    ],
    "pianek": [
        "Pianek idzie na przedzie, taranując barkiem pajęczyny.",
        "Pianek próbuje przepchnąć wielki głaz, żeby sprawdzić co pod nim jest.",
        "Pianek chrupie coś głośno, całkowicie ignorując potrzebę zachowania ciszy."
    ],
    "yomen": [
        "Yomen potyka się o własne nogi, ale udaje, że to było celowe.",
        "Yomen chowa się za resztą za każdym razem, gdy gdzieś kapnie woda.",
        "Yomen nagle podskakuje ze strachu po tym, jak nadepnął na kruchą gałązkę."
    ],
    "maślak": [
        "Maślak próbuje zjeść znalezionego grzyba, a reszta drużyny go powstrzymuje.",
        "Maślak zastanawia się głośno, czy potwory stąd nadają się na grilla.",
        "Maślak kopie w kamień i zaraz potem zaczyna skakać, trzymając się za stopę."
    ],
    "domcia": [
        "Domcia szuka w kieszeniach jakiegoś błyskotliwego przedmiotu do rzucenia.",
        "Domcia poprawia sprzęt, żeby dobrze wyglądać nawet w mrocznych podziemiach.",
        "Domcia narzeka, że ten loch kompletnie nie pasuje do jej stylu."
    ]
}

def generate_base_texts():
    texts = []
    # Generuje 5 * 65 = 325 kombinacji w liczbie pojedynczej
    for s in singular_subjects:
        for a in singular_actions:
            texts.append(f"{s} {a}.")
            
    # Generuje 5 * 65 = 325 kombinacji w liczbie mnogiej
    for p_s in plural_subjects:
        for p_a in plural_actions:
            texts.append(f"{p_s} {p_a}.")
            
    # W sumie daje to 650 poprawnych gramatycznie bazowych opisów (znacznie ponad oczekiwane 150).
    return texts

BASE_TEXTS = generate_base_texts()

def get_random_flavor_text(party):
    """ Zwraca losowy tekst podziemi. Dodaje odzywkę znajomego TYLKO, gdy faktycznie jest on w `party`. """
    base = random.choice(BASE_TEXTS)
    
    # 25% szansy na specjalne zdarzenie od kogoś z obecnej drużyny
    if party and len(party) > 0 and random.random() < 0.25:
        chosen_member = random.choice(party)
        if chosen_member in character_events:
            extra_comment = random.choice(character_events[chosen_member])
            return base + " " + extra_comment
            
    return base
