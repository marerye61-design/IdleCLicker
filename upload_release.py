import urllib.request
import json

token = 'UKRYTY_TOKEN_GITHUB'
repo = 'marerye61-design/IdleCLicker'
tag_name = 'v0.15'
release_name = 'Idle Clicker - Wersja 0.15 (CustomTkinter)'
zip_path = 'IdleClicker_0.15.zip'

url = f'https://api.github.com/repos/{repo}/releases'
headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}
data = {
    'tag_name': tag_name,
    'name': release_name,
    'body': '''Wersja 0.15 przynosi fundamentalną przebudowę pod maską gry i stabilizację interfejsu w oparciu o nowy silnik CustomTkinter:

- **Nowy Wygląd i Silnik (CustomTkinter)**: Główne okno gry oraz wszystkie mechanizmy przycisków wewnątrz paneli zostały zmodernizowane, przynosząc zaokrąglone krawędzie i płynniejsze działanie.
- **Globalny System Przechwytywania Błędów (Crash Handler)**: Zaimplementowano tarczę bezpieczeństwa; w przypadku nagłego załamania gry, program bezpiecznie zapisze szczegóły błędu w pliku `error_log.txt`, uniemożliwiając ciche "crashe".
- **Stabilizacja Sklepów, Ekwipunku i Miasta**: Wyczyszczono stare pozostałości klasycznego Tkintera, które konfliktowały się z nowymi obiektami (bg, fg, relief).''',
    'draft': False,
    'prerelease': False
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
try:
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        upload_url = res_data['upload_url'].split('{')[0]
except Exception as e:
    exit(1)

upload_url_full = f'{upload_url}?name=IdleClicker_0.15.zip'
headers['Content-Type'] = 'application/zip'
with open(zip_path, 'rb') as f:
    file_data = f.read()

req_upload = urllib.request.Request(upload_url_full, data=file_data, headers=headers, method='POST')
try:
    urllib.request.urlopen(req_upload)
except Exception:
    pass
