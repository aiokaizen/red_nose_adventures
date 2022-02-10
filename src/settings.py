import pygame


pygame.font.init()


class Colors:
    def __init__(self):
        self.black = (0, 0, 0)
        self.dark = (51, 50, 61)
        self.light = (245, 241, 222)
        self.orange = (221, 198, 161)
        self.red = (208, 170, 157)
        self.white = (255, 255, 255)
        self.green = (64, 119, 105)

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
VERTICAL_ROWS = 11
SCREEN_HEIGHT = TILE_SIZE * VERTICAL_ROWS

# Camera settings
LEFT_CAMERA_BORDER = SCREEN_WIDTH / 4
RIGHT_CAMERA_BORDER = SCREEN_WIDTH - LEFT_CAMERA_BORDER

# Time related settings
FPS = 60

# Debug
DEBUG = False
debug_font = pygame.font.Font(None, 24)
