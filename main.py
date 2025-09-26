import pygame
import sys
import random
from game.gamestate import GameState
from game import rendering
from game import ui
from game.battle_system import BattleSystem
from game.team import Team

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

# Initialize battle system
battle_system = BattleSystem(breedte, hoogte)

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
    # Load and scale the background image
    try:
        background_image = pygame.image.load("assets/menu.png")
        scaled_bg = pygame.transform.scale(background_image, (breedte, hoogte))
        screen.blit(scaled_bg, (0, 0))
    except pygame.error:
        # Fallback if image can't be loaded
        screen.fill((0, 0, 50))

    # Load and draw logo in top left corner
    try:
        logo_image = pygame.image.load("assets/logo.png")
        # Scale logo to be small (adjust size as needed)
        logo_size = 55  # You can adjust this value to make it smaller/larger
        scaled_logo = pygame.transform.scale(logo_image, (logo_size, logo_size))
        # Position in top left with small padding
        screen.blit(scaled_logo, (15, 15))
    except pygame.error:
        # If logo can't be loaded, you could draw a placeholder or just skip
        pass

    # Create fonts with Comic Sans style
    title_font = pygame.font.SysFont("comicsansms", 72, bold=True)  # Larger Comic Sans font
    subtitle_font = pygame.font.SysFont("comicsansms", 36)  # Comic Sans for subtitle

    # Main title text
    title_text = "Title"
    title_shadow = title_font.render(title_text, True, (0, 0, 0))  # Black shadow
    title_main = title_font.render(title_text, True, (255, 255, 255))  # White text

    # Shadow offset
    shadow_offset = 3
    title_x = breedte // 2 - title_main.get_width() // 2
    title_y = hoogte // 3  # Position in upper third of screen
    screen.blit(title_shadow, (title_x + shadow_offset, title_y + shadow_offset))
    screen.blit(title_main, (title_x, title_y))

    # Subtitle/instruction text
    subtitle_text = "Press Enter"
    subtitle_shadow = subtitle_font.render(subtitle_text, True, (0, 0, 0))  # Black shadow
    subtitle_main = subtitle_font.render(subtitle_text, True, (200, 200, 200))  # Light gray text
    subtitle_x = breedte // 2 - subtitle_main.get_width() // 2
    subtitle_y = title_y + title_main.get_height() + 30  # 30 pixels below title
    screen.blit(subtitle_shadow, (subtitle_x + shadow_offset, subtitle_y + shadow_offset))
    screen.blit(subtitle_main, (subtitle_x, subtitle_y))

    # Show coins in menu
    draw_coin_display(screen)


