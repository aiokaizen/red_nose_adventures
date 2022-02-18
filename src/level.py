import pygame
from camera import CameraGroup
from tile import *
from player import Player
from settings import *
from particles import ParticleEffect
from tools import (
    ParticleEffectType, debug, draw_outline, import_csv_layout, update_layout_exclude,
    update_layout_to_only_contain
)
from decoration import Clouds, Sky, Water
from enemy import Enemy, EnemyConstraint
from tools import get_level_data
from ui import CoinsIndicator, HealthBar


class Level:

    def __init__(self, stats, show_menu):
        level_data = get_level_data(stats.current_level)
        self.display_surface = pygame.display.get_surface()
        self.level_data = level_data
        self.show_menu = show_menu
        self.stats = stats
        self.next_level = self.stats.current_level + 1
        self.coins_indicator = CoinsIndicator(self.display_surface)
        self.is_input_disabled = False
        self.level_completed = False
        self.pause_timer_start = 0
        self.pause_timer_duration = 2000
        
        tmp_layout = import_csv_layout(level_data['player'])
        self.level_rect = pygame.Rect(
            0, 0, len(tmp_layout[0]) * TILE_SIZE, len(tmp_layout) * TILE_SIZE
        )

        # Groups
        self.visible_sprites = CameraGroup(self.level_rect)  # Visible sprites
        self.active_sprites = pygame.sprite.Group()  # Updatable sprites
        self.collision_sprites = pygame.sprite.Group()  # Collision sprites
        self.collectible_sprites = pygame.sprite.Group()  # Collectibles like potions, coins, ...
        self.invisible_sprites = pygame.sprite.Group()  # Invisible sprites (Hidden objects, and enemeies constraints)
        self.enemies = pygame.sprite.Group()  # Collision sprites
        # self.particle_effects = pygame.sprite.Group()  # Particle effects sprites

        self.setup_level()
    
        # Audio
        self.soundeffects = {
            'collect_coin': pygame.mixer.Sound(os.path.join(BASE_DIR, 'audio', 'effects', 'coin.wav')),
            'stomp': pygame.mixer.Sound(os.path.join(BASE_DIR, 'audio', 'effects', 'stomp.wav')),
        }

    def play_soundeffect(self, soundeffect, volume=0.05):
        sound: pygame.mixer.Sound = self.soundeffects[soundeffect]
        sound.set_volume(volume)
        sound.play()
    
    def get_bg_terrain_tile_ids(self):
        return [
            '13',
            '4', '5', '6', '7', '8', '9', '10',
            '16', '17', '18', '19', '20', '21', '22', '23'
        ]
 
    def setup_level(self):

        self.sky = Sky(horizon=5)
        self.water = Water(35, self.level_rect.width)
        self.clouds = Clouds(8, self.level_rect.width, 20)

        # Setup UI
        self.setup_ui()

        bg_palms_layout = import_csv_layout(self.level_data['bg_palms'])
        self.create_sprites_from_layout(bg_palms_layout, 'bg_palms', [self.visible_sprites, self.active_sprites])

        terrain_layout = import_csv_layout(self.level_data['terrain'])
        bg_terrain2_layout = import_csv_layout(self.level_data['bg_terrain'])
        self.create_sprites_from_layout(bg_terrain2_layout, 'bg_terrain', [self.visible_sprites])

        bg_terrain_layout = update_layout_to_only_contain(terrain_layout, self.get_bg_terrain_tile_ids())
        self.create_sprites_from_layout(bg_terrain_layout, 'bg_terrain', [self.visible_sprites])

        collidable_terrain_layout = update_layout_exclude(terrain_layout, self.get_bg_terrain_tile_ids())
        self.create_sprites_from_layout(collidable_terrain_layout, 'terrain', [self.visible_sprites, self.collision_sprites])

        crates_layout = import_csv_layout(self.level_data['crates'])
        self.create_sprites_from_layout(crates_layout, 'crates', [self.visible_sprites])

        grass_layout = import_csv_layout(self.level_data['grass'])
        self.create_sprites_from_layout(grass_layout, 'grass', [self.visible_sprites])

        coins_layout = import_csv_layout(self.level_data['coins'])
        self.create_sprites_from_layout(coins_layout, 'coins', [self.visible_sprites, self.active_sprites, self.collectible_sprites])

        spikes_layout = import_csv_layout(self.level_data['spikes'])
        self.create_sprites_from_layout(
            spikes_layout, 'spikes', [self.visible_sprites, self.enemies]
        )

        enemies_constraints_layout = import_csv_layout(self.level_data['enemies_constraints'])
        self.create_sprites_from_layout(
            enemies_constraints_layout, 'enemies_constraints', [self.invisible_sprites]
        )

        enemies_layout = import_csv_layout(self.level_data['enemies'])
        self.create_sprites_from_layout(
            enemies_layout, 'enemies',
            [self.visible_sprites, self.active_sprites, self.enemies]
        )

        fg_palms_layout = import_csv_layout(self.level_data['fg_palms'])
        self.create_sprites_from_layout(fg_palms_layout, 'fg_palms', [self.visible_sprites, self.active_sprites, self.collision_sprites])

        player_layout = import_csv_layout(self.level_data['player'])
        self.setup_player(player_layout)

        self.visible_sprites.set_target(self.player)
    
    def setup_ui(self):
        self.health_bar = pygame.sprite.GroupSingle(
            HealthBar(self.stats.health, self.stats.max_health, self.display_surface)
        )
     
    def setup_player(self, layout):

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
                        self.player = Player(
                            (x, y),
                            [self.active_sprites],
                            self.collision_sprites,
                            self.health_bar, self.display_surface, player_animations
                        )
                    else:
                        self.target = FlagTile(
                            (x, y), [self.visible_sprites, self.active_sprites]
                        )
        # Adding player to visible sprites late to show it on top
        # of the target sprite
        self.visible_sprites.add(self.player)
    
    def create_sprites_from_layout(self, layout, layout_type, groups):

        for i, row in enumerate(layout):
            for j, cell in enumerate(row):
                cell = int(cell)
                if cell != -1:
                    x, y = j * TILE_SIZE, i * TILE_SIZE
                    if layout_type == 'water':
                        WaterTile((x, y), groups)
                    elif layout_type in ['terrain', 'bg_terrain', 'bg_terrain2']:
                        TerrainTile((x, y), groups, cell)
                    elif layout_type == 'grass':
                        GrassTile((x, y), groups, cell)
                    elif layout_type == 'coins':
                        CoinTile((x, y), groups, cell)
                    elif layout_type in ['fg_palms', 'bg_palms']:
                        PalmTile((x, y), groups, cell)
                    elif layout_type in ['crates']:
                        CrateTile((x, y), groups, cell)
                    elif layout_type == 'enemies':
                        enemies_constraints_group = pygame.sprite.Group([
                            sprite for sprite in self.invisible_sprites.sprites() if sprite.__class__ == EnemyConstraint
                        ])
                        Enemy((x, y), groups, enemies_constraints_group)
                    elif layout_type == 'enemies_constraints':
                        EnemyConstraint((x, y), groups)
                    elif layout_type == 'spikes':
                        SpikesTile((x, y), groups)
         
    def create_coin_collect_animation(self, pos):
        coin_animation = ParticleEffect(pos, [], ParticleEffectType.COLLECT_COIN)
        self.visible_sprites.add(coin_animation)
        self.active_sprites.add(coin_animation)

    def create_jump_animation(self, pos):
        jump_particle_sprite = ParticleEffect(pos, [], ParticleEffectType.JUMP)
        self.visible_sprites.add(jump_particle_sprite)
        self.active_sprites.add(jump_particle_sprite)
    
    def create_land_animation(self, pos):
        land_particle_sprite = ParticleEffect(pos, [], ParticleEffectType.LAND)
        self.visible_sprites.add(land_particle_sprite)
        self.active_sprites.add(land_particle_sprite)
   
    def create_explosion_animation(self, pos):
        explosion_particle_sprite = ParticleEffect(pos, [], ParticleEffectType.EXPLOSION)
        self.visible_sprites.add(explosion_particle_sprite)
        self.active_sprites.add(explosion_particle_sprite)
    
    def draw(self):

        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface)
        self.water.draw(self.display_surface)

        self.visible_sprites.draw()
        
        self.health_bar.sprite.draw()
        self.coins_indicator.draw()
    
    def draw_outlines(self):
        outlined_sprites = set(
            self.player,
            self.target,
            *self.collision_sprites.sprites(),
            *self.enemies.sprites(),
            *self.invisible_sprites.sprites(),
        )
        for sprite in outlined_sprites:
            draw_outline(self.display_surface, sprite)

    def display_menu(self, is_completed):
        next_level = self.next_level if is_completed else self.stats.current_level
        navigate_to = self.next_level if is_completed else -1
        pygame.mixer.music.unload()
        self.show_menu(next_level, navigate_to)
    
    def kill_enemy(self, enemy):
        enemy.kill()
        self.create_explosion_animation(enemy.rect.center)
        self.player.direction.y = -15
    
    def check_if_completed(self):
        """Checks if the player reached the goal."""
        if pygame.sprite.collide_rect(self.player, self.target):
            self.prepare_to_pause()
            self.level_completed = True
            self.player.set_level_completed()
            self.target.start_transition()
        
    def check_if_player_is_dead(self):
        """Checks if the player is dead."""
        if (
            self.player.rect.bottom > SCREEN_HEIGHT or
            self.player.health_bar.sprite.current_health <= 0
        ):
            self.prepare_to_pause()
    
    def check_spike_collision(self):
        if self.player.is_dead:
            return
        spikes = [sprite for sprite in self.visible_sprites.sprites() if sprite.__class__ == SpikesTile]
        for spike in spikes:
            if self.player.rect.colliderect(spike.collide_rect):
                self.player.take_damage(spike.damage)
                self.player.direction.x *= -1
                self.player.direction.y = -12
    
    def check_enemy_collision(self):
        if self.player.is_dead:
            return
        enemies = [sprite for sprite in self.visible_sprites.sprites() if sprite.__class__ == Enemy]
        for enemy in enemies:
            if self.player.rect.colliderect(enemy.rect):
                player_rect = self.player.rect
                enemy_rect = enemy.rect
                if self.player.direction.x > 0 or enemy.direction.x < 0:
                    if self.player.direction.y == 0 or (
                        abs(player_rect.right - enemy_rect.left) < abs(player_rect.bottom - enemy_rect.top)
                    ):
                        self.player.take_damage(enemy.damage)
                    elif self.player.direction.y < 0:
                        self.player.take_damage(enemy.damage)
                    else:
                        self.kill_enemy(enemy)
                        self.play_soundeffect('stomp')
                elif self.player.direction.x < 0 or enemy.direction.x > 0:
                    if self.player.direction.y == 0 or (
                        abs(enemy_rect.right - player_rect.left) < abs(player_rect.bottom - enemy_rect.top)
                    ):
                        self.player.take_damage(enemy.damage)
                    elif self.player.direction.y < 0:
                        self.player.take_damage(enemy.damage)
                    else:
                        self.kill_enemy(enemy)
                        self.play_soundeffect('stomp')
    
    def check_coin_collision(self):
        if self.player.is_dead:
            return
        coins = [sprite for sprite in self.collectible_sprites.sprites() if sprite.__class__ == CoinTile]
        for coin in coins:
            if self.player.rect.colliderect(coin.rect):
                self.player.collect_coin(coin.type)
                self.coins_indicator.add_coin(coin.type)
                self.play_soundeffect('collect_coin')
                self.create_coin_collect_animation(coin.rect.center)
                coin.kill()
    
    def prepare_to_pause(self):
        self.pause_timer_start = pygame.time.get_ticks()
        self.is_input_disabled = True

    def pause(self):
        self.stats.gold_coins = self.coins_indicator.gold_coins
        self.stats.silver_coins = self.coins_indicator.silver_coins
        self.display_menu(False)
    
    def run(self):

        # Draw
        self.draw()
        if DEBUG is True:
            self.draw_outlines()
        
        if self.is_input_disabled and self.pause_timer_start > -1:
            if pygame.time.get_ticks() - self.pause_timer_start >= self.pause_timer_duration:
                self.pause()
                self.pause_timer_start = -1

        if not self.is_input_disabled:
            self.check_spike_collision()
            self.check_enemy_collision()
            self.check_coin_collision()
            self.check_if_completed()
            self.check_if_player_is_dead()

            # Update UI
            self.health_bar.update()

        # Update active sprites
        self.active_sprites.update()

