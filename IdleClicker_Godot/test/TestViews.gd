extends SceneTree

func _init():
	print("--- Testowanie ładowania wszystkich scen widoków ---")
	var views = [
		"res://scenes/views/CombatView.tscn",
		"res://scenes/views/DungeonsView.tscn",
		"res://scenes/views/StatsView.tscn",
		"res://scenes/views/InventoryView.tscn",
		"res://scenes/views/TavernView.tscn",
		"res://scenes/views/AlchemyView.tscn",
		"res://scenes/views/MarketView.tscn",
		"res://scenes/views/BlacksmithView.tscn",
		"res://scenes/views/AchievementsView.tscn"
	]

	for v_path in views:
		var scene = load(v_path)
		if scene == null:
			push_error("Błąd ładowania sceny: %s" % v_path)
			quit(1)
		var inst = scene.instantiate()
		if inst == null:
			push_error("Błąd instancjonowania: %s" % v_path)
			quit(1)
		print("[PASS] Pomyślnie załadowano: %s" % v_path.get_file())
		inst.free()

	print("Wszystkie widoki ładują się i instancjonują poprawnie!")
	quit(0)
