# main entry point, pulls together components
import pygame
import sys
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, RED
from cube import Cube
from level import Level

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


# initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flip It! 4 - 2D Platformer Demo")
clock = pygame.time.Clock()
font = None
font_is_freetype = False

# (cube implementation now lives in cube.py)
# create game objects
cube = Cube(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT // 2 - 25)
# level handles loading/drawing the background/ground
level = Level("assets/Level1.svg")

# Main game loop
running = True
while running:
    dt = clock.tick(FPS)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Get pressed keys
    keys = pygame.key.get_pressed()
    
    # Update (pass level so cube can check wall contact for wall-jump)
    cube.handle_input(keys, level)
    cube.update(level)
    
    # Draw
    screen.fill(BLACK)
    if draw_background == True:
        level.draw_background(screen)
    level.draw(screen)
    cube.draw(screen)
    # FPS counter (top-left, red) with background so it draws over the level
    # Draw a small contrasting background box for readability (always drawn)
    hud_bg_rect = (6, 6, 45, 30)
    hud_bg_color = (30, 30, 30)
    pygame.draw.rect(screen, hud_bg_color, hud_bg_rect)
    # now render FPS text on top
    # We only support rendering FPS if pygame.freetype was available at startup.
    # Avoid calling pygame.font.* at runtime to prevent circular-import warnings.

    fps = int(1000 / max(1, dt))
    rendered = False
    if font is not None and font_is_freetype:
        # Render with explicit background so surface is opaque and visible
        fps_surf, _ = font.render(f"FPS: {fps}", RED, hud_bg_color)
        screen.blit(fps_surf, (10, 8))
        rendered = True
    else:
        # Try a safe SysFont fallback (may be unavailable on some installs)
        try:
            if hasattr(pygame, 'font'):
                sf = pygame.font.SysFont(None, 24)
                fps_surf = sf.render(f"FPS: {fps}", True, RED, hud_bg_color)
                screen.blit(fps_surf, (10, 8))
                rendered = True
        except Exception:
            rendered = False

    if not rendered:
        # Ultimate fallback: draw digits manually so user always sees numbers
        _draw_small_number(screen, str(max(0, int(fps))), (14, 8), scale=4, color=RED)

    # Update display
    pygame.display.flip()

pygame.quit()
sys.exit()