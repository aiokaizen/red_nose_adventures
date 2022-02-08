import pygame
from pygame.math import Vector2 as vec2
from settings import *
from tools import Direction, PlayerState, ParticleEffectType, import_folder
from tile import Tile


class Player(pygame.sprite.Sprite):

    def __init__(self, pos, surface: pygame.Surface, animation_functions: dict):
        super().__init__()
        self.import_character_assets()

        # Dust particles animation
        self.import_particles_assets()
        self.particles_frame_index = 0
        self.particles_animation_speed = 0.2
        self.display_surface = surface

        # Animation settings
        self.animation_functions = animation_functions
        self.frame_index = 0
        self.animation_speed = 0.09
        self.state = PlayerState.IDLE
        self.image = self.animations[self.state][self.frame_index]
        # self.rect = self.image.get_rect(topleft=pos)
        self.rect = pygame.Rect(pos, [50, self.image.get_height()])
        self.collidable = pygame.Surface((self.rect.width, self.rect.height))
        self.is_facing_right = True
        self.touching_ground = False
        self.touching_left_wall = False
        self.touching_right_wall = False
        self.touching_ceiling = False
        # The x value when horizontal collision is detected
        # This was declared to fix a bug when vertically colliding with a wall
        # The bug makes the character jump to the top of the wall
        self.h_collision_x = 0 

        # Horizontal Movement
        self.direction = pygame.math.Vector2(0, 0)
        self.h_speed = 6
        self.can_move_right = True
        self.can_move_left = True

        # Vertical Movement
        self.gravity = 1.2
        self.jumps_left = 2
        self.jump_height = -22
        self.is_airborn = False
        self.is_falling = False

        # Abilities
        self.can_jump_while_falling = True
        self.can_double_jump = True
    
    def import_character_assets(self):
        self.animations = {
            PlayerState.IDLE: [],
            PlayerState.WALK: [],
            PlayerState.RUN: [],
            PlayerState.JUMP: [],
            PlayerState.FALL: [],
            PlayerState.AIRBORN: [],
            PlayerState.AIRBORN_TOUCH_WALL: [],
        }
        character_assets_dir = '../graphics/character/'
        for animation in self.animations.keys():
            animation_path = character_assets_dir + animation.value
            self.animations[animation] = import_folder(animation_path)
    
    def import_particles_assets(self):
        self.particles_animations = {
            ParticleEffectType.RUN: [],
            ParticleEffectType.JUMP: [],
            ParticleEffectType.LAND: [],
        }
        character_assets_dir = '../graphics/character/dust_particles/'
        for animation in self.particles_animations.keys():
            animation_path = character_assets_dir + animation.value
            self.particles_animations[animation] = import_folder(animation_path)
    
    def animate(self):
        if not self.state == PlayerState.LAND:
            animation = self.animations[self.state]
            self.frame_index += self.animation_speed
            if self.frame_index > len(animation):
                self.frame_index = 0

            image = animation[int(self.frame_index)]
            self.image = image if self.is_facing_right else pygame.transform.flip(image, True, False)
        
    #     self.update_player_position()
    
    # def update_player_position(self):
    #     if self.state in [PlayerState.RUN, PlayerState.IDLE]:
    #         img_rect = self.image.get_rect(bottomright=self.rect.bottomright)
    #         self.rect.bottom = img_rect.bottom

    def animate_particles(self):
        if self.state == PlayerState.RUN:
            # Get the correct animation
            animation = self.particles_animations[ParticleEffectType.RUN]

            # Get next frame
            self.particles_frame_index += self.particles_animation_speed
            if self.particles_frame_index > len(animation):
                self.particles_frame_index = 0
            
            # Animate the particles
            particle: pygame.Surface = animation[int(self.particles_frame_index)]

            if self.is_facing_right:
                particle_pos = self.rect.bottomleft - vec2(particle.get_width(), particle.get_height())
                self.display_surface.blit(particle, particle_pos)
            else:
                particle_pos = self.rect.bottomright + vec2(particle.get_width(), -particle.get_height())
                flipped_particle = pygame.transform.flip(particle, True, False)
                self.display_surface.blit(flipped_particle, particle_pos)

    def get_input(self):
        keys = pygame.key.get_pressed()

        # Horisontal movement
        self.direction.x = 0
        if keys[pygame.K_RIGHT]:
            self.change_direction(Direction.RIGHT)
        elif keys[pygame.K_LEFT]:
            self.change_direction(Direction.LEFT)
        
        # Vertical movement
        if keys[pygame.K_SPACE]:
            self.jump()

    def change_direction(self, direction):
        if direction in [Direction.RIGHT, Direction.LEFT]:
            if direction == Direction.LEFT:
                if not self.can_move_right:
                    self.can_move_right = True
                self.direction.x = -1
                self.is_facing_right = False
            elif direction == Direction.RIGHT:
                if not self.can_move_left:
                    self.can_move_left = True
                self.direction.x = 1
                self.is_facing_right = True
    
    def jump(self):
        if (
            self.jumps_left > 0 and
            (self.touching_ground or self.can_jump_while_falling) and
            (self.jumps_left >= 2 or self.direction.y > self.jump_height + 10)
        ):
            self.direction.y = self.jump_height
            self.rect.y += self.direction.y
            self.is_airborn = True
            self.animation_functions['jump'](self.rect.midbottom + vec2(0, 9))
            self.jumps_left = self.jumps_left -1 if self.can_double_jump else 0
    
    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y
        # tmp code
        if self.rect.y > SCREEN_HEIGHT:
            self.rect.y = -70
    
    def check_for_horizontal_collisions(self, tile_group_list):
        collision_detected = False

        for tiles in tile_group_list:
            for tile in tiles.sprites():
                if tile.rect.colliderect(self.rect):
                    if self.direction.x > 0:
                        if self.direction.y == 0 or (
                            abs(self.rect.right - tile.rect.left) < min(
                                abs(tile.rect.bottom - self.rect.top),
                                abs(self.rect.bottom - tile.rect.top)
                            )
                        ):
                            self.rect.right = tile.rect.left
                            self.touching_right_wall = True
                            self.h_collision_x = self.rect.right
                            collision_detected = True
                            break
                    elif self.direction.x < 0:
                        if self.direction.y == 0 or (
                            abs(tile.rect.right - self.rect.left) < min(
                                abs(tile.rect.bottom - self.rect.top),
                                abs(self.rect.bottom - tile.rect.top)
                            )
                        ):
                            self.rect.left = tile.rect.right
                            self.touching_left_wall = True
                            self.h_collision_x = self.rect.left
                            collision_detected = True
                            break
                if collision_detected:
                    break

        if not collision_detected:
            self.can_move_left = True
            self.can_move_right = True
        
        if (
            self.touching_left_wall and self.h_collision_x - 5 < self.rect.left > self.h_collision_x + 5
        ):
            self.touching_left_wall = False
        if (
            self.touching_right_wall and self.h_collision_x - 5 < self.rect.right > self.h_collision_x + 5
        ):
            self.touching_right_wall = False
        
    def check_for_vertical_collisions(self, tile_group_list):
        self.touching_ground = False
        self.touching_ceiling = False

        for tiles in tile_group_list:
            for tile in tiles.sprites():
                if tile.rect.colliderect(self.rect):
                    if self.direction.y > 0:
                        self.rect.bottom = tile.rect.top
                        self.is_airborn = False
                        self.init_jump_count()
                        self.touching_ground = True
                    elif self.direction.y < 0:
                        self.rect.top = tile.rect.bottom
                        self.touching_ceiling = True
                    self.direction.y = 0
    
    def init_jump_count(self):
        self.jumps_left = 2
    
    def update_state(self):
        if self.direction.y == 0 and self.state == PlayerState.FALL:
            self.state = PlayerState.LAND
            self.animation_functions['land'](self.rect.midbottom + vec2(0, -18))
        elif self.direction.x == 0 and self.direction.y == 0:
            self.state = PlayerState.IDLE
        elif self.direction.y < 0:
            self.state = PlayerState.JUMP
        elif self.direction.y > 0:
            self.state = PlayerState.FALL
        elif self.direction.x != 0:
            self.state = PlayerState.RUN
    
    def run(self):
        running_speed = self.direction.x * self.h_speed
        if (self.can_move_right and running_speed > 0) or (self.can_move_left and running_speed < 0):
            self.rect.centerx += running_speed

    def update(self, tiles_dict):

        # Get input
        self.get_input()

        self.run()

        collidable_tiles = [
            tiles_dict['terrain'], tiles_dict['fg_palms']
        ]

        # Horizontal collisions
        self.check_for_horizontal_collisions(collidable_tiles)
        
        self.apply_gravity()
        # Vertical collisions
        self.check_for_vertical_collisions(collidable_tiles)
        
        # Animations
        self.update_state()
        self.animate()
        self.animate_particles()

    def draw(self, surface: pygame.Surface):

        if self.is_facing_right or self.state == PlayerState.JUMP:
            pos = (self.rect.left, self.rect.bottom - self.image.get_height())
        else:
            pos = (self.rect.left + self.image.get_width() - 100, self.rect.bottom - self.image.get_height())
        surface.blit(self.image, pos)

class HatTile(Tile):

    def __init__(self, pos):
        super().__init__(pos)
        self.image = pygame.image.load("../graphics/character/hat.png").convert_alpha()
        pos = (
            pos[0] + int(TILE_SIZE / 2) - (self.image.get_width() / 2),
            pos[1] + int(TILE_SIZE / 2) - (self.image.get_height() / 2)
        )
        self.rect = self.image.get_rect(center=pos)