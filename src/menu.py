import pygame
from pygame import Vector2 as vec

from settings import SCREEN_HEIGHT, SCREEN_WIDTH, colors, normal_font, large_font, small_font
from data import PlayerData
from tools import scale_rect
from ui import Button, Label


class Menu:

    def __init__(self, stats, level_completed, restart, view_map):
        self.display_surface = pygame.display.get_surface()
        self.player_stats = stats
        self.current_level = self.player_stats.current_level
        self.level_completed = level_completed

        # Game functions
        self.restart = restart
        self.view_map = view_map

        # UI elements Groups
        self.labels = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()

        menu_width = 500
        menu_height = 400
        self.menu_rect = pygame.Rect(
            (SCREEN_WIDTH / 2 - menu_width / 2, SCREEN_HEIGHT / 2 - menu_height / 2),
            (menu_width, menu_height)
        )

        # Menu Title
        menu_title = 'You died :)' if not self.level_completed else 'Level completed!'
        self.title_label = large_font.render(menu_title, True, colors.light)
        self.title_rect = self.title_label.get_rect(center=self.menu_rect.midtop)

        level_data = self.player_stats.levels[self.current_level]
        # Silver coins
        silver_coins_label_text = f"Silver coins: {level_data['current_silver_coins']} / {level_data['max_silver_coins']}"
        self.silver_coins_label = Label(
            (self.menu_rect.x + 70, self.menu_rect.y + 50), silver_coins_label_text, groups=[self.labels]
        )

        # Gold coins
        gold_coins_label_text = f"Gold coins: {level_data['current_gold_coins']} / {level_data['max_gold_coins']}"
        self.gold_coins_label = Label(
            (self.menu_rect.x + 70, self.menu_rect.y + 90),
            gold_coins_label_text, groups=[self.labels]
        )

        # Enemies killed
        enemies_killed_label_text = f"Enemies killed: {level_data['current_enemies_killed']} / {level_data['max_enemies']}"
        self.enemies_killed_label = Label(
            (self.menu_rect.x + 70, self.menu_rect.y + 130),
            enemies_killed_label_text, groups=[self.labels]
        )

        # Score
        score_label_text = f"Final score: {level_data['current_score']}"
        self.score_label = Label(
            (self.menu_rect.x + 70, self.menu_rect.y + 170),
            score_label_text, colors.darkred, groups=[self.labels]
        )

        # Restart button
        self.restart_btn = Button(
            (0, 0), 'RESTART', self.restart, (20, 10), 'large', groups=[self.buttons]
        )
        self.restart_btn.set_position(self.get_btn_restart_position())

        # Back to levels button
        self.view_map_btn = Button(
            (0, 0), 'RETURN TO MAP', self.view_map, groups=[self.buttons]
        )
        self.view_map_btn.set_position(self.get_btn_view_map_position())
    
    def get_input(self):
        keyboard_keys = pygame.key.get_pressed()
        if keyboard_keys[pygame.K_RETURN]:
            self.restart()
        elif keyboard_keys[pygame.K_ESCAPE]:
            self.view_map()
    
    def get_btn_restart_position(self):
        return vec(
            self.menu_rect.centerx - self.restart_btn.rect.width / 2,
            self.menu_rect.bottom - 150
        )
    
    def get_btn_view_map_position(self):
        return vec(
            self.menu_rect.centerx - self.view_map_btn.rect.width / 2,
            self.menu_rect.bottom - 80
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

        self.labels.draw(self.display_surface)

        for btn in self.buttons.sprites():
            btn.draw()
    
    def update(self):

        for btn in self.buttons.sprites():
            btn.update()
        
        self.draw()
