import random

import pygame

from settings import *
from tile import Tile, WaterTile, CloudTile
from tools import import_folder


class Sky:

    def __init__(self, horizon):
        self.horizon = horizon
        self.top = pygame.image.load('../graphics/decoration/sky/sky_top.png').convert_alpha()
        self.middle = pygame.image.load('../graphics/decoration/sky/sky_middle.png').convert_alpha()
        self.bottom = pygame.image.load('../graphics/decoration/sky/sky_bottom.png').convert_alpha()

        # Stretch images
        self.top = pygame.transform.scale(self.top, (SCREEN_WIDTH, TILE_SIZE))
        self.middle = pygame.transform.scale(self.middle, (SCREEN_WIDTH, TILE_SIZE))
        self.bottom = pygame.transform.scale(self.bottom, (SCREEN_WIDTH, TILE_SIZE))
    
    def draw(self, surface):
        for row in range(VERTICAL_ROWS):
            y = row * TILE_SIZE
            if row < self.horizon:
                surface.blit(self.top, (0, y))
            elif row == self.horizon:
                surface.blit(self.middle, (0, y))
            else:
                surface.blit(self.bottom, (0, y))


class Clouds:

    def __init__(self, horizon, world_width, cloud_number):
        self.min_x = -SCREEN_WIDTH
        self.max_x = world_width + SCREEN_WIDTH
        self.min_y = 0
        self.max_y = horizon * TILE_SIZE
        self.cloud_number = cloud_number
        self.generate_clouds()
    
    def generate_clouds(self):
        cloud_surface_list = import_folder("../graphics/decoration/clouds/")
        self.cloud_sprites = pygame.sprite.Group()
        for n in range(self.cloud_number):
            cloud = random.choice(cloud_surface_list)
            x = random.randint(self.min_x, self.max_x)
            y = random.randint(self.min_y, self.max_y)

            sprite = Tile((x, y), cloud)
            self.cloud_sprites.add(sprite)

    def draw(self, surface, shift_x):
        self.cloud_sprites.update(shift_x)
        self.cloud_sprites.draw(surface)


class Water:

    def __init__(self, water_level, world_width):
        left_border = -SCREEN_WIDTH
        tile_width = 192
        tiles_number = int((world_width + SCREEN_WIDTH * 3) / tile_width)
        self.water_sprites = pygame.sprite.Group()

        for tile_index in range(tiles_number):
            x = tile_index * tile_width + left_border
            y = SCREEN_HEIGHT - water_level
            sprite = WaterTile((x, y))
            self.water_sprites.add(sprite)

    def draw(self, surface, x_shift):
        self.water_sprites.update(x_shift)
        self.water_sprites.draw(surface)
