import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH, colors, normal_font, large_font, small_font
from tools import scale_rect


class Menu:

    def __init__(self, stats, surface: pygame.Surface, restart, view_map):
        self.display_surface = surface
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
        self.title_label = large_font.render('GAME OVER', True, colors.light)
        self.title_rect = self.title_label.get_rect(center=self.menu_rect.midtop)

        # Restart button
        self.restart_btn_label = normal_font.render('RESTART', True, colors.dark)
        self.restart_btn_rect = self.restart_btn_label.get_rect(topleft=self.get_btn_restart_position())

        # Back to levels button
        self.view_map_btn_label = normal_font.render('VIEW MAP', True, colors.dark)
        self.view_map_btn_rect = self.view_map_btn_label.get_rect(topleft=self.get_btn_view_map_position())
    
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
            self.restart()
        elif keyboard_keys[pygame.K_ESCAPE]:
            self.view_map()
    
    def get_btn_restart_position(self):
        return (
            self.menu_rect.left + 50,
            self.menu_rect.bottom - 90
        )
    
    def get_btn_view_map_position(self):
        return (
            self.menu_rect.right - self.view_map_btn_label.get_size()[0] - 50,
            self.menu_rect.bottom - 90
        )
    
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

        # Button restart
        if self.restart_btn_rect.collidepoint(pygame.mouse.get_pos()):
            restart_bg_rect = scale_rect(self.restart_btn_rect, 20)
            restart_bg = pygame.Surface(restart_bg_rect.size)
            restart_bg.fill(colors.light)
            self.display_surface.blit(restart_bg, restart_bg_rect)
        self.display_surface.blit(self.restart_btn_label, self.get_btn_restart_position())

        # Button view map
        if self.view_map_btn_rect.collidepoint(pygame.mouse.get_pos()):
            view_map_bg_rect = scale_rect(self.view_map_btn_rect, 20)
            view_map_bg = pygame.Surface(view_map_bg_rect.size)
            view_map_bg.fill(colors.light)
            self.display_surface.blit(view_map_bg, view_map_bg_rect)
        self.display_surface.blit(self.view_map_btn_label, self.get_btn_view_map_position())
        
        #     print('mouse hovers restart rect')
        # elif self.view_map_btn_rect.collidepoint(pygame.mouse.get_pos()):
        #     print('mouse hovers view map rect')
