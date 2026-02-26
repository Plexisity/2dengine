# Main processor for drawing on the screen
import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Create display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Engine")
clock = pygame.time.Clock()

# Cube class
class Cube:
    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
    
    def handle_input(self, keys):
        """Handle keyboard input for cube movement"""
        self.velocity_x = 0
        self.velocity_y = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity_y = self.speed
    
    def update(self):
        """Update cube position"""
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Keep cube within bounds
        if self.x < 0:
            self.x = 0
        if self.x + self.size > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.size
        if self.y < 0:
            self.y = 0
        if self.y + self.size > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.size
    
    def draw(self, surface):
        """Draw the cube"""
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(surface, WHITE, (self.x, self.y + self.size, self.size, 5))  # Ground plane

# Create cube
cube = Cube(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT // 2 - 25)

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
    
    # Update
    cube.handle_input(keys)
    cube.update()
    
    # Draw
    screen.fill(BLACK)
    cube.draw(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()
sys.exit()