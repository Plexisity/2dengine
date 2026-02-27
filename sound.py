#play music loop for /assets/Music/music.mp3
import pygame

class SoundManager:
    """Manages sound effects and music playback for the game.
    """
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.5
        self.effects_volume = 0.5

    def load_sound(self, name: str, path: str):
        """Load a sound effect from the given file path."""
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.effects_volume)
            self.sounds[name] = sound
        except Exception as e:
            print(f"Error loading sound '{name}' from '{path}': {e}")

    def play_sound(self, name: str):
        """Play a loaded sound effect by name."""
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"Sound '{name}' not found!")

    def play_music(self, path: str, loop: bool = True):
        """Play background music from the given file path."""
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception as e:
            print(f"Error loading music from '{path}': {e}")

    def stop_music(self):
        """Stop the currently playing music."""
        pygame.mixer.music.stop()

    def set_music_volume(self, volume: float):
        """Set the music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def set_effects_volume(self, volume: float):
        """Set the sound effects volume (0.0 to 1.0)."""
        self.effects_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.effects_volume)