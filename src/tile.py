from os import path

import pygame
from settings import ANIMATION_FPS, FPS, SCREEN_WIDTH, TILE_SIZE, BASE_DIR
from tools import import_cut_graphics, import_folder


class Tile(pygame.sprite.Sprite):
    
    def __init__(self, pos, surface=None):
        super().__init__()
        if surface:
            self.image = surface
            self.rect = self.image.get_rect(topleft=pos)
        else:
            self.rect = pygame.Rect(*pos, TILE_SIZE, TILE_SIZE)
    
    def update(self, x_shift):
        self.rect.x += x_shift


class AnimatedTile(Tile):

    def __init__(self, pos, animations_dirs, graphic_id=0):
        super().__init__(pos)
        self.frame_index = 0
        self.animation_speed = ANIMATION_FPS
        self.keyframes = import_folder(animations_dirs[graphic_id])
        self.image = self.keyframes[int(self.frame_index)]
        self.rect = self.image.get_rect(bottomleft=pos)
    
    def animate(self):
        self.image = self.keyframes[int(self.frame_index)]
        self.frame_index += self.animation_speed / FPS
        if self.frame_index >= len(self.keyframes):
            self.frame_index = 0
    
    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift


class CloudTile(Tile):

    def __init__(self, pos, graphic_id=-1):
        super().__init__(pos)
        if graphic_id != -1:
            image_paths = [
                BASE_DIR + '/graphics/decoration/clouds/1.png',
                BASE_DIR + '/graphics/decoration/clouds/2.png',
                BASE_DIR + '/graphics/decoration/clouds/3.png',
            ]
            self.image = pygame.image.load(image_paths[graphic_id]).convert_alpha()
            offset_pos = (pos[0], pos[1] + TILE_SIZE)
            self.rect = self.image.get_rect(bottomleft=offset_pos)
    
    def update(self, first_sprite, last_sprite):
        self.rect.x += 1
        if self.rect.x > last_sprite.rect.x + SCREEN_WIDTH:
            self.rect.x = first_sprite.rect.x - SCREEN_WIDTH


class WaterTile(AnimatedTile):

    def __init__(self, pos):
        image_paths = [
            BASE_DIR + '/graphics/decoration/water/',
        ]
        super().__init__(pos, image_paths)
        self.rect = self.image.get_rect(topleft=pos)


class TerrainTile(Tile):

    def __init__(self, pos, graphic_id=-1):
        super().__init__(pos)
        if graphic_id != -1:
            terrain_tile_list = import_cut_graphics(path.join(BASE_DIR, "graphics", "terrain", "terrain_tiles.png"))
            self.image = terrain_tile_list[graphic_id]
            self.rect = self.image.get_rect(topleft=pos)


class GrassTile(Tile):

    def __init__(self, pos, graphic_id=-1):
        super().__init__(pos)
        if graphic_id != -1:
            grass_tile_list = import_cut_graphics(path.join(BASE_DIR, "graphics", "decoration", "grass", "grass.png"))
            self.image = grass_tile_list[graphic_id]
            self.rect = self.image.get_rect(topleft=pos)


class PalmTile(AnimatedTile):

    def __init__(self, pos, graphic_id=-1):
        paths = [
            BASE_DIR + '/graphics/terrain/palm_small',
            BASE_DIR + '/graphics/terrain/palm_large',
            BASE_DIR + '/graphics/terrain/palm_bg',
        ]
        super().__init__(pos, paths, graphic_id)
        self.rect = self.image.get_rect(bottomleft=(pos[0], pos[1] + TILE_SIZE))


class CrateTile(Tile):

    def __init__(self, pos, graphic_id=-1):
        super().__init__(pos)
        if graphic_id != -1:
            self.image = pygame.image.load(path.join(BASE_DIR, "graphics", "terrain", "crate.png")).convert_alpha()
            self.rect = self.image.get_rect(bottomleft=(pos[0], pos[1] + TILE_SIZE))


class CoinTile(AnimatedTile):

    def __init__(self, pos, graphic_id=-1):
        paths = [
            BASE_DIR + '/graphics/items/coins/gold',
            BASE_DIR + '/graphics/items/coins/silver',
        ]
        self.type = 'gold' if graphic_id == 0 else 'silver'
        super().__init__(pos, paths, graphic_id)
        center_x, center_y = pos[0] + int(TILE_SIZE / 2), pos[1] + int(TILE_SIZE / 2)
        self.rect = self.image.get_rect(center=(center_x, center_y))
