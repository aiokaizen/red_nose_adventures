from copy import copy
from overworld import Overworld
from level import Level
from tools import save_player_stats
from stats import PlayerStats


class Game:
    
    def __init__(self, surface):
        self.display_surface = surface
        self.player_stats = PlayerStats.load_player_stats()
        self.level = None
        self.create_overworld(self.player_stats.max_level)
    
    def create_level(self):
        self.level = Level(self.player_stats, self.display_surface, self.create_overworld)
        self.active_screen = 'level'
    
    def create_overworld(self, max_level=-1, navigate_to=-1):
        if max_level > self.player_stats.max_level:
            self.player_stats.max_level = max_level
        stats = copy(self.player_stats)
        if navigate_to >= 0:
            stats.current_level = navigate_to
        save_player_stats(stats)
        navigate_to = navigate_to if navigate_to > -1 else self.player_stats.current_level
        self.overworld = Overworld(self.player_stats, self.display_surface, self.create_level, navigate_to)
        self.active_screen = 'overworld'
    
    def run(self):
        if self.active_screen == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
