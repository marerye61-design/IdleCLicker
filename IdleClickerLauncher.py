import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import sys
import subprocess
import zipfile
import threading
import io

REPO_OWNER = "marerye61-design"
REPO_NAME = "IdleCLicker"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
VERSION_FILE = "version.txt"
MAIN_EXECUTABLE = "IdleClicker.exe"

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IdleClicker Launcher")
        self.root.geometry("400x150")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c1a12")
        
        # Srodkowanie okna
        self.root.eval('tk::PlaceWindow . center')
        
        self.status_lbl = tk.Label(root, text="Sprawdzanie aktualizacji...", font=("Georgia", 12), bg="#2c1a12", fg="#f4d03f")
        self.status_lbl.pack(pady=20)
        
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        
        # Uruchom w tle by nie blokować GUI
        threading.Thread(target=self.check_for_updates, daemon=True).start()
        
    def get_local_version(self):
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r") as f:
                return f.read().strip()
        return "0.0.0"

    def set_local_version(self, version):
        with open(VERSION_FILE, "w") as f:
            f.write(version)

    def launch_game(self):
        self.root.after(0, lambda: self.status_lbl.config(text="Uruchamianie gry..."))
        
        if os.path.exists(MAIN_EXECUTABLE):
            subprocess.Popen([MAIN_EXECUTABLE])
        elif os.path.exists("main.py"):
            # Fallback dla wersji developerskiej
            subprocess.Popen([sys.executable, "main.py"])
        else:
            messagebox.showerror("Błąd", f"Nie znaleziono pliku {MAIN_EXECUTABLE}!")
        
        self.root.after(1000, self.root.destroy)

    def check_for_updates(self):
        try:
            resp = requests.get(API_URL, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                latest_version = data.get("tag_name", "0.0.0").replace("v", "")
                local_version = self.get_local_version().replace("v", "")
                
                # Porównanie wersji - prymitywne sprawdzanie stringa
                if latest_version != local_version and latest_version != "0.0.0":
                    self.root.after(0, lambda: self.status_lbl.config(text=f"Znaleziono aktualizację: v{latest_version}"))
                    
                    assets = data.get("assets", [])
                    if assets:
                        zip_url = assets[0].get("browser_download_url")
                        if zip_url:
                            self.download_and_extract(zip_url, latest_version)
                            return
                
        except Exception as e:
            print(f"Błąd sprawdzania aktualizacji: {e}")
            
        # Jesli nie ma updatu lub wystapil blad, odpal gre
        self.launch_game()

    def download_and_extract(self, url, new_version):
        try:
            self.root.after(0, lambda: self.status_lbl.config(text="Pobieranie aktualizacji..."))
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            block_size = 8192
            downloaded = 0
            
            zip_buffer = io.BytesIO()
            for data in response.iter_content(block_size):
                zip_buffer.write(data)
                downloaded += len(data)
                if total_size > 0:
                    percent = int((downloaded / total_size) * 100)
                    self.root.after(0, lambda p=percent: self.progress.config(value=p))
            
            self.root.after(0, lambda: self.status_lbl.config(text="Rozpakowywanie..."))
            
            # Wypakuj z wyłączeniem pliku launchera na ktorym pracujemy (aby uniknąć blokady pliku)
            with zipfile.ZipFile(zip_buffer) as zip_ref:
                for member in zip_ref.namelist():
                    if not member.endswith("IdleClickerLauncher.exe"):
                        # Upewnij sie, ze jesli uzytkownik pobral release jako IdleClicker/costam, to to obslugujemy.
                        # Standardowy GitHub release robi zipa z zawartoscia luzem (wg naszego builda).
                        zip_ref.extract(member, ".")
                        
            self.set_local_version(new_version)
            self.launch_game()
            
        except Exception as e:
            messagebox.showerror("Błąd Aktualizacji", f"Wystąpił błąd podczas pobierania aktualizacji:\n{e}")
            self.launch_game()

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()
