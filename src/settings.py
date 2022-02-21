import os
import pygame


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR = os.path.join(BASE_DIR, 'save')
SECRET_KEY = b'vbKy2tcCyigQxr6VmdZK26QIhMuhAb_1fUfTNf38csc='

DEBUG = False

pygame.font.init()
debug_font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(os.path.join(BASE_DIR, 'graphics', 'ui', 'ARCADEPI.TTF'), 18)
normal_font = pygame.font.Font(os.path.join(BASE_DIR, 'graphics', 'ui', 'ARCADEPI.TTF'), 26)
large_font = pygame.font.Font(os.path.join(BASE_DIR, 'graphics', 'ui', 'ARCADEPI.TTF'), 40)


class Colors:
    def __init__(self):
        self.black = (0, 0, 0)
        self.dark = (51, 50, 61)
        self.light = (245, 241, 222)
        self.orange = (221, 198, 161)
        self.red = (255, 10, 10)
        self.skyred = (208, 170, 157)
        self.white = (255, 255, 255)
        self.green = (64, 119, 105)
        self.darkred = (187, 100, 100)

colors = Colors()

# Level settings
levels = {
    1: {'node_pos': (110, 400),},
    2: { 'node_pos': (300, 220)},
    3: { 'node_pos': (480, 610)},
    4: { 'node_pos': (610, 350)},
    5: { 'node_pos': (880, 210)},
    6: { 'node_pos': (1050, 400)},
}
TILE_SIZE = 64
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768

# Camera settings
CAMERA_BORDERS = {
    'left': SCREEN_WIDTH // 3.5,
    'right': SCREEN_WIDTH // 3.5,
    'top': SCREEN_HEIGHT // 5,
    'bottom': SCREEN_HEIGHT // 3,
}

# Time related settings
FPS = 60
ANIMATION_FPS = 10
