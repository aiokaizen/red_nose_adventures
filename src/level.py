import pygame
from tile import *
from player import HatTile, Player
from settings import *
from particles import ParticleEffect
from tools import ParticleEffectType, draw_outline, import_csv_layout, update_layout_exclude, update_layout_to_only_contain
from decoration import Clouds, Sky, Water
from enemy import Enemy, EnemyConstraint


class Level:

    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.level_data = level_data
        self.shift_speed = 0
        self.first_sprite = None
        self.last_sprite = None

        # Particle effects
        self.particle_effects = pygame.sprite.Group()

        self.setup_level()
        self.change_view('player')
        
    def create_jump_animation(self, pos):
        jump_particle_sprite = ParticleEffect(pos, ParticleEffectType.JUMP)
        self.particle_effects.add(jump_particle_sprite)
    
    def create_land_animation(self, pos):
        land_particle_sprite = ParticleEffect(pos, ParticleEffectType.LAND)
        self.particle_effects.add(land_particle_sprite)
    
    def setup_player(self, layout):

        player_grp = pygame.sprite.GroupSingle()
        goal_grp = pygame.sprite.GroupSingle()

        for i, row in enumerate(layout):
            for j, cell in enumerate(row):
                cell = int(cell)
                if cell in [0, 1]:
                    x, y = j * TILE_SIZE, i * TILE_SIZE
                    if cell == 0:
                        player_animations = {
                            'jump': self.create_jump_animation,
                            'land': self.create_land_animation
                        }
                        sprite = Player((x, y), self.display_surface, player_animations)
                        player_grp.add(sprite)
                    else:
                        sprite = HatTile((x, y))
                        goal_grp.add(sprite)
        
        return player_grp, goal_grp
    
    def create_tile_group(self, layout, layout_type):

        sprite_group = pygame.sprite.Group()
        for i, row in enumerate(layout):
            for j, cell in enumerate(row):
                cell = int(cell)
                if cell != -1:
                    x, y = j * TILE_SIZE, i * TILE_SIZE
                    if layout_type == 'water':
                        sprite = WaterTile((x, y))
                    elif layout_type == 'terrain':
                        sprite = TerrainTile((x, y), cell)
                    elif layout_type == 'bg_terrain':
                        sprite = TerrainTile((x, y), cell)
                    elif layout_type == 'grass':
                        sprite = GrassTile((x, y), cell)
                    elif layout_type == 'coins':
                        sprite = CoinTile((x, y), cell)
                    elif layout_type in ['fg_palms', 'bg_palms']:
                        sprite = PalmTile((x, y), cell)
                    elif layout_type in ['crates']:
                        sprite = CrateTile((x, y), cell)
                    elif layout_type == 'enemies':
                        sprite = Enemy((x, y))
                    elif layout_type == 'enemies_constraints':
                        sprite = EnemyConstraint((x, y))
                    elif layout_type == 'player':  # The last check is temporary
                        if cell == 0:
                            player_animations = {
                                'jump': self.create_jump_animation,
                                'land': self.create_land_animation
                            }
                            sprite = Player((x, y), self.display_surface, player_animations)
                        else:
                            sprite = HatTile((x, y))
                        sprite_group = pygame.sprite.GroupSingle()
                    if not self.first_sprite and not self.last_sprite:
                        self.first_sprite = sprite
                        self.last_sprite = sprite
                    elif self.first_sprite.rect > sprite.rect:
                        self.first_sprite = sprite
                    elif self.last_sprite.rect < sprite.rect:
                        self.last_sprite = sprite
                    sprite_group.add(sprite)

        return sprite_group
    
    def setup_level(self):

        self.world_sprites = {}
        terrain_layout = import_csv_layout(self.level_data['terrain'])

        self.sky = Sky(horizon=8)
        world_width = len(terrain_layout[0]) * TILE_SIZE
        self.water = Water(35, world_width)
        self.clouds = Clouds(9, world_width, 20)

        bg_palms_layout = import_csv_layout(self.level_data['bg_palms'])
        self.world_sprites['bg_palms'] = self.create_tile_group(bg_palms_layout, 'bg_palms')

        collidable_terrain_layout = update_layout_exclude(terrain_layout, ['5'])
        self.world_sprites['terrain'] = self.create_tile_group(collidable_terrain_layout, 'terrain')
        bg_terrain_layout = update_layout_to_only_contain(terrain_layout, ['5'])
        self.world_sprites['bg_terrain'] = self.create_tile_group(bg_terrain_layout, 'bg_terrain')

        crates_layout = import_csv_layout(self.level_data['crates'])
        self.world_sprites['crates'] = self.create_tile_group(crates_layout, 'crates')

        grass_layout = import_csv_layout(self.level_data['grass'])
        self.world_sprites['grass'] = self.create_tile_group(grass_layout, 'grass')

        coins_layout = import_csv_layout(self.level_data['coins'])
        self.world_sprites['coins'] = self.create_tile_group(coins_layout, 'coins')

        fg_palms_layout = import_csv_layout(self.level_data['fg_palms'])
        self.world_sprites['fg_palms'] = self.create_tile_group(fg_palms_layout, 'fg_palms')

        enemies_constraints_layout = import_csv_layout(self.level_data['enemies_constraints'])
        self.world_sprites['enemies_constraints'] = self.create_tile_group(
            enemies_constraints_layout, 'enemies_constraints'
        )

        enemies_layout = import_csv_layout(self.level_data['enemies'])
        self.enemies = self.create_tile_group(enemies_layout, 'enemies')

        player_layout = import_csv_layout(self.level_data['player'])
        self.player, self.goal = self.setup_player(player_layout)
    
    def change_view(self, target):
        if target == "player":
            player_rect = self.player.sprite.rect
            while player_rect.centerx != SCREEN_WIDTH // 2:
                if player_rect.centerx > SCREEN_WIDTH // 2:
                    self.move_camera((-1, 0))
                else:
                    self.move_camera((1, 0))
                self.draw()
    
    def move_camera(self, shift):
        """ Manually moves the camera by a specific value(x, y)"""

        # Move world objects (Terrain, coins, palms, ...)
        for type, sprites in self.world_sprites.items():
            for tile in sprites.sprites():
                tile.rect.x += shift[0]
                tile.rect.y += shift[1]
        
        # Move the enemies
        for enemy in self.enemies.sprites():
            enemy.rect.x += shift[0]
            enemy.rect.y += shift[1]

        # Move the player
        self.player.sprite.rect.x += shift[0]
        self.player.sprite.rect.y += shift[1]

        # Move the goal
        self.goal.sprite.rect.x += shift[0]
        self.goal.sprite.rect.y += shift[1]
    
    def update_shift_speed(self):
        player = self.player.sprite
        player_rect = player.rect
        player_direction = player.direction
        player_h_speed = player.h_speed

        if player_rect.centerx > RIGHT_CAMERA_BORDER and player_direction.x > 0:
            self.shift_speed = -player_h_speed * player_direction.x
            player.can_move_right = False
        elif player_rect.centerx < LEFT_CAMERA_BORDER and player_direction.x < 0:
            self.shift_speed = -player_h_speed * player_direction.x
            player.can_move_left = False
        else:
            self.shift_speed = 0
    
    def draw(self):

        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.shift_speed)

        self.water.draw(self.display_surface, self.shift_speed)

        for type, sprites in self.world_sprites.items():
            if type not in ['enemies_constraints']:
                sprites.draw(self.display_surface)
        
        self.enemies.draw(self.display_surface)

        self.player.sprite.draw(self.display_surface)
        self.goal.draw(self.display_surface)

        self.particle_effects.draw(self.display_surface)
    
    def draw_outlines(self):
        for type, sprites in self.world_sprites.items():
            if type not in ['bg_terrain', 'crates', 'grass', 'coins', 'enemies', 'bg_palms', 'enemies_constraints']:
                for sprite in sprites.sprites():
                    draw_outline(self.display_surface, sprite)
        
        for enemy in self.enemies.sprites():
            draw_outline(self.display_surface, enemy)

        draw_outline(self.display_surface, self.player.sprite)
        draw_outline(self.display_surface, self.goal.sprite)
    
    def run(self):

        # Player sprite
        self.player.update(self.world_sprites)
        self.goal.update(self.shift_speed)

        # Enemies spries
        self.enemies.update(self.world_sprites['enemies_constraints'], self.shift_speed)

        # Particles
        self.particle_effects.update(self.shift_speed)

        # Level tiles
        self.update_shift_speed()
        for type, sprites in self.world_sprites.items():
            sprites.update(self.shift_speed)

        # Draw
        self.draw()
        if DEBUG is True:
            self.draw_outlines()
