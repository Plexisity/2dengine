# main entry point, pulls together components
import pygame
import sys
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, RED
from cube import Cube
from level import Level
from sound import SoundManager
from text import IntroText
from utils import svg_to_surface
from menu import LevelMenu

draw_background = True

def _draw_small_number(surface, text, pos, scale=4, color=(255, 0, 0)):
    """Draw a small 3x5-pixel font for digits as a fallback when no font is available."""
    patterns = {
        "0": ["111","101","101","101","111"],
        "1": ["010","110","010","010","111"],
        "2": ["111","001","111","100","111"],
        "3": ["111","001","111","001","111"],
        "4": ["101","101","111","001","001"],
        "5": ["111","100","111","001","111"],
        "6": ["111","100","111","101","111"],
        "7": ["111","001","010","010","010"],
        "8": ["111","101","111","101","111"],
        "9": ["111","101","111","001","111"],
    }
    x0, y0 = pos
    spacing = scale + 1
    for i, ch in enumerate(text):
        pattern = patterns.get(ch, patterns.get("0"))
        x_offset = i * (3 * scale + spacing) 
        for ry, row in enumerate(pattern):
            for rx, c in enumerate(row):
                if c == "1":
                    rect = (x0 + x_offset + rx * scale, y0 + ry * scale, scale, scale)
                    pygame.draw.rect(surface, color, rect)

def load_level(level_number):
    global level, current_level

    current_level = level_number
    level = Level(f"assets/Levels/Level{level_number}.svg")

    cube.teleport(100, 0)
    cube.velocity_x = 0
    cube.velocity_y = 0


# initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flip It! 4 - 2D Platformer Demo")
clock = pygame.time.Clock()
font = None
font_is_freetype = False
cube = Cube(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT // 2 - 25)
current_level = None
sound_manager = SoundManager()
sound_manager.play_music("assets/Music/music.mp3", loop=True)
sound_manager.set_music_volume(0.1)
# wait until level is set by menu before loading

intro = IntroText("assets/Text/Text.svg")
menu = LevelMenu()
cube.teleport(100, 0)

# Main game loop
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    dtfps = dt * 1000.0

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        selected_level = menu.handle_event(event)

        if selected_level is not None:
            current_level = selected_level
            level = Level(f"assets/Levels/Level{current_level}.svg")
            menu.visible = False
            cube.teleport(100, 0)

    keys = pygame.key.get_pressed()


    if current_level is not None:
        cube.handle_input(keys, level)
        result = cube.update(dt, level)

        if result:
            load_level(current_level + 1)

        if draw_background:
            level.draw_background(screen)

        level.draw_spikes(screen, current_level)      
        level.draw(screen)
        cube.draw(screen)
        intro.update(dt)
        intro.draw(screen)

    menu.draw(screen)

    fps = int(1000 / max(1, dtfps))
    _draw_small_number(screen, str(max(0, int(fps))), (14, 8), scale=4, color=RED)



    pygame.display.flip()

pygame.quit()
sys.exit()
