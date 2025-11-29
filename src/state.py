import pygame

from src.assets import Assets


class BaseState:
    def __init__(self, manager: 'StateManager'):
        self.manager = manager

    def enter(self):
        """Вызывается при входе в состояние"""
        pass

    def exit(self):
        """Вызывается при выходе из состояния"""
        pass

    def handle_events(self, events):
        """Обработка событий"""
        pass

    def update(self, dt):
        """Обновление логики"""
        pass

    def render(self):
        """Отрисовка"""
        pass


class StateManager:
    def __init__(self, screen: pygame.Surface, assets: 'Assets', settings: dict) -> None:
        self.screen = screen
        self.assets = assets
        self.settings = settings

        self.stack = []

        self.running = True

    def push(self, state: BaseState) -> None:
        """"""
        if self.stack:
            self.stack[-1].exit()

        self.stack.append(state)

        state.enter()

    def pop(self) -> None:
        """"""
        if self.stack:
            self.stack[-1].exit()
            self.stack.pop()

        if self.stack:
            self.stack[-1].enter()

        else:
            self.running = False

    def switch(self, state: BaseState) -> None:
        """Переключение состояний"""
        self.pop()
        if state:
            self.push(state)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        if self.stack:
            self.stack[-1].handle_events(events)

    def update(self, dt: float) -> None:
        if self.stack:
            self.stack[-1].update(dt)

    def render(self) -> None:
        if self.stack:
            self.stack[-1].render()
