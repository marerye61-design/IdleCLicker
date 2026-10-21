# Forge Pixel-Art Dark Fantasy UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the flat and static Godot interface into a dynamic, "living" pixel-art dark fantasy interface inspired by forged iron, glowing embers, and anvil flames with springy hover micro-interactions across the entire game frame.

**Architecture:** Implement custom Godot 2D canvas shaders (`forge_ember.gdshader`) and ambient particle emitters for animated fire/embers in panel backgrounds; introduce an interactive micro-interaction utility (`ForgeUIEffects.gd`) providing spring physics and molten-glow tweens on hover/press; completely restyle and animate the Top HUD, Navigation Sidebar, and `StatsView` (Hero Altar & Talent Tree) using a cohesive forged metal aesthetic.

**Tech Stack:** Godot 4.3+, GDScript, CanvasItem Shaders (GLSL ES 3.0), CPUParticles2D, Tween animations, StyleBoxFlat & custom pixel-art borders.

**Spec:** User request: "Czarny lub brązowy kolor, w tle kafelków płomienie jak z kutego metalu na kowadle wraz z mikro-reakcjami na najechanie myszką na kafelki. Ma objąć całą ramę gry."

## Global Constraints
- Must preserve 100% of existing game logic, signals, and database bindings.
- All UI actions and button interactions must maintain keyboard/gamepad accessibility and pass all existing unit tests.
- Palette strictly adheres to Dark Fantasy Forged Metal: Obsidian/Charcoal `#121011`, Deep Forged Brown `#231814`, Iron Gray `#3a322d`, Molten Orange `#ff7700`, Radiant Gold `#f4d03f`.
- Rule 1 (Changelog Tracker) and Rule 2 (two-directory sync if applicable) must be observed.

## Review Focus
- Hovering quickly between multiple buttons must not accumulate stuck tweens or distorted scales.
- Shaders must run efficiently without causing GPU spikes or memory leaks.
- Progress bars (HP, Mana, Exp) must smoothly interpolate during combat and second ticks.
- Dynamic screen resizing must keep forged frames and ember particles aligned.
- Contrast between text and animated backgrounds must maintain WCAG AA readability (> 4.5:1).

---

### Task 1: Forge Ember Shader & Ambient Sparks Emitter

**Files:**
- Create: `C:/Users/Qonara/Documents/IdleClicker_Godot/shaders/forge_flame.gdshader`
- Create: `C:/Users/Qonara/Documents/IdleClicker_Godot/scenes/components/EmberSparks.tscn`
- Test: Headless Shader Compilation & Scene instantiation via `godot_console`

**Steps:**
- [x] Write `forge_flame.gdshader` generating procedural pixel-art embers and flame licks with parameters for intensity, flame color, and molten border glow.
- [x] Create `EmberSparks.tscn` using `CPUParticles2D` emitting tiny rising glowing orange/gold embers.
- [x] Verify shader compiles cleanly in Godot without warnings.

---

### Task 2: Interactive Spring Micro-Interactions System (`ForgeUIEffects.gd`)

**Files:**
- Create: `C:/Users/Qonara/Documents/IdleClicker_Godot/scripts/ui/ForgeUIEffects.gd`
- Test: Unit test for button registration and tween cleanup

**Steps:**
- [x] Implement `ForgeUIEffects.gd` with static helper methods:
  - `apply_button_effect(btn: Button, scale_boost: float = 1.04, glow_color: Color = Color("#ffaa00"))`
  - Connects `mouse_entered`, `mouse_exited`, `button_down`, and `button_up` with spring tweens (`TRANS_BACK`, `EASE_OUT`).
  - `apply_card_effect(panel: Control)` for interactive content cards.
- [x] Add sound triggers (`play_click()` / hammer click) on interaction where appropriate.
- [x] Test that mouse enter/exit cleans up existing tweens cleanly without drifting scales.

---

### Task 3: Top HUD Overhaul (Living Resource Bars & Forged Header)

**Files:**
- Modify: `C:/Users/Qonara/Documents/IdleClicker_Godot/scenes/Main.tscn`
- Modify: `C:/Users/Qonara/Documents/IdleClicker_Godot/scenes/Main.gd`

**Steps:**
- [x] Restyle `TopHUD` in `Main.tscn`: dark iron forged header with molten gold border.
- [x] Upgrade HP, Mana, and Exp bars with custom StyleBoxes:
  - HP: Molten ruby gradient with glowing border.
  - Mana: Arcane sapphire/amethyst gradient.
  - Exp: Molten gold line with animated fill tween.
- [x] Update `Main.gd` to animate bar updates using smooth tweens instead of instant value snapping.
- [x] Add `ForgeUIEffects` to `BtnHeroClick` with an anvil spark effect on click.

---

### Task 4: Navigation Sidebar Overhaul (Forged Anvil Plates)

**Files:**
- Modify: `C:/Users/Qonara/Documents/IdleClicker_Godot/scenes/Main.tscn`
- Modify: `C:/Users/Qonara/Documents/IdleClicker_Godot/scenes/Main.gd`

**Steps:**
- [x] Restyle `NavSidebar` and all navigation buttons in `Main.tscn` with forged dark iron textures, rivet accents, and molten border highlights.
- [x] In `Main.gd`, register all navigation buttons with `ForgeUIEffects.apply_button_effect()`.
- [x] Add an active indicator: selected navigation tab glows with continuous fiery amber border and subtle breathing pulse.
- [x] Attach `EmberSparks.tscn` in the background of `MainBody` for subtle floating sparks.

---

### Task 5: StatsView Overhaul (Ołtarz Bohaterów & Drzewko Talentów)

**Files:**
- Modify: `C:/Users/Qonara/Documents/IdleClicker_Godot/scenes/views/StatsView.tscn`
- Modify: `C:/Users/Qonara/Documents/IdleClicker_Godot/scenes/views/StatsView.gd`

**Steps:**
- [x] Redesign `StatsView.tscn` layout:
  - Left panel: Forged Hero Altar with framed portrait, level badge, and stat cards (ATK, DEF, CRIT, DOUBLE, HP, GPS) with dark brown stone backgrounds and glowing values.
  - Runic `+1` and `+5` stat investment buttons styled as molten runes.
  - Right panel: Talent Tree with heavy forged steel plates for each path (Berserker, Obrońca, Awanturnik) and glowing rune progress indicators.
- [x] In `StatsView.gd`, bind `ForgeUIEffects` to all stat and talent buttons.
- [x] Add punchy feedback tweens when allocating stat points or talent runes.

---

### Task 6: Verification, TestRunner & Live Visual Verification

**Files:**
- Test: `C:/Users/Qonara/Documents/IdleClicker_Godot/test/TestRunner.gd`
- Test: `C:/Users/Qonara/Documents/IdleClicker_Godot/test/AutomatedLiveTester.tscn`
- Modify: `C:/Users/Qonara/Documents/IdleClicker/CHANGELOG_DRAFT.md`

**Steps:**
- [x] Run headless test suite `TestRunner.gd` to verify 100% test pass.
- [x] Launch `odpal_test_na_zywo.bat` or interactive test runner to verify smooth visual motion, flame shader, and springy hover reactions.
- [x] Record changes in `CHANGELOG_DRAFT.md` and sync with `IdleClicker_CustomTkinter`.
