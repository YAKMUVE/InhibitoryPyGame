import pygame

from src.state import BaseState
from src.states.stats_state import StatsState
from src.states.trainer_state import TrainerState
from src.states.diagnosis_state import DiagnosisState

import os


class Button:
    def __init__(self, rect, text, callback, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font

        self.is_hovered = False

    def draw(self, surf):
        if self.is_hovered:
            pygame.draw.rect(surf, (138, 158, 255), self.rect, border_radius=36)

        txt = self.font.render(self.text, True, (0, 0, 0))
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, e):
        if e.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.is_hovered = True
            else:
                self.is_hovered = False

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.callback()


class MainMenuState(BaseState):
    def __init__(self, manager):
        super().__init__(manager)

        self.screen = None
        self.assets = None
        self.font = None
        self.buttons = None

    def enter(self):
        self.screen = self.manager.screen
        self.assets = self.manager.assets
        self.font = pygame.font.SysFont('arial', 24)

        self.assets.background_image = self.assets.get_image('background_main_menu')

        w, h = self.screen.get_size()
        self.buttons = [
            Button((w // 2 - 150, 360 + i * 70, 300, 60), name, cb, self.font)
            for i, (name, cb) in enumerate([
                ("Начать игру", lambda: self.manager.push(TrainerState(self.manager))),
                ("Диагностика", lambda: self.manager.push(DiagnosisState(self.manager))),
                ("Статистика", lambda: self.manager.push(StatsState(self.manager))),
                ("Руководство", lambda: os.startfile(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '\data\guide.pdf'))
            ])
        ]

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.manager.running = False

            for b in self.buttons:
                b.handle_event(e)

    def update(self, dt):
        pass

    def render(self):
        if self.assets.background_image:
            self.screen.blit(self.assets.background_image, (0, -50))
        else:
            self.screen.fill((228, 239, 246))

        title = pygame.font.SysFont('arial', 36).render('Меню', True, (0, 0, 0))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 60))

        for b in self.buttons:
            b.draw(self.screen)
