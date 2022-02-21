import pygame
from pygame import Vector2 as vec

from settings import colors, small_font, large_font, BASE_DIR


class LoadingScreen:

    def __init__(self, max_value):
        self.display_surface = pygame.display.get_surface()
        self.background = pygame.Surface(pygame.display.get_window_size())
        self.background.fill('#050505')
        self.max_value = max_value
        self.current_value = 0

        self.loading_bar_width = 400
        self.loading_bar_height = 20
        self.loading_bar_rect = pygame.Rect(
            int(self.background.get_width() / 2 - self.loading_bar_width / 2),
            int(self.background.get_height() / 2 - self.loading_bar_height / 2),
            self.loading_bar_width,
            self.loading_bar_height
        )

        self.loading_text = small_font.render('loading...', True, colors.light)
        self.loading_text_rect = self.loading_text.get_rect(
            midtop=(self.background.get_width() / 2, self.background.get_height() / 2 + 30)
        )
    
    def get_progress(self):
        max_bar_width = self.loading_bar_width - 10
        return self.current_value * max_bar_width / self.max_value
    
    def increment(self):
        self.current_value += 1
        if self.current_value >= self.max_value:
            self.current_value = self.max_value
            self.finished = True
    
    def run(self):
        self.draw()
    
    def draw(self):
        # Draw background
        self.display_surface.blit(self.background, (0, 0))
        
        # Draw loading bar border
        pygame.draw.rect(self.display_surface, colors.light, self.loading_bar_rect, 3, 3)

        # Draw loading bar progress
        inner_loading_bar_rect = pygame.Rect(
            vec(self.loading_bar_rect.topleft) + vec(5, 5),
            vec(self.get_progress(), self.loading_bar_rect.height - 10)
        )
        pygame.draw.rect(self.display_surface, colors.light, inner_loading_bar_rect)

        # Draw loading text
        self.display_surface.blit(self.loading_text, self.loading_text_rect)

        self.finished = False


class WelcomeScreen:

    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(f'{BASE_DIR}/graphics/ui/cairo_black.ttf', 48)
        
        self.background = pygame.Surface(pygame.display.get_window_size())
        self.background.fill('#050505')

        self.logo = self.font.render('EKB Games', True, colors.white)
        self.logo.set_alpha(0)
        self.logo_rect = self.logo.get_rect(
            center=vec(pygame.display.get_window_size()) / 2
        )
        self.start_time = pygame.time.get_ticks()

        self.finished = False
        
    def draw(self):
        # Draw background
        self.display_surface.blit(self.background, (0, 0))
        
        # Draw Logo
        self.display_surface.blit(self.logo, self.logo_rect)
    
    def run(self):
        time_elapsed = pygame.time.get_ticks() - self.start_time 

        if time_elapsed < 1500:
            alpha_value = (time_elapsed - 500) * 255 / 1000
            self.logo.set_alpha(alpha_value)
        
        elif time_elapsed > 2500 and time_elapsed <= 3500:
            alpha_value = 255 - (time_elapsed - 2500) * 255 / 1000
            self.logo.set_alpha(alpha_value)
        
        if time_elapsed > 4000:
            alpha_value = 255 - (time_elapsed - 4000) * 255 / 1000
            self.background.set_alpha(alpha_value)
        
        if time_elapsed > 5000:
            self.finished = True

        self.draw()
