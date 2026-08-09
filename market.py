class Building:
    def __init__(self, b_id, name, description, base_cost, gold_per_sec, cost_multiplier=1.15):
        self.b_id = b_id
        self.name = name
        self.description = description
        self.base_cost = base_cost
        self.gold_per_sec = gold_per_sec
        self.cost_multiplier = cost_multiplier

    def get_cost(self, count):
        return int(self.base_cost * (self.cost_multiplier ** count))

BUILDINGS_DB = {
    "b1": Building("b1", "Cukiernia Maślaka", "Produkuje lukrowane pączki i dowozi je do klasztorów. Słodki zysk!", 50, 1),
    "b2": Building("b2", "Strażnica Damiana", "Damian pobiera 'dobrowolne' myto od wędrowców w zamian za ochronę.", 500, 10),
    "b3": Building("b3", "Plantacja Ziół Domci", "Domcia hoduje rzadkie 'magiczne' grzybki i zioła na eksport.", 3000, 50),
    "b4": Building("b4", "Boisko Siatkarskie Eczme", "Eczme organizuje turnieje w lochach. Wpisowe jest wysokie, a przeżywalność niska.", 15000, 200),
    "b5": Building("b5", "Siłownia Pianka", "Pianek pobiera opłaty za patrzenie, jak podnosi ciężary i krzyczy.", 50000, 1000),
    "b6": Building("b6", "Warsztat 'BeeMWe' Yomena", "Yomen łata pęknięte uszczelki wywarem z czaszek. Zyski z napraw są ogromne!", 250000, 5000)
}

class Market:
    def __init__(self):
        self.buildings = BUILDINGS_DB

    def get_cost(self, player, b_id):
        if b_id in self.buildings:
            count = player.buildings.get(b_id, 0)
            return self.buildings[b_id].get_cost(count)
        return 0

    def show_buildings(self, player):
        print("\n--- SKLEP Z BUDYNKAMI ---")
        for b_id, building in self.buildings.items():
            count = player.buildings.get(b_id, 0)
            cost = building.get_cost(count)
            print(f"[{b_id}] {building.name} (Posiadasz: {count})")
            print(f"    Koszt: {cost} złota | Produkcja: +{building.gold_per_sec} złoto/sek")
            print(f"    Opis: {building.description}")

    def buy_building(self, player, b_id):
        if b_id in self.buildings:
            building = self.buildings[b_id]
            count = player.buildings.get(b_id, 0)
            cost = building.get_cost(count)
            
            if player.gold >= cost:
                player.gold -= cost
                player.buildings[b_id] = count + 1
                player.stats["gold_per_sec"] += building.gold_per_sec
                print(f"Sukces! Kupiłeś '{building.name}'.")
                return True
            else:
                print("Nie masz wystarczająco złota!")
                return False
        else:
            print("Nie ma takiego budynku.")
            return False
