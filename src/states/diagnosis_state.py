import pygame

import time, random, os, json

from src.state import BaseState
from typing import List


class DiagnosisState(BaseState):
    def __init__(self, manager):
        super().__init__(manager)
        self.exit_rect = pygame.Rect(10, 10, 48, 32)

        self.grid = []
        self.cell_rects: List[List[pygame.Rect]] = []

        self.found = set()

        self.start_time = None
        self.end_time = None
        self.next_number = 1

        self.font = pygame.font.SysFont('arial', 24)

        self.finished = False

    def enter(self):
        self.prepare_grid()

    def prepare_grid(self):
        nums = list(range(1, 26))
        random.shuffle(nums)

        self.grid = [nums[i * 5:(i + 1) * 5] for i in range(5)]
        self.cell_rects = []

        w, h = self.manager.screen.get_width(), self.manager.screen.get_height()

        grid_size = min(w - 100, h - 200)
        cell_size = grid_size // 5

        start_x, start_y = (w - cell_size * 5) // 2, 120
        for r in range(5):
            row_rects = []
            for c in range(5):
                rect = pygame.Rect(start_x + c * cell_size, start_y + r * cell_size, cell_size - 4, cell_size - 4)
                row_rects.append(rect)

            self.cell_rects.append(row_rects)

        self.found = set()
        self.next_number = 1

        self.start_time = None
        self.end_time = None

        self.finished = False

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.exit_rect.collidepoint(e.pos):
                    self.manager.pop()
                    return

                if self.finished:
                    return

                for r in range(5):
                    for c in range(5):
                        rect = self.cell_rects[r][c]
                        if rect.collidepoint(e.pos):
                            val = self.grid[r][c]
                            if val == self.next_number:
                                if self.next_number == 1:
                                    self.start_time = time.time()

                                self.found.add(val)
                                self.next_number += 1

                                if self.next_number > 25:
                                    self.end_time = time.time()
                                    self.finished = True

    def update(self, dt):
        pass

    def render(self):
        self.manager.screen.fill((255, 255, 255))

        pygame.draw.rect(self.manager.screen, (200, 200, 200), self.exit_rect)
        self.manager.screen.blit(pygame.transform.smoothscale(self.manager.assets.get_image('exit'), (25, 25)), (self.exit_rect.x  + self.exit_rect.w // 2 - 12.5, self.exit_rect.y + self.exit_rect.h // 2 - 12.5))

        title = self.font.render("Нажимайте на числа по порядку", True, (0,0,0))
        self.manager.screen.blit(title, (self.manager.screen.get_width() // 2 - title.get_width() // 2, 60))

        for r in range(5):
            for c in range(5):
                rect = self.cell_rects[r][c]
                val = self.grid[r][c]

                color = (230, 230, 230) if val in self.found else (245, 245, 245)
                pygame.draw.rect(self.manager.screen, color, rect)

                txt = self.font.render(str(val), True, (0, 0, 0))
                self.manager.screen.blit(txt, (rect.x + rect.w // 2 - txt.get_width() // 2, rect.y + rect.h // 2 - txt.get_height() // 2))

        if self.finished and self.start_time and self.end_time:
            total = self.end_time - self.start_time

            msg = f'Время: {total:.2f} сек'
            surf = self.font.render(msg, True, (0, 0, 0))
            self.manager.screen.blit(surf, (self.manager.screen.get_width() // 2 - surf.get_width() // 2, self.manager.screen.get_height() - 80))
