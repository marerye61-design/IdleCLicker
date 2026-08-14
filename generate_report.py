import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

print("Generowanie raportu...")

# 1. Ładowanie danych
df_combat = pd.read_csv('sim_combat_winrates.csv')
df_upgrades = pd.read_csv('sim_upgrades_efficiency.csv')
df_equip = pd.read_csv('sim_equipment_stats.csv')

html_content = """
<html>
<head>
<title>Raport Balansu - Idle RPG</title>
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #f0f0f0; margin: 40px; }
    h1, h2, h3 { color: #f4d03f; }
    .card { background-color: #2d2d2d; border-radius: 8px; padding: 20px; margin-bottom: 30px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
    img { max-width: 100%; height: auto; border-radius: 4px; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.9em; }
    th, td { border: 1px solid #444; padding: 8px; text-align: center; }
    th { background-color: #3d3d3d; color: #f4d03f; }
    tr:nth-child(even) { background-color: #2a2a2a; }
</style>
</head>
<body>
<h1>Raport Symulacji Balansu Gry (Idle RPG)</h1>
<p>Dokument wygenerowany automatycznie z 500 iteracjami walk Monte Carlo na punkt pomiarowy.</p>
"""

# --- Wykres 1: Szansa na wygraną według poziomu ---
html_content += """<div class="card">
<h2>1. Analiza Walk: Win-Rate</h2>
<p>Wykres przedstawia szansę gracza na pokonanie wroga na odpowiednim progu poziomowym, wyposażonego w pełny ekwipunek "Best in Slot" i bohatera Eczme (brak używania mikstur leczących).</p>
"""
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#2d2d2d')
ax.set_facecolor('#2d2d2d')

for enemy in df_combat['Enemy Name'].unique():
    subset = df_combat[df_combat['Enemy Name'] == enemy]
    ax.plot(subset['Player Lvl'], subset['Win Rate %'], marker='o', label=enemy)

ax.set_title('Win Rate vs Wrogowie wg Poziomów', color='white')
ax.set_xlabel('Poziom Gracza', color='white')
ax.set_ylabel('Win Rate (%)', color='white')
ax.tick_params(colors='white')
ax.grid(True, color='#555555', linestyle='--', alpha=0.5)
ax.legend(facecolor='#2d2d2d', labelcolor='white')

html_content += f'<img src="data:image/png;base64,{fig_to_base64(fig)}" />'
html_content += "</div>"
plt.close(fig)

# --- Szczegółowa Analityka Walk (Autobalans) ---
html_content += """<div class="card">
<h2>2. Szczegółowe Statystyki Batalistyczne (Autobalans)</h2>
<p>Kluczowe metryki pomagające zidentyfikować wrogów, którzy są zbyt trudni ("HP Shortfall" pokazuje ile wrogowi zostawało zdrowia, gdy gracz ginął) lub zbyt łatwi.</p>
"""
# Tabela ze wszystkim
display_cols = [
    "Player Lvl", "Enemy Name", "Win Rate %", 
    "Avg Turns (Win)", "Avg Player HP Left (Win)", "Avg Enemy HP Left (Loss)", 
    "Player Avg DMG/Turn", "Enemy Avg DMG/Turn"
]
html_content += df_combat[display_cols].to_html(index=False, classes='table')
html_content += "</div>"

# --- Wykres 2: Opłacalność Ulepszeń (Kowal) ---
html_content += """<div class="card">
<h2>3. Ekonomia Kuźni (Koszt 1 punktu Statystyki)</h2>
"""
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#2d2d2d')
ax.set_facecolor('#2d2d2d')

rarities = df_upgrades['Rarity'].unique()
colors = {'Zwykły': '#cccccc', 'Legendarny': '#f4d03f', 'Mityczny': '#e74c3c'}

for rarity in rarities:
    subset = df_upgrades[(df_upgrades['Rarity'] == rarity) & (df_upgrades['Upgrade Level'] > 0)]
    avg_cost = subset.groupby('Upgrade Level')['Gold per Stat Point'].mean()
    ax.plot(avg_cost.index, avg_cost.values, marker='s', label=rarity, color=colors.get(rarity, 'white'))

ax.set_title('Średni Koszt Ulepszenia za 1 Pkt Statystyki wg Rzadkości', color='white')
ax.set_xlabel('Poziom Ulepszenia (+X)', color='white')
ax.set_ylabel('Złoto / 1 Pkt Statystyki', color='white')
ax.tick_params(colors='white')
ax.grid(True, color='#555555', linestyle='--', alpha=0.5)
ax.legend(facecolor='#2d2d2d', labelcolor='white')

html_content += f'<img src="data:image/png;base64,{fig_to_base64(fig)}" />'
html_content += "</div>"
plt.close(fig)

html_content += """
</body>
</html>
"""

desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'Raport_Balansu_IdleClicker.html')
with open(desktop_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Pomyślnie wygenerowano raport: {desktop_path}")
