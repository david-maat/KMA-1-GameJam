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

# COIN SYSTEM
player_coins = 100  # Starting coins
coin_font = pygame.font.SysFont("Arial", 36, bold=True)

# init rendering (team build)
rendering.init_rendering()

# fonts en teams voor UI
vs_font, label_font = ui.load_fonts()
enemy_team = ui.create_enemy_team()
PATH_Y = hoogte // 2

# transition variabelen
transition_message = ""
transition_timer = 0


def draw_coin_display(screen):
    """Draw the coin counter in the top right corner"""
    coin_text = coin_font.render(f"Coins: {player_coins}", True, (255, 215, 0))  # Gold color
    coin_shadow = coin_font.render(f"Coins: {player_coins}", True, (0, 0, 0))  # Black shadow

    # Position in top right with some padding
    x = breedte - coin_text.get_width() - 20
    y = 20

    # Draw shadow slightly offset
    screen.blit(coin_shadow, (x + 2, y + 2))
    screen.blit(coin_text, (x, y))

    # Draw coin icon (simple circle)
    pygame.draw.circle(screen, (255, 215, 0), (x - 30, y + 18), 12)
    pygame.draw.circle(screen, (218, 165, 32), (x - 30, y + 18), 12, 2)


def menu_screen(screen):
    screen.fill((0, 0, 50))
    text = font.render("MENU - Press Enter", True, (255, 255, 255))
    screen.blit(text, (breedte // 2 - text.get_width() // 2, hoogte // 2 - 24))

    # Show coins in menu
    draw_coin_display(screen)


def team_select_screen(screen):
    pygame.draw.rect(screen, (0, 0, 150), (0, 0, breedte // 2, hoogte))
    pygame.draw.rect(screen, (150, 0, 0), (breedte // 2, 0, breedte // 2, hoogte))
    tekst_links = font.render("Team Blauw", True, (255, 255, 255))
    tekst_rechts = font.render("Team Rood", True, (255, 255, 255))
    screen.blit(tekst_links, (breedte // 4 - 100, hoogte // 2 - 24))
    screen.blit(tekst_rechts, (3 * breedte // 4 - 100, hoogte // 2 - 24))

    # Show coins in team select
    draw_coin_display(screen)


def result_screen(screen, team):
    global player_coins

    screen.fill((50, 50, 0))
    tekst = font.render(f"RESULT SCREEN - Team: {team}", True, (255, 255, 255))
    screen.blit(tekst, (100, hoogte // 2 - 24))
    instructie = font.render("Druk ENTER om terug naar menu te gaan", True, (255, 255, 0))
    screen.blit(instructie, (50, hoogte // 2 + 50))

    # Award coins for battle completion
    coins_earned = random.randint(20, 50)
    player_coins += coins_earned

    coins_text = font.render(f"Coins verdiend: +{coins_earned}", True, (255, 215, 0))
    screen.blit(coins_text, (50, hoogte // 2 + 100))

    draw_coin_display(screen)


def transition_screen(screen):
    global transition_timer, current_state
    screen.fill((0, 0, 0))  # zwart scherm

    # fade effect
    transition_timer += 1
    alpha = min(255, transition_timer * 5)

    font_big = pygame.font.SysFont("comic sans ms", 60, bold=True)
    text = font_big.render(transition_message, True, (255, 255, 255))
    text.set_alpha(alpha)
    screen.blit(text, (breedte // 2 - text.get_width() // 2, hoogte // 2 - text.get_height() // 2))

    # na 2 seconden naar battle
    if transition_timer > 120:
        current_state = GameState.BATTLE


def can_afford(cost):
    """Check if player has enough coins"""
    return player_coins >= cost


def spend_coins(amount):
    """Spend coins if player has enough"""
    global player_coins
    if can_afford(amount):
        player_coins -= amount
        return True
    return False


def add_coins(amount):
    """Add coins to player's total"""
    global player_coins
    player_coins += amount


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

            # Cheat codes for testing (remove in final version)
            elif event.key == pygame.K_c:  # Press 'C' to add 100 coins
                add_coins(100)
            elif event.key == pygame.K_x:  # Press 'X' to spend 10 coins (for testing)
                spend_coins(10)

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
                # Pass coin functions to rendering system
                result = rendering.handle_event(event, arena_y, shop_y,
                                                coin_check=can_afford,
                                                coin_spend=spend_coins)
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
        arena_y, shop_y = rendering.draw(screen, player_coins)  # Pass coins to shop
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