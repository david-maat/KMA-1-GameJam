import pygame
import os
import random
from game.dinosaur import DinoSprite

WIDTH, HEIGHT = 1200, 700
font = pygame.font.Font(None, 18)
price_font = pygame.font.Font(None, 24)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

bg_image = None
arena_team = []
shop_dinos = []
round_counter = 1
dragged_dino = None
offset_x, offset_y = 0, 0
MAX_ARENA = 6

# Start-knop
start_button = None

# --- Dino sprite class ---

# --- Dino pool with prices (name, hp, atk, oil, image_file, price) ---
dino_pool = [
    ("T-Rex", 3, 1, 2, "trex.png", 30),
    ("Triceratops", 4, 1, 2, "Triceratops.png", 25),
    ("Stegosaurus", 4, 1, 2, "Stegosaurus.png", 25),
    ("Brachiosaurus", 5, 1, 3, "Brachiosaurus.png", 40),
    ("Diplodocus", 5, 1, 3, "Diplodocus.png", 40),
    ("Velociraptor", 2, 2, 2, "Velociraptor.png", 20),
    ("Spinosaurus", 4, 2, 3, "Spinosaurus.png", 35),
    ("Ankylosaurus", 5, 1, 3, "Ankylosaurus.png", 40),
    ("Parasaurolophus", 3, 1, 2, "Parasaurolophus.png", 20),
    ("Pterodactyl", 2, 2, 2, "Pterodactyl.png", 20),
]

starter_dinos = dino_pool[:4]


# --- Helpers ---
def create_dino(data, pos):
    if len(data) == 6:  # Format: (name, hp, atk, oil, image_file, price)
        name, hp, atk, oil, image_file, price = data
        dino = DinoSprite(name, hp, atk, oil, image_file, pos)
        dino.price = price
        return dino
    else:  # Old format: (name, hp, atk, oil, image_file) - add default price
        name, hp, atk, oil, image_file = data
        dino = DinoSprite(name, hp, atk, oil, image_file, pos)
        dino.price = 15  # Default price for backwards compatibility
        return dino


def fill_shop(shop_y):
    shop_dinos.clear()
    spacing = WIDTH // 5
    if round_counter <= 2:
        for i, data in enumerate(starter_dinos):
            shop_dinos.append(create_dino(data, (spacing * (i + 1), shop_y)))
    else:
        for i in range(4):
            shop_dinos.append(create_dino(random.choice(dino_pool), (spacing * (i + 1), shop_y)))


def update_arena_positions(arena_y):
    if not arena_team:
        return
    spacing = WIDTH // (len(arena_team) + 1)
    for i, dino in enumerate(arena_team):
        if not dino.dragging:
            dino.pos = [spacing * (i + 1), arena_y]


def reorder_arena(arena_y):
    global arena_team
    arena_team.sort(key=lambda d: d.pos[0])
    update_arena_positions(arena_y)


def draw_shop_prices(screen, shop_y):
    """Draw prices under shop dinosaurs"""
    for dino in shop_dinos:
        if hasattr(dino, 'price'):
            price_text = price_font.render(f"${dino.price}", True, (255, 215, 0))  # Gold color
            price_shadow = price_font.render(f"${dino.price}", True, (0, 0, 0))  # Black shadow

            # Position under the dinosaur
            text_x = dino.pos[0] - price_text.get_width() // 2
            text_y = shop_y + 40

            # Draw shadow slightly offset
            screen.blit(price_shadow, (text_x + 1, text_y + 1))
            screen.blit(price_text, (text_x, text_y))


