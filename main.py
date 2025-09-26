import pygame
import sys
import random
from game.gamestate import GameState
from game import rendering
from game import ui

# Init
pygame.init()
breedte, hoogte = 1200, 700
screen = pygame.display.set_mode((breedte, hoogte))
pygame.display.set_caption("Dino Foodprint Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

current_state = GameState.MENU
gekozen_team = None
player_team = []
enemy_team = []

# init rendering (team build)
rendering.init_rendering()

# fonts en teams voor UI
vs_font, label_font = ui.load_fonts()
enemy_team = ui.create_enemy_team()
PATH_Y = hoogte // 2

# transition variabelen
transition_message = ""
transition_timer = 0

# Laad de afbeeldingen buiten de functie (één keer bij opstarten)
bg_blauw = pygame.image.load("assets/classic.jpg")
bg_rood = pygame.image.load("assets/desert.jpg")

# Optioneel: schaal de afbeeldingen naar de helft van het scherm
bg_blauw = pygame.transform.scale(bg_blauw, (breedte//2, hoogte))
bg_rood = pygame.transform.scale(bg_rood, (breedte//2, hoogte))


def menu_screen(screen):
    # Load and scale the background image
    background_image = pygame.image.load("assets/menu.png")
    scaled_bg = pygame.transform.scale(background_image, (breedte, hoogte))
    screen.blit(scaled_bg, (0, 0))

    # Create title text with shadow effect using Comic Sans
    title_font = pygame.font.SysFont("comicsansms", 96)  # Comic Sans, bigger size
    subtitle_font = pygame.font.SysFont("comicsansms", 48)  # Comic Sans for subtitle too

    # Main title
    title_text = "GAME TITLE"  # Replace with your actual game title
    title_shadow = title_font.render(title_text, True, (0, 0, 0))  # Black shadow
    title_main = title_font.render(title_text, True, (255, 255, 255))  # White text

    # Shadow offset (3 pixels down and right)
    shadow_offset = 3
    title_x = breedte // 2 - title_main.get_width() // 2
    title_y = hoogte // 3  # Position in upper third of screen

    screen.blit(title_shadow, (title_x + shadow_offset, title_y + shadow_offset))
    screen.blit(title_main, (title_x, title_y))

    # Subtitle/instruction text
    subtitle_text = "Press Enter to Start"
    subtitle_shadow = subtitle_font.render(subtitle_text, True, (0, 0, 0))
    subtitle_main = subtitle_font.render(subtitle_text, True, (200, 200, 200))

    subtitle_x = breedte // 2 - subtitle_main.get_width() // 2
    subtitle_y = title_y + title_main.get_height() + 50  # 50 pixels below title

    screen.blit(subtitle_shadow, (subtitle_x + shadow_offset, subtitle_y + shadow_offset))
    screen.blit(subtitle_main, (subtitle_x, subtitle_y))

def team_select_screen(screen):
    # Teken de achtergrondafbeeldingen
    screen.blit(bg_blauw, (0, 0))
    screen.blit(bg_rood, (breedte//2, 0))

    # Voeg de hoofdtekst toe
    title_font = pygame.font.SysFont("comicsansms", 60, bold=True)
    title_text = title_font.render("Select Your Team", True, (0,0,0))  # Witte tekst
    title_rect = title_text.get_rect(center=(breedte // 2, 80))  # Gecentreerd, 80 pixels van de bovenkant
    screen.blit(title_text, title_rect)

    # Shadow voor de titel
    title_shadow = title_font.render("Select Your Team", True, (50, 50, 50))  # Donkergrijs voor shadow
    title_shadow_rect = title_shadow.get_rect(center=(breedte // 2 + 2, 80 + 2))  # 3 pixels verschoven

    # Eerst de shadow tekenen, dan de hoofdtekst
    screen.blit(title_shadow, title_shadow_rect)
    screen.blit(title_text, title_rect)

    # Voeg de teamteksten toe
    jungle_font = pygame.font.SysFont("comicsansms", 50, bold=True)
    # Border voor Team Jungle
    tekst_links_border = jungle_font.render("Team Jungle", True, (0, 90, 0))  # Donkerder groen
    tekst_links = jungle_font.render("Team Jungle", True, (0, 128, 0))

    dessert_font = pygame.font.SysFont("comicsansms", 48, bold=True)
    # Border voor Team Dessert
    tekst_rechts_border = dessert_font.render("Team Dessert", True, (230, 218, 140))  # Donkerder geel
    tekst_rechts = dessert_font.render("Team Dessert", True, (255, 243, 165))  # #FFF3A5

    # Teken de borders eerst (iets verschoven)
    border_offset = 2
    screen.blit(tekst_links_border, (breedte // 4 - 150 + border_offset, hoogte // 2 - 28 + border_offset))
    screen.blit(tekst_rechts_border, (3 * breedte // 4 - 150 + border_offset, hoogte // 2 - 28 + border_offset))

    # Teken de hoofdteksten erover
    screen.blit(tekst_links, (breedte // 4 - 150, hoogte // 2 - 28))
    screen.blit(tekst_rechts, (3 * breedte // 4 - 150, hoogte // 2 - 28))

def result_screen(screen, team):
    screen.fill((50, 50, 0))
    tekst = font.render(f"RESULT SCREEN - Team: {team}", True, (255, 255, 255))
    screen.blit(tekst, (100, hoogte // 2 - 24))
    instructie = font.render("Druk ENTER om terug naar menu te gaan", True, (255, 255, 0))
    screen.blit(instructie, (50, hoogte // 2 + 50))

def transition_screen(screen):
    global transition_timer, current_state
    screen.fill((0, 0, 0))  # zwart scherm

    # fade effect
    transition_timer += 1
    alpha = min(255, transition_timer * 5)

    font_big = pygame.font.SysFont("comic sans ms", 60, bold=True)
    text = font_big.render(transition_message, True, (255, 255, 255))
    text.set_alpha(alpha)
    screen.blit(text, (breedte//2 - text.get_width()//2, hoogte//2 - text.get_height()//2))

    # na 2 seconden naar battle
    if transition_timer > 120:
        current_state = GameState.BATTLE

# Main loop
running = True
arena_y, shop_y = None, None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if current_state == GameState.MENU and event.key == pygame.K_RETURN:
                current_state = GameState.TEAM_SELECT
            elif current_state == GameState.TEAM_SELECT and event.key == pygame.K_RETURN:
                current_state = GameState.SHOP
            elif current_state == GameState.BATTLE and event.key == pygame.K_RETURN:
                current_state = GameState.RESULT
            elif current_state == GameState.RESULT and event.key == pygame.K_RETURN:
                current_state = GameState.MENU
                gekozen_team = None

        if event.type == pygame.MOUSEBUTTONDOWN and current_state == GameState.TEAM_SELECT:
            x, y = event.pos
            if x < breedte // 2:
                gekozen_team = "Blauw"
            else:
                gekozen_team = "Rood"
            current_state = GameState.SHOP

        # events doorgeven aan rendering
        if current_state == GameState.SHOP:
            if arena_y and shop_y:
                result = rendering.handle_event(event, arena_y, shop_y)
                if result == "start":
                    # neem arena team als player team
                    player_team = rendering.arena_team

                    # bepaal wie begint
                    starting_player = random.choice([1, 2])
                    transition_message = f"Player {starting_player} begint!"
                    transition_timer = 0

                    current_state = GameState.TRANSITION

    # ---------- RENDERING -------------
    if current_state == GameState.MENU:
        menu_screen(screen)
    elif current_state == GameState.TEAM_SELECT:
        team_select_screen(screen)
    elif current_state == GameState.SHOP:
        arena_y, shop_y = rendering.draw(screen)
    elif current_state == GameState.TRANSITION:
        transition_screen(screen)
    elif current_state == GameState.BATTLE:
        ui.draw_battle(screen, player_team, enemy_team, vs_font, label_font, PATH_Y)
    elif current_state == GameState.RESULT:
        result_screen(screen, gekozen_team)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
