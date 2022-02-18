from os import path

import pygame
from pygame import Vector2 as vec

from settings import ANIMATION_FPS, FPS, TILE_SIZE, BASE_DIR
from tile import Tile
from tools import import_folder


class Enemy(pygame.sprite.Sprite):

    def __init__(self, pos, groups, constraint_tiles_group):
        super().__init__(groups)
        self.constraint_tiles = constraint_tiles_group
        self.direction = vec(2, 0)
        self.damage = 25
        self.frame_index = 0
        self.animation_speed = ANIMATION_FPS
        self.keyframes = import_folder(path.join(BASE_DIR, "graphics", "enemy", "run"))
        self.image = self.keyframes[self.frame_index]
        offset_x, offset_y = pos[0] + int(TILE_SIZE / 2), pos[1] + TILE_SIZE
        self.rect = self.image.get_rect(midbottom=(offset_x, offset_y))
    
    def animate(self):
        # Play current frame
        if self.direction.x < 0:
            self.image = self.keyframes[int(self.frame_index)]
        elif self.direction.x > 0:
            self.image = pygame.transform.flip(self.keyframes[int(self.frame_index)], True, False)
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

        # Choose next frame
        animation_speed = self.animation_speed / FPS
        self.frame_index += animation_speed
        if self.frame_index >= len(self.keyframes):
            self.frame_index = 0

    def check_for_collisions(self):
        for tile in self.constraint_tiles.sprites():
            if tile.rect.colliderect(self.rect):
                if self.direction.x > 0:
                    self.rect.right = tile.rect.left
                elif self.direction.x < 0:
                    self.rect.left = tile.rect.right
                self.direction.x *= -1

    def update(self):
        self.rect.x += self.direction.x
        self.check_for_collisions()
        self.animate()


class EnemyConstraint(Tile):

    def __init__(self, pos, groups):
        super().__init__(pos, groups)
        # self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        # self.image.fill('red')
        # self.image.set_alpha(50)
    