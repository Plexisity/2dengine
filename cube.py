import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y


class Cube:
    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        # jump physics
        self.jumping = False
        self.jump_speed = -15.0
        self.gravity = 0.5

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

    def update(self, level=None):
        """Update cube position with collision resolution against the level."""
        # horizontal movement
        self.x += self.velocity_x

        # Keep cube within horizontal bounds
        if self.x < 0:
            self.x = 0
        if self.x + self.size > 1920:  # SCREEN_WIDTH before scaling
            self.x = 1920 - self.size

        # apply gravity and vertical movement
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # collision resolution with level
        if level:
            # Check for collision and resolve if needed
            if level.get_collisions(self.rect()):
                # Resolve by pushing up and stopping vertical velocity
                _, new_y, _ = level.resolve_collision(self.rect(), self.velocity_y)
                self.y = new_y
                self.velocity_y = 0
                self.jumping = False
        else:
            # Fallback: simple ground collision
            if self.y + self.size >= 1000:  # GROUND_Y
                self.y = 1000 - self.size
                self.velocity_y = 0
                self.jumping = False

    def on_ground(self):
        """Return True if cube is standing on the ground"""
        return self.y + self.size >= GROUND_Y

    def rect(self) -> pygame.Rect:
        """Return bounding rect for collision checks."""
        return pygame.Rect(int(self.x), int(self.y), int(self.size), int(self.size))

    def draw(self, surface):
        """Draw the cube"""
        pygame.draw.rect(surface, pygame.Color('white'), (self.x, self.y, self.size, self.size))
