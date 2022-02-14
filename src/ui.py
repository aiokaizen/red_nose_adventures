import pygame
from pygame import Vector2 as vec

from settings import colors, normal_font


class LevelUI:

    def __init__(self, current_health, max_health, surface):
        self.health_bar = HealthBar(current_health, max_health, surface)
        self.coins_indicator = CoinsIndicator(surface)
    
    def draw(self):
        self.health_bar.draw()
        self.coins_indicator.draw()


class HealthBar(pygame.sprite.Sprite):

    def __init__(self, current_health, max_health, surface: pygame.Surface):
        super().__init__()
        self.current_health = current_health
        self.displayed_health = current_health
        self.max_health = max_health
        self.display_surface = surface
        self.image = pygame.image.load("../graphics/ui/health_bar.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(30, 30))
    
    def get_bar_rect(self):
        width = self.displayed_health * 154 / 100
        height = 6
        x, y = (self.rect.x + 33, self.rect.y + 28)
        return pygame.Rect(x, y, width, height)
    
    def draw(self):
        self.display_surface.blit(self.image, self.rect.topleft)
        pygame.draw.rect(self.display_surface, colors.red, self.get_bar_rect()) 
    
    def take_damage(self, damage):
        self.current_health -= damage
    
    def heal(self, heal):
        self.current_health += heal

    def update(self):
        if self.displayed_health != self.current_health:
            if self.displayed_health < self.current_health:
                self.displayed_health += 1
            else:
                self.displayed_health -= 1


class CoinsIndicator(pygame.sprite.Sprite):

    def __init__(self, surface: pygame.Surface):
        super().__init__()
        self.display_surface = surface
        self.gold_coins = 0
        self.silver_coins = 0
        self.gold_coin = pygame.image.load("../graphics/coins/gold/0.png").convert_alpha()
        self.silver_coin = pygame.image.load("../graphics/coins/silver/0.png").convert_alpha()
        self.rect = pygame.Rect(30, 100, 160, 32)
    
    def add_coin(self, type):
        if type == 'gold':
            self.gold_coins += 1
        elif type == 'silver':
            self.silver_coins += 1
    
    def draw(self):
        self.display_surface.blit(self.silver_coin, self.rect.topleft)
        self.display_surface.blit(self.gold_coin, vec(self.rect.topleft) + vec(102, 0))
        silver_coins_indicator = normal_font.render(str(self.silver_coins), True, colors.black)
        gold_coins_indicator = normal_font.render(str(self.gold_coins), True, colors.black)
        text_y_pos = self.rect.top + ((self.rect.height - silver_coins_indicator.get_height()) / 2)
        self.display_surface.blit(silver_coins_indicator, [self.rect.left + 42, text_y_pos])
        self.display_surface.blit(gold_coins_indicator, [self.rect.left + 144, text_y_pos])
