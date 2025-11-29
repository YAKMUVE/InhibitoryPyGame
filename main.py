import pygame

from src.state import StateManager
from src.states.main_menu import MainMenuState
from src.assets import Assets

import json

SCREEN_W = 1280
SCREEN_H = 720

def load_json(path, default=None):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except Exception:
        return default

def main():
    pygame.init()

    settings = load_json('data/config/settings.json', {
        "screen_w": SCREEN_W,
        "screen_h": SCREEN_H,
        "fps": 60
    })

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Умный рыболов')
    clock = pygame.time.Clock()

    assets = Assets(screen)

    sm = StateManager(screen, assets, settings)
    sm.push(MainMenuState(sm))

    fps = settings.get('fps', 60)
    while sm.running:
        dt = clock.tick(fps) / 1000.0
        sm.handle_events(pygame.event.get())
        sm.update(dt)
        sm.render()
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
