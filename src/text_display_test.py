import pygame


SCREEN_WIDTH = 1388
SCREEN_HEIGHT = 768

class TextDisplayTest:

    def __init__(self, current_level, surface: pygame.Surface):
        
        self.display_surface = surface
        content = "This is a text display test" 
        self.font = pygame.font.Font(None, 50)
        self.txt_content = self.font.render(content, True, 'white')
        screen_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.txt_rect = self.txt_content.get_rect(center = screen_center)
    
    def run(self):
        self.get_input()
        self.display_surface.blit(self.txt_content, self.txt_rect.center)