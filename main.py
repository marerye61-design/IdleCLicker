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

def resource_path(relative_path):
    """ Zwraca absolutną ścieżkę do zasobów (zarówno w trybie deweloperskim, jak i w .exe z PyInstallera) """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

import combat
from player import Player
from quests import get_all_quests
from shop import FantasyShop
from market import Market
import npc_lore
from sound_manager import sounds
from items import get_item, Consumable
import dungeons
from flavor_texts import get_random_flavor_text
import bounties
from bounties import generate_daily_bounties
from gems import GEMS_DB, get_gem, get_random_gem_id, roll_gem_drop, ensure_item_sockets, get_sockets_summary
from achievements import ACHIEVEMENTS_DB
from alchemy import HERBS_DB, MONSTER_INGREDIENTS_DB, RECIPES_DB, roll_monster_ingredient_drop

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
        title_y = max(25, start_y - 82)
        self.tavern_canvas.create_text(title_x, title_y, text="Tawerna 'Pod Skrzydłem Upadłego Anioła'", font=("Georgia", 22, "bold"), fill="#f4d03f")
        
        btn_y = title_y + 36
        
        # 1. Przycisk Tablicy Ogłoszeń (po lewej)
        btn_board = ctk.CTkButton(
            self.tavern_canvas,
            text="📋 TABLICA ZLECEŃ",
            font=("Georgia", 11, "bold"),
            fg_color="#8b4513",
            hover_color="#a0522d",
            text_color="#f4d03f",
            corner_radius=8,
            border_width=2,
            border_color="#f4d03f",
            width=210,
            height=28,
            command=self.open_bounty_board
        )
        self.tavern_canvas.create_window(title_x - 240, btn_y, window=btn_board)
        
        # 2. Przycisk Odpoczynku i Regeneracji Zdrowia (na środku)
        btn_rest = ctk.CTkButton(
            self.tavern_canvas,
            text="🛏️ ODPOCZYNEK (REGENERACJA HP)",
            font=("Georgia", 11, "bold"),
            fg_color="#1e7e34",
            hover_color="#28a745",
            text_color="#ffffff",
            corner_radius=8,
            border_width=2,
            border_color="#2ecc71",
            width=250,
            height=28,
            command=self.open_tavern_rest
        )
        self.tavern_canvas.create_window(title_x, btn_y, window=btn_rest)
        
        # 3. Przycisk Depozytu Nagród u Karczmarza Barnaby (po prawej)
        stash_count = len(getattr(self.player, 'inventory_stash', []))
        stash_text = f"🎁 DEPOZYT ({stash_count} SZT.)" if stash_count > 0 else "🎁 DEPOZYT NAGRÓD"
        stash_col = "#27ae60" if stash_count > 0 else "#3e2723"
        stash_hover = "#2ecc71" if stash_count > 0 else "#4e342e"
        btn_stash = ctk.CTkButton(
            self.tavern_canvas,
            text=stash_text,
            font=("Georgia", 11, "bold"),
            fg_color=stash_col,
            hover_color=stash_hover,
            text_color="#ffffff" if stash_count > 0 else "#f4d03f",
            corner_radius=8,
            border_width=2,
            border_color="#f4d03f",
            width=210,
            height=28,
            command=self.claim_barnaby_stash
        )
        self.tavern_canvas.create_window(title_x + 240, btn_y, window=btn_stash)
        
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
        
        if "passive_name" in npc:
            p_frame = tk.Frame(info_frame, bg="#2c1a12", bd=2, relief=tk.RIDGE)
            p_frame.pack(fill=tk.X, pady=(6, 2), padx=5)
            tk.Label(p_frame, text=f"⚡ Zdolność Pasywna: {npc['passive_name']}", font=("Georgia", 11, "bold"), fg="#f1c40f", bg="#2c1a12").pack(anchor="w", padx=8, pady=(4, 1))
            tk.Label(p_frame, text=npc["passive_desc"], font=("Georgia", 10, "italic"), fg="#ecf0f1", bg="#2c1a12", wraplength=520, justify=tk.LEFT).pack(anchor="w", padx=8, pady=(1, 4))
        
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
            
        if npc_id == "innkeeper":
            stash_count = len(getattr(self.player, 'inventory_stash', []))
            if stash_count > 0:
                btn_stash = ctk.CTkButton(
                    btn_frame,
                    text=f"🎁 [DEPOZYT NAGRÓD] Odbierz nagrody ({stash_count} szt.)",
                    font=("Georgia", 12, "bold"),
                    fg_color="#27ae60",
                    hover_color="#2ecc71",
                    text_color="#ffffff",
                    command=lambda: (win.destroy(), self.claim_barnaby_stash())
                )
                btn_stash.pack(fill=tk.X, padx=30, pady=4)
            else:
                btn_stash = ctk.CTkButton(
                    btn_frame,
                    text="🎁 [DEPOZYT NAGRÓD] Skrytka na nagrody (Pusto: 0 szt.)",
                    font=("Georgia", 11, "bold"),
                    fg_color="#3e2723",
                    hover_color="#4e342e",
                    text_color="#f4d03f",
                    command=lambda: say("Twój depozyt jest obecnie pusty, przyjacielu! Jeśli twój ekwipunek będzie w pełni zapełniony (80/80 slotów), wszystkie zdobyte nagrody ze zleceń, zadań i lochów bezpiecznie przechowam tutaj za ladą.")
                )
                btn_stash.pack(fill=tk.X, padx=30, pady=4)
                
            btn_rest_dialog = ctk.CTkButton(
                btn_frame,
                text="🛏️ [ODPOCZYNEK] Wynajmij pokój i zregeneruj siły witalne (HP)",
                font=("Georgia", 12, "bold"),
                fg_color="#1e7e34",
                hover_color="#28a745",
                text_color="#ffffff",
                command=lambda: (win.destroy(), self.open_tavern_rest())
            )
            btn_rest_dialog.pack(fill=tk.X, padx=30, pady=4)
            
            btn_bounties = ctk.CTkButton(
                btn_frame,
                text="📋 [TABLICA OGŁOSZEŃ] Zobacz dzisiejsze zlecenia",
                font=("Georgia", 12, "bold"),
                fg_color="#d35400",
                hover_color="#e67e22",
                text_color="#ffffff",
                command=lambda: (win.destroy(), self.open_bounty_board())
            )
            btn_bounties.pack(fill=tk.X, padx=30, pady=5)
            
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
        
        # Opcje rekrutacji i wyboru towarzysza w walce (tylko dla kompanów)
        if npc_id != "innkeeper":
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
        assets_dir = resource_path("assets")
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
        portraits_dir = resource_path(os.path.join("assets", "portraits"))
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
        items_dir = resource_path(os.path.join("assets", "items"))
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
        win.geometry("380x480")
        win.configure(bg="#2c1a12")
        win.transient(self.root)
        win.grab_set()
        
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 380) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 480) // 2
        win.geometry(f"+{x}+{y}")
        
        tk.Label(win, text="WYBIERZ ZAPIS GRY:", font=("Georgia", 14, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=(12, 2))
        tk.Label(win, text="Kliknij dwukrotnie lub zaznacz i kliknij [Wczytaj]", font=("Georgia", 9, "italic"), bg="#2c1a12", fg="#aaaaaa").pack(pady=(0, 8))
        
        listbox = tk.Listbox(
            win, 
            bg="#1a100b", 
            fg="white", 
            selectbackground="#8b4513", 
            selectforeground="#f4d03f", 
            activestyle="none",
            highlightcolor="#f4d03f",
            highlightbackground="#5c3a21",
            highlightthickness=2,
            bd=3,
            relief=tk.SUNKEN,
            font=("Georgia", 12, "bold")
        )
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        for s in saves:
            listbox.insert(tk.END, f"  ⚔️  {s.replace('.pkl', '')}")
            
        def load_selected(event=None):
            sel = listbox.curselection()
            if sel:
                idx = sel[0]
                filepath = os.path.join(SAVES_DIR, saves[idx])
                with open(filepath, 'rb') as f:
                    p = pickle.load(f)
                    if getattr(p, 'version', '1.0') != '1.1':
                        if not messagebox.askyesno("Ostrzeżenie", "Ten zapis pochodzi ze starszej wersji gry.\nMoże to skutkować błędami. Czy na pewno chcesz wczytać?"):
                            return
                    p.migrate()
                    p.update_offline_progress()
                self.player = p
                self.current_save_path = filepath
                sounds.play_ui_click()
                win.destroy()
                self.build_main_ui()
                
        listbox.bind("<Double-Button-1>", load_selected)
        listbox.bind("<Return>", load_selected)
        win.bind("<Return>", load_selected)
        
        if saves:
            listbox.select_set(0)
            listbox.focus_set()
            
        btn_box = tk.Frame(win, bg="#2c1a12")
        btn_box.pack(fill=tk.X, padx=20, pady=12)
        
        ctk.CTkButton(btn_box, text="Wczytaj Zapis", font=("Georgia", 11, "bold"), fg_color="#27ae60", hover_color="#2ecc71", text_color="#ffffff", command=load_selected).pack(fill=tk.X, pady=3)
        ctk.CTkButton(btn_box, text="Anuluj", font=("Georgia", 10), fg_color="#3e2723", hover_color="#4e342e", text_color="#aaaaaa", command=win.destroy).pack(fill=tk.X, pady=2)

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
        
        self.sidebar = tk.Frame(self.container, width=290, bg="#1a100b")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Ramka na statystyki i pasek zdrowia
        stats_box = tk.Frame(self.sidebar, bg="#1a100b")
        stats_box.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.lbl_stats_top = tk.Label(stats_box, text="", font=("Georgia", 10, "bold"), justify=tk.LEFT, bg="#1a100b", fg="#f4d03f", anchor="nw", wraplength=270)
        self.lbl_stats_top.pack(fill=tk.X)
        
        # Pasek Zdrowia Bohatera w panelu bocznym
        self.sidebar_hp_canvas = tk.Canvas(stats_box, width=265, height=22, bg="#1a100b", highlightthickness=0)
        self.sidebar_hp_canvas.pack(fill=tk.X, pady=(4, 6))
        
        self.lbl_stats = tk.Label(stats_box, text="", font=("Georgia", 10, "bold"), justify=tk.LEFT, bg="#1a100b", fg="#f4d03f", anchor="nw", wraplength=270)
        self.lbl_stats.pack(fill=tk.X)
        
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
        ctk.CTkButton(nav_frame, text="Kowal (Kuźnia & Klejnoty)", command=self.show_blacksmith).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Alchemia (Ogród Domci)", command=self.show_alchemy).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Osiągnięcia (Trofea)", command=self.show_achievements).pack(fill=tk.X, padx=10, pady=3)
        ctk.CTkButton(nav_frame, text="Miasto (Tawerna)", command=self.show_tavern).pack(fill=tk.X, padx=10, pady=3)
        self.btn_audio = ctk.CTkButton(nav_frame, text="🔊 Dźwięki: WŁ" if sounds.enabled else "🔇 Dźwięki: WYŁ", fg_color="#3e2723", hover_color="#5d4037", text_color="#f4d03f", command=self.toggle_audio_sfx)
        self.btn_audio.pack(fill=tk.X, padx=10, pady=3)
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

    def toggle_audio_sfx(self):
        is_on = sounds.toggle_sound()
        if hasattr(self, 'btn_audio') and self.btn_audio.winfo_exists():
            self.btn_audio.configure(text="🔊 Dźwięki: WŁ" if is_on else "🔇 Dźwięki: WYŁ")
        if is_on:
            sounds.play_ui_click()

    def update_sidebar(self):
        if not hasattr(self, "lbl_stats") or not self.lbl_stats.winfo_exists(): return
        if not self.player: return
        t_atk = self.player.get_total_atk()
        t_def = self.player.get_total_def()
        t_crit = self.player.get_total_crit()
        t_hp = self.player.get_max_hp()
        cur_hp = max(0, min(t_hp, int(self.player.hp)))
        
        active_c = getattr(self.player, 'active_companion', None)
        from npc_lore import NPC_DB
        active_name = NPC_DB.get(active_c, {}).get('name', active_c).split(',')[0] if active_c else "Brak"
        unlocked_count = len(self.player.party)
        
        comp_line = f"Aktywny: {active_name}"
        if active_c and active_c in NPC_DB and "passive_name" in NPC_DB[active_c]:
            p_name = NPC_DB[active_c].get('passive_name', '')
            p_short = NPC_DB[active_c].get('passive_short', '')
            comp_line += f"\n⚡ {p_name}:\n  {p_short}"
        
        stats_top = f"""✦ BOHATER ✦
Imię: {self.player.name}
Poz: {self.player.level}
EXP: {self.player.exp} / {self.player.get_exp_required()}
Złoto: {self.player.gold}
Pasywne: {self.player.stats['gold_per_sec']}/s"""

        if hasattr(self, 'lbl_stats_top') and self.lbl_stats_top.winfo_exists():
            self.lbl_stats_top.configure(text=stats_top.strip())

        # Rysowanie paska zdrowia w panelu bocznym
        if hasattr(self, 'sidebar_hp_canvas') and self.sidebar_hp_canvas.winfo_exists():
            self.sidebar_hp_canvas.delete("all")
            w = 265
            h = 22
            ratio = max(0.0, min(1.0, cur_hp / t_hp)) if t_hp > 0 else 0.0
            fill_w = int((w - 4) * ratio)
            
            # Kolor paska zależny od stanu zdrowia
            if ratio > 0.5:
                bar_color = "#22c55e" # Zielony
            elif ratio > 0.25:
                bar_color = "#eab308" # Żółty/bursztynowy
            else:
                bar_color = "#ef4444" # Czerwony
                
            # Tło paska i złocisto-brązowa ramka
            self.sidebar_hp_canvas.create_rectangle(1, 1, w - 1, h - 1, fill="#1a100b", outline="#8b5a2b", width=2)
            self.sidebar_hp_canvas.create_rectangle(3, 3, w - 3, h - 3, fill="#450a0a", outline="")
            if fill_w > 0:
                self.sidebar_hp_canvas.create_rectangle(3, 3, 3 + fill_w, h - 3, fill=bar_color, outline="")
                
            # Tekst na środku paska
            hp_text = f"❤ HP: {cur_hp} / {t_hp}"
            self.sidebar_hp_canvas.create_text(w // 2, h // 2, text=hp_text, fill="white", font=("Georgia", 9, "bold"))

        buff_str = ""
        if hasattr(self.player, 'active_buffs') and self.player.active_buffs:
            from alchemy import RECIPES_DB
            b_list = []
            for b_id, f_count in self.player.active_buffs.items():
                r_icon = RECIPES_DB.get(b_id, {}).get("icon", "✨")
                r_name = RECIPES_DB.get(b_id, {}).get("name", b_id).replace("Eliksir ", "").replace("Mikstura ", "")
                b_list.append(f"{r_icon} {r_name} ({f_count}w)")
            buff_str = "\n\n✦ AKTYWNE ELIKSIRY ✦\n" + "\n".join(b_list)

        stats_bot = f"""✦ WALKA ✦
ATK: {t_atk}
DEF: {t_def}
CRIT: {t_crit}%
Stat-PKT: {self.player.stat_points}

✦ DRUŻYNA (Limit 1) ✦
{comp_line}
Zrekrutowano: {unlocked_count}/6{buff_str}"""

        self.lbl_stats.configure(text=stats_bot.strip())

    def log_msg(self, msg):
        if not hasattr(self, "log_text") or not self.log_text.winfo_exists(): return
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.update_sidebar()

    def schedule_combat_task(self, delay_ms, func):
        if not hasattr(self, 'combat_after_ids'):
            self.combat_after_ids = []
        aid = self.root.after(delay_ms, func)
        self.combat_after_ids.append(aid)
        return aid

    def cancel_all_combat_timers(self):
        if hasattr(self, 'combat_after_ids'):
            for aid in list(self.combat_after_ids):
                try:
                    self.root.after_cancel(aid)
                except Exception:
                    pass
            self.combat_after_ids.clear()

    def clear_view(self):
        self.cancel_all_combat_timers()
        if hasattr(self, 'alchemy_timer_id') and self.alchemy_timer_id:
            try:
                self.root.after_cancel(self.alchemy_timer_id)
            except Exception:
                pass
            self.alchemy_timer_id = None
        for widget in self.view_panel.winfo_children():
            if hasattr(self, 'bg_label') and widget == self.bg_label:
                continue
            if hasattr(self, 'trip_bg_canvas') and widget == self.trip_bg_canvas:
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
        self.cancel_all_combat_timers()
        self.enemy = enemy
        self.setup_combat_ui()
        self.start_combat()

    def setup_combat_ui(self):
        self.clear_view()
        
        if self.current_view == "dungeon" and self.current_dungeon:
            d_id = self.current_dungeon.d_id if hasattr(self.current_dungeon, 'd_id') else str(self.current_dungeon)
            d_bg_key = f"dungeon_{d_id}"
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
        sounds.play_potion()
        
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
        self.loop_combat = False
        self.cancel_all_combat_timers()
        self.log_msg("Uciekłeś z pola bitwy na z góry upatrzone pozycje!")
        if hasattr(self, 'btn_potion') and self.btn_potion and self.btn_potion.winfo_exists():
            try:
                self.btn_potion.pack_forget()
            except Exception:
                pass
        
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
            
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas or not self.combat_canvas.winfo_exists():
            self.setup_combat_ui()
            
        self.potions_used_this_battle = 0
        if hasattr(self, 'btn_attack') and self.btn_attack and self.btn_attack.winfo_exists():
            try:
                self.btn_attack.configure(text="UCIEKNIJ Z WALKI", fg_color="#7a3333", text_color="white", command=self.flee_combat, state=tk.NORMAL)
            except Exception:
                pass
        self.loop_combat = True
        
        potions = len([i for i in self.player.inventory if i["id"] == "pot_hp"])
        if hasattr(self, 'btn_potion') and self.btn_potion and self.btn_potion.winfo_exists():
            try:
                if potions > 0:
                    self.btn_potion.configure(text=f"Wypij Miksturę ({potions}) [Użyto: 0/3]")
                    self.btn_potion.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)
                else:
                    self.btn_potion.pack_forget()
            except Exception:
                pass
            
        self.combat_active = True
        self.enemy_cur_hp = self.enemy.max_hp
        self.combat_turn = 0
        
        if hasattr(self, 'combat_canvas') and self.combat_canvas and self.combat_canvas.winfo_exists():
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
                        boss_p = resource_path(f"assets/{self.enemy.img_key}.jpg")
                        if os.path.exists(boss_p):
                            img = Image.open(boss_p)
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
        self.schedule_combat_task(350, self.combat_tick)

    def combat_tick(self):
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas.winfo_exists() or not self.combat_active or not getattr(self, 'loop_combat', True):
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
        
        sounds.play_sword()
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
            self.schedule_combat_task(16, lambda: self.animate_sword_swing(steps_left - 1, total_steps, start_x, start_y, target_x, target_y, start_angle, end_angle))
        else:
            self.combat_canvas.delete("sword")
            self.combat_canvas.move("player_p", -15, 0) # Wróć portretem
            self.apply_player_damage()

    def apply_player_damage(self):
        if not self.combat_active:
            return
            
        is_first = (self.combat_turn == 0)
        dmg, is_crit = combat.calculate_player_dmg(self.player, self.enemy, is_first_turn=is_first)
        self.enemy_cur_hp -= dmg
        
        if is_first and getattr(self.player, 'active_companion', None) == 'eczme':
            self.log_msg("🏐 Pasywka Eczmego: Serwis z wyskoku zadaje +25% obrażeń w 1. rundzie!")
        
        if is_crit:
            sounds.play_crit()
            self.player.record_achievement_stat("total_crits", 1, mode="add")
            self.float_text(920, 190, f"-{dmg} KRYT!", "#ff3333")
            if getattr(self.player, 'active_buffs', None) and self.player.active_buffs.get("elixir_psychedelic", 0) > 0:
                self.float_text(450, 120, "🌀 PSYCHODELICZNY TRANS!", "#a29bfe")
        else:
            sounds.play_hit()
            self.float_text(920, 190, f"-{dmg}", "orange")
        
        if self.enemy_cur_hp <= 0:
            self.enemy_cur_hp = 0
            self.draw_health_bars()
            self.schedule_combat_task(1000, lambda: self.end_combat(True))
            return
            
        self.draw_health_bars()
        
        # Pasywka Domci: "Mistyczna Prędkość" (+8% szybkości ataku -> 8% szansy na natychmiastowy dodatkowy cios)
        if getattr(self.player, 'active_companion', None) == 'domcia' and random.random() < 0.08:
            self.log_msg("🍄 Pasywka Domci: Wyostrzona szybkość ataku pozwala na natychmiastowy dodatkowy cios!")
            self.float_text(450, 150, "SZYBKI ATAK!", "#1abc9c")
            self.schedule_combat_task(220, self.animate_player_attack)
            return

        self.combat_turn += 1
        # Przerwa po udanym uderzeniu gracza przed ruchem wroga (przyspieszona o 40%)
        self.schedule_combat_task(270, self.combat_tick)

    def draw_boss_mace(self, x, y, angle_deg=0):
        # Wczytanie i renderowanie dedykowanej grafiki maczugi Ptysia z rotacją
        if not hasattr(self, '_ptys_mace_pil'):
            try:
                from PIL import Image
                p = resource_path("assets/ptys_mace.png")
                if os.path.exists(p):
                    self._ptys_mace_pil = Image.open(p).convert("RGBA")
                else:
                    self._ptys_mace_pil = None
            except Exception:
                self._ptys_mace_pil = None
                
        if getattr(self, '_ptys_mace_pil', None):
            try:
                from PIL import Image, ImageTk
                rotated = self._ptys_mace_pil.rotate(angle_deg, resample=Image.BICUBIC, expand=True)
                tk_mace = ImageTk.PhotoImage(rotated)
                self._cur_mace_tk = tk_mace
                self.combat_canvas.create_image(x, y, image=tk_mace, tags="boss_mace", anchor=tk.CENTER)
                return
            except Exception:
                pass

        # Zapasowy render wektorowy w razie braku pliku
        parts = [
            ([x-50, y-4, x+10, y-4, x+10, y+4, x-50, y+4], {"fill": "#5c2e0e", "outline": "#3e2723", "width": 2}, True),
            ([x-40, y-5, x-25, y-5, x-25, y+5, x-40, y+5], {"fill": "#8d6e63", "outline": "#4e342e", "width": 1}, True),
            ([x-10, y-5, x-6, y-5, x-6, y+5, x-10, y+5], {"fill": "#78909c", "outline": "#37474f", "width": 1}, True),
            ([x+2, y-5, x+6, y-5, x+6, y+5, x+2, y+5], {"fill": "#78909c", "outline": "#37474f", "width": 1}, True),
            ([x+10, y-14, x+26, y-14, x+36, y-6, x+36, y+6, x+26, y+14, x+10, y+14, x+4, y+6, x+4, y-6], 
             {"fill": "#37474f", "outline": "#263238", "width": 2}, True),
            ([x+14, y-9, x+26, y-9, x+30, y, x+26, y+9, x+14, y+9, x+10, y], 
             {"fill": "#546e7a", "outline": "#37474f", "width": 1}, True),
            ([x+16, y-14, x+20, y-26, x+24, y-14], {"fill": "#b0bec5", "outline": "#455a64", "width": 1}, True),
            ([x+16, y+14, x+20, y+26, x+24, y+14], {"fill": "#b0bec5", "outline": "#455a64", "width": 1}, True),
            ([x+36, y-5, x+48, y, x+36, y+5], {"fill": "#eceff1", "outline": "#455a64", "width": 1}, True),
            ([x+28, y-12, x+40, y-20, x+34, y-6], {"fill": "#b0bec5", "outline": "#455a64", "width": 1}, True),
            ([x+28, y+12, x+40, y+20, x+34, y+6], {"fill": "#b0bec5", "outline": "#455a64", "width": 1}, True),
            ([x-54, y-6, x-50, y-6, x-50, y+6, x-54, y+6], {"fill": "#78909c", "outline": "#37474f", "width": 1}, True)
        ]
        
        for coords, kwargs, is_poly in parts:
            rot_coords = []
            for i in range(0, len(coords), 2):
                nx, ny = self.rotate_point(coords[i], coords[i+1], x, y, angle_deg)
                rot_coords.extend([nx, ny])
            
            if is_poly:
                self.combat_canvas.create_polygon(*rot_coords, tags="boss_mace", **kwargs)
            else:
                self.combat_canvas.create_line(*rot_coords, tags="boss_mace", **kwargs)

    def draw_boss_fireball(self, x, y, angle_deg=0):
        # Wczytanie i renderowanie wirującej kuli ognia Kollmana
        if not hasattr(self, '_kollman_fb_pil'):
            try:
                from PIL import Image
                p = resource_path("assets/kollman_fireball.png")
                if os.path.exists(p):
                    self._kollman_fb_pil = Image.open(p).convert("RGBA")
                else:
                    self._kollman_fb_pil = None
            except Exception:
                self._kollman_fb_pil = None
                
        if getattr(self, '_kollman_fb_pil', None):
            try:
                from PIL import Image, ImageTk
                rotated = self._kollman_fb_pil.rotate(angle_deg, resample=Image.BICUBIC, expand=True)
                tk_fb = ImageTk.PhotoImage(rotated)
                self._cur_fb_tk = tk_fb
                self.combat_canvas.create_image(x, y, image=tk_fb, tags="boss_fireball", anchor=tk.CENTER)
                return
            except Exception:
                pass

        # Zapasowy render wektorowy
        self.combat_canvas.create_oval(x-35, y-35, x+35, y+35, fill="#ff4500", outline="#ffd700", width=3, tags="boss_fireball")
        self.combat_canvas.create_oval(x-20, y-20, x+20, y+20, fill="#ffff00", outline="#ffffff", width=2, tags="boss_fireball")

    def animate_enemy_attack(self):
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas.winfo_exists() or not self.combat_active: return
        
        # Specjalne unikalne ataki dla bossów lochów
        is_ptys = getattr(self.enemy, 'img_key', '') == 'boss_ptys' or getattr(self.enemy, 'e_id', '') == 'boss_ptys'
        is_kollman = getattr(self.enemy, 'img_key', '') == 'boss_kollman' or getattr(self.enemy, 'e_id', '') == 'boss_kollman'
        
        if is_ptys:
            self.combat_canvas.move("enemy_p", -20, 0)
            start_x, start_y = 920, 240
            target_x, target_y = 270, 240
            start_angle = -35  # Odchylona głownią do tyłu (faza zamachu)
            end_angle = 45     # Pochylona delikatnie do przodu (faza uderzenia w gracza)
            steps = 18
            sounds.play_sword()
            self.animate_boss_mace_swing(steps, steps, start_x, start_y, target_x, target_y, start_angle, end_angle)
        elif is_kollman:
            self.combat_canvas.move("enemy_p", -20, 0)
            start_x, start_y = 920, 240
            target_x, target_y = 270, 240
            steps = 18
            sounds.play_sword()
            self.animate_boss_fireball(steps, steps, start_x, start_y, target_x, target_y)
        else:
            self.combat_canvas.move("enemy_p", -30, 0)
            # Ośrodek portretu gracza to 270, 240
            center_x, center_y = 270, 240
            self.combat_canvas.create_line(center_x-40, center_y-40, center_x+40, center_y+40, fill="#e74c3c", width=6, tags="scratch")
            self.combat_canvas.create_line(center_x-20, center_y-50, center_x+60, center_y+30, fill="#c0392b", width=6, tags="scratch")
            self.combat_canvas.create_line(center_x-60, center_y-30, center_x+20, center_y+50, fill="#e74c3c", width=6, tags="scratch")
            self.schedule_combat_task(180, self.clear_scratch_and_apply_damage)

    def animate_boss_mace_swing(self, steps_left, total_steps, start_x, start_y, target_x, target_y, start_angle, end_angle):
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas.winfo_exists():
            return
            
        if not self.combat_active:
            self.combat_canvas.delete("boss_mace")
            return
            
        if steps_left > 0:
            self.combat_canvas.delete("boss_mace")
            step = (total_steps - steps_left + 1)
            t = step / total_steps
            
            # Lot po łuku parabolicznym z prawej (wróg) do lewej (gracz)
            curr_x = start_x + (target_x - start_x) * t
            curr_y = start_y + (target_y - start_y) * t - 35 * math.sin(t * math.pi)
            current_angle = start_angle + (end_angle - start_angle) * t
            
            self.draw_boss_mace(curr_x, curr_y, current_angle)
            self.schedule_combat_task(16, lambda: self.animate_boss_mace_swing(steps_left - 1, total_steps, start_x, start_y, target_x, target_y, start_angle, end_angle))
        else:
            self.combat_canvas.delete("boss_mace")
            self.combat_canvas.move("enemy_p", 20, 0) # Wróć portretem
            self.clear_scratch_and_apply_damage()

    def animate_boss_fireball(self, steps_left, total_steps, start_x, start_y, target_x, target_y):
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas.winfo_exists():
            return
            
        if not self.combat_active:
            self.combat_canvas.delete("boss_fireball")
            return
            
        if steps_left > 0:
            self.combat_canvas.delete("boss_fireball")
            step = (total_steps - steps_left + 1)
            t = step / total_steps
            
            # Lot kuli ognia prosto z lekkim spiralnym falowaniem
            curr_x = start_x + (target_x - start_x) * t
            curr_y = start_y + (target_y - start_y) * t + 12 * math.sin(t * math.pi * 2)
            current_angle = (t * 720) % 360  # wirujący płomień
            
            self.draw_boss_fireball(curr_x, curr_y, current_angle)
            self.schedule_combat_task(16, lambda: self.animate_boss_fireball(steps_left - 1, total_steps, start_x, start_y, target_x, target_y))
        else:
            self.combat_canvas.delete("boss_fireball")
            self.combat_canvas.move("enemy_p", 20, 0) # Wróć portretem
            self.clear_scratch_and_apply_damage()
        
    def clear_scratch_and_apply_damage(self):
        if not hasattr(self, 'combat_canvas') or not self.combat_canvas.winfo_exists(): return
        self.combat_canvas.delete("scratch")
        self.combat_canvas.delete("boss_mace")
        self.combat_canvas.delete("boss_fireball")
        
        is_ptys = getattr(self.enemy, 'img_key', '') == 'boss_ptys' or getattr(self.enemy, 'e_id', '') == 'boss_ptys'
        is_kollman = getattr(self.enemy, 'img_key', '') == 'boss_kollman' or getattr(self.enemy, 'e_id', '') == 'boss_kollman'
        if not (is_ptys or is_kollman):
            self.combat_canvas.move("enemy_p", 30, 0) # Wróć portretem dla standardowych potworów
        
        if not self.combat_active:
            return
            
        dmg = combat.calculate_enemy_dmg(self.enemy, self.player)
        self.player.hp -= dmg
        sounds.play_enemy_hit()
        self.float_text(270, 190, f"-{dmg}", "red")
        
        if self.player.hp <= 0:
            self.player.hp = 0
            self.draw_health_bars()
            self.update_sidebar()
            self.schedule_combat_task(1000, lambda: self.end_combat(False))
            return
            
        self.draw_health_bars()
        self.update_sidebar()
        self.combat_turn += 1
        # Przerwa po uderzeniu wroga przed ruchem gracza (przyspieszona o 40%)
        self.schedule_combat_task(330, self.combat_tick)

    def end_combat(self, won):
        self.combat_active = False
        t_hp = self.player.get_max_hp()
        
        if not won:
            self.player.hp = 1
            self.log_msg(f"[{self.enemy.name}] Pokonał Cię! Ledwo uchodzisz z życiem (1 HP). Użyj mikstury w ekwipunku!")
            save_game(self.player, self.current_save_path)
            self.update_sidebar()
            if hasattr(self, 'btn_attack') and self.btn_attack and self.btn_attack.winfo_exists():
                try:
                    self.btn_attack.configure(state=tk.NORMAL)
                except Exception:
                    pass
                
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
            
            
            # Pasywka Maślaka: "Słodki Łup" (+15% na podwójne złoto, +5% na miksturę)
            if getattr(self.player, 'active_companion', None) == "maslak":
                if random.random() < 0.15:
                    gold_gain *= 2
                    self.log_msg("🍩 Pasywka Maślaka: Wywęszyłeś podwójną sakiewkę złota!")
                if random.random() < 0.05:
                    succ, st = self.player.add_to_inventory("pot_hp", is_reward=True)
                    if st == "stashed":
                        self.log_msg("🍩 Pasywka Maślaka: Mikstura Zdrowia trafiła do depozytu Barnaby (pełny ekwipunek)!")
                    else:
                        self.log_msg("🍩 Pasywka Maślaka: Znalazłeś dodatkową Miksturę Zdrowia!")
            
            # Postęp w zleceniach z Tablicy Ogłoszeń
            for b in getattr(self.player, 'bounties', []):
                if b.status == 'IN_PROGRESS' and b.target_type == 'kill' and b.target_name == e_name:
                    if b.add_progress(1):
                        self.log_msg(f"📋 Zlecenie z tablicy ukończone: '{b.title}'! Odbierz nagrodę u Karczmarza.")
                    else:
                        self.log_msg(f"📋 Postęp zlecenia '{b.title}': {b.current_count}/{b.target_count}")
            
            # Zliczanie statystyk do osiągnięć
            self.player.record_achievement_stat("total_kills", 1, mode="add")
            self.player.record_achievement_stat("total_gold_earned", gold_gain, mode="add")
            if getattr(self, 'is_dungeon_boss', False):
                self.player.record_achievement_stat("dungeons_cleared", 1, mode="add")
                if "ptyś" in e_name.lower() or "ptys" in e_name.lower():
                    self.player.record_achievement_stat("boss_ptys_kills", 1, mode="add")
                elif "kollman" in e_name.lower():
                    self.player.record_achievement_stat("boss_kollman_kills", 1, mode="add")

            # Konsumpcja aktywnych eliksirów (1 walka)
            expired_buffs = self.player.tick_active_buffs()
            if expired_buffs:
                for b_id in expired_buffs:
                    r_name = RECIPES_DB.get(b_id, {}).get("name", b_id)
                    self.log_msg(f"⏳ Działanie eliksiru '{r_name}' dobiegło końca.")

            # Drop Magicznych Klejnotów (3% ze zwykłych potworów od 15 lvl, 10% z bossa lochu od 1 lvl)
            gem_drop_id = roll_gem_drop(is_boss=getattr(self, 'is_dungeon_boss', False), player_level=self.player.level)
            if gem_drop_id:
                gem_data = GEMS_DB[gem_drop_id]
                succ, st = self.player.add_to_inventory(gem_drop_id, is_reward=True)
                sounds.play_quest_complete()
                if st == "stashed":
                    self.log_msg(f"🔮 {gem_data.icon} DROP KLEJNOTU! {gem_data.name} trafił do depozytu Barnaby (pełny ekwipunek)!")
                else:
                    self.log_msg(f"🔮 {gem_data.icon} RZADKI DROP KLEJNOTU! Zdobyłeś {gem_data.name} ({gem_data.get_stat_summary()})!")

            # Drop Składników Alchemicznych z potworów
            ing_drop_id = roll_monster_ingredient_drop(e_name)
            if ing_drop_id:
                ing_data = MONSTER_INGREDIENTS_DB[ing_drop_id]
                succ, st = self.player.add_to_inventory(ing_drop_id, is_reward=True)
                if st == "stashed":
                    self.log_msg(f"🧪 {ing_data.icon} Składnik Alchemiczny: {ing_data.name} trafił do depozytu Barnaby!")
                else:
                    self.log_msg(f"🧪 {ing_data.icon} Składnik Alchemiczny: Zdobyto {ing_data.name}!")

            self.log_msg(f"ZWYCIĘSTWO! Otrzymujesz {exp_gain} EXP i {gold_gain} Złota. (HP: {int(self.player.hp)}/{t_hp})")
            self.player.gold += gold_gain
            
            old_lvl = self.player.level
            self.player.add_exp(exp_gain)
            sounds.play_coin()
            if self.player.level > old_lvl:
                sounds.play_level_up()
            
            if getattr(self, 'is_dungeon_boss', False):
                # Postęp w zleceniu lochu
                for b in getattr(self.player, 'bounties', []):
                    if b.status == 'IN_PROGRESS' and b.target_type == 'dungeon':
                        if b.add_progress(1):
                            self.log_msg(f"📋 Zlecenie z tablicy ukończone: '{b.title}'! Odbierz nagrodę u Karczmarza.")
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
                            
                    drop_item_dict = {"id": drop_id, "lvl": 0, "modifier": chosen_mod_id, "sockets": [None, None]}
                    succ, st = self.player.add_to_inventory(drop_item_dict, is_reward=True)
                    item = get_item({"id": drop_id, "modifier": chosen_mod_id})
                    
                    if item:
                        rarity = getattr(item, 'rarity', 'Zwykły')
                        rarity_prefix = "🌟 [LEGENDARDNY] " if rarity == "Legendarny" else ("🌌 [MITYCZNY] " if rarity == "Mityczny" else "")
                        if st == "stashed":
                            self.log_msg(f"*** {rarity_prefix}DROP Z LOCHU! {item.name} trafił do depozytu Barnaby (pełny ekwipunek)! ***")
                            messagebox.showinfo(
                                "🌟 ARTEFAKT Z LOCHU! (DEPOZYT) 🌟", 
                                f"Po pokonaniu bossa w lochu {d.name} odnalazłeś niezwykły artefakt!\n\nPrzedmiot: {item.name} [{rarity.upper()}]\n\n⚠️ Twój ekwipunek jest pełny! Przedmiot został bezpiecznie złożony w depozycie u Karczmarza Barnaby w Tawernie."
                            )
                        else:
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
                    succ, st = self.player.add_to_inventory("pot_hp", is_reward=True)
                    if st == "stashed":
                        self.log_msg("*** DROP Z POTWORA! Mikstura Życia trafiła do depozytu u Karczmarza (pełny ekwipunek) ***")
                    else:
                        self.log_msg("*** DROP Z POTWORA! Znalazłeś: Mikstura Życia ***")
                
            if self.player.level > old_lvl:
                self.log_msg(f"*** AWANS NA {self.player.level} POZIOM! Otrzymujesz pasywnie bonusy do statystyk! ***")
            else:
                req = self.player.get_exp_required()
                rem = req - self.player.exp
                self.log_msg(f"(Brakuje: {rem} EXP do {self.player.level+1} poziomu)")
            
            self.player.stats["total_clicks"] += 1
            
            if getattr(self, 'loop_combat', False) and not getattr(self, 'is_dungeon_boss', False) and self.current_view in ("expedition", "dungeon"):
                # Generujemy tego samego potwora ponownie
                from combat import Enemy
                import copy
                
                # Odtwarzamy potwora z pełnym HP
                self.enemy.hp = self.enemy.max_hp
                
                self.schedule_combat_task(1500, self.start_combat)
            else:
                # Wróć do ekranu wyboru po krótkiej pauzie by gracz mógł przeczytać log
                self.schedule_combat_task(2000, self.show_dungeons if self.current_view == "dungeon" else self.show_expedition)

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
        sounds.play_dungeon_enter()
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

    def debug_fight_boss(self, boss_id, skip_cinematic=True):
        """Natychmiastowe rozpoczęcie pojedynku z bossem lochu w celach testowych."""
        self.clear_view()
        self.current_view = "dungeon"
        
        # Przypisanie obiektu Dungeon
        d_obj = dungeons.DUNGEONS[0] if boss_id == "boss_ptys" else dungeons.DUNGEONS[1]
        for d in dungeons.DUNGEONS:
            if getattr(d, 'hardcoded_boss', None) == boss_id:
                d_obj = d
                break
        self.current_dungeon = d_obj
        self.is_dungeon_boss = True
        
        boss = combat.get_hardcoded_boss(boss_id, getattr(self.player, 'level', 5))
        self.enemy = boss
        self.log_msg(f"[DEBUG] Szybka walka testowa z: {boss.name}")
        
        if skip_cinematic:
            self.setup_combat_ui()
            self.start_combat()
        else:
            self.play_boss_cinematic(boss, lambda: self.start_combat())

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
            sounds.play_boss_intro()
            
            # Wczytywanie portretu bossa, staramy się go wycentrować
            img_key = boss.img_key
            img_cache_key = f"{img_key}_cinematic"
            if img_cache_key not in self.portraits:
                try:
                    from PIL import Image, ImageTk
                    cinematic_p = resource_path(f"assets/{img_key}.jpg")
                    if os.path.exists(cinematic_p):
                        img = Image.open(cinematic_p)
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

    def show_equipment(self, selected_item_dict=None, is_equipped_slot=None, current_page=None):
        if self.is_busy(): return
        
        # Paginacja ekwipunku (maks 4 strony po 20 slotów = 80 slotów)
        if not hasattr(self, 'inv_current_page') or self.inv_current_page is None:
            self.inv_current_page = 1
            
        if current_page is not None:
            self.inv_current_page = current_page
        elif selected_item_dict in self.player.inventory:
            sel_idx = self.player.inventory.index(selected_item_dict)
            self.inv_current_page = (sel_idx // 20) + 1
            
        self.inv_current_page = max(1, min(4, self.inv_current_page))
        
        if self.current_view == "equipment" and hasattr(self, 'eq_main_frame') and self.eq_main_frame.winfo_exists():
            for w in self.eq_main_frame.winfo_children():
                w.destroy()
            main_frame = self.eq_main_frame
        else:
            self.clear_view()
            self.current_view = "equipment"
            self.set_background(self.view_panel, "menu")
            
            main_frame = tk.Frame(self.view_panel, bg="#2c1a12")
            main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.90, relheight=0.88)
            self.eq_main_frame = main_frame
            
        # Lewy panel - Założony sprzęt i Siatka Plecaka
        left_panel = tk.Frame(main_frame, bg="#2c1a12", width=560)
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
                        if self.player.is_inventory_full():
                            messagebox.showwarning("Pełny Ekwipunek", "Twój ekwipunek jest pełny (maksymalnie 80 slotów)!\nNie możesz zdjąć przedmiotu do plecaka.")
                            self.show_equipment(self.drag_item_dict, is_equipped_slot=slot)
                            self.drag_item_dict = None
                            return
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

        # --- NAGŁÓWEK PLECAKA I PAGINACJA (4 STRONY PO 20 SLOTÓW) ---
        inv_header_frame = tk.Frame(left_panel, bg="#2c1a12")
        inv_header_frame.pack(fill=tk.X, pady=(8, 2))
        
        inv_count = len(self.player.inventory)
        max_slots = self.player.get_max_inventory_slots()
        count_color = "#e74c3c" if inv_count >= max_slots else "#f4d03f"
        
        lbl_inv_title = tk.Label(
            inv_header_frame, 
            text=f"Plecak ({inv_count}/{max_slots})", 
            font=("Georgia", 12, "bold"), 
            bg="#2c1a12", 
            fg=count_color
        )
        lbl_inv_title.pack(side=tk.LEFT)
        
        # Paginacja: Strony 1 - 4
        pages_nav_frame = tk.Frame(inv_header_frame, bg="#2c1a12")
        pages_nav_frame.pack(side=tk.RIGHT)
        
        def switch_page(p):
            self.inv_current_page = p
            self.show_equipment(selected_item_dict, is_equipped_slot=is_equipped_slot, current_page=p)

        prev_btn = ctk.CTkButton(
            pages_nav_frame, text="◀", width=28, height=24, font=("Georgia", 10, "bold"),
            fg_color="#3e2723" if self.inv_current_page > 1 else "#22150f",
            text_color="#f4d03f" if self.inv_current_page > 1 else "#555",
            state=tk.NORMAL if self.inv_current_page > 1 else tk.DISABLED,
            command=lambda: switch_page(self.inv_current_page - 1)
        )
        prev_btn.pack(side=tk.LEFT, padx=2)
        
        for p in range(1, 5):
            is_active_page = (p == self.inv_current_page)
            p_items_count = len(self.player.inventory[(p-1)*20 : p*20])
            p_btn_color = "#d35400" if is_active_page else ("#3e2723" if p_items_count > 0 else "#22150f")
            p_txt_color = "#ffffff" if is_active_page else ("#f4d03f" if p_items_count > 0 else "#777")
            
            ctk.CTkButton(
                pages_nav_frame, text=f"{p}", width=26, height=24, font=("Georgia", 10, "bold"),
                fg_color=p_btn_color,
                text_color=p_txt_color,
                command=lambda pg=p: switch_page(pg)
            ).pack(side=tk.LEFT, padx=1)
            
        next_btn = ctk.CTkButton(
            pages_nav_frame, text="▶", width=28, height=24, font=("Georgia", 10, "bold"),
            fg_color="#3e2723" if self.inv_current_page < 4 else "#22150f",
            text_color="#f4d03f" if self.inv_current_page < 4 else "#555",
            state=tk.NORMAL if self.inv_current_page < 4 else tk.DISABLED,
            command=lambda: switch_page(self.inv_current_page + 1)
        )
        next_btn.pack(side=tk.LEFT, padx=2)

        # Komunikat o przechowanych przedmiotach u Barnaby (depozyt)
        stash_count = len(getattr(self.player, 'inventory_stash', []))
        if stash_count > 0:
            stash_bar = tk.Frame(left_panel, bg="#4a1515", bd=2, relief=tk.RIDGE)
            stash_bar.pack(fill=tk.X, pady=(2, 4))
            tk.Label(
                stash_bar, 
                text=f"🎁 Depozyt u Karczmarza: {stash_count} nagród czeka na odbiór!", 
                font=("Georgia", 9, "bold"), 
                fg="#f4d03f", 
                bg="#4a1515"
            ).pack(side=tk.LEFT, padx=8, pady=3)
            
            ctk.CTkButton(
                stash_bar, 
                text="Odbierz Nagrody", 
                width=110, height=22, 
                font=("Georgia", 9, "bold"),
                fg_color="#d35400", hover_color="#e67e22", text_color="white",
                command=self.claim_barnaby_stash
            ).pack(side=tk.RIGHT, padx=5, pady=2)
        elif self.player.is_inventory_full():
            full_bar = tk.Frame(left_panel, bg="#3a1010", bd=1, relief=tk.SOLID)
            full_bar.pack(fill=tk.X, pady=(2, 4))
            tk.Label(
                full_bar, 
                text="⚠️ Ekwipunek jest pełny (4/4 strony)! Nowe nagrody trafią do depozytu u Karczmarza.", 
                font=("Georgia", 8, "italic"), 
                fg="#ff8888", 
                bg="#3a1010"
            ).pack(pady=2)

        # Siatka 20 slotów dla bieżącej strony (4 rzędy po 5 kolumn)
        start_idx = (self.inv_current_page - 1) * 20
        page_items = self.player.inventory[start_idx : start_idx + 20]

        self.inv_grid_frame = tk.Frame(left_panel, bg="#140b07", bd=3, relief=tk.SUNKEN)
        self.inv_grid_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        cols = 5
        for slot_i in range(20):
            r, c = divmod(slot_i, cols)
            
            if slot_i < len(page_items):
                inv_item_dict = page_items[slot_i]
                item = get_item(inv_item_dict)
                if not item: continue
                
                is_leg = getattr(item, 'rarity', 'Zwykły') == "Legendarny"
                border_col = "#f4d03f" if is_leg else "#7f8c8d"
                is_selected = (inv_item_dict == selected_item_dict and is_equipped_slot is None)
                bg_highlight = "#5d4037" if is_selected else "#2c1a12"
                
                tile = tk.Frame(self.inv_grid_frame, bg=bg_highlight, bd=2, relief=tk.RAISED, width=96, height=105, cursor="hand2")
                tile.grid(row=r, column=c, padx=5, pady=5)
                tile.grid_propagate(False)
                
                icon_canvas = tk.Canvas(tile, width=64, height=64, bg="#111", highlightbackground=border_col, highlightthickness=2)
                icon_canvas.pack(pady=4)
                
                if hasattr(self, 'item_icons') and inv_item_dict["id"] in self.item_icons:
                    icon_canvas.create_image(32, 32, image=self.item_icons[inv_item_dict["id"]])
                else:
                    icon_canvas.create_text(32, 32, text=item.name[:2], fill=border_col, font=("Georgia", 12, "bold"))
                
                lvl = inv_item_dict.get('lvl', 0)
                if lvl > 0:
                    icon_canvas.create_text(48, 48, text=f"+{lvl}", fill="#2ecc71", font=("Arial", 10, "bold"))
                
                lvl_str = f" +{lvl}" if lvl > 0 else ""
                name_short = item.name if len(item.name) <= 7 else item.name[:6] + "…"
                lbl_n = tk.Label(tile, text=name_short + lvl_str, font=("Georgia", 8, "bold"), bg=bg_highlight, fg=border_col)
                lbl_n.pack()
                
                for widget in (tile, icon_canvas, lbl_n):
                    widget.bind("<Button-1>", lambda e, item_d=inv_item_dict: self.show_equipment(item_d, is_equipped_slot=None))
                    widget.bind("<ButtonPress-1>", lambda e, item_d=inv_item_dict: on_drag_start(e, item_d))
                    widget.bind("<B1-Motion>", on_drag_motion)
                    widget.bind("<ButtonRelease-1>", on_drag_release)
            else:
                # Wyraźny, powiększony pusty slot ekwipunku bez numeracji
                empty_tile = tk.Frame(
                    self.inv_grid_frame, 
                    bg="#1c100a", 
                    bd=2, 
                    relief=tk.SUNKEN, 
                    highlightbackground="#4a2e1b", 
                    highlightcolor="#4a2e1b",
                    highlightthickness=2, 
                    width=96, 
                    height=105
                )
                empty_tile.grid(row=r, column=c, padx=5, pady=5)
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
            
            if "sockets" in selected_item_dict and selected_item_dict["sockets"]:
                sock_str = get_sockets_summary(selected_item_dict, req_lvl)
                tk.Label(right_panel, text=f"Gniazda: {sock_str}", font=("Georgia", 9, "bold"), fg="#f39c12", bg="#1a100b", wraplength=270).pack(pady=2)

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
                        if self.player.is_inventory_full():
                            messagebox.showwarning("Pełny Ekwipunek", "Twój ekwipunek jest pełny (maksymalnie 80 slotów)!\nNie możesz zdjąć przedmiotu do plecaka.")
                            return
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
                        t_hp = self.player.get_max_hp()
                        if self.player.hp >= t_hp:
                            messagebox.showinfo("Pełne Zdrowie", "Twoje zdrowie jest już w pełni zregenerowane!")
                            return
                            
                        old_hp = self.player.hp
                        if hasattr(item, 'effect'):
                            if 'hp_pct' in item.effect:
                                heal_pct = item.effect['hp_pct'] / 100.0
                                heal_amt = int(t_hp * heal_pct)
                                self.player.hp = min(t_hp, self.player.hp + heal_amt)
                            elif 'heal' in item.effect:
                                heal_amt = item.effect['heal']
                                self.player.hp = min(t_hp, self.player.hp + heal_amt)
                            else:
                                self.player.hp = t_hp
                        else:
                            self.player.hp = t_hp
                            
                        gained = int(self.player.hp - old_hp)
                        sounds.play_potion()
                        self.log_msg(f"🧪 Wypito {item.name}! Odzyskano +{gained} HP. (HP: {int(self.player.hp)}/{t_hp})")
                        self.player.inventory.remove(selected_item_dict)
                        save_game(self.player, self.current_save_path)
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
                elif selected_item_dict.get("id") in ("herb_mystery", "elixir_psychedelic"):
                    def consume_ziolko():
                        self.player.inventory.remove(selected_item_dict)
                        self.start_psychedelic_trip(60)
                        self.update_sidebar()
                        self.show_equipment()
                    ctk.CTkButton(btn_box, text="🌀 Zażyj Ziółko (60s)", fg_color="#8e44ad", hover_color="#9b59b6", font=("Georgia", 10, "bold"), command=consume_ziolko).pack(fill=tk.X, pady=2)
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
        
        if self.player.is_inventory_full():
            messagebox.showwarning("Pełny Ekwipunek", "Twój ekwipunek jest pełny (maksymalnie 4 strony / 80 slotów)!\nNie możesz kupić nowego przedmiotu, dopóki nie zwolnisz miejsca (np. sprzedając zbędne przedmioty w ekwipunku).")
            self.log_msg("❌ Ekwipunek pełny! Nie możesz kupić przedmiotu.")
            return
            
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
                sounds.play_quest_accept()
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
            sounds.play_quest_complete()
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

    def show_blacksmith(self, active_tab="upgrade"):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "blacksmith"
        self.set_background(self.view_panel, "menu")
        
        main_frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.88, relheight=0.88)
        
        # Nagłówek z portretem Kowala
        header_frame = tk.Frame(main_frame, bg="#1a100b", bd=2, relief=tk.RAISED)
        header_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        # Portret Kowala
        if hasattr(self, 'portraits') and "blacksmith" in self.portraits:
            p_lbl = tk.Label(header_frame, image=self.portraits["blacksmith"], bg="#1a100b")
            p_lbl.pack(side=tk.LEFT, padx=10, pady=6)
        
        title_box = tk.Frame(header_frame, bg="#1a100b")
        title_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=6)
        
        tk.Label(title_box, text="⚒️ MISTRZOWSKA KUŹNIA KOWALA ⚒️", font=("Georgia", 18, "bold"), bg="#1a100b", fg="#f4d03f", anchor="w").pack(fill=tk.X)
        tk.Label(title_box, text="\"Rozgrzany młot i czysta stal nie kłamią. Ulepsz swój oręż lub wpraw magiczne klejnoty w gniazda!\"", font=("Georgia", 10, "italic"), bg="#1a100b", fg="#cccccc", anchor="w").pack(fill=tk.X)
        tk.Label(title_box, text=f"Twoje złoto: {self.player.gold}g", font=("Georgia", 12, "bold"), bg="#1a100b", fg="#f1c40f", anchor="w").pack(fill=tk.X, pady=(2, 0))
        
        # Przełącznik zakładek: [🔨 ULEPSZANIE (+1 do +9)] | [🔮 MAGICZNE GNIAZDA I KLEJNOTY]
        tab_box = tk.Frame(main_frame, bg="#2c1a12")
        tab_box.pack(fill=tk.X, padx=15, pady=(6, 4))
        
        btn_tab_upg = ctk.CTkButton(
            tab_box, 
            text="🔨 ULEPSZANIE PRZEDMIOTÓW (+1 do +9)", 
            font=("Georgia", 11, "bold"),
            fg_color="#8b4513" if active_tab == "upgrade" else "#3e2723",
            text_color="#f4d03f" if active_tab == "upgrade" else "#aaaaaa",
            command=lambda: self.show_blacksmith("upgrade")
        )
        btn_tab_upg.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        
        btn_tab_gems = ctk.CTkButton(
            tab_box, 
            text="🔮 MAGICZNE GNIAZDA & KLEJNOTY", 
            font=("Georgia", 11, "bold"),
            fg_color="#8b4513" if active_tab == "sockets" else "#3e2723",
            text_color="#f4d03f" if active_tab == "sockets" else "#aaaaaa",
            command=lambda: self.show_blacksmith("sockets")
        )
        btn_tab_gems.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        
        sf = ScrollableFrame(main_frame, bg_color="#1a100b")
        sf.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        if active_tab == "upgrade":
            all_items = []
            for slot, item_dict in self.player.equipment.items():
                if item_dict:
                    all_items.append((item_dict, f"[Założone: {slot.upper()}]"))
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
                base_stats = item.stats.get("atk", 0) + item.stats.get("def", 0) + (item.stats.get("hp_max", 0) / 10.0)
                cost = int(base_stats * 50 * (1.9 ** lvl))
                if cost < 10: cost = 10
                
                if getattr(self.player, 'active_companion', None) == "yomen":
                    cost = max(5, int(cost * 0.85))
                if getattr(self.player, 'permanent_perks', None) and "perk_master_smith" in self.player.permanent_perks:
                    cost = max(5, int(cost * 0.90))
                
                if lvl >= 9:
                    tk.Label(row, text="MAX (+9)", font=("Georgia", 14, "bold"), bg="#3e2723", fg="#ff6666").pack(side=tk.RIGHT, padx=15, pady=10)
                else:
                    def do_upgrade(i_dict=inv_item_dict, c=cost):
                        if self.player.gold >= c:
                            self.player.gold -= c
                            i_dict["lvl"] = i_dict.get("lvl", 0) + 1
                            sounds.play_hit()
                            sounds.play_coin()
                            self.player.record_achievement_stat("upgrades_done", 1, mode="add")
                            self.player.record_achievement_stat("max_upgrade_level", i_dict["lvl"], mode="max")
                            self.log_msg(f"Pomyślnie wykuto {get_item(i_dict).name} +{i_dict['lvl']}!")
                            
                            for b in getattr(self.player, 'bounties', []):
                                if b.status == 'IN_PROGRESS' and b.target_type == 'upgrade':
                                    if b.add_progress(1):
                                        self.log_msg(f"📋 Zlecenie z tablicy ukończone: '{b.title}'! Odbierz nagrodę u Karczmarza.")
                                        
                            self.update_sidebar()
                            self.show_blacksmith("upgrade")
                        else:
                            messagebox.showwarning("Brak Złota", "Masz za mało złota na to ulepszenie!")
                            
                    btn = ctk.CTkButton(row, text=f"Ulepsz ({cost}g)", command=do_upgrade)
                    btn.pack(side=tk.RIGHT, padx=15, pady=10)
                
                name_lbl = f"{item.name} +{lvl} {location_tag}" if lvl > 0 else f"{item.name} {location_tag}"
                tk.Label(row, text=name_lbl, font=("Georgia", 12, "bold"), bg="#3e2723", fg="#f4d03f").pack(side=tk.LEFT, padx=15, pady=15)
                
                next_lvl_stats = ", ".join([f"{k.upper()}: +{int(v * (1.0 + 0.15 * (lvl + 1)))}" for k, v in item.stats.items()])
                tk.Label(row, text=f"Poz. {lvl+1}: {next_lvl_stats}", font=("Georgia", 9, "italic"), bg="#3e2723", fg="#ccc", wraplength=200).pack(side=tk.LEFT, padx=5)

        else:
            # Widok Gniazd i Klejnotów (Sockets & Gems)
            socketable_items = []
            for slot, item_dict in self.player.equipment.items():
                if item_dict and isinstance(item_dict, dict):
                    item = get_item(item_dict)
                    if item and hasattr(item, 'stats'):
                        if "sockets" not in item_dict:
                            rarity = getattr(item, 'rarity', 'Zwykły')
                            item_dict["sockets"] = [None, None] if rarity in ("Legendarny", "Mityczny") else []
                        socketable_items.append((item_dict, f"[Założone: {slot.upper()}]"))
                            
            for item_dict in self.player.inventory:
                if item_dict and isinstance(item_dict, dict):
                    item = get_item(item_dict)
                    if item and hasattr(item, 'stats'):
                        if "sockets" not in item_dict:
                            rarity = getattr(item, 'rarity', 'Zwykły')
                            item_dict["sockets"] = [None, None] if rarity in ("Legendarny", "Mityczny") else []
                        socketable_items.append((item_dict, "[Plecak]"))
                            
            if not socketable_items:
                tk.Label(
                    sf.scrollable_frame, 
                    text="Nie posiadasz w ekwipunku przedmiotów z gniazdami na klejnoty.\n(Przedmioty ze sklepu nie posiadają gniazd, natomiast relikty i dropy z potworów posiadają 1-2 gniazda!)", 
                    font=("Georgia", 12, "italic"), 
                    bg="#1a100b", 
                    fg="#aaa"
                ).pack(pady=40)
                return
                
            for item_dict, location_tag in socketable_items:
                item = get_item(item_dict)
                if not item: continue
                
                card = tk.Frame(sf.scrollable_frame, bg="#2a1610", bd=2, relief=tk.GROOVE)
                card.pack(fill=tk.X, padx=10, pady=6)
                
                header_c = tk.Frame(card, bg="#2a1610")
                header_c.pack(fill=tk.X, padx=10, pady=(6, 2))
                
                lvl = item_dict.get('lvl', 0)
                lvl_str = f" +{lvl}" if lvl > 0 else ""
                tk.Label(header_c, text=f"{item.name}{lvl_str} {location_tag}", font=("Georgia", 11, "bold"), fg="#f4d03f", bg="#2a1610").pack(side=tk.LEFT)
                
                sockets = item_dict.get("sockets", [])
                req_lvl = getattr(item, 'level_req', 1)
                
                # Przycisk wykuwania nowego gniazda u Kowala za składniki
                max_sockets = 2 if getattr(item, 'rarity', 'Zwykły') in ("Legendarny", "Mityczny") or req_lvl >= 15 else 1
                if len(sockets) < max_sockets:
                    forge_frame = tk.Frame(card, bg="#1a100b", bd=1, relief=tk.RIDGE)
                    forge_frame.pack(fill=tk.X, padx=10, pady=4)
                    
                    is_second = (len(sockets) == 1)
                    forge_cost = 400 if is_second else 150
                    req_ing_id = "ing_ectoplasm" if is_second else "ing_fang"
                    req_ing_name = "Ektoplazma Upiora" if is_second else "Kieł Bestii"
                    
                    lbl_txt = f"⚒️ Wykuj Gniazdo #{len(sockets)+1} (Koszt: {forge_cost}g + 1x {req_ing_name})"
                    tk.Label(forge_frame, text=lbl_txt, font=("Georgia", 10, "bold"), fg="#f39c12", bg="#1a100b").pack(side=tk.LEFT, padx=10, pady=6)
                    
                    def do_forge_socket(i_d=item_dict, cost=forge_cost, ing_id=req_ing_id):
                        if self.player.gold < cost:
                            messagebox.showwarning("Brak Złota", f"Wykuwanie gniazda wymaga {cost}g!")
                            return
                        ing_match = next((i for i in self.player.inventory if i.get("id") == ing_id), None)
                        if not ing_match:
                            messagebox.showwarning("Brak Składnika", f"Potrzebujesz 1x {req_ing_name} (zdobądź go z potworów)!")
                            return
                        self.player.gold -= cost
                        self.player.inventory.remove(ing_match)
                        if "sockets" not in i_d: i_d["sockets"] = []
                        i_d["sockets"].append(None)
                        sounds.play_hit()
                        sounds.play_coin()
                        self.log_msg(f"Kowal z powodzeniem wykuł nowe gniazdo w {item.name}!")
                        self.update_sidebar()
                        self.show_blacksmith("sockets")
                        
                    ctk.CTkButton(forge_frame, text="Wykuj Gniazdo", width=120, height=26, fg_color="#d35400", hover_color="#e67e22", text_color="white", font=("Georgia", 9, "bold"), command=do_forge_socket).pack(side=tk.RIGHT, padx=8, pady=4)
                
                for s_idx, g_id in enumerate(sockets):
                    s_row = tk.Frame(card, bg="#1a100b", bd=1, relief=tk.SOLID)
                    s_row.pack(fill=tk.X, padx=10, pady=3)
                    
                    if g_id and g_id in GEMS_DB:
                        gem = GEMS_DB[g_id]
                        stat_summary = gem.get_stat_summary(req_lvl)
                        tk.Label(s_row, text=f"Gniazdo #{s_idx+1}: {gem.icon} {gem.name} ({stat_summary})", font=("Georgia", 10, "bold"), fg=gem.color, bg="#1a100b").pack(side=tk.LEFT, padx=10, pady=6)
                        
                        def unsocket(i_d=item_dict, idx=s_idx):
                            if self.player.gold < 50:
                                messagebox.showwarning("Brak Złota", "Wyjęcie klejnotu kosztuje 50g!")
                                return
                            if self.player.is_inventory_full():
                                messagebox.showwarning("Pełny Plecak", "Nie masz miejsca w plecaku na wyjęty klejnot!")
                                return
                            self.player.gold -= 50
                            removed_gem = i_d["sockets"][idx]
                            i_d["sockets"][idx] = None
                            self.player.inventory.append({"id": removed_gem, "lvl": 0})
                            sounds.play_hit()
                            self.log_msg(f"Kowal bezpiecznie wybił {GEMS_DB[removed_gem].name} z gniazda.")
                            self.update_sidebar()
                            self.show_blacksmith("sockets")
                            
                        ctk.CTkButton(s_row, text="Wybij Klejnot (50g)", width=130, height=26, fg_color="#7f1d1d", hover_color="#991b1b", text_color="#f4d03f", font=("Georgia", 9, "bold"), command=unsocket).pack(side=tk.RIGHT, padx=8, pady=4)
                    else:
                        tk.Label(s_row, text=f"Gniazdo #{s_idx+1}: ○ Puste Gniazdo", font=("Georgia", 10, "italic"), fg="#888888", bg="#1a100b").pack(side=tk.LEFT, padx=10, pady=6)
                        
                        def open_gem_picker(i_d=item_dict, idx=s_idx):
                            gems_in_bag = [i for i in self.player.inventory if i.get("id", "").startswith("gem_")]
                            if not gems_in_bag:
                                messagebox.showinfo("Brak Klejnotów", "Nie posiadasz żadnych magicznych klejnotów w plecaku!\n(Klejnoty dropią z bossów oraz od 15 poziomu z potworów).")
                                return
                            if self.player.gold < 100:
                                messagebox.showwarning("Brak Złota", "Wprawienie klejnotu kosztuje 100g!")
                                return
                                
                            p_win = tk.Toplevel(self.root)
                            p_win.title("Wybierz Klejnot do Wprawienia")
                            p_win.geometry("450x380")
                            p_win.configure(bg="#2c1a12")
                            p_win.transient(self.root)
                            p_win.grab_set()
                            
                            p_win.update_idletasks()
                            rx = self.root.winfo_x() + (self.root.winfo_width() - 450) // 2
                            ry = self.root.winfo_y() + (self.root.winfo_height() - 380) // 2
                            p_win.geometry(f"450x380+{max(0, rx)}+{max(0, ry)}")
                            
                            tk.Label(p_win, text="WYBIERZ KLEJNOT Z PLECAKA:", font=("Georgia", 13, "bold"), fg="#f4d03f", bg="#2c1a12").pack(pady=10)
                            
                            p_sf = ScrollableFrame(p_win, bg_color="#1a100b")
                            p_sf.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
                            
                            for g_dict in list(gems_in_bag):
                                gid = g_dict["id"]
                                gem_obj = GEMS_DB.get(gid)
                                if not gem_obj: continue
                                
                                g_btn_f = tk.Frame(p_sf.scrollable_frame, bg="#3e2723", bd=1, relief=tk.RAISED)
                                g_btn_f.pack(fill=tk.X, padx=5, pady=4)
                                
                                tk.Label(g_btn_f, text=f"{gem_obj.icon} {gem_obj.name}\n{gem_obj.get_stat_summary(getattr(item, 'level_req', 1))}", font=("Georgia", 10, "bold"), fg=gem_obj.color, bg="#3e2723", justify=tk.LEFT).pack(side=tk.LEFT, padx=10, pady=5)
                                
                                def do_socket(chosen_gid=gid, chosen_dict=g_dict):
                                    self.player.gold -= 100
                                    self.player.inventory.remove(chosen_dict)
                                    i_d["sockets"][idx] = chosen_gid
                                    sounds.play_coin()
                                    sounds.play_hit()
                                    self.player.record_achievement_stat("gems_socketed", 1, mode="add")
                                    self.log_msg(f"Wprawiono {gem_obj.name} do {item.name}!")
                                    self.update_sidebar()
                                    p_win.destroy()
                                    self.show_blacksmith("sockets")
                                    
                                ctk.CTkButton(g_btn_f, text="Wpraw (100g)", width=100, height=28, fg_color="#27ae60", hover_color="#2ecc71", text_color="white", command=do_socket).pack(side=tk.RIGHT, padx=8, pady=8)
                                
                            ctk.CTkButton(p_win, text="Anuluj", fg_color="#2a1610", command=p_win.destroy).pack(pady=8)
                            
                        ctk.CTkButton(s_row, text="+ Wpraw Klejnot", width=130, height=26, fg_color="#27ae60", hover_color="#2ecc71", text_color="white", font=("Georgia", 9, "bold"), command=open_gem_picker).pack(side=tk.RIGHT, padx=8, pady=4)

    def show_achievements(self, selected_category="all"):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "achievements"
        self.set_background(self.view_panel, "menu")
        
        main_frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.88, relheight=0.88)
        
        tk.Label(main_frame, text="🏆 KSIĘGA OSIĄGNIĘĆ I TROFEÓW 🏆", font=("Georgia", 20, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=(10, 2))
        
        # Obliczenie statystyk ukończenia
        unlocked_count = 0
        for a_id in ACHIEVEMENTS_DB:
            if self.player.achievements.get(a_id, {}).get("claimed", False):
                unlocked_count += 1
        perks_count = len(getattr(self.player, 'permanent_perks', []))
        
        tk.Label(main_frame, text=f"Odblokowano: {unlocked_count} / {len(ACHIEVEMENTS_DB)} Osiągnięć | Aktywne Stałe Perki Konta: {perks_count}", font=("Georgia", 11, "bold"), bg="#2c1a12", fg="#a8ff9e").pack(pady=2)
        
        # Pasek kategorii
        cat_bar = tk.Frame(main_frame, bg="#1a100b", bd=2, relief=tk.SUNKEN)
        cat_bar.pack(fill=tk.X, padx=15, pady=6)
        
        categories = [
            ("all", "Wszystkie"),
            ("walka", "🗡️ Walka"),
            ("lochy", "🏰 Lochy"),
            ("rzemioslo", "🔨 Rzemiosło"),
            ("alchemia", "🌿 Alchemia"),
            ("druzyna", "👥 Drużyna"),
            ("bogactwo", "💰 Bogactwo")
        ]
        
        for c_id, c_label in categories:
            is_active = (selected_category == c_id)
            btn = tk.Button(
                cat_bar,
                text=c_label,
                font=("Georgia", 9, "bold"),
                bg="#f4d03f" if is_active else "#3e2723",
                fg="#1a100b" if is_active else "#f4d03f",
                relief=tk.SUNKEN if is_active else tk.RAISED,
                command=lambda cid=c_id: self.show_achievements(cid)
            )
            btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=3)
            
        sf = ScrollableFrame(main_frame, bg_color="#1a100b")
        sf.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        for a_id, a_data in ACHIEVEMENTS_DB.items():
            if selected_category != "all" and a_data["category"] != selected_category:
                continue
                
            card = tk.Frame(sf.scrollable_frame, bg="#2a1610", bd=2, relief=tk.GROOVE)
            card.pack(fill=tk.X, padx=10, pady=5)
            
            # Pobieramy bieżący postęp
            target = a_data["target"]
            stat_key = a_data["stat_key"]
            if stat_key == "party_count":
                current_val = len(self.player.party)
            else:
                current_val = self.player.achievement_stats.get(stat_key, 0)
                
            is_completed = (current_val >= target)
            is_claimed = self.player.achievements.get(a_id, {}).get("claimed", False)
            
            # Ikona
            icon_box = tk.Label(card, text=a_data["icon"], font=("Georgia", 24), bg="#1a100b", width=3)
            icon_box.pack(side=tk.LEFT, padx=10, pady=8)
            
            # Treść
            info_box = tk.Frame(card, bg="#2a1610")
            info_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            tk.Label(info_box, text=a_data["title"], font=("Georgia", 12, "bold"), fg="#f4d03f", bg="#2a1610", anchor="w").pack(fill=tk.X)
            tk.Label(info_box, text=a_data["desc"], font=("Georgia", 9, "italic"), fg="#cccccc", bg="#2a1610", anchor="w").pack(fill=tk.X)
            
            # Pasek postępu
            pct = min(1.0, max(0.0, current_val / target)) if target > 0 else 1.0
            prog_text = f"Postęp: {current_val} / {target} ({int(pct*100)}%)" if not is_completed else f"Postęp: {target} / {target} (UKOŃCZONE!)"
            prog_col = "#2ecc71" if is_completed else "#f39c12"
            tk.Label(info_box, text=prog_text, font=("Georgia", 9, "bold"), fg=prog_col, bg="#2a1610", anchor="w").pack(fill=tk.X, pady=(2, 0))
            
            # Nagrody
            rew = a_data["rewards"]
            rew_str = f"🎁 Nagroda: +{rew['gold']}g, +{rew['exp']} EXP"
            if "perk_desc" in rew:
                rew_str += f" | {rew['perk_desc']}"
            tk.Label(info_box, text=rew_str, font=("Georgia", 9, "bold"), fg="#a8ff9e" if "perk_desc" in rew else "#f1c40f", bg="#2a1610", anchor="w", wraplength=450).pack(fill=tk.X)
            
            # Przycisk odbioru
            if is_claimed:
                tk.Label(card, text="✅ ODEBRANO", font=("Georgia", 11, "bold"), fg="#2ecc71", bg="#2a1610").pack(side=tk.RIGHT, padx=15)
            elif is_completed:
                def claim_ach(aid=a_id, r=rew):
                    self.player.gold += r["gold"]
                    self.player.add_exp(r["exp"])
                    if "perk_id" in r:
                        if r["perk_id"] not in self.player.permanent_perks:
                            self.player.permanent_perks.append(r["perk_id"])
                    self.player.achievements[aid] = {"completed": True, "claimed": True}
                    sounds.play_quest_complete()
                    self.log_msg(f"🏆 ODEBRANO NAGRODĘ ZA OSIĄGNIĘCIE: '{ACHIEVEMENTS_DB[aid]['title']}'!")
                    self.update_sidebar()
                    self.show_achievements(selected_category)
                    
                ctk.CTkButton(card, text="🎁 ODBIERZ NAGRODĘ", font=("Georgia", 11, "bold"), fg_color="#27ae60", hover_color="#2ecc71", command=claim_ach).pack(side=tk.RIGHT, padx=15)
            else:
                ctk.CTkButton(card, text="⏳ W trakcie...", font=("Georgia", 10, "italic"), fg_color="#2a1610", text_color="#888", state=tk.DISABLED).pack(side=tk.RIGHT, padx=15)

    # ---- PSYCHODELICZNY EFEKT ZIÓŁKA (60s DEFORMACJA, MIRAŻE I KOLORY) ----

    def start_psychedelic_trip(self, duration=60):
        self.psychedelic_end = time.time() + duration
        if not hasattr(self.player, 'active_buffs'):
            self.player.active_buffs = {}
        self.player.active_buffs["elixir_psychedelic"] = 10
        sounds.play_level_up()
        self.log_msg("🌀 [ZIÓŁKO] Zażyłeś Ziółko! Rzeczywistość zaczyna falować, kolory pulsują, a przez środek ekranu płyną tęczowe miraże!")
        
        # Pływający baner stanu ziółka u góry ekranu
        if not hasattr(self, 'trip_banner') or not self.trip_banner.winfo_exists():
            self.trip_banner = tk.Label(
                self.root, 
                text="🌀 🌿 FAZA: ZIÓŁKO (60s) 🌿 🌀", 
                font=("Georgia", 11, "bold"), 
                bg="#120024", 
                fg="#00ffff", 
                bd=3, 
                relief=tk.RAISED
            )
            self.trip_banner.place(relx=0.5, y=10, anchor=tk.N)
            
        # Kolorowe tęczowe ramki wokół całego okna gry
        if not hasattr(self, 'trip_border_top') or not self.trip_border_top.winfo_exists():
            self.trip_border_top = tk.Frame(self.root, bg="#ff00ff", height=4)
            self.trip_border_top.place(x=0, y=0, relwidth=1.0)
            self.trip_border_bot = tk.Frame(self.root, bg="#ff00ff", height=4)
            self.trip_border_bot.place(x=0, rely=1.0, y=-4, relwidth=1.0)
            self.trip_border_left = tk.Frame(self.root, bg="#ff00ff", width=4)
            self.trip_border_left.place(x=0, y=0, relheight=1.0)
            self.trip_border_right = tk.Frame(self.root, bg="#ff00ff", width=4)
            self.trip_border_right.place(relx=1.0, x=-4, y=0, relheight=1.0)

        # Czysty, wewnątrzokienny Canvas w view_panel z falami mirażu (umieszczony na spodzie, nie blokuje ŻADNYCH kliknięć)
        if not hasattr(self, 'trip_bg_canvas') or not self.trip_bg_canvas.winfo_exists():
            self.trip_bg_canvas = tk.Canvas(self.view_panel, bg="#0d0414", highlightthickness=0)
            self.trip_bg_canvas.place(x=0, y=0, relwidth=1.0, relheight=1.0)
            tk.Misc.lower(self.trip_bg_canvas)
            
        self.tick_psychedelic_effect()

    def tick_psychedelic_effect(self):
        if not hasattr(self, 'psychedelic_end'):
            return
            
        now = time.time()
        rem = int(self.psychedelic_end - now)
        
        if rem <= 0:
            # Przywrócenie normalnej geometrii i usunięcie nakładek
            self.container.place(x=0, y=0, relwidth=1.0, relheight=1.0)
            if hasattr(self, 'trip_banner') and self.trip_banner.winfo_exists():
                self.trip_banner.destroy()
            if hasattr(self, 'trip_border_top') and self.trip_border_top.winfo_exists():
                self.trip_border_top.destroy()
                self.trip_border_bot.destroy()
                self.trip_border_left.destroy()
                self.trip_border_right.destroy()
            if hasattr(self, 'trip_bg_canvas') and self.trip_bg_canvas.winfo_exists():
                self.trip_bg_canvas.destroy()
            if hasattr(self, 'combat_canvas') and self.combat_canvas.winfo_exists():
                self.combat_canvas.delete("trip_mirage")
            self.log_msg("🌀 Efekt ziółka minął. Wracasz do trzeźwej rzeczywistości.")
            self.update_sidebar()
            return
            
        # 1. Delikatne, organiczne falowanie kontenera (Screen Breathing - 2-3px, bez przesuwania przycisków za ekran)
        t = now * 3.5
        offset_x = int(math.sin(t * 0.8) * 3 + math.sin(t * 1.7) * 2)
        offset_y = int(math.cos(t * 0.6) * 3 + math.cos(t * 1.3) * 2)
        self.container.place(x=offset_x, y=offset_y, relwidth=1.0, relheight=1.0)
        
        # 2. Dynamiczne przeliczanie tęczowej palety barw (HSV Spectrum Cycling)
        import colorsys
        hue1 = (now * 0.45) % 1.0
        hue2 = (now * 0.45 + 0.33) % 1.0
        hue3 = (now * 0.45 + 0.66) % 1.0
        
        rgb1 = colorsys.hsv_to_rgb(hue1, 0.9, 1.0)
        rgb2 = colorsys.hsv_to_rgb(hue2, 0.9, 1.0)
        rgb3 = colorsys.hsv_to_rgb(hue3, 0.9, 1.0)
        
        hex1 = f"#{int(rgb1[0]*255):02x}{int(rgb1[1]*255):02x}{int(rgb1[2]*255):02x}"
        hex2 = f"#{int(rgb2[0]*255):02x}{int(rgb2[1]*255):02x}{int(rgb2[2]*255):02x}"
        hex3 = f"#{int(rgb3[0]*255):02x}{int(rgb3[1]*255):02x}{int(rgb3[2]*255):02x}"
        
        # 3. Aktualizacja banera i tęczowych ramek
        if hasattr(self, 'trip_banner') and self.trip_banner.winfo_exists():
            wave_dots = "~" * (int(now * 5) % 4 + 1)
            self.trip_banner.configure(
                text=f"🌀 {wave_dots} FAZA: ZIÓŁKO (Pozostało: {rem}s) {wave_dots} 🌀",
                fg=hex1,
                bg="#120024"
            )
            banner_y = 10 + int(math.sin(t * 1.1) * 2)
            self.trip_banner.place_configure(y=banner_y)
            
        if hasattr(self, 'trip_border_top') and self.trip_border_top.winfo_exists():
            self.trip_border_top.configure(bg=hex1)
            self.trip_border_bot.configure(bg=hex2)
            self.trip_border_left.configure(bg=hex3)
            self.trip_border_right.configure(bg=hex1)
            
        # 4. Renderowanie falujących miraży w tle view_panel (Underneath UI - Zero click interception)
        if hasattr(self, 'trip_bg_canvas') and self.trip_bg_canvas.winfo_exists():
            try:
                gw = self.view_panel.winfo_width()
                gh = self.view_panel.winfo_height()
                if gw > 50 and gh > 50:
                    c = self.trip_bg_canvas
                    c.delete("all")
                    cx, cy = gw / 2.0, gh / 2.0
                    
                    # A. Rozchodzące się pierścienie fali psychodelicznej z centrum
                    for r_i in range(5):
                        r_val = int((now * 80 + r_i * 100) % 520)
                        if r_val > 15:
                            r_h = (hue1 + r_i * 0.20) % 1.0
                            r_col = colorsys.hsv_to_rgb(r_h, 0.9, 1.0)
                            r_hex = f"#{int(r_col[0]*255):02x}{int(r_col[1]*255):02x}{int(r_col[2]*255):02x}"
                            c.create_oval(
                                cx - r_val * 1.5, cy - r_val, cx + r_val * 1.5, cy + r_val,
                                outline=r_hex, width=max(1, int(4 * (1.0 - r_val / 520.0)))
                            )
                            
                    # B. Płynące tęczowe pasma fali sinusoidalnej
                    for w_idx in range(6):
                        w_y = cy - 200 + w_idx * 75
                        w_h = (hue2 + w_idx * 0.16) % 1.0
                        w_col = colorsys.hsv_to_rgb(w_h, 0.9, 1.0)
                        w_hex = f"#{int(w_col[0]*255):02x}{int(w_col[1]*255):02x}{int(w_col[2]*255):02x}"
                        
                        pts = []
                        steps = 24
                        for s_i in range(steps + 1):
                            px = (gw / steps) * s_i
                            py = w_y + math.sin(px * 0.015 + now * 4.5 + w_idx * 1.3) * 24 + math.cos(px * 0.008 - now * 3.0) * 15
                            pts.extend([px, py])
                            
                        c.create_line(pts, fill=w_hex, width=3, smooth=True)
            except Exception:
                pass

        # 5. Renderowanie miraży bezpośrednio na arenie walki (Combat Canvas)
        if hasattr(self, 'combat_canvas') and self.combat_canvas.winfo_exists() and self.combat_active:
            try:
                cc = self.combat_canvas
                cc.delete("trip_mirage")
                cw = 1100
                ch = 400
                cx, cy = 550, 200
                
                # Fale mirażu przemieszczające się między bohaterem a wrogiem
                for w_idx in range(4):
                    w_y = cy - 80 + w_idx * 50
                    w_h = (hue3 + w_idx * 0.22) % 1.0
                    w_col = colorsys.hsv_to_rgb(w_h, 0.95, 1.0)
                    w_hex = f"#{int(w_col[0]*255):02x}{int(w_col[1]*255):02x}{int(w_col[2]*255):02x}"
                    
                    pts = []
                    for px in range(250, 850, 30):
                        py = w_y + math.sin(px * 0.02 + now * 5.0 + w_idx * 1.5) * 18
                        pts.extend([px, py])
                    cc.create_line(pts, fill=w_hex, width=2, smooth=True, tags="trip_mirage")
                    
                # Pierścienie energii krytycznej w centrum areny
                for r_i in range(3):
                    r_val = int((now * 90 + r_i * 90) % 250)
                    if r_val > 10:
                        cc.create_oval(cx - r_val, cy - r_val * 0.6, cx + r_val, cy + r_val * 0.6, outline=hex1, width=2, tags="trip_mirage")
            except Exception:
                pass
            
        # Kolejna klatka animacji za 40ms (~25 FPS)
        self.root.after(40, self.tick_psychedelic_effect)


    def show_alchemy(self):
        if self.is_busy(): return
        self.clear_view()
        self.current_view = "alchemy"
        self.set_background(self.view_panel, "menu")
        
        main_frame = tk.Frame(self.view_panel, bg="#2c1a12", bd=5, relief=tk.RIDGE)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.90, relheight=0.90)
        
        tk.Label(main_frame, text="🧪 ALCHEMIA & OGRÓD ZIÓŁ U DOMCI 🧪", font=("Georgia", 20, "bold"), bg="#2c1a12", fg="#f4d03f").pack(pady=(8, 2))
        tk.Label(main_frame, text="Zbieraj wyhodowane zioła z grządek i warz w kociołku potężne eliksiry wzmacniające w walce!", font=("Georgia", 10, "italic"), bg="#2c1a12", fg="#ddd").pack(pady=(0, 6))
        
        # --- SEKCJA 1: OGRÓD ZIÓŁ ---
        garden_header = tk.Frame(main_frame, bg="#1a100b", bd=2, relief=tk.RAISED)
        garden_header.pack(fill=tk.X, padx=15, pady=(4, 2))
        
        tk.Label(garden_header, text="🌿 OGRÓD ZIÓŁ DOMCI (4 GRZĄDKI)", font=("Georgia", 12, "bold"), fg="#a8ff9e", bg="#1a100b").pack(side=tk.LEFT, padx=10, pady=4)
        
        def harvest_all():
            harvested = 0
            now = time.time()
            for plot in self.player.herb_garden:
                planted = plot.get("planted_at", 0)
                g_time = plot.get("growth_time", 60)
                h_type = plot.get("type", "herb_amanita")
                if now - planted >= g_time:
                    count = 2 if getattr(self.player, 'permanent_perks', None) and "perk_alchemist_touch" in self.player.permanent_perks else 1
                    for _ in range(count):
                        self.player.add_to_inventory(h_type, is_reward=True)
                    plot["planted_at"] = now
                    harvested += count
                    self.player.record_achievement_stat("herbs_harvested", count, mode="add")
            if harvested > 0:
                sounds.play_coin()
                self.log_msg(f"🌿 Zebrano {harvested} ziół z Ogrodu Domci! Posadzono nowe nasiona.")
                self.update_sidebar()
                self.show_alchemy()
            else:
                messagebox.showinfo("Ogród", "Żadne zioło nie jest jeszcze w pełni dojrzałe!")
                
        ctk.CTkButton(garden_header, text="🌾 ZBIERZ WSZYSTKIE GOTOWE ZIOŁA", font=("Georgia", 10, "bold"), fg_color="#27ae60", hover_color="#2ecc71", command=harvest_all).pack(side=tk.RIGHT, padx=10, pady=3)
        
        # 4 Grządki w rzędzie
        plots_frame = tk.Frame(main_frame, bg="#2c1a12")
        plots_frame.pack(fill=tk.X, padx=15, pady=4)
        
        now = time.time()
        self.alchemy_plot_widgets = []
        
        for idx, plot in enumerate(self.player.herb_garden):
            p_card = tk.Frame(plots_frame, bg="#1a100b", bd=2, relief=tk.GROOVE)
            p_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=2)
            
            h_type = plot.get("type", "herb_amanita")
            h_info = HERBS_DB.get(h_type, HERBS_DB["herb_amanita"])
            planted = plot.get("planted_at", 0)
            g_time = plot.get("growth_time", 60)
            
            elapsed = now - planted
            is_ready = (elapsed >= g_time)
            rem_sec = max(0, int(g_time - elapsed))
            
            tk.Label(p_card, text=f"{h_info['icon']} Grządka #{idx+1}", font=("Georgia", 11, "bold"), fg=h_info['color'], bg="#1a100b").pack(pady=(4, 1))
            tk.Label(p_card, text=h_info['name'], font=("Georgia", 10, "bold"), fg="white", bg="#1a100b").pack()
            tk.Label(p_card, text=f"({h_info['description']})", font=("Georgia", 8, "italic"), fg="#aaa", bg="#1a100b", wraplength=170).pack(pady=1)
            
            lbl_timer = tk.Label(
                p_card, 
                text="✅ GOTOWE DO ZBIORU!" if is_ready else f"🌱 Rośnie... ({rem_sec}s)", 
                font=("Georgia", 9, "bold" if is_ready else "italic"), 
                fg="#2ecc71" if is_ready else "#f39c12", 
                bg="#1a100b"
            )
            lbl_timer.pack(pady=3)
            
            def harvest_single(p=plot, ht=h_type):
                count = 2 if getattr(self.player, 'permanent_perks', None) and "perk_alchemist_touch" in self.player.permanent_perks else 1
                for _ in range(count):
                    self.player.add_to_inventory(ht, is_reward=True)
                p["planted_at"] = time.time()
                self.player.record_achievement_stat("herbs_harvested", count, mode="add")
                sounds.play_coin()
                self.log_msg(f"🌿 Zebrano {count}x {HERBS_DB[ht]['name']}! Posadzono nowe nasiona.")
                self.update_sidebar()
                self.show_alchemy()
                
            btn_action = ctk.CTkButton(
                p_card, 
                text="Zbierz Zioło" if is_ready else "Czekaj...", 
                height=24, 
                fg_color="#27ae60" if is_ready else "#2a1610", 
                hover_color="#2ecc71", 
                text_color="white" if is_ready else "#888",
                state=tk.NORMAL if is_ready else tk.DISABLED,
                font=("Georgia", 9, "bold" if is_ready else "italic"), 
                command=harvest_single
            )
            btn_action.pack(pady=(2, 6))
            
            self.alchemy_plot_widgets.append({
                "plot": plot,
                "type": h_type,
                "lbl": lbl_timer,
                "btn": btn_action
            })
            
        # Rozpoczęcie automatycznego odświeżania zegarów co 1 sekundę
        self.update_alchemy_timers()
                
        # --- SEKCJA 2: KOCIOŁEK ALCHEMICZNY ---
        cauldron_lbl = tk.Label(main_frame, text="⚗️ KOCIOŁEK ALCHEMICZNY (WARZENIE ELIKSIRÓW)", font=("Georgia", 12, "bold"), fg="#f4d03f", bg="#2c1a12")
        cauldron_lbl.pack(pady=(8, 2))
        
        sf_recipes = ScrollableFrame(main_frame, bg_color="#1a100b")
        sf_recipes.pack(fill=tk.BOTH, expand=True, padx=15, pady=(2, 8))
        
        inv_counts = {}
        for item_dict in self.player.inventory:
            iid = item_dict.get("id", "")
            inv_counts[iid] = inv_counts.get(iid, 0) + 1
            
        for r_id, r_data in RECIPES_DB.items():
            r_card = tk.Frame(sf_recipes.scrollable_frame, bg="#2a1610", bd=2, relief=tk.GROOVE)
            r_card.pack(fill=tk.X, padx=8, pady=4)
            
            tk.Label(r_card, text=r_data["icon"], font=("Georgia", 22), bg="#1a100b", width=3).pack(side=tk.LEFT, padx=8, pady=6)
            
            r_info = tk.Frame(r_card, bg="#2a1610")
            r_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=4)
            
            tk.Label(r_info, text=r_data["name"], font=("Georgia", 11, "bold"), fg=r_data["color"], bg="#2a1610", anchor="w").pack(fill=tk.X)
            tk.Label(r_info, text=r_data["description"], font=("Georgia", 9, "italic"), fg="#cccccc", bg="#2a1610", anchor="w").pack(fill=tk.X)
            
            req_parts = []
            has_all = True
            for ing_k, ing_needed in r_data["ingredients"].items():
                have_cnt = inv_counts.get(ing_k, 0)
                ing_name = HERBS_DB.get(ing_k, {}).get("name", MONSTER_INGREDIENTS_DB.get(ing_k, {}).get("name", ing_k))
                ing_icon = HERBS_DB.get(ing_k, {}).get("icon", MONSTER_INGREDIENTS_DB.get(ing_k, {}).get("icon", "📦"))
                if have_cnt < ing_needed:
                    has_all = False
                    req_parts.append(f"{ing_icon} {ing_name}: {have_cnt}/{ing_needed} ❌")
                else:
                    req_parts.append(f"{ing_icon} {ing_name}: {have_cnt}/{ing_needed} ✅")
            
            tk.Label(r_info, text="Wymagane: " + " | ".join(req_parts), font=("Georgia", 8, "bold"), fg="#f4d03f", bg="#2a1610", anchor="w").pack(fill=tk.X, pady=(2, 0))
            
            if has_all:
                def brew(rid=r_id, rinfo=r_data):
                    for ing_k, ing_needed in rinfo["ingredients"].items():
                        removed = 0
                        for i_dict in list(self.player.inventory):
                            if i_dict.get("id") == ing_k and removed < ing_needed:
                                self.player.inventory.remove(i_dict)
                                removed += 1
                                
                    if "is_item_reward" in rinfo:
                        self.player.add_to_inventory(rinfo["is_item_reward"], is_reward=True)
                        self.log_msg(f"⚗️ Uwarzono: {rinfo['name']}! Dodano do plecaka.")
                    else:
                        dur = rinfo.get("duration_fights", 5)
                        self.player.active_buffs[rid] = self.player.active_buffs.get(rid, 0) + dur
                        self.log_msg(f"⚗️ Wypito świeżo uwarzony {rinfo['name']}!")
                        
                    self.player.record_achievement_stat("potions_brewed", 1, mode="add")
                    if rid == "elixir_psychedelic":
                        self.player.record_achievement_stat("psychedelic_brewed", 1, mode="add")
                        self.start_psychedelic_trip(60)
                        
                    sounds.play_coin()
                    sounds.play_quest_complete()
                    self.update_sidebar()
                    self.show_alchemy()
                    
                ctk.CTkButton(r_card, text="⚗️ Uwarz Eliksir", width=120, font=("Georgia", 10, "bold"), fg_color="#8e44ad", hover_color="#9b59b6", command=brew).pack(side=tk.RIGHT, padx=10, pady=8)
            else:
                ctk.CTkButton(r_card, text="Brak składników", width=120, font=("Georgia", 9, "italic"), fg_color="#2a1610", text_color="#888", state=tk.DISABLED).pack(side=tk.RIGHT, padx=10, pady=8)

    def update_alchemy_timers(self):
        """Automatyczne odświeżanie zegarów odliczających wzrost ziół co 1 sekundę w czasie rzeczywistym."""
        if self.current_view != "alchemy" or not hasattr(self, 'alchemy_plot_widgets'):
            return
            
        now = time.time()
        for item in self.alchemy_plot_widgets:
            plot = item['plot']
            h_type = item['type']
            lbl = item['lbl']
            btn = item['btn']
            
            if not lbl.winfo_exists() or not btn.winfo_exists():
                continue
                
            planted = plot.get("planted_at", 0)
            g_time = plot.get("growth_time", 60)
            elapsed = now - planted
            
            if elapsed >= g_time:
                lbl.configure(text="✅ GOTOWE DO ZBIORU!", font=("Georgia", 9, "bold"), fg="#2ecc71")
                def make_harvest(p=plot, ht=h_type):
                    def do_h():
                        count = 2 if getattr(self.player, 'permanent_perks', None) and "perk_alchemist_touch" in self.player.permanent_perks else 1
                        for _ in range(count):
                            self.player.add_to_inventory(ht, is_reward=True)
                        p["planted_at"] = time.time()
                        self.player.record_achievement_stat("herbs_harvested", count, mode="add")
                        sounds.play_coin()
                        self.log_msg(f"🌿 Zebrano {count}x {HERBS_DB[ht]['name']}! Posadzono nowe nasiona.")
                        self.update_sidebar()
                        self.show_alchemy()
                    return do_h
                btn.configure(
                    text="Zbierz Zioło",
                    state=tk.NORMAL,
                    fg_color="#27ae60",
                    hover_color="#2ecc71",
                    text_color="white",
                    font=("Georgia", 9, "bold"),
                    command=make_harvest(plot, h_type)
                )
            else:
                rem_sec = max(0, int(g_time - elapsed))
                lbl.configure(text=f"🌱 Rośnie... ({rem_sec}s)", font=("Georgia", 9, "italic"), fg="#f39c12")
                btn.configure(
                    text="Czekaj...",
                    state=tk.DISABLED,
                    fg_color="#2a1610",
                    text_color="#888",
                    font=("Georgia", 9, "italic")
                )
                
        self.alchemy_timer_id = self.root.after(1000, self.update_alchemy_timers)


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

        # Szybka walka z bossami
        f_boss = tk.Frame(win, bg="#1a100b", bd=2, relief=tk.GROOVE)
        f_boss.pack(fill=tk.X, padx=20, pady=8)
        
        tk.Label(f_boss, text="👹 SZYBKA WALKA Z BOSSAMI (TESTY):", font=("Georgia", 11, "bold"), fg="#e74c3c", bg="#1a100b").pack(pady=4)
        
        b_box = tk.Frame(f_boss, bg="#1a100b")
        b_box.pack(fill=tk.X, padx=5, pady=4)
        
        ctk.CTkButton(b_box, text="⚔️ Walcz: Giga Ork Ptyś (Loch 1)", fg_color="#7f1d1d", text_color="#f4d03f", font=("Georgia", 10, "bold"), 
                      command=lambda: (win.destroy(), self.debug_fight_boss("boss_ptys", skip_cinematic=True))).grid(row=0, column=0, padx=4, pady=3, sticky="ew")
        
        ctk.CTkButton(b_box, text="⚔️ Walcz: Kollman (Loch 2)", fg_color="#7f1d1d", text_color="#f4d03f", font=("Georgia", 10, "bold"), 
                      command=lambda: (win.destroy(), self.debug_fight_boss("boss_kollman", skip_cinematic=True))).grid(row=0, column=1, padx=4, pady=3, sticky="ew")
                      
        ctk.CTkButton(b_box, text="🎬 Cutscenka + Walka: Ork Ptyś", fg_color="#3e2723", text_color="#a8ff9e", font=("Georgia", 10, "bold"), 
                      command=lambda: (win.destroy(), self.debug_fight_boss("boss_ptys", skip_cinematic=False))).grid(row=1, column=0, columnspan=2, padx=4, pady=3, sticky="ew")
                      
        b_box.columnconfigure(0, weight=1)
        b_box.columnconfigure(1, weight=1)

        # Testy Ekwipunku, Klejnotów, Osiągnięć i Alchemii
        f_inv_test = tk.Frame(win, bg="#1a100b", bd=2, relief=tk.GROOVE)
        f_inv_test.pack(fill=tk.X, padx=20, pady=6)
        tk.Label(f_inv_test, text="🔮 TESTY NOWYCH SYSTEMÓW (KLEJNOTY, ALCHEMIA, OSIĄGNIĘCIA):", font=("Georgia", 10, "bold"), fg="#f39c12", bg="#1a100b").pack(pady=3)
        inv_box = tk.Frame(f_inv_test, bg="#1a100b")
        inv_box.pack(fill=tk.X, padx=5, pady=3)
        
        def debug_add_gems():
            for gid in GEMS_DB:
                self.player.add_to_inventory(gid, is_reward=True)
            self.log_msg("🔮 [DEBUG] Dodano po 1 szt. każdego Magicznego Klejnotu!")
            lbl_status.configure(text="Dodano komplet klejnotów do plecaka!")
            self.update_sidebar()

        def debug_add_socketed_item():
            item_d = {"id": "wep_mithril_blade", "lvl": 3, "sockets": [None, None]}
            self.player.add_to_inventory(item_d, is_reward=True)
            self.log_msg("💎 [DEBUG] Dodano Mithrilowe Ostrze +3 z 2 wolnymi gniazdami!")
            lbl_status.configure(text="Dodano broń z 2 gniazdami!")
            self.update_sidebar()

        def debug_add_alchemy_items():
            for hid in HERBS_DB:
                self.player.add_to_inventory(hid, is_reward=True)
                self.player.add_to_inventory(hid, is_reward=True)
            for mid in MONSTER_INGREDIENTS_DB:
                self.player.add_to_inventory(mid, is_reward=True)
                self.player.add_to_inventory(mid, is_reward=True)
            self.log_msg("🧪 [DEBUG] Dodano komplet ziół i składników potworów (po 2 szt.)!")
            lbl_status.configure(text="Dodano składniki alchemiczne!")
            self.update_sidebar()

        def debug_grow_garden():
            now = time.time()
            for p in getattr(self.player, 'herb_garden', []):
                p["planted_at"] = now - 9999
            self.log_msg("🌱 [DEBUG] Wszystkie zioła w ogrodzie Domci natychmiast dojrzały!")
            lbl_status.configure(text="Zioła w ogrodzie gotowe do zbioru!")
            self.update_sidebar()

        def debug_psychedelic():
            self.start_psychedelic_trip(60)
            self.log_msg("🌀 [DEBUG] Aktywowano Ziółko (60-sekundowa psychodela i deformacja świata)!")
            lbl_status.configure(text="Aktywowano Ziółko (60s)!")
            self.update_sidebar()

        def debug_complete_achievements():
            self.player.achievement_stats["total_kills"] = 1000
            self.player.achievement_stats["total_crits"] = 100
            self.player.achievement_stats["boss_ptys_kills"] = 5
            self.player.achievement_stats["boss_kollman_kills"] = 5
            self.player.achievement_stats["dungeons_cleared"] = 20
            self.player.achievement_stats["upgrades_done"] = 20
            self.player.achievement_stats["max_upgrade_level"] = 9
            self.player.achievement_stats["gems_socketed"] = 10
            self.player.achievement_stats["herbs_harvested"] = 50
            self.player.achievement_stats["potions_brewed"] = 25
            self.player.achievement_stats["total_gold_earned"] = 200000
            self.log_msg("🏆 [DEBUG] Zaktualizowano statystyki: Wszystkie osiągnięcia gotowe do odbioru!")
            lbl_status.configure(text="Wszystkie osiągnięcia ukończone!")
            self.update_sidebar()

        ctk.CTkButton(inv_box, text="🔮 +Klejnoty (Komplet)", fg_color="#27ae60", text_color="white", font=("Georgia", 9, "bold"), command=debug_add_gems).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(inv_box, text="💎 +Broń (2 Gniazda)", fg_color="#2980b9", text_color="white", font=("Georgia", 9, "bold"), command=debug_add_socketed_item).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(inv_box, text="🧪 +Składniki Alchemii", fg_color="#8e44ad", text_color="white", font=("Georgia", 9, "bold"), command=debug_add_alchemy_items).grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        
        ctk.CTkButton(inv_box, text="🌱 Dojrzyj Ogród Ziół", fg_color="#16a085", text_color="white", font=("Georgia", 9, "bold"), command=debug_grow_garden).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(inv_box, text="🌀 Włącz Psychodelię", fg_color="#6c5ce7", text_color="white", font=("Georgia", 9, "bold"), command=debug_psychedelic).grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(inv_box, text="🏆 Odblokuj Osiągnięcia", fg_color="#d35400", text_color="white", font=("Georgia", 9, "bold"), command=debug_complete_achievements).grid(row=1, column=2, padx=2, pady=2, sticky="ew")

        inv_box.columnconfigure(0, weight=1)
        inv_box.columnconfigure(1, weight=1)
        inv_box.columnconfigure(2, weight=1)

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

    def open_bounty_board(self):
        if not self.player: return
        if not hasattr(self.player, 'bounties') or not self.player.bounties:
            self.player.bounties = generate_daily_bounties(self.player.level)
            
        win = tk.Toplevel(self.root)
        win.title("📋 TABLICA OGŁOSZEŃ - GOSPODA BARNABY")
        win.geometry("900x750")
        win.configure(bg="#1a100b")
        win.transient(self.root)
        win.grab_set()
        
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 900) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 750) // 2
        win.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(win, bg="#2c1a12", bd=3, relief=tk.RIDGE)
        header.pack(fill=tk.X, padx=15, pady=12)
        
        tk.Label(header, text="📋 TABLICA ZLECEŃ KARCZMARZA BARNABY 📋", font=("Georgia", 18, "bold"), fg="#f4d03f", bg="#2c1a12").pack(pady=(8, 2))
        tk.Label(header, text="Wypełniaj zlecenia na potwory, lochy i kowalstwo, by zdobywać złoto, doświadczenie oraz cenne eliksiry!", font=("Georgia", 11, "italic"), fg="#ddd", bg="#2c1a12").pack(pady=(0, 8))
        
        # Cards container
        cards_frame = tk.Frame(win, bg="#1a100b")
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        def refresh_board_ui():
            for w in cards_frame.winfo_children():
                w.destroy()
                
            for idx, b in enumerate(self.player.bounties):
                card = tk.Frame(cards_frame, bg="#2c1a12", bd=2, relief=tk.GROOVE)
                card.pack(fill=tk.X, padx=10, pady=8)
                
                # Left info
                info_f = tk.Frame(card, bg="#2c1a12")
                info_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)
                
                status_icon = "📜" if b.status == "AVAILABLE" else ("⏳" if b.status == "IN_PROGRESS" else ("🎁" if b.status == "COMPLETED" else "✅"))
                tk.Label(info_f, text=f"{status_icon} {b.title}", font=("Georgia", 14, "bold"), fg="#f4d03f", bg="#2c1a12").pack(anchor="w")
                tk.Label(info_f, text=b.description, font=("Georgia", 10, "italic"), fg="#ccc", bg="#2c1a12", wraplength=520, justify=tk.LEFT).pack(anchor="w", pady=(2, 6))
                
                # Postęp
                prog_text = f"🎯 Cel: {b.current_count} / {b.target_count}"
                if b.status == "CLAIMED":
                    prog_text += " [ZREALIZOWANO]"
                prog_color = "#2ecc71" if b.status in ["COMPLETED", "CLAIMED"] else "#f39c12"
                tk.Label(info_f, text=prog_text, font=("Georgia", 11, "bold"), fg=prog_color, bg="#2c1a12").pack(anchor="w")
                
                # Nagrody
                rew_text = f"💰 +{b.gold_reward}g  |  ⭐ +{b.exp_reward} EXP"
                if b.item_reward:
                    rew_text += "  |  🧪 +1 Mikstura Zdrowia"
                tk.Label(info_f, text=f"🎁 Nagroda: {rew_text}", font=("Georgia", 10, "bold"), fg="#e67e22", bg="#2c1a12").pack(anchor="w", pady=(2, 0))
                
                # Right action button
                act_f = tk.Frame(card, bg="#2c1a12")
                act_f.pack(side=tk.RIGHT, padx=15, pady=10)
                
                if b.status == "AVAILABLE":
                    def do_accept(bounty=b):
                        bounty.accept()
                        sounds.play_quest_accept()
                        self.log_msg(f"📋 Przyjęto zlecenie z tablicy: '{bounty.title}'!")
                        refresh_board_ui()
                    ctk.CTkButton(act_f, text="Przyjmij Zlecenie", font=("Georgia", 12, "bold"), fg_color="#f1c40f", text_color="black", hover_color="#f39c12", command=do_accept).pack(pady=10)
                elif b.status == "IN_PROGRESS":
                    ctk.CTkButton(act_f, text=f"W trakcie ({b.current_count}/{b.target_count})", font=("Georgia", 11, "italic"), fg_color="#3e2723", text_color="#aaaaaa", state=tk.DISABLED).pack(pady=10)
                elif b.status == "COMPLETED":
                    def do_claim(bounty=b):
                        if bounty.claim_reward(self.player):
                            sounds.play_quest_complete()
                            sounds.play_coin()
                            self.log_msg(f"🎁 Odebrano nagrodę za zlecenie '{bounty.title}' (+{bounty.gold_reward}g, +{bounty.exp_reward} EXP)!")
                            self.update_sidebar()
                            refresh_board_ui()
                    ctk.CTkButton(act_f, text="🎁 ODBIERZ NAGRODĘ!", font=("Georgia", 12, "bold"), fg_color="#27ae60", hover_color="#2ecc71", text_color="white", command=do_claim).pack(pady=10)
                elif b.status == "CLAIMED":
                    tk.Label(act_f, text="✅ Odebrano", font=("Georgia", 12, "bold"), fg="#7f8c8d", bg="#2c1a12").pack(pady=10)
                    
        refresh_board_ui()
        
        # Footer with reroll button
        footer = tk.Frame(win, bg="#1a100b")
        footer.pack(fill=tk.X, padx=15, pady=12)
        
        def reroll_bounties():
            cost = 50
            if self.player.gold < cost:
                messagebox.showwarning("Brak Złota", f"Potrzebujesz {cost} złota, aby zorganizować nowe zlecenia!")
                return
            if messagebox.askyesno("Odświeżenie Tablicy", f"Czy chcesz wydać {cost} złota na zerwanie obecnych ogłoszeń i wygenerowanie 3 nowych zleceń?"):
                self.player.gold -= cost
                self.player.bounties = generate_daily_bounties(self.player.level)
                sounds.play_coin()
                self.update_sidebar()
                self.log_msg("📋 Odświeżono Tablicę Ogłoszeń u Karczmarza Barnaby.")
                refresh_board_ui()
                
        ctk.CTkButton(footer, text="🔄 Nowe Zlecenia (Koszt: 50g)", font=("Georgia", 12, "bold"), fg_color="#34495e", hover_color="#415b76", command=reroll_bounties).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(footer, text="Zamknij", font=("Georgia", 11, "italic"), fg_color="#2a1610", text_color="#aaa", command=win.destroy).pack(side=tk.RIGHT, padx=10)

    def open_tavern_rest(self):
        """Okienko odpoczynku w tawernie z dynamicznie napełniającym się paskiem zdrowia w czasie rzeczywistym."""
        max_hp = self.player.get_max_hp()
        if self.player.hp >= max_hp:
            messagebox.showinfo(
                "Pełnia Sił", 
                f"Gracz {self.player.name} czuje się wyśmienicie i ma już 100% zdrowia ({int(self.player.hp)}/{max_hp} HP)!"
            )
            return

        sounds.play_heal()

        rest_win = tk.Toplevel(self.root)
        rest_win.title(f"Odpoczynek w Tawernie - {self.player.name}")
        rest_win.geometry("520x350")
        rest_win.configure(bg="#1c100b")
        rest_win.transient(self.root)
        rest_win.grab_set()

        rest_win.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width() - 520) // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - 350) // 2
        rest_win.geometry(f"520x350+{max(0, rx)}+{max(0, ry)}")

        tk.Label(
            rest_win, 
            text="🛏️ ODPOCZYNEK PRZY CIEPŁYM KOMINKU 🛏️", 
            font=("Georgia", 15, "bold"), 
            fg="#f4d03f", 
            bg="#1c100b"
        ).pack(pady=(18, 6))

        lbl_hero = tk.Label(
            rest_win, 
            text=f"Gracz {self.player.name} odpoczywa w tawernie...", 
            font=("Georgia", 12, "bold"), 
            fg="#e0e0e0", 
            bg="#1c100b"
        )
        lbl_hero.pack(pady=4)

        lbl_desc = tk.Label(
            rest_win, 
            text="Ciepło paleniska, kufel miodu i miękkie posłanie powoli przywracają Twoje siły witalne (~20s na pełny odpoczynek).\nMikstury z plecaka leczą natychmiast!", 
            font=("Georgia", 10, "italic"), 
            fg="#aaaaaa", 
            bg="#1c100b",
            wraplength=460,
            justify=tk.CENTER
        )
        lbl_desc.pack(pady=(2, 16))

        # Kontener paska zdrowia
        bar_w = 420
        bar_h = 32
        bar_bg = tk.Frame(rest_win, bg="#0d0705", bd=3, relief=tk.SUNKEN, width=bar_w, height=bar_h)
        bar_bg.pack(pady=5)
        bar_bg.pack_propagate(False)

        init_ratio = max(0.0, min(1.0, self.player.hp / max_hp))
        bar_fill = tk.Frame(bar_bg, bg="#22c55e", width=int(bar_w * init_ratio), height=bar_h)
        bar_fill.place(x=0, y=0, relheight=1.0)

        lbl_hp_val = tk.Label(
            bar_bg, 
            text=f"❤ HP: {int(self.player.hp)} / {max_hp} ({int(init_ratio * 100)}%)", 
            font=("Georgia", 11, "bold"), 
            fg="white", 
            bg="#0d0705"
        )
        lbl_hp_val.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        btn_action = ctk.CTkButton(
            rest_win, 
            text="Przerwij Odpoczynek", 
            font=("Georgia", 11, "bold"),
            fg_color="#7f1d1d", 
            hover_color="#991b1b",
            text_color="#f4d03f",
            width=220,
            height=32
        )
        btn_action.pack(pady=(22, 10))

        # Pętla regeneracji w czasie rzeczywistym (~20 sekund od 0 do 100%, 0.5% max HP co 100ms)
        heal_per_tick = max(0.2, float(max_hp) * 0.005)
        rest_timer_id = [None]

        def on_close():
            if rest_timer_id[0]:
                try:
                    self.root.after_cancel(rest_timer_id[0])
                except Exception:
                    pass
                rest_timer_id[0] = None
            rest_win.destroy()

        rest_win.protocol("WM_DELETE_WINDOW", on_close)
        btn_action.configure(command=on_close)

        def tick_rest():
            if not rest_win.winfo_exists():
                return
            
            cur_max = self.player.get_max_hp()
            self.player.hp = min(cur_max, self.player.hp + heal_per_tick)
            ratio = max(0.0, min(1.0, self.player.hp / cur_max))
            
            bar_fill.place(x=0, y=0, width=int(bar_w * ratio), relheight=1.0)
            lbl_hp_val.configure(text=f"❤ HP: {int(self.player.hp)} / {cur_max} ({int(ratio * 100)}%)")
            self.update_sidebar()

            if self.player.hp >= cur_max:
                sounds.play_level_up()
                lbl_hero.configure(text=f"✨ Gracz {self.player.name} w pełni zregenerował siły życiowe! ✨", fg="#2ecc71")
                lbl_desc.configure(text="Czujesz niesamowity przypływ energii i jesteś gotów do kolejnych wypraw oraz walk!")
                btn_action.configure(text="✅ Wstań wypoczęty (Zamknij)", fg_color="#27ae60", hover_color="#2ecc71", text_color="#ffffff")
                self.log_msg(f"🛏️ [TAWERNA] {self.player.name} odpoczął w tawernie i w pełni zregenerował zdrowie ({cur_max} HP)!")
                rest_timer_id[0] = None
            else:
                rest_timer_id[0] = self.root.after(100, tick_rest)

        rest_timer_id[0] = self.root.after(100, tick_rest)

    def claim_barnaby_stash(self):
        """Odbiór odłożonych nagród z depozytu u Karczmarza Barnaby."""
        if not hasattr(self.player, 'inventory_stash') or not self.player.inventory_stash:
            messagebox.showinfo("Depozyt Barnaby", "Twój depozyt u Karczmarza Barnaby jest obecnie pusty!\n\nGdy w przyszłości Twój ekwipunek będzie pełny (80/80 slotów), wszelkie zdobyte nagrody z zadań, zleceń, potworów i lochów trafią tutaj, byś mógł je później bezpiecznie odebrać.")
            return
            
        free_slots = self.player.get_max_inventory_slots() - len(self.player.inventory)
        if free_slots <= 0:
            stash_count = len(self.player.inventory_stash)
            messagebox.showwarning("Pełny Ekwipunek", f"W depozycie u Karczmarza czeka {stash_count} przedmiot(ów), ale Twój ekwipunek jest wciąż pełny (80/80 slotów)!\n\nZwolnij miejsce w plecaku (np. sprzedaj zbędne przedmioty w Ekwipunku), a następnie wróć, aby odebrać nagrody.")
            return
            
        claimed = []
        to_claim = min(free_slots, len(self.player.inventory_stash))
        for _ in range(to_claim):
            item_d = self.player.inventory_stash.pop(0)
            self.player.inventory.append(item_d)
            it = get_item(item_d)
            claimed.append(it.name if it else item_d.get('id', 'Przedmiot'))
            
        sounds.play_quest_complete()
        names_str = ", ".join(claimed)
        self.log_msg(f"🎁 Odebrano z depozytu Barnaby ({len(claimed)} szt.): {names_str}")
        self.update_sidebar()
        
        remaining = len(self.player.inventory_stash)
        if remaining > 0:
            messagebox.showinfo("Odebrano Nagrody", f"Pomyślnie odebrano {len(claimed)} przedmiot(ów) z depozytu:\n{names_str}\n\nW depozycie Karczmarza pozostało jeszcze {remaining} przedmiot(ów). Zwolnij więcej miejsca, aby odebrać resztę!")
        else:
            messagebox.showinfo("Odebrano Nagrody", f"Pomyślnie odebrano wszystkie nagrody z depozytu ({len(claimed)} szt.):\n{names_str}")
            
        if self.current_view == "equipment":
            self.show_equipment()
        elif self.current_view == "tavern":
            self.show_tavern()

    def save_and_quit(self):
        if self.player and self.current_save_path:
            save_game(self.player, self.current_save_path)
            self.log_msg("Zapisano grę.")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = IdleRPGApp(root)
    root.mainloop()
