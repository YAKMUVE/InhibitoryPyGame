import pygame

from src.state import BaseState
from src.mvc.trainer_model import TrainerModel
from src.mvc.trainer_view import TrainerView
from src.mvc.trainer_controller import TrainerController


class TrainerState(BaseState):
    def __init__(self, manager):
        super().__init__(manager)

        self.screen = None
        self.assets = None

        # MVC
        self.model = None
        self.view = None
        self.controller = None

    def enter(self):
        self.screen = self.manager.screen
        self.assets = self.manager.assets

        self.model = TrainerModel(self.assets, self.manager.settings)
        self.view = TrainerView(self.screen, self.assets, self.model)
        self.controller = TrainerController(self.model, self.manager)

        music_list = self.assets.get_music_list()
        for music in music_list:
            pygame.mixer.music.load(self.assets.assets_dir + f'/music/{music}')

        if music_list:
            pygame.mixer.music.play(loops=True)


    def handle_events(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.manager.running = False

            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.model.exit_rect.collidepoint(e.pos):
                    self.model.game_running = False

            self.controller.handle_event(e)

    def update(self, dt):
        self.model.update(dt)

        if not self.model.game_running:
            pygame.mixer.music.stop()
            self.manager.pop()

    def render(self):
        self.view.render()
