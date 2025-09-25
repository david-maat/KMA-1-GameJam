import pygame
import sys
from game.gamestate import GameState

# init pygame
# ---------- Init ----------
pygame.init()
breedte, hoogte = 800, 600
screen = pygame.display.set_mode((breedte, hoogte))
pygame.display.set_caption("Dino Foodprint Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

current_state = GameState.MENU
gekozen_team = None

current_state = GameState.MENU

def menu_screen(screen):
    screen.fill((0, 0, 50))
    font = pygame.font.SysFont(None, 48)
    text = font.render("MENU - Press Enter", True, (255,255,255))
    screen.blit(text, (200, 200))

def team_select_screen(screen):
    # Links = blauw
    pygame.draw.rect(screen, (0, 0, 150), (0, 0, breedte//2, hoogte))
    # Rechts = rood
    pygame.draw.rect(screen, (150, 0, 0), (breedte//2, 0, breedte//2, hoogte))

    # Tekst toevoegen
    tekst_links = font.render("Team Blauw", True, (255,255,255))
    tekst_rechts = font.render("Team Rood", True, (255,255,255))
    screen.blit(tekst_links, (breedte//4 - 100, hoogte//2 - 24))
    screen.blit(tekst_rechts, (3*breedte//4 - 100, hoogte//2 - 24))

def battle_screen(screen, team):
    screen.fill((0, 50, 0))
    if team:
        tekst = font.render(f"BATTLE! Je zit in Team: {team}", True, (255,255,255))
    else:
        tekst = font.render("BATTLE! Geen team gekozen", True, (255,255,255))
    screen.blit(tekst, (100, hoogte//2 - 24))

def result_screen(screen, team):
    screen.fill((50, 50, 0))
    tekst = font.render(f"RESULT SCREEN - Team: {team}", True, (255, 255, 255))
    screen.blit(tekst, (100, hoogte // 2 - 24))
    instructie = font.render("Druk ENTER om terug naar menu te gaan", True, (255, 255, 0))
    screen.blit(instructie, (50, hoogte // 2 + 50))

# --------- MAIN LOOP
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Menu -> Team Select
            if current_state == GameState.MENU and event.key == pygame.K_RETURN:
                current_state = GameState.TEAM_SELECT

            # Team Select -> Battle (via Enter)
            elif current_state == GameState.TEAM_SELECT and event.key == pygame.K_RETURN:
                current_state = GameState.BATTLE

            # Battle -> Result
            elif current_state == GameState.BATTLE and event.key == pygame.K_RETURN:
                current_state = GameState.RESULT

            # Result -> Menu
            elif current_state == GameState.RESULT and event.key == pygame.K_RETURN:
                current_state = GameState.MENU
                gekozen_team = None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == GameState.TEAM_SELECT:
                x, y = event.pos
                if x < breedte // 2:
                    gekozen_team = "Blauw"
                else:
                    gekozen_team = "Rood"
                current_state = GameState.BATTLE
                print("Gekozen team:", gekozen_team)

    if current_state == GameState.MENU:
        menu_screen(screen)
    elif current_state == GameState.TEAM_SELECT:
        team_select_screen(screen)
    elif current_state == GameState.BATTLE:
        battle_screen(screen, gekozen_team)
    elif current_state == GameState.RESULT:
        result_screen(screen, gekozen_team)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