def team_select_screen(screen):
    # Load and draw background images for each team
    try:
        # Load blue team (jungle) background
        bg_blauw = pygame.image.load("assets/classic.jpg")
        scaled_bg_blauw = pygame.transform.scale(bg_blauw, (breedte // 2, hoogte))
        screen.blit(scaled_bg_blauw, (0, 0))
    except pygame.error:
        # Fallback for blue team side
        pygame.draw.rect(screen, (0, 0, 150), (0, 0, breedte // 2, hoogte))

    try:
        # Load red team (desert) background
        bg_rood = pygame.image.load("assets/desert.jpg")
        scaled_bg_rood = pygame.transform.scale(bg_rood, (breedte // 2, hoogte))
        screen.blit(scaled_bg_rood, (breedte // 2, 0))
    except pygame.error:
        # Fallback for red team side
        pygame.draw.rect(screen, (150, 0, 0), (breedte // 2, 0, breedte // 2, hoogte))

    # Add main title text
    title_font = pygame.font.SysFont("comicsansms", 60, bold=True)
    title_text = "Select Your Team"
    title_shadow = title_font.render(title_text, True, (0,0, 0))  # Dark gray shadow
    title_main = title_font.render(title_text, True, (255, 255, 255))  # White text

    # Center the title at top
    title_x = breedte // 2 - title_main.get_width() // 2
    title_y = 80
    shadow_offset = 2

    # Draw shadow first, then main text
    screen.blit(title_shadow, (title_x + shadow_offset, title_y + shadow_offset))
    screen.blit(title_main, (title_x, title_y))

    # Team text fonts
    team_font = pygame.font.SysFont("comicsansms", 50, bold=True)

    # Team Jungle text with border effect
    tekst_links_border = team_font.render("Team Jungle", True, (0, 100, 0))  # Darker jungle border
    tekst_links = team_font.render("Team Jungle", True, (34, 139, 34))  # Jungle green main text

    # Team Yellow text with border effect
    tekst_rechts_border = team_font.render("Team Geel", True, (200, 190, 130))  # Darker border
    tekst_rechts = team_font.render("Team Geel", True, (255, 243, 165))  # Main text

    # Draw borders first (slightly offset)
    border_offset = 2
    left_x = breedte // 4 - tekst_links.get_width() // 2
    right_x = 3 * breedte // 4 - tekst_rechts.get_width() // 2
    team_y = hoogte // 2 - 24

    screen.blit(tekst_links_border, (left_x + border_offset, team_y + border_offset))
    screen.blit(tekst_rechts_border, (right_x + border_offset, team_y + border_offset))

    # Draw main team texts over borders
    screen.blit(tekst_links, (left_x, team_y))
    screen.blit(tekst_rechts, (right_x, team_y))

    # Show coins in team select
    draw_coin_display(screen)


def result_screen(screen, team):
    global player_coins

    # Different background colors based on battle result
    if battle_system.battle_result == "player_wins":
        screen.fill((0, 50, 0))  # Green for victory
        result_text = "VICTORY!"
        result_color = (0, 255, 0)
    elif battle_system.battle_result == "enemy_wins":
        screen.fill((50, 0, 0))  # Red for defeat
        result_text = "DEFEAT!"
        result_color = (255, 0, 0)
    else:
        screen.fill((50, 50, 0))  # Yellow for unknown
        result_text = "BATTLE COMPLETE"
        result_color = (255, 255, 0)

    # Display battle result
    large_font = pygame.font.SysFont(None, 72, bold=True)
    result_surface = large_font.render(result_text, True, result_color)
    screen.blit(result_surface, (breedte // 2 - result_surface.get_width() // 2, hoogte // 2 - 100))
    
    # Display team info
    team_text = font.render(f"Team: {team}", True, (255, 255, 255))
    screen.blit(team_text, (100, hoogte // 2 - 24))
    
    instructie = font.render("Druk ENTER om terug naar menu te gaan", True, (255, 255, 0))
    screen.blit(instructie, (50, hoogte // 2 + 50))

    # Show coins earned (already awarded during battle)
    coins_text = font.render("Coins earned from battle!", True, (255, 215, 0))
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
                if battle_system.battle_phase == "battle_over":
                    current_state = GameState.RESULT
            elif current_state == GameState.RESULT and event.key == pygame.K_RETURN:
                # Return to shop and reflect battle results
                # Remove dead dinos from arena team
                try:
                    rendering.arena_team = [d for d in rendering.arena_team if getattr(d, 'hp', 1) > 0]
                except Exception:
                    pass
                # Reorder arena positions for a clean layout
                try:
                    # If we don't have a cached arena_y, compute the same as rendering.draw
                    local_arena_y = arena_y if arena_y else int(hoogte * 0.65) - 100
                    rendering.reorder_arena(local_arena_y)
                except Exception:
                    pass
                current_state = GameState.SHOP
                gekozen_team = None

            # Cheat codes for testing (remove in final version)
            elif event.key == pygame.K_c:  # Press 'C' to add 100 coins
                add_coins(100)
            elif event.key == pygame.K_x:  # Press 'X' to spend 10 coins (for testing)
                spend_coins(10)

        if event.type == pygame.MOUSEBUTTONDOWN and current_state == GameState.BATTLE:
            battle_system.handle_click(event.pos)
        
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
                    
                    # Convert arena team to Team object for battle system
                    player_team_obj = Team(player_team)
                    
                    # bepaal wie begint (0 = player, 1 = enemy)
                    starting_player = random.choice([0, 1])
                    # Start battle with random enemy team and selected starter
                    battle_system.start_battle(player_team_obj, starting_player=starting_player)

                    # Transition text uses 1/2 for readability
                    human_player_num = 1 if starting_player == 0 else 2
                    transition_message = f"Player {human_player_num} begint!"
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
        battle_system.update()
        battle_system.draw(screen)
        
        # Check if battle just ended and award coins once
        if battle_system.battle_phase == "battle_over" and not hasattr(battle_system, 'coins_awarded'):
            if battle_system.battle_result == "player_wins":
                # Award extra coins for victory
                coins_earned = random.randint(30, 70)
                add_coins(coins_earned)
            elif battle_system.battle_result == "enemy_wins":
                # Small consolation prize
                coins_earned = random.randint(5, 15)
                add_coins(coins_earned)
            battle_system.coins_awarded = True  # Mark as awarded
    elif current_state == GameState.RESULT:
        result_screen(screen, gekozen_team)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()