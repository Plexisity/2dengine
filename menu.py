import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class LevelMenu:
    def __init__(self):
        self.visible = True
        self.font = pygame.font.SysFont("Arial", 40)

        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        cols = 3
        rows = 2
        button_w = 150
        button_h = 80
        spacing = 40

        start_x = SCREEN_WIDTH // 2 - (cols * button_w + (cols - 1) * spacing) // 2
        start_y = SCREEN_HEIGHT // 2 - (rows * button_h + (rows - 1) * spacing) // 2

        level_num = 1
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(
                    start_x + c * (button_w + spacing),
                    start_y + r * (button_h + spacing),
                    button_w,
                    button_h
                )
                self.buttons.append((rect, level_num))
                level_num += 1

    def handle_event(self, event):
        if not self.visible:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect, level_num in self.buttons:
                if rect.collidepoint(event.pos):
                    self.visible = False  # hide menu
                    return level_num  # tell game to change level

        return None

    def draw(self, screen):
        if not self.visible:
            return

        # dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(255)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # draw buttons
        for rect, level_num in self.buttons:
            pygame.draw.rect(screen, (70, 70, 200), rect, border_radius=10)

            text = self.font.render(f"Level {level_num}", True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=rect.center))