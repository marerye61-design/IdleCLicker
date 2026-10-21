class_name SaveSystem

const SAVES_DIR: String = "user://saves"
const LEGACY_SAVE_PATH: String = "user://savegame.json"

static var current_save_filename: String = ""

static func init_saves_dir() -> void:
	if not DirAccess.dir_exists_absolute(SAVES_DIR):
		DirAccess.make_dir_recursive_absolute(SAVES_DIR)

	# Bezpieczna migracja starego pojedynczego pliku zapisu user://savegame.json
	if FileAccess.file_exists(LEGACY_SAVE_PATH):
		print("[SaveSystem] Wykryto starszy plik zapisu %s. Rozpoczynanie migracji..." % LEGACY_SAVE_PATH)
		var file = FileAccess.open(LEGACY_SAVE_PATH, FileAccess.READ)
		if file:
			var json_str = file.get_as_text()
			file.close()

			var json = JSON.new()
			if json.parse(json_str) == OK and json.get_data() is Dictionary:
				var data: Dictionary = json.get_data()
				var hero_name: String = str(data.get("name", "Bohater")).strip_edges()
				if hero_name.is_empty():
					hero_name = "Bohater"
				var new_filename: String = sanitize_filename(hero_name) + ".json"
				var new_path: String = SAVES_DIR.path_join(new_filename)

				if not FileAccess.file_exists(new_path):
					var new_file = FileAccess.open(new_path, FileAccess.WRITE)
					if new_file:
						new_file.store_string(json_str)
						new_file.close()
						print("[SaveSystem] Zmigrowano zapis gry do profilu: %s" % new_path)

				# Zabezpiecz stary plik zmieniając rozszerzenie na .migrated
				DirAccess.rename_absolute(LEGACY_SAVE_PATH, LEGACY_SAVE_PATH + ".migrated")
				print("[SaveSystem] Migracja zakończona sukcesem. Kopia zapasowa zachowana.")

static func sanitize_filename(raw_name: String) -> String:
	var clean = raw_name.strip_edges().replace(" ", "_")
	var invalid_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
	for ch in invalid_chars:
		clean = clean.replace(ch, "")
	if clean.is_empty():
		clean = "Bohater"
	return clean

static func get_all_saves() -> Array[Dictionary]:
	init_saves_dir()
	var saves: Array[Dictionary] = []
	var dir = DirAccess.open(SAVES_DIR)
	if dir == null:
		return saves

	dir.list_dir_begin()
	var file_name = dir.get_next()
	while not file_name.is_empty():
		if not dir.current_is_dir() and file_name.ends_with(".json") and not file_name.ends_with(".bak"):
			var filepath = SAVES_DIR.path_join(file_name)
			var file = FileAccess.open(filepath, FileAccess.READ)
			if file:
				var json_str = file.get_as_text()
				file.close()
				var json = JSON.new()
				if json.parse(json_str) == OK and json.get_data() is Dictionary:
					var data: Dictionary = json.get_data()
					var char_name: String = str(data.get("name", file_name.get_basename()))
					var lvl: int = int(data.get("level", 1))
					var gold: int = int(data.get("gold", 0))
					var mod_time = FileAccess.get_modified_time(filepath)

					var dt = Time.get_datetime_dict_from_unix_time(mod_time)
					var date_str = "%04d-%02d-%02d %02d:%02d" % [dt.year, dt.month, dt.day, dt.hour, dt.minute]

					saves.append({
						"filename": file_name,
						"filepath": filepath,
						"name": char_name,
						"level": lvl,
						"gold": gold,
						"modified_time": mod_time,
						"date_str": date_str
					})
		file_name = dir.get_next()
	dir.list_dir_end()

	# Sortowanie: najnowsze zapisy na początku
	saves.sort_custom(func(a, b): return a["modified_time"] > b["modified_time"])
	return saves

static func save_game(player: Player, filename: String = "") -> bool:
	init_saves_dir()
	if filename.is_empty():
		if not current_save_filename.is_empty():
			filename = current_save_filename
		else:
			filename = sanitize_filename(player.name) + ".json"

	if not filename.ends_with(".json"):
		filename += ".json"

	current_save_filename = filename
	var save_path = SAVES_DIR.path_join(filename)

	# Tworzenie kopii zapasowej .bak przed nadpisaniem
	if FileAccess.file_exists(save_path):
		var bak_path = save_path + ".bak"
		DirAccess.copy_absolute(save_path, bak_path)

	var file = FileAccess.open(save_path, FileAccess.WRITE)
	if file == null:
		push_error("Nie udało się otworzyć pliku do zapisu: %s" % save_path)
		return false

	var save_data = player.to_dict()
	var json_str = JSON.stringify(save_data, "\t")
	file.store_string(json_str)
	file.close()
	print("[SaveSystem] Gra zapisana pomyślnie w: %s" % save_path)
	return true

static func load_game(player: Player, filename: String = "") -> bool:
	init_saves_dir()
	if filename.is_empty():
		if not current_save_filename.is_empty():
			filename = current_save_filename
		else:
			var all = get_all_saves()
			if all.is_empty():
				print("[SaveSystem] Brak zapisów w katalogu %s." % SAVES_DIR)
				return false
			filename = all[0]["filename"]

	if not filename.ends_with(".json"):
		filename += ".json"

	var save_path = SAVES_DIR.path_join(filename)
	if not FileAccess.file_exists(save_path):
		var bak_path = save_path + ".bak"
		if FileAccess.file_exists(bak_path):
			save_path = bak_path
			print("[SaveSystem] Główny plik nie istnieje, wczytywanie z kopii: %s" % bak_path)
		else:
			push_error("Plik zapisu nie istnieje: %s" % save_path)
			return false

	var file = FileAccess.open(save_path, FileAccess.READ)
	if file == null:
		push_error("Nie udało się otworzyć pliku zapisu: %s" % save_path)
		return false

	var json_str = file.get_as_text()
	file.close()

	var json = JSON.new()
	var error = json.parse(json_str)
	if error != OK:
		# Awaryjna próba wczytania z .bak
		var bak_path = save_path + ".bak"
		if FileAccess.file_exists(bak_path) and save_path != bak_path:
			var bfile = FileAccess.open(bak_path, FileAccess.READ)
			if bfile:
				json_str = bfile.get_as_text()
				bfile.close()
				error = json.parse(json_str)
		if error != OK:
			push_error("Błąd parsowania JSON zapisu gry.")
			return false

	var data = json.get_data()
	if data is Dictionary:
		player.from_dict(data)
		current_save_filename = filename
		print("[SaveSystem] Zapis '%s' wczytany pomyślnie." % filename)
		return true

	return false

static func delete_save(filename: String) -> bool:
	init_saves_dir()
	if not filename.ends_with(".json"):
		filename += ".json"
	var save_path = SAVES_DIR.path_join(filename)
	var bak_path = save_path + ".bak"
	var deleted = false
	if FileAccess.file_exists(save_path):
		DirAccess.remove_absolute(save_path)
		deleted = true
	if FileAccess.file_exists(bak_path):
		DirAccess.remove_absolute(bak_path)
	if current_save_filename == filename:
		current_save_filename = ""
	print("[SaveSystem] Usunięto profil zapisu: %s" % filename)
	return deleted
