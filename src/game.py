from os import path
from copy import copy

import pygame
from loading_screens import LoadingScreen

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
        self.loading_screen = LoadingScreen(200)
        self.unlock_level = self.player_stats.current_level
        self.level_completed = True
    
        # Audio
        self.level_bg_music = pygame.mixer.Sound(path.join(BASE_DIR, 'audio', 'level_music.wav'))
        self.overworld_bg_music = pygame.mixer.Sound(path.join(BASE_DIR, 'audio', 'overworld_music.wav'))
        music_volume = self.player_stats.preferences.get('music_volume', 0.4)
        self.level_bg_music.set_volume(music_volume)
        self.overworld_bg_music.set_volume(music_volume)

        self.create_overworld()

    def create_level(self, restart_music=True):
        self.level = Level(self.player_stats, self.show_menu)
        if restart_music:
            self.overworld_bg_music.fadeout(100)
            self.level_bg_music.play(-1)
        self.active_screen = 'level'
    
    def show_menu(self, unlock_level=-1):
        if not self.level_completed:
            self.unlock_level = unlock_level
        if self.unlock_level == self.level.next_level:
            self.level_completed = True
        self.menu = Menu(self.player_stats, self.level_completed, self.restart, self.create_overworld)
        self.active_screen = 'menu'
    
    def create_overworld(self):
        self.level_completed = False
        if self.unlock_level > self.player_stats.max_level:
            self.player_stats.max_level = self.unlock_level
        stats = copy(self.player_stats)
        stats.current_level = self.unlock_level
        save_player_stats(stats)
        navigate_to = self.unlock_level
        self.overworld = Overworld(self.player_stats, self.create_level, navigate_to)
        self.level_bg_music.fadeout(100)
        self.overworld_bg_music.play(-1)
        self.active_screen = 'overworld'
    
    def restart(self):
        self.create_level(False)
    
    def run(self):
        if self.active_screen == 'overworld':
            self.overworld.run([self.level_bg_music, self.overworld_bg_music])
        elif self.active_screen in ['level', 'menu']:
            self.level.run()
            if self.active_screen == 'menu':
                self.menu.update()
