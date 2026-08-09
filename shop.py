class FantasyShop:
    def __init__(self):
        # Asortyment sklepu podzielony na kategorie poziomowe
        self.tiers = {
            0: {
                "name": "Alchemik",
                "label": "Mikstury (Skalowane)",
                "req_level": 1,
                "items": ["pot_hp"]
            },
            1: {
                "name": "Zestaw Nowicjusza",
                "label": "Poz. 1 - 5",
                "req_level": 1,
                "items": ["wep_wooden_club", "arm_leather", "helm_leather", "acc_ring_small"]
            },
            2: {
                "name": "Zestaw Żelazny",
                "label": "Poz. 5 - 15",
                "req_level": 5,
                "items": ["wep_iron_sword", "arm_iron_plate", "helm_iron", "acc_iron_ring"]
            },
            3: {
                "name": "Zestaw Stalowy",
                "label": "Poz. 15 - 30",
                "req_level": 15,
                "items": ["wep_steel_sword", "arm_steel_plate", "helm_steel", "acc_silver_amulet"]
            },
            4: {
                "name": "Zestaw Mithrilowy",
                "label": "Poz. 30 - 50",
                "req_level": 30,
                "items": ["wep_mithril_blade", "arm_mithril_mail", "helm_mithril", "acc_ruby_pendant"]
            },
            5: {
                "name": "Zestaw Adamantowy",
                "label": "Poz. 50 - 75",
                "req_level": 50,
                "items": ["wep_adamant_greatsword", "arm_adamant_cuirass", "helm_adamant", "acc_dragon_eye"]
            },
            6: {
                "name": "Zestaw Boski",
                "label": "Poz. 75+",
                "req_level": 75,
                "items": ["wep_shadow_slayer", "arm_dragon_scale", "helm_demon_crown", "acc_god_talisman"]
            }
        }
        
        self.stock = [item_id for t in self.tiers.values() for item_id in t["items"]]

    def show(self, player):
        from items import ITEMS_DB
        print("\n--- SKLEP FANTASY ---")
        print("Kupuj ekwipunek, by stawać się silniejszym!")
        print(f"Twoje złoto: {player.gold}")
        
        for idx, item_id in enumerate(self.stock):
            item = ITEMS_DB.get(item_id)
            if item:
                print(f"[{idx+1}] {item.name} - {item.value} złota")
                stat_str = ", ".join([f"{k.upper()}: +{v}" for k, v in item.stats.items()])
                print(f"    Statystyki: {stat_str}")
        
    def buy(self, player, choice_str):
        from items import ITEMS_DB
        try:
            idx = int(choice_str) - 1
            if 0 <= idx < len(self.stock):
                item_id = self.stock[idx]
                item = ITEMS_DB.get(item_id)
                if item and player.gold >= item.value:
                    player.gold -= item.value
                    player.add_to_inventory(item_id)
                    print(f"Kupiłeś {item.name}!")
                    return True
                else:
                    print("Nie masz wystarczająco złota!")
            else:
                print("Nieprawidłowy wybór.")
        except ValueError:
            print("Wpisz numer przedmiotu.")
        return False
