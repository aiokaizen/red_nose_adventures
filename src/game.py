from overworld import Overworld


class Game:
    
    def __init__(self, surface):
        self.start_level = 2
        self.max_level = 4
        self.overworld = Overworld(self.start_level, self.max_level, surface)
    
    def run(self):
        self.overworld.run()