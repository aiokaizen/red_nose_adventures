from os.path import join

import pygame
from tools import ParticleEffectType, import_folder
from settings import ANIMATION_FPS, BASE_DIR, FPS


class ParticleEffect(pygame.sprite.Sprite):

    def __init__(self, pos, groups, type):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = ANIMATION_FPS
        frames_folder = BASE_DIR + '/graphics/character/dust_particles/' + type.value
        if type == ParticleEffectType.EXPLOSION:
            frames_folder = join(BASE_DIR, 'graphics', 'enemy', 'explosion')
        elif type == ParticleEffectType.COLLECT_COIN:
            frames_folder = join(BASE_DIR, 'graphics', 'items', 'coins', 'effect')
        elif type == ParticleEffectType.COLLECT_SKULL:
            frames_folder = join(BASE_DIR, 'graphics', 'items', 'skull_effect')

        self.frames = import_folder(frames_folder) 
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
    
    def animate(self):
        animation_speed = self.animation_speed / FPS
        self.frame_index += animation_speed
        if int(self.frame_index) >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()
