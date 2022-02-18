from enum import Enum
import logging
import os
import json
from csv import reader

from cryptography import fernet

import pygame
from pygame import Vector2 as vec

from settings import SAVE_DIR, SCREEN_WIDTH, SECRET_KEY, TILE_SIZE, debug_font, colors, BASE_DIR


logging.basicConfig(filename='game.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


class PlayerState(Enum):
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    JUMP = "jump"
    FALL = "fall"
    LAND = "land"
    DEAD_HIT = "dead_hit"
    DEAD_GROUND = "dead_ground"
    AIRBORN_TOUCH_WALL = "airborn_touch_wall"

    @classmethod
    def from_value(cls, value: str):
        if type(value) != str:
            raise Exception("invalid value. Must be of type 'str'.")
        if hasattr(cls, value.upper()):
            return getattr(cls, value.upper())
        raise Exception(cls.__name__, "class has no '" + value + "' attribute")
        

class ParticleEffectType(Enum):
    RUN = "run"
    JUMP = "jump"
    LAND = "land"
    EXPLOSION = 'expolosion'
    COLLECT_COIN = 'collect_coin'

    @classmethod
    def from_value(cls, value: str):
        if type(value) != str:
            raise Exception("invalid value. Must be of type 'str'.")
        if hasattr(cls, value.upper()):
            return getattr(cls, value.upper())
        raise Exception(cls.__name__, "class has no '" + value + "' attribute")


class Debug:

    def __init__(self, position='topleft'):
        self.count = 0
        self.position = position
        self.start_position = vec(SCREEN_WIDTH - 400, 10)
        self.step = vec(0, 20)
    
    def reset(self):
        self.count = 0

    def write(self, text, surface: pygame.Surface, pos=()):
        pos = self.start_position + (self.step * self.count) if not pos else pos
        content = debug_font.render(text, True, colors.dark)
        surface.blit(content, pos)
        self.count += 1


debug = Debug()


def load_player_data(path=''):

    from data import PlayerData

    if not path:
        path = os.path.join(SAVE_DIR, 'save.ar')

    if not os.path.exists(path) or not os.path.isfile(path):
        logging.warn("Loading failed. Invalid file path.")
        return PlayerData()

    with open(path, 'r') as file:
        try:
            stats = bytes(bytearray.fromhex(file.read()))
            secret_key = SECRET_KEY
            key = fernet.Fernet(secret_key)
            json_stats = key.decrypt(stats)
            player_stats = PlayerData.from_dict(json.loads(json_stats))
            return player_stats
        except Exception as e:
            logging.error(str(e))
            return PlayerData()


def save_player_stats(player_stats):
    path = os.path.join(SAVE_DIR, 'save.ar')
    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)
    
    with open(path, 'w') as file:
        key = fernet.Fernet(SECRET_KEY)
        enc_stats = key.encrypt(bytes(json.dumps(player_stats.as_dict()), 'utf-8'))
        file.write(enc_stats.hex())
        logging.debug("Player stats saved successfully.")


def import_folder(path):
    surface_list = []
    for _, _, img_files in os.walk(path):
        img_files.sort()
        for img in img_files:
            full_path = os.path.join(path, img)
            surface_list.append(
                pygame.image.load(full_path).convert_alpha()
            )
    return surface_list


def get_level_data(level):
    base_dir = os.path.join(BASE_DIR, "levels", f"level_{level}")
    return {
        'terrain': f'{base_dir}/level_{level}_terrain.csv',
        'bg_terrain': f'{base_dir}/level_{level}_terrain_bg.csv',
        'player': f'{base_dir}/level_{level}_player.csv',
        'enemies': f'{base_dir}/level_{level}_enemies.csv',
        'enemies_constraints': f'{base_dir}/level_{level}_enemies_constraints.csv',
        'coins': f'{base_dir}/level_{level}_coins.csv',
        'spikes': f'{base_dir}/level_{level}_spikes.csv',
        'grass': f'{base_dir}/level_{level}_grass.csv',
        'crates': f'{base_dir}/level_{level}_crates.csv',
        'fg_palms': f'{base_dir}/level_{level}_fg_palms.csv',
        'bg_palms': f'{base_dir}/level_{level}_bg_palms.csv',
        'sky': f'{base_dir}/level_{level}_sky.csv',
        'clouds': f'{base_dir}/level_{level}_clouds.csv',
        'water': f'{base_dir}/level_{level}_water.csv',
    }


def import_csv_layout(file_path):
    layout = []
    with open(file_path) as map:
        level = reader(map, delimiter=',')
        for row in level:
            layout.append(list(row))
        return layout


def import_cut_graphics(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_width() / TILE_SIZE)
    tile_num_y = int(surface.get_height() / TILE_SIZE)
    cut_graphics = []

    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x, y = col * TILE_SIZE, row * TILE_SIZE
            splice = pygame.Surface((TILE_SIZE, TILE_SIZE), flags=pygame.SRCALPHA)
            splice.blit(surface, (0, 0), pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
            cut_graphics.append(splice)
    return cut_graphics


def update_layout_exclude(layout, values):
    new_layout = []
    for row in layout:
        new_layout.append([])
        for cell in row:
            new_value = cell if cell not in values else '-1'
            new_layout[len(new_layout) - 1].append(new_value)
    return new_layout


def update_layout_to_only_contain(layout, values):
    new_layout = []
    for row in layout:
        new_layout.append([])
        for cell in row:
            new_value = cell if cell in values else '-1'
            new_layout[len(new_layout) - 1].append(new_value)
    return new_layout


def draw_outline(surface, sprite):
    rect = sprite.rect
    if hasattr(sprite, 'collide_rect'):
        collide_rect = sprite.collide_rect
        x, y, w, h = collide_rect.x, collide_rect.y, collide_rect.width, collide_rect.height
        pygame.draw.rect(surface, (255, 0, 0), (x, y, w, h), 1)

    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    pygame.draw.rect(surface, (255, 0, 0), (x, y, w, h), 1)


def scale_rect(rect, scale=10):
    return pygame.Rect(
        (rect.left - scale // 2, rect.top - scale // 2),
        (rect.width + scale, rect.height + scale)
    )
