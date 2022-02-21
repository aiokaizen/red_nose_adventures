from os import path

import pygame
from settings import ANIMATION_FPS, FPS, SCREEN_WIDTH, TILE_SIZE, BASE_DIR
from tools import import_cut_graphics, import_folder


class Tile(pygame.sprite.Sprite):
    
    def __init__(self, pos, groups=[], surface=None):
        super().__init__(groups)
        if surface:
            self.image = surface
            self.rect = self.image.get_rect(topleft=pos)
        else:
            self.rect = pygame.Rect(*pos, TILE_SIZE, TILE_SIZE)
    
    def update(self):
        pass


class AnimatedTile(Tile):

    def __init__(self, pos, groups, animations_dirs, graphic_id=0):
        super().__init__(pos, groups)
        self.frame_index = 0
        self.animation_speed = ANIMATION_FPS
        self.keyframes = import_folder(animations_dirs[graphic_id])
        self.image = self.keyframes[int(self.frame_index)]
        self.rect = self.image.get_rect(bottomleft=pos)
        self.collid_rect = self.rect
    
    def animate(self):
        self.image = self.keyframes[int(self.frame_index)]
        self.frame_index += self.animation_speed / FPS
        if self.frame_index >= len(self.keyframes):
            self.frame_index = 0
    
    def update(self):
        self.animate()


class CloudTile(Tile):

    def __init__(self, pos, groups, graphic_id=-1):
        super().__init__(pos, groups)
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


class WaterReflectionTile(AnimatedTile):

    def __init__(self, pos, size='big', groups=[]):
        path = BASE_DIR + f'/graphics/decoration/water/reflection_{size}'
        image_paths = [
            path,
        ]
        super().__init__(pos, groups, image_paths)
        self.rect = self.image.get_rect(topleft=pos)


class TerrainTile(Tile):

    def __init__(self, pos, groups, graphic_id=-1):
        super().__init__(pos, groups)
        if graphic_id != -1:
            terrain_tile_list = import_cut_graphics(path.join(BASE_DIR, "graphics", "terrain", "terrain_tiles_extended.png"))
            self.image = terrain_tile_list[graphic_id]
            self.rect = self.image.get_rect(topleft=pos)


class GrassTile(Tile):

    def __init__(self, pos, groups, graphic_id=-1):
        super().__init__(pos, groups)
        if graphic_id != -1:
            grass_tile_list = import_cut_graphics(path.join(BASE_DIR, "graphics", "decoration", "grass", "grass.png"))
            self.image = grass_tile_list[graphic_id]
            self.rect = self.image.get_rect(topleft=pos)


class PalmTile(AnimatedTile):

    def __init__(self, pos, groups, graphic_id=-1):
        paths = [
            BASE_DIR + '/graphics/terrain/palm_small',
            BASE_DIR + '/graphics/terrain/palm_large',
            BASE_DIR + '/graphics/terrain/palm_bg',
            BASE_DIR + '/graphics/terrain/palm_bg_top',
            BASE_DIR + '/graphics/terrain/palm_bg_left',
            BASE_DIR + '/graphics/terrain/palm_bg_right',
        ]
        super().__init__(pos, groups, paths, graphic_id)
        self.rect = self.image.get_rect(bottomleft=(pos[0], pos[1] + TILE_SIZE))


class CrateTile(Tile):

    def __init__(self, pos, groups, graphic_id=-1):
        super().__init__(pos, groups)
        if graphic_id != -1:
            self.image = pygame.image.load(path.join(BASE_DIR, "graphics", "terrain", "crate.png")).convert_alpha()
            self.rect = self.image.get_rect(bottomleft=(pos[0], pos[1] + TILE_SIZE))


class CollectibleTile(AnimatedTile):

    def __init__(self, pos, groups, graphic_id=-1):
        paths = [
            BASE_DIR + '/graphics/items/golden_skull',
            BASE_DIR + '/graphics/items/red_diamond',
            BASE_DIR + '/graphics/items/green_bottle',
        ]
        self.type = 'golden_skull'
        if graphic_id == 1:
            self.type = 'red_diamond'
        elif graphic_id == 2:
            self.type = 'green_bottle'
        super().__init__(pos, groups, paths, graphic_id)
        center_x, center_y = pos[0] + int(TILE_SIZE / 2), pos[1] + int(TILE_SIZE / 2)
        self.rect = self.image.get_rect(center=(center_x, center_y))
        self.collid_rect.height = 26
        self.collid_rect.bottom = self.rect.bottom


class CoinTile(AnimatedTile):

    def __init__(self, pos, groups, graphic_id=-1):
        paths = [
            BASE_DIR + '/graphics/items/coins/gold',
            BASE_DIR + '/graphics/items/coins/silver',
        ]
        self.type = 'gold' if graphic_id == 0 else 'silver'
        super().__init__(pos, groups, paths, graphic_id)
        center_x, center_y = pos[0] + int(TILE_SIZE / 2), pos[1] + int(TILE_SIZE / 2)
        self.rect = self.image.get_rect(center=(center_x, center_y))


class SpikesTile(Tile):

    def __init__(self, pos, groups):
        super().__init__(pos, groups)
        self.image = pygame.image.load(path.join(BASE_DIR, "graphics", "terrain", "spikes.png")).convert_alpha()
        self.rect = self.image.get_rect(bottomleft=(pos[0], pos[1] + TILE_SIZE))
        self.collide_rect = pygame.Rect(self.rect.left, self.rect.top + 32, self.rect.width, self.rect.height - 32)
        self.damage = 25


class FlagTile(AnimatedTile):

    FLAG_STATES = [
        'no_wind',
        'trans_to_wind',
        'wind',
        'trans_to_no_wind',
    ]

    def __init__(self, pos, groups):
        self.animation_states = {
            'no_wind': BASE_DIR + '/graphics/sail/no_wind',
            'trans_to_wind': BASE_DIR + '/graphics/sail/trans_to_wind',
            'wind': BASE_DIR + '/graphics/sail/wind',
            'trans_to_no_wind': BASE_DIR + '/graphics/sail/trans_to_no_wind',
        }
        self.state = FlagTile.FLAG_STATES[0]
        self.transition_state = FlagTile.FLAG_STATES[1]
        super().__init__(pos, groups, [self.animation_states[self.state]])
        self.rect.y += TILE_SIZE

        self.transitionning = False

    def animate(self):
        self.image = self.keyframes[int(self.frame_index)]
        self.frame_index += self.animation_speed / FPS
        if self.frame_index >= len(self.keyframes):
            self.frame_index = 0
            if self.transitionning:
                self.stop_transition()
    
    def start_transition(self):
        self.transitionning = True
        self.frame_index = 0
        self.keyframes = import_folder(self.animation_states[self.transition_state])
        if self.state == FlagTile.FLAG_STATES[0]:
            self.state = FlagTile.FLAG_STATES[2]
            self.transition_state = FlagTile.FLAG_STATES[3]
        else:
            self.state = FlagTile.FLAG_STATES[0]
            self.transition_state = FlagTile.FLAG_STATES[1]
    
    def stop_transition(self):
        self.transitionning = False
        self.keyframes = import_folder(self.animation_states[self.state])
    