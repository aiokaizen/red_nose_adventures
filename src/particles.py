import pygame
from tools import import_folder, ParticleEffectType


class ParticleEffect(pygame.sprite.Sprite):

    def __init__(self, pos, type):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.5
        self.frames = import_folder('../graphics/character/dust_particles/' + type.value) 
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
    
    def animate(self):
        self.frame_index += self.animation_speed
        if int(self.frame_index) >= len(self.frames):
            # self.frame_index = 0
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift
