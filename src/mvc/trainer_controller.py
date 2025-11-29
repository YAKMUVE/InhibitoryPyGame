import pygame

from src.state import StateManager
from src.mvc.trainer_model import TrainerModel, KEY_POOL


class TrainerController:
    def __init__(self, model: TrainerModel, state_manager: StateManager):
        self.model = model
        self.state_manager = state_manager

        self.model.pick_new_target()
        self.model.spawn_entity()

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in KEY_POOL:
                mouse_pos = pygame.mouse.get_pos()

                for entity in self.model.entities:
                    if entity.rect.collidepoint(mouse_pos):
                        self.model.handle_selection(entity, e.key)
