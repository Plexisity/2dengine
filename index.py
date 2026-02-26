# Main processor for drawing on the screen
import pygame
import sys
import io
import cairosvg

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

#Ground level
GROUND_Y = 500
GROUND_HEIGHT = 100


# utility --------------------------------------------------
def svg_to_surface(svg_path, width=None, height=None):
    """Render an SVG file to a Pygame Surface.

    The SVG is rasterised to PNG in memory using CairoSVG and loaded
    via a BytesIO buffer.  Width/height may be specified to scale the
    output; if omitted the SVG's intrinsic size is used.
    """
    png_bytes = cairosvg.svg2png(url=svg_path,
                                output_width=width,
                                output_height=height)
    return pygame.image.load(io.BytesIO(png_bytes)).convert_alpha()


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
        # jump physics
        # we only need an instantaneous upward impulse and constant gravity
        self.jumping = False
        # initial jump impulse (negative = upwards)
        self.jump_speed = -15.0               # much stronger jump
        # gravity acceleration per frame
        self.gravity = 0.5                    # pull back down
    
    def handle_input(self, keys):
        """Handle keyboard input for cube movement"""
        self.velocity_x = 0
        # do not touch self.velocity_y; let physics handle vertical motion

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed

        # begin jump with a strong upward impulse if on the ground
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground():
            self.jumping = True
            self.velocity_y = self.jump_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            # simple manual down control (could be removed)
            self.velocity_y = self.speed
    
    def update(self):
        """Update cube position"""
        # horizontal movement
        self.x += self.velocity_x

        # we don't need a timer – the jump is a single impulse and gravity handles the rest

        # always apply gravity so the cube falls after jumping or walking off an edge
        self.velocity_y += self.gravity

        # vertical movement (only once)
        self.y += self.velocity_y

        # Keep cube within horizontal bounds
        if self.x < 0:
            self.x = 0
        if self.x + self.size > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.size

        # ground collision
        if self.y + self.size >= GROUND_Y:
            self.y = GROUND_Y - self.size
            self.velocity_y = 0
            self.jumping = False

    def on_ground(self):
        """Return True if cube is standing on the ground"""
        return self.y + self.size >= GROUND_Y
    
    def draw(self, surface):
        """Draw the cube"""
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.size, self.size))

# Create cube
cube = Cube(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT // 2 - 25)

# load ground sprite (make sure assets/ground.svg exists)
ground_image = svg_to_surface("assets/grass.svg",
                              width=SCREEN_WIDTH,
                              height=GROUND_HEIGHT)

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
    # draw ground sprite at its y‑position
    screen.blit(ground_image, (0, GROUND_Y))
    cube.draw(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()
sys.exit()