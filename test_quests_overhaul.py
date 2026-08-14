import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import items
import quests
import npc_lore
import player

print("=== WERYFIKACJA ROZPIĘTOŚCI QUESTÓW (1 -> 50) I MOCY PRZEDMIOTÓW (>= 2X) ===\n")

p = player.Player("Tester_Spread")
p.migrate()

shop_comparisons = {
    "wep_maslak": ("wep_wooden_club", "Broń Lvl 1 (Pałka)"),
    "acc_eczme": ("acc_iron_ring", "Amulet Lvl 5 (Sygnet)"),
    "helm_pianek": ("helm_steel", "Hełm Lvl 15 (Przyłbica)"),
    "arm_damian": ("arm_mithril_mail", "Pancerz Lvl 30 (Mithril)"),
    "acc_domcia": ("acc_ruby_pendant", "Amulet Lvl 30 (Rubin)"),
    "wep_yomen": ("wep_adamant_greatsword", "Broń Lvl 50 (Adamant)")
}

for q in p.quests:
    q_item_id = q.rewards.get("item")
    q_item = items.get_item(q_item_id)
    comp_id, comp_name = shop_comparisons[q_item_id]
    comp_item = items.get_item(comp_id)
    
    print(f"📜 [Lvl {q.unlock_level:2d}] {q.name} ({q.npc_id.upper()})")
    print(f"   Cel: {q.requirements['kills']}")
    print(f"   🎁 Nagroda: {q_item.name} [{q_item.slot.upper()}] (Wymaga Lvl: {q_item.level_req})")
    print(f"   -> Statystyki Quest Item: {q_item.stats}")
    print(f"   -> Statystyki Standardowego Sklepowego ({comp_name}): {comp_item.stats}")
    
    # Check primary stat comparison
    primary_stat = "atk" if q_item.slot == "weapon" else ("def" if q_item.slot in ["armor", "helmet"] else "atk")
    q_val = q_item.stats.get(primary_stat, 0)
    c_val = comp_item.stats.get(primary_stat, 0)
    ratio = q_val / max(1, c_val)
    print(f"   ⚡ Porównanie głównej statystyki ({primary_stat.upper()}): Quest={q_val} vs Sklep={c_val} (Mnożnik: {ratio:.1f}x mocniejszy)")
    assert ratio >= 2.0, f"Przedmiot {q_item.name} nie jest 2x silniejszy od {comp_name}!"
    assert q.unlock_level >= q_item.level_req, f"Niezgodność poziomu: Quest unlock {q.unlock_level} < Item req {q_item.level_req}"
    print("   ✔ SPEŁNIA WARUNEK >= 2X MOCY ORAZ ZGODNOŚCI POZIOMU!\n")

print("✅ WSZYSTKIE 6 PRZEDMIOTÓW Z QUESTÓW SĄ CONAJMNIEJ 2X POTĘŻNIEJSZE I PERFEKCYJNIE ZBALANSOWANE DO 50 POZIOMU!")
