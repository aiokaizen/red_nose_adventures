from os import path
from copy import copy

import pygame

from menu import Menu
from overworld import Overworld
from level import Level
from tools import save_player_stats
from data import PlayerData
from settings import BASE_DIR


class Game:
    
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.player_stats = PlayerData.load_player_data()
        self.level = None
        self.menu = None
        self.music_volum = 0.04
        self.vfx_colum = 0.04
    
        # Audio
        self.level_bg_music = pygame.mixer.Sound(path.join(BASE_DIR, 'audio', 'level_music.wav'))
        self.overworld_bg_music = pygame.mixer.Sound(path.join(BASE_DIR, 'audio', 'overworld_music.wav'))
        self.level_bg_music.set_volume(self.music_volum)
        self.overworld_bg_music.set_volume(self.music_volum)

        self.create_overworld(self.player_stats.max_level)

    def create_level(self, restart_music=True):
        self.level = Level(self.player_stats, self.show_menu)
        if restart_music:
            self.overworld_bg_music.fadeout(100)
            self.level_bg_music.play(-1)
        self.active_screen = 'level'
    
    def show_menu(self, max_level=-1, navigate_to=-1):
        self.menu = Menu(self.player_stats, self.restart, self.create_overworld)
        self.active_screen = 'menu'
    
    def create_overworld(self, max_level=-1, navigate_to=-1):
        if max_level > self.player_stats.max_level:
            self.player_stats.max_level = max_level
        stats = copy(self.player_stats)
        if navigate_to >= 0:
            stats.current_level = navigate_to
        save_player_stats(stats)
        navigate_to = navigate_to if navigate_to > -1 else self.player_stats.current_level
        self.overworld = Overworld(self.player_stats, self.create_level, navigate_to)
        self.level_bg_music.fadeout(100)
        self.overworld_bg_music.play(-1)
        self.active_screen = 'overworld'
    
    def restart(self):
        self.create_level(False)
    
    def run(self):
        if self.active_screen == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            if self.active_screen == 'menu':
                self.menu.draw()
