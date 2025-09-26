import pygame
import sys
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
DAMAGE_DURATION = 500  # milliseconds

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Attack + Damage Animation")
clock = pygame.time.Clock()

# --- Load dino sprite ---
dino_image = pygame.image.load("../assets/dino.png").convert_alpha()
dino_rect = dino_image.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))

# --- Attack parameters ---
is_attacking = False
attack_timer = 0
attack_duration = 500
attack_peak_offset = 150
attack_height = 80
attack_stay_time = 200
attack_phase = None
dino_start_x = dino_rect.x
dino_start_y = dino_rect.y

# --- Damage parameters ---
is_damaged = False
damage_timer = 0

# --- Bite effect ---
def create_jaw_surface(width, height, num_teeth, inverted=False):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    tooth_width = width // num_teeth
    points = []
    for i in range(num_teeth):
        x_start = i * tooth_width
        if inverted:
            # Points downwards for top jaw
            points.append((x_start, 0))
            points.append((x_start + tooth_width // 2, height))
            points.append((x_start + tooth_width, 0))
        else:
            # Points upwards for bottom jaw
            points.append((x_start, height))
            points.append((x_start + tooth_width // 2, 0))
            points.append((x_start + tooth_width, height))
    pygame.draw.polygon(surf, (255, 255, 255, 220), points)
    return surf

jaw_width = 120
jaw_height = 30
num_teeth = 8
upper_jaw = create_jaw_surface(jaw_width, jaw_height, num_teeth, inverted=True)
lower_jaw = create_jaw_surface(jaw_width, jaw_height, num_teeth, inverted=False)

# --- Damage flash function ---
def red_flash(image, intensity=100):
    tinted = image.copy()
    red_surf = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    red_surf.fill((intensity, 0, 0, 0))
    tinted.blit(red_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted

# --- Main loop ---
running = True
while running:
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not is_attacking and not is_damaged:
                # Start attack
                is_attacking = True
                attack_timer = 0
                attack_phase = "jump_forward"

    # --- Update attack animation ---
    if is_attacking:
        attack_timer += dt

        if attack_phase == "jump_forward":
            t = attack_timer / attack_duration
            if t > 1:
                t = 1
                attack_phase = "stay_forward"
                attack_timer = 0
            # Move left
            dino_rect.x = dino_start_x - attack_peak_offset * math.sin(t * math.pi / 2)
            # Vertical jump arc
            dino_rect.y = dino_start_y - attack_height * math.sin(t * math.pi)

        elif attack_phase == "stay_forward":
            dino_rect.x = dino_start_x - attack_peak_offset
            dino_rect.y = dino_start_y
            if attack_timer >= attack_stay_time:
                attack_phase = "return"
                attack_timer = 0

        elif attack_phase == "return":
            t = attack_timer / attack_duration
            if t > 1:
                t = 1
                is_attacking = False
                dino_rect.x = dino_start_x
                dino_rect.y = dino_start_y
                # Trigger damage animation immediately after attack
                is_damaged = True
                damage_timer = DAMAGE_DURATION
            else:
                dino_rect.x = dino_start_x - attack_peak_offset * (1 - t)
                dino_rect.y = dino_start_y

    # --- Update damage timer ---
    if is_damaged:
        damage_timer -= dt
        if damage_timer <= 0:
            is_damaged = False

    # --- Draw ---
    screen.fill((34, 139, 34))  # background

    # Draw dino (with damage flash if active)
    if is_damaged:
        # Shake + red flash
        red_image = red_flash(dino_image, intensity=100)
        offset_x = 5 if (pygame.time.get_ticks() // 50) % 2 == 0 else -5
        screen.blit(red_image, (dino_rect.x + offset_x, dino_rect.y))
    else:
        screen.blit(dino_image, dino_rect.topleft)

    # Draw bite effect during attack peak
    if is_attacking and attack_phase == "jump_forward" and 0.45 <= attack_timer / attack_duration <= 0.65:
        t_clamp = (attack_timer / attack_duration - 0.45) / 0.2
        jaw_offset = jaw_height * (1 - t_clamp)
        upper_rect = upper_jaw.get_rect(midbottom=(dino_rect.left - 10, dino_rect.centery - jaw_offset))
        lower_rect = lower_jaw.get_rect(midtop=(dino_rect.left - 10, dino_rect.centery + jaw_offset))
        screen.blit(upper_jaw, upper_rect.topleft)
        screen.blit(lower_jaw, lower_rect.topleft)

    pygame.display.flip()

pygame.quit()
sys.exit()
