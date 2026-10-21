class_name ForgeUIEffects
extends RefCounted

const ForgeFlameShader = preload("res://shaders/forge_flame.gdshader")

static func create_forge_material(intensity: float = 0.5, border_glow: float = 0.35) -> ShaderMaterial:
	var mat = ShaderMaterial.new()
	mat.shader = ForgeFlameShader
	mat.set_shader_parameter("flame_intensity", intensity)
	mat.set_shader_parameter("border_glow", border_glow)
	return mat

static func apply_button_effect(btn: Button, scale_boost: float = 1.04, glow_color: Color = Color(1.0, 0.85, 0.4)):
	if btn == null or not is_instance_valid(btn):
		return

	# Wycentruj pivot, aby skalowanie odbywało się z punktu środkowego
	btn.resized.connect(func():
		btn.pivot_offset = btn.size * 0.5
	)
	btn.pivot_offset = btn.size * 0.5

	# Zmienna do przechowywania aktywnego tweena
	var active_tween: Tween = null

	btn.mouse_entered.connect(func():
		if btn.disabled: return
		if active_tween and active_tween.is_valid():
			active_tween.kill()

		active_tween = btn.create_tween().set_parallel(true)
		active_tween.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		active_tween.tween_property(btn, "scale", Vector2(scale_boost, scale_boost), 0.16)
		active_tween.tween_property(btn, "modulate", glow_color, 0.16)

		# Jeśli przycisk posiada materiał płomieni, zwiększ płomień
		if btn.material is ShaderMaterial:
			active_tween.tween_property(btn.material, "shader_parameter/flame_intensity", 1.25, 0.2)
			active_tween.tween_property(btn.material, "shader_parameter/border_glow", 0.95, 0.2)
	)

	btn.mouse_exited.connect(func():
		if active_tween and active_tween.is_valid():
			active_tween.kill()

		active_tween = btn.create_tween().set_parallel(true)
		active_tween.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		active_tween.tween_property(btn, "scale", Vector2(1.0, 1.0), 0.18)
		active_tween.tween_property(btn, "modulate", Color.WHITE, 0.18)

		if btn.material is ShaderMaterial:
			active_tween.tween_property(btn.material, "shader_parameter/flame_intensity", 0.5, 0.25)
			active_tween.tween_property(btn.material, "shader_parameter/border_glow", 0.35, 0.25)
	)

	btn.button_down.connect(func():
		if btn.disabled: return
		var down_tween = btn.create_tween()
		down_tween.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		down_tween.tween_property(btn, "scale", Vector2(0.96, 0.96), 0.08)
	)

	btn.button_up.connect(func():
		if btn.disabled: return
		var up_tween = btn.create_tween()
		up_tween.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		up_tween.tween_property(btn, "scale", Vector2(scale_boost, scale_boost), 0.12)
	)

static func apply_card_effect(panel: Control, scale_boost: float = 1.02, glow_color: Color = Color(1.08, 1.05, 0.98)):
	if panel == null or not is_instance_valid(panel):
		return

	panel.resized.connect(func():
		panel.pivot_offset = panel.size * 0.5
	)
	panel.pivot_offset = panel.size * 0.5

	# Znajdź materiał ognia jeśli istnieje (na panelu lub w tle FlameBg)
	var flame_mat: ShaderMaterial = null
	if panel.material is ShaderMaterial:
		flame_mat = panel.material
	elif panel.has_node("FlameBg") and panel.get_node("FlameBg").material is ShaderMaterial:
		flame_mat = panel.get_node("FlameBg").material
	else:
		for c in panel.get_children():
			if c is CanvasItem and c.material is ShaderMaterial:
				flame_mat = c.material
				break

	var active_tween: Tween = null

	panel.mouse_entered.connect(func():
		if active_tween and active_tween.is_valid():
			active_tween.kill()

		active_tween = panel.create_tween().set_parallel(true)
		active_tween.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		active_tween.tween_property(panel, "scale", Vector2(scale_boost, scale_boost), 0.18)
		active_tween.tween_property(panel, "modulate", glow_color, 0.18)

		if flame_mat:
			active_tween.tween_property(flame_mat, "shader_parameter/flame_intensity", 0.95, 0.25)
			active_tween.tween_property(flame_mat, "shader_parameter/border_glow", 0.8, 0.25)
	)

	panel.mouse_exited.connect(func():
		if active_tween and active_tween.is_valid():
			active_tween.kill()

		active_tween = panel.create_tween().set_parallel(true)
		active_tween.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		active_tween.tween_property(panel, "scale", Vector2(1.0, 1.0), 0.2)
		active_tween.tween_property(panel, "modulate", Color.WHITE, 0.2)

		if flame_mat:
			active_tween.tween_property(flame_mat, "shader_parameter/flame_intensity", 0.4, 0.25)
			active_tween.tween_property(flame_mat, "shader_parameter/border_glow", 0.35, 0.25)
	)

static func register_interactive_controls(root: Node):
	if root == null or not is_instance_valid(root):
		return

	for child in root.get_children():
		if child is Button:
			apply_button_effect(child)
		elif child is PanelContainer and (child.name.ends_with("Card") or child.has_meta("interactive_card")):
			if not child.name.begins_with("Detail") and not child.has_meta("static_panel") and not child.name.contains("Panel"):
				apply_card_effect(child)
		register_interactive_controls(child)

static func pulse_node(node: Control, peak_scale: float = 1.12):
	if node == null or not is_instance_valid(node):
		return
	node.pivot_offset = node.size * 0.5
	var tween = node.create_tween()
	tween.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(node, "scale", Vector2(peak_scale, peak_scale), 0.12)
	tween.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_property(node, "scale", Vector2(1.0, 1.0), 0.16)

static func animate_bar_value(bar: ProgressBar, target_val: float, duration: float = 0.35):
	if bar == null or not is_instance_valid(bar):
		return
	var tween = bar.create_tween()
	tween.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(bar, "value", target_val, duration)
