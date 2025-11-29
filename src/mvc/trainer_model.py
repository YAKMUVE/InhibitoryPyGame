import pygame

from src.assets import Assets
from typing import Dict, List

import random, json, time


KEY_POOL = [pygame.K_SPACE, pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l]


class Entity:
    def __init__(self, data: dict, target_pos: tuple):
        self.data = data

        self.pos = (target_pos[0], target_pos[1] + 100)
        self.target_pos = target_pos
        self.speed = 2

        self.rect = pygame.Rect(*self.pos, 100, 100)

        self.created_at = time.time()

    def update(self):
        if abs(self.target_pos[1] - self.pos[1]) > 2:
            self.pos = (self.pos[0], self.pos[1] - self.speed)
            self.rect = pygame.Rect(*self.pos, 100, 100)


class TrainerModel:
    def __init__(self, assets: Assets, settings: dict) -> None:
        self.assets = assets
        self.settings = settings

        self.exit_rect = pygame.Rect(10, 10, 48, 32)

        self.day = True
        self.game_running = True

        self.entities_pool = self._load_entities(self.day)
        self.entities: List[Entity] = []

        self.lives = 3

        self.current_target: Dict | None = None
        self.current_target_key: int | None = None

        # статистика
        self.score = 0
        self.max_focus = 0.0
        self.current_focus = 0.0
        self.errors = {}

        self.game_start_time = None
        self.current_game_time = 0.0
        self.spawn_timer = 0.0


    def _load_entities(self, is_day: bool) -> List[Dict]:
        """
        Чтение сущностей из файла конфига
        :param is_day: день
        :return: список сущностей
        """
        try:
            if is_day:
                with open('data\config\entities_day.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                with open('data\config\entities_night.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)

            return data

        except Exception:
            return []

    def toggle_daynight(self) -> None:
        if self.day:
            self.day = False
            self.assets.background_image = self.assets.get_image('background_trainer_night')

        else:
            self.day = True
            self.assets.background_image = self.assets.get_image('background_trainer_day')

        self.entities_pool = self._load_entities(self.day)

    def pick_new_target(self) -> None:
        self.current_target = random.choice(self.entities_pool)
        self.current_target_key = random.choice(KEY_POOL)

    def handle_selection(self, chosen_entity: Entity, pressed_key: int) -> None:
        if chosen_entity.data == self.current_target and pressed_key == self.current_target_key:
            self.score += 1

            self.entities.remove(chosen_entity)
            self.pick_new_target()

        else:
            self._lose_life()

    def _lose_life(self):
        self.lives -= 1

        self.current_focus = 0
        if self.errors.get(self.current_target["image"], False):
            self.errors[self.current_target["image"]] += 1
        else:
            self.errors[self.current_target["image"]] = 1

        if self.lives <= 0:
            self.game_over()

        else:
            snd = self.assets.get_sound('lose_life')
            if snd:
                self.assets.get_sound('lose_life').play()

    def game_over(self):
        self.game_running = False

        snd = self.assets.get_sound('game_over')
        if snd:
            self.assets.get_sound('game_over').play()

        entry = {
            'score': getattr(self, 'score', 0),
            'max_focus': getattr(self, 'max_focus', 0),
            'errors': getattr(self, 'errors', {}),
            'time': round(getattr(self, 'current_game_time', 0.0), 2),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        try:
            with open('data/stats/stats.json', 'r', encoding='utf-8') as f:
                arr = json.load(f)

        except Exception:
            arr = []

        arr.append(entry)
        with open('data/stats/stats.json', 'w', encoding='utf-8') as f:
            json.dump(arr, f, ensure_ascii=False, indent=2)

    def spawn_entity(self) -> None:
        if len(self.entities) > 3:
            if self.entities[0].data == self.current_target:
                self._lose_life()

            self.entities.pop(0)

        ent = random.choice(self.entities_pool)
        self.entities.append(Entity(ent, (random.choice([elem for elem in range(100, 1100, 50)]), random.choice([elem for elem in range(300, 600, 50)]))))

    def update(self, dt: float) -> None:
        self.spawn_timer += dt
        self.current_game_time += dt

        for entity in self.entities:
            entity.update()

        if self.current_game_time % 30 < dt:
            self.toggle_daynight()

        if self.spawn_timer > 1.0:
            self.spawn_entity()
            self.spawn_timer = 0.0

        self.current_focus += dt
        self.max_focus = max(self.max_focus, self.current_focus)
