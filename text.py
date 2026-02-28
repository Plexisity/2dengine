import pygame
from utils import svg_to_surface
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class IntroText:
    def __init__(self, svg_path):
        self.surface = svg_to_surface(
            svg_path,
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )
        self.alpha = 255
        self.fade_speed = 255 / 5  # fade out over 5 seconds

    def update(self, dt):
        if self.alpha > 0:
            self.alpha -= self.fade_speed * dt
            self.alpha = max(0, self.alpha)

    def draw(self, screen):
        if self.surface:
            temp = self.surface.copy()
            temp.set_alpha(int(self.alpha))
            screen.blit(temp, (0, 0))