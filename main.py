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

# CARBON TRACKING SYSTEM
total_player_carbon = 0  # Persistent carbon across all battles
total_enemy_carbon = 0   # Persistent carbon across all battles

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

    # Different background colors based on battle result
    if battle_system.battle_result == "player_wins":
        screen.fill((0, 50, 0))  # Green for victory
        result_text = "VICTORY!"
        result_color = (0, 255, 0)
    elif battle_system.battle_result == "enemy_wins":
        screen.fill((50, 0, 0))  # Red for defeat
        result_text = "DEFEAT!"
        result_color = (255, 0, 0)
    elif battle_system.battle_result == "world_ends":
        screen.fill((20, 20, 20))  # Dark for world ending
        result_text = "WORLD ENDS!"
        result_color = (255, 100, 0)  # Orange/red
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


def can_afford_anything():
    """Check if player can afford any dinosaur in the shop"""
    # Get the cheapest dinosaur price from the shop
    min_price = float('inf')
    for dino in rendering.shop_dinos:
        if hasattr(dino, 'price'):
            min_price = min(min_price, dino.price)
    
    # If no prices found, use default minimum
    if min_price == float('inf'):
        min_price = 15  # Default minimum price
    
    return player_coins >= min_price


def carbon_to_tonnes(carbon_points):
    """Convert carbon points to tonnes of CO2 for display"""
    # Each carbon point represents 0.5 tonnes of CO2
    return carbon_points * 0.5


def game_over_screen(screen):
    """Display game over screen with carbon footprint overview"""
    
    screen.fill((20, 20, 20))  # Dark background
    
    # Title
    title_font = pygame.font.SysFont(None, 72, bold=True)
    title_text = title_font.render("GAME OVER", True, (255, 100, 100))
    screen.blit(title_text, (breedte // 2 - title_text.get_width() // 2, 100))
    
    # Subtitle
    subtitle_font = pygame.font.SysFont(None, 36)
    subtitle_text = subtitle_font.render("Not enough coins to continue!", True, (255, 255, 255))
    screen.blit(subtitle_text, (breedte // 2 - subtitle_text.get_width() // 2, 180))
    
    # Carbon footprint overview
    carbon_font = pygame.font.SysFont(None, 48, bold=True)
    overview_font = pygame.font.SysFont(None, 32)
    
    # Header
    carbon_header = carbon_font.render("CARBON FOOTPRINT OVERVIEW", True, (255, 200, 0))
    screen.blit(carbon_header, (breedte // 2 - carbon_header.get_width() // 2, 250))
    
    # Player carbon
    player_tonnes = carbon_to_tonnes(total_player_carbon)
    player_text = overview_font.render(f"Your Carbon Emissions: {player_tonnes:.1f} tonnes CO2", True, (255, 100, 100))
    screen.blit(player_text, (breedte // 2 - player_text.get_width() // 2, 320))
    
    # Enemy carbon
    enemy_tonnes = carbon_to_tonnes(total_enemy_carbon)
    enemy_text = overview_font.render(f"Enemy Carbon Emissions: {enemy_tonnes:.1f} tonnes CO2", True, (255, 100, 100))
    screen.blit(enemy_text, (breedte // 2 - enemy_text.get_width() // 2, 360))
    
    # Total carbon
    total_tonnes = player_tonnes + enemy_tonnes
    total_text = carbon_font.render(f"TOTAL: {total_tonnes:.1f} tonnes CO2", True, (255, 50, 50))
    screen.blit(total_text, (breedte // 2 - total_text.get_width() // 2, 420))
    
    # Environmental message
    if total_tonnes > 10:
        message = "Catastrophic environmental damage!"
        color = (255, 0, 0)
    elif total_tonnes > 5:
        message = "Significant environmental impact"
        color = (255, 100, 0)
    else:
        message = "Moderate environmental impact"
        color = (255, 200, 0)
    
    message_text = overview_font.render(message, True, color)
    screen.blit(message_text, (breedte // 2 - message_text.get_width() // 2, 480))
    
    # Instructions
    instruction_text = overview_font.render("Press ENTER to return to menu", True, (255, 255, 255))
    screen.blit(instruction_text, (breedte // 2 - instruction_text.get_width() // 2, 550))
    
    # Show current coins
    draw_coin_display(screen)


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
                # Add battle carbon to persistent totals
                total_player_carbon += battle_system.player_carbon
                total_enemy_carbon += battle_system.enemy_carbon
                
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
                
                # Check if player can afford anything
                if not can_afford_anything():
                    current_state = GameState.GAME_OVER
                else:
                    current_state = GameState.SHOP
                gekozen_team = None
            elif current_state == GameState.GAME_OVER and event.key == pygame.K_RETURN:
                # Reset game and return to menu
                total_player_carbon = 0
                total_enemy_carbon = 0
                player_coins = 100
                rendering.arena_team = []
                current_state = GameState.MENU
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
                    # Set persistent carbon values
                    battle_system.player_carbon = total_player_carbon
                    battle_system.enemy_carbon = total_enemy_carbon

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
            elif battle_system.battle_result == "world_ends":
                # No coins when world ends - everyone loses
                pass
            battle_system.coins_awarded = True  # Mark as awarded
    elif current_state == GameState.RESULT:
        result_screen(screen, gekozen_team)
    elif current_state == GameState.GAME_OVER:
        game_over_screen(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()