import pygame
import random

pygame.init()

# Constants for character and background
scroll_speed = 10

# Initialize the screen
FPS = 60
screen_width = 1500
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Shoot or Die")

# Loading sounds
pygame.mixer.init()
pygame.mixer.music.load("sounds/startmenu_sound.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)
shoot_sound = pygame.mixer.Sound("./sounds/shootsound.mp3")

# Load asset images
startmenu_background = pygame.image.load("images/startmenu_background.png").convert()
startmenu_background = pygame.transform.scale(startmenu_background, (screen_width, screen_height))

background = pygame.image.load("images/background2.jpeg").convert()
background = pygame.transform.scale(background, (screen_width, screen_height))

character_image = pygame.image.load("images/plane.png").convert_alpha()
character_image = pygame.transform.scale(character_image, (93, 93))

enemy_image = pygame.image.load("images/missile.png")

explosion_image = pygame.image.load("images/explosion.jpeg").convert_alpha()
explosion_image = pygame.transform.scale(explosion_image, (64 * 4, 64))  # Adjusted for 4 frames

# Character variables
plane_x = 6
plane_y = 175
plane_width = 93
plane_height = 93
character_speed = 9

# Bullet variables
bullet_image = pygame.image.load("images/bullets.png").convert_alpha()
bullet_width = 30
bullet_height = 90
bullet_image = pygame.transform.scale(bullet_image, (bullet_width, bullet_height))
bullet_speed = 20
bullets = []
shoot_delay = 0
shoot_timer = 0
shooting = False

# Function to fire a bullet
def fire_bullet(x, y):
    bullet = {
        "x": x + plane_width,
        "y": y + plane_height // 2 - bullet_height // 2
    }
    bullets.append(bullet)
    shoot_sound.play()

# Initial background positions
bg_x = 0
game_state = "start_menu"

# Start menu
def draw_start_menu():
    screen.blit(startmenu_background, (0, 0))
    font = pygame.font.SysFont('impact', 40)
    title = font.render('Shoot or Die', True, (255, 255, 255))
    start_button = font.render('Press SPACE to start', True, (255, 255, 255))
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, screen_height // 2 - title.get_height() // 2))
    screen.blit(start_button, (screen_width // 2 - start_button.get_width() // 2, screen_height // 2 + start_button.get_height() // 2))
    pygame.display.update()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        scaled_enemy_image = pygame.transform.scale(enemy_image, (70, 70))
        self.image = scaled_enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(0, screen_height - self.rect.height)
        self.speed = 25

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.rect.x = screen_width

# Track the time since the last wave of enemies
last_enemy_wave_time = pygame.time.get_ticks()
respawn_interval = 30000
num_enemies_in_wave = 5

# Create a sprite group for enemies
all_sprites = pygame.sprite.Group()

# Create and add enemies to the sprite group
for _ in range(20):
    enemy = Enemy()
    all_sprites.add(enemy)

# Create an explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = explosion_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.frame = 0
        self.load_images()

    def load_images(self):
        frame_width = 64
        frame_height = 64
        sheet_width = self.image.get_width()

        self.explosion_frames = []
        for x in range(0, sheet_width, frame_width):
            frame_rect = pygame.Rect(x, 0, frame_width, frame_height)
            frame_image = self.image.subsurface(frame_rect)
            self.explosion_frames.append(frame_image)

    def update(self):
        if self.frame < len(self.explosion_frames):
            self.image = self.explosion_frames[self.frame]
            self.frame += 1
        else:
            self.kill()

# Create a sprite group for explosions
explosion_sprites = pygame.sprite.Group()

# Health bar class
class HealthBar():
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w  # Increased width for longer health bar
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp  # Fixed to allow dynamic max health

    def draw(self, surface):
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, "red", (self.x, self.y, self.w, self.h))  # Full health bar
        pygame.draw.rect(surface, "green", (self.x, self.y, self.w * ratio, self.h))  # Current health

# Position of the health bar
health_bar = HealthBar(10, 10, 300, 30, 100)  # Adjusted to make it longer and taller
buffer_surface = pygame.Surface((screen_width, screen_height))

# Game loop
clock = pygame.time.Clock()
running = True
game_over = False

while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Check if it's time to spawn a new wave of enemies
    if current_time - last_enemy_wave_time > respawn_interval:
        last_enemy_wave_time = current_time
        num_enemies_in_wave += 1
        for _ in range(num_enemies_in_wave):
            enemy = Enemy()
            all_sprites.add(enemy)

    if game_state == "start_menu":
        draw_start_menu()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_state = "game"
            game_over = False
            pygame.mixer.music.stop()

    elif game_state == "game":
        keys = pygame.key.get_pressed()
        bg_x -= scroll_speed
        if keys[pygame.K_w]:
            if plane_y - character_speed >= 0:
                plane_y -= character_speed
        if keys[pygame.K_s]:
            if plane_y + character_speed <= screen_height - plane_height:
                plane_y += character_speed
        if keys[pygame.K_SPACE] and shoot_timer <= 0 and not shooting:
            fire_bullet(plane_x, plane_y)
            shoot_timer = shoot_delay
            shooting = True

        if shoot_timer > 0:
            shoot_timer -= 1

        if not keys[pygame.K_SPACE]:
            shooting = False

        if bg_x <= -screen_width:
            bg_x = 0

        for bullet in bullets:
            bullet["x"] += bullet_speed

        # Clear the buffer surface
        buffer_surface.fill((0, 0, 0))

        # Draw background, character, and health bar on the buffer surface
        buffer_surface.blit(background, (bg_x, 0))
        buffer_surface.blit(background, (bg_x + screen_width, 0))
        buffer_surface.blit(character_image, (plane_x, plane_y))
        health_bar.draw(buffer_surface)

        # Draw bullets on the buffer surface
        for bullet in bullets:
            buffer_surface.blit(bullet_image, (bullet["x"], bullet["y"]))

        # Check for collisions and handle enemy hits
        for bullet in bullets:
            for enemy in all_sprites:
                if enemy.rect.colliderect(pygame.Rect(bullet["x"], bullet["y"], bullet_width, bullet_height)):
                    # Create an explosion at the enemy's position
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(explosion)
                    explosion_sprites.add(explosion)
                    enemy.kill()
                    if bullet in bullets:
                        bullets.remove(bullet)

        # Check for collisions with the character (reduces health when hit)
        for enemy in all_sprites:
            if plane_x < enemy.rect.centerx < plane_x + plane_width and plane_y < enemy.rect.centery < plane_y + plane_height:
                health_bar.hp -= 10  # Reduce health by 10 per hit
                enemy.kill()
                if health_bar.hp <= 0:
                    game_state = "start_menu"  # Restart the game if health reaches 0

        # Draw the buffer surface on the screen
        screen.blit(buffer_surface, (0, 0))

        # Update and draw sprites
        all_sprites.update()
        all_sprites.draw(screen)
        explosion_sprites.update()
        explosion_sprites.draw(screen)

        pygame.display.update()

# Quit pygame
pygame.quit()
