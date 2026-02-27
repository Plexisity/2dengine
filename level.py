import pygame
from utils import svg_to_surface
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Level:
    """Draws a full-screen SVG level and provides pixel-perfect collision detection."""

    def __init__(self, svg_path: str):
        # Convert SVG to full screen surface
        self.image = svg_to_surface(
            svg_path,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            scale_mode="fill"
        )
        
        # Create a mask for collision detection from the SVG surface.
        # Non-transparent pixels (alpha > 0) are considered solid.
        self.mask = pygame.mask.from_surface(self.image)
        # Cache a background image (if present) so we don't re-render SVG every frame.
        try:
            self.bg_image = svg_to_surface("assets/bg.svg", width=SCREEN_WIDTH, height=SCREEN_HEIGHT, scale_mode="fill")
        except Exception:
            self.bg_image = None

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, (0, 0))

    def get_collisions(self, rect: pygame.Rect) -> bool:
        """Check if the given rect overlaps any non-transparent pixels in the level."""
        if not rect.colliderect(self.image.get_rect()):
            return False
        
        # Get the intersection of the cube's rect and the level bounds
        level_rect = self.image.get_rect()
        intersection = rect.clip(level_rect)
        
        if intersection.width <= 0 or intersection.height <= 0:
            return False
        
        try:
            # Check if any pixel in the intersection is solid (non-transparent)
            for x in range(intersection.left, intersection.right):
                for y in range(intersection.top, intersection.bottom):
                    if 0 <= x < level_rect.width and 0 <= y < level_rect.height:
                        if self.mask.get_at((x, y)):
                            return True
        except (IndexError, ValueError):
            pass
        
        return False

    def resolve_collision(self, rect: pygame.Rect, velocity) -> tuple:
        """Resolve collision and return adjusted position and velocity.
        
        Returns (x, y, vel_y) after resolving collisions.
        """
        if not self.get_collisions(rect):
            return rect.x, rect.y, velocity
        
        # Simple resolution: push upward until no collision
        # (works for landing on platforms from above)
        x, y = rect.x, rect.y
        test_rect = pygame.Rect(x, y, rect.width, rect.height)
        
        # Try moving up pixel by pixel until clear
        for i in range(1, rect.height + 10):
            test_rect.y = y - i
            if not self.get_collisions(test_rect):
                return x, y - i, 0
        
        return x, y, velocity
    
    def draw_background(self, surface: pygame.Surface):
        """Draw just the background layer of the level /assets/bg.svg"""
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))