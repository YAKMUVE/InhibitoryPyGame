import pygame

import os


class Assets:
    def __init__(self, screen: pygame.Surface, assets_dir: str = 'assets'):
        self.screen = screen
        self.assets_dir = assets_dir

        self.background_image = None

        self.images = {}
        self.music = {}

    def get_image(self, key: str) -> pygame.Surface | None:
        if not key:
            return None

        try:
            if key in self.images:
                return self.images[key]

            img = pygame.image.load(self.assets_dir + f'/image/{key}.png').convert_alpha()
            self.images[key] = img

            return img

        except Exception:
            return None

    def get_sound(self, file: str) -> pygame.mixer.Sound | None:
        pass

    def get_music_list(self) -> list[str]:
        return os.listdir(self.assets_dir + '/music')