# --- API ---
def init_rendering():
    global font, price_font, bg_image, start_button
    pygame.font.init()
    font = pygame.font.Font(None, 18)
    price_font = pygame.font.Font(None, 24)

    # achtergrond
    bg_path = os.path.join(ASSETS_DIR, "classic.jpg")
    bg_image = pygame.image.load(bg_path).convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    # init shop
    shop_y = int(HEIGHT * 0.8)
    fill_shop(shop_y)

    # startknop bovenaan in het midden
    start_button = pygame.Rect(WIDTH // 2 - 100, 20, 200, 50)


def handle_event(event, arena_y, shop_y, coin_check=None, coin_spend=None):
    global dragged_dino, offset_x, offset_y, round_counter

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # knop checken
        if start_button.collidepoint(event.pos):
            return "start"

        # shop dinos - with coin checking
        for i, dino in enumerate(shop_dinos):
            if dino.is_clicked(event.pos):
                if len(arena_team) < MAX_ARENA:
                    # Check if player can afford this dinosaur
                    dino_price = getattr(dino, 'price', 15)

                    if coin_check and not coin_check(dino_price):
                        return "insufficient_funds"

                    # Player can afford it - spend coins and add to arena
                    if coin_spend:
                        coin_spend(dino_price)

                    arena_team.append(dino)
                    reorder_arena(arena_y)
                    spacing = WIDTH // 5
                    if round_counter <= 2:
                        shop_dinos[i] = create_dino(starter_dinos[i], (spacing * (i + 1), shop_y))
                    else:
                        shop_dinos[i] = create_dino(random.choice(dino_pool), (spacing * (i + 1), shop_y))
                return "purchase_made"

        # arena dinos
        for dino in arena_team:
            if dino.is_clicked(event.pos):
                dragged_dino = dino
                dino.dragging = True
                offset_x = dino.pos[0] - event.pos[0]
                offset_y = dino.pos[1] - event.pos[1]
                return

    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        if dragged_dino:
            dragged_dino.dragging = False
            dragged_dino = None
            reorder_arena(arena_y)

    elif event.type == pygame.MOUSEMOTION:
        if dragged_dino and dragged_dino.dragging:
            dragged_dino.pos[0] = event.pos[0] + offset_x
            dragged_dino.pos[1] = event.pos[1] + offset_y

    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        round_counter += 1
        fill_shop(shop_y)


def draw(screen, player_coins=None):
    # achtergrond tekenen
    screen.blit(bg_image, (0, 0))

    # posities
    arena_y = int(HEIGHT * 0.65) - 100
    shop_y = int(HEIGHT * 0.85) - 80

    # dinos tekenen
    for dino in shop_dinos:
        dino.draw(screen)

        # Visual feedback for affordability
        if player_coins is not None and hasattr(dino, 'price'):
            if player_coins < dino.price:
                # Darken unaffordable dinosaurs
                overlay = pygame.Surface((dino.size * 2, dino.size * 2))
                overlay.set_alpha(128)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (dino.pos[0] - dino.size, dino.pos[1] - dino.size))

    for dino in arena_team:
        dino.draw(screen)

    # Draw shop prices
    draw_shop_prices(screen, shop_y)

    # Draw labels for arena and shop
    arena_label = font.render("ARENA", True, (255, 255, 255))
    screen.blit(arena_label, (10, arena_y - 30))

    shop_label = font.render("SHOP", True, (255, 255, 255))
    screen.blit(shop_label, (10, shop_y - 30))

    # ronde nummer
    round_text = font.render(f"Ronde: {round_counter}", True, (0, 0, 0))
    screen.blit(round_text, (10, 10))

    # Arena count
    arena_count_text = font.render(f"Arena: {len(arena_team)}/{MAX_ARENA}", True, (0, 0, 0))
    screen.blit(arena_count_text, (10, 30))

    # start knop (bovenaan in het midden) - color based on arena team
    button_color = (0, 200, 0) if len(arena_team) > 0 else (100, 100, 100)
    pygame.draw.rect(screen, button_color, start_button, border_radius=10)
    text = font.render("START BATTLE", True, (255, 255, 255))
    screen.blit(text, (start_button.centerx - text.get_width() // 2,
                       start_button.centery - text.get_height() // 2))

    return arena_y, shop_y