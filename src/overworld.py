from os import path
import sys
import pygame
from pygame import Vector2 as vec

from settings import *
from decoration import Sky, Clouds
from tile import AnimatedTile
from tools import play_example_vfx
from ui import Button, Label, Slider


class Node(AnimatedTile):

    def __init__(self, pos, level, status):
        animation_path = path.join(BASE_DIR, 'graphics', 'overworld', f"{level - 1}")
        super().__init__(pos, [], [animation_path])
        self.status = status
        self.level = level
        self.rect = self.image.get_rect(center=pos)
    
    def animate(self):
        if self.status != 'locked':
            return super().animate()
        tint_surface = self.image.copy()
        tint_surface.fill(colors.dark, None, pygame.BLEND_RGB_MULT)
        self.image.blit(tint_surface, (0, 0))


class Hat(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load(path.join(BASE_DIR, 'graphics', 'overworld', "hat.png")).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.is_moving = False
        self.pos = vec(pos)
        self.destination = vec(pos)
    
    def update(self):
        destination = self.destination - vec(self.rect.center)
        if destination.length() > 0:
            self.is_moving = True
            direction = destination.normalize() * 5
            self.pos += direction
            self.rect.center = round(self.pos.x), round(self.pos.y)
            if (self.destination - vec(self.rect.center)).length() < 5:
                self.rect.center = self.destination
                self.is_moving = False


class Overworld:

    def __init__(self, stats, create_level, navigate_to=-1):

        # setup
        self.display_surface = pygame.display.get_surface()
        self.create_level = create_level
        self.player_stats = stats
        self.hat = pygame.sprite.GroupSingle()
        self.navigate_to = navigate_to

        self.sky = Sky(12)
        self.clouds = Clouds(10, SCREEN_WIDTH * 2, 35, overworld=True)
    
        self.start_time = pygame.time.get_ticks()
        self.allow_input = False

        # Sprites
        self.setup_levels()

        if navigate_to > -1 and navigate_to != self.player_stats.current_level:
            if navigate_to > self.player_stats.current_level:
                self.go_next_node()
            else:
                self.go_previous_node()
        
        # Settings
        self.controllers = pygame.sprite.Group()
        self.labels = pygame.sprite.Group()
        self.menu_is_visible = False
        self.is_menu_toggle_running = False
        self.menu_wrapper = pygame.Rect(0, -90, 600, 90)
        self.settings_btn = Button(
            (0, 0), 'Settings', self.start_toggle_menu, font_size='small', bg_color=colors.skyred,
            color=colors.dark, border_width=2, groups=[self.controllers]
        )
        self.exit_btn = Button(
            (self.settings_btn.rect.width, 0), 'Exit', self.exit, font_size='small', bg_color=colors.darkred,
            color=colors.light, border_width=2, groups=[self.controllers]
        )
        menu_tl = vec(self.menu_wrapper.topleft)
        self.music_volume_label = Label(menu_tl + vec(10, 10), 'Music volume: ', groups=self.labels)
        music_volume = self.player_stats.preferences.get('music_volume', 0.04)
        self.music_volume_slider = Slider(menu_tl + vec(180, 10), music_volume, 0, 1, groups=[self.controllers])

        self.vfx_volume_label = Label(menu_tl + vec(10, 40), 'VFX volume: ', groups=self.labels)
        vfx_volume = self.player_stats.preferences.get('vfx_volume', 0.04)
        self.vfx_volume_slider = Slider(menu_tl + vec(180, 40), vfx_volume, 0, 1, on_release=self.play_vfx, groups=[self.controllers])
    
    def setup_levels(self):
        self.nodes = pygame.sprite.Group()
        current_level = self.player_stats.current_level if self.navigate_to == -1 else self.navigate_to
        for level, data in levels.items():
            status = 'available' if self.player_stats.max_level >= level else 'locked'
            if level < current_level:
                status = 'completed'
            node = Node(data['node_pos'], level, status)
            self.nodes.add(node)
        
        current_pos = self.get_node_by_level(self.player_stats.current_level).rect.center
        self.hat.add(Hat(current_pos))

    def get_node_by_level(self, level):
        nodes = [node for node in self.nodes if node.level == level]
        if len(nodes) >= 1:
            return nodes[0]
        return None

    def start_toggle_menu(self):
        self.is_menu_toggle_running = True
    
    def play_vfx(self):
        play_example_vfx(self.player_stats.preferences['vfx_volume'])
    
    def move_menu(self, distance: vec):
        self.menu_wrapper.move_ip(distance)
        for label in self.labels.sprites():
            label.rect.move_ip(distance)
        for controller in self.controllers.sprites():
            controller.move(distance)

    def toggle_menu(self):
        move_by = 3
        if self.menu_is_visible:
            self.move_menu(vec(0, -move_by))
            if self.menu_wrapper.bottom <= 0:
                if self.menu_wrapper.bottom < 0:
                    self.move_menu(vec(0, -self.menu_wrapper.bottom))
                self.menu_is_visible = False
                self.is_menu_toggle_running = False
        else:
            self.move_menu(vec(0, move_by))
            if self.menu_wrapper.top >= 0:
                if self.menu_wrapper.bottom > 0:
                    self.move_menu(vec(0, -self.menu_wrapper.top))
                self.menu_is_visible = True
                self.is_menu_toggle_running = False
        
    def exit(self):
        pygame.quit()
        sys.exit()
    
    def update_volume(self, music_sounds=[], vfx_sounds=[]):
        music_volume = self.music_volume_slider.current_value
        vfx_volume = self.vfx_volume_slider.current_value

        if music_volume != self.player_stats.preferences['music_volume']:
            self.player_stats.preferences['music_volume'] = music_volume
            for sound in music_sounds:
                sound.set_volume(music_volume)

        if vfx_volume != self.player_stats.preferences['vfx_volume']:
            self.player_stats.preferences['vfx_volume'] = vfx_volume
            for sound in vfx_sounds:
                sound.set_volume(vfx_volume)
    
    def get_input(self):
        if not self.hat.sprite.is_moving and self.allow_input:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.go_next_node()
            elif keys[pygame.K_LEFT]:
                self.go_previous_node()
            elif keys[pygame.K_RETURN]:
                self.begin_level()
    
    def go_next_node(self):
        next_node = self.get_node_by_level(self.player_stats.current_level + 1)
        if next_node and next_node.status != 'locked':
            self.hat.sprite.destination = vec(next_node.rect.center)
            self.player_stats.current_level = next_node.level

    def go_previous_node(self):
        previous_node = self.get_node_by_level(self.player_stats.current_level - 1)
        if previous_node and previous_node.status != 'locked':
            self.hat.sprite.destination = vec(previous_node.rect.center)
            self.player_stats.current_level = previous_node.level
    
    def begin_level(self):
        if not self.hat.sprite.is_moving:
            self.create_level()

    def draw_lines(self):
        available_points = [node.rect.center for node in self.nodes.sprites() if node.status != 'locked']
        if len(available_points) > 1:
            pygame.draw.lines(self.display_surface, colors.light, False, available_points, 6)
    
    def draw(self):
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface)
        self.draw_lines()
        self.nodes.draw(self.display_surface)
        self.hat.draw(self.display_surface)

        # Draw the menu
        pygame.draw.rect(self.display_surface, colors.skyred, self.menu_wrapper, 0, border_bottom_right_radius=90)
        # pygame.draw.rect(self.display_surface, colors.dark, self.menu_wrapper, 2, border_bottom_right_radius=90)
        self.labels.draw(self.display_surface)
        for sprite in self.controllers.sprites():
            sprite.draw()

    def run(self, music_sounds=[], vfx_sounds=[]):
        if not self.allow_input:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= 500:
                self.allow_input = True
        self.get_input()
        self.hat.update()
        self.nodes.update()

        # toggeling menu
        if self.is_menu_toggle_running:
            self.toggle_menu()

        # Settings
        for sprite in self.controllers.sprites():
            sprite.update()

        self.update_volume(music_sounds, vfx_sounds)
        self.draw()
