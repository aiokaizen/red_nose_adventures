from os import path
from types import FunctionType

import pygame
from pygame import Vector2 as vec

from settings import colors, large_font, normal_font, small_font, BASE_DIR
from tools import empty_fn


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
        self.image = pygame.image.load(path.join(BASE_DIR, "graphics", "ui", "health_bar.png")).convert_alpha()
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
        self.gold_coin = pygame.image.load(path.join(BASE_DIR, "graphics", "items", "coins", "gold", "0.png")).convert_alpha()
        self.silver_coin = pygame.image.load(path.join(BASE_DIR, "graphics", "items", "coins", "silver", "0.png")).convert_alpha()
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


class Label(pygame.sprite.Sprite):

    def __init__(self, pos, text, font_size='small', color=colors.dark, groups=[]):
        super().__init__(groups)
        self.text = text
        self.color = color
        font = small_font if font_size == 'small' else normal_font
        if font_size == 'large':
            font = large_font
        self.image = font.render(self.text, True, self.color)
        self.rect = self.image.get_rect(topleft=pos)


class Button(pygame.sprite.Sprite):

    def __init__(self, pos, label_text, action, padding=(10, 10), font_size='normal', color=colors.dark, bg_color=colors.light, border_width=4, groups=[]):
        self.display_surface = pygame.display.get_surface()
        super().__init__(groups)
        pos = vec(pos)
        self.padding = vec(padding)
        self.action = action
        self.color = color
        self.bg_color = bg_color
        self.border_width = border_width
        label_pos = pos + padding
        self.label = Label(label_pos, label_text, font_size, self.color)
        self.image = pygame.Surface(vec(self.label.image.get_size()) + (self.padding * 2))
        self.image.fill(self.bg_color)
        self.rect = self.image.get_rect(topleft=pos)
    
    def set_position(self, topleft):
        self.rect.topleft = topleft
        self.label.rect.topleft = vec(topleft) + self.padding
    
    def move(self, distance: vec):
        self.rect.move_ip(distance)
        self.label.rect.move_ip(distance)
    
    def get_input(self):
        mouse_left_pressed = pygame.mouse.get_pressed()[0]
        if mouse_left_pressed:
            if self.hovered():
                self.action()
    
    def hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def update(self):
        self.get_input()

    def draw(self):
        self.display_surface.blit(self.image, self.rect)
        self.display_surface.blit(self.label.image, self.label.rect)
        if self.hovered():
            pygame.draw.rect(self.display_surface, self.color, self.rect, self.border_width)


class Slider(pygame.sprite.Sprite):

    def __init__(self, pos, current_value=50, min_value=0, max_value=100, size=(200, 20), color=colors.dark, bg_color=None, on_release=empty_fn, groups=[]):
        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()
        self.color = color
        self.bg_color = bg_color
        self.on_release = on_release

        self.current_value = current_value
        self.min_value = min_value
        self.max_value = max_value
        self.selecting_value = False

        # Slider wrapper
        self.image = pygame.Surface(size).convert_alpha()
        if self.bg_color:
            self.image.fill(self.bg_color)
        else:
            self.image.set_alpha(0)

        self.rect = self.image.get_rect(topleft=pos)
        
        # Slider track
        self.track_height = size[1] // 4
        self.track = pygame.Surface((size[0] - 10, 3))
        self.track.fill(self.color)
        self.track.set_alpha(120)
        self.track_rect = self.track.get_rect(topleft=vec(self.rect.topleft) + vec(5, self.track_height))
        self.update_track()
    
    def set_position(self, topleft):
        self.rect.topleft = topleft
        self.track_rect.topleft = vec(topleft) + vec(5, self.track_height)
        self.selected_track_rect.topleft = self.track_rect.topleft
    
    def move(self, distance: vec):
        self.rect.move_ip(distance)
        self.track_rect.move_ip(distance)
        self.selected_track_rect.move_ip(distance)
    
    def update_track(self):
        if self.selecting_value:
            new_track_width = pygame.mouse.get_pos()[0] - self.track_rect.left
            new_value = new_track_width * self.max_value / self.track_rect.width
            new_value = min(max(new_value, self.min_value), self.max_value)
            self.current_value = new_value
        else:
            new_track_width = int(self.current_value * self.track_rect.width / self.max_value)
        
        new_track_width = min(max(new_track_width, 0), self.track_rect.width)
        self.selected_track_rect = pygame.Rect(self.track_rect.topleft, (new_track_width, self.track_height))
    
    def change_value(self, value):
        if type(value) != int or self.min_value > value or value > self.max_value:
            raise Exception(f"Value '{value}' should be an int beween {self.min_value} and {self.max_value} (included).")
        self.current_value = value
        self.update_track()
    
    def get_input(self):
        mouse_left_pressed = pygame.mouse.get_pressed()[0]
        if mouse_left_pressed:
            if self.hovered() or self.selecting_value:
                self.selecting_value = True
                self.update_track()
        elif self.selecting_value:
            self.on_release()
            self.selecting_value = False
    
    def hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def update(self):
        self.get_input()

    def draw(self):
        self.display_surface.blit(self.image, self.rect)
        self.display_surface.blit(self.track, self.track_rect)
        pygame.draw.rect(self.display_surface, self.color, self.selected_track_rect)
        pygame.draw.circle(self.display_surface, self.color, self.selected_track_rect.midright, self.track_height * 1.3)
