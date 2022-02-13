from os.path import join

import pygame
from tools import ParticleEffectType, import_folder
from settings import BASE_DIR


class ParticleEffect(pygame.sprite.Sprite):

    def __init__(self, pos, type):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.5
        frames_folder = BASE_DIR + '/graphics/character/dust_particles/' + type.value
        if type == ParticleEffectType.EXPLOSION:
            frames_folder = join(BASE_DIR, 'graphics', 'enemy', 'explosion')
        self.frames = import_folder(frames_folder) 
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
    
    def animate(self):
        self.frame_index += self.animation_speed
        if int(self.frame_index) >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift
