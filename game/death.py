import pygame
import sys
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Initialize ---
pygame.init()
pygame.mixer.init()  # initialize sound system
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Death Animation with Swaying Skull")
clock = pygame.time.Clock()

# --- Load sprites ---
dino_image = pygame.image.load("../assets/dino.png").convert_alpha()
dino_rect = dino_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

# Skull image
skull_image_orig = pygame.image.load("../assets/skull.png").convert_alpha()

# --- Load sounds ---
death_sound = pygame.mixer.Sound("../assets/death.mp3")
death_sound.set_volume(0.8)  # adjust volume (0.0 - 1.0)

# --- Death animation state ---
is_dead = False
fade_alpha = 255
dino_animation_speed = 2  # pixels per frame for dino
fade_speed = 3  # alpha reduction per frame for dino
skull_delay = 30  # frames before skull appears
skull_timer = 0
skull_scale = 0.3  # start smaller
skull_rise_speed = 2  # pixels per frame
skull_fade_speed = 2  # alpha reduction per frame for skull
skull_sway_amplitude = 15  # pixels left/right
skull_sway_speed = 0.15  # sway frequency

# Skull vertical position and alpha
skull_alpha = 255
skull_y = 0  # initialized on death


def trigger_death():
    global is_dead, fade_alpha, skull_timer, skull_alpha, skull_y
    is_dead = True
    fade_alpha = 255
    skull_timer = 0
    skull_alpha = 255
    skull_y = dino_rect.centery + 20  # start slightly below dino center
    # Play death sound once
    death_sound.play()


# --- Main loop ---
running = True
while running:
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d and not is_dead:
                trigger_death()  # press D to trigger death

    # --- Update animation ---
    if is_dead:
        # Fade dino
        fade_alpha -= fade_speed
        if fade_alpha < 0:
            fade_alpha = 0
        # Move dino down
        dino_rect.y += dino_animation_speed

        # Update skull timer
        skull_timer += 1
        if skull_timer > skull_delay:
            skull_y -= skull_rise_speed  # skull moves up
            skull_alpha -= skull_fade_speed
            if skull_alpha < 0:
                skull_alpha = 0

    # --- Draw ---
    screen.fill((34, 139, 34))  # background

    # Draw dino with fading
    if fade_alpha > 0:
        dino_copy = dino_image.copy()
        dino_copy.fill((255, 255, 255, fade_alpha), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(dino_copy, dino_rect.topleft)

    # Draw skull rising, swaying, and fading
    if is_dead and skull_timer > skull_delay and skull_alpha > 0:
        # Scale skull
        skull_scaled = pygame.transform.scale(
            skull_image_orig,
            (int(skull_image_orig.get_width() * skull_scale),
             int(skull_image_orig.get_height() * skull_scale))
        )
        # Apply fade
        skull_scaled_copy = skull_scaled.copy()
        skull_scaled_copy.fill((255, 255, 255, skull_alpha), special_flags=pygame.BLEND_RGBA_MULT)
        # Horizontal sway using sine wave
        skull_x = dino_rect.centerx + math.sin((skull_timer - skull_delay) * skull_sway_speed) * skull_sway_amplitude
        skull_rect_scaled = skull_scaled_copy.get_rect(center=(skull_x, skull_y))
        screen.blit(skull_scaled_copy, skull_rect_scaled.topleft)

    pygame.display.flip()

pygame.quit()
sys.exit()
