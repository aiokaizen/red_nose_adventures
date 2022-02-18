from os import path
import pygame
from pygame import Vector2 as vec

from settings import *
from decoration import Sky, Clouds
from tile import AnimatedTile


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

    def run(self):
        if not self.allow_input:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= 500:
                self.allow_input = True
        self.get_input()
        self.hat.update()
        self.nodes.update()
        self.draw()
