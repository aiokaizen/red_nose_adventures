from enum import Enum
from os import walk
from csv import reader

import pygame

from settings import TILE_SIZE, debug_font, colors


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
    AIRBORN = "airborn"  # Player is in the air (JUMPING or FALLING)
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

    @classmethod
    def from_value(cls, value: str):
        if type(value) != str:
            raise Exception("invalid value. Must be of type 'str'.")
        if hasattr(cls, value.upper()):
            return getattr(cls, value.upper())
        raise Exception(cls.__name__, "class has no '" + value + "' attribute")
        

def import_folder(path):
    surface_list = []
    for _, _, img_files in walk(path):
        for img in img_files:
            full_path = path + '/' + img
            surface_list.append(
                pygame.image.load(full_path).convert_alpha()
            )
    return surface_list


def get_level_data(level):
    base_dir = f"../levels/level_{level}"
    return {
        'terrain': f'{base_dir}/level_{level}_terrain.csv',
        'player': f'{base_dir}/level_{level}_player.csv',
        'enemies': f'{base_dir}/level_{level}_enemies.csv',
        'enemies_constraints': f'{base_dir}/level_{level}_enemies_constraints.csv',
        'coins': f'{base_dir}/level_{level}_coins.csv',
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
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    pygame.draw.rect(surface, (255, 0, 0), (x, y, w, h), 1)


def debug(text, surface: pygame.Surface, pos=(10, 10)):
    content = debug_font.render(text, True, colors.dark)
    surface.blit(content, pos)
