import pygame
from pygame import Vector2 as vec

from settings import TILE_SIZE
from tile import Tile
from tools import import_folder


class Enemy(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        self.direction = vec(2, 0)
        self.damage = 25
        self.frame_index = 0
        self.animation_speed = 0.15
        self.keyframes = import_folder("../graphics/enemy/run")
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
        self.frame_index += self.animation_speed
        if self.frame_index > len(self.keyframes):
            self.frame_index = 0

    def check_for_collisions(self, constraint_tiles: pygame.sprite.Group):
        for tile in constraint_tiles.sprites():
            if tile.rect.colliderect(self.rect):
                if self.direction.x > 0:
                    self.rect.right = tile.rect.left
                elif self.direction.x < 0:
                    self.rect.left = tile.rect.right
                self.direction.x *= -1

    def update(self, constraint_tiles, x_shift):
        self.rect.x += self.direction.x + x_shift
        self.check_for_collisions(constraint_tiles)
        self.animate()


class EnemyConstraint(Tile):

    def __init__(self, pos):
        super().__init__(pos)
        # self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        # self.image.fill('red')
        # self.image.set_alpha(50)
    