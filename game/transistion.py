import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Round Transition with Flash Fade Out")
clock = pygame.time.Clock()

# --- Fonts ---
base_font_size = 80  # maximum font size
font_name = "Arial"

# --- Transition parameters ---
rounds = [1, 2, 3]
current_round_index = 0
timer = 0

# Circle parameters
circle_max_radius = 150
circle_min_radius = 0
circle_radius = 0
circle_grow_speed = 4
circle_shrink_speed = 4

# Phase: "grow", "stay", "shrink", "fade_flash"
phase = "grow"
stay_time = 5000  # milliseconds

# Flash background
flash_color = (255, 255, 255)  # white flash
flash_alpha = 0  # current flash alpha
flash_max_alpha = 200  # max opacity of flash
flash_fade_speed = 3  # speed to fade out

# Text color
text_color = (255, 215, 0)  # gold/yellow


def draw_round_circle(round_number, radius):
    # Draw black circle
    pygame.draw.circle(screen, (0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), int(radius))

    # Scale font with circle
    font_size = int(base_font_size * (radius / circle_max_radius))
    if font_size < 1:
        font_size = 1
    font = pygame.font.SysFont(font_name, font_size, bold=True)

    # Draw text in the center
    text = font.render(f"ROUND {round_number}", True, text_color)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)


# --- Main loop ---
running = True
while running:
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Draw normal background ---
    screen.fill((34, 139, 34))  # green background

    # --- Flash background logic ---
    if phase == "grow" and circle_radius < circle_max_radius:
        flash_alpha = flash_max_alpha  # flash fully visible during grow
    elif phase == "fade_flash":
        flash_alpha -= flash_fade_speed
        if flash_alpha < 0:
            flash_alpha = 0

    # Draw flash overlay
    if flash_alpha > 0:
        flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        flash_surface.set_alpha(int(flash_alpha))
        flash_surface.fill(flash_color)
        screen.blit(flash_surface, (0, 0))

    # --- Transition logic ---
    if current_round_index < len(rounds):
        if phase == "grow":
            circle_radius += circle_grow_speed
            if circle_radius >= circle_max_radius:
                circle_radius = circle_max_radius
                phase = "stay"
                timer = 0
        elif phase == "stay":
            timer += dt
            if timer >= stay_time:
                phase = "shrink"
        elif phase == "shrink":
            circle_radius -= circle_shrink_speed
            if circle_radius <= circle_min_radius:
                circle_radius = circle_min_radius
                phase = "fade_flash"
        elif phase == "fade_flash":
            if flash_alpha <= 0:
                phase = "grow"
                current_round_index += 1
                circle_radius = 0

        # Draw the circle and text **on top of flash**
        draw_round_circle(rounds[current_round_index], circle_radius)

    pygame.display.flip()

pygame.quit()
sys.exit()
