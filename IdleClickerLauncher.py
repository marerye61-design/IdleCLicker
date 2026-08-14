import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import json
import os
import sys
import subprocess
import shutil
import zipfile
import threading
import io
import webbrowser

REPO_OWNER = "marerye61-design"
REPO_NAME = "IdleCLicker"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases"
# Zabezpieczenie ścieżek bezwzględnych dla skrótów Windows
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

VERSION_FILE = os.path.join(SCRIPT_DIR, "version.txt")
MAIN_EXECUTABLE = os.path.join(SCRIPT_DIR, "IdleClicker.exe")

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IdleClicker Launcher")
        self.root.geometry("450x200")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c1a12")
        
        self.root.eval('tk::PlaceWindow . center')
        
        self.status_lbl = tk.Label(root, text="Sprawdzanie aktualizacji...", font=("Georgia", 12), bg="#2c1a12", fg="#f4d03f")
        self.status_lbl.pack(pady=15)
        
        self.link_lbl = tk.Label(root, text="", font=("Georgia", 10, "underline"), bg="#2c1a12", fg="#3498db", cursor="hand2")
        self.link_lbl.pack(pady=5)
        self.link_lbl.bind("<Button-1>", lambda e: webbrowser.open(REPO_URL))
        
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        
        self.btn_frame = tk.Frame(root, bg="#2c1a12")
        self.btn_frame.pack(pady=10)
        
        threading.Thread(target=self.check_for_updates, daemon=True).start()
        
    def get_local_version(self):
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r", encoding="utf-8") as f:
                return f.read().strip().replace('\ufeff', '')
        return "0.0.0"

    def set_local_version(self, version):
        with open(VERSION_FILE, "w") as f:
            f.write(version)

    def launch_game(self):
        self.root.after(0, lambda: self.status_lbl.config(text="Uruchamianie gry..."))
        
        if os.path.exists(MAIN_EXECUTABLE):
            subprocess.Popen([MAIN_EXECUTABLE])
        elif os.path.exists("main.py"):
            subprocess.Popen([sys.executable, "main.py"])
        else:
            messagebox.showerror("Błąd", f"Nie znaleziono pliku {MAIN_EXECUTABLE} ani main.py!")
        
        self.root.after(1000, self.root.destroy)

    def show_up_to_date(self, version):
        self.status_lbl.config(text=f"Gra jest aktualna! (Wersja: v{version})", fg="#2ecc71")
        self.link_lbl.config(text="")
        btn = ttk.Button(self.btn_frame, text="Graj", command=self.launch_game)
        btn.pack(side=tk.LEFT, padx=10)
        self.root.after(3000, self.launch_game)

    def show_update_available(self, latest_version, zip_url):
        self.status_lbl.config(text=f"Dostępna nowa wersja: v{latest_version}!", fg="#e74c3c")
        self.link_lbl.config(text="Pobierz ręcznie z GitHub (kliknij)")
        
        btn_auto = ttk.Button(self.btn_frame, text="Aktualizuj Automatycznie", 
                              command=lambda: threading.Thread(target=self.download_and_extract, args=(zip_url, latest_version), daemon=True).start())
        btn_auto.pack(side=tk.LEFT, padx=5)
        
        btn_skip = ttk.Button(self.btn_frame, text="Pomiń i Graj", command=self.launch_game)
        btn_skip.pack(side=tk.LEFT, padx=5)

    def check_for_updates(self):
        try:
            req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if data and isinstance(data, list):
                        latest_release = data[0]
                        latest_version = latest_release.get("tag_name", "0.0.0").replace("v", "").strip()
                        local_version = self.get_local_version().replace("v", "").strip()
                        
                        if latest_version != local_version and latest_version != "0.0.0":
                            assets = latest_release.get("assets", [])
                            zip_url = assets[0].get("browser_download_url") if assets else None
                            if zip_url:
                                self.root.after(0, lambda: self.show_update_available(latest_version, zip_url))
                                return
                            else:
                                self.root.after(0, lambda: self.show_update_available(latest_version, None))
                                return
                        else:
                            self.root.after(0, lambda: self.show_up_to_date(local_version))
                            return
                    else:
                        self.root.after(0, lambda: self.show_up_to_date(self.get_local_version()))
                else:
                    self.root.after(0, lambda: self.show_up_to_date(self.get_local_version()))
        except Exception as e:
            print(f"Błąd sprawdzania aktualizacji: {e}")
            self.root.after(0, lambda: self.show_up_to_date(self.get_local_version()))

    def download_and_extract(self, url, new_version):
        if not url: return
        try:
            for widget in self.btn_frame.winfo_children():
                widget.destroy()
            self.root.after(0, lambda: self.status_lbl.config(text="Pobieranie aktualizacji...", fg="#f1c40f"))
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                total_size = int(response.headers.get('content-length', 0))
                
                block_size = 8192
                downloaded = 0
                
                zip_buffer = io.BytesIO()
                while True:
                    data = response.read(block_size)
                    if not data:
                        break
                    zip_buffer.write(data)
                    downloaded += len(data)
                    if total_size > 0:
                        percent = int((downloaded / total_size) * 100)
                        self.root.after(0, lambda p=percent: self.progress.config(value=p))
                
            self.root.after(0, lambda: self.status_lbl.config(text="Czyszczenie starych plików..."))
            
            safe_to_keep = {
                "IdleClickerLauncher.py", "IdleClickerLauncher.exe", "IdleClickerLauncher.spec",
                "saves", "savegame.pkl", "version.txt", ".git", ".gitignore", "build.ps1", "IdleClicker.spec"
            }
            
            for item in os.listdir(SCRIPT_DIR):
                if item in safe_to_keep:
                    continue
                item_path = os.path.join(SCRIPT_DIR, item)
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                except Exception as e:
                    print(f"Nie usunięto {item}: {e}")
                    
            self.root.after(0, lambda: self.status_lbl.config(text="Rozpakowywanie..."))
            
            with zipfile.ZipFile(zip_buffer) as zip_ref:
                for member in zip_ref.namelist():
                    if not member.endswith("IdleClickerLauncher.exe"):
                        zip_ref.extract(member, SCRIPT_DIR)
                        
            self.set_local_version(new_version)
            self.launch_game()
            
        except Exception as e:
            messagebox.showerror("Błąd Aktualizacji", f"Wystąpił błąd podczas pobierania aktualizacji:\n{e}")
            self.launch_game()

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()
