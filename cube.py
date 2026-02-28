import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y, WHITE
import sound
from utils import svg_to_surface
from sound import SoundManager
soundmgr = SoundManager()
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
        self.gravity = 3000
        self.wall_sliding = False
        self.wall_dir = 0
        self.wall_slide_gravity_scale = 0.5
        self.wall_slide_max_fall = 40.5
        self.wall_jump_h_mult = 1.7
        self.jump_key_held = False
        self.sprite = None
        self.trail = []
        self.max_trail_length = 20
        self.trail_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self._trail_sprite_cache = []
        self._trail_rect_cache = []
        self._trail_cache_key = None

        #cache player sprite
        try:
            img = svg_to_surface("assets/player.svg", width=self.size, height=self.size, scale_mode="fit")
            self.sprite = img.convert_alpha()
        except Exception:            self.sprite = None
        self._rebuild_trail_cache()
    
    def teleport(self, new_x, new_y):
        """Instantly move player to a specific position"""
        self.x = new_x
        self.y = new_y

    def _rebuild_trail_cache(self):
        """Rebuild cached alpha variants used by the trail renderer."""
        cache_key = (self.max_trail_length, self.size, self.sprite is not None)
        if cache_key == self._trail_cache_key:
            return

        self._trail_cache_key = cache_key
        self._trail_sprite_cache = []
        self._trail_rect_cache = []

        max_alpha = 200
        if self.max_trail_length <= 0:
            return

        for i in range(self.max_trail_length):
            alpha = int(max_alpha * ((i + 1) / self.max_trail_length))
            if self.sprite:
                temp = self.sprite.copy()
                temp.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                self._trail_sprite_cache.append(temp)
            else:
                temp = self.trail_surface.copy()
                temp.fill((255, 255, 255))
                temp.set_alpha(alpha)
                self._trail_rect_cache.append(temp)

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

        # Spike collision
        if level and level.touching_spikes(self.rect()):
            soundmgr.death_sound()
            self.teleport(0, 500)
            self.velocity_x = 0
            self.velocity_y = 0

        def _resolve_axis(delta, axis):
            if delta == 0:
                return False

            blocked = False
            start = self.x if axis == "x" else self.y
            direction = 1 if delta > 0 else -1
            steps = abs(int(delta))

            # Move in bounded whole-pixel steps and stop at first contact.
            for _ in range(steps):
                candidate = start + direction
                if axis == "x":
                    self.x = candidate
                else:
                    self.y = candidate

                if level and level.get_collisions(self.rect()):
                    if axis == "x":
                        self.x = start
                    else:
                        self.y = start
                    blocked = True
                    break

                start = candidate

            if blocked:
                return True

            # Resolve the remaining fractional movement with a bounded binary search.
            end = (self.x if axis == "x" else self.y) + (delta - (direction * steps))
            low = self.x if axis == "x" else self.y
            high = end

            for _ in range(12):
                if abs(high - low) <= 0.001:
                    break
                mid = (low + high) * 0.5
                if axis == "x":
                    self.x = mid
                else:
                    self.y = mid

                if level and level.get_collisions(self.rect()):
                    high = mid
                    blocked = True
                else:
                    low = mid

            if axis == "x":
                self.x = low
            else:
                self.y = low

            return blocked

        # --- Horizontal movement ---
        dx = self.velocity_x * dt
        x_blocked = _resolve_axis(dx, "x")

        # Keep cube within screen bounds
        clamped_x = max(0, min(self.x, SCREEN_WIDTH - self.size))
        if clamped_x != self.x:
            x_blocked = True
            self.x = clamped_x

        if x_blocked:
            self.velocity_x = 0

        # --- Gravity / Vertical movement ---
        effective_gravity = self.gravity * (self.wall_slide_gravity_scale if self.wall_sliding else 1.0)
        self.velocity_y += effective_gravity * dt

        # Cap vertical speed if sliding
        if self.wall_sliding and self.velocity_y > self.wall_slide_max_fall:
            self.velocity_y = self.wall_slide_max_fall

        # Move vertically
        dy = self.velocity_y * dt
        was_falling = self.velocity_y > 0
        y_blocked = _resolve_axis(dy, "y")
        if y_blocked:
            if was_falling:
                self.jumping = False
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

        # Kill player if they fall below the screen
        if self.y > SCREEN_HEIGHT:
            soundmgr.death_sound()
            self.teleport(0, 500)
        
        #signal next level if player reaches right edge of screen
        if self.x + self.size >= SCREEN_WIDTH:
            return True

    def on_ground(self):
        """Return True if cube is standing on the ground"""
        return self.y + self.size >= GROUND_Y

    def rect(self) -> pygame.Rect:
        """Return bounding rect for collision checks."""
        return pygame.Rect(int(self.x), int(self.y), int(self.size), int(self.size))

    def draw(self, surface):
        self._rebuild_trail_cache()

        # Draw trail
        trail_length = len(self.trail)
        if trail_length == 0:
            trail_length = 1

        for i, (tx, ty) in enumerate(self.trail):
            # newest = more opaque, oldest = transparent
            cache_index = int((i + 1) * self.max_trail_length / trail_length) - 1
            cache_index = max(0, min(cache_index, self.max_trail_length - 1))

            if self.sprite:
                surface.blit(self._trail_sprite_cache[cache_index], (int(tx), int(ty)))
            else:
                surface.blit(self._trail_rect_cache[cache_index], (int(tx), int(ty)))

        # Draw main cube on top
        if self.sprite:
            surface.blit(self.sprite, (int(self.x), int(self.y)))
        else:
            pygame.draw.rect(surface, WHITE, self.rect())
