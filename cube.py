import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y, WHITE
from utils import svg_to_surface

class Cube:
    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 7.5
        self.jumping = False
        self.jump_speed = -17.5
        self.gravity = 0.7
        self.wall_sliding = False
        self.wall_dir = 0
        self.wall_slide_gravity_scale = 0.22
        self.wall_slide_max_fall = 4.5
        self.wall_jump_h_mult = 1.7
        self.jump_key_held = False
        self.sprite = None
        #cache player sprite
        try:
            img = svg_to_surface("assets/player.svg", width=self.size, height=self.size, scale_mode="fit")
            self.sprite = img.convert_alpha()
        except Exception:            self.sprite = None

    def handle_input(self, keys, *args):
        """Handle keyboard input for cube movement"""
        self.velocity_x = 0
        # do not touch self.velocity_y; let physics handle vertical motion
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed

        # jump handling: detect initial press (not held)
        pressed = keys[pygame.K_SPACE] or keys[pygame.K_w]
        # Note: handle_input may optionally receive a level to allow wall detection
        level = None
        # Try to get level from extra arg if provided (backwards-compatible)
        try:
            # callers may pass (keys, level)
            level = args[0]
        except Exception:
            pass

        touching_left = False
        touching_right = False
        if level:
            rect = self.rect()
            touching_left = level.get_collisions(rect.move(-1, 0))
            touching_right = level.get_collisions(rect.move(1, 0))

        # Determine if we are sliding on a wall: in-air, touching a wall and falling
        self.wall_sliding = (not self.on_ground()) and (touching_left or touching_right) and self.velocity_y > 0
        if touching_left:
            self.wall_dir = -1
        elif touching_right:
            self.wall_dir = 1
        else:
            self.wall_dir = 0


        if level:
            rect = self.rect()
            touching_ground = level.get_collisions(rect.move(0, 1))
            touching_wall = touching_left or touching_right
            can_jump = touching_ground or (touching_wall and not touching_ground)
        else:
            can_jump = self.on_ground()

        if pressed and not self.jump_key_held and can_jump:
            self.jumping = True
            self.velocity_y = self.jump_speed
            if not self.on_ground():
                if touching_left:
                    self.velocity_x = self.speed * self.wall_jump_h_mult
                elif touching_right:
                    self.velocity_x = -self.speed * self.wall_jump_h_mult

        self.jump_key_held = pressed

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity_y = self.speed

    def update(self, level=None):
        """Update cube position with collision resolution against the level.

        This resolves horizontal movement first (checking per-pixel steps),
        then vertical movement similarly. Works when `level` provides
        pixel-perfect collisions via `get_collisions(rect)`.
        """

        target_x = self.x + self.velocity_x
        if level:
            delta_x = target_x - self.x
            steps = int(abs(int(round(delta_x))))
            step_dir = 1 if delta_x > 0 else -1
            for _ in range(steps):
                self.x += step_dir
                if level.get_collisions(self.rect()):
                    self.x -= step_dir
                    self.velocity_x = 0
                    break
        else:
            self.x = target_x

        # Keep cube within horizontal bounds
        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
        if self.x + self.size > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.size
            self.velocity_x = 0

        # apply gravity (reduced while sliding on a wall)
        effective_gravity = self.gravity * (self.wall_slide_gravity_scale if self.wall_sliding else 1.0)
        self.velocity_y += effective_gravity

        # while sliding on a wall, cap downward speed to allow climbing timing
        if self.wall_sliding and self.velocity_y > self.wall_slide_max_fall:
            self.velocity_y = self.wall_slide_max_fall

        # Vertical movement with per-pixel collision resolution
        target_y = self.y + self.velocity_y
        if level:
            delta_y = target_y - self.y
            steps = int(abs(int(round(delta_y))))
            step_dir = 1 if delta_y > 0 else -1
            for _ in range(steps):
                self.y += step_dir
                if level.get_collisions(self.rect()):
                    # step back and stop vertical velocity
                    self.y -= step_dir
                    self.velocity_y = 0
                    self.jumping = False
                    break
        else:
            self.y = target_y

        # fallback ground collision if no level provided
        if level is None and self.y + self.size >= GROUND_Y:
            self.y = GROUND_Y - self.size
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
        if self.sprite:
            surface.blit(self.sprite, (int(self.x), int(self.y)))
        else:
            pygame.draw.rect(surface, WHITE, self.rect())
