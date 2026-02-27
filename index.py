# main entry point, pulls together components
import pygame
import sys
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
from cube import Cube
from level import Level

# initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Engine")
clock = pygame.time.Clock()

# (cube implementation now lives in cube.py)
# create game objects
cube = Cube(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT // 2 - 25)
# level handles loading/drawing the background/ground
level = Level("assets/Level1.svg")

# Main game loop
running = True
while running:
    clock.tick(FPS)
    
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
    level.draw(screen)
    cube.draw(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()
sys.exit()