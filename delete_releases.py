import urllib.request
import json
import urllib.error

token = 'UKRYTY_TOKEN_GITHUB'
repo = 'marerye61-design/IdleCLicker'
tags = ['v0.11-pre-alpha', 'pre_alpha-0.1']

url = f'https://api.github.com/repos/{repo}/releases'
headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        releases = json.loads(response.read().decode('utf-8'))
        for r in releases:
            if r['tag_name'] in tags:
                del_url = f"https://api.github.com/repos/{repo}/releases/{r['id']}"
                del_req = urllib.request.Request(del_url, headers=headers, method='DELETE')
                try:
                    urllib.request.urlopen(del_req)
                    print(f"Deleted release {r['tag_name']}")
                except Exception as e:
                    print(f"Failed to delete {r['tag_name']}: {e}")
                    
        # Also need to delete the tags themselves, so recreation works smoothly
        for tag in tags:
            tag_url = f"https://api.github.com/repos/{repo}/git/refs/tags/{tag}"
            tag_req = urllib.request.Request(tag_url, headers=headers, method='DELETE')
            try:
                urllib.request.urlopen(tag_req)
                print(f"Deleted tag {tag}")
            except Exception as e:
                print(f"Failed to delete tag {tag}: {e}")

except Exception as e:
    print(f"Error listing releases: {e}")
