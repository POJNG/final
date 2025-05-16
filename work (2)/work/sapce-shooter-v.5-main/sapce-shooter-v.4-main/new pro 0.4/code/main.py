# Space Shooter Game
# A 2D space shooter game with power-ups, enemies, and score tracking

import pygame
from os.path import join
import random
import math

# Initialize pygame and set up the game window
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space Shooter')
clock = pygame.time.Clock()

# Load game assets (images and sounds)
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

# Load and configure game sounds
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.1)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.01)

# Base sprite class that other game objects inherit from #mo3taz
class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000  # How long the sprite lives in milliseconds
        self.direction = pygame.Vector2(random.uniform(-0.5, 0.5), 1)  # Random movement direction

# Star class for background decoration
class Star(BaseSprite):
    def __init__(self, surf, groups):
        # Random position within the window
        pos = (random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))
        super().__init__(surf, pos, groups)

# Player class - the main character controlled by the user# kalid
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        # Load and set up player image
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        
        # Movement and shooting properties
        self.direction = pygame.Vector2()
        self.speed = 300
        self.can_shoot = True
        self.shoot_cooldown = 200
        self.last_shot = 0
        
        # Health and invincibility properties
        self.health = 3
        self.max_health = 5
        self.invincible = False
        self.invincible_time = 0
        self.invincible_duration = 0.5
        self.alive = True
        
        # Collision detection
        self.mask = pygame.mask.from_surface(self.image)
        
        # Power-up properties
        self.laser_mode = 'single'  # Can be 'single', 'double', or 'triple'
        self.power_up_time = 0
        self.power_up_duration = 20000
        self.has_power_up = False
        self.kill_count = 0
        self.kills_for_power_up = 3

    def update(self, dt):
        if not self.alive:
            return

        # Handle player movement
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction

        # Update position with boundary checking
        new_pos = self.rect.center + self.direction * self.speed * dt
        new_pos.x = max(0, min(new_pos.x, WINDOW_WIDTH))
        new_pos.y = max(0, min(new_pos.y, WINDOW_HEIGHT))
        self.rect.center = new_pos

        # Handle shooting cooldown
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_cooldown:
            self.can_shoot = True

        # Handle invincibility
        if self.invincible and current_time - self.invincible_time > self.invincible_duration:
            self.invincible = False

        # Handle power-up duration
        if self.has_power_up and current_time - self.power_up_time > self.power_up_duration:
            self.laser_mode = 'single'
            self.has_power_up = False

    def apply_power_up(self, power_up_type):
        current_time = pygame.time.get_ticks()
        self.power_up_time = current_time
        self.has_power_up = True
        
        # Apply different power-up effects
        if power_up_type == 'health':
            self.health = min(self.health + 1, self.max_health)
        elif power_up_type == 'double_laser':
            self.laser_mode = 'double'
        elif power_up_type == 'triple_laser':
            self.laser_mode = 'triple'

# Laser Class# khalid
class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)
        self.speed = 400

    def update(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill()

# Enemy Laser Class# yuif
class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, pos, angle, groups):
        super().__init__(groups)
        # Create a more visible laser
        self.image = pygame.Surface((12, 40), pygame.SRCALPHA)
        # Create a glowing effect
        for i in range(40):
            alpha = int(255 * (1 - i/40))
            color = (255, 200, 0, alpha)
            pygame.draw.line(self.image, color, (6, i), (6, i+1), 6)
            if i < 20:
                pygame.draw.line(self.image, (255, 255, 255, alpha), (6, i), (6, i+1), 3)
        
        self.rect = self.image.get_frect(center=pos)
        self.speed = 1000
        self.direction = pygame.Vector2()
        self.direction.from_polar((1, angle))
        self.rotation = angle
        self.image = pygame.transform.rotate(self.image, angle)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if (self.rect.right < 0 or self.rect.left > WINDOW_WIDTH or
            self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT):
            self.kill()

# Shooting Enemy Ship  # khalid
class ShootingEnemyShip(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player):
        super().__init__(groups)
        original_image = pygame.image.load(join('images', 'enemy_space_ship.png')).convert_alpha()
        scale_factor = 0.3
        self.image = pygame.transform.scale(original_image, 
            (int(original_image.get_width() * scale_factor), 
             int(original_image.get_height() * scale_factor)))
        self.original_surf = self.image.copy()
        self.rect = self.image.get_frect(center=pos)
        self.speed = 250
        self.direction = pygame.Vector2()
        self.direction.from_polar((1, 0))
        self.health = 3
        self.player = player
        self.can_shoot = True
        self.shoot_cooldown = 1200
        self.last_shot = pygame.time.get_ticks()
        self.mask = pygame.mask.from_surface(self.image)
        self.moving_right = True
        self.vertical_speed = 70
        self.last_player_pos = pygame.Vector2(player.rect.center)
        self.player_velocity = pygame.Vector2(0, 0)
        self.movement_state = 'horizontal'
        self.horizontal_distance = 0
        self.max_horizontal_distance = 250
        self.vertical_distance = 0
        self.max_vertical_distance = 40
        self.zigzag_amplitude = 120
        self.zigzag_frequency = 2.5
        self.time = 0
        self.charge_speed = 500
        self.is_charging = False
        self.charge_cooldown = 2500
        self.last_charge = pygame.time.get_ticks()
        self.charge_duration = 800
        self.charge_start_time = 0

    def update(self, dt):
        self.time += dt
        current_time = pygame.time.get_ticks()

        # Update player velocity tracking
        current_pos = pygame.Vector2(self.player.rect.center)
        self.player_velocity = (current_pos - self.last_player_pos) / dt if dt > 0 else pygame.Vector2(0, 0)
        self.last_player_pos = current_pos

        # Check if we should start charging
        if not self.is_charging and current_time - self.last_charge > self.charge_cooldown:
            self.is_charging = True
            self.charge_start_time = current_time
            # Calculate direction to player
            self.direction = (pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)).normalize()

        # Handle charging movement
        if self.is_charging:
            if current_time - self.charge_start_time < self.charge_duration:
                self.rect.center += self.direction * self.charge_speed * dt
            else:
                self.is_charging = False
                self.last_charge = current_time

        # Normal movement when not charging
        if not self.is_charging:
            if self.movement_state == 'horizontal':
                # Add zigzag movement
                zigzag_offset = math.sin(self.time * self.zigzag_frequency) * self.zigzag_amplitude
                
                if self.moving_right:
                    self.rect.x += self.speed * dt
                    self.rect.y += zigzag_offset * dt
                    self.horizontal_distance += self.speed * dt
                else:
                    self.rect.x -= self.speed * dt
                    self.rect.y += zigzag_offset * dt
                    self.horizontal_distance += self.speed * dt

                if self.horizontal_distance >= self.max_horizontal_distance:
                    self.movement_state = 'vertical'
                    self.horizontal_distance = 0
                    self.moving_right = not self.moving_right

            elif self.movement_state == 'vertical':
                self.rect.y += self.vertical_speed * dt
                self.vertical_distance += self.vertical_speed * dt

                if self.vertical_distance >= self.max_vertical_distance:
                    self.movement_state = 'horizontal'
                    self.vertical_distance = 0

        # Shooting logic
        if current_time - self.last_shot > self.shoot_cooldown and self.player.alive and not self.is_charging:
            if self.rect.centery < self.player.rect.centery:
                self.shoot()
                self.last_shot = current_time

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

        # Check collision with player
        if not self.player.invincible and self.player.alive:
            if pygame.sprite.collide_mask(self, self.player):
                self.player.health -= 2  # Deal 2 damage on collision
                self.player.invincible = True
                self.player.invincible_time = pygame.time.get_ticks()
                AnimatedExplosion(explosion_frames, self.rect.center, all_sprites)
                self.kill()

    def shoot(self):
        # Calculate time to reach player
        distance = pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)
        time_to_reach = distance.length() / 800

        # Predict player position
        predicted_pos = pygame.Vector2(self.player.rect.center)
        if self.player_velocity.length() > 0:
            predicted_pos += self.player_velocity * time_to_reach

        # Calculate angle to predicted position
        dx = predicted_pos.x - self.rect.centerx
        dy = predicted_pos.y - self.rect.centery
        angle = math.degrees(math.atan2(-dy, dx)) - 90

        # Add slight random spread
        spread = random.uniform(-3, 3)  # Reduced spread for better accuracy
        angle += spread

        EnemyLaser(self.rect.center, angle, (all_sprites, enemy_laser_sprites))

# Meteor Class # abod
class Meteor(BaseSprite):
    def __init__(self, surf, pos, groups):
        super().__init__(surf, pos, groups)
        speed_multiplier = min(1 + (difficulty - 1) * 0.3, 2.5)
        self.speed = random.randint(int(base_meteor_speed * speed_multiplier),
                                    int(max_meteor_speed * speed_multiplier))
        self.rotation_speed = random.randint(30, 50)
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center=self.rect.center)

# PowerUp Class # abod
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.types = ['health', 'double_laser', 'triple_laser']
        self.type = random.choice(self.types)
        
        # Create power-up surface with different colors based on type
        self.original_image = pygame.Surface((30, 30), pygame.SRCALPHA)
        if self.type == 'health':
            pygame.draw.circle(self.original_image, (255, 0, 0), (15, 15), 15)  # Red for health
        elif self.type == 'double_laser':
            pygame.draw.circle(self.original_image, (0, 255, 0), (15, 15), 15)  # Green for double laser
        else:  # triple_laser
            pygame.draw.circle(self.original_image, (0, 0, 255), (15, 15), 15)  # Blue for triple laser
            
        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(center=pos)
        self.speed = 200
        self.direction = pygame.Vector2(0, 1)
        self.rotation = 0
        self.rotation_speed = 100

    def update(self, dt):
        # Update position
        self.rect.center += self.direction * self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
            return
        
        # Update rotation
        self.rotation = (self.rotation + self.rotation_speed * dt) % 360
        self.image = pygame.transform.rotozoom(self.original_image, self.rotation, 1)
        # Keep the center position after rotation
        self.rect = self.image.get_frect(center=self.rect.center)

# Explosion#yuif
class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        explosion_sound.play()

    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

# Start Menu class - handles the game's start screen #mo3taz
class StartMenu:
    def __init__(self):
        # Load and scale background image with error handling
        try:
            self.background = pygame.image.load(join('images', 'rip gaz.png')).convert_alpha()
            self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except:
            self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.background.fill('#3a2e3f')
        
        # Create menu text elements
        self.title = font.render("SPACE SHOOTER", True, (240, 240, 240))
        self.start_text = font.render("Press SPACE to Start", True, (240, 240, 240))
        self.quit_text = font.render("Press Q to Quit", True, (240, 240, 240))
        
        # Position text elements
        self.title_rect = self.title.get_frect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100))
        self.start_rect = self.start_text.get_frect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
        self.quit_rect = self.quit_text.get_frect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 120))

    def draw(self, surface):
        # Draw all menu elements
        surface.blit(self.background, (0, 0))
        surface.blit(self.title, self.title_rect)
        surface.blit(self.start_text, self.start_rect)
        surface.blit(self.quit_text, self.quit_rect)
        
        # Draw borders around text
        pygame.draw.rect(surface, (240, 240, 240), self.title_rect.inflate(40, 20), 5, 10)
        pygame.draw.rect(surface, (240, 240, 240), self.start_rect.inflate(40, 20), 5, 10)
        pygame.draw.rect(surface, (240, 240, 240), self.quit_rect.inflate(40, 20), 5, 10)

# Game Over Screen class - handles the end game screen #khlaid
class GameOver:
    def __init__(self, score):
        self.score = score
        # Create game over text elements
        self.title = font.render("GAME OVER", True, (240, 240, 240))
        self.score_text = font.render(f"Score: {score}", True, (240, 240, 240))
        
        # Handle high score
        self.high_score = self.load_high_score()
        if score > self.high_score:
            self.save_high_score(score)
            self.high_score = score
        self.high_score_text = font.render(f"High Score: {self.high_score}", True, (240, 240, 240))
        self.retry = font.render("Press R to Restart", True, (200, 200, 200))

    def draw(self, surface):
        # Draw game over screen elements
        surface.fill((60, 50, 70))
        center_x = WINDOW_WIDTH // 2
        y = WINDOW_HEIGHT // 2 - 120
        
        # Draw all text elements with proper spacing
        surface.blit(self.title, self.title.get_frect(center=(center_x, y)))
        y += 100
        surface.blit(self.score_text, self.score_text.get_frect(center=(center_x, y)))
        y += 60
        surface.blit(self.high_score_text, self.high_score_text.get_frect(center=(center_x, y)))
        y += 120
        surface.blit(self.retry, self.retry.get_frect(center=(center_x, y)))

    def load_high_score(self):
        # Load high score from file
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0

    def save_high_score(self, score):
        # Save new high score to file
        with open('highscore.txt', 'w') as f:
            f.write(str(score))

# Draw UI function # mohamed
def draw_ui():
    for i in range(player.max_health):
        color = (240, 240, 240) if i < player.health else (100, 100, 100)
        pygame.draw.circle(display_surface, color, (30 + i * 40, 30), 15)

    # Calculate score accounting for pause time
    current_time = pygame.time.get_ticks()
    if paused:
        score = (pause_time - total_pause_time) // 100
    else:
        score = (current_time - start_time - total_pause_time) // 100
    
    score_text = font.render(str(score), True, (240, 240, 240))
    score_rect = score_text.get_frect(midbottom=(WINDOW_WIDTH/2, WINDOW_HEIGHT-50))
    display_surface.blit(score_text, score_rect)
    pygame.draw.rect(display_surface, (240, 240, 240), score_rect.inflate(20, 10).move(0, -8), 5, 10)

    diff_text = font.render(f"Level: {difficulty}", True, (240, 240, 240))
    diff_rect = diff_text.get_frect(midtop=(WINDOW_WIDTH/2, 50))
    display_surface.blit(diff_text, diff_rect)
    pygame.draw.rect(display_surface, (240, 240, 240), diff_rect.inflate(20, 10), 5, 10)

    # Draw power-up status if active
    if player.has_power_up:
        power_up_text = font.render(f"Power: {player.laser_mode}", True, (240, 240, 240))
        power_up_rect = power_up_text.get_frect(midtop=(WINDOW_WIDTH/2, 200))
        display_surface.blit(power_up_text, power_up_rect)
        pygame.draw.rect(display_surface, (240, 240, 240), power_up_rect.inflate(20, 10), 5, 10)

# Initialize sprite groups for different game objects # khlaid
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
enemy_laser_sprites = pygame.sprite.Group()
shooting_enemy_sprites = pygame.sprite.Group()
power_up_sprites = pygame.sprite.Group()
invader_sprites = pygame.sprite.Group()

# Initialize game objects
for _ in range(20):
    Star(star_surf, all_sprites)
player = Player(all_sprites)

# Game variables and settings
difficulty = 1
difficulty_increase_interval = 8000
last_difficulty_increase = start_time = pygame.time.get_ticks()
base_meteor_speed = 200
max_meteor_speed = 400
base_meteor_interval = 600
min_meteor_interval = 200
pause_time = 0
total_pause_time = 0
shooting_enemy_spawn_interval = 5000

# Set up custom events for spawning enemies
meteor_event = pygame.event.custom_type()
shooting_enemy_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, base_meteor_interval)
pygame.time.set_timer(shooting_enemy_event, shooting_enemy_spawn_interval)

# Game state variables
running = True
paused = False
game_over = False
game_over_screen = None
in_start_menu = True
start_menu = StartMenu()

