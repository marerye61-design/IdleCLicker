extends SceneTree

func _init():
	var screen_count = DisplayServer.get_screen_count()
	print("Screens count: ", screen_count)
	for i in range(screen_count):
		print("Screen ", i, " usable rect: ", DisplayServer.screen_get_usable_rect(i))
	
	print("Initial window screen: ", DisplayServer.window_get_current_screen(), " pos: ", DisplayServer.window_get_position())
	
	DisplayServer.window_set_current_screen(1)
	print("After set_current_screen(1), screen: ", DisplayServer.window_get_current_screen(), " pos: ", DisplayServer.window_get_position())
	
	var r = DisplayServer.screen_get_usable_rect(1)
	var pos = r.position + (r.size - Vector2i(1280, 720)) / 2
	DisplayServer.window_set_position(pos)
	print("After set_position(", pos, "), pos is: ", DisplayServer.window_get_position())
	
	quit(0)
