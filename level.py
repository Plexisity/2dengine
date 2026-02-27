import pygame
from utils import svg_to_surface
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Level:
    """Draws a full-screen SVG level background."""

    def __init__(self, svg_path: str):
        # Convert SVG to full screen surface
        self.image = svg_to_surface(
            svg_path,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            scale_mode="fill"
        )

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, (0, 0))