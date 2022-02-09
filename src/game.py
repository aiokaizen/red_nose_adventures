from overworld import Overworld
from level import Level


class Game:
    
    def __init__(self, surface):
        self.start_level = 1
        self.max_level = 1
        self.display_surface = surface
        self.create_level(self.start_level)
        self.create_overworld(self.start_level, self.max_level)
    
    def create_level(self, current_level):
        self.level = Level(current_level, self.display_surface, self.create_overworld)
        self.active_screen = 'level'
    
    def create_overworld(self, current_level, max_level, navigate_to=-1):
        navigate_to = navigate_to if navigate_to > -1 else current_level
        self.overworld = Overworld(current_level, max_level, self.display_surface, self.create_level, navigate_to)
        self.active_screen = 'overworld'
    
    def run(self):
        if self.active_screen == 'overworld':
            self.overworld.run()
        else:
            self.level.run()