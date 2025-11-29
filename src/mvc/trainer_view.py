import pygame

from src.assets import Assets
from src.mvc.trainer_model import TrainerModel


class TrainerView:
    def __init__(self, screen: pygame.Surface, assets: Assets, model: TrainerModel):
        self.screen = screen
        self.assets = assets
        self.model = model

        self.font = pygame.font.SysFont('arial', 22)

        self.assets.background_image = self.assets.get_image('background_trainer_day')

    def render(self) -> None:
        self._render_ui()
        self._render_entities()

    def _render_entities(self) -> None:
        for entity in self.model.entities:
            self.screen.blit(pygame.transform.smoothscale(self.assets.get_image(entity.data["image"]), (100, 100)), entity.pos)

    def _render_ui(self) -> None:
        if self.assets.background_image:
            self.screen.blit(self.assets.background_image, (0, 0))
        else:
            self.screen.fill((10, 20, 60))

        self.screen.blit(self.assets.get_image('water'), (0, -100))

        # выход
        pygame.draw.rect(self.screen, (200, 200, 200), self.model.exit_rect)
        self.screen.blit(pygame.transform.smoothscale(self.assets.get_image('exit'), (25, 25)), (
        self.model.exit_rect.x + self.model.exit_rect.w // 2 - 12.5, self.model.exit_rect.y + self.model.exit_rect.h // 2 - 12.5))

        # жизни
        for i in range(self.model.lives):
            self.screen.blit(pygame.transform.smoothscale(self.assets.get_image('lives'), (50, 50)), (120 + i * 35, 10))

        # время
        txt = self.font.render(f'{self.model.current_game_time:.1f}', True, (255, 255, 255))
        self.screen.blit(txt, (self.screen.get_width() - txt.get_width() // 2 - 50, 20))

        # цель (кнопка)
        if self.model.current_target_key == 32: txt = pygame.font.SysFont('arial', 36).render('[SPACE]', True, (255, 255, 255))
        elif self.model.current_target_key == 119: txt = pygame.font.SysFont('arial', 36).render('[W]', True, (255, 255, 255))
        elif self.model.current_target_key == 115: txt = pygame.font.SysFont('arial', 36).render('[S]', True, (255, 255, 255))
        elif self.model.current_target_key == 100: txt = pygame.font.SysFont('arial', 36).render('[D]', True, (255, 255, 255))
        elif self.model.current_target_key == 102: txt = pygame.font.SysFont('arial', 36).render('[F]', True, (255, 255, 255))
        elif self.model.current_target_key == 103: txt = pygame.font.SysFont('arial', 36).render('[G]', True, (255, 255, 255))
        elif self.model.current_target_key == 104: txt = pygame.font.SysFont('arial', 36).render('[H]', True, (255, 255, 255))
        elif self.model.current_target_key == 106: txt = pygame.font.SysFont('arial', 36).render('[J]', True, (255, 255, 255))
        elif self.model.current_target_key == 107: txt = pygame.font.SysFont('arial', 36).render('[K]', True, (255, 255, 255))
        elif self.model.current_target_key == 108: txt = pygame.font.SysFont('arial', 36).render('[L]', True, (255, 255, 255))
        self.screen.blit(txt, (self.screen.get_width() // 2 - txt.get_width() // 2 - 40, 15))

        # цель (сущность)
        target = pygame.transform.smoothscale(self.assets.get_image(self.model.current_target["image"]), (100, 100))
        self.screen.blit(target, (self.screen.get_width() // 2 - target.get_width() // 2 + 40, 0))
