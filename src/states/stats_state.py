import pygame

import json, os

from src.state import BaseState

class StatsState(BaseState):
    def __init__(self, manager):
        super().__init__(manager)
        self.exit_rect = pygame.Rect(10, 10, 48, 32)

        self.sessions = []
        self.font = pygame.font.SysFont('arial', 20)

    def enter(self):
        self.load_sessions()

    def load_sessions(self):
        try:
            with open('data/stats/stats.json', 'r', encoding='utf-8') as f:
                self.sessions = json.load(f)

        except Exception:
            self.sessions = []

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.exit_rect.collidepoint(e.pos):
                    self.manager.pop()

    def update(self, dt):
        pass

    def render(self):
        self.manager.screen.fill((248, 249, 250))

        # выход
        pygame.draw.rect(self.manager.screen, (200, 200, 200), self.exit_rect)
        self.manager.screen.blit(pygame.transform.smoothscale(self.manager.assets.get_image('exit'), (25, 25)), (self.exit_rect.x + self.exit_rect.w // 2 - 12.5, self.exit_rect.y + self.exit_rect.h // 2 - 12.5))

        title = self.font.render("Статистика", True, (0,0,0))
        self.manager.screen.blit(title, (self.manager.screen.get_width()//2 - title.get_width()//2, 60))

        y = 110
        for s in reversed(self.sessions[-10:]):  # show last 10
            line = f"{s.get('timestamp','')}: score={s.get('score',0)} errors={s.get('errors',0)} max_focus={s.get('max_focus',0)} time={s.get('time','')}"
            surf = self.font.render(line, True, (0,0,0))
            self.manager.screen.blit(surf, (60, y))
            y += 28
            if y > self.manager.screen.get_height() - 50:
                break
