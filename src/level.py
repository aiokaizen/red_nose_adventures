import pygame
from camera import CameraGroup
from tile import *
from player import HatTile, Player
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

    def __init__(self, stats, surface: pygame.Surface, show_menu):
        level_data = get_level_data(stats.current_level)
        self.display_surface = surface
        self.level_data = level_data
        self.first_sprite = None
        self.last_sprite = None
        self.show_menu = show_menu
        self.stats = stats
        self.next_level = self.stats.current_level + 1
        self.coins_indicator = CoinsIndicator(self.display_surface)
        self.is_paused = False

        tmp_layout = import_csv_layout(level_data['player'])
        self.level_rect = pygame.Rect(
            0, 0, len(tmp_layout[0]) * TILE_SIZE, len(tmp_layout) * TILE_SIZE
        )

        self.setup_level()

        # Particle effects
        self.particle_effects = CameraGroup(self.player_group.sprites()[0], self.level_rect)
    
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

        self.world_sprites = {}
        terrain_layout = import_csv_layout(self.level_data['terrain'])

        self.sky = Sky(horizon=8)
        world_width = len(terrain_layout[0]) * TILE_SIZE
        self.water = Water(35, world_width)
        self.clouds = Clouds(9, world_width, 20)

        # Setup UI
        self.setup_ui()

        player_layout = import_csv_layout(self.level_data['player'])
        self.player_group = self.setup_player(player_layout)
    
        bg_palms_layout = import_csv_layout(self.level_data['bg_palms'])
        self.world_sprites['bg_palms'] = self.create_tile_group(bg_palms_layout, 'bg_palms')

        bg_terrain2_layout = import_csv_layout(self.level_data['bg_terrain'])
        self.world_sprites['bg_terrain2'] = self.create_tile_group(bg_terrain2_layout, 'bg_terrain')
        bg_terrain_layout = update_layout_to_only_contain(terrain_layout, self.get_bg_terrain_tile_ids())
        self.world_sprites['bg_terrain'] = self.create_tile_group(bg_terrain_layout, 'bg_terrain')
        collidable_terrain_layout = update_layout_exclude(terrain_layout, self.get_bg_terrain_tile_ids())
        self.world_sprites['terrain'] = self.create_tile_group(collidable_terrain_layout, 'terrain')

        crates_layout = import_csv_layout(self.level_data['crates'])
        self.world_sprites['crates'] = self.create_tile_group(crates_layout, 'crates')

        grass_layout = import_csv_layout(self.level_data['grass'])
        self.world_sprites['grass'] = self.create_tile_group(grass_layout, 'grass')

        coins_layout = import_csv_layout(self.level_data['coins'])
        self.world_sprites['coins'] = self.create_tile_group(coins_layout, 'coins')

        enemies_constraints_layout = import_csv_layout(self.level_data['enemies_constraints'])
        self.world_sprites['enemies_constraints'] = self.create_tile_group(
            enemies_constraints_layout, 'enemies_constraints'
        )

        spikes_layout = import_csv_layout(self.level_data['spikes'])
        self.world_sprites['spikes'] = self.create_tile_group(spikes_layout, 'spikes')

        enemies_layout = import_csv_layout(self.level_data['enemies'])
        self.enemies = self.create_tile_group(enemies_layout, 'enemies')

        fg_palms_layout = import_csv_layout(self.level_data['fg_palms'])
        self.world_sprites['fg_palms'] = self.create_tile_group(fg_palms_layout, 'fg_palms')

    def setup_ui(self):
        self.health_bar = pygame.sprite.GroupSingle(
            HealthBar(self.stats.health, self.stats.max_health, self.display_surface)
        )
     
    def setup_player(self, layout):

        player_sprite = None
        flag_sprite = None

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
                        player_sprite = Player((x, y), self.health_bar, self.display_surface, player_animations)
                    else:
                        flag_sprite = FlagTile((x, y))
        player_grp = CameraGroup(player_sprite, self.level_rect)
        player_grp.add(player_sprite, flag_sprite)
        return player_grp
    
    def create_tile_group(self, layout, layout_type):

        sprite_group = CameraGroup(self.player_group.sprites()[0], self.level_rect)
        for i, row in enumerate(layout):
            for j, cell in enumerate(row):
                cell = int(cell)
                if cell != -1:
                    x, y = j * TILE_SIZE, i * TILE_SIZE
                    if layout_type == 'water':
                        sprite = WaterTile((x, y))
                    elif layout_type in ['terrain', 'bg_terrain', 'bg_terrain2']:
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
                    elif layout_type == 'spikes':
                        sprite = SpikesTile((x, y))

                    if not self.first_sprite and not self.last_sprite:
                        self.first_sprite = sprite
                        self.last_sprite = sprite
                    elif self.first_sprite.rect > sprite.rect:
                        self.first_sprite = sprite
                    elif self.last_sprite.rect < sprite.rect:
                        self.last_sprite = sprite
                    sprite_group.add(sprite)

        return sprite_group
         
    def create_coin_collect_animation(self, pos):
        coin_animation = ParticleEffect(pos, ParticleEffectType.COLLECT_COIN)
        self.particle_effects.add(coin_animation)

    def create_jump_animation(self, pos):
        jump_particle_sprite = ParticleEffect(pos, ParticleEffectType.JUMP)
        self.particle_effects.add(jump_particle_sprite)
    
    def create_land_animation(self, pos):
        land_particle_sprite = ParticleEffect(pos, ParticleEffectType.LAND)
        self.particle_effects.add(land_particle_sprite)
   
    def create_explosion_animation(self, pos):
        explosion_particle_sprite = ParticleEffect(pos, ParticleEffectType.EXPLOSION)
        self.particle_effects.add(explosion_particle_sprite)
    
    def draw(self):

        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface)

        self.water.draw(self.display_surface)

        for type, sprites in self.world_sprites.items():
            if type not in ['enemies_constraints']:
                sprites.draw()
        
        self.enemies.draw()

        self.player_group.draw()

        self.particle_effects.draw()

        self.health_bar.sprite.draw()
        self.coins_indicator.draw()
    
    def draw_outlines(self):
        for type, sprites in self.world_sprites.items():
            if type not in ['bg_terrain', 'crates', 'grass', 'coins', 'enemies', 'bg_palms', 'enemies_constraints']:
                for sprite in sprites.sprites():
                    draw_outline(self.display_surface, sprite)
        
        for enemy in self.enemies.sprites():
            draw_outline(self.display_surface, enemy)

        draw_outline(self.display_surface, self.player_group.sprites()[0])
        draw_outline(self.display_surface, self.player_group.sprites()[1])
    
    def display_menu(self, is_completed):
        next_level = self.next_level if is_completed else self.stats.current_level
        navigate_to = self.next_level if is_completed else -1
        pygame.mixer.music.unload()
        self.show_menu(next_level, navigate_to)
    
    def kill_enemy(self, enemy):
        enemy.kill()
        self.create_explosion_animation(enemy.rect.center)
        self.player_group.sprites()[0].direction.y = -15
    
    def check_if_completed(self):
        """Checks if the player reached the goal."""
        if pygame.sprite.collide_rect(self.player_group.sprites()[0], self.player_group.sprites()[1]):
            self.pause()
            self.display_menu(True)
        
    def check_if_player_is_dead(self):
        """Checks if the player is dead."""
        if (
            self.player_group.sprites()[0].rect.bottom > SCREEN_HEIGHT or
            self.player_group.sprites()[0].health_bar.sprite.current_health <= 0
        ):
            self.pause()
            self.display_menu(False)
    
    def check_spike_collision(self):
        for spike in self.world_sprites['spikes'].sprites():
            if self.player_group.sprites()[0].rect.colliderect(spike.collide_rect):
                self.player_group.sprites()[0].take_damage(spike.damage)
                self.player_group.sprites()[0].direction.x *= -1
                self.player_group.sprites()[0].direction.y = -12
    
    def check_enemy_collision(self):
        for enemy in self.enemies.sprites():
            if self.player_group.sprites()[0].rect.colliderect(enemy.rect):
                player_rect = self.player_group.sprites()[0].rect
                enemy_rect = enemy.rect
                if self.player_group.sprites()[0].direction.x > 0 or enemy.direction.x < 0:
                    if self.player_group.sprites()[0].direction.y == 0 or (
                        abs(player_rect.right - enemy_rect.left) < abs(player_rect.bottom - enemy_rect.top)
                    ):
                        self.player_group.sprites()[0].take_damage(enemy.damage)
                    elif self.player_group.sprites()[0].direction.y < 0:
                        self.player_group.sprites()[0].take_damage(enemy.damage)
                    else:
                        self.kill_enemy(enemy)
                        self.play_soundeffect('stomp')
                elif self.player_group.sprites()[0].direction.x < 0 or enemy.direction.x > 0:
                    if self.player_group.sprites()[0].direction.y == 0 or (
                        abs(enemy_rect.right - player_rect.left) < abs(player_rect.bottom - enemy_rect.top)
                    ):
                        self.player_group.sprites()[0].take_damage(enemy.damage)
                    elif self.player_group.sprites()[0].direction.y < 0:
                        self.player_group.sprites()[0].take_damage(enemy.damage)
                    else:
                        self.kill_enemy(enemy)
                        self.play_soundeffect('stomp')
    
    def check_coin_collision(self):
        for coin in self.world_sprites['coins'].sprites():
            if self.player_group.sprites()[0].rect.colliderect(coin.rect):
                self.player_group.sprites()[0].collect_coin(coin.type)
                self.coins_indicator.add_coin(coin.type)
                self.play_soundeffect('collect_coin')
                self.create_coin_collect_animation(coin.rect.center)
                coin.kill()
    
    def pause(self):
        self.stats.gold_coins = self.coins_indicator.gold_coins
        self.stats.silver_coins = self.coins_indicator.silver_coins
        self.is_paused = True
    
    def run(self):

        # Draw
        self.draw()
        if DEBUG is True:
            self.draw_outlines()

        # Pause the game
        if self.is_paused:
            return

        # Player sprite
        self.player_group.sprites()[0].update(self.world_sprites)
        self.player_group.sprites()[1].update()

        # Enemies spries
        self.enemies.update(self.world_sprites['enemies_constraints'])

        # Particles
        self.particle_effects.update()

        # Level tiles
        for sprites in self.world_sprites.values():
            sprites.update()

        self.check_spike_collision()
        self.check_enemy_collision()
        self.check_coin_collision()
        self.check_if_completed()
        self.check_if_player_is_dead()

        # Update UI
        self.health_bar.update()
