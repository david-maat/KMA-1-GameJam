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
font = pygame.font.SysFont("Times New Roman", 48)
button_font = pygame.font.SysFont("Times New Roman", 30)

current_state = GameState.MENU
gekozen_team = None

# Simple medieval colors
DARK_GREEN = (20, 80, 40)
MEDIUM_GREEN = (60, 180, 75)
LIGHT_GREEN = (120, 220, 120)
CREAM = (255, 250, 230)
BROWN = (101, 67, 33)
DARK_BROWN = (62, 39, 35)

# Team colors
TEAM_BLUE = (50, 150, 255)
TEAM_RED = (255, 80, 80)

# Button hover colors
HOVER_GREEN = (80, 220, 100)
HOVER_BROWN = (160, 100, 40)

# Background image
background_image = None
try:
    background_image = pygame.image.load("designer.png")
    background_image = pygame.transform.scale(background_image, (breedte, hoogte))
except:
    pass


class SimpleButton:
    def __init__(self, x, y, width, height, text, color, text_color, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color or color
        self.is_hovered = False

    def draw(self, screen, font):
        current_color = self.hover_color if self.is_hovered else self.color

        # Simple rectangle with small black border
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        # Draw text with small black border
        draw_text_with_border(screen, self.text, font, self.text_color, (0, 0, 0), self.rect.center, 1)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


def draw_text_with_border(surface, text, font, text_color, border_color, pos, border_width=2):
    """Draw text with a border"""
    x, y = pos

    # Draw border by rendering text multiple times with offsets
    for dx in range(-border_width, border_width + 1):
        for dy in range(-border_width, border_width + 1):
            if dx != 0 or dy != 0:  # Don't draw at center position yet
                border_surface = font.render(text, True, border_color)
                border_rect = border_surface.get_rect(center=(x + dx, y + dy))
                surface.blit(border_surface, border_rect)

    # Draw main text on top
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


def draw_background(screen):
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(DARK_GREEN)


def menu_screen(screen):
    draw_background(screen)

    # Title with black border
    title_font = pygame.font.SysFont("Times New Roman", 60)
    draw_text_with_border(screen, "DINO FOODPRINT GAME", title_font, CREAM, (0, 0, 0), (breedte // 2, 150), 3)

    # Subtitle
    subtitle_text = font.render("Kies een team en ga de strijd aan!", True, LIGHT_GREEN)
    subtitle_rect = subtitle_text.get_rect(center=(breedte // 2, 220))
    screen.blit(subtitle_text, subtitle_rect)

    # Simple buttons
    start_button = SimpleButton(breedte // 2 - 100, 320, 200, 60, "Start Game", MEDIUM_GREEN, CREAM, LIGHT_GREEN)
    quit_button = SimpleButton(breedte // 2 - 100, 420, 200, 60, "Quit", BROWN, CREAM, HOVER_BROWN)

    return start_button, quit_button


def team_select_screen(screen):
    draw_background(screen)

    # Simple title
    title_text = font.render("Kies je team:", True, CREAM)
    title_rect = title_text.get_rect(center=(breedte // 2, 100))
    screen.blit(title_text, title_rect)

    # Team areas - simple rectangles
    team_blue_rect = pygame.Rect(50, 200, 300, 300)
    team_red_rect = pygame.Rect(450, 200, 300, 300)

    # Draw team areas with thick borders
    pygame.draw.rect(screen, TEAM_BLUE, team_blue_rect)
    pygame.draw.rect(screen, DARK_BROWN, team_blue_rect, 6)

    pygame.draw.rect(screen, TEAM_RED, team_red_rect)
    pygame.draw.rect(screen, DARK_BROWN, team_red_rect, 6)

    # Team labels
    blue_text = font.render("Team Blauw", True, CREAM)
    blue_text_rect = blue_text.get_rect(center=team_blue_rect.center)
    screen.blit(blue_text, blue_text_rect)

    red_text = font.render("Team Rood", True, CREAM)
    red_text_rect = red_text.get_rect(center=team_red_rect.center)
    screen.blit(red_text, red_text_rect)

    # Instruction
    instruction = button_font.render("Klik op een team om te kiezen", True, LIGHT_GREEN)
    instruction_rect = instruction.get_rect(center=(breedte // 2, 550))
    screen.blit(instruction, instruction_rect)

    return team_blue_rect, team_red_rect


def battle_screen(screen, team):
    draw_background(screen)

    if team:
        text = f"BATTLE! Je zit in Team: {team}"
    else:
        text = "BATTLE! Geen team gekozen"

    battle_text = font.render(text, True, CREAM)
    battle_rect = battle_text.get_rect(center=(breedte // 2, hoogte // 2 - 50))
    screen.blit(battle_text, battle_rect)

    # Instructions
    instruction = button_font.render("Druk ENTER om naar resultaten te gaan", True, LIGHT_GREEN)
    instruction_rect = instruction.get_rect(center=(breedte // 2, hoogte // 2 + 20))
    screen.blit(instruction, instruction_rect)


def result_screen(screen, team):
    draw_background(screen)

    text = f"RESULT SCREEN - Team: {team}"
    result_text = font.render(text, True, CREAM)
    result_rect = result_text.get_rect(center=(breedte // 2, hoogte // 2 - 50))
    screen.blit(result_text, result_rect)

    instruction = button_font.render("Druk ENTER om terug naar menu te gaan", True, LIGHT_GREEN)
    instruction_rect = instruction.get_rect(center=(breedte // 2, hoogte // 2 + 20))
    screen.blit(instruction, instruction_rect)


# --------- MAIN LOOP
running = True
start_button = None
quit_button = None
team_blue_rect = None
team_red_rect = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle button events in menu
        if current_state == GameState.MENU:
            if start_button and start_button.handle_event(event):
                current_state = GameState.TEAM_SELECT
            elif quit_button and quit_button.handle_event(event):
                running = False

        # Handle team selection
        elif current_state == GameState.TEAM_SELECT and event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if team_blue_rect and team_blue_rect.collidepoint((x, y)):
                gekozen_team = "Blauw"
                current_state = GameState.BATTLE
                print("Gekozen team:", gekozen_team)
            elif team_red_rect and team_red_rect.collidepoint((x, y)):
                gekozen_team = "Rood"
                current_state = GameState.BATTLE
                print("Gekozen team:", gekozen_team)

        # Handle keyboard events for other states
        elif event.type == pygame.KEYDOWN:
            # Battle -> Result
            if current_state == GameState.BATTLE and event.key == pygame.K_RETURN:
                current_state = GameState.RESULT
            # Result -> Menu
            elif current_state == GameState.RESULT and event.key == pygame.K_RETURN:
                current_state = GameState.MENU
                gekozen_team = None

    # Render screens
    if current_state == GameState.MENU:
        start_button, quit_button = menu_screen(screen)
        if start_button:
            start_button.draw(screen, button_font)
        if quit_button:
            quit_button.draw(screen, button_font)

    elif current_state == GameState.TEAM_SELECT:
        team_blue_rect, team_red_rect = team_select_screen(screen)

    elif current_state == GameState.BATTLE:
        battle_screen(screen, gekozen_team)

    elif current_state == GameState.RESULT:
        result_screen(screen, gekozen_team)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()