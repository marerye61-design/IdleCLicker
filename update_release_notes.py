import urllib.request
import json

token = 'UKRYTY_TOKEN_GITHUB'
repo = 'marerye61-design/IdleCLicker'
tag_name = 'v0.14-pre-alpha'

url_get = f'https://api.github.com/repos/{repo}/releases/tags/{tag_name}'
headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}
req_get = urllib.request.Request(url_get, headers=headers)
try:
    with urllib.request.urlopen(req_get) as response:
        release_data = json.loads(response.read().decode('utf-8'))
        release_id = release_data['id']
except Exception as e:
    print(f"Error fetching release: {e}")
    exit(1)

new_body = '''Wersja 0.14 Pre-Alpha przynosi znaczne poprawki interfejsu (UX) oraz jakości (QoL):
- **Owijki PowerKeeper** - dodano nowy, potężny przedmiot do gry (Owijki 'PowerKeeper').
- **Tryb Fullscreen** - dostosowano interfejs gry pod kątem działania w trybie pełnoekranowym (fullscreen).
- **Poprawiono leczenie mikstur** - teraz odnawiają właściwy procent HP uwzględniając bonusy z przedmiotów.
- **Odświeżanie na Wyprawach** - dodano nowy przycisk pozwalający przetasować przeciwników z poziomu zakładki bez konieczności wychodzenia.
- **Siatka Inwentarza** - zreorganizowano wygląd plecaka; dodano puste pola na końcu ekwipunku i powiększono ikony.
- **Zdejmowanie ekwipunku (Drag & Drop)** - ułatwiono zarządzanie ubiorem; przeciągnięcie wyposażonego przedmiotu na siatkę inwentarza zdejmuje go z postaci i umieszcza w plecaku.
- **Eliminacja migotania interfejsu** - całkowicie usunięto irytujące mruganie ekranu podczas zmian ekwipunku i sklepu poprzez wprowadzenie reużywania wyrenderowanych ramek zamiast ich ponownego odrysowywania.
- **Blokada Ekwipunku** - wdrożono sprawdzanie poziomu bohatera; nie można już wyposażyć (przez przeciąganie i przycisk) przedmiotów przewyższających poziom postaci.
- **Rozbudowa Konsoli Debugowania** - dodano pole pozwalające zespawnować każdy dostępny w grze przedmiot; wdrożono automatyczne skalowanie okna do zawartości.
- **Usuwanie zapisów** - dodano opcję "Wyczyść wszystko", usuwającą wszystkie pliki save za jednym zamachem (z monitem zabezpieczającym).
- **Balans Rozgrywki** - zmniejszono drastyczny przyrost siły ataku przeciwników i wzmocniono podstawowe statystyki zbroi i broni.'''

url_patch = f'https://api.github.com/repos/{repo}/releases/{release_id}'
data = {
    'body': new_body
}
req_patch = urllib.request.Request(url_patch, data=json.dumps(data).encode('utf-8'), headers=headers, method='PATCH')
try:
    with urllib.request.urlopen(req_patch) as response:
        print("Successfully updated release notes.")
except Exception as e:
    print(f"Error updating release: {e}")
