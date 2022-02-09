
levels = {
    0: {'node_pos': (110, 400), 'content': "This is level 0.", 'next_level': 1 },
    1: { 'node_pos': (300, 220), 'content': "This is level 1.", 'next_level': 2 },
    2: { 'node_pos': (480, 610), 'content': "This is level 2.", 'next_level': 3 },
    3: { 'node_pos': (610, 350), 'content': "This is level 3.", 'next_level': 4 },
    4: { 'node_pos': (880, 210), 'content': "This is level 4.", 'next_level': 5 },
    5: { 'node_pos': (1050, 400), 'content': "This is level 5.", 'next_level': 5 },
}

TILE_SIZE = 64
SCREEN_WIDTH = 1366
VERTICAL_ROWS = 11
SCREEN_HEIGHT = TILE_SIZE * VERTICAL_ROWS

# Camera settings
LEFT_CAMERA_BORDER = SCREEN_WIDTH / 4
RIGHT_CAMERA_BORDER = SCREEN_WIDTH - LEFT_CAMERA_BORDER

# Player related settings
PLAYER_SIZE = (32, 64)

# Time related settings
FPS = 60

# Debug
DEBUG = False
