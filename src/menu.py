import pygame
from pygame import Vector2 as vec

from settings import SCREEN_HEIGHT, SCREEN_WIDTH, colors, normal_font, large_font, small_font
from data import PlayerData
from tools import scale_rect


class Menu:

    def __init__(self, stats, restart, view_map):
        self.display_surface = pygame.display.get_surface()
        self.player_stats = stats

        # Game functions
        self.restart = restart
        self.view_map = view_map

        menu_width = 500
        menu_height = 400
        self.menu_rect = pygame.Rect(
            (SCREEN_WIDTH / 2 - menu_width / 2, SCREEN_HEIGHT / 2 - menu_height / 2),
            (menu_width, menu_height)
        )

        # Menu Title
        self.title_label = large_font.render('You died :)', True, colors.light)
        self.title_rect = self.title_label.get_rect(center=self.menu_rect.midtop)

        # Score
        self.score_label = normal_font.render('Your score: ', True, colors.dark)
        self.score_rect = self.score_label.get_rect(bottomright=self.menu_rect.center)
        self.score_value_label = normal_font.render(' ' + str(self.get_score()), True, colors.dark)
        self.score_value_rect = self.score_value_label.get_rect(bottomleft=self.menu_rect.center)

        # Restart button
        self.restart_btn_label = large_font.render('RESTART', True, colors.dark)
        self.restart_btn_rect = self.restart_btn_label.get_rect(center=self.get_btn_restart_position())
        self.highlight_restart = False

        # Back to levels button
        self.view_map_btn_label = normal_font.render('RETURN TO MAP', True, colors.dark)
        self.view_map_btn_rect = self.view_map_btn_label.get_rect(center=self.get_btn_view_map_position())
        self.highlight_view_map = False
    
    def get_input(self):
        mouse_keys = pygame.mouse.get_pressed()
        keyboard_keys = pygame.key.get_pressed()
        if mouse_keys[0]:
            if self.restart_btn_rect.collidepoint(pygame.mouse.get_pos()):
                self.restart()
            elif self.view_map_btn_rect.collidepoint(pygame.mouse.get_pos()):
                self.view_map()
            return
        
        if keyboard_keys[pygame.K_RETURN]:
            self.highlight_restart = True
            self.restart()
        elif keyboard_keys[pygame.K_ESCAPE]:
            self.highlight_view_map = True
            self.view_map()
    
    def get_btn_restart_position(self):
        bh = self.restart_btn_label.get_height()  # button height
        return vec(
            self.menu_rect.centerx,
            self.menu_rect.bottom - (bh / 2) - 100
        )
    
    def get_btn_view_map_position(self):
        bh = self.view_map_btn_label.get_height()  # button height
        return vec(
            self.menu_rect.centerx,
            self.menu_rect.bottom - bh - 20
        )
    
    def get_score(self):
        stats: PlayerData = self.player_stats
        return (
            stats.gold_coins * 500 + stats.silver_coins * 100
        )
    
    def hover(self, button):
        if button == 'restart':
            button_bg_rect = scale_rect(self.restart_btn_rect, 20)
        elif button == 'view_map':
            button_bg_rect = scale_rect(self.view_map_btn_rect, 20)
        btn_bg = pygame.Surface(button_bg_rect.size)
        btn_bg.fill(colors.light)
        self.display_surface.blit(btn_bg, button_bg_rect)

    
    def draw(self):

        self.get_input()

        # Overlay shadow
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(168)
        self.display_surface.blit(overlay, (0, 0))

        # Menu background
        menu_bg = pygame.Surface(self.menu_rect.size)
        menu_bg.fill(colors.orange, None)
        self.display_surface.blit(menu_bg, self.menu_rect)

        # Menu Border
        menu_border_rect = scale_rect(self.menu_rect, 20)
        pygame.draw.rect(self.display_surface, colors.darkred, menu_border_rect, 20, 20)

        # Menu title
        title_bg_rect = scale_rect(self.title_rect, 20)
        title_bg = pygame.Surface(title_bg_rect.size)
        title_bg.fill(colors.black)
        self.display_surface.blit(title_bg, title_bg_rect)
        self.display_surface.blit(self.title_label, self.title_rect.topleft)

        # Score
        self.display_surface.blit(self.score_label, self.score_rect)
        self.display_surface.blit(self.score_value_label, self.score_value_rect)

        # Button restart
        if self.highlight_restart:
            self.hover('restart')
        elif self.restart_btn_rect.collidepoint(pygame.mouse.get_pos()):
            self.hover('restart')
        self.display_surface.blit(self.restart_btn_label, self.restart_btn_rect)  # button_offset)

        # Button view map
        if self.highlight_view_map:
            self.hover('view_map')
        elif self.view_map_btn_rect.collidepoint(pygame.mouse.get_pos()):
            self.hover('view_map')
        self.display_surface.blit(self.view_map_btn_label, self.view_map_btn_rect)
        