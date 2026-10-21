shader_type canvas_item;
render_mode blend_mix;

// Kolorystyka kutego żelaza i żaru kowadła
uniform vec4 base_dark_color : source_color = vec4(0.08, 0.06, 0.07, 0.94);
uniform vec4 ember_color_core : source_color = vec4(1.0, 0.58, 0.08, 1.0);
uniform vec4 ember_color_edge : source_color = vec4(0.55, 0.12, 0.04, 0.85);
uniform vec4 border_molten_color : source_color = vec4(1.0, 0.45, 0.05, 1.0);

uniform float flame_intensity : hint_range(0.0, 2.5) = 0.5;
uniform float flame_speed : hint_range(0.1, 4.0) = 1.3;
uniform float border_glow : hint_range(0.0, 2.0) = 0.35;
uniform float pixel_density : hint_range(16.0, 256.0) = 64.0;

// Prosty proceduralny szum pseudo-losowy
float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
	           mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

void fragment() {
	// Pikselizacja koordynatów dla stylu Pixel Art
	vec2 pix_uv = floor(UV * pixel_density) / pixel_density;

	// Obliczanie odległości od krawędzi (efekt kutej ramki)
	float edge_dist_x = min(UV.x, 1.0 - UV.x);
	float edge_dist_y = min(UV.y, 1.0 - UV.y);
	float edge_dist = min(edge_dist_x, edge_dist_y);
	float is_border = step(edge_dist, 0.035);

	// Falujący płomień z dołu kafelka
	float t = TIME * flame_speed;
	float n1 = noise(pix_uv * vec2(4.0, 6.0) + vec2(0.0, -t * 1.5));
	float n2 = noise(pix_uv * vec2(8.0, 12.0) + vec2(t * 0.4, -t * 2.2));
	float flame_noise = (n1 * 0.65 + n2 * 0.35);

	// Gradacja ognia od dołu ku górze
	float vertical_gradient = pow(1.0 - pix_uv.y, 1.8);
	float flame_val = vertical_gradient * flame_noise * flame_intensity;

	// Mieszanie kolorów żaru
	vec4 fire_col = mix(ember_color_edge, ember_color_core, clamp(flame_val * 1.6, 0.0, 1.0));
	vec4 final_color = mix(base_dark_color, fire_col, clamp(flame_val, 0.0, 0.85));

	// Rozżarzona krawędź kutej stali
	if (is_border > 0.5) {
		float border_flicker = 0.85 + 0.15 * sin(t * 4.0 + pix_uv.x * 20.0);
		vec4 current_border = border_molten_color * (border_glow * border_flicker);
		final_color = mix(final_color, current_border, clamp(border_glow * 1.2, 0.0, 0.95));
	}

	COLOR = final_color;
}
