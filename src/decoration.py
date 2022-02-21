import random
from os.path import join

import pygame

from settings import *
from tile import Tile, WaterReflectionTile
from tools import import_folder


class Sky:

    def __init__(self, horizon):
        self.horizon = horizon
        self.top = pygame.image.load(BASE_DIR + '/graphics/decoration/sky/sky_top.png').convert_alpha()
        self.middle = pygame.image.load(BASE_DIR + '/graphics/decoration/sky/sky_middle.png').convert_alpha()
        self.bottom = pygame.image.load(BASE_DIR + '/graphics/decoration/sky/sky_bottom.png').convert_alpha()

        # Stretch images
        self.top = pygame.transform.scale(self.top, (SCREEN_WIDTH, TILE_SIZE))
        self.middle = pygame.transform.scale(self.middle, (SCREEN_WIDTH, TILE_SIZE))
        self.bottom = pygame.transform.scale(self.bottom, (SCREEN_WIDTH, TILE_SIZE))
    
    def draw(self, surface):
        for row in range(SCREEN_HEIGHT // TILE_SIZE):
            y = row * TILE_SIZE
            if row < self.horizon:
                surface.blit(self.top, (0, y))
            elif row == self.horizon:
                surface.blit(self.middle, (0, y))
            else:
                surface.blit(self.bottom, (0, y))


class Clouds:

    def __init__(self, lowest_point, world_width, cloud_number, overworld=False):
        self.min_x = -SCREEN_WIDTH
        self.max_x = world_width + SCREEN_WIDTH
        self.min_y = 0
        self.max_y = lowest_point * TILE_SIZE
        self.cloud_number = cloud_number
        self.overworld_clouds = overworld
        self.generate_clouds()
    
    def generate_clouds(self):
        if self.overworld_clouds:
            cloud_surface_list = import_folder(join(BASE_DIR, "graphics", "overworld", "clouds"))
        else:
            cloud_surface_list = import_folder(join(BASE_DIR, "graphics", "decoration", "clouds"))
        self.cloud_sprites = pygame.sprite.Group()
        for _ in range(self.cloud_number):
            cloud = random.choice(cloud_surface_list)
            x = random.randint(self.min_x, self.max_x)
            y = random.randint(self.min_y, self.max_y)

            sprite = Tile((x, y), [], cloud)
            self.cloud_sprites.add(sprite)

    def draw(self, surface):
        self.cloud_sprites.draw(surface)


class Water:

    def __init__(self, water_level):
        self.display_surface = pygame.display.get_surface()
        self.water_level = water_level
        self.water_level_px = self.water_level * TILE_SIZE + 15
        self.water = pygame.image.load(BASE_DIR + '/graphics/decoration/water/water.png')
        self.water = pygame.transform.scale(self.water, (SCREEN_WIDTH, TILE_SIZE))
        self.particles = WaterReflectionTile((SCREEN_WIDTH // 2 - 100, (self.water_level_px + 20)), 'big')

    def draw(self, surface):
        for row in range(self.water_level, SCREEN_HEIGHT // TILE_SIZE):
            y = row * TILE_SIZE + 15
            surface.blit(self.water, (0, y))
        pygame.draw.line(self.display_surface, colors.white, (0, self.water_level_px), (SCREEN_WIDTH, self.water_level_px))
        self.particles.update()
        self.display_surface.blit(self.particles.image, self.particles.rect)
