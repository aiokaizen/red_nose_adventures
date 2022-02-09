import pygame
from pygame import Vector2 as vec

from settings import *


class Node(pygame.sprite.Sprite):

    def __init__(self, pos, level, status):
        super().__init__()
        self.image = pygame.Surface((100, 80))
        self.status = status
        self.level = level
        if self.status == 'available':
            self.image.fill('indianred')
        elif self.status == 'completed':
            self.image.fill('goldenrod')
        else:
            self.image.fill('#333333')
        self.rect = self.image.get_rect(center=pos)


class Hat(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("../graphics/overworld/hat.png").convert_alpha()
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

    def __init__(self, start_level, max_level, surface):

        # setup
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.hat = pygame.sprite.GroupSingle()

        # Sprites
        self.setup_levels()
    
    def setup_levels(self):
        self.nodes = pygame.sprite.Group()
        for level, data in levels.items():
            status = 'available' if self.max_level >= level else 'locked'
            if level < self.current_level:
                status = 'completed'
            node = Node(data['node_pos'], level, status)
            self.nodes.add(node)
        
        current_pos = self.get_node_by_level(self.current_level).rect.center
        self.hat.add(Hat(current_pos))

    def get_node_by_level(self, level):
        nodes = [node for node in self.nodes if node.level == level]
        if len(nodes) >= 1:
            return nodes[0]
        return None
    
    def get_input(self):
        if not self.hat.sprite.is_moving:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.go_next_node()
            elif keys[pygame.K_LEFT]:
                self.go_previous_node()
    
    def go_next_node(self):
        next_node = self.get_node_by_level(self.current_level + 1)
        if next_node and next_node.status != 'locked':
            self.hat.sprite.destination = vec(next_node.rect.center)
            self.current_level = next_node.level

    def go_previous_node(self):
        previous_node = self.get_node_by_level(self.current_level - 1)
        if previous_node and previous_node.status != 'locked':
            self.hat.sprite.destination = vec(previous_node.rect.center)
            self.current_level = previous_node.level
    
    def draw_lines(self):
        available_points = [node.rect.center for node in self.nodes.sprites() if node.status != 'locked']
        locked_points = [node.rect.center for node in self.nodes.sprites() if node.status == 'locked']
        if len(available_points) > 1:
            pygame.draw.lines(self.display_surface, 'silver', False, available_points, 6)
        if len(locked_points) > 1:
            pygame.draw.lines(self.display_surface, '#333333', False, locked_points, 6)
        if available_points and locked_points:
            pygame.draw.lines(self.display_surface, '#333333', False, [available_points[-1], locked_points[0]], 6)
    
    def run(self):
        self.get_input()
        self.draw_lines()
        self.nodes.draw(self.display_surface)
        self.hat.update()
        self.hat.draw(self.display_surface)