# Main game loop #all
while running:
    # Calculate delta time for smooth movement # abod
    dt = clock.tick() / 600
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Start menu controls
            if in_start_menu:
                if event.key == pygame.K_SPACE:
                    in_start_menu = False
                    start_time = pygame.time.get_ticks()
                    last_difficulty_increase = start_time
                    game_music.play(-1)
                elif event.key == pygame.K_q:
                    running = False
            
            # Game controls# abod
            elif event.key == pygame.K_ESCAPE and not game_over:
                paused = not paused
                if paused:
                    pause_time = pygame.time.get_ticks()
                    game_music.stop()
                else:
                    total_pause_time += pygame.time.get_ticks() - pause_time
                    game_music.play(-1)

            # Restart game# khalid
            if event.key == pygame.K_r and game_over:
                game_over = False
                game_over_screen = None
                player.health = player.max_health
                player.alive = True
                start_time = pygame.time.get_ticks()
                last_difficulty_increase = start_time
                difficulty = 1
                pause_time = 0
                total_pause_time = 0
                for sprite in all_sprites:
                    if not isinstance(sprite, (Player, Star)):
                        sprite.kill()
                game_music.play(-1)

            # Shooting controls # yuif
            if event.key == pygame.K_SPACE and player.can_shoot and not paused and not game_over and not in_start_menu:
                # Handle different laser modes
                if player.laser_mode == 'single':
                    Laser(laser_surf, player.rect.midtop, (all_sprites, laser_sprites))
                elif player.laser_mode == 'double':
                    Laser(laser_surf, (player.rect.midtop[0] - 15, player.rect.midtop[1]), (all_sprites, laser_sprites))
                    Laser(laser_surf, (player.rect.midtop[0] + 15, player.rect.midtop[1]), (all_sprites, laser_sprites))
                else:  # triple laser
                    Laser(laser_surf, player.rect.midtop, (all_sprites, laser_sprites))
                    Laser(laser_surf, (player.rect.midtop[0] - 20, player.rect.midtop[1]), (all_sprites, laser_sprites))
                    Laser(laser_surf, (player.rect.midtop[0] + 20, player.rect.midtop[1]), (all_sprites, laser_sprites))
                
                laser_sound.play()
                player.can_shoot = False
                player.last_shot = pygame.time.get_ticks()

        # Enemy spawning events # mo3taz
        if not paused and not game_over and not in_start_menu:
            if event.type == meteor_event:
                num_meteors = min(1 + (difficulty // 2), 4)
                for _ in range(num_meteors):
                    x = random.randint(0, WINDOW_WIDTH)
                    y = random.randint(-200, -100)
                    Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

            if event.type == shooting_enemy_event:
                x = random.randint(100, WINDOW_WIDTH - 100)
                ShootingEnemyShip((x, -50), (all_sprites, shooting_enemy_sprites), player)

    # Game state handling# mo3taz
    if in_start_menu:
        # Draw start menu
        display_surface.fill('#3a2e3f')
        start_menu.draw(display_surface)
    else:
        if not paused and not game_over:
            # Update game difficulty
            current_time = pygame.time.get_ticks()
            if current_time - last_difficulty_increase >= difficulty_increase_interval:
                difficulty += 1
                last_difficulty_increase = current_time
                new_interval = max(base_meteor_interval - (difficulty - 1) * 30, min_meteor_interval)
                pygame.time.set_timer(meteor_event, int(new_interval))

            # Update all game objects
            all_sprites.update(dt)

            # Handle player collisions and damage # mohamed
            if not player.invincible and player.alive:
                meteor_hits = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
                if meteor_hits:
                    player.health -= 1
                    player.invincible = True
                    player.invincible_time = pygame.time.get_ticks()
                    for meteor in meteor_hits:
                        AnimatedExplosion(explosion_frames, meteor.rect.center, all_sprites)

                laser_hits = pygame.sprite.spritecollide(player, enemy_laser_sprites, True, pygame.sprite.collide_mask)
                if laser_hits:
                    player.health -= 1
                    player.invincible = True
                    player.invincible_time = pygame.time.get_ticks()
                    for laser in laser_hits:
                        AnimatedExplosion(explosion_frames, laser.rect.center, all_sprites)

                # Check for player death #khalid
                    player.alive = False
                    game_over = True
                    game_music.stop()
                    final_score = (pygame.time.get_ticks() - start_time - total_pause_time) // 100
                    game_over_screen = GameOver(final_score)

            # Handle laser collisions with enemies# khlaid
            for laser in laser_sprites:
                meteor_hits = pygame.sprite.spritecollide(laser, meteor_sprites, True)
                if meteor_hits:
                    laser.kill()
                    for meteor in meteor_hits:
                        AnimatedExplosion(explosion_frames, meteor.rect.center, all_sprites)
                        player.kill_count += 1
                        if player.kill_count >= player.kills_for_power_up:
                            player.kill_count = 0
                            x = random.randint(100, WINDOW_WIDTH - 100)
                            PowerUp((x, -50), (all_sprites, power_up_sprites))

                enemy_hits = pygame.sprite.spritecollide(laser, shooting_enemy_sprites, False)
                if enemy_hits:
                    laser.kill()
                    for enemy in enemy_hits:
                        enemy.health -= 1
                        if enemy.health <= 0:
                            enemy.kill()
                            AnimatedExplosion(explosion_frames, enemy.rect.center, all_sprites)
                            player.kill_count += 1
                            if player.kill_count >= player.kills_for_power_up:
                                player.kill_count = 0
                                x = random.randint(100, WINDOW_WIDTH - 100)
                                PowerUp((x, -50), (all_sprites, power_up_sprites))

            # Handle power-up collisions
            power_up_hits = pygame.sprite.spritecollide(player, power_up_sprites, True, pygame.sprite.collide_mask)
            for power_up in power_up_hits:
                player.apply_power_up(power_up.type)
                AnimatedExplosion(explosion_frames, power_up.rect.center, all_sprites)

        # Draw game state
        display_surface.fill('#3a2e3f')
        all_sprites.draw(display_surface)

        if not game_over:
            draw_ui()

        # Draw pause screen # abooood
        if paused:
            pause_text = font.render("PAUSED", True, (240, 240, 240))
            pause_rect = pause_text.get_frect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40))
            resume_text = font.render("Press ESC to Resume", True, (200, 200, 200))
            resume_rect = resume_text.get_frect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
            display_surface.blit(pause_text, pause_rect)
            display_surface.blit(resume_text, resume_rect)
            pygame.draw.rect(display_surface, (240, 240, 240), pause_rect.inflate(40, 20), 5, 10)

        # Draw game over screen
        elif game_over and game_over_screen:
            game_over_screen.draw(display_surface)

    # Update display
    pygame.display.update()

# Clean up
pygame.quit()
