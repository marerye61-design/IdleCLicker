extends Node2D

@onready var label: Label = $Label

func setup(text: String, color: Color = Color.WHITE, is_crit: bool = false):
	if label == null:
		label = $Label
	label.text = text
	label.modulate = color

	if is_crit:
		label.add_theme_font_size_override("font_size", 28)
		scale = Vector2(1.4, 1.4)
	else:
		label.add_theme_font_size_override("font_size", 20)
		scale = Vector2(1.0, 1.0)

	var tween = create_tween().set_parallel(true)
	var target_pos = position + Vector2(randf_range(-30, 30), -70)
	tween.tween_property(self, "position", target_pos, 0.75).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "modulate:a", 0.0, 0.75).set_ease(Tween.EASE_IN)
	tween.chain().tween_callback(queue_free)
