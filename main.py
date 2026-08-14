import tkinter as tk
import customtkinter as ctk
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import math
from PIL import Image, ImageTk
import os
import sys
import pickle
import random
import time
import threading
import traceback
# --- PATCH CUSTOMTKINTER BUGS ---
import customtkinter as ctk
original_destroy = ctk.CTkButton.destroy
def safe_destroy(self):
    if not hasattr(self, '_font'): self._font = None
    try: original_destroy(self)
    except Exception: pass
ctk.CTkButton.destroy = safe_destroy
# --------------------------------

from datetime import datetime

def global_excepthook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}] KRYTYCZNY BŁĄD:\n")
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
        f.write("-" * 50 + "\n")
        
    print("Wystąpił błąd krytyczny. Zapisano do error_log.txt", file=sys.stderr)

sys.excepthook = global_excepthook

def tk_excepthook(exc, val, tb):
    global_excepthook(exc, val, tb)

import combat
from player import Player
from quests import get_all_quests
from shop import FantasyShop
from market import Market
import npc_lore
from items import get_item, Consumable
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
        super().__init__(container, bg=bg_color, *args, **kwargs)
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
        self.root.title("Idle RPG - Fantasy Edition")
        self.root.configure(bg="#000000")
        
        # Podpięcie przechwytywania błędów interfejsu (Tkinter) do naszego loggera
        self.root.report_callback_exception = tk_excepthook
        
        self.root.geometry("1024x768")
        try:
            self.root.state("zoomed")
        except:
            pass # Fallback dla systemów innych niż Windows
            
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        
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

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)

    def make_wrapping_label(self, parent, text, **kwargs):
        lbl = tk.Label(parent, text=text, **kwargs)
        lbl.pack(anchor=tk.W, fill=tk.X)
        lbl.bind('<Configure>', lambda e: lbl.configure(wraplength=e.width - 20))
        return lbl

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
            self.player.update_offline_progress(is_offline=False)
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
        
        self.set_background(self.view_panel, "tavern")
        
        # Pełnowymiarowy canvas tawerny pokrywający cały panel widoku
        self.tavern_canvas = tk.Canvas(self.view_panel, highlightthickness=0, bg="#111")
        self.tavern_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        
        # Pobieramy rzeczywistą szerokość i wysokość view_panel
        self.view_panel.update_idletasks()
        vp_w = self.view_panel.winfo_width()
        vp_h = self.view_panel.winfo_height()
        if vp_w < 500 or vp_h < 500:
            vp_w = sw - 260
            vp_h = sh
        
        # Wyśrodkowanie tła tawerny dokładnie tak samo jak w tk.Label (brak przesunięć)
        if "tavern" in self.bg_images:
            self.tavern_canvas.create_image(vp_w / 2, vp_h / 2, image=self.bg_images["tavern"], anchor=tk.CENTER)
            
        # Idealnie wycentrowany układ 6 kart towarzyszy (2 rzędy po 3 kolumny)
        card_w = 240
        card_h = 240
        gap_x = 60
        gap_y = 50
        total_cards_w = card_w * 3 + gap_x * 2  # 840px
        total_cards_h = card_h * 2 + gap_y      # 530px
        
        start_x = int((vp_w - total_cards_w) / 2)
        start_y = int((vp_h - total_cards_h) / 2)
        
        # Półprzezroczyste zaciemnienie tła dokładnie pod wycentrowanymi kartami i tytułem
        self.tavern_canvas.create_rectangle(start_x - 35, start_y - 110, start_x + total_cards_w + 35, start_y + total_cards_h + 30, fill="#000000", stipple="gray50", tags="bg_dim")
        
        title_x = int(vp_w / 2)
        title_y = max(40, start_y - 75)
        self.tavern_canvas.create_text(title_x, title_y, text="Tawerna 'Pod Skrzydłem Upadłego Anioła'", font=("Georgia", 26, "bold"), fill="#f4d03f")
        self.tavern_canvas.create_text(title_x, title_y + 35, text="Kliknij na postać, aby z nią porozmawiać.", font=("Georgia", 15, "italic"), fill="#ccc")
        
        positions = {
            "maslak": (start_x, start_y),
            "damian": (start_x + (card_w + gap_x), start_y),
            "pianek": (start_x + (card_w + gap_x) * 2, start_y),
            "yomen": (start_x, start_y + (card_h + gap_y)),
            "eczme": (start_x + (card_w + gap_x), start_y + (card_h + gap_y)),
            "domcia": (start_x + (card_w + gap_x) * 2, start_y + (card_h + gap_y))
        }
        
        for npc_id, npc_data in npc_lore.NPC_DB.items():
            if npc_id in positions:
                x, y = positions[npc_id]
                img_key = npc_data["img"]
                tag = f"npc_{npc_id}"
                
                # Złota ramka, domyślnie ukryta
                self.tavern_canvas.create_rectangle(x-4, y-4, x+244, y+244, outline="#f4d03f", width=4, tags=f"rect_{npc_id}", state=tk.HIDDEN)
                
                if img_key in self.portraits:
                    self.tavern_canvas.create_image(x, y, image=self.portraits[img_key], anchor=tk.NW, tags=(tag, "npc_img"))
                else:
                    self.tavern_canvas.create_rectangle(x, y, x+240, y+240, fill="gray", tags=(tag, "npc_img"))
                
                # Nazwa, domyślnie ukryta
                self.tavern_canvas.create_text(x+120, y-20, text=npc_data["name"].split(',')[0], fill="#f4d03f", font=("Georgia", 18, "bold"), tags=f"name_{npc_id}", state=tk.HIDDEN)
                
                # Złoty wykrzyknik jeśli postać ma ważne zadanie do przekazania lub nagrodę
                has_quest = False
                for q in self.player.quests:
                    if q.quest_id.endswith(f"_{npc_id}"):
                        q.update_status(self.player.level)
                        if q.status in ['AVAILABLE', 'COMPLETED']:
                            has_quest = True
                            break
                            
                if has_quest:
                    self.tavern_canvas.create_text(x+222, y+32, text="!", fill="#000000", font=("Georgia", 58, "bold"), tags=tag)
                    self.tavern_canvas.create_text(x+220, y+30, text="!", fill="#f1c40f", font=("Georgia", 58, "bold"), tags=tag)
                
                self.tavern_canvas.tag_bind(tag, "<Enter>", lambda e, n_id=npc_id: self.on_npc_hover(n_id))
                self.tavern_canvas.tag_bind(tag, "<Leave>", lambda e, n_id=npc_id: self.on_npc_leave(n_id))
                self.tavern_canvas.tag_bind(tag, "<Button-1>", lambda e, n_id=npc_id: self.open_npc_dialog(n_id))

        # --- KARCZMARZ BARNABA (Całkowicie po prawej stronie za ladą) ---
        # Precyzyjny wielokąt aury Karczmarza Barnaby (wyekstrahowany bezpośrednio z edytowanej grafiki)
        rel_pts = [
            (0.8145, 0.4553),
            (0.8184, 0.4273),
            (0.8252, 0.4238),
            (0.8564, 0.4361),
            (0.8604, 0.4291),
            (0.8633, 0.4221),
            (0.8643, 0.4028),
            (0.8662, 0.3608),
            (0.8760, 0.3503),
            (0.8857, 0.3503),
            (0.8906, 0.3520),
            (0.8984, 0.3608),
            (0.9023, 0.3818),
            (0.9082, 0.3958),
            (0.9150, 0.4221),
            (0.9229, 0.4326),
            (0.9277, 0.4483),
            (0.9297, 0.4658),
            (0.9307, 0.4851),
            (0.9297, 0.4904),
            (0.9248, 0.5026),
            (0.9170, 0.5254),
            (0.9121, 0.5324),
            (0.8955, 0.5464),
            (0.8945, 0.5464),
            (0.8838, 0.5534),
            (0.8760, 0.5534),
            (0.8672, 0.5464),
            (0.8613, 0.5271),
            (0.8545, 0.5026),
            (0.8467, 0.5009),
            (0.8408, 0.4956),
            (0.8281, 0.4886),
            (0.8184, 0.4851),
            (0.8145, 0.4588),
        ]
        poly_pts = []
        for rx, ry in rel_pts:
            px = rx * sw - (sw - vp_w) / 2
            py = ry * sh - (sh - vp_h) / 2
            poly_pts.extend([int(px), int(py)])

        # 1. Czysta, elegancka biała poświata spoczynkowa (brak zaciemniania postaci w środku)
        self.tavern_canvas.create_polygon(
            poly_pts, 
            fill="", 
            outline="#ffffff", 
            width=2, 
            smooth=True, 
            tags=("innkeeper_body", "npc_innkeeper")
        )
        
        # 2. Mocne złote podświetlenie (aktywne po najechaniu myszką)
        self.tavern_canvas.create_polygon(
            poly_pts, 
            fill="", 
            outline="#f4d03f", 
            width=4, 
            smooth=True, 
            tags=("innkeeper_hover_glow", "npc_innkeeper"), 
            state=tk.HIDDEN
        )
        
        # 3. Dodatkowa poświata zewnętrzna
        self.tavern_canvas.create_polygon(
            poly_pts, 
            fill="", 
            outline="#fff8dc", 
            width=6, 
            smooth=True, 
            tags=("innkeeper_outer_aura", "npc_innkeeper"), 
            state=tk.HIDDEN
        )
        
        # 4. Etykieta nad głową Karczmarza
        head_x = int(0.8857 * sw - (sw - vp_w) / 2)
        head_y = max(30, int(0.30 * sh - (sh - vp_h) / 2))
        self.tavern_canvas.create_text(
            head_x, head_y, 
            text="✨ Karczmarz Barnaba (Kliknij)", 
            fill="#f4d03f", 
            font=("Georgia", 15, "bold"), 
            tags=("innkeeper_name", "npc_innkeeper"), 
            state=tk.HIDDEN
        )
        
        # 5. Precyzyjna detekcja kursora w całym wnętrzu sylwetki (Point-in-Polygon)
        def is_inside_innkeeper(mx, my):
            n = len(poly_pts) // 2
            inside = False
            p1x, p1y = poly_pts[0], poly_pts[1]
            for i in range(1, n + 1):
                p2x, p2y = poly_pts[(i % n) * 2], poly_pts[(i % n) * 2 + 1]
                if my > min(p1y, p2y) and my <= max(p1y, p2y) and mx <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (my - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or mx <= xinters:
                        inside = not inside
                p1x, p1y = p2x, p2y
            return inside

        self._innkeeper_hovered = False
        def on_tavern_canvas_motion(event):
            if is_inside_innkeeper(event.x, event.y):
                if not self._innkeeper_hovered:
                    self._innkeeper_hovered = True
                    self.on_innkeeper_hover()
            else:
                if self._innkeeper_hovered:
                    self._innkeeper_hovered = False
                    self.on_innkeeper_leave()

        def on_tavern_canvas_click(event):
            if is_inside_innkeeper(event.x, event.y):
                self.open_npc_dialog("innkeeper")

        self.tavern_canvas.bind("<Motion>", on_tavern_canvas_motion, add="+")
        self.tavern_canvas.bind("<Button-1>", on_tavern_canvas_click, add="+")
        self.tavern_canvas.tag_bind("npc_innkeeper", "<Enter>", self.on_innkeeper_hover)
        self.tavern_canvas.tag_bind("npc_innkeeper", "<Leave>", self.on_innkeeper_leave)
        self.tavern_canvas.tag_bind("npc_innkeeper", "<Button-1>", lambda e: self.open_npc_dialog("innkeeper"))

    def on_innkeeper_hover(self, event=None):
        if hasattr(self, 'tavern_canvas'):
            self.tavern_canvas.itemconfigure("innkeeper_hover_glow", state=tk.NORMAL)
            self.tavern_canvas.itemconfigure("innkeeper_outer_aura", state=tk.NORMAL)
            self.tavern_canvas.itemconfigure("innkeeper_name", state=tk.NORMAL)
            self.tavern_canvas.configure(cursor="hand2")

    def on_innkeeper_leave(self, event=None):
        if hasattr(self, 'tavern_canvas'):
            self.tavern_canvas.itemconfigure("innkeeper_hover_glow", state=tk.HIDDEN)
            self.tavern_canvas.itemconfigure("innkeeper_outer_aura", state=tk.HIDDEN)
            self.tavern_canvas.itemconfigure("innkeeper_name", state=tk.HIDDEN)
            self.tavern_canvas.configure(cursor="")

    def on_npc_hover(self, npc_id):
        if hasattr(self, 'tavern_canvas'):
            self.tavern_canvas.itemconfigure(f"rect_{npc_id}", state=tk.NORMAL)
            self.tavern_canvas.itemconfigure(f"name_{npc_id}", state=tk.NORMAL)
            self.tavern_canvas.configure(cursor="hand2")
            
    def on_npc_leave(self, npc_id):
        if hasattr(self, 'tavern_canvas'):
            self.tavern_canvas.itemconfigure(f"rect_{npc_id}", state=tk.HIDDEN)
            self.tavern_canvas.itemconfigure(f"name_{npc_id}", state=tk.HIDDEN)
            self.tavern_canvas.configure(cursor="")

    def open_npc_dialog(self, npc_id):
        npc = npc_lore.NPC_DB[npc_id]
        
        win = tk.Toplevel(self.root)
        win.title(npc["name"])
        win.geometry("850x750")
        win.configure(bg="#1a100b")
        win.transient(self.root)
        win.grab_set()
        
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 850) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 750) // 2
        win.geometry(f"+{x}+{y}")
        
        top_frame = tk.Frame(win, bg="#1a100b")
        top_frame.pack(pady=15, fill=tk.X)
        
        if npc["img"] in self.portraits:
            lbl_img = tk.Label(top_frame, image=self.portraits[npc["img"]], bg="#1a100b", bd=3, relief=tk.RIDGE)
            lbl_img.pack(side=tk.LEFT, padx=25)
        else:
            # Fallback dla Karczmarza i postaci w tle
            avatar_frame = tk.Frame(top_frame, bg="#2c1a12", bd=3, relief=tk.RIDGE, width=120, height=120)
            avatar_frame.pack(side=tk.LEFT, padx=25)
            avatar_frame.pack_propagate(False)
            icon_char = "🍺" if npc_id == "innkeeper" else "👤"
            tk.Label(avatar_frame, text=icon_char, font=("Georgia", 44), bg="#2c1a12", fg="#f4d03f").pack(expand=True)
            
        info_frame = tk.Frame(top_frame, bg="#1a100b")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.make_wrapping_label(info_frame, npc["name"], font=("Georgia", 18, "bold"), fg="#f4d03f", bg="#1a100b")
        
        dialog_box = scrolledtext.ScrolledText(win, bg="#2c1a12", fg="#ddd", font=("Georgia", 11), wrap=tk.WORD, height=10, bd=4, relief=tk.SUNKEN)
        dialog_box.pack(padx=20, pady=8, fill=tk.BOTH, expand=True)
        dialog_box.insert(tk.END, f"{npc['name'].split(',')[0]}: {npc['greeting']}\n\n")
        dialog_box.configure(state=tk.DISABLED)
        
        def say(text):
            dialog_box.configure(state=tk.NORMAL)
            dialog_box.insert(tk.END, f"{npc['name'].split(',')[0]}: {text}\n\n", "response")
            dialog_box.tag_config("response", foreground="#f4d03f")
            dialog_box.see(tk.END)
            dialog_box.configure(state=tk.DISABLED)
            
        btn_frame = tk.Frame(win, bg="#1a100b")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        for option, response in npc["options"].items():
            btn = ctk.CTkButton(btn_frame, text=option, font=("Georgia", 11, "bold"), fg_color="#3e2723", text_color="#f4d03f", command=lambda r=response: say(r))
            btn.pack(fill=tk.X, padx=30, pady=3)
            
        # ----- SEKCJA ZADAŃ (QUESTS) -----
        for q in self.player.quests:
            if q.quest_id.endswith(f"_{npc_id}"):
                q.update_status(self.player.level)
                
                if q.status == 'AVAILABLE':
                    def open_offer(quest=q):
                        self.open_quest_offer_dialog(quest, parent_win=win, on_accepted=lambda: (self.show_tavern(), self.open_npc_dialog(npc_id)))
                        
                    btn_q = ctk.CTkButton(btn_frame, text=f"📜 [NOWE ZADANIE] Porozmawiaj: {q.name}", font=("Georgia", 11, "bold"), fg_color="#f1c40f", text_color="black", hover_color="#f39c12", command=open_offer)
                    btn_q.pack(fill=tk.X, padx=30, pady=5)
                    
                elif q.status == 'IN_PROGRESS':
                    q.check_completion(self.player)
                    if q.status == 'COMPLETED':
                        win.destroy()
                        self.show_tavern()
                        self.open_npc_dialog(npc_id)
                        return
                        
                    def remind_q(quest=q):
                        say(f"Pamiętaj o naszej umowie: {quest.description}\nPostęp: {quest.get_progress_str()}")
                        
                    btn_q = ctk.CTkButton(btn_frame, text=f"⏳ [W TRAKCIE] {q.name} ({q.get_progress_str()})", font=("Georgia", 11, "italic"), fg_color="#2a1610", text_color="#f4d03f", hover_color="#3e2723", command=remind_q)
                    btn_q.pack(fill=tk.X, padx=30, pady=5)
                    
                elif q.status == 'COMPLETED':
                    def claim_q(quest=q):
                        if quest.claim_reward(self.player):
                            self.log_msg(f"Ukończono zadanie: {quest.name}! Odebrano nagrodę.")
                            self.update_sidebar()
                            win.destroy()
                            self.show_tavern()
                            self.open_npc_dialog(npc_id)
                            
                    btn_q = ctk.CTkButton(btn_frame, text=f"🎁 [ZADANIE UKOŃCZONE] Odbierz Nagrodę: {q.name}", font=("Georgia", 11, "bold"), fg_color="#2ecc71", text_color="white", hover_color="#27ae60", command=claim_q)
                    btn_q.pack(fill=tk.X, padx=30, pady=5)
        # ---------------------------------
        
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
                    
                btn_p = ctk.CTkButton(btn_frame, text="[Wyrusz ze mną do lochu!]", font=("Georgia", 11, "bold"), fg_color="#27ae60", text_color="white", command=recruit_action)
                btn_p.pack(fill=tk.X, padx=30, pady=3)
            else:
                btn_p = ctk.CTkButton(btn_frame, text="✅ Towarzyszy ci w walce", font=("Georgia", 11, "bold"), fg_color="#1a100b", text_color="#2ecc71", state=tk.DISABLED)
                btn_p.pack(fill=tk.X, padx=30, pady=3)
        else:
            btn_locked = ctk.CTkButton(btn_frame, text="🔒 [Zwerbuj] (Ukończ zadanie postaci)", font=("Georgia", 11, "italic"), fg_color="#2a1610", text_color="#888", state=tk.DISABLED)
            btn_locked.pack(fill=tk.X, padx=30, pady=3)

        btn_close = ctk.CTkButton(btn_frame, text="(Odejdź)", font=("Georgia", 11, "italic"), fg_color="#2a1610", text_color="#aaa", command=win.destroy)
        btn_close.pack(fill=tk.X, padx=30, pady=4)

    def load_backgrounds(self):
        assets_dir = "assets"
        try:
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            
            if os.path.exists(os.path.join(assets_dir, "menu_bg.jpg")):
                self.bg_images["menu"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "menu_bg.jpg")).resize((screen_w, screen_h)))
            if os.path.exists(os.path.join(assets_dir, "combat_bg.jpg")):
                self.bg_images["combat"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "combat_bg.jpg")).resize((screen_w, screen_h)))
            if os.path.exists(os.path.join(assets_dir, "dungeon_bg.jpg")):
                self.bg_images["dungeon"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "dungeon_bg.jpg")).resize((screen_w, screen_h)))
            if os.path.exists(os.path.join(assets_dir, "tavern_bg.jpg")):
                self.bg_images["tavern"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "tavern_bg.jpg")).resize((screen_w, screen_h)))
                
            # Dedykowane tła tytularne dla lochów
            if os.path.exists(os.path.join(assets_dir, "dungeon_d1_bg.jpg")):
                self.bg_images["dungeon_d1"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "dungeon_d1_bg.jpg")).resize((screen_w, screen_h)))
            if os.path.exists(os.path.join(assets_dir, "dungeon_d2_bg.jpg")):
                self.bg_images["dungeon_d2"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "dungeon_d2_bg.jpg")).resize((screen_w, screen_h)))
            if os.path.exists(os.path.join(assets_dir, "dungeon_d3_bg.jpg")):
                self.bg_images["dungeon_d3"] = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "dungeon_d3_bg.jpg")).resize((screen_w, screen_h)))
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
                    self.portraits[key] = ImageTk.PhotoImage(img.resize((240, 240), Image.NEAREST))
                    self.companion_portraits[key] = ImageTk.PhotoImage(img.resize((120, 120), Image.NEAREST))
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
                    self.item_icons[key] = ImageTk.PhotoImage(img.resize((64, 64)))
                    self.item_icons_large[key] = ImageTk.PhotoImage(img.resize((120, 120)))
        except Exception as e:
            print("Błąd ładowania ikon przedmiotów:", e)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def set_background(self, parent, bg_type):
        if not hasattr(self, 'bg_label') or not self.bg_label.winfo_exists():
            self.bg_label = tk.Label(parent, bg="#000000")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            
        if bg_type in self.bg_images:
            self.bg_label.configure(image=self.bg_images[bg_type])
        
        self.bg_label.lower()

    def show_start_menu(self):
        self.clear_container()
        self.set_background(self.container, "menu")
        
        menu_frame = tk.Frame(self.container, bg="#2c1a12", bd=10)
        menu_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=450, height=500)
        
        tk.Label(menu_frame, text="IDLE RPG\nFantasy Edition", font=("Georgia", 28, "bold"), fg="#f4d03f", bg="#2c1a12").pack(pady=30)
        
        ctk.CTkButton(menu_frame, text="Nowa Gra", command=self.new_game).pack(pady=15, fill=tk.X, padx=50)
        
        if not os.path.exists(SAVES_DIR):
            os.makedirs(SAVES_DIR)
        saves = [f for f in os.listdir(SAVES_DIR) if f.endswith('.pkl')]
        
        if saves:
            ctk.CTkButton(menu_frame, text="Wczytaj Grę", command=lambda: self.load_game_menu(saves)).pack(pady=15, fill=tk.X, padx=50)
            ctk.CTkButton(menu_frame, text="Usuń Zapis", command=lambda: self.delete_save_menu(saves)).pack(pady=15, fill=tk.X, padx=50)
            
        ctk.CTkButton(menu_frame, text="Wyjdź", command=self.root.quit).pack(pady=15, fill=tk.X, padx=50)

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
        
        entry = tk.Entry(win, font=("Georgia", 14), bg="#3e2723", fg="white", insertbackground="white")
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
            
        ctk.CTkButton(win, text="Rozpocznij Przygodę", command=confirm).pack(pady=15)
        win.bind('<Return>', confirm)

    def load_game_menu(self, saves):
        win = tk.Toplevel(self.root)
        win.title("Wczytaj Zapis")
        win.geometry("350x450")
        win.configure(bg="#2c1a12")
        win.transient(self.root)
        win.grab_set()
        
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 350) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 450) // 2
        win.geometry(f"+{x}+{y}")
        
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
                
        ctk.CTkButton(win, text="Wczytaj", command=load_selected).pack(pady=10)

    def delete_save_menu(self, saves):
        win = tk.Toplevel(self.root)
        win.title("Usuń Zapis")
        win.geometry("350x450")
        win.configure(bg="#2c1a12")
        win.transient(self.root)
        win.grab_set()
        
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 350) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 450) // 2
        win.geometry(f"+{x}+{y}")
        
        tk.Label(win, text="Wybierz zapis do usunięcia:", font=("Georgia", 14), bg="#2c1a12", fg="#ff9999").pack(pady=10)
        listbox = tk.Listbox(win, bg="#3e2723", fg="white", font=("Georgia", 12))
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        current_saves = saves.copy()
        
        for s in current_saves:
            listbox.insert(tk.END, s.replace('.pkl', ''))
            
        def del_selected():
            if not listbox.winfo_exists(): return
            sel = listbox.curselection()
            if sel:
                idx = sel[0]
                save_name = current_saves[idx]
                filepath = os.path.join(SAVES_DIR, save_name)
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                del current_saves[idx]
                if listbox.winfo_exists():
                    listbox.delete(idx)
                
                self.show_start_menu()
                messagebox.showinfo("Sukces", f"Usunięto {save_name}")
                
                if not current_saves and win.winfo_exists():
                    win.destroy()
                
        def del_all():
            if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć WSZYSTKIE zapisy gry? Ta operacja jest nieodwracalna!"):
                for s in list(current_saves):
                    filepath = os.path.join(SAVES_DIR, s)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                current_saves.clear()
                self.show_start_menu()
                if win.winfo_exists():
                    win.destroy()
                messagebox.showinfo("Sukces", "Wyczyszczono wszystkie zapisy gry.")
                
        ctk.CTkButton(win, text="Usuń Wybrany", command=del_selected).pack(pady=5)
        ctk.CTkButton(win, text="Wyczyść Wszystko", command=del_all).pack(pady=5)
        ctk.CTkButton(win, text="Zamknij", command=win.destroy).pack(pady=5)

    def build_main_ui(self):
        self.clear_container()
        
        self.sidebar = tk.Frame(self.container, width=280, bg="#1a100b")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        self.lbl_stats = tk.Label(self.sidebar, text="", font=("Georgia", 10, "bold"), justify=tk.LEFT, bg="#1a100b", fg="#f4d03f", anchor="nw")
        self.lbl_stats.pack(fill=tk.BOTH, padx=10, pady=10)
        
        nav_sf = ScrollableFrame(self.sidebar, bg_color="#1a100b")
        nav_sf.pack(fill=tk.BOTH, expand=True, pady=10)
        nav_frame = nav_sf.scrollable_frame
        
        ctk.CTkButton(nav_frame, text="Wyprawa (Walka)", command=self.show_expedition).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Lochy (Wyprawy)", command=self.show_dungeons).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Rozwój Postaci", command=self.show_stats).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Ekwipunek", command=self.show_equipment).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Sklep Fantasy", command=self.show_fantasy_shop).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Budowle (Pasywne)", command=self.show_buildings_shop).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Bestiariusz", command=self.show_bestiary).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Kowal (Ulepszenia)", command=self.show_blacksmith).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Miasto (Tawerna)", command=self.show_tavern).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="🛠 DEBUG KONSOLA", fg_color="#c0392b", hover_color="#e74c3c", text_color="white", command=self.open_debug_console).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Zapisz i Wyjdź", command=self.save_and_quit).pack(fill=tk.X, padx=10, pady=15)
        
        main_area = tk.Frame(self.container, bg="#000000")
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.view_panel = tk.Frame(main_area, bg="black")
        self.view_panel.pack(fill=tk.BOTH, expand=True)
        
        log_frame = tk.Frame(main_area, height=130, bg="#000000")
        log_frame.pack(side=tk.BOTTOM, fill=tk.X)
        log_frame.pack_propagate(False)
        self.log_text = scrolledtext.ScrolledText(log_frame, bg="#0d0d0d", fg="#a8ff9e", font=("Consolas", 10, "bold"), state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.update_sidebar()
        self.log_msg(f"Witaj, {self.player.name}! Wybierz opcję z pergaminowego menu po lewej.")
        self.show_expedition()

    def update_sidebar(self):
        if not hasattr(self, "lbl_stats") or not self.lbl_stats.winfo_exists(): return
        if not self.player: return
        t_atk = self.player.get_total_atk()
        t_def = self.player.get_total_def()
        t_crit = self.player.get_total_crit()
        t_hp = self.player.get_max_hp()
        
        active_c = getattr(self.player, 'active_companion', None)
        from npc_lore import NPC_DB
        active_name = NPC_DB.get(active_c, {}).get('name', active_c).split(',')[0] if active_c else "Brak"
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
CRIT: {t_crit}%
Stat-PKT: {self.player.stat_points}

✦ DRUŻYNA (Limit 1) ✦
Aktywny: {active_name}
Zrekrutowano: {unlocked_count}/6
        """
        self.lbl_stats.configure(text=stats.strip())

    def log_msg(self, msg):
        if not hasattr(self, "log_text") or not self.log_text.winfo_exists(): return
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.update_sidebar()

    def clear_view(self):
        for widget in self.view_panel.winfo_children():
            if hasattr(self, 'bg_label') and widget == self.bg_label:
                continue
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

        lbl = tk.Label(self.view_panel, text="Wybierz cel swojej wyprawy:", font=("Georgia", 26, "bold"), bg="#1a100b", fg="#f4d03f")
        lbl.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        
        cards_frame = tk.Frame(self.view_panel, bg="#1a100b")
        cards_frame.place(relx=0.5, rely=0.55, anchor=tk.CENTER, relwidth=0.85, relheight=0.7)
        
        for enemy in choices:
            card = tk.Frame(cards_frame, bg="#2c1a12", bd=5, relief=tk.RIDGE)
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=30, pady=20)
            
            if hasattr(self, 'portraits') and enemy.img_key in self.portraits:
                lbl_img = tk.Label(card, image=self.portraits[enemy.img_key], bg="#2c1a12", bd=3, relief=tk.SUNKEN)
                lbl_img.pack(pady=15, padx=10)
                
            tk.Label(card, text=f"{enemy.name}", font=("Georgia", 18, "bold"), bg="#2c1a12", fg="#f4d03f", wraplength=260).pack(pady=5)
            tk.Label(card, text=f"Poziom {enemy.level}", font=("Georgia", 15, "bold"), bg="#2c1a12", fg="#aaa").pack(pady=5)
            tk.Label(card, text=f"HP: {enemy.max_hp} | ATK: {enemy.atk} | DEF: {enemy.defence}", font=("Georgia", 13), bg="#2c1a12", fg="#ddd").pack(pady=10)
            tk.Label(card, text=f"Nagroda: ~{enemy.gold_reward} Złota, ~{enemy.exp_reward} EXP", font=("Georgia", 12, "italic"), bg="#2c1a12", fg="#aaa", wraplength=260).pack(pady=10)
            
            btn = ctk.CTkButton(card, text="WALCZ", font=("Georgia", 16, "bold"), fg_color="#3e2723", text_color="#f4d03f",
                            command=lambda e=enemy: self.select_enemy(e))
            btn.pack(side=tk.BOTTOM, pady=20, ipadx=40, ipady=10)

        refresh_btn = ctk.CTkButton(self.view_panel, text="🔄 Odśwież Przeciwników", font=("Georgia", 16, "bold"), fg_color="#3e2723", text_color="#f4d03f",
                        command=self.show_expedition, )
        refresh_btn.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def select_enemy(self, enemy):
        self.enemy = enemy
        self.setup_combat_ui()
        self.start_combat()

    def setup_combat_ui(self):
        self.clear_view()
        
        if self.current_view == "dungeon" and self.current_dungeon:
            d_bg_key = f"dungeon_{self.current_dungeon.d_id}"
            if d_bg_key in self.bg_images:
                bg_key = d_bg_key
            else:
                bg_key = "dungeon"
        else:
            bg_key = "combat"
                
        self.set_background(self.view_panel, bg_key)
        
        self.combat_canvas = tk.Canvas(self.view_panel, width=1200, height=700, bg="#111", highlightthickness=0)
        self.combat_canvas.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        
        if bg_key in self.bg_images:
            # Ponieważ combat_canvas jest przesunięty wyżej (rely=0.45 zamiast 0.5), musimy przesunąć
            # tło wewnątrz canvasa lekko w dół, aby połączyło się bezszwowo z głównym tłem aplikacji.
            self.root.update_idletasks()
            offset_y = self.view_panel.winfo_height() * 0.05
            self.combat_canvas.create_image(600, 350 + offset_y, image=self.bg_images[bg_key], anchor=tk.CENTER)

        frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        frame.place(relx=0.5, rely=0.88, anchor=tk.CENTER, width=650)
        
        lbl = tk.Label(frame, text=f"Cel: {self.enemy.name} (Lvl {self.enemy.level})", font=("Georgia", 20, "bold"), bg="#2c1a12", fg="#f4d03f")
        lbl.pack(pady=10)
        
        btn_frame = tk.Frame(frame, bg="#2c1a12")
        btn_frame.pack(pady=10)
        
        self.btn_attack = ctk.CTkButton(btn_frame, text="ZACZNIJ", font=("Georgia", 16, "bold"), fg_color="#3e2723", text_color="#f4d03f", command=self.start_combat)
        self.btn_attack.pack(side=tk.LEFT, padx=10, ipadx=40, ipady=10)
        
        self.btn_potion = ctk.CTkButton(btn_frame, text="Wypij Miksturę", font=("Georgia", 14, "bold"), fg_color="#27ae60", text_color="white", command=self.drink_potion)

    def drink_potion(self):
        if not self.combat_active: return
        if getattr(self, 'potions_used_this_battle', 0) >= 3:
            self.log_msg("Osiągnąłeś limit 3 mikstur w tej walce!")
            return
            
        potions = [i for i in self.player.inventory if i["id"] == "pot_hp"]
        if not potions: return
        
        self.player.inventory.remove(potions[0])
        self.player.hp = self.player.get_max_hp()
        self.potions_used_this_battle = getattr(self, 'potions_used_this_battle', 0) + 1
        
        self.log_msg("Wypiłeś Miksturę Pełnego Zdrowia! Odzyskano 100% HP.")
        self.float_text(150, 100, "LECZYSZ SIĘ!", "#2ecc71")
        self.draw_health_bars()
        
        remaining = len(potions) - 1
        if remaining > 0 and self.potions_used_this_battle < 3:
            self.btn_potion.configure(text=f"Wypij Miksturę ({remaining}) [Użyto: {self.potions_used_this_battle}/3]")
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
            self.loop_combat = False
            self.show_dungeons()
        else:
            self.loop_combat = False
            self.show_expedition()

    def draw_health_bars(self):
        self.combat_canvas.delete("ui")
        
        p_max = self.player.get_max_hp()
        p_cur = self.player.hp
        e_max = self.enemy.max_hp
        
        if not hasattr(self, 'enemy_cur_hp'):
            self.enemy_cur_hp = e_max

        # Import narzędzia pomiaru czcionki dla idealnego dopasowania szerokości
        try:
            from tkinter import font as tkfont
            ui_font = tkfont.Font(family="Georgia", size=11, weight="bold")
        except Exception:
            ui_font = None
            
        # --- PASEK ZDROWIA GRACZA ---
        p_text = f"{self.player.name} HP: {int(p_cur)}/{p_max}"
        p_text_w = ui_font.measure(p_text) if ui_font else len(p_text) * 9
        p_bar_w = max(240, p_text_w + 36)
        p_center_x = 270
        p_x1 = int(p_center_x - p_bar_w / 2)
        p_x2 = int(p_center_x + p_bar_w / 2)
        
        # Ramka i tło gracza
        self.combat_canvas.create_rectangle(p_x1 - 2, 68, p_x2 + 2, 102, fill="#1a100b", outline="#8b5a2b", width=2, tags="ui")
        self.combat_canvas.create_rectangle(p_x1, 70, p_x2, 100, fill="#7f1d1d", tags="ui")
        
        p_ratio = max(0.0, min(1.0, p_cur / p_max))
        p_fill_w = int(p_bar_w * p_ratio)
        if p_fill_w > 0:
            self.combat_canvas.create_rectangle(p_x1, 70, p_x1 + p_fill_w, 100, fill="#22c55e", tags="ui")
        self.combat_canvas.create_text(p_center_x, 85, text=p_text, fill="white", font=("Georgia", 11, "bold"), tags="ui")
        
        # --- PASEK ZDROWIA WROGA / BOSSA ---
        e_text = f"{self.enemy.name} HP: {int(self.enemy_cur_hp)}/{e_max}"
        e_text_w = ui_font.measure(e_text) if ui_font else len(e_text) * 9
        e_bar_w = max(240, e_text_w + 36)
        
        is_boss = getattr(self.enemy, 'is_boss', False) or "boss" in getattr(self, 'enemy', None).__class__.__name__.lower() or "[BOSS]" in self.enemy.name
        e_center_x = 980 if is_boss else 920
        e_x1 = int(e_center_x - e_bar_w / 2)
        e_x2 = int(e_center_x + e_bar_w / 2)
        
        # Ramka i tło wroga
        border_col = "#cd853f" if is_boss else "#8b5a2b"
        self.combat_canvas.create_rectangle(e_x1 - 2, 68, e_x2 + 2, 102, fill="#1a100b", outline=border_col, width=2, tags="ui")
        self.combat_canvas.create_rectangle(e_x1, 70, e_x2, 100, fill="#7f1d1d", tags="ui")
        
        e_ratio = max(0.0, min(1.0, self.enemy_cur_hp / e_max))
        e_fill_w = int(e_bar_w * e_ratio)
        if e_fill_w > 0:
            self.combat_canvas.create_rectangle(e_x1, 70, e_x1 + e_fill_w, 100, fill="#22c55e", tags="ui")
        self.combat_canvas.create_text(e_center_x, 85, text=e_text, fill="white", font=("Georgia", 11, "bold"), tags="ui")

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
            
        self.potions_used_this_battle = 0
        self.btn_attack.configure(text="UCIEKNIJ Z WALKI", fg_color="#7a3333", text_color="white", command=self.flee_combat, state=tk.NORMAL)
        self.loop_combat = True
        
        potions = len([i for i in self.player.inventory if i["id"] == "pot_hp"])
        if potions > 0:
            self.btn_potion.configure(text=f"Wypij Miksturę ({potions}) [Użyto: 0/3]")
            self.btn_potion.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)
        else:
            self.btn_potion.pack_forget()
            
        self.combat_active = True
        self.enemy_cur_hp = self.enemy.max_hp
        self.combat_turn = 0
        
        self.combat_canvas.delete("portrait")
        if hasattr(self, 'portraits'):
            if "hero" in self.portraits:
                # Obramowanie na portret (240x240 img w 150, 120)
                self.combat_canvas.create_rectangle(148, 118, 392, 362, fill="#f4d03f", tags=("portrait", "player_p"))
                self.combat_canvas.create_image(150, 120, image=self.portraits["hero"], anchor=tk.NW, tags=("portrait", "player_p"))
            
            # Widoczny w walce aktywny towarzysz (1 w drużynie)
            ac_id = getattr(self.player, 'active_companion', None)
            if ac_id and ac_id in self.portraits:
                ac_name = npc_lore.NPC_DB.get(ac_id, {}).get('name', ac_id).split(',')[0]
                # Obramowanie i ikona aktywnego towarzysza przy bohaterze (120x120 img w 390, 270)
                self.combat_canvas.create_rectangle(388, 268, 512, 392, fill="#f4d03f", outline="#ffffff", width=2, tags=("portrait", "player_p", "companion_p"))
                if hasattr(self, 'companion_portraits') and ac_id in self.companion_portraits:
                    self.combat_canvas.create_image(390, 270, image=self.companion_portraits[ac_id], anchor=tk.NW, tags=("portrait", "player_p", "companion_p"))
                else:
                    self.combat_canvas.create_image(390, 270, image=self.portraits[ac_id], anchor=tk.NW, tags=("portrait", "player_p", "companion_p"))
                self.combat_canvas.create_text(450, 405, text=f"👥 {ac_name}", fill="#f4d03f", font=("Georgia", 11, "bold"), tags=("portrait", "player_p", "companion_p"))

            e_id = self.enemy.e_id
            
            # Wczytaj większy portret dla bossa jeśli to możliwe
            is_boss = getattr(self.enemy, 'is_boss', False) or "boss" in getattr(self, 'enemy', None).__class__.__name__.lower() or "[BOSS]" in self.enemy.name
            
            if is_boss:
                e_img_key = f"{self.enemy.img_key}_combat"
                if e_img_key not in self.portraits:
                    try:
                        from PIL import Image, ImageTk
                        img = Image.open(f"assets/{self.enemy.img_key}.jpg")
                        self.portraits[e_img_key] = ImageTk.PhotoImage(img.resize((360, 360), Image.NEAREST))
                    except Exception as e:
                        pass
                
                if e_img_key in self.portraits:
                    # Rysowanie dużej ramki bossa
                    cx = 800 + 180
                    cy = 140 + 180
                    self.combat_canvas.create_rectangle(cx - 184, cy - 184, cx + 184, cy + 184, outline="#2c1a12", width=8, tags=("portrait", "enemy_p"))
                    self.combat_canvas.create_rectangle(cx - 180, cy - 180, cx + 180, cy + 180, outline="#8b5a2b", width=4, tags=("portrait", "enemy_p"))
                    self.combat_canvas.create_rectangle(cx - 178, cy - 178, cx + 178, cy + 178, outline="#cd853f", width=2, tags=("portrait", "enemy_p"))
                    self.combat_canvas.create_image(800, 140, image=self.portraits[e_img_key], anchor=tk.NW, tags=("portrait", "enemy_p"))
                elif e_id in self.portraits:
                    self.combat_canvas.create_rectangle(798, 118, 1042, 362, fill="#f4d03f", tags=("portrait", "enemy_p"))
                    self.combat_canvas.create_image(800, 120, image=self.portraits[e_id], anchor=tk.NW, tags=("portrait", "enemy_p"))
            else:
                if e_id in self.portraits:
                    self.combat_canvas.create_rectangle(798, 118, 1042, 362, fill="#f4d03f", tags=("portrait", "enemy_p"))
                    self.combat_canvas.create_image(800, 120, image=self.portraits[e_id], anchor=tk.NW, tags=("portrait", "enemy_p"))
                
        self.draw_health_bars()
        self.log_msg(f"--- ROZPOCZYNASZ WALKĘ Z: {self.enemy.name} ---")
        self.root.after(350, self.combat_tick)

    def combat_tick(self):
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas.winfo_exists() or not self.combat_active:
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
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas.winfo_exists() or not self.combat_active: return
        self.combat_canvas.move("player_p", 15, 0)
        
        # Trajektoria: start od portretu gracza do portretu wroga
        start_x, start_y = 270, 240
        target_x, target_y = 920, 240
        start_angle = -45
        end_angle = 45
        # 18 klatek przy 16ms (~60 FPS) = ok. 288ms dynamicznego lotu (40% szybciej)
        steps = 18
        
        self.animate_sword_swing(steps, steps, start_x, start_y, target_x, target_y, start_angle, end_angle)

    def animate_sword_swing(self, steps_left, total_steps, start_x, start_y, target_x, target_y, start_angle, end_angle):
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas.winfo_exists():
            return
            
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
            
        dmg, is_crit = combat.calculate_player_dmg(self.player, self.enemy)
        self.enemy_cur_hp -= dmg
        
        if is_crit:
            self.float_text(920, 190, f"-{dmg} KRYT!", "#ff3333")
        else:
            self.float_text(920, 190, f"-{dmg}", "orange")
        
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
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas.winfo_exists() or not self.combat_active: return
        self.combat_canvas.move("enemy_p", -30, 0)
        
        # Ośrodek portretu gracza to 270, 240
        center_x, center_y = 270, 240
        self.combat_canvas.create_line(center_x-40, center_y-40, center_x+40, center_y+40, fill="#e74c3c", width=6, tags="scratch")
        self.combat_canvas.create_line(center_x-20, center_y-50, center_x+60, center_y+30, fill="#c0392b", width=6, tags="scratch")
        self.combat_canvas.create_line(center_x-60, center_y-30, center_x+20, center_y+50, fill="#e74c3c", width=6, tags="scratch")
        
        self.root.after(180, self.clear_scratch_and_apply_damage)
        
    def clear_scratch_and_apply_damage(self):
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas.winfo_exists(): return
        self.combat_canvas.delete("scratch")
        self.combat_canvas.move("enemy_p", 30, 0) # Wróć portretem
        
        if not self.combat_active:
            return
            
        dmg = combat.calculate_enemy_dmg(self.enemy, self.player)
        self.player.hp -= dmg
        self.float_text(270, 190, f"-{dmg}", "red")
        
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
                self.btn_attack.configure(state=tk.NORMAL)
                
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
                    
                    # Logika losowania modyfikatora (50% szans na sprzęt)
                    chosen_mod_id = None
                    base_item_temp = get_item(drop_id)
                    from items import Equipment
                    from modifiers import MODIFIERS_DB
                    
                    if isinstance(base_item_temp, Equipment) and random.random() < 0.5:
                        valid_mods = [mod for mod in MODIFIERS_DB.values() if base_item_temp.slot in mod.allowed_slots]
                        if valid_mods:
                            chosen_mod = random.choice(valid_mods)
                            chosen_mod_id = chosen_mod.mod_id
                            
                    self.player.add_to_inventory(drop_id, modifier=chosen_mod_id)
                    item = get_item({"id": drop_id, "modifier": chosen_mod_id})
                    
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
                self.loop_combat = False
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
            
            if getattr(self, 'loop_combat', False) and not getattr(self, 'is_dungeon_boss', False):
                # Generujemy tego samego potwora ponownie
                from combat import Enemy
                import copy
                
                # Odtwarzamy potwora z pełnym HP
                self.enemy.hp = self.enemy.max_hp
                
                self.root.after(1500, self.start_combat)
            else:
                # Wróć do ekranu wyboru po krótkiej pauzie by gracz mógł przeczytać log
                self.root.after(2000, self.show_dungeons if self.current_view == "dungeon" else self.show_expedition)

    def show_dungeons(self):
        if self.combat_active:
            messagebox.showwarning("Zajęty", "Trwa walka! Dokończ najpierw pojedynek.")
            return

        self.clear_view()
        self.current_view = "dungeon"
        
        # Domyślne tło wyboru lochów
        self.set_background(self.view_panel, "dungeon")
            
        if self.dungeon_active and self.current_dungeon:
            # Nadpisanie dedykowanym tłem dla konkretnego lochu
            d_bg_key = f"dungeon_{self.current_dungeon.d_id}"
            if d_bg_key in self.bg_images:
                self.set_background(self.view_panel, d_bg_key)
                
            # Dedykowana scena graficzna dla aktywnej wyprawy w lochu ("W PODRÓŻY")
            d = self.current_dungeon
            
            card = tk.Frame(self.view_panel, bg="#1a100b", bd=8, relief=tk.RIDGE)
            card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=650, height=480)
            
            # Kolorystyka klimatyczna dopasowana do konkretnego lochu
            theme_colors = {
                "d1": "#2ecc71", # Złowrogi Las (Szmaragdowy/Zielony)
                "d2": "#e67e22", # Górska Przełęcz (Górski Brąz / Miedź)
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
            
            ctk.CTkButton(card, text="Wycofaj się z lochu", command=self.cancel_dungeon).pack(pady=15)
            return

        # Domyślne okno wyboru lochów
        frame = tk.Frame(self.view_panel, bg="#2c1a12")
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
            btn = ctk.CTkButton(scrollable_frame, text=f"{d.name} (Wymaga poz. {d.level_req})", command=lambda d=d: self.start_dungeon(d))
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
            self.lbl_journey_status.configure(text=f"W PODRÓŻY{dots}")
            
        if hasattr(self, 'lbl_dungeon_timer') and self.lbl_dungeon_timer.winfo_exists():
            self.lbl_dungeon_timer.configure(text=f"Pozostały czas: {rem}s")
            
        if hasattr(self, 'dungeon_progress') and self.dungeon_progress.winfo_exists():
            self.dungeon_progress["value"] = self.dungeon_time
            
        if self.dungeon_time >= self.dungeon_next_flavor:
            flavor = get_random_flavor_text(self.player.party)
            self.log_msg(f"[{self.dungeon_time}s] {flavor}")
            if hasattr(self, 'lbl_dungeon_event') and self.lbl_dungeon_event.winfo_exists():
                self.lbl_dungeon_event.configure(text=f"\"{flavor}\"")
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
        
        # Sprawdzanie czy loch posiada unikalnego, z góry ustalonego bossa
        if hasattr(d, 'hardcoded_boss') and d.hardcoded_boss:
            boss = combat.get_hardcoded_boss(d.hardcoded_boss, self.player.level)
            self.enemy = boss
            
            # Weryfikacja czy gracz już widział kinematyk dla tego bossa
            if not self.player.seen_cinematics.get(boss.e_id, False):
                self.play_boss_cinematic(boss, lambda: self.start_combat())
                return # Zatrzymujemy tutaj - walka odpali się po animacji
            else:
                self.log_msg(f"--- CZAS MINĄŁ! DROGĘ ZAGRADZA CI {boss.name.upper()}! ---")
                
        else:
            # Stara logika (losowy przeciwnik skalowany jako boss)
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

    def play_boss_cinematic(self, boss, on_complete):
        """Silnik do odtwarzania kinowego intra bossa przed walką."""
        self.clear_view()
        self.current_view = "cinematic"
        
        # Całkowicie czarne tło
        cinematic_canvas = tk.Canvas(self.view_panel, bg="black", highlightthickness=0)
        cinematic_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Oczekujemy na wyrenderowanie, by pobrać prawdziwe wymiary
        self.root.update_idletasks()
        canvas_width = cinematic_canvas.winfo_width()
        if canvas_width <= 1: canvas_width = 800
        canvas_height = cinematic_canvas.winfo_height()
        if canvas_height <= 1: canvas_height = 600
        
        # Teksty narracyjne i unikalne cytaty specyficzne dla każdego bossa
        cinematics_data = {
            "boss_ptys": {
                "narrative": "Zanurzasz się w gęsty, mroczny las...\nWśród starych dębów dostrzegasz opuszczony fort.\nW jego ruinach, na tronie z czaszek, czeka na Ciebie potężny kształt...",
                "quote": "Czekałem na Ciebie, słabeuszu. Podejdź no tu...",
                "quote_color": "#e74c3c"
            },
            "boss_kollman": {
                "narrative": "Wspinasz się po stromych turniach Górskiej Przełęczy...\nWichura świszczy między iglicami, a w powietrzu czuć zapach ozonu i rozgrzanej skóry rękawic.\nNa wąskiej skalnej półce czeka wojowniczy mag, zaciskając bandaże na dłoniach...",
                "quote": "Trzymaj szczelną gardę, bo zaraz dostaniesz lewy prosty z pioruna i sprowadzenie do parteru! Zatańczymy w oktagonie, leszczu!",
                "quote_color": "#f1c40f"
            }
        }
        
        c_info = cinematics_data.get(boss.e_id, {
            "narrative": f"Przemierzasz niezbadane ostępy podziemi...\nW powietrzu unosi się złowrogi chłód.\nNagle z mroku wyłania się potężny przeciwnik: {boss.name}!",
            "quote": "Twoja wędrówka dobiegła końca!",
            "quote_color": "#e74c3c"
        })
        narrative_text = c_info["narrative"]
        boss_quote = c_info["quote"]
        quote_color = c_info["quote_color"]
        
        text_id = cinematic_canvas.create_text(
            canvas_width // 2, canvas_height // 2 - 30,
            text="", fill="white", font=("Georgia", 17, "italic"),
            justify=tk.CENTER, width=680, anchor=tk.CENTER
        )
        
        prompt_id = cinematic_canvas.create_text(
            canvas_width // 2, canvas_height - 60,
            text="[ Kliknij w dowolnym miejscu, aby pominąć pisanie / przejść dalej ▶ ]",
            fill="#888888", font=("Georgia", 11, "italic"),
            justify=tk.CENTER, anchor=tk.CENTER
        )

        state = {"stage": "typing", "typing_done": False, "after_id": None}

        # Powolne "pisanie" liter na ekranie
        def type_text(index=0):
            if self.current_view != "cinematic": return
            if index <= len(narrative_text):
                cinematic_canvas.itemconfig(text_id, text=narrative_text[:index])
                state["after_id"] = self.root.after(30, lambda: type_text(index + 1))
            else:
                state["typing_done"] = True
                cinematic_canvas.itemconfig(prompt_id, text="[ Kliknij w dowolnym miejscu, aby kontynuować ▶ ]", fill="#f4d03f")
                
        def show_boss():
            if self.current_view != "cinematic": return
            state["stage"] = "boss_revealed"
            if state["after_id"]:
                self.root.after_cancel(state["after_id"])
                state["after_id"] = None
                
            cinematic_canvas.delete(text_id)
            cinematic_canvas.delete(prompt_id)
            
            # Wczytywanie portretu bossa, staramy się go wycentrować
            img_key = boss.img_key
            img_cache_key = f"{img_key}_cinematic"
            if img_cache_key not in self.portraits:
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(f"assets/{img_key}.jpg")
                    self.portraits[img_cache_key] = ImageTk.PhotoImage(img.resize((380, 380), Image.NEAREST))
                except Exception as e:
                    print("Błąd ładowania obrazu bossa:", e)
                
            cx = canvas_width // 2
            cy = canvas_height // 2 - 50
            
            if img_cache_key in self.portraits:
                img = self.portraits[img_cache_key]
                # Rysowanie potrójnej klimatycznej ramki wokół obrazu
                cinematic_canvas.create_rectangle(cx - 194, cy - 194, cx + 194, cy + 194, outline="#2c1a12", width=8)
                cinematic_canvas.create_rectangle(cx - 190, cy - 190, cx + 190, cy + 190, outline="#8b5a2b", width=4)
                cinematic_canvas.create_rectangle(cx - 188, cy - 188, cx + 188, cy + 188, outline="#cd853f", width=2)
                cinematic_canvas.create_image(cx, cy, anchor=tk.CENTER, image=img)
                
            # Dymek z tekstem od bossa (lekko pod obrazkiem)
            cinematic_canvas.create_text(
                canvas_width // 2, cy + 225,
                text=f'"{boss_quote}"', fill=quote_color, font=("Georgia", 16, "bold"), justify=tk.CENTER, width=750, anchor=tk.CENTER
            )
            
            # Monit przejścia do walki po kliknięciu
            cinematic_canvas.create_text(
                canvas_width // 2, canvas_height - 50,
                text="⚔️ [ KLIKNIJ W DOWOLNYM MIEJSCU, ABY ROZPOCZĄĆ POJEDYNEK ] ⚔️",
                fill="#2ecc71", font=("Georgia", 13, "bold"), justify=tk.CENTER, anchor=tk.CENTER
            )
            
        def end_cinematic():
            if self.current_view != "cinematic": return
            if state["after_id"]:
                self.root.after_cancel(state["after_id"])
                state["after_id"] = None
                
            # Oznaczamy jako obejrzane
            self.player.seen_cinematics[boss.e_id] = True
            
            # Wracamy do widoku walki
            self.current_view = "dungeon"
            self.setup_combat_ui()
            on_complete()

        def on_cinematic_click(event=None):
            if state["stage"] == "typing":
                if not state["typing_done"]:
                    # Natychmiastowe dokończenie tekstu narracji
                    if state["after_id"]:
                        self.root.after_cancel(state["after_id"])
                        state["after_id"] = None
                    cinematic_canvas.itemconfig(text_id, text=narrative_text)
                    cinematic_canvas.itemconfig(prompt_id, text="[ Kliknij w dowolnym miejscu, aby kontynuować ▶ ]", fill="#f4d03f")
                    state["typing_done"] = True
                else:
                    # Przejście do ujawnienia bossa
                    show_boss()
            elif state["stage"] == "boss_revealed":
                # Przejście do walki
                end_cinematic()

        cinematic_canvas.bind("<Button-1>", on_cinematic_click)
        self.root.bind("<space>", on_cinematic_click)
        self.root.bind("<Return>", on_cinematic_click)

        # Rozpoczynamy animację
        type_text(0)

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
        frame = tk.Frame(self.view_panel, bg="#2c1a12")
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
                
                if stat_name == 'crit_chance':
                    current = self.player.stats.get('crit_chance', 0)
                    if current >= 30:
                        messagebox.showinfo("Limit Osiągnięty", "Maksymalnie możesz zainwestować 30% bazowej szansy na krytyk!")
                        return
                        
                self.player.stats[stat_name] = self.player.stats.get(stat_name, 0) + 1
                self.player.stat_points -= 1
                lbl_pts.configure(text=f"Punkty do rozdania: {self.player.stat_points}")
                self.update_sidebar()
                
        ctk.CTkButton(frame, text="+1 Baza ATK", command=lambda: add_stat('base_atk')).pack(fill=tk.X, padx=80, pady=10)
        ctk.CTkButton(frame, text="+1 Baza DEF", command=lambda: add_stat('base_def')).pack(fill=tk.X, padx=80, pady=10)
        ctk.CTkButton(frame, text="+1% Szansy na Kryt (Max 30%)", command=lambda: add_stat('crit_chance')).pack(fill=tk.X, padx=80, pady=10)
        ctk.CTkButton(frame, text="+1% Zdobyczy z Walki (Max 50%)", command=lambda: add_stat('bonus_loot_pct')).pack(fill=tk.X, padx=80, pady=10)

    def show_equipment(self, selected_item_dict=None, is_equipped_slot=None):
        if self.is_busy(): return
        
        if self.current_view == "equipment" and hasattr(self, 'eq_main_frame') and self.eq_main_frame.winfo_exists():
            for w in self.eq_main_frame.winfo_children():
                w.destroy()
            main_frame = self.eq_main_frame
        else:
            self.clear_view()
            self.current_view = "equipment"
            self.set_background(self.view_panel, "menu")
            
            main_frame = tk.Frame(self.view_panel, bg="#2c1a12")
            main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.85, relheight=0.85)
            self.eq_main_frame = main_frame
            
        # Lewy panel - Założony sprzęt i Siatka Plecaka
        left_panel = tk.Frame(main_frame, bg="#2c1a12", width=500)
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

        # Funkcje Drag & Drop
        self.drag_phantom = None
        self.drag_item_dict = None
        
        def on_drag_start(event, item_dict):
            if hasattr(self, 'drag_phantom') and self.drag_phantom:
                try:
                    self.drag_phantom.destroy()
                except:
                    pass
                
            self.drag_item_dict = item_dict
            
            self.drag_phantom = tk.Toplevel(self.root)
            self.drag_phantom.withdraw()
            self.drag_phantom.configure(bg="#111")
            self.drag_phantom.overrideredirect(True)
            self.drag_phantom.attributes("-topmost", True)
            self.drag_phantom.attributes("-alpha", 0.8) # Lekka przezroczystość (zjawa)
            
            item = get_item(item_dict)
            if hasattr(self, 'item_icons') and item_dict["id"] in self.item_icons:
                lbl = tk.Label(self.drag_phantom, image=self.item_icons[item_dict["id"]], bg="#111", bd=2, relief=tk.RAISED)
            else:
                lbl = tk.Label(self.drag_phantom, text=item.name[:4], font=("Georgia", 10, "bold"), bg="#111", fg="#f4d03f", bd=2, relief=tk.RAISED)
            lbl.pack()
            
            self.drag_phantom.geometry(f"+{event.x_root + 15}+{event.y_root + 15}")
            self.drag_phantom.deiconify()
            
            self.drag_phantom.bind("<B1-Motion>", on_drag_motion)
            self.drag_phantom.bind("<ButtonRelease-1>", on_drag_release)

        def on_drag_motion(event):
            if hasattr(self, 'drag_phantom') and self.drag_phantom:
                self.drag_phantom.geometry(f"+{event.x_root + 15}+{event.y_root + 15}")

        def on_drag_release(event):
            if hasattr(self, 'drag_phantom') and self.drag_phantom:
                try:
                    self.drag_phantom.destroy()
                except:
                    pass
                self.drag_phantom = None
                
            if not getattr(self, 'drag_item_dict', None):
                return
                
            target_widget = self.root.winfo_containing(event.x_root, event.y_root)
            
            w = target_widget
            found_slot = None
            is_in_inventory = False
            while w:
                if w in self.equipment_slot_widgets:
                    found_slot = self.equipment_slot_widgets[w]
                    break
                if hasattr(self, 'inv_grid_frame') and w == self.inv_grid_frame:
                    is_in_inventory = True
                w = getattr(w, 'master', None)
                
            if found_slot:
                item = get_item(self.drag_item_dict)
                if item and getattr(item, "slot", None) == found_slot:
                    req_lvl = getattr(item, "level_req", 1)
                    if self.player.level < req_lvl:
                        messagebox.showwarning("Zbyt Niski Poziom", f"Twój poziom ({self.player.level}) jest zbyt niski, by założyć ten przedmiot!\n(Wymagany poziom: {req_lvl})")
                        self.show_equipment(self.drag_item_dict, is_equipped_slot=None)
                        self.drag_item_dict = None
                        return
                        
                    if self.player.equip(self.drag_item_dict):
                        self.log_msg(f"Założono: {item.name}")
                        self.update_sidebar()
                        self.show_equipment(self.drag_item_dict, is_equipped_slot=found_slot)
                        self.drag_item_dict = None
                        return
                else:
                    self.log_msg("To złe miejsce na ten przedmiot!")
            elif is_in_inventory:
                item = get_item(self.drag_item_dict)
                if item:
                    slot = getattr(item, "slot", None)
                    if slot and self.player.equipment.get(slot) == self.drag_item_dict:
                        self.player.inventory.append(self.drag_item_dict)
                        self.player.equipment[slot] = None
                        self.log_msg(f"Zdjęto: {item.name}")
                        self.update_sidebar()
                        self.show_equipment(self.drag_item_dict, is_equipped_slot=None)
                        self.drag_item_dict = None
                        return
            
            item_to_show = self.drag_item_dict
            self.drag_item_dict = None
            self.show_equipment(item_to_show, is_equipped_slot=None)

        self.equipment_slot_widgets = {}
        for slot_key, slot_label in slot_names.items():
            slot_box = tk.Frame(eq_slots_frame, bg="#2c1a12", bd=2, relief=tk.RAISED, width=90, height=105)
            slot_box.pack(side=tk.LEFT, padx=6, pady=6)
            slot_box.pack_propagate(False)
            
            # Rejestracja widgetu slotu do Drag & Drop
            # Ponieważ puszczenie myszy nad np. labelem też ma działać, będziemy wędrować w górę masterów
            self.equipment_slot_widgets[slot_box] = slot_key
            
            tk.Label(slot_box, text=slot_label, font=("Georgia", 9, "bold"), bg="#2c1a12", fg="#aaa").pack(pady=2)
            
            eq_item_dict = self.player.equipment.get(slot_key)
            if eq_item_dict and get_item(eq_item_dict):
                item = get_item(eq_item_dict)
                is_leg = getattr(item, 'rarity', 'Zwykły') == "Legendarny"
                border_col = "#f4d03f" if is_leg else "#3498db"
                
                icon_btn = tk.Canvas(slot_box, width=64, height=64, bg="#111", highlightbackground=border_col, highlightthickness=2, cursor="hand2")
                icon_btn.pack(pady=2)
                
                if hasattr(self, 'item_icons') and eq_item_dict["id"] in self.item_icons:
                    icon_btn.create_image(32, 32, image=self.item_icons[eq_item_dict["id"]])
                else:
                    icon_btn.create_text(32, 32, text=item.name[:2], fill=border_col, font=("Georgia", 12, "bold"))
                
                lvl = eq_item_dict.get('lvl', 0)
                if lvl > 0:
                    icon_btn.create_text(48, 48, text=f"+{lvl}", fill="#2ecc71", font=("Arial", 10, "bold"))
                    
                icon_btn.bind("<Button-1>", lambda e, item_d=eq_item_dict, s_key=slot_key: self.show_equipment(item_d, is_equipped_slot=s_key))
                icon_btn.bind("<ButtonPress-1>", lambda e, item_d=eq_item_dict: on_drag_start(e, item_d))
                icon_btn.bind("<B1-Motion>", on_drag_motion)
                icon_btn.bind("<ButtonRelease-1>", on_drag_release)
            else:
                empty_lbl = tk.Label(slot_box, text="[ Puste ]", font=("Georgia", 9, "italic"), bg="#2c1a12", fg="#666")
                empty_lbl.pack(expand=True)

        tk.Label(left_panel, text="Plecak (Przeciągnij by założyć)", font=("Georgia", 12, "bold"), bg="#2c1a12", fg="#f4d03f").pack(anchor=tk.W, pady=(10, 2))
        
        sf = ScrollableFrame(left_panel, bg_color="#1a100b")
        sf.pack(fill=tk.BOTH, expand=True, pady=5)
        

        self.inv_grid_frame = tk.Frame(sf.scrollable_frame, bg="#1a100b")
        self.inv_grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        cols = 5
        # Rysujemy minimum 30 slotów, lub więcej jeśli gracz ma ponad 30 przedmiotów
        total_slots = max(30, ((len(self.player.inventory) + cols - 1) // cols) * cols)
        
        for idx in range(total_slots):
            r, c = divmod(idx, cols)
            
            if idx < len(self.player.inventory):
                inv_item_dict = self.player.inventory[idx]
                item = get_item(inv_item_dict)
                if not item: continue
                
                is_leg = getattr(item, 'rarity', 'Zwykły') == "Legendarny"
                border_col = "#f4d03f" if is_leg else "#7f8c8d"
                is_selected = (inv_item_dict == selected_item_dict and is_equipped_slot is None)
                bg_highlight = "#5d4037" if is_selected else "#2c1a12"
                
                tile = tk.Frame(self.inv_grid_frame, bg=bg_highlight, bd=2, relief=tk.RAISED, width=84, height=100, cursor="hand2")
                tile.grid(row=r, column=c, padx=4, pady=4)
                tile.grid_propagate(False)
                
                icon_canvas = tk.Canvas(tile, width=64, height=64, bg="#111", highlightbackground=border_col, highlightthickness=2)
                icon_canvas.pack(pady=3)
                
                if hasattr(self, 'item_icons') and inv_item_dict["id"] in self.item_icons:
                    icon_canvas.create_image(32, 32, image=self.item_icons[inv_item_dict["id"]])
                else:
                    icon_canvas.create_text(32, 32, text=item.name[:2], fill=border_col, font=("Georgia", 12, "bold"))
                
                lvl = inv_item_dict.get('lvl', 0)
                if lvl > 0:
                    icon_canvas.create_text(48, 48, text=f"+{lvl}", fill="#2ecc71", font=("Arial", 10, "bold"))
                
                lvl_str = f" +{lvl}" if lvl > 0 else ""
                name_short = item.name if len(item.name) <= 6 else item.name[:5] + "…"
                lbl_n = tk.Label(tile, text=name_short + lvl_str, font=("Georgia", 7, "bold"), bg=bg_highlight, fg=border_col)
                lbl_n.pack()
                
                # Bindowanie zdarzeń do wszystkich elementów płytki plecaka
                for widget in (tile, icon_canvas, lbl_n):
                    widget.bind("<ButtonPress-1>", lambda e, item_d=inv_item_dict: on_drag_start(e, item_d))
                    widget.bind("<B1-Motion>", on_drag_motion)
                    widget.bind("<ButtonRelease-1>", on_drag_release)
            else:
                # Pusty slot dający wizualne odczucie siatki
                empty_tile = tk.Frame(self.inv_grid_frame, bg="#20130d", bd=1, relief=tk.SUNKEN, width=84, height=100)
                empty_tile.grid(row=r, column=c, padx=4, pady=4)
                empty_tile.grid_propagate(False)

        # Prawy panel - Inspektor Szczegółów Przedmiotu
        right_panel = tk.Frame(main_frame, bg="#1a100b", width=310, bd=4, relief=tk.RIDGE)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        right_panel.pack_propagate(False)
        
        if selected_item_dict and get_item(selected_item_dict):
            item = get_item(selected_item_dict)
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
                lbl_stat = tk.Label(right_panel, text=f"Statystyki: {stat_str}", font=("Georgia", 11, "bold"), fg="#a8ff9e", bg="#1a100b")
                lbl_stat.pack(pady=4, fill=tk.X)
                lbl_stat.bind('<Configure>', lambda e: e.widget.config(wraplength=e.width - 20))
            elif hasattr(item, 'effect'):
                eff_str = ", ".join([f"{k.upper()}: {v}" for k, v in item.effect.items()])
                lbl_eff = tk.Label(right_panel, text=f"Efekt: {eff_str}", font=("Georgia", 11, "bold"), fg="#3498db", bg="#1a100b")
                lbl_eff.pack(pady=4, fill=tk.X)
                lbl_eff.bind('<Configure>', lambda e: e.widget.config(wraplength=e.width - 20))
                
            tk.Label(right_panel, text=f"Wartość: {item.value}g | Sprzedaż: {sell_price}g", font=("Georgia", 10, "bold"), fg="#f4d03f", bg="#1a100b").pack()
            
            # Opis / Historia
            desc_box = scrolledtext.ScrolledText(right_panel, bg="#2c1a12", fg="#ddd", font=("Georgia", 9), wrap=tk.WORD, height=5, bd=3, relief=tk.SUNKEN)
            desc_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
            desc_box.insert(tk.END, item.description)
            desc_box.configure(state=tk.DISABLED)
            
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
                ctk.CTkButton(btn_box, text="Zdejmij Przedmiot", command=unequip_action).pack(fill=tk.X, pady=2)
            else:
                def equip_action():
                    req_lvl = getattr(item, "level_req", 1)
                    if self.player.level < req_lvl:
                        messagebox.showwarning("Zbyt Niski Poziom", f"Twój poziom ({self.player.level}) jest zbyt niski, by założyć ten przedmiot!\n(Wymagany poziom: {req_lvl})")
                        return
                        
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
                    ctk.CTkButton(btn_box, text="Załóż Przedmiot", command=equip_action).pack(fill=tk.X, pady=2)
                elif hasattr(item, 'effect'):
                    ctk.CTkButton(btn_box, text="Użyj Przedmiotu", command=use_action).pack(fill=tk.X, pady=2)
                    
                ctk.CTkButton(btn_box, text=f"💰 Sprzedaj ({sell_price}g)", command=sell_action).pack(fill=tk.X, pady=2)
        else:
            tk.Label(right_panel, text="Brak Wyboru", font=("Georgia", 14, "bold"), fg="#aaa", bg="#1a100b").pack(pady=40)
            tk.Label(right_panel, text="Kliknij dowolny przedmiot w plecaku lub założonym ekwipunku, aby wyświetlić szczegóły i historię.", font=("Georgia", 10, "italic"), fg="#888", bg="#1a100b", wraplength=250, justify=tk.CENTER).pack(padx=15)

    def show_fantasy_shop(self, selected_tier=1):
        if self.is_busy(): return
        
        if self.current_view == "fantasy_shop" and hasattr(self, 'shop_main_frame') and self.shop_main_frame.winfo_exists():
            for w in self.shop_main_frame.winfo_children():
                w.destroy()
            frame = self.shop_main_frame
        else:
            self.clear_view()
            self.current_view = "fantasy_shop"
            self.set_background(self.view_panel, "menu")
            
            frame = tk.Frame(self.view_panel, bg="#2c1a12")
            frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.85, relheight=0.85)
            self.shop_main_frame = frame
        
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
            item = get_item(item_id)
            if not item: continue
            
            row = tk.Frame(sf.scrollable_frame, bg="#2c1a12", bd=2, relief=tk.RIDGE)
            row.pack(fill=tk.X, padx=5, pady=5)
            
            # Ikona przedmiotu
            icon_canvas = tk.Canvas(row, width=64, height=64, bg="#111", highlightbackground="#f4d03f", highlightthickness=2)
            icon_canvas.pack(side=tk.LEFT, padx=10, pady=8)
            
            if hasattr(self, 'item_icons') and item_id in self.item_icons:
                icon_canvas.create_image(32, 32, image=self.item_icons[item_id])
            else:
                icon_canvas.create_text(32, 32, text=item.name[:2], fill="#f4d03f", font=("Georgia", 12, "bold"))
                
            info = tk.Frame(row, bg="#2c1a12")
            info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)
            
            title_color = "white" if self.player.level >= req_lvl else "#ffaaaa"
            tk.Label(info, text=item.name, font=("Georgia", 13, "bold"), bg="#2c1a12", fg=title_color).pack(anchor=tk.W)
            
            if hasattr(item, 'stats'):
                stat_str = ", ".join([f"{k.upper()}: +{v}" for k, v in item.stats.items()])
                self.make_wrapping_label(info, f"Statystyki: {stat_str}", font=("Georgia", 10, "bold"), bg="#2c1a12", fg="#a8ff9e")
            elif hasattr(item, 'effect'):
                eff_str = ", ".join([f"{k.upper()}: {v}" for k, v in item.effect.items()])
                self.make_wrapping_label(info, f"Efekt: {eff_str}", font=("Georgia", 10, "bold"), bg="#2c1a12", fg="#3498db")
                
            self.make_wrapping_label(info, item.description, font=("Georgia", 9, "italic"), bg="#2c1a12", fg="#aaaaaa")
            
            # Dynamiczna cena dla mikstur
            price = item.value
            if item_id == "pot_hp":
                price = int(50 + (self.player.level ** 1.3) * 15)
                
            if self.player.level >= req_lvl:
                ttk.Button(
                    row, 
                    text=f"Kup ({price}g)", 
                    command=lambda i=item_id, s_tier=selected_tier, p=price: self.buy_fantasy_item(i, s_tier, p)
                ).pack(side=tk.RIGHT, padx=15, pady=10)
            else:
                tk.Label(row, text=f"🔒 Poz. {req_lvl}", font=("Georgia", 12, "bold"), bg="#2c1a12", fg="#ff6666").pack(side=tk.RIGHT, padx=15, pady=10)

    def buy_fantasy_item(self, item_id, selected_tier=1, override_price=None):
        from items import get_item
        item = get_item(item_id)
        if not item: return
        req_lvl = getattr(item, 'level_req', 1)
        if self.player.level < req_lvl:
            messagebox.showwarning("Zbyt Niski Poziom", f"Wymagany jest {req_lvl} poziom, aby kupić {item.name}!")
            return
        price = override_price if override_price is not None else getattr(item, 'value', 100)
            
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
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.85, relheight=0.85)
        
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
            self.make_wrapping_label(info, b.description, font=("Georgia", 10), bg="#3e2723", fg="#aaaaaa")
            tk.Label(info, text=f"Posiadasz: {owned}", font=("Georgia", 10, "italic"), bg="#3e2723", fg="gold").pack(anchor=tk.W)
            
            ctk.CTkButton(row, text=f"Kup ({cost}g)", command=lambda bid=b_id: self.buy_building(bid)).pack(side=tk.RIGHT, padx=10, pady=10)

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
        frame = tk.Frame(self.view_panel, bg="#2c1a12")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.85, relheight=0.85)
        
        tk.Label(frame, text="DZIENNIK ZADAŃ", font=("Georgia", 22, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=10)
        
        sf = ScrollableFrame(frame, bg_color="#3e2723")
        sf.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Aktualizacja statusów
        for q in self.player.quests:
            q.update_status(self.player.level)
            
        for q in self.player.quests:
            row = tk.Frame(sf.scrollable_frame, bg="#2c1a12", bd=2, relief=tk.RIDGE)
            row.pack(fill=tk.X, padx=8, pady=8)
            
            npc_id = getattr(q, 'npc_id', 'innkeeper')
            npc_data = npc_lore.NPC_DB.get(npc_id, {})
            npc_name = npc_data.get('name', 'Zleceniodawca').split(',')[0]
            
            # Miniaturka NPC zlecającego zadanie
            npc_frame = tk.Frame(row, bg="#2c1a12", width=110)
            npc_frame.pack(side=tk.LEFT, padx=10, pady=10)
            
            if hasattr(self, 'companion_portraits') and npc_id in self.companion_portraits:
                tk.Label(npc_frame, image=self.companion_portraits[npc_id], bg="#2c1a12", bd=2, relief=tk.SOLID).pack()
            elif npc_id in self.portraits:
                tk.Label(npc_frame, image=self.portraits[npc_id], bg="#2c1a12", bd=2, relief=tk.SOLID).pack()
            else:
                icon_char = "🍺" if npc_id == "innkeeper" else "📜"
                tk.Label(npc_frame, text=icon_char, font=("Georgia", 36), bg="#3e2723", fg="#f4d03f", width=3, height=2, bd=2, relief=tk.SOLID).pack()
                
            tk.Label(npc_frame, text=npc_name, font=("Georgia", 10, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=4)
            
            info = tk.Frame(row, bg="#2c1a12")
            info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)
            
            # Formatowanie czytelnego opisu nagród
            reward_parts = []
            if 'gold' in q.rewards:
                reward_parts.append(f"💰 +{q.rewards['gold']}g Złota")
            if 'item' in q.rewards:
                item = get_item(q.rewards['item'])
                if item:
                    is_leg = getattr(item, 'rarity', 'Zwykły') == "Legendarny"
                    icon = "🌟 " if is_leg else "🛡️ "
                    reward_parts.append(f"{icon}Przedmiot: {item.name}")
            if 'party' in q.rewards:
                member_id = q.rewards['party']
                member_name = npc_lore.NPC_DB.get(member_id, {}).get('name', member_id).split(',')[0]
                reward_parts.append(f"👥 Towarzysz: Dołącza {member_name}")
            reward_str = " | ".join(reward_parts) if reward_parts else "Brak"
            
            if q.status == 'LOCKED':
                self.make_wrapping_label(info, f"🔒 [Wymaga Poz. {q.unlock_level}] {q.name}", font=("Georgia", 13, "bold"), bg="#2c1a12", fg="#888888")
                self.make_wrapping_label(info, f"Zadanie zablokowane do osiągnięcia {q.unlock_level} poziomu bohatera.", font=("Georgia", 9, "italic"), bg="#2c1a12", fg="#777777")
                self.make_wrapping_label(info, f"🎁 Nagroda: {reward_str}", font=("Georgia", 9), bg="#2c1a12", fg="#888888")
            else:
                title_color = "#2ecc71" if q.status == 'COMPLETED' else ("#f4d03f" if q.status == 'IN_PROGRESS' else "white")
                self.make_wrapping_label(info, f"📜 [Poz. {q.unlock_level}] {q.name}", font=("Georgia", 14, "bold"), bg="#2c1a12", fg=title_color)
                
                # Dialog / cytat fabularny od NPC
                if getattr(q, 'dialog_offer', ''):
                    quote_text = q.dialog_offer[:150] + ("..." if len(q.dialog_offer) > 150 else "")
                    self.make_wrapping_label(info, f'💬 {npc_name}: "{quote_text}"', font=("Georgia", 10, "italic"), bg="#2c1a12", fg="#f9e79f")
                    
                self.make_wrapping_label(info, q.description, font=("Georgia", 10), bg="#2c1a12", fg="#cccccc")
                
                # Licznik postępu
                prog_color = "#2ecc71" if q.status == 'COMPLETED' else "#f1c40f"
                self.make_wrapping_label(info, f"🎯 Postęp: {q.get_progress_str()}", font=("Georgia", 10, "bold"), bg="#2c1a12", fg=prog_color)
                self.make_wrapping_label(info, f"🎁 Nagroda: {reward_str}", font=("Georgia", 10, "bold"), bg="#2c1a12", fg="#f4d03f")
                
                btn_frame = tk.Frame(row, bg="#2c1a12")
                btn_frame.pack(side=tk.RIGHT, padx=15, pady=10)
                
                if q.status == 'AVAILABLE':
                    ctk.CTkButton(btn_frame, text="Przyjmij Zadanie", font=("Georgia", 12, "bold"), fg_color="#3e2723", text_color="#f4d03f", hover_color="#5d4037", command=lambda quest=q: self.accept_quest(quest)).pack(pady=5)
                elif q.status == 'IN_PROGRESS':
                    ctk.CTkButton(btn_frame, text="W trakcie...", font=("Georgia", 11, "italic"), fg_color="#2a1610", text_color="#888888", state=tk.DISABLED).pack(pady=5)
                elif q.status == 'COMPLETED':
                    ctk.CTkButton(btn_frame, text="🎁 ODBIERZ NAGRODĘ", font=("Georgia", 12, "bold"), fg_color="#27ae60", hover_color="#2ecc71", text_color="white", command=lambda quest=q: self.claim_quest(quest)).pack(pady=5)
                elif q.status == 'CLAIMED':
                    tk.Label(btn_frame, text="✔ UKOŃCZONE", font=("Georgia", 12, "bold"), bg="#2c1a12", fg="#2ecc71").pack(pady=5)

    def open_quest_offer_dialog(self, quest, parent_win=None, on_accepted=None):
        npc_id = getattr(quest, 'npc_id', 'innkeeper')
        npc = npc_lore.NPC_DB.get(npc_id, {
            "name": "Tajemniczy Zleceniodawca",
            "img": "maslak",
            "greeting": "Witaj, wędrowcze."
        })
        
        dialog_win = tk.Toplevel(self.root)
        dialog_win.title(f"📜 Zlecenie: {quest.name}")
        dialog_win.geometry("900x780")
        dialog_win.configure(bg="#1a100b")
        dialog_win.transient(self.root)
        dialog_win.grab_set()
        
        dialog_win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 900) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 780) // 2
        dialog_win.geometry(f"+{x}+{y}")
        
        # Nagłówek okna (Portret, imię NPC i tytuł zadania)
        header = tk.Frame(dialog_win, bg="#1a100b", bd=2, relief=tk.RIDGE)
        header.pack(fill=tk.X, padx=15, pady=10)
        
        img_key = npc.get("img", "")
        if img_key in self.portraits:
            lbl_img = tk.Label(header, image=self.portraits[img_key], bg="#1a100b", bd=3, relief=tk.RIDGE)
            lbl_img.pack(side=tk.LEFT, padx=15, pady=10)
        else:
            avatar_frame = tk.Frame(header, bg="#2c1a12", bd=3, relief=tk.RIDGE, width=100, height=100)
            avatar_frame.pack(side=tk.LEFT, padx=15, pady=10)
            avatar_frame.pack_propagate(False)
            icon_char = "🍺" if npc_id == "innkeeper" else "👤"
            tk.Label(avatar_frame, text=icon_char, font=("Georgia", 40), bg="#2c1a12", fg="#f4d03f").pack(expand=True)
            
        header_text = tk.Frame(header, bg="#1a100b")
        header_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(header_text, text=npc["name"], font=("Georgia", 16, "bold"), fg="#f4d03f", bg="#1a100b").pack(anchor="w")
        tk.Label(header_text, text=f"📜 Zadanie: {quest.name} [Wymagany Poz. {quest.unlock_level}]", font=("Georgia", 13, "bold"), fg="#2ecc71", bg="#1a100b").pack(anchor="w", pady=(2, 4))
        tk.Label(header_text, text=quest.description, font=("Georgia", 10, "italic"), fg="#cccccc", bg="#1a100b", wraplength=580, justify=tk.LEFT).pack(anchor="w")
        
        # Główny obszar narracji i monologu NPC
        body_frame = tk.Frame(dialog_win, bg="#1a100b")
        body_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        tk.Label(body_frame, text="💬 Rozmowa z postacią:", font=("Georgia", 12, "bold"), fg="#f4d03f", bg="#1a100b").pack(anchor="w", padx=5, pady=(0, 4))
        
        dialog_box = scrolledtext.ScrolledText(body_frame, bg="#24140e", fg="#f5e6cb", font=("Georgia", 11), wrap=tk.WORD, height=10, bd=3, relief=tk.SUNKEN)
        dialog_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        offer_text = getattr(quest, 'dialog_offer', '') or quest.description
        dialog_box.insert(tk.END, f"{offer_text}\n")
        dialog_box.configure(state=tk.DISABLED)
        
        # Ramka ze szczegółami celów i nagród
        details_frame = tk.Frame(dialog_win, bg="#2c1a12", bd=2, relief=tk.GROOVE)
        details_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Kolumna Lewa: Cele
        req_frame = tk.Frame(details_frame, bg="#2c1a12")
        req_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=8)
        tk.Label(req_frame, text="🎯 Cele do wykonania:", font=("Georgia", 11, "bold"), fg="#e67e22", bg="#2c1a12").pack(anchor="w")
        
        if 'kills' in quest.requirements:
            for mon_name, count in quest.requirements['kills'].items():
                tk.Label(req_frame, text=f"  • Pokonaj: {mon_name} ({count}x)", font=("Georgia", 10, "bold"), fg="#ffffff", bg="#2c1a12").pack(anchor="w")
        else:
            tk.Label(req_frame, text="  • Wykonaj polecenia z opisu zadania", font=("Georgia", 10), fg="#ffffff", bg="#2c1a12").pack(anchor="w")
            
        # Kolumna Prawa: Nagrody
        rew_frame = tk.Frame(details_frame, bg="#2c1a12")
        rew_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=8)
        tk.Label(rew_frame, text="🎁 Nagroda za ukończenie:", font=("Georgia", 11, "bold"), fg="#f4d03f", bg="#2c1a12").pack(anchor="w")
        
        if 'gold' in quest.rewards:
            tk.Label(rew_frame, text=f"  • 💰 Złoto: +{quest.rewards['gold']}g", font=("Georgia", 10, "bold"), fg="#f1c40f", bg="#2c1a12").pack(anchor="w")
        if 'item' in quest.rewards:
            item = get_item(quest.rewards['item'])
            if item:
                rarity = getattr(item, 'rarity', 'Zwykły')
                rarity_prefix = "🌟 [LEGENDARNY] " if rarity == "Legendarny" else "🛡️ "
                tk.Label(rew_frame, text=f"  • {rarity_prefix}{item.name}", font=("Georgia", 10, "bold"), fg="#2ecc71", bg="#2c1a12").pack(anchor="w")
        if 'party' in quest.rewards:
            p_name = npc_lore.NPC_DB.get(quest.rewards['party'], {}).get('name', 'Towarzysz').split(',')[0]
            tk.Label(rew_frame, text=f"  • 👥 Nowy Kompan: {p_name} dołącza do drużyny!", font=("Georgia", 10, "bold"), fg="#3498db", bg="#2c1a12").pack(anchor="w")
            
        # Stopka z interaktywnymi przyciskami gracza
        action_frame = tk.Frame(dialog_win, bg="#1a100b")
        action_frame.pack(fill=tk.X, padx=15, pady=12)
        
        def confirm_accept():
            if quest.accept():
                self.log_msg(f"📜 Przyjęto zadanie od {npc['name'].split(',')[0]}: '{quest.name}'!")
                
                # Wyświetlenie reakcji postaci w oknie dialogowym
                reaction = getattr(quest, 'dialog_accept_reaction', '') or "*Kiwając głową z uznaniem życzy ci powodzenia w walce.*"
                dialog_box.configure(state=tk.NORMAL)
                dialog_box.insert(tk.END, f"\n--- PRZYJĘTO ZLECENIE ---\n\n{reaction}\n", "accept_tag")
                dialog_box.tag_config("accept_tag", foreground="#f1c40f", font=("Georgia", 11, "bold"))
                dialog_box.see(tk.END)
                dialog_box.configure(state=tk.DISABLED)
                
                # Zmiana przycisków
                for child in action_frame.winfo_children():
                    child.destroy()
                    
                def close_and_refresh():
                    dialog_win.destroy()
                    if parent_win and parent_win.winfo_exists():
                        parent_win.destroy()
                    if on_accepted:
                        on_accepted()
                    else:
                        self.show_quests()
                        
                ctk.CTkButton(
                    action_frame, 
                    text="🚀 [RUSZAJMY DO WALKI!]", 
                    font=("Georgia", 13, "bold"), 
                    fg_color="#27ae60", 
                    hover_color="#2ecc71", 
                    height=42, 
                    command=close_and_refresh
                ).pack(fill=tk.X, padx=20, pady=5)
                
        btn_accept = ctk.CTkButton(
            action_frame, 
            text=f"⚔️ PRZYJMUJĘ ZLECENIE: {quest.name.upper()}!", 
            font=("Georgia", 13, "bold"), 
            fg_color="#f1c40f", 
            hover_color="#f39c12", 
            text_color="black", 
            height=40, 
            command=confirm_accept
        )
        btn_accept.pack(fill=tk.X, padx=20, pady=4)
        
        btn_decline = ctk.CTkButton(
            action_frame, 
            text="⏳ Muszę się jeszcze przygotować (Odejdź)", 
            font=("Georgia", 11, "italic"), 
            fg_color="#2a1610", 
            hover_color="#3e2723", 
            text_color="#aaaaaa", 
            height=32, 
            command=dialog_win.destroy
        )
        btn_decline.pack(fill=tk.X, padx=20, pady=2)

    def accept_quest(self, quest):
        self.open_quest_offer_dialog(quest, on_accepted=self.show_quests)

    def claim_quest(self, quest):
        if quest.claim_reward(self.player):
            npc_id = getattr(quest, 'npc_id', 'innkeeper')
            npc_name = npc_lore.NPC_DB.get(npc_id, {}).get('name', 'Zleceniodawca').split(',')[0]
            dialog_complete = getattr(quest, 'dialog_complete', 'Wspaniała robota! Zasłużyłeś na tę nagrodę.')
            
            self.log_msg(f"✅ Ukończono zadanie: '{quest.name}'! Odebrano nagrodę.")
            self.update_sidebar()
            self.show_quests()
            
            messagebox.showinfo(
                f"🌟 ZADANIE UKOŃCZONE: {quest.name} 🌟",
                f"Wspaniały sukces!\n\n💬 {npc_name}:\n\"{dialog_complete}\"\n\nOtrzymano nagrody za ukończenie zlecenia!"
            )

    def show_bestiary(self):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "bestiary"
        self.set_background(self.view_panel, "menu")
        frame = tk.Frame(self.view_panel, bg="#2c1a12")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.85, relheight=0.85)
        
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
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.85, relheight=0.85)
        
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
            item = get_item(inv_item_dict)
            if not item or not hasattr(item, 'stats'): continue
            
            row = tk.Frame(sf.scrollable_frame, bg="#3e2723", bd=2, relief=tk.RAISED)
            row.pack(fill=tk.X, padx=10, pady=5)
            
            lvl = inv_item_dict.get('lvl', 0)
            
            # Nowy system: koszt oparty na mocy przedmiotu, a nie cenie sklepowej
            base_stats = item.stats.get("atk", 0) + item.stats.get("def", 0) + (item.stats.get("hp_max", 0) / 10.0)
            cost = int(base_stats * 50 * (1.9 ** lvl))
            if cost < 10: cost = 10
            
            if lvl >= 9:
                tk.Label(row, text="MAX", font=("Georgia", 14, "bold"), bg="#3e2723", fg="#ff6666").pack(side=tk.RIGHT, padx=15, pady=10)
            else:
                def do_upgrade(i_dict=inv_item_dict, c=cost):
                    if self.player.gold >= c:
                        self.player.gold -= c
                        i_dict["lvl"] = i_dict.get("lvl", 0) + 1
                        self.log_msg(f"Pomyślnie wykuto {get_item(i_dict).name} +{i_dict['lvl']}!")
                        self.update_sidebar()
                        self.show_blacksmith()
                    else:
                        messagebox.showwarning("Brak Złota", "Masz za mało złota na to ulepszenie!")
                        
                # Najpierw pakujemy przycisk do prawej, by etykiety tekstowe go nie wypchnęły poza ekran!
                btn = ctk.CTkButton(row, text=f"Ulepsz ({cost}g)", command=do_upgrade)
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
        win.configure(bg="#2c1a12")
        win.transient(self.root)
        
        tk.Label(win, text="🛠 KONSOLA DEBUGOWANIA (TESTY)", font=("Georgia", 16, "bold"), fg="#f4d03f", bg="#2c1a12").pack(pady=12)
        
        btn_frame = tk.Frame(win, bg="#2c1a12")
        btn_frame.pack(fill=tk.X, )
        
        def add_gold(amount):
            self.player.gold += amount
            self.update_sidebar()
            self.log_msg(f"[DEBUG] Dodano {amount} Złota.")
            lbl_status.configure(text=f"Dodano {amount} Złota! Posiadasz: {self.player.gold}")

        def add_levels(count):
            for _ in range(count):
                req = self.player.get_exp_required()
                self.player.add_exp(req - self.player.exp)
            self.update_sidebar()
            self.log_msg(f"[DEBUG] Awansowano +{count} Poziomów. Obecny Poziom: {self.player.level}.")
            lbl_status.configure(text=f"Awansowano na {self.player.level} Poziom!")

        def full_heal():
            self.player.hp = self.player.get_max_hp()
            self.player.mana = self.player.max_mana
            self.update_sidebar()
            self.log_msg("[DEBUG] Przywrócono pełne HP i Manę.")
            lbl_status.configure(text="Bohater w pełni uleczony!")

        def add_stat_pts(pts):
            self.player.stat_points += pts
            self.update_sidebar()
            self.log_msg(f"[DEBUG] Dodano +{pts} Stat Points.")
            lbl_status.configure(text=f"Dodano +{pts} punktów statystyk! Razem: {self.player.stat_points}")

        ctk.CTkButton(btn_frame, text="+10,000 Złota", fg_color="#3e2723", text_color="#f4d03f", font=("Georgia", 10, "bold"), command=lambda: add_gold(10000)).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="+1,000,000 Złota", fg_color="#3e2723", text_color="#f4d03f", font=("Georgia", 10, "bold"), command=lambda: add_gold(1000000)).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(btn_frame, text="+1 Level", fg_color="#3e2723", text_color="#a8ff9e", font=("Georgia", 10, "bold"), command=lambda: add_levels(1)).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="+10 Leveli", fg_color="#3e2723", text_color="#a8ff9e", font=("Georgia", 10, "bold"), command=lambda: add_levels(10)).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(btn_frame, text="Ulecz HP i Manę", fg_color="#3e2723", text_color="#88ccff", font=("Georgia", 10, "bold"), command=full_heal).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="+50 Pkt Statystyk", fg_color="#3e2723", text_color="#ffcc88", font=("Georgia", 10, "bold"), command=lambda: add_stat_pts(50)).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        input_frame = tk.Frame(win, bg="#1a100b")
        input_frame.pack(fill=tk.X, padx=20, pady=10)

        # Custom Gold
        f_gold = tk.Frame(input_frame, bg="#1a100b")
        f_gold.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f_gold, text="Dodaj Złoto:", fg="white", bg="#1a100b", font=("Georgia", 10, "bold"), width=15, anchor="e").pack(side=tk.LEFT)
        e_gold = tk.Entry(f_gold, bg="#3e2723", fg="white", font=("Georgia", 10), width=12)
        e_gold.pack(side=tk.LEFT, padx=5)
        e_gold.insert(0, "50000")
        def set_custom_gold():
            try:
                val = int(e_gold.get())
                add_gold(val)
            except ValueError:
                lbl_status.configure(text="Błąd: Podaj liczbę!")
        ctk.CTkButton(f_gold, text="Dodaj", fg_color="#5d4037", text_color="white", command=set_custom_gold).pack(side=tk.LEFT)

        # Custom Level
        f_lvl = tk.Frame(input_frame, bg="#1a100b")
        f_lvl.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f_lvl, text="Ustaw Poziom:", fg="white", bg="#1a100b", font=("Georgia", 10, "bold"), width=15, anchor="e").pack(side=tk.LEFT)
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
                    lbl_status.configure(text=f"Ustawiono poziom na {val}")
            except ValueError:
                lbl_status.configure(text="Błąd: Podaj liczbę!")
        ctk.CTkButton(f_lvl, text="Ustaw", fg_color="#5d4037", text_color="white", command=set_custom_level).pack(side=tk.LEFT)

        # Custom Item
        f_item = tk.Frame(input_frame, bg="#1a100b")
        f_item.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f_item, text="Dodaj Przedmiot:", fg="white", bg="#1a100b", font=("Georgia", 10, "bold"), width=15, anchor="e").pack(side=tk.LEFT)
        
        from items import ITEMS_DB
        item_list = [f"{i_id} - {item.name}" for i_id, item in ITEMS_DB.items()]
        cb_item = ttk.Combobox(f_item, values=item_list, font=("Georgia", 9), width=45, state="readonly")
        cb_item.pack(side=tk.LEFT, padx=5)
        if item_list:
            cb_item.current(0)
            
        def set_custom_item():
            sel = cb_item.get()
            if not sel: return
            item_id = sel.split(" - ")[0]
            self.player.add_to_inventory(item_id)
            self.log_msg(f"[DEBUG] Dodano przedmiot: {item_id}")
            lbl_status.configure(text=f"Dodano przedmiot {item_id} do ekwipunku!")
            
        ctk.CTkButton(f_item, text="Dodaj", fg_color="#5d4037", text_color="white", command=set_custom_item).pack(side=tk.LEFT)

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
                lbl_status.configure(text="Wykonano komendę Python!")
            except Exception as err:
                lbl_status.configure(text=f"Błąd: {err}")
        ctk.CTkButton(f_code, text="Wykonaj", fg_color="#7a3333", text_color="white", command=exec_code).pack(side=tk.LEFT)

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
