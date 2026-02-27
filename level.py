import pygame

from utils import svg_to_surface
from constants import SCREEN_WIDTH, GROUND_HEIGHT, GROUND_Y


class Level:
    """Simple container for level graphics and related data.

    Right now the only thing we draw is the ground constructed from an SVG.
    The class is responsible for loading the graphic, computing its draw
    position, and offering a helper for collision checks later.
    """

    def __init__(self, svg_path: str,
                 width: int = SCREEN_WIDTH,
                 height: int = GROUND_HEIGHT,
                 ground_y: int = GROUND_Y):
        # rasterise the svg once and keep surface
        self.ground_image = svg_to_surface(svg_path,
                                          width=width,
                                          height=height,
                                          scale_mode='fill')

        # ground is supposed to sit at `ground_y`; the SVG may be shorter than
        # the allotted height so we compute an actual screen y coordinate that
        # keeps the bottom of the graphic flush with the bottom of the region.
        self.ground_y = ground_y
        self.ground_height = height
        self._compute_positions()

    def _compute_positions(self):
        # when drawing, the image may be shorter than height if the SVG scaled
        # differently; align its bottom edge to ground_y + ground_height
        self.ground_y_pos = self.ground_y + self.ground_height - self.ground_image.get_height()

        # also build a pygame.Rect representing the ground region (useful for
        # basic collision later). the rect covers the entire area reserved for
        # ground, not just the visible pixels.
        self.ground_rect = pygame.Rect(0, self.ground_y, SCREEN_WIDTH, self.ground_height)

    def draw(self, surface: pygame.Surface):
        """Blit level graphics onto the provided surface."""
        surface.blit(self.ground_image, (0, self.ground_y_pos))

    # placeholder for future collision support
    def point_solid(self, x: int, y: int) -> bool:
        """Return True if the given screen coordinate lands on a non-transparent
        pixel of the ground image. Coordinates outside the image return False.
        """
        rel_x = x
        rel_y = y - self.ground_y_pos
        if rel_x < 0 or rel_x >= self.ground_image.get_width():
            return False
        if rel_y < 0 or rel_y >= self.ground_image.get_height():
            return False
        # use PixelArray for speed
        px = pygame.PixelArray(self.ground_image)
        alpha = (px[rel_x, rel_y] >> 24) & 0xFF
        del px
        return alpha != 0
