from os import path

from math import sin

import pygame
from pygame.math import Vector2 as vec

from settings import *
from tools import Direction, PlayerState, ParticleEffectType, debug, import_folder
from tile import Tile


class Player(pygame.sprite.Sprite):

    def __init__(self, pos, groups, collision_sprites, health_bar, surface: pygame.Surface, animation_functions: dict):
        super().__init__(groups)

        # Dust particles animation
        self.import_particles_assets()
        self.particles_frame_index = 0
        self.particles_animation_speed = ANIMATION_FPS
        self.display_surface = surface
        self.particle_effect: pygame.Surface = pygame.Surface((0, 0))
        self.particle_effect_rect: pygame.Rect = self.particle_effect.get_rect(topleft=(0, 0))

        # Animation settings
        self.import_character_assets()
        self.state = PlayerState.IDLE
        self.animation_functions = animation_functions
        self.frame_index = 0
        self.animation_speed = ANIMATION_FPS
        self.is_animating = True
        self.image = self.animations[self.state][self.frame_index]
        self.rect = pygame.Rect(pos, [50, self.image.get_height()])
        
        self.collidable = pygame.Surface((self.rect.width, self.rect.height))
        self.collision_sprites = collision_sprites
        
        # Player stats
        self.health_bar = health_bar
        self.gold_coins = 0
        self.silver_coins = 0
        self.is_facing_right = True
        self.touching_ground = False
        self.touching_left_wall = False
        self.touching_right_wall = False
        self.touching_ceiling = False
        # The x value when horizontal collision is detected
        # This was declared to fix a bug when vertically colliding with a wall
        # The bug makes the character jump to the top of the wall
        self.h_collision_x = 0 
        self.is_dead = False
        self.level_completed = False

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
        self.can_jump_while_falling = False
        self.can_double_jump = False
        self.is_invincible = 0
        self.invincibility_start_time = -1
        self.invincibility_duration = 0  # in miliseconds
        self.invincibility_after_damage = 2000  # in miliseconds

        # Audio
        self.soundeffects = {
            'hit': pygame.mixer.Sound(os.path.join(BASE_DIR, 'audio', 'effects', 'hit.wav')),
            'jump': pygame.mixer.Sound(os.path.join(BASE_DIR, 'audio', 'effects', 'jump.wav')),
        }
    
    def set_level_completed(self):
        self.state = PlayerState.IDLE
        self.level_completed = True
    
    def play_soundeffect(self, soundeffect, volume=0.05):
        sound: pygame.mixer.Sound = self.soundeffects[soundeffect]
        sound.set_volume(volume)
        sound.play()
    
    def import_character_assets(self):
        self.animations = {
            PlayerState.IDLE: [],
            PlayerState.WALK: [],
            PlayerState.RUN: [],
            PlayerState.JUMP: [],
            PlayerState.FALL: [],
            PlayerState.DEAD_HIT: [],
            PlayerState.DEAD_GROUND: [],
            PlayerState.AIRBORN_TOUCH_WALL: [],
        }
        character_assets_dir = BASE_DIR + '/graphics/character/'
        for animation in self.animations.keys():
            animation_path = character_assets_dir + animation.value
            self.animations[animation] = import_folder(animation_path)
    
    def import_particles_assets(self):
        self.particles_animations = {
            ParticleEffectType.RUN: [],
            # ParticleEffectType.JUMP: [],
            # ParticleEffectType.LAND: [],
        }
        character_assets_dir = BASE_DIR + '/graphics/character/dust_particles/'
        for animation in self.particles_animations.keys():
            animation_path = character_assets_dir + animation.value
            self.particles_animations[animation] = import_folder(animation_path)
    
    def animate(self):
        if self.state == PlayerState.LAND or not self.is_animating:
            return

        animation = self.animations[self.state]
        animation_speed = self.animation_speed / FPS
        self.frame_index += animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
            if self.state == PlayerState.DEAD_HIT:
                self.state = PlayerState.DEAD_GROUND
            elif self.state == PlayerState.DEAD_GROUND:
                self.is_animating = False
                return

        image = animation[int(self.frame_index)]
        self.image = image if self.is_facing_right else pygame.transform.flip(image, True, False)
  
    def animate_particles(self):
        if self.state != PlayerState.RUN:
            return

        # Get the correct animation
        animation = self.particles_animations[ParticleEffectType.RUN]

        # Get next frame
        animation_speed = self.particles_animation_speed / FPS
        self.particles_frame_index += animation_speed
        if self.particles_frame_index >= len(animation):
            self.particles_frame_index = 0
        
        # Animate the particles
        self.particle_effect: pygame.Surface = animation[int(self.particles_frame_index)]
        self.particle_effect_rect: pygame.Rect = pygame.Rect(
            0, 0, self.particle_effect.get_width(), self.particle_effect.get_height()
        )

        if self.is_facing_right:
            self.particle_effect_rect.topleft = vec(self.rect.bottomleft) - vec(self.particle_effect_rect.size)
        else:
            self.particle_effect = pygame.transform.flip(self.particle_effect, True, False)
            self.particle_effect_rect.topleft = vec(self.rect.bottomright) - vec(0, self.particle_effect_rect.height)

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
                if self.is_facing_right:
                    self.is_facing_right = False
                    self.frame_index = 0
            elif direction == Direction.RIGHT:
                if not self.can_move_left:
                    self.can_move_left = True
                self.direction.x = 1
                if not self.is_facing_right:
                    self.frame_index = 0
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
            self.animation_functions['jump'](self.rect.midbottom + vec(0, 9))
            self.jumps_left = self.jumps_left -1 if self.can_double_jump else 0
            self.frame_index = 0
            self.play_soundeffect('jump')
    
    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y
    
    def check_for_horizontal_collisions(self):
        collision_detected = False
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if self.direction.x > 0:
                    if self.direction.y == 0 or (
                        abs(self.rect.right - sprite.rect.left) < min(
                            abs(sprite.rect.bottom - self.rect.top),
                            abs(self.rect.bottom - sprite.rect.top)
                        )
                    ):
                        self.rect.right = sprite.rect.left
                        self.touching_right_wall = True
                        self.h_collision_x = self.rect.right
                        collision_detected = True
                        break
                elif self.direction.x < 0:
                    if self.direction.y == 0 or (
                        abs(sprite.rect.right - self.rect.left) < min(
                            abs(sprite.rect.bottom - self.rect.top),
                            abs(self.rect.bottom - sprite.rect.top)
                        )
                    ):
                        self.rect.left = sprite.rect.right
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
        
    def check_for_vertical_collisions(self):
        self.touching_ground = False
        self.touching_ceiling = False

        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if self.direction.y > 0:
                    self.rect.bottom = sprite.rect.top
                    self.is_airborn = False
                    self.init_jump_count()
                    self.touching_ground = True
                elif self.direction.y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.touching_ceiling = True
                self.direction.y = 0
    
    def init_jump_count(self):
        self.jumps_left = 2
    
    def update_state(self):
        if self.direction.y == 0 and self.state == PlayerState.FALL:
            self.state = PlayerState.LAND
            self.frame_index = 0
            self.animation_functions['land'](self.rect.midbottom + vec(0, -18))
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

    def take_damage(self, damage):
        if not self.is_invincible:
            self.health_bar.sprite.take_damage(damage)
            self.is_invincible = True
            self.invincibility_start_time = pygame.time.get_ticks()
            self.invincibility_duration = self.invincibility_after_damage
            self.play_soundeffect('hit')
            if self.health_bar.sprite.current_health <= 0:
                self.state = PlayerState.DEAD_HIT
                self.is_dead = True
                self.frame_index = 0
    
    def heal(self, value):
        self.health_bar.sprite.heal(value)
    
    def get_invincibility_remaining_duration(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.invincibility_start_time 
    
    def reset_buffs(self):
        self.is_invincible = False
        self.invincibility_start_time = -1

    def update(self):

        if self.is_dead or self.level_completed:
            self.reset_buffs()
            self.apply_gravity()
            self.check_for_vertical_collisions()
            self.animate()
            self.animate_particles()
            return

        # Get input
        self.get_input()
        self.run()

        # Update stats
        self.health_bar.update()
        if self.is_invincible:
            if self.get_invincibility_remaining_duration() >= self.invincibility_duration:
                self.is_invincible = False
                self.invincibility_start_time = -1

        # Horizontal collisions
        self.check_for_horizontal_collisions()
        
        self.apply_gravity()
        # Vertical collisions
        self.check_for_vertical_collisions()
        
        # Animations
        self.update_state()
        self.animate()
        self.animate_particles()
    
    def collect_coin(self, type):
        if type == 'gold':
            self.gold_coins += 1
        elif type == 'silver':
            self.silver_coins += 1

    def draw(self, new_rect=None):
        
        rect = new_rect if new_rect else self.rect
        offset = vec(self.rect.topleft) - vec(new_rect.topleft)
        if self.is_dead:
            rect.top += 5
        particle_pos = vec(self.particle_effect_rect.topleft) - offset
        if self.is_facing_right or self.state in [PlayerState.JUMP, PlayerState.DEAD_HIT, PlayerState.DEAD_GROUND]:
            pos = (rect.left, rect.bottom - self.image.get_height())
        else:
            pos = (rect.left + self.image.get_width() - 100, rect.bottom - self.image.get_height())
        opacity = (1 + sin(self.get_invincibility_remaining_duration())) * 256 / 2 if self.is_invincible else 255
        self.image.set_alpha(opacity)
        self.display_surface.blit(self.image, pos)
        if self.state == PlayerState.RUN:
            self.display_surface.blit(self.particle_effect, particle_pos)

class HatTile(Tile):

    def __init__(self, pos, groups):
        super().__init__(pos, groups)
        self.image = pygame.image.load(path.join(BASE_DIR, "graphics", "character", "hat.png")).convert_alpha()
        pos = (
            pos[0] + int(TILE_SIZE / 2) - (self.image.get_width() / 2),
            pos[1] + int(TILE_SIZE / 2) - (self.image.get_height() / 2)
        )
        self.rect = self.image.get_rect(center=pos)
