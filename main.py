import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import math
from PIL import Image, ImageTk
import os
import sys
import pickle
import random
import time
import threading

import combat
from player import Player
from quests import get_all_quests
from shop import FantasyShop
from market import Market
import npc_lore
from items import ITEMS_DB
import dungeons
from flavor_texts import get_random_flavor_text

# Ustawienie bezpiecznej ścieżki do plików zapisu (aby uniknąć ich nadpisania przy aktualizacji plików gry)
APPDATA_DIR = os.path.join(os.getenv('APPDATA'), 'IdleClicker') if os.name == 'nt' else os.path.join(os.path.expanduser('~'), '.idleclicker')
SAVES_DIR = os.path.join(APPDATA_DIR, 'saves')

# Próba migracji starych zapisów z lokalnego folderu (jeśli ktoś aktualizuje grę)
LOCAL_SAVES_DIR = "saves"
if os.path.exists(LOCAL_SAVES_DIR) and not os.path.exists(SAVES_DIR):
    import shutil
    try:
        shutil.copytree(LOCAL_SAVES_DIR, SAVES_DIR)
        print(f"Pomyślnie zmigrowano lokalne save'y do {SAVES_DIR}")
    except Exception as e:
        print(f"Błąd podczas migracji save'ów: {e}")

def save_game(player, filepath):
    player.last_update_time = time.time()
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)
    
    # Podmiana katalogu na bezpieczny
    safe_filepath = os.path.join(SAVES_DIR, os.path.basename(filepath))
    with open(safe_filepath, 'wb') as f:
        pickle.dump(player, f)

class ScrollableFrame(tk.Frame):
    def __init__(self, container, bg_color="#2c1a12", *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Wiązanie zmiany rozmiaru płótna by wymusić szerokość wewnętrznej ramki
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.window_id, width=e.width)
        )
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        # Sprawdzamy czy okno rzeczywiście potrzebuje scrolla
        if self.canvas.yview() == (0.0, 1.0): return
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def destroy(self):
        self.canvas.unbind_all("<MouseWheel>")
        super().destroy()

class IdleRPGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IDLE RPG - Fantasy Edition GUI")
        self.root.geometry("1024x768")
        
        self.setup_styles()
        
        self.player = None
        self.current_save_path = None
        self.market = Market()
        self.fantasy_shop = FantasyShop()
        
        self.bg_images = {}
        self.load_backgrounds()
        self.load_portraits()
        self.load_item_icons()
        
        self.container = tk.Frame(self.root, bg="#1a120c")
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.dungeon_active = False
        self.dungeon_time = 0
        self.dungeon_next_flavor = 0
        self.current_dungeon = None
        
        self.combat_active = False
        self.combat_enemy = None
        self.combat_turn = 0
        self.current_view = "menu"
        
        self.root.bind("<F12>", lambda e: self.open_debug_console())
        self.root.bind("<grave>", lambda e: self.open_debug_console())
        
        self.save_timer_id = None
        self.gold_timer_id = None
        self.auto_save_timer()
        self.passive_gold_timer()
        
        self.show_start_menu()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Fantasy.TButton", 
                        font=("Georgia", 12, "bold"), 
                        foreground="#f4d03f", 
                        background="#3e2723",
                        borderwidth=3, 
                        relief="raised")
        style.map("Fantasy.TButton", 
                  background=[("active", "#5d4037")],
                  foreground=[("active", "#f7dc6f")])
                  
        style.configure("Danger.TButton", 
                        font=("Georgia", 12, "bold"), 
                        foreground="#ff9999", 
                        background="#4a2323",
                        borderwidth=3)
        style.map("Danger.TButton", background=[("active", "#7a3333")])

    def auto_save_timer(self):
        if self.player and self.current_save_path:
            save_game(self.player, self.current_save_path)
            self.log_msg("[System] Automatyczny zapis gry.")
            
        if getattr(self, 'save_timer_id', None):
            self.root.after_cancel(self.save_timer_id)
        self.save_timer_id = self.root.after(60000, self.auto_save_timer)

    def passive_gold_timer(self):
        if self.player:
            self.player.update_offline_progress()
            self.update_sidebar()
            # Quest checker w tle
            for q in self.player.quests:
                q.update_status(self.player.level)
                if q.status == 'IN_PROGRESS':
                    q.complete(self.player) # aktualizuje flagi ukończenia np ze złota
                    
        if getattr(self, 'gold_timer_id', None):
            self.root.after_cancel(self.gold_timer_id)
        self.gold_timer_id = self.root.after(1000, self.passive_gold_timer)

    def show_tavern(self):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "tavern"
        
        # Nowe wygenerowane mroczne tło tawerny
        self.set_background(self.view_panel, "tavern")
        
        self.tavern_canvas = tk.Canvas(self.view_panel, width=700, height=600, bg="#111", highlightthickness=0)
        self.tavern_canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        if "tavern" in self.bg_images:
            self.tavern_canvas.create_image(0, 0, image=self.bg_images["tavern"], anchor=tk.NW)
            
        # Półprzezroczyste zaciemnienie tła tawerny dla lepszej widoczności
        self.tavern_canvas.create_rectangle(0, 0, 700, 600, fill="#000000", stipple="gray50", tags="bg_dim")
        
        title = self.tavern_canvas.create_text(350, 40, text="Tawerna 'Pod Skrzydłem Upadłego Anioła'", font=("Georgia", 22, "bold"), fill="#f4d03f")
        self.tavern_canvas.create_text(350, 70, text="Kliknij na postać, aby z nią porozmawiać.", font=("Georgia", 12, "italic"), fill="#ccc")
        
        positions = {
            "maslak": (80, 150),
            "damian": (280, 150),
            "pianek": (480, 150),
            "yomen": (80, 370),
            "eczme": (280, 370),
            "domcia": (480, 370)
        }
        
        for npc_id, npc_data in npc_lore.NPC_DB.items():
            if npc_id in positions:
                x, y = positions[npc_id]
                img_key = npc_data["img"]
                tag = f"npc_{npc_id}"
                
                # Złota ramka, domyślnie ukryta
                self.tavern_canvas.create_rectangle(x-2, y-2, x+182, y+182, outline="#f4d03f", width=4, tags=f"rect_{npc_id}", state=tk.HIDDEN)
                
                if img_key in self.portraits:
                    self.tavern_canvas.create_image(x, y, image=self.portraits[img_key], anchor=tk.NW, tags=(tag, "npc_img"))
                else:
                    self.tavern_canvas.create_rectangle(x, y, x+180, y+180, fill="gray", tags=(tag, "npc_img"))
                
                # Nazwa, domyślnie ukryta
                self.tavern_canvas.create_text(x+90, y-15, text=npc_data["name"].split(',')[0], fill="#f4d03f", font=("Georgia", 14, "bold"), tags=f"name_{npc_id}", state=tk.HIDDEN)
                
                self.tavern_canvas.tag_bind(tag, "<Enter>", lambda e, n_id=npc_id: self.on_npc_hover(n_id))
                self.tavern_canvas.tag_bind(tag, "<Leave>", lambda e, n_id=npc_id: self.on_npc_leave(n_id))
                self.tavern_canvas.tag_bind(tag, "<Button-1>", lambda e, n_id=npc_id: self.open_npc_dialog(n_id))

    def on_npc_hover(self, npc_id):
        if hasattr(self, 'tavern_canvas'):
            self.tavern_canvas.itemconfigure(f"rect_{npc_id}", state=tk.NORMAL)
            self.tavern_canvas.itemconfigure(f"name_{npc_id}", state=tk.NORMAL)
            self.tavern_canvas.config(cursor="hand2")
            
    def on_npc_leave(self, npc_id):
        if hasattr(self, 'tavern_canvas'):
            self.tavern_canvas.itemconfigure(f"rect_{npc_id}", state=tk.HIDDEN)
            self.tavern_canvas.itemconfigure(f"name_{npc_id}", state=tk.HIDDEN)
            self.tavern_canvas.config(cursor="")

    def open_npc_dialog(self, npc_id):
        npc = npc_lore.NPC_DB[npc_id]
        
        win = tk.Toplevel(self.root)
        win.title(npc["name"])
        win.geometry("650x720")
        win.configure(bg="#1a100b")
        win.transient(self.root)
        win.grab_set()
        
        x = self.root.winfo_x() + (self.root.winfo_width() - 650) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 720) // 2
        win.geometry(f"+{x}+{y}")
        
        top_frame = tk.Frame(win, bg="#1a100b")
        top_frame.pack(pady=15, fill=tk.X)
        
        if npc["img"] in self.portraits:
            lbl_img = tk.Label(top_frame, image=self.portraits[npc["img"]], bg="#1a100b", bd=3, relief=tk.RIDGE)
            lbl_img.pack(side=tk.LEFT, padx=25)
            
        lbl_name = tk.Label(top_frame, text=npc["name"], font=("Georgia", 16, "bold"), fg="#f4d03f", bg="#1a100b", wraplength=380, justify=tk.LEFT)
        lbl_name.pack(side=tk.LEFT, padx=10)
        
        dialog_box = scrolledtext.ScrolledText(win, bg="#2c1a12", fg="#ddd", font=("Georgia", 11), wrap=tk.WORD, height=10, bd=4, relief=tk.SUNKEN)
        dialog_box.pack(padx=20, pady=8, fill=tk.BOTH, expand=True)
        dialog_box.insert(tk.END, f"{npc['name'].split(',')[0]}: {npc['greeting']}\n\n")
        dialog_box.config(state=tk.DISABLED)
        
        def say(text):
            dialog_box.config(state=tk.NORMAL)
            dialog_box.insert(tk.END, f"{npc['name'].split(',')[0]}: {text}\n\n", "response")
            dialog_box.tag_config("response", foreground="#f4d03f")
            dialog_box.see(tk.END)
            dialog_box.config(state=tk.DISABLED)
            
        btn_frame = tk.Frame(win, bg="#1a100b")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        for option, response in npc["options"].items():
            btn = tk.Button(btn_frame, text=option, font=("Georgia", 11, "bold"), bg="#3e2723", fg="#f4d03f", activebackground="#5d4037", activeforeground="#f7dc6f", bd=3, relief=tk.RAISED, command=lambda r=response: say(r))
            btn.pack(fill=tk.X, padx=30, pady=3)
            
        # Opcje rekrutacji i wyboru towarzysza w walce (jako opcja dialogowa)
        if npc_id in self.player.party:
            is_active = (getattr(self.player, 'active_companion', None) == npc_id)
            if not is_active:
                def recruit_action():
                    say("Z przyjemnością! Pakuję sprzęt i ruszamy.")
                    self.player.select_active_companion(npc_id)
                    self.update_sidebar()
                    self.log_msg(f"Ustawiono: {npc['name'].split(',')[0]} walczy jako twój aktywny towarzysz!")
                    win.destroy()
                    self.open_npc_dialog(npc_id)
                    
                btn_p = tk.Button(btn_frame, text="[Wyrusz ze mną do lochu!]", font=("Georgia", 11, "bold"), bg="#27ae60", fg="white", activebackground="#2ecc71", activeforeground="white", bd=3, relief=tk.RAISED, command=recruit_action)
                btn_p.pack(fill=tk.X, padx=30, pady=3)
            else:
                btn_p = tk.Button(btn_frame, text="✅ Towarzyszy ci w walce", font=("Georgia", 11, "bold"), bg="#1a100b", fg="#2ecc71", bd=1, state=tk.DISABLED)
                btn_p.pack(fill=tk.X, padx=30, pady=3)
        else:
            tk.Label(btn_frame, text="🔒 [Zwerbuj] (Ukończ zadanie postaci w Dzienniku Zadań)", font=("Georgia", 9, "italic"), bg="#1a100b", fg="#aaa").pack(pady=3)

        btn_close = tk.Button(btn_frame, text="(Odejdź)", font=("Georgia", 11, "italic"), bg="#2a1610", fg="#aaa", bd=2, command=win.destroy)
        btn_close.pack(fill=tk.X, padx=30, pady=4)

    def load_backgrounds(self):
        assets_dir = "assets"
        try:
            if os.path.exists(os.path.join(assets_dir, "menu_bg.jpg")):
                self.bg_images["menu"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "menu_bg.jpg")).resize((1024, 768)))
            if os.path.exists(os.path.join(assets_dir, "combat_bg.jpg")):
                self.bg_images["combat"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "combat_bg.jpg")).resize((1024, 768)))
            if os.path.exists(os.path.join(assets_dir, "dungeon_bg.jpg")):
                self.bg_images["dungeon"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "dungeon_bg.jpg")).resize((1024, 768)))
            if os.path.exists(os.path.join(assets_dir, "tavern_bg.jpg")):
                self.bg_images["tavern"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "tavern_bg.jpg")).resize((1024, 768)))
                
            # Dedykowane tła tytularne dla lochów
            if os.path.exists(os.path.join(assets_dir, "dungeon_d1_bg.jpg")):
                self.bg_images["dungeon_d1"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "dungeon_d1_bg.jpg")).resize((1024, 768)))
            if os.path.exists(os.path.join(assets_dir, "dungeon_d2_bg.jpg")):
                self.bg_images["dungeon_d2"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "dungeon_d2_bg.jpg")).resize((1024, 768)))
            if os.path.exists(os.path.join(assets_dir, "dungeon_d3_bg.jpg")):
                self.bg_images["dungeon_d3"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "dungeon_d3_bg.jpg")).resize((1024, 768)))
        except Exception as e:
            print("Nie można załadować obrazów:", e)

    def load_portraits(self):
        self.portraits = {}
        self.companion_portraits = {}
        portraits_dir = os.path.join("assets", "portraits")
        if not os.path.exists(portraits_dir):
            return
        try:
            for file in os.listdir(portraits_dir):
                if file.endswith(".jpg") or file.endswith(".png"):
                    key = file.split('.')[0]
                    img = Image.open(os.path.join(portraits_dir, file))
                    width, height = img.size
                    if width != height:
                        min_dim = min(width, height)
                        left = (width - min_dim) // 2
                        top = 0 # Ucina od góry dla zachowania twarzy
                        right = (width + min_dim) // 2
                        bottom = min_dim
                        img = img.crop((left, top, right, bottom))
                    self.portraits[key] = ImageTk.PhotoImage(img.resize((180, 180)))
                    self.companion_portraits[key] = ImageTk.PhotoImage(img.resize((80, 80)))
        except Exception as e:
            print("Nie można załadować portretów:", e)

    def load_item_icons(self):
        self.item_icons = {}
        self.item_icons_large = {}
        items_dir = os.path.join("assets", "items")
        if not os.path.exists(items_dir):
            return
        try:
            for file in os.listdir(items_dir):
                if file.endswith(".jpg") or file.endswith(".png"):
                    key = file.split('.')[0]
                    img = Image.open(os.path.join(items_dir, file))
                    width, height = img.size
                    if width != height:
                        min_dim = min(width, height)
                        left = (width - min_dim) // 2
                        top = (height - min_dim) // 2
                        right = (width + min_dim) // 2
                        bottom = (height + min_dim) // 2
                        img = img.crop((left, top, right, bottom))
                    self.item_icons[key] = ImageTk.PhotoImage(img.resize((54, 54)))
                    self.item_icons_large[key] = ImageTk.PhotoImage(img.resize((120, 120)))
        except Exception as e:
            print("Błąd ładowania ikon przedmiotów:", e)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def set_background(self, parent, bg_type):
        if bg_type in self.bg_images:
            bg_label = tk.Label(parent, image=self.bg_images[bg_type])
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def show_start_menu(self):
        self.clear_container()
        self.set_background(self.container, "menu")
        
        menu_frame = tk.Frame(self.container, bg="#2c1a12", bd=10, relief=tk.RIDGE)
        menu_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=450, height=500)
        
        tk.Label(menu_frame, text="IDLE RPG\nFantasy Edition", font=("Georgia", 28, "bold"), fg="#f4d03f", bg="#2c1a12").pack(pady=30)
        
        ttk.Button(menu_frame, text="Nowa Gra", style="Fantasy.TButton", command=self.new_game).pack(pady=15, fill=tk.X, padx=50)
        
        if not os.path.exists(SAVES_DIR):
            os.makedirs(SAVES_DIR)
        saves = [f for f in os.listdir(SAVES_DIR) if f.endswith('.pkl')]
        
        if saves:
            ttk.Button(menu_frame, text="Wczytaj Grę", style="Fantasy.TButton", command=lambda: self.load_game_menu(saves)).pack(pady=15, fill=tk.X, padx=50)
            ttk.Button(menu_frame, text="Usuń Zapis", style="Danger.TButton", command=lambda: self.delete_save_menu(saves)).pack(pady=15, fill=tk.X, padx=50)
            
        ttk.Button(menu_frame, text="Wyjdź", style="Fantasy.TButton", command=self.root.quit).pack(pady=15, fill=tk.X, padx=50)

    def new_game(self):
        win = tk.Toplevel(self.root)
        win.title("Nowa Gra")
        win.geometry("400x250")
        win.configure(bg="#2c1a12")
        win.transient(self.root)
        win.grab_set()
        
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - win.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{x}+{y}")
        
        tk.Label(win, text="PODAJ IMIĘ BOHATERA:", font=("Georgia", 16, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=25)
        
        entry = tk.Entry(win, font=("Georgia", 14), bg="#3e2723", fg="white", insertbackground="white", bd=3, relief=tk.SUNKEN)
        entry.pack(pady=10, padx=50, fill=tk.X)
        entry.focus()
        
        def confirm(event=None):
            name = entry.get().strip()
            if not name:
                messagebox.showwarning("Ostrzeżenie", "Imię bohatera nie może być puste!", parent=win)
                return
            
            win.destroy()
            self.player = Player(name)
            self.player.quests = get_all_quests()
            self.current_save_path = os.path.join(SAVES_DIR, f"{name.replace(' ', '_')}.pkl")
            save_game(self.player, self.current_save_path)
            self.build_main_ui()
            
        ttk.Button(win, text="Rozpocznij Przygodę", style="Fantasy.TButton", command=confirm).pack(pady=15)
        win.bind('<Return>', confirm)

    def load_game_menu(self, saves):
        win = tk.Toplevel(self.root)
        win.title("Wczytaj Zapis")
        win.geometry("350x450")
        win.configure(bg="#2c1a12")
        
        tk.Label(win, text="Wybierz zapis:", font=("Georgia", 14), bg="#2c1a12", fg="#f4d03f").pack(pady=10)
        listbox = tk.Listbox(win, bg="#3e2723", fg="white", font=("Georgia", 12))
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        for s in saves:
            listbox.insert(tk.END, s.replace('.pkl', ''))
            
        def load_selected():
            sel = listbox.curselection()
            if sel:
                idx = sel[0]
                filepath = os.path.join(SAVES_DIR, saves[idx])
                with open(filepath, 'rb') as f:
                    p = pickle.load(f)
                    if getattr(p, 'version', '1.0') != '1.1':
                        if not messagebox.askyesno("Ostrzeżenie", "Ten zapis pochodzi ze starszej wersji gry.\nMoże to skutkować błędami. Czy na pewno chcesz wczytać?"):
                            return
                    # Przeniesienie logiki migracji do klasy obiektu by utrzymać czystość kodu (Iteracja 4)
                    p.migrate()
                    p.update_offline_progress()
                self.player = p
                self.current_save_path = filepath
                win.destroy()
                self.build_main_ui()
                
        ttk.Button(win, text="Wczytaj", style="Fantasy.TButton", command=load_selected).pack(pady=10)

    def delete_save_menu(self, saves):
        win = tk.Toplevel(self.root)
        win.title("Usuń Zapis")
        win.geometry("350x450")
        win.configure(bg="#2c1a12")
        
        tk.Label(win, text="Wybierz zapis do usunięcia:", font=("Georgia", 14), bg="#2c1a12", fg="#ff9999").pack(pady=10)
        listbox = tk.Listbox(win, bg="#3e2723", fg="white", font=("Georgia", 12))
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        for s in saves:
            listbox.insert(tk.END, s.replace('.pkl', ''))
            
        def del_selected():
            sel = listbox.curselection()
            if sel:
                idx = sel[0]
                filepath = os.path.join(SAVES_DIR, saves[idx])
                os.remove(filepath)
                messagebox.showinfo("Sukces", f"Usunięto {saves[idx]}")
                win.destroy()
                self.show_start_menu()
                
        ttk.Button(win, text="Usuń", style="Danger.TButton", command=del_selected).pack(pady=10)

    def build_main_ui(self):
        self.clear_container()
        
        self.sidebar = tk.Frame(self.container, width=280, bg="#1a100b", bd=5, relief=tk.RIDGE)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        self.lbl_stats = tk.Label(self.sidebar, text="", font=("Georgia", 10, "bold"), justify=tk.LEFT, bg="#1a100b", fg="#f4d03f", anchor="nw")
        self.lbl_stats.pack(fill=tk.BOTH, padx=10, pady=10)
        
        nav_sf = ScrollableFrame(self.sidebar, bg_color="#1a100b")
        nav_sf.pack(fill=tk.BOTH, expand=True, pady=10)
        nav_frame = nav_sf.scrollable_frame
        
        ttk.Button(nav_frame, text="Wyprawa (Walka)", style="Fantasy.TButton", command=self.show_expedition).pack(fill=tk.X, padx=10, pady=3)
        ttk.Button(nav_frame, text="Lochy (Wyprawy)", style="Fantasy.TButton", command=self.show_dungeons).pack(fill=tk.X, padx=10, pady=3)
        ttk.Button(nav_frame, text="Rozwój Postaci", style="Fantasy.TButton", command=self.show_stats).pack(fill=tk.X, padx=10, pady=3)
        ttk.Button(nav_frame, text="Ekwipunek", style="Fantasy.TButton", command=self.show_equipment).pack(fill=tk.X, padx=10, pady=3)
        ttk.Button(nav_frame, text="Sklep Fantasy", style="Fantasy.TButton", command=self.show_fantasy_shop).pack(fill=tk.X, padx=10, pady=3)
        ttk.Button(nav_frame, text="Budowle (Pasywne)", style="Fantasy.TButton", command=self.show_buildings_shop).pack(fill=tk.X, padx=10, pady=3)
        ttk.Button(nav_frame, text="Dziennik Zadań", style="Fantasy.TButton", command=self.show_quests).pack(fill=tk.X, padx=10, pady=3)
        ttk.Button(nav_frame, text="Bestiariusz", style="Fantasy.TButton", command=self.show_bestiary).pack(fill=tk.X, padx=10, pady=3)
        ttk.Button(nav_frame, text="Kowal (Ulepszenia)", style="Fantasy.TButton", command=self.show_blacksmith).pack(fill=tk.X, padx=10, pady=3)
        ttk.Button(nav_frame, text="Miasto (Tawerna)", style="Fantasy.TButton", command=self.show_tavern).pack(fill=tk.X, padx=10, pady=3)
        ttk.Button(nav_frame, text="🛠 DEBUG KONSOLA", style="Danger.TButton", command=self.open_debug_console).pack(fill=tk.X, padx=10, pady=3)
        ttk.Button(nav_frame, text="Zapisz i Wyjdź", style="Danger.TButton", command=self.save_and_quit).pack(fill=tk.X, padx=10, pady=15)
        
        main_area = tk.Frame(self.container, bg="#000000")
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.view_panel = tk.Frame(main_area, bg="black")
        self.view_panel.pack(fill=tk.BOTH, expand=True)
        
        log_frame = tk.Frame(main_area, height=130, bd=5, relief=tk.SUNKEN)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X)
        log_frame.pack_propagate(False)
        self.log_text = scrolledtext.ScrolledText(log_frame, bg="#0d0d0d", fg="#a8ff9e", font=("Consolas", 10, "bold"), state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.update_sidebar()
        self.log_msg(f"Witaj, {self.player.name}! Wybierz opcję z pergaminowego menu po lewej.")
        self.show_expedition()

    def update_sidebar(self):
        if not self.player: return
        t_atk = self.player.get_total_atk()
        t_def = self.player.get_total_def()
        t_hp = self.player.get_max_hp()
        
        active_c = getattr(self.player, 'active_companion', None)
        active_name = npc_lore.NPC_DB.get(active_c, {}).get('name', active_c).split(',')[0] if active_c else "Brak"
        unlocked_count = len(self.player.party)
        
        stats = f"""
✦ BOHATER ✦
Imię: {self.player.name}
Poz: {self.player.level}
EXP: {self.player.exp} / {self.player.get_exp_required()}
Złoto: {self.player.gold}
Pasywne Złoto: {self.player.stats['gold_per_sec']}/s

✦ ŻYCIE ✦
HP: {int(self.player.hp)} / {t_hp}
Mana: {int(self.player.mana)} / {self.player.max_mana}

✦ WALKA ✦
ATK: {t_atk}
DEF: {t_def}
Stat-PKT: {self.player.stat_points}

✦ DRUŻYNA (Limit 1) ✦
Aktywny: {active_name}
Zrekrutowano: {unlocked_count}/6
        """
        self.lbl_stats.config(text=stats.strip())

    def log_msg(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.update_sidebar()

    def clear_view(self):
        for widget in self.view_panel.winfo_children():
            widget.destroy()

    # ---- ZAKŁADKI ----

    def is_busy(self):
        if self.dungeon_active or self.combat_active:
            messagebox.showwarning("Zajęty", "Trwa walka lub loch! Dokończ najpierw akcję.")
            return True
        return False

    def show_expedition(self):
        if self.is_busy(): return
            
        self.clear_view()
        self.current_view = "expedition"
        self.set_background(self.view_panel, "combat")
        
        choices = combat.get_expedition_choices(self.player.level, 3)

        lbl = tk.Label(self.view_panel, text="Wybierz cel swojej wyprawy:", font=("Georgia", 20, "bold"), bg="#1a100b", fg="#f4d03f")
        lbl.place(relx=0.5, rely=0.08, anchor=tk.CENTER)
        
        cards_frame = tk.Frame(self.view_panel, bg="#1a100b")
        cards_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        for enemy in choices:
            card = tk.Frame(cards_frame, bg="#2c1a12", bd=4, relief=tk.RIDGE)
            card.pack(side=tk.LEFT, padx=15, pady=10)
            
            if hasattr(self, 'portraits') and enemy.img_key in self.portraits:
                lbl_img = tk.Label(card, image=self.portraits[enemy.img_key], bg="#2c1a12", bd=2, relief=tk.SUNKEN)
                lbl_img.pack(pady=5, padx=10)
                
            tk.Label(card, text=f"{enemy.name}", font=("Georgia", 14, "bold"), bg="#2c1a12", fg="#f4d03f", wraplength=180).pack(pady=2)
            tk.Label(card, text=f"Poziom {enemy.level}", font=("Georgia", 12, "bold"), bg="#2c1a12", fg="#aaa").pack(pady=2)
            tk.Label(card, text=f"HP: {enemy.max_hp} | ATK: {enemy.atk} | DEF: {enemy.defence}", font=("Georgia", 10), bg="#2c1a12", fg="#ddd").pack(pady=5)
            tk.Label(card, text=f"Nagroda: ~{enemy.gold_reward} Złota, ~{enemy.exp_reward} EXP", font=("Georgia", 9, "italic"), bg="#2c1a12", fg="#aaa", wraplength=180).pack(pady=5)
            
            btn = tk.Button(card, text="WALCZ", font=("Georgia", 12, "bold"), bg="#3e2723", fg="#f4d03f", 
                            activebackground="#5d4037", activeforeground="#f7dc6f", bd=4, relief=tk.RAISED,
                            command=lambda e=enemy: self.select_enemy(e))
            btn.pack(pady=10, ipadx=20, fill=tk.X)

    def select_enemy(self, enemy):
        self.enemy = enemy
        self.setup_combat_ui()
        self.start_combat()

    def setup_combat_ui(self):
        self.clear_view()
        bg_key = "combat"
        if getattr(self, 'is_dungeon_boss', False) and self.current_dungeon:
            d_bg_key = f"dungeon_{self.current_dungeon.d_id}"
            if d_bg_key in self.bg_images:
                bg_key = d_bg_key
            else:
                bg_key = "dungeon"
                
        self.set_background(self.view_panel, bg_key)
        
        self.combat_canvas = tk.Canvas(self.view_panel, width=700, height=450, bg="#111", highlightthickness=0)
        self.combat_canvas.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        
        if bg_key in self.bg_images:
            self.combat_canvas.create_image(0, 0, image=self.bg_images[bg_key], anchor=tk.NW)

        frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        frame.place(relx=0.5, rely=0.85, anchor=tk.CENTER, width=650)
        
        lbl = tk.Label(frame, text=f"Cel: {self.enemy.name} (Lvl {self.enemy.level})", font=("Georgia", 20, "bold"), bg="#2c1a12", fg="#f4d03f")
        lbl.pack(pady=10)
        
        btn_frame = tk.Frame(frame, bg="#2c1a12")
        btn_frame.pack(pady=10)
        
        self.btn_attack = tk.Button(btn_frame, text="ZACZNIJ", font=("Georgia", 16, "bold"), bg="#3e2723", fg="#f4d03f", activebackground="#5d4037", activeforeground="#f7dc6f", bd=4, relief=tk.RAISED, command=self.start_combat)
        self.btn_attack.pack(side=tk.LEFT, padx=10, ipadx=40, ipady=10)
        
        self.btn_potion = tk.Button(btn_frame, text="Wypij Miksturę", font=("Georgia", 14, "bold"), bg="#27ae60", fg="white", bd=4, relief=tk.RAISED, command=self.drink_potion)

    def drink_potion(self):
        if not self.combat_active: return
        potions = [i for i in self.player.inventory if i["id"] == "pot_hp"]
        if not potions: return
        
        self.player.inventory.remove(potions[0])
        self.player.hp = self.player.max_hp
        self.log_msg("Wypiłeś Miksturę Pełnego Zdrowia! Odzyskano 100% HP.")
        self.float_text(150, 100, "LECZYSZ SIĘ!", "#2ecc71")
        self.draw_health_bars()
        
        remaining = len(potions) - 1
        if remaining > 0:
            self.btn_potion.config(text=f"Wypij Miksturę ({remaining})")
        else:
            self.btn_potion.pack_forget()

    def flee_combat(self):
        self.combat_active = False
        self.log_msg("Uciekłeś z pola bitwy na z góry upatrzone pozycje!")
        if hasattr(self, 'btn_potion'):
            self.btn_potion.pack_forget()
        
        if getattr(self, 'is_dungeon_boss', False):
            self.is_dungeon_boss = False
            self.current_dungeon = None
            self.show_dungeons()
        else:
            self.show_expedition()

    def draw_health_bars(self):
        self.combat_canvas.delete("ui")
        
        p_max = self.player.get_max_hp()
        p_cur = self.player.hp
        e_max = self.enemy.max_hp
        
        if not hasattr(self, 'enemy_cur_hp'):
            self.enemy_cur_hp = e_max
            
        # Gracz Bar
        self.combat_canvas.create_rectangle(50, 50, 250, 75, fill="red", tags="ui")
        p_width = max(0, 200 * (p_cur / p_max))
        self.combat_canvas.create_rectangle(50, 50, 50+p_width, 75, fill="green", tags="ui")
        self.combat_canvas.create_text(150, 62, text=f"{self.player.name} HP: {int(p_cur)}/{p_max}", fill="white", font=("Georgia", 12, "bold"), tags="ui")
        
        # Wróg Bar
        self.combat_canvas.create_rectangle(450, 50, 650, 75, fill="red", tags="ui")
        e_width = max(0, 200 * (self.enemy_cur_hp / e_max))
        self.combat_canvas.create_rectangle(450, 50, 450+e_width, 75, fill="green", tags="ui")
        self.combat_canvas.create_text(550, 62, text=f"{self.enemy.name} HP: {int(self.enemy_cur_hp)}/{e_max}", fill="white", font=("Georgia", 12, "bold"), tags="ui")

    def float_text(self, x, y, text, color):
        tag = f"float_{random.randint(1000,99999)}"
        self.combat_canvas.create_text(x, y, text=text, font=("Georgia", 26, "bold"), fill=color, tags=tag)
        self.animate_float(tag, x, y, 0)

    def animate_float(self, tag, x, y, step):
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas.winfo_exists():
            return
            
        if step < 20:
            self.combat_canvas.move(tag, 0, -3)
            self.root.after(40, lambda: self.animate_float(tag, x, y, step+1))
        else:
            self.combat_canvas.delete(tag)

    def start_combat(self):
        if self.current_view not in ("expedition", "dungeon"):
            return
        if self.combat_active:
            return
            
        self.btn_attack.config(text="UCIEKNIJ Z WALKI", bg="#7a3333", fg="white", activebackground="#aa4444", activeforeground="white", command=self.flee_combat, state=tk.NORMAL)
        
        potions = len([i for i in self.player.inventory if i["id"] == "pot_hp"])
        if potions > 0:
            self.btn_potion.config(text=f"Wypij Miksturę ({potions})")
            self.btn_potion.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)
        else:
            self.btn_potion.pack_forget()
            
        self.combat_active = True
        self.enemy_cur_hp = self.enemy.max_hp
        self.combat_turn = 0
        
        self.combat_canvas.delete("portrait")
        if hasattr(self, 'portraits'):
            if "hero" in self.portraits:
                # Obramowanie na portret
                self.combat_canvas.create_rectangle(48, 98, 232, 282, fill="#f4d03f", tags=("portrait", "player_p"))
                self.combat_canvas.create_image(50, 100, image=self.portraits["hero"], anchor=tk.NW, tags=("portrait", "player_p"))
            
            # Widoczny w walce aktywny towarzysz (1 w drużynie)
            ac_id = getattr(self.player, 'active_companion', None)
            if ac_id and ac_id in self.portraits:
                ac_name = npc_lore.NPC_DB.get(ac_id, {}).get('name', ac_id).split(',')[0]
                # Obramowanie i ikona aktywnego towarzysza przy bohaterze
                self.combat_canvas.create_rectangle(248, 148, 332, 232, fill="#f4d03f", outline="#ffffff", width=2, tags=("portrait", "player_p", "companion_p"))
                if hasattr(self, 'companion_portraits') and ac_id in self.companion_portraits:
                    self.combat_canvas.create_image(250, 150, image=self.companion_portraits[ac_id], anchor=tk.NW, tags=("portrait", "player_p", "companion_p"))
                else:
                    self.combat_canvas.create_image(250, 150, image=self.portraits[ac_id], anchor=tk.NW, tags=("portrait", "player_p", "companion_p"))
                self.combat_canvas.create_text(290, 245, text=f"👥 {ac_name}", fill="#f4d03f", font=("Georgia", 9, "bold"), tags=("portrait", "player_p", "companion_p"))

            e_id = self.enemy.e_id
            if e_id in self.portraits:
                self.combat_canvas.create_rectangle(448, 98, 632, 282, fill="#f4d03f", tags=("portrait", "enemy_p"))
                self.combat_canvas.create_image(450, 100, image=self.portraits[e_id], anchor=tk.NW, tags=("portrait", "enemy_p"))
                
        self.draw_health_bars()
        self.log_msg(f"--- ROZPOCZYNASZ WALKĘ Z: {self.enemy.name} ---")
        self.root.after(350, self.combat_tick)

    def combat_tick(self):
        if not self.combat_active:
            return
            
        if self.combat_turn % 2 == 0:
            # Gracz atakuje - zacznij animację miecza
            self.animate_player_attack()
        else:
            # Wróg atakuje - zacznij animację zadrapań
            self.animate_enemy_attack()

    def rotate_point(self, x, y, cx, cy, angle_deg):
        rad = math.radians(angle_deg)
        nx = cx + (x - cx) * math.cos(rad) - (y - cy) * math.sin(rad)
        ny = cy + (x - cx) * math.sin(rad) + (y - cy) * math.cos(rad)
        return nx, ny

    def draw_sword(self, x, y, angle_deg=0):
        parts = [
            # Ostrze - dół
            ([x, y, x+100, y, x+80, y+8, x, y+8], {"fill": "#7f8c8d", "outline": "#2c3e50", "width": 2}, True),
            # Ostrze - góra
            ([x, y-8, x+80, y-8, x+100, y, x, y], {"fill": "#bdc3c7", "outline": "#2c3e50", "width": 2}, True),
            # Zbrocze
            ([x, y, x+70, y], {"fill": "#2c3e50", "width": 2}, False),
            # Jelec
            ([x-8, y-25, x, y-30, x+4, y-25, x+4, y+25, x, y+30, x-8, y+25], {"fill": "#f1c40f", "outline": "#e67e22", "width": 2}, True),
            # Klejnot
            ([x, y-5, x+5, y, x, y+5, x-5, y], {"fill": "#e74c3c", "outline": "#c0392b", "width": 2}, True),
            # Rękojeść
            ([x-35, y-5, x-8, y-5, x-8, y+5, x-35, y+5], {"fill": "#8b4513", "outline": "#5c2e0e", "width": 2}, True),
            # Oploty
            ([x-30, y-5, x-25, y+5], {"fill": "#5c2e0e", "width": 2}, False),
            ([x-25, y-5, x-20, y+5], {"fill": "#5c2e0e", "width": 2}, False),
            ([x-20, y-5, x-15, y+5], {"fill": "#5c2e0e", "width": 2}, False),
            ([x-15, y-5, x-10, y+5], {"fill": "#5c2e0e", "width": 2}, False),
            # Głowica
            ([x-45, y-5, x-40, y-8, x-35, y-5, x-35, y+5, x-40, y+8, x-45, y+5], {"fill": "#f1c40f", "outline": "#e67e22", "width": 2}, True)
        ]
        
        for coords, kwargs, is_poly in parts:
            rot_coords = []
            for i in range(0, len(coords), 2):
                nx, ny = self.rotate_point(coords[i], coords[i+1], x, y, angle_deg)
                rot_coords.extend([nx, ny])
            
            if is_poly:
                self.combat_canvas.create_polygon(*rot_coords, tags="sword", **kwargs)
            else:
                self.combat_canvas.create_line(*rot_coords, tags="sword", **kwargs)

    def animate_player_attack(self):
        # Wypad portretu gracza lekko w przód
        self.combat_canvas.move("player_p", 15, 0)
        
        # Trajektoria: start od portretu gracza (200, 170) do portretu wroga (500, 200)
        start_x, start_y = 200, 170
        target_x, target_y = 500, 200
        start_angle = -45
        end_angle = 45
        # 18 klatek przy 16ms (~60 FPS) = ok. 288ms dynamicznego lotu (40% szybciej)
        steps = 18
        
        self.animate_sword_swing(steps, steps, start_x, start_y, target_x, target_y, start_angle, end_angle)

    def animate_sword_swing(self, steps_left, total_steps, start_x, start_y, target_x, target_y, start_angle, end_angle):
        if not self.combat_active:
            self.combat_canvas.delete("sword")
            return
            
        if steps_left > 0:
            self.combat_canvas.delete("sword")
            step = (total_steps - steps_left + 1)
            t = step / total_steps
            
            # Lot po trajektorii: z X1 do X2, z delikatnym opadaniem po sinusu w stronę wroga
            curr_x = start_x + (target_x - start_x) * t
            curr_y = start_y + (target_y - start_y) * t + 25 * math.sin(t * math.pi)
            current_angle = start_angle + (end_angle - start_angle) * t
            
            self.draw_sword(curr_x, curr_y, current_angle)
            # 16ms ~ 60 FPS
            self.root.after(16, lambda: self.animate_sword_swing(steps_left - 1, total_steps, start_x, start_y, target_x, target_y, start_angle, end_angle))
        else:
            self.combat_canvas.delete("sword")
            self.combat_canvas.move("player_p", -15, 0) # Wróć portretem
            self.apply_player_damage()

    def apply_player_damage(self):
        if not self.combat_active:
            return
            
        dmg = combat.calculate_player_dmg(self.player, self.enemy)
        self.enemy_cur_hp -= dmg
        self.float_text(550, 190, f"-{dmg}", "orange")
        
        if self.enemy_cur_hp <= 0:
            self.enemy_cur_hp = 0
            self.draw_health_bars()
            self.root.after(1000, lambda: self.end_combat(True))
            return
            
        self.draw_health_bars()
        self.combat_turn += 1
        # Przerwa po udanym uderzeniu gracza przed ruchem wroga (przyspieszona o 40%)
        self.root.after(270, self.combat_tick)

    def animate_enemy_attack(self):
        # Shakes & Fidget style: Enemy lunges left
        self.combat_canvas.move("enemy_p", -30, 0)
        
        # Trzy czerwone zadrapania na portrecie gracza
        center_x, center_y = 140, 190
        self.combat_canvas.create_line(center_x-40, center_y-40, center_x+40, center_y+40, fill="#e74c3c", width=6, tags="scratch")
        self.combat_canvas.create_line(center_x-20, center_y-50, center_x+60, center_y+30, fill="#c0392b", width=6, tags="scratch")
        self.combat_canvas.create_line(center_x-60, center_y-30, center_x+20, center_y+50, fill="#e74c3c", width=6, tags="scratch")
        
        self.root.after(180, self.clear_scratch_and_apply_damage)
        
    def clear_scratch_and_apply_damage(self):
        self.combat_canvas.delete("scratch")
        self.combat_canvas.move("enemy_p", 30, 0) # Wróć portretem
        
        if not self.combat_active:
            return
            
        dmg = combat.calculate_enemy_dmg(self.enemy, self.player)
        self.player.hp -= dmg
        self.float_text(150, 190, f"-{dmg}", "red")
        
        if self.player.hp <= 0:
            self.player.hp = 0
            self.draw_health_bars()
            self.root.after(1000, lambda: self.end_combat(False))
            return
            
        self.draw_health_bars()
        self.combat_turn += 1
        # Przerwa po uderzeniu wroga przed ruchem gracza (przyspieszona o 40%)
        self.root.after(330, self.combat_tick)

    def end_combat(self, won):
        self.combat_active = False
        t_hp = self.player.get_max_hp()
        
        if not won:
            self.log_msg(f"[{self.enemy.name}] Pokonał Cię! Tracisz resztki sił.")
            self.player.hp = t_hp
            save_game(self.player, self.current_save_path)
            if hasattr(self, 'btn_attack') and self.btn_attack.winfo_exists():
                self.btn_attack.config(state=tk.NORMAL)
                
            if getattr(self, 'is_dungeon_boss', False):
                self.log_msg("Porażka z bossem lochu... Tracisz nagrodę za eksplorację!")
                self.is_dungeon_boss = False
                self.current_dungeon = None
                self.show_dungeons()
            else:
                self.show_expedition()
        else:
            bonus_pct = getattr(self.player, 'stats', {}).get('bonus_loot_pct', 0)
            mult = 1.0 + (bonus_pct / 100.0) if bonus_pct > 0 else 1.0
            
            exp_gain = int(self.enemy.exp_reward * mult)
            gold_gain = int(self.enemy.gold_reward * mult)
            
            # Krok 2 (Bestiariusz) - Zliczanie zabójstw
            e_name = self.enemy.name.replace("[BOSS] ", "")
            if not hasattr(self.player, 'bestiary'):
                self.player.bestiary = {}
            self.player.bestiary[e_name] = self.player.bestiary.get(e_name, 0) + 1
            
            # Powiadomienia o postępie w aktywnych zadaniach
            if hasattr(self.player, 'quests'):
                for q in self.player.quests:
                    if q.status == 'IN_PROGRESS':
                        if not hasattr(q, 'progress'):
                            q.progress = {'kills': {}}
                        if 'kills' not in q.progress:
                            q.progress['kills'] = {}
                            
                        # Śledzenie zabójstw konkretnych potworów
                        if 'kills' in q.requirements and e_name in q.requirements['kills']:
                            q.progress['kills'][e_name] = q.progress['kills'].get(e_name, 0) + 1
                            current = q.progress['kills'][e_name]
                            target = q.requirements['kills'][e_name]
                            if current <= target:
                                self.log_msg(f"📝 Postęp zadania '{q.name}': {e_name} {current}/{target}")
                        
                        # Złoto i level śledzimy dyskretniej, ale gdy wpadnie komplet - informujemy o ukończeniu
                        if q.check_completion(self.player):
                            self.log_msg(f"✅ ZADANIE GOTOWE: {q.name}! Odbierz nagrodę w Dzienniku Zadań.")
            
            
            self.log_msg(f"ZWYCIĘSTWO! Otrzymujesz {exp_gain} EXP i {gold_gain} Złota. (HP: {int(self.player.hp)}/{t_hp})")
            self.player.gold += gold_gain
            
            old_lvl = self.player.level
            self.player.add_exp(exp_gain)
            
            if getattr(self, 'is_dungeon_boss', False):
                d = self.current_dungeon
                d_exp = d.exp_reward
                d_gold = d.gold_reward
                
                if bonus_pct > 0:
                    d_exp = int(d_exp * mult)
                    d_gold = int(d_gold * mult)
                    
                self.log_msg(f"--- UKOŃCZONO LOCH: {d.name} ---")
                self.log_msg(f"Nagroda Dodatkowa: {d_exp} EXP oraz {d_gold} Złota.")
                self.player.gold += d_gold
                self.player.add_exp(d_exp)
                
                if random.random() < 0.25 and d.drop_pool:
                    drop_id = random.choice(d.drop_pool)
                    self.player.add_to_inventory(drop_id)
                    item = ITEMS_DB.get(drop_id)
                    if item:
                        rarity = getattr(item, 'rarity', 'Zwykły')
                        rarity_prefix = "🌟 [LEGENDARDNY] " if rarity == "Legendarny" else ("🌌 [MITYCZNY] " if rarity == "Mityczny" else "")
                        self.log_msg(f"*** {rarity_prefix}DROP Z LOCHU! Znalazłeś: {item.name} ***")
                        messagebox.showinfo(
                            "🌟 ARTEFAKT Z LOCHU! 🌟", 
                            f"Po pokonaniu bossa w lochu {d.name} odnalazłeś niezwykły artefakt!\n\nPrzedmiot: {item.name} [{rarity.upper()}]\n\n{item.description}"
                        )
                self.is_dungeon_boss = False
                self.current_dungeon = None
            else:
                # Zwykłe potwory - szansa 5% na drop mikstury życia
                if random.random() < 0.05:
                    self.player.add_to_inventory("pot_hp")
                    self.log_msg("*** DROP Z POTWORA! Znalazłeś: Mikstura Życia ***")
                
            if self.player.level > old_lvl:
                self.log_msg(f"*** AWANS NA {self.player.level} POZIOM! Otrzymujesz pasywnie bonusy do statystyk! ***")
            else:
                req = self.player.get_exp_required()
                rem = req - self.player.exp
                self.log_msg(f"(Brakuje: {rem} EXP do {self.player.level+1} poziomu)")
            
            self.player.stats["total_clicks"] += 1
            
            # Wróć do ekranu wyboru po krótkiej pauzie by gracz mógł przeczytać log
            self.root.after(2000, self.show_dungeons if self.current_view == "dungeon" else self.show_expedition)

    def show_dungeons(self):
        if self.combat_active:
            messagebox.showwarning("Zajęty", "Trwa walka! Dokończ najpierw pojedynek.")
            return

        self.clear_view()
        self.current_view = "dungeon"
            
        if self.dungeon_active and self.current_dungeon:
            # Ustawienie dedykowanego tła graficznego dla aktywnego lochu
            d_bg_key = f"dungeon_{self.current_dungeon.d_id}"
            if d_bg_key in self.bg_images:
                self.set_background(self.view_panel, d_bg_key)
            else:
                self.set_background(self.view_panel, "dungeon")
                
            # Dedykowana scena graficzna dla aktywnej wyprawy w lochu ("W PODRÓŻY")
            d = self.current_dungeon
            
            card = tk.Frame(self.view_panel, bg="#1a100b", bd=8, relief=tk.RIDGE)
            card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=650, height=480)
            
            # Kolorystyka klimatyczna dopasowana do konkretnego lochu
            theme_colors = {
                "d1": "#2ecc71", # Złowrogi Las (Szmaragdowy/Zielony)
                "d2": "#e67e22", # Opuszczona Kopalnia (Ciepła Miedź/Złoto)
                "d3": "#b833ff", # Twierdza Cieni (Mroczny Fiolet)
                "d4": "#e74c3c", # Wulkaniczne Czeluście (Czerwono-Ognisty)
                "d5": "#1abc9c", # Kryształowe Jaskinie (Turkus)
                "d6": "#3498db", # Zamarznięta Pustka (Mroźny Błękit)
                "d7": "#f1c40f", # Świątynia Upadłych Bogów (Złoty)
                "d8": "#9b59b6"  # Wymiar Czasoprzestrzeni (Astralny Fiolet)
            }
            d_color = theme_colors.get(d.d_id, "#f4d03f")
            
            tk.Label(card, text=f"⚔️ {d.name.upper()} ⚔️", font=("Georgia", 22, "bold"), fg=d_color, bg="#1a100b").pack(pady=20)
            
            # Główny napis "W PODRÓŻY" umieszczony na samym środku
            self.lbl_journey_status = tk.Label(card, text="W PODRÓŻY...", font=("Georgia", 32, "bold"), fg="#f4d03f", bg="#1a100b")
            self.lbl_journey_status.pack(pady=20)
            
            rem = max(0, d.duration - self.dungeon_time)
            self.lbl_dungeon_timer = tk.Label(card, text=f"Pozostały czas: {rem}s", font=("Georgia", 14, "bold"), fg="white", bg="#1a100b")
            self.lbl_dungeon_timer.pack(pady=5)
            
            # Pasek postępu ekspedycji
            self.dungeon_progress = ttk.Progressbar(card, orient="horizontal", length=480, mode="determinate")
            self.dungeon_progress.pack(pady=15)
            self.dungeon_progress["maximum"] = d.duration
            self.dungeon_progress["value"] = self.dungeon_time
            
            # Klimatyczny podgląd wydarzeń w tle
            self.lbl_dungeon_event = tk.Label(card, text="Drużyna powoli zagłębia się w mroczne korytarze lochu...", font=("Georgia", 11, "italic"), fg="#aaaaaa", bg="#1a100b", wraplength=550)
            self.lbl_dungeon_event.pack(pady=15)
            
            ttk.Button(card, text="Wycofaj się z lochu", style="Danger.TButton", command=self.cancel_dungeon).pack(pady=15)
            return

        # Domyślne okno wyboru lochów
        frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=600, height=450)
        
        tk.Label(frame, text="Mroczne Lochy", font=("Georgia", 22, "bold"), fg="#b833ff", bg="#2c1a12").pack(pady=10)
        
        canvas = tk.Canvas(frame, bg="#2c1a12", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2c1a12")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', on_canvas_configure)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        for d in dungeons.DUNGEONS:
            btn = ttk.Button(scrollable_frame, text=f"{d.name} (Wymaga poz. {d.level_req})", style="Fantasy.TButton", command=lambda d=d: self.start_dungeon(d))
            btn.pack(pady=10, fill=tk.X, padx=10)

    def start_dungeon(self, dungeon):
        if self.player.level < dungeon.level_req:
            messagebox.showwarning("Zbyt niski poziom", f"Potrzebujesz {dungeon.level_req} poziomu by wejść do {dungeon.name}!")
            return
            
        self.dungeon_active = True
        self.current_dungeon = dungeon
        self.dungeon_time = 0
        self.dungeon_next_flavor = 5
        self.log_msg(f"Wkroczyłeś do lochu: {dungeon.name} na {dungeon.duration} sekund!")
        self.show_dungeons()
        self.tick_dungeon()

    def tick_dungeon(self):
        if not self.dungeon_active or not self.current_dungeon:
            return
            
        self.dungeon_time += 1
        d = self.current_dungeon
        rem = max(0, d.duration - self.dungeon_time)
        
        # Animacja napisu "W PODRÓŻY..."
        dots = "." * ((self.dungeon_time % 3) + 1)
        if hasattr(self, 'lbl_journey_status') and self.lbl_journey_status.winfo_exists():
            self.lbl_journey_status.config(text=f"W PODRÓŻY{dots}")
            
        if hasattr(self, 'lbl_dungeon_timer') and self.lbl_dungeon_timer.winfo_exists():
            self.lbl_dungeon_timer.config(text=f"Pozostały czas: {rem}s")
            
        if hasattr(self, 'dungeon_progress') and self.dungeon_progress.winfo_exists():
            self.dungeon_progress["value"] = self.dungeon_time
            
        if self.dungeon_time >= self.dungeon_next_flavor:
            flavor = get_random_flavor_text(self.player.party)
            self.log_msg(f"[{self.dungeon_time}s] {flavor}")
            if hasattr(self, 'lbl_dungeon_event') and self.lbl_dungeon_event.winfo_exists():
                self.lbl_dungeon_event.config(text=f"\"{flavor}\"")
            self.dungeon_next_flavor += random.randint(10, 15)
            
        if self.dungeon_time >= d.duration:
            self.finish_dungeon()
        else:
            self.root.after(1000, self.tick_dungeon)

    def finish_dungeon(self):
        d = self.current_dungeon
        self.dungeon_active = False
        self.is_dungeon_boss = True
        
        import combat
        boss_choices = combat.get_expedition_choices(self.player.level + 5, 1)
        boss = boss_choices[0]
        boss.name = f"[BOSS] {boss.name}"
        boss.hp = int(boss.hp * 1.5)
        boss.max_hp = boss.hp
        boss.atk = int(boss.atk * 1.2)
        boss.exp_reward = int(boss.exp_reward * 2.5)
        boss.gold_reward = int(boss.gold_reward * 2.5)
        
        self.enemy = boss
        self.log_msg(f"--- CZAS MINĄŁ! DROGĘ ZAGRADZA CI {boss.name.upper()}! ---")
        
        self.setup_combat_ui()
        self.start_combat()

    def cancel_dungeon(self):
        self.dungeon_active = False
        self.current_dungeon = None
        self.log_msg("Uciekłeś z lochu w strachu. Brak nagród.")
        self.show_dungeons()

    def show_stats(self):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "stats"
        self.set_background(self.view_panel, "menu")
        frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=500, height=350)
        
        tk.Label(frame, text="Ołtarz Bohaterów", font=("Georgia", 22, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=15)
        lbl_pts = tk.Label(frame, text=f"Punkty do rozdania: {self.player.stat_points}", bg="#2c1a12", fg="white", font=("Georgia", 16))
        lbl_pts.pack(pady=10)
        
        def add_stat(stat_name):
            if self.player.stat_points > 0:
                if stat_name == 'bonus_loot_pct':
                    current = self.player.stats.get('bonus_loot_pct', 0)
                    if current >= 50:
                        messagebox.showinfo("Limit Osiągnięty", "Maksymalny bonus do zdobyczy z walki wynosi 50%!")
                        return
                        
                self.player.stats[stat_name] = self.player.stats.get(stat_name, 0) + 1
                self.player.stat_points -= 1
                lbl_pts.config(text=f"Punkty do rozdania: {self.player.stat_points}")
                self.update_sidebar()
                
        ttk.Button(frame, text="+1 Baza ATK", style="Fantasy.TButton", command=lambda: add_stat('base_atk')).pack(fill=tk.X, padx=80, pady=10)
        ttk.Button(frame, text="+1 Baza DEF", style="Fantasy.TButton", command=lambda: add_stat('base_def')).pack(fill=tk.X, padx=80, pady=10)
        ttk.Button(frame, text="+1% Zdobyczy z Walki (Max 50%)", style="Fantasy.TButton", command=lambda: add_stat('bonus_loot_pct')).pack(fill=tk.X, padx=80, pady=10)

    def show_equipment(self, selected_item_dict=None, is_equipped_slot=None):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "equipment"
        self.set_background(self.view_panel, "menu")
        
        main_frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=760, height=570)
        
        # Lewy panel - Założony sprzęt i Siatka Plecaka
        left_panel = tk.Frame(main_frame, bg="#2c1a12", width=420)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(left_panel, text="Założony Ekwipunek", font=("Georgia", 14, "bold"), bg="#2c1a12", fg="#f4d03f").pack(anchor=tk.W, pady=2)
        
        # Rząd 4 założonych slotów
        eq_slots_frame = tk.Frame(left_panel, bg="#1a100b", bd=2, relief=tk.SUNKEN)
        eq_slots_frame.pack(fill=tk.X, pady=5)
        
        slot_names = {"weapon": "Broń", "armor": "Zbroja", "helmet": "Hełm", "accessory": "Amulet"}
        
        # Jeśli nic nie wybrane, domyślnie wybierz pierwszy z założonych lub pierwszy z plecaka
        if selected_item_dict is None:
            for s_dict in self.player.equipment.values():
                if s_dict:
                    selected_item_dict = s_dict
                    break
            if selected_item_dict is None and self.player.inventory:
                selected_item_dict = self.player.inventory[0]

        self.equipment_slot_widgets = {}
        for slot_key, slot_label in slot_names.items():
            slot_box = tk.Frame(eq_slots_frame, bg="#2c1a12", bd=2, relief=tk.RAISED, width=85, height=90)
            slot_box.pack(side=tk.LEFT, padx=6, pady=6)
            slot_box.pack_propagate(False)
            
            # Rejestracja widgetu slotu do Drag & Drop
            # Ponieważ puszczenie myszy nad np. labelem też ma działać, będziemy wędrować w górę masterów
            self.root.update_idletasks() # upewnijmy sie ze id dziala
            self.equipment_slot_widgets[slot_box] = slot_key
            
            tk.Label(slot_box, text=slot_label, font=("Georgia", 9, "bold"), bg="#2c1a12", fg="#aaa").pack(pady=2)
            
            eq_item_dict = self.player.equipment.get(slot_key)
            if eq_item_dict and eq_item_dict["id"] in ITEMS_DB:
                item = ITEMS_DB[eq_item_dict["id"]]
                is_leg = getattr(item, 'rarity', 'Zwykły') == "Legendarny"
                border_col = "#f4d03f" if is_leg else "#3498db"
                
                icon_btn = tk.Canvas(slot_box, width=54, height=54, bg="#111", highlightbackground=border_col, highlightthickness=2, cursor="hand2")
                icon_btn.pack(pady=2)
                
                if hasattr(self, 'item_icons') and eq_item_dict["id"] in self.item_icons:
                    icon_btn.create_image(27, 27, image=self.item_icons[eq_item_dict["id"]])
                else:
                    icon_btn.create_text(27, 27, text=item.name[:2], fill=border_col, font=("Georgia", 12, "bold"))
                
                lvl = eq_item_dict.get('lvl', 0)
                if lvl > 0:
                    icon_btn.create_text(40, 40, text=f"+{lvl}", fill="#2ecc71", font=("Arial", 9, "bold"))
                    
                icon_btn.bind("<Button-1>", lambda e, item_d=eq_item_dict, s_key=slot_key: self.show_equipment(item_d, is_equipped_slot=s_key))
            else:
                empty_lbl = tk.Label(slot_box, text="[ Puste ]", font=("Georgia", 9, "italic"), bg="#2c1a12", fg="#666")
                empty_lbl.pack(expand=True)

        tk.Label(left_panel, text="Plecak (Przeciągnij by założyć)", font=("Georgia", 12, "bold"), bg="#2c1a12", fg="#f4d03f").pack(anchor=tk.W, pady=(10, 2))
        
        sf = ScrollableFrame(left_panel, bg_color="#1a100b")
        sf.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Funkcje Drag & Drop
        self.drag_phantom = None
        self.drag_item_dict = None
        
        def on_drag_start(event, item_dict):
            # Zabezpieczenie przed wiszacymi zjawami z poprzednich widoków
            if hasattr(self, 'drag_phantom') and self.drag_phantom:
                try:
                    self.drag_phantom.destroy()
                except:
                    pass
                
            self.drag_item_dict = item_dict
            # UWAGA: Usunięto wywoływanie show_equipment() tutaj! Zmieniało to całkowicie okno, kasowało stare kafelki 
            # i urywało eventy myszy powodując zatrzymanie się zjaw na ekranie na stałe.
            
            self.drag_phantom = tk.Toplevel(self.root)
            self.drag_phantom.overrideredirect(True)
            self.drag_phantom.attributes("-topmost", True)
            self.drag_phantom.attributes("-alpha", 0.8) # Lekka przezroczystość (zjawa)
            
            item = ITEMS_DB.get(item_dict["id"])
            if hasattr(self, 'item_icons') and item_dict["id"] in self.item_icons:
                lbl = tk.Label(self.drag_phantom, image=self.item_icons[item_dict["id"]], bg="#111", bd=2, relief=tk.RAISED)
            else:
                lbl = tk.Label(self.drag_phantom, text=item.name[:4], font=("Georgia", 10, "bold"), bg="#111", fg="#f4d03f", bd=2, relief=tk.RAISED)
            lbl.pack()
            
            self.drag_phantom.geometry(f"+{event.x_root + 15}+{event.y_root + 15}")
            
            # Jesli kursor wjedzie na zjawe, niech zjawa przesyla puszczenie przycisku i ruch dalej!
            self.drag_phantom.bind("<B1-Motion>", on_drag_motion)
            self.drag_phantom.bind("<ButtonRelease-1>", on_drag_release)

        def on_drag_motion(event):
            if hasattr(self, 'drag_phantom') and self.drag_phantom:
                self.drag_phantom.geometry(f"+{event.x_root + 15}+{event.y_root + 15}")

        def on_drag_release(event):
            # Zniszcz najpierw zjawę, aby nie zasłaniała interfejsu przy pytaniu "co jest pod myszką"
            if hasattr(self, 'drag_phantom') and self.drag_phantom:
                try:
                    self.drag_phantom.destroy()
                except:
                    pass
                self.drag_phantom = None
                
            if not getattr(self, 'drag_item_dict', None):
                return
                
            target_widget = self.root.winfo_containing(event.x_root, event.y_root)
            
            # Wspinamy się po drzewie widgetów by sprawdzić czy jesteśmy w slot_box
            w = target_widget
            found_slot = None
            while w:
                if w in self.equipment_slot_widgets:
                    found_slot = self.equipment_slot_widgets[w]
                    break
                w = getattr(w, 'master', None)
                
            if found_slot:
                item = ITEMS_DB.get(self.drag_item_dict["id"])
                if item and getattr(item, "slot", None) == found_slot:
                    if self.player.equip(self.drag_item_dict):
                        self.log_msg(f"Założono: {item.name}")
                        self.update_sidebar()
                        self.show_equipment(self.drag_item_dict, is_equipped_slot=found_slot)
                        self.drag_item_dict = None
                        return
                else:
                    self.log_msg("To złe miejsce na ten przedmiot!")
            
            # Jeśli nie upuszczono na slot - traktuj to jak normalne kliknięcie by otworzyć menu przedmiotu po prawej!
            item_to_show = self.drag_item_dict
            self.drag_item_dict = None
            self.show_equipment(item_to_show, is_equipped_slot=None)

        if not self.player.inventory:
            tk.Label(sf.scrollable_frame, text="Twój plecak jest pusty.", font=("Georgia", 11, "italic"), bg="#1a100b", fg="gray").pack(pady=30)
        else:
            grid_frame = tk.Frame(sf.scrollable_frame, bg="#1a100b")
            grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            cols = 5
            for idx, inv_item_dict in enumerate(self.player.inventory):
                item = ITEMS_DB.get(inv_item_dict["id"])
                if not item: continue
                
                r, c = divmod(idx, cols)
                
                is_leg = getattr(item, 'rarity', 'Zwykły') == "Legendarny"
                border_col = "#f4d03f" if is_leg else "#7f8c8d"
                is_selected = (inv_item_dict == selected_item_dict and is_equipped_slot is None)
                bg_highlight = "#5d4037" if is_selected else "#2c1a12"
                
                tile = tk.Frame(grid_frame, bg=bg_highlight, bd=2, relief=tk.RAISED, width=72, height=78, cursor="hand2")
                tile.grid(row=r, column=c, padx=4, pady=4)
                tile.grid_propagate(False)
                
                icon_canvas = tk.Canvas(tile, width=50, height=50, bg="#111", highlightbackground=border_col, highlightthickness=2)
                icon_canvas.pack(pady=3)
                
                if hasattr(self, 'item_icons') and inv_item_dict["id"] in self.item_icons:
                    icon_canvas.create_image(25, 25, image=self.item_icons[inv_item_dict["id"]])
                else:
                    icon_canvas.create_text(25, 25, text=item.name[:2], fill=border_col, font=("Georgia", 10, "bold"))
                
                lvl = inv_item_dict.get('lvl', 0)
                if lvl > 0:
                    icon_canvas.create_text(35, 35, text=f"+{lvl}", fill="#2ecc71", font=("Arial", 9, "bold"))
                
                lvl_str = f" +{lvl}" if lvl > 0 else ""
                name_short = item.name if len(item.name) <= 6 else item.name[:5] + "…"
                lbl_n = tk.Label(tile, text=name_short + lvl_str, font=("Georgia", 7, "bold"), bg=bg_highlight, fg=border_col)
                lbl_n.pack()
                
                # Bindowanie zdarzeń do wszystkich elementów płytki plecaka
                for widget in (tile, icon_canvas, lbl_n):
                    widget.bind("<ButtonPress-1>", lambda e, item_d=inv_item_dict: on_drag_start(e, item_d))
                    widget.bind("<B1-Motion>", on_drag_motion)
                    widget.bind("<ButtonRelease-1>", on_drag_release)

        # Prawy panel - Inspektor Szczegółów Przedmiotu
        right_panel = tk.Frame(main_frame, bg="#1a100b", width=310, bd=4, relief=tk.RIDGE)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        right_panel.pack_propagate(False)
        
        if selected_item_dict and selected_item_dict["id"] in ITEMS_DB:
            item = ITEMS_DB[selected_item_dict["id"]]
            lvl = selected_item_dict.get('lvl', 0)
            is_leg = getattr(item, 'rarity', 'Zwykły') == "Legendarny"
            rarity_text = "🌟 LEGENDARDNY ARTEFAKT" if is_leg else "PRZEDMIOT PODSTAWOWY"
            rarity_color = "#f4d03f" if is_leg else "#aaa"
            
            tk.Label(right_panel, text=rarity_text, font=("Georgia", 10, "bold"), fg=rarity_color, bg="#1a100b").pack(pady=(12, 2))
            lvl_suffix = f" +{lvl}" if lvl > 0 else ""
            tk.Label(right_panel, text=item.name + lvl_suffix, font=("Georgia", 14, "bold"), fg="white", bg="#1a100b", wraplength=280, justify=tk.CENTER).pack(pady=2)
            
            # Duża ikona przedmiotu
            img_box = tk.Canvas(right_panel, width=120, height=120, bg="#0d0d0d", highlightbackground=rarity_color, highlightthickness=3)
            img_box.pack(pady=8)
            
            if hasattr(self, 'item_icons_large') and selected_item_dict["id"] in self.item_icons_large:
                img_box.create_image(60, 60, image=self.item_icons_large[selected_item_dict["id"]])
            else:
                img_box.create_text(60, 60, text=item.name[:4], fill=rarity_color, font=("Georgia", 18, "bold"))
                
            # Statystyki i typ
            slot_name = slot_names.get(getattr(item, 'slot', 'weapon'), 'Przedmiot')
            req_lvl = getattr(item, 'level_req', 1)
            tk.Label(right_panel, text=f"Typ: {slot_name} | Wymaga poz. {req_lvl}", font=("Georgia", 10, "italic"), fg="#ccc", bg="#1a100b").pack()
            
            sell_price = max(1, int(item.value * 0.10) + (lvl * 50))
            if hasattr(item, 'stats'):
                stat_str = ", ".join([f"{k.upper()}: +{int(v * (1.0 + 0.15 * lvl))}" for k, v in item.stats.items()])
                tk.Label(right_panel, text=f"Statystyki: {stat_str}", font=("Georgia", 11, "bold"), fg="#a8ff9e", bg="#1a100b").pack(pady=4)
            elif hasattr(item, 'effect'):
                eff_str = ", ".join([f"{k.upper()}: {v}" for k, v in item.effect.items()])
                tk.Label(right_panel, text=f"Efekt: {eff_str}", font=("Georgia", 11, "bold"), fg="#3498db", bg="#1a100b").pack(pady=4)
                
            tk.Label(right_panel, text=f"Wartość: {item.value}g | Sprzedaż: {sell_price}g", font=("Georgia", 10, "bold"), fg="#f4d03f", bg="#1a100b").pack()
            
            # Opis / Historia
            desc_box = scrolledtext.ScrolledText(right_panel, bg="#2c1a12", fg="#ddd", font=("Georgia", 9), wrap=tk.WORD, height=5, bd=3, relief=tk.SUNKEN)
            desc_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
            desc_box.insert(tk.END, item.description)
            desc_box.config(state=tk.DISABLED)
            
            # Przyciski akcji (Załóż / Zdejmij / Sprzedaj / Użyj)
            btn_box = tk.Frame(right_panel, bg="#1a100b")
            btn_box.pack(fill=tk.X, pady=6, padx=5)
            
            if is_equipped_slot:
                def unequip_action():
                    slot = is_equipped_slot
                    if self.player.equipment[slot]:
                        self.player.inventory.append(self.player.equipment[slot])
                        self.player.equipment[slot] = None
                        self.log_msg(f"Zdjęto przedmiot: {item.name}")
                        self.update_sidebar()
                        self.show_equipment()
                ttk.Button(btn_box, text="Zdejmij Przedmiot", style="Danger.TButton", command=unequip_action).pack(fill=tk.X, pady=2)
            else:
                def equip_action():
                    if self.player.equip(selected_item_dict):
                        self.log_msg(f"Założono przedmiot: {item.name}")
                        self.update_sidebar()
                        self.show_equipment(selected_item_dict, is_equipped_slot=getattr(item, 'slot', None))
                        
                def use_action():
                    if selected_item_dict in self.player.inventory:
                        if hasattr(item, 'effect') and 'heal' in item.effect:
                            heal_amt = item.effect['heal']
                            old_hp = self.player.hp
                            t_hp = self.player.get_max_hp()
                            self.player.hp = min(self.player.hp + heal_amt, t_hp)
                            self.log_msg(f"Wypito {item.name}! Odzyskano {int(self.player.hp - old_hp)} HP.")
                        self.player.inventory.remove(selected_item_dict)
                        self.update_sidebar()
                        self.show_equipment()
                    
                def sell_action():
                    if selected_item_dict in self.player.inventory:
                        self.player.inventory.remove(selected_item_dict)
                        self.player.gold += sell_price
                        self.log_msg(f"Sprzedano {item.name} za {sell_price} złota.")
                        self.update_sidebar()
                        self.show_equipment()
                        
                if hasattr(item, 'slot'):
                    ttk.Button(btn_box, text="Załóż Przedmiot", style="Fantasy.TButton", command=equip_action).pack(fill=tk.X, pady=2)
                elif hasattr(item, 'effect'):
                    ttk.Button(btn_box, text="Użyj Przedmiotu", style="Fantasy.TButton", command=use_action).pack(fill=tk.X, pady=2)
                    
                ttk.Button(btn_box, text=f"💰 Sprzedaj ({sell_price}g)", style="Danger.TButton", command=sell_action).pack(fill=tk.X, pady=2)
        else:
            tk.Label(right_panel, text="Brak Wyboru", font=("Georgia", 14, "bold"), fg="#aaa", bg="#1a100b").pack(pady=40)
            tk.Label(right_panel, text="Kliknij dowolny przedmiot w plecaku lub założonym ekwipunku, aby wyświetlić szczegóły i historię.", font=("Georgia", 10, "italic"), fg="#888", bg="#1a100b", wraplength=250, justify=tk.CENTER).pack(padx=15)

    def show_fantasy_shop(self, selected_tier=1):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "fantasy_shop"
        self.set_background(self.view_panel, "menu")
        
        frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=760, height=570)
        
        tk.Label(frame, text="⚔️ SKLEP FANTASY ⚔️", font=("Georgia", 22, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=(12, 2))
        tk.Label(frame, text=f"Twoje złoto: {self.player.gold}g | Twój Poziom: {self.player.level}", font=("Georgia", 12, "bold"), bg="#2c1a12", fg="white").pack(pady=2)
        
        # Pasek wyboru kategorii / stron poziomowych (Tiers Tabs)
        tabs_frame = tk.Frame(frame, bg="#1a100b", bd=2, relief=tk.SUNKEN)
        tabs_frame.pack(fill=tk.X, padx=15, pady=8)
        
        for tier_id, t_data in self.fantasy_shop.tiers.items():
            is_active = (tier_id == selected_tier)
            is_locked = (self.player.level < t_data["req_level"])
            
            # Kolory zakładki
            if is_active:
                bg_col = "#f4d03f"
                fg_col = "#1a100b"
            elif is_locked:
                bg_col = "#2a1610"
                fg_col = "#888888"
            else:
                bg_col = "#3e2723"
                fg_col = "#f4d03f"
                
            btn_text = f"🔒 {t_data['label']}" if is_locked else t_data['label']
            
            btn = tk.Button(
                tabs_frame, 
                text=btn_text, 
                font=("Georgia", 10, "bold"), 
                bg=bg_col, 
                fg=fg_col, 
                activebackground="#5d4037",
                bd=2, 
                relief=tk.RAISED if not is_active else tk.SUNKEN,
                command=lambda tid=tier_id: self.show_fantasy_shop(selected_tier=tid)
            )
            btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=3)

        # Informacja o wybranym zestawi
        current_tier = self.fantasy_shop.tiers.get(selected_tier, self.fantasy_shop.tiers[1])
        tier_title = f"{current_tier['name']} ({current_tier['label']})"
        req_lvl = current_tier['req_level']
        
        sub_info = tk.Frame(frame, bg="#2c1a12")
        sub_info.pack(fill=tk.X, padx=20, pady=2)
        tk.Label(sub_info, text=f"Kategoria: {tier_title}", font=("Georgia", 13, "bold"), bg="#2c1a12", fg="#f4d03f").pack(side=tk.LEFT)
        
        if self.player.level < req_lvl:
            tk.Label(sub_info, text=f"🔒 Wymagany {req_lvl} poziom bohatera", font=("Georgia", 11, "bold"), bg="#2c1a12", fg="#ff6666").pack(side=tk.RIGHT)
        else:
            tk.Label(sub_info, text="✅ Odblokowano", font=("Georgia", 11, "bold"), bg="#2c1a12", fg="#2ecc71").pack(side=tk.RIGHT)

        sf = ScrollableFrame(frame, bg_color="#1a100b")
        sf.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)
        
        for item_id in current_tier["items"]:
            item = ITEMS_DB.get(item_id)
            if not item: continue
            
            row = tk.Frame(sf.scrollable_frame, bg="#2c1a12", bd=2, relief=tk.RIDGE)
            row.pack(fill=tk.X, padx=5, pady=5)
            
            # Ikona przedmiotu
            icon_canvas = tk.Canvas(row, width=54, height=54, bg="#111", highlightbackground="#f4d03f", highlightthickness=2)
            icon_canvas.pack(side=tk.LEFT, padx=10, pady=8)
            
            if hasattr(self, 'item_icons') and item_id in self.item_icons:
                icon_canvas.create_image(27, 27, image=self.item_icons[item_id])
            else:
                icon_canvas.create_text(27, 27, text=item.name[:2], fill="#f4d03f", font=("Georgia", 12, "bold"))
                
            info = tk.Frame(row, bg="#2c1a12")
            info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)
            
            title_color = "white" if self.player.level >= req_lvl else "#ffaaaa"
            tk.Label(info, text=item.name, font=("Georgia", 13, "bold"), bg="#2c1a12", fg=title_color).pack(anchor=tk.W)
            
            if hasattr(item, 'stats'):
                stat_str = ", ".join([f"{k.upper()}: +{v}" for k, v in item.stats.items()])
                tk.Label(info, text=f"Statystyki: {stat_str}", font=("Georgia", 10, "bold"), bg="#2c1a12", fg="#a8ff9e").pack(anchor=tk.W)
            elif hasattr(item, 'effect'):
                eff_str = ", ".join([f"{k.upper()}: {v}" for k, v in item.effect.items()])
                tk.Label(info, text=f"Efekt: {eff_str}", font=("Georgia", 10, "bold"), bg="#2c1a12", fg="#3498db").pack(anchor=tk.W)
                
            tk.Label(info, text=item.description, font=("Georgia", 9, "italic"), bg="#2c1a12", fg="#aaaaaa", wraplength=380, justify=tk.LEFT).pack(anchor=tk.W)
            
            # Dynamiczna cena dla mikstur
            price = item.value
            if item_id == "pot_hp":
                price = int(50 + (self.player.level ** 1.3) * 15)
                
            if self.player.level >= req_lvl:
                ttk.Button(
                    row, 
                    text=f"Kup ({price}g)", 
                    style="Fantasy.TButton", 
                    command=lambda i=item_id, s_tier=selected_tier, p=price: self.buy_fantasy_item(i, s_tier, p)
                ).pack(side=tk.RIGHT, padx=15, pady=10)
            else:
                tk.Label(row, text=f"🔒 Poz. {req_lvl}", font=("Georgia", 12, "bold"), bg="#2c1a12", fg="#ff6666").pack(side=tk.RIGHT, padx=15, pady=10)

    def buy_fantasy_item(self, item_id, selected_tier=1, override_price=None):
        item = ITEMS_DB.get(item_id)
        if not item: return
        req_lvl = getattr(item, 'level_req', 1)
        if self.player.level < req_lvl:
            messagebox.showwarning("Zbyt Niski Poziom", f"Wymagany jest {req_lvl} poziom, aby kupić {item.name}!")
            return
        price = override_price if override_price is not None else item.value
            
        if self.player.gold >= price:
            self.player.gold -= price
            self.player.add_to_inventory(item_id)
            self.log_msg(f"Zakupiono wspaniały przedmiot: {item.name}!")
            self.update_sidebar()
            self.show_fantasy_shop(selected_tier=selected_tier)
        else:
            messagebox.showwarning("Brak Złota", f"Potrzebujesz {price} złota, aby kupić {item.name}!")

    def show_buildings_shop(self):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "buildings_shop"
        self.set_background(self.view_panel, "menu")
        frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=700, height=550)
        
        tk.Label(frame, text="MIASTO (Pasywne Złoto)", font=("Georgia", 22, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=10)
        
        sf = ScrollableFrame(frame, bg_color="#3e2723")
        sf.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for b_id, b in self.market.buildings.items():
            cost = self.market.get_cost(self.player, b_id)
            owned = self.player.buildings.get(b_id, 0)
            
            row = tk.Frame(sf.scrollable_frame, bg="#3e2723", bd=1, relief=tk.SOLID)
            row.pack(fill=tk.X, padx=5, pady=5)
            
            info = tk.Frame(row, bg="#3e2723")
            info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            tk.Label(info, text=f"{b.name} (Złoto/s: +{b.gold_per_sec})", font=("Georgia", 14, "bold"), bg="#3e2723", fg="white").pack(anchor=tk.W)
            tk.Label(info, text=b.description, font=("Georgia", 10), bg="#3e2723", fg="#aaaaaa", wraplength=400, justify=tk.LEFT).pack(anchor=tk.W)
            tk.Label(info, text=f"Posiadasz: {owned}", font=("Georgia", 10, "italic"), bg="#3e2723", fg="gold").pack(anchor=tk.W)
            
            ttk.Button(row, text=f"Kup ({cost}g)", style="Fantasy.TButton", command=lambda bid=b_id: self.buy_building(bid)).pack(side=tk.RIGHT, padx=10, pady=10)

    def buy_building(self, b_id):
        if self.market.buy_building(self.player, b_id):
            self.log_msg(f"Wzniesiono nową budowlę: {self.market.buildings[b_id].name}")
            self.show_buildings_shop()
        else:
            messagebox.showwarning("Brak Złota", "Skarbiec świeci pustkami!")

    def show_quests(self):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "quests"
        self.set_background(self.view_panel, "menu")
        frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=700, height=600)
        
        tk.Label(frame, text="DZIENNIK ZADAŃ", font=("Georgia", 22, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=10)
        
        sf = ScrollableFrame(frame, bg_color="#3e2723")
        sf.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Aktualizacja statusów
        for q in self.player.quests:
            q.update_status(self.player.level)
            
        for q in self.player.quests:
            row = tk.Frame(sf.scrollable_frame, bg="#3e2723", bd=1, relief=tk.SOLID)
            row.pack(fill=tk.X, padx=5, pady=5)
            
            info = tk.Frame(row, bg="#3e2723")
            info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Formatowanie czytelnego opisu nagród
            reward_parts = []
            if 'gold' in q.rewards:
                reward_parts.append(f"💰 +{q.rewards['gold']}g Złota")
            if 'item' in q.rewards:
                item = ITEMS_DB.get(q.rewards['item'])
                if item:
                    is_leg = getattr(item, 'rarity', 'Zwykły') == "Legendarny"
                    icon = "🌟 " if is_leg else "🛡️ "
                    reward_parts.append(f"{icon}Przedmiot: {item.name}")
            if 'party' in q.rewards:
                npc_id = q.rewards['party']
                npc_name = npc_lore.NPC_DB.get(npc_id, {}).get('name', npc_id).split(',')[0]
                reward_parts.append(f"👥 Towarzysz: Dołącza {npc_name}")
            reward_str = " | ".join(reward_parts) if reward_parts else "Brak"
            
            if q.status == 'LOCKED':
                tk.Label(info, text=f"🔒 {q.name} (Zablokowane Zadanie)", font=("Georgia", 13, "bold"), bg="#3e2723", fg="#888888").pack(anchor=tk.W)
                tk.Label(info, text=f"Wymagany {q.unlock_level} poziom bohatera | Nagroda: {reward_str}", font=("Georgia", 9, "italic"), bg="#3e2723", fg="#aaaaaa").pack(anchor=tk.W)
            else:
                color = "#f4d03f" if q.status == 'COMPLETED' else "white"
                tk.Label(info, text=q.name, font=("Georgia", 14, "bold"), bg="#3e2723", fg=color).pack(anchor=tk.W)
                tk.Label(info, text=q.description, font=("Georgia", 10), bg="#3e2723", fg="#cccccc", wraplength=450, justify=tk.LEFT).pack(anchor=tk.W)
                tk.Label(info, text=f"🎁 Nagroda: {reward_str}", font=("Georgia", 10, "bold"), bg="#3e2723", fg="#f4d03f", wraplength=450, justify=tk.LEFT).pack(anchor=tk.W, pady=(3, 1))
                
                # Stan tekstowy zadania
                status_texts = {
                    'AVAILABLE': "Status: Oczekujące (Zlecenie dostępne do przyjęcia)",
                    'IN_PROGRESS': "Status: W trakcie wykonywania...",
                    'COMPLETED': "Status: Zakończone sukcesem! (Odbierz nagrodę)",
                    'CLAIMED': "Status: Odebrano (Zadanie ukończone)"
                }
                tk.Label(info, text=status_texts[q.status], font=("Georgia", 9, "italic"), bg="#3e2723", fg="#aaaaaa").pack(anchor=tk.W)
                
                if q.status == 'AVAILABLE':
                    ttk.Button(row, text="Przyjmij", style="Fantasy.TButton", command=lambda q=q: self.accept_quest(q)).pack(side=tk.RIGHT, padx=10, pady=10)
                elif q.status == 'COMPLETED':
                    ttk.Button(row, text="Odbierz", style="Fantasy.TButton", command=lambda q=q: self.claim_quest(q)).pack(side=tk.RIGHT, padx=10, pady=10)
                elif q.status == 'CLAIMED':
                    tk.Label(row, text="✔", font=("Georgia", 24), bg="#3e2723", fg="green").pack(side=tk.RIGHT, padx=15, pady=10)

    def accept_quest(self, quest):
        if quest.accept():
            self.log_msg(f"Przyjęto zadanie: {quest.name}")
            self.show_quests()

    def claim_quest(self, quest):
        if quest.claim_reward(self.player):
            self.log_msg(f"Odebrano nagrodę za: {quest.name}!")
            self.show_quests()

    def show_bestiary(self):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "bestiary"
        self.set_background(self.view_panel, "menu")
        frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=700, height=600)
        
        tk.Label(frame, text="BESTIARIUSZ (Kolekcjoner Dusz)", font=("Georgia", 22, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=10)
        
        if not hasattr(self.player, 'bestiary'):
            self.player.bestiary = {}
            
        bonus_val = int(self.player.get_bestiary_bonus() * 100)
        tk.Label(frame, text=f"Pasywny Bonus Obrażeń: +{bonus_val}% (Maks. 100%)", font=("Georgia", 14, "bold"), bg="#2c1a12", fg="#2ecc71").pack(pady=5)
        tk.Label(frame, text="Każde 50 pokonanych potworów daje +1% do wszystkich Twoich obrażeń.", font=("Georgia", 10, "italic"), bg="#2c1a12", fg="#ccc").pack(pady=5)
        
        sf = ScrollableFrame(frame, bg_color="#3e2723")
        sf.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        if not self.player.bestiary:
            tk.Label(sf.scrollable_frame, text="Twój bestiariusz jest póki co pusty...\nWyrusz w świat by polować na potwory!", font=("Georgia", 14, "italic"), bg="#3e2723", fg="#aaaaaa").pack(pady=50)
            return
            
        # Posortowane malejąco po ilości zabić
        sorted_bestiary = sorted(self.player.bestiary.items(), key=lambda x: x[1], reverse=True)
        
        for name, count in sorted_bestiary:
            row = tk.Frame(sf.scrollable_frame, bg="#3e2723", bd=1, relief=tk.SOLID)
            row.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Label(row, text=name, font=("Georgia", 16, "bold"), bg="#3e2723", fg="#f4d03f").pack(side=tk.LEFT, padx=20, pady=15)
            tk.Label(row, text=f"Pokonano: {count}x", font=("Georgia", 16, "bold"), bg="#3e2723", fg="white").pack(side=tk.RIGHT, padx=20, pady=15)

    def show_blacksmith(self):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "blacksmith"
        self.set_background(self.view_panel, "menu")
        
        main_frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=760, height=570)
        
        tk.Label(main_frame, text="KUŹNIA BOHATERÓW", font=("Georgia", 22, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=10)
        tk.Label(main_frame, text="Wybierz przedmiot z plecaka, by przekuć go i ulepszyć (+15% bazowych statystyk za poziom).", font=("Georgia", 11, "italic"), bg="#2c1a12", fg="#ccc").pack(pady=5)
        tk.Label(main_frame, text=f"Twoje złoto: {self.player.gold}g", font=("Georgia", 14, "bold"), bg="#2c1a12", fg="gold").pack(pady=5)
        
        sf = ScrollableFrame(main_frame, bg_color="#1a100b")
        sf.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Zbieramy wszystkie przedmioty (założone i te w plecaku)
        all_items = []
        for slot, item_dict in self.player.equipment.items():
            if item_dict:
                all_items.append((item_dict, f"[Założone]"))
        for item_dict in self.player.inventory:
            all_items.append((item_dict, "[Plecak]"))
            
        if not all_items:
            tk.Label(sf.scrollable_frame, text="Nie masz żadnych przedmiotów do ulepszenia.", font=("Georgia", 14, "italic"), bg="#1a100b", fg="gray").pack(pady=30)
            return
            
        for inv_item_dict, location_tag in all_items:
            item = ITEMS_DB.get(inv_item_dict["id"])
            if not item or not hasattr(item, 'stats'): continue
            
            row = tk.Frame(sf.scrollable_frame, bg="#3e2723", bd=2, relief=tk.RAISED)
            row.pack(fill=tk.X, padx=10, pady=5)
            
            lvl = inv_item_dict.get('lvl', 0)
            # Koszt rośnie bazując na wartości i poziomie, mityczne przedmioty będą cholernie drogie
            cost = int(item.value * (1.5 ** lvl) * 2.5)
            if cost < 10: cost = 10
            
            def do_upgrade(i_dict=inv_item_dict, c=cost):
                if self.player.gold >= c:
                    self.player.gold -= c
                    i_dict["lvl"] = i_dict.get("lvl", 0) + 1
                    self.log_msg(f"Pomyślnie wykuto {ITEMS_DB[i_dict['id']].name} +{i_dict['lvl']}!")
                    self.update_sidebar()
                    self.show_blacksmith()
                else:
                    messagebox.showwarning("Brak Złota", "Masz za mało złota na to ulepszenie!")
                    
            # Najpierw pakujemy przycisk do prawej, by etykiety tekstowe go nie wypchnęły poza ekran!
            btn = ttk.Button(row, text=f"Ulepsz ({cost}g)", style="Fantasy.TButton", command=do_upgrade)
            btn.pack(side=tk.RIGHT, padx=15, pady=10)
            
            name_lbl = f"{item.name} +{lvl} {location_tag}" if lvl > 0 else f"{item.name} {location_tag}"
            tk.Label(row, text=name_lbl, font=("Georgia", 12, "bold"), bg="#3e2723", fg="#f4d03f").pack(side=tk.LEFT, padx=15, pady=15)
            
            next_lvl_stats = ", ".join([f"{k.upper()}: +{int(v * (1.0 + 0.15 * (lvl + 1)))}" for k, v in item.stats.items()])
            tk.Label(row, text=f"Poz. {lvl+1}: {next_lvl_stats}", font=("Georgia", 9, "italic"), bg="#3e2723", fg="#ccc", wraplength=200).pack(side=tk.LEFT, padx=5)

    def open_debug_console(self):
        if not self.player:
            messagebox.showinfo("Debug", "Najpierw rozpocznij lub wczytaj grę!")
            return
            
        win = tk.Toplevel(self.root)
        win.title("🛠 Debug Konsola / Cheaty")
        win.geometry("500x520")
        win.configure(bg="#2c1a12")
        win.transient(self.root)
        
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - win.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{x}+{y}")
        
        tk.Label(win, text="🛠 KONSOLA DEBUGOWANIA (TESTY)", font=("Georgia", 16, "bold"), fg="#f4d03f", bg="#2c1a12").pack(pady=12)
        
        btn_frame = tk.Frame(win, bg="#2c1a12")
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        
        def add_gold(amount):
            self.player.gold += amount
            self.update_sidebar()
            self.log_msg(f"[DEBUG] Dodano {amount} Złota.")
            lbl_status.config(text=f"Dodano {amount} Złota! Posiadasz: {self.player.gold}")

        def add_levels(count):
            for _ in range(count):
                req = self.player.get_exp_required()
                self.player.add_exp(req - self.player.exp)
            self.update_sidebar()
            self.log_msg(f"[DEBUG] Awansowano +{count} Poziomów. Obecny Poziom: {self.player.level}.")
            lbl_status.config(text=f"Awansowano na {self.player.level} Poziom!")

        def full_heal():
            self.player.hp = self.player.get_max_hp()
            self.player.mana = self.player.max_mana
            self.update_sidebar()
            self.log_msg("[DEBUG] Przywrócono pełne HP i Manę.")
            lbl_status.config(text="Bohater w pełni uleczony!")

        def add_stat_pts(pts):
            self.player.stat_points += pts
            self.update_sidebar()
            self.log_msg(f"[DEBUG] Dodano +{pts} Stat Points.")
            lbl_status.config(text=f"Dodano +{pts} punktów statystyk! Razem: {self.player.stat_points}")

        tk.Button(btn_frame, text="+10,000 Złota", bg="#3e2723", fg="#f4d03f", font=("Georgia", 10, "bold"), command=lambda: add_gold(10000)).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(btn_frame, text="+1,000,000 Złota", bg="#3e2723", fg="#f4d03f", font=("Georgia", 10, "bold"), command=lambda: add_gold(1000000)).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        tk.Button(btn_frame, text="+1 Level", bg="#3e2723", fg="#a8ff9e", font=("Georgia", 10, "bold"), command=lambda: add_levels(1)).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(btn_frame, text="+10 Leveli", bg="#3e2723", fg="#a8ff9e", font=("Georgia", 10, "bold"), command=lambda: add_levels(10)).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        tk.Button(btn_frame, text="Ulecz HP i Manę", bg="#3e2723", fg="#88ccff", font=("Georgia", 10, "bold"), command=full_heal).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(btn_frame, text="+50 Pkt Statystyk", bg="#3e2723", fg="#ffcc88", font=("Georgia", 10, "bold"), command=lambda: add_stat_pts(50)).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        input_frame = tk.Frame(win, bg="#1a100b", bd=3, relief=tk.GROOVE)
        input_frame.pack(fill=tk.X, padx=20, pady=10)

        # Custom Gold
        f_gold = tk.Frame(input_frame, bg="#1a100b")
        f_gold.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f_gold, text="Dodaj Złoto:", fg="white", bg="#1a100b", font=("Georgia", 10, "bold")).pack(side=tk.LEFT)
        e_gold = tk.Entry(f_gold, bg="#3e2723", fg="white", font=("Georgia", 10), width=12)
        e_gold.pack(side=tk.LEFT, padx=5)
        e_gold.insert(0, "50000")
        def set_custom_gold():
            try:
                val = int(e_gold.get())
                add_gold(val)
            except ValueError:
                lbl_status.config(text="Błąd: Podaj liczbę!")
        tk.Button(f_gold, text="Dodaj", bg="#5d4037", fg="white", command=set_custom_gold).pack(side=tk.LEFT)

        # Custom Level
        f_lvl = tk.Frame(input_frame, bg="#1a100b")
        f_lvl.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f_lvl, text="Ustaw Poziom:", fg="white", bg="#1a100b", font=("Georgia", 10, "bold")).pack(side=tk.LEFT)
        e_lvl = tk.Entry(f_lvl, bg="#3e2723", fg="white", font=("Georgia", 10), width=12)
        e_lvl.pack(side=tk.LEFT, padx=5)
        e_lvl.insert(0, "50")
        def set_custom_level():
            try:
                val = int(e_lvl.get())
                if val > self.player.level:
                    add_levels(val - self.player.level)
                else:
                    self.player.level = val
                    self.update_sidebar()
                    lbl_status.config(text=f"Ustawiono poziom na {val}")
            except ValueError:
                lbl_status.config(text="Błąd: Podaj liczbę!")
        tk.Button(f_lvl, text="Ustaw", bg="#5d4037", fg="white", command=set_custom_level).pack(side=tk.LEFT)

        # Python Exec Command
        f_code = tk.Frame(input_frame, bg="#1a100b")
        f_code.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f_code, text="Komenda Python:", fg="white", bg="#1a100b", font=("Georgia", 10, "bold")).pack(side=tk.LEFT)
        e_code = tk.Entry(f_code, bg="#3e2723", fg="white", font=("Georgia", 9), width=20)
        e_code.pack(side=tk.LEFT, padx=5)
        e_code.insert(0, "self.player.gold += 100000")
        def exec_code():
            try:
                cmd = e_code.get()
                exec(cmd, {"self": self, "player": self.player, "combat": combat})
                self.update_sidebar()
                self.log_msg(f"[DEBUG] Wykonano: {cmd}")
                lbl_status.config(text="Wykonano komendę Python!")
            except Exception as err:
                lbl_status.config(text=f"Błąd: {err}")
        tk.Button(f_code, text="Wykonaj", bg="#7a3333", fg="white", command=exec_code).pack(side=tk.LEFT)

        lbl_status = tk.Label(win, text="Wybierz opcję do przetestowania...", font=("Georgia", 10, "italic"), fg="#f4d03f", bg="#2c1a12")
        lbl_status.pack(pady=10)

    def save_and_quit(self):
        if self.player and self.current_save_path:
            save_game(self.player, self.current_save_path)
            self.log_msg("Zapisano grę.")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = IdleRPGApp(root)
    root.mainloop()
