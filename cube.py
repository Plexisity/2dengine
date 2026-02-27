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
        self.speed = 400
        self.jumping = False
        self.jump_speed = -900
        self.gravity = 2500
        self.wall_sliding = False
        self.wall_dir = 0
        self.wall_slide_gravity_scale = 0.22
        self.wall_slide_max_fall = 4.5
        self.wall_jump_h_mult = 1.7
        self.jump_key_held = False
        self.sprite = None
        self.trail = []
        self.max_trail_length = 20
        self.trail_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        #cache player sprite
        try:
            img = svg_to_surface("assets/player.svg", width=self.size, height=self.size, scale_mode="fit")
            self.sprite = img.convert_alpha()
        except Exception:            self.sprite = None

    def handle_input(self, keys, *args):
        """Handle keyboard input for cube movement"""
        self.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed

        # jump handling: detect initial press (not held)
        pressed = keys[pygame.K_SPACE] or keys[pygame.K_w]
        level = None
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

    def update(self, dt, level=None):
        """Update cube position with collisions, frame-rate independent."""
        
        # --- Horizontal movement ---
        self.x += self.velocity_x * dt
        if level and level.get_collisions(self.rect()):
            # Move back until not colliding
            if self.velocity_x > 0:
                while level.get_collisions(self.rect()):
                    self.x -= 1
            elif self.velocity_x < 0:
                while level.get_collisions(self.rect()):
                    self.x += 1
            self.velocity_x = 0

        # Keep cube within screen bounds
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.size))

        # --- Gravity / Vertical movement ---
        effective_gravity = self.gravity * (self.wall_slide_gravity_scale if self.wall_sliding else 1.0)
        self.velocity_y += effective_gravity * dt

        # Cap vertical speed if sliding
        if self.wall_sliding and self.velocity_y > self.wall_slide_max_fall:
            self.velocity_y = self.wall_slide_max_fall

        # Move vertically
        self.y += self.velocity_y * dt
        if level and level.get_collisions(self.rect()):
            # Move back until not colliding
            if self.velocity_y > 0:  # falling
                while level.get_collisions(self.rect()):
                    self.y -= 1
                self.jumping = False
            elif self.velocity_y < 0:  # jumping
                while level.get_collisions(self.rect()):
                    self.y += 1
            self.velocity_y = 0

        # Ground collision fallback
        if level is None and self.y + self.size >= GROUND_Y:
            self.y = GROUND_Y - self.size
            self.velocity_y = 0
            self.jumping = False

        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    def on_ground(self):
        """Return True if cube is standing on the ground"""
        return self.y + self.size >= GROUND_Y

    def rect(self) -> pygame.Rect:
        """Return bounding rect for collision checks."""
        return pygame.Rect(int(self.x), int(self.y), int(self.size), int(self.size))

    def draw(self, surface):
        # Draw trail
        trail_length = len(self.trail)
        for i, (tx, ty) in enumerate(self.trail):
            # newest = more opaque, oldest = transparent
            base_alpha = 0      # fully transparent at the tail
            max_alpha = 200     # most visible near the player
            # fade from tail -> head
            alpha = int(base_alpha + (max_alpha - base_alpha) * ((i + 1) / trail_length))

            if self.sprite:
                temp = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
                temp.blit(self.sprite, (0, 0))
                temp.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(temp, (int(tx), int(ty)))
            else:
                trail_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                trail_surf.fill((255, 255, 255, alpha))
                surface.blit(trail_surf, (int(tx), int(ty)))

        # Draw main cube on top
        if self.sprite:
            surface.blit(self.sprite, (int(self.x), int(self.y)))
        else:
            pygame.draw.rect(surface, WHITE, self.rect())
