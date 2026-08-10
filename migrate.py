import re
import os
import shutil

FILE = "main.py"
BACKUP = "main_backup.py"

if not os.path.exists(BACKUP):
    shutil.copy(FILE, BACKUP)

with open(BACKUP, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Importy
if "import customtkinter as ctk" not in content:
    content = content.replace("import tkinter as tk", "import tkinter as tk\nimport customtkinter as ctk\nctk.set_appearance_mode('dark')\nctk.set_default_color_theme('dark-blue')")

# 2. Główne okno zostawiamy jako tk.Tk() aby uniknąć konfliktów z place()
# content = content.replace("self.root = tk.Tk()", "self.root = ctk.CTk()")
# content = content.replace("class ScrollableFrame(tk.Frame):", "class ScrollableFrame(ctk.CTkFrame):")

# 3. Widgets - proste zamiany nazw klas (aby zachować tk namespace zostawiamy resztę na razie, tylko podmieniamy wywołania ctk)
# Uwaga: CTkButton domyślnie używa fg_color zamiast bg, text_color zamiast fg. 
# Aby to bezpiecznie zmigrować w tak ogromnym kodzie, użyjemy wyrażeń regularnych.

def replace_widget(match, widget_name):
    args = match.group(1)
    # Usuwamy niekompatybilne parametry
    args = re.sub(r',\s*relief=[^,)]+', '', args)
    args = re.sub(r',\s*bd=[^,)]+', '', args)
    args = re.sub(r',\s*highlightthickness=[^,)]+', '', args)
    args = re.sub(r',\s*activebackground=[^,)]+', '', args)
    args = re.sub(r',\s*activeforeground=[^,)]+', '', args)
    args = re.sub(r',\s*style=[^,)]+', '', args)  # Usuwa parametr style="Fantasy.TButton" itp.
    
    # Zamiana bg -> fg_color, fg -> text_color
    args = re.sub(r'\bbg\s*=', 'fg_color=', args)
    args = re.sub(r'\bfg\s*=', 'text_color=', args)
    
    # W CTkLabel anchor "e" / "w" działa nieco inaczej, ale zostawmy
    return f"ctk.CTk{widget_name}({args})"

content = re.sub(r'\btk\.Button\((.*?)\)', lambda m: replace_widget(m, 'Button'), content)
content = re.sub(r'\bttk\.Button\((.*?)\)', lambda m: replace_widget(m, 'Button'), content)

content = content.replace("tctk.", "ctk.")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Migracja regex zakończona pomyślnie. Utworzono kopię zapasową w main_backup.py.")
