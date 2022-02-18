import pygame
from pygame import Vector2 as vec

from settings import CAMERA_BORDERS, DEBUG, colors
from tools import debug


class CameraGroup(pygame.sprite.Group):

    def __init__(self, level_rect, target=None, sprites=[]):
        super().__init__(sprites)
        self.display_surface = pygame.display.get_surface()
        self.offset = vec(0, 0)
        self.lvl_rect = level_rect
        self.target: pygame.sprite.Sprite = target
        borders = CAMERA_BORDERS
        self.camera_rect = pygame.Rect(
            borders['left'], borders['top'],
            pygame.display.get_window_size()[0] - (borders['left'] + borders['right']),
            pygame.display.get_window_size()[1] - (borders['top'] + borders['bottom'])
        )
        self.position = vec(self.camera_rect.topleft)
        self.view = pygame.Rect(
            self.position - (CAMERA_BORDERS['left'], CAMERA_BORDERS['top']),
            pygame.display.get_window_size(),
        )
    
    def set_target(self, target: pygame.sprite.Sprite):
        self.target = target
    
    def update_view(self):
        self.view.topleft = self.position - (CAMERA_BORDERS['left'], CAMERA_BORDERS['top'])

    def draw(self):
        sprites = self.sprites()
        surface = self.display_surface

        # Horizontal movement
        if self.target.rect.left < self.camera_rect.left:
            self.position.x += self.target.rect.left - self.camera_rect.left
            self.camera_rect.left = self.target.rect.left
            self.update_view()
            if self.view.left < self.lvl_rect.left:
                self.camera_rect.left = self.lvl_rect.left + CAMERA_BORDERS['left']
                self.position.x = self.lvl_rect.left + CAMERA_BORDERS['left']
        elif self.target.rect.right > self.camera_rect.right:
            self.position.x += self.target.rect.right - self.camera_rect.right
            self.camera_rect.right = self.target.rect.right
            self.update_view()
            if self.view.right > self.lvl_rect.right:
                self.camera_rect.right = self.lvl_rect.right - CAMERA_BORDERS['right']
                self.position.x = self.lvl_rect.right - self.camera_rect.width - CAMERA_BORDERS['right']
        
        # Vertical movement
        if self.target.rect.top < self.camera_rect.top:
            self.position.y += self.target.rect.top - self.camera_rect.top
            self.camera_rect.top = self.target.rect.top
            self.update_view()
            if self.view.top < self.lvl_rect.top - 200:
                self.camera_rect.top = self.lvl_rect.top - 200 + CAMERA_BORDERS['top']
                self.position.y = self.lvl_rect.top - 200 + CAMERA_BORDERS['top']
        elif self.target.rect.bottom > self.camera_rect.bottom:
            self.position.y += self.target.rect.bottom - self.camera_rect.bottom
            self.camera_rect.bottom = self.target.rect.bottom
            self.update_view()
            if self.view.bottom > self.lvl_rect.bottom:
                self.camera_rect.bottom = self.lvl_rect.bottom - CAMERA_BORDERS['bottom']
                self.position.y = self.lvl_rect.bottom - self.camera_rect.height - CAMERA_BORDERS['bottom']
            
        self.offset = vec(
            self.camera_rect.left - CAMERA_BORDERS['left'],
            self.camera_rect.top - CAMERA_BORDERS['top']
        )

        if DEBUG:
            camera_offset = self.camera_rect.copy()
            camera_offset.topleft -= self.offset
            pygame.draw.rect(surface, colors.red, camera_offset, 2)
        
        debug.reset()

        for spr in sprites:
            offset_pos = spr.rect.topleft - self.offset
            offset_rect = pygame.Rect(spr.rect).move(-self.offset)
            if hasattr(spr, 'draw'):
                spr.draw(offset_rect)
            else:
                self.spritedict[spr] = surface.blit(spr.image, offset_pos)
