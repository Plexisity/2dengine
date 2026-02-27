import pygame
from constants import GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT


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
        pygame.draw.rect(surface, pygame.Color('white'), (self.x, self.y, self.size, self.size))
