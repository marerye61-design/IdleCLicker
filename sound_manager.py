import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class SoundManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def __init__(self):
        self.enabled = True
        self.volume = 0.7
        self.sounds = {}
        self.initialized = False
        self._init_mixer()

    def _init_mixer(self):
        try:
            import pygame
            # Sprawdzenie czy mikser nie był już wcześniej zainicjalizowany
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.initialized = True
            self._load_sounds()
        except Exception as e:
            print("[SoundManager] Nie udało się zainicjalizować audio (tryb cichy):", e)
            self.initialized = False

    def _load_sounds(self):
        if not self.initialized:
            return
        try:
            import pygame
            sound_dir = resource_path(os.path.join("assets", "sounds"))
            if not os.path.exists(sound_dir):
                return

            sound_files = {
                "coin": ("coin.wav", 0.6),
                "sword": ("sword_swing.wav", 0.7),
                "hit": ("hit.wav", 0.8),
                "crit": ("crit_hit.wav", 1.0),
                "enemy_hit": ("enemy_hit.wav", 0.75),
                "level_up": ("level_up.wav", 0.85),
                "potion": ("potion.wav", 0.7),
                "ui_click": ("ui_click.wav", 0.4),
                "boss_intro": ("boss_intro.wav", 0.9),
                "quest_accept": ("quest_accept.wav", 0.75),
                "quest_complete": ("quest_complete.wav", 0.85),
                "dungeon_enter": ("dungeon_enter.wav", 0.7)
            }

            for key, (filename, vol) in sound_files.items():
                p = os.path.join(sound_dir, filename)
                if os.path.exists(p):
                    snd = pygame.mixer.Sound(p)
                    snd.set_volume(vol * self.volume)
                    self.sounds[key] = (snd, vol)
        except Exception as e:
            print("[SoundManager] Błąd ładowania plików dźwiękowych:", e)

    def play(self, sound_key):
        if not self.enabled or not self.initialized:
            return
        if sound_key in self.sounds:
            try:
                snd, _ = self.sounds[sound_key]
                snd.play()
            except Exception:
                pass

    def toggle_sound(self):
        self.enabled = not self.enabled
        return self.enabled

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        for key, (snd, base_vol) in self.sounds.items():
            snd.set_volume(base_vol * self.volume)

    # Wygodne skróty dla kodu gry
    def play_coin(self): self.play("coin")
    def play_sword(self): self.play("sword")
    def play_hit(self): self.play("hit")
    def play_crit(self): self.play("crit")
    def play_enemy_hit(self): self.play("enemy_hit")
    def play_level_up(self): self.play("level_up")
    def play_potion(self): self.play("potion")
    def play_heal(self): self.play("potion")
    def play_ui_click(self): self.play("ui_click")
    def play_boss_intro(self): self.play("boss_intro")
    def play_quest_accept(self): self.play("quest_accept")
    def play_quest_complete(self): self.play("quest_complete")
    def play_dungeon_enter(self): self.play("dungeon_enter")

# Globalny singleton
sounds = SoundManager.get_instance()
