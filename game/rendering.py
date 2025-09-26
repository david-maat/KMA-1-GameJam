import pygame
import os
import random
from game.dinosaur import DinoSprite

WIDTH, HEIGHT = 1200, 700
font = pygame.font.Font(None, 18)

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

# --- Dino pool ---
dino_pool = [
    ("T-Rex", 3, 1, 2, "trex.png"),
    ("Triceratops", 4, 1, 2, "Triceratops.png"),
    ("Stegosaurus", 4, 1, 2, "Stegosaurus.png"),
    ("Brachiosaurus", 5, 1, 3, "Brachiosaurus.png"),
    ("Diplodocus", 5, 1, 3, "Diplodocus.png"),
    ("Velociraptor", 2, 2, 2, "Velociraptor.png"),
    ("Spinosaurus", 4, 2, 3, "Spinosaurus.png"),
    ("Ankylosaurus", 5, 1, 3, "Ankylosaurus.png"),
    ("Parasaurolophus", 3, 1, 2, "Parasaurolophus.png"),
    ("Pterodactyl", 2, 2, 2, "Pterodactyl.png"),
]

starter_dinos = dino_pool[:4]

# --- Helpers ---
def create_dino(data, pos):
    name, hp, atk, oil, image_file = data
    return DinoSprite(name, hp, atk, oil, image_file, pos)

def fill_shop(shop_y):
    shop_dinos.clear()
    spacing = WIDTH // 5
    if round_counter <= 2:
        for i, data in enumerate(starter_dinos):
            shop_dinos.append(create_dino(data, (spacing * (i+1), shop_y)))
    else:
        for i in range(4):
            shop_dinos.append(create_dino(random.choice(dino_pool), (spacing * (i+1), shop_y)))

def update_arena_positions(arena_y):
    if not arena_team:
        return
    spacing = WIDTH // (len(arena_team) + 1)
    for i, dino in enumerate(arena_team):
        if not dino.dragging:
            dino.pos = [spacing * (i+1), arena_y]

def reorder_arena(arena_y):
    global arena_team
    arena_team.sort(key=lambda d: d.pos[0])
    update_arena_positions(arena_y)

# --- API ---
def init_rendering():
    global font, bg_image, start_button
    pygame.font.init()
    font = pygame.font.Font(None, 18)

    # achtergrond
    bg_path = os.path.join(ASSETS_DIR, "classic.jpg")
    bg_image = pygame.image.load(bg_path).convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    # init shop
    shop_y = int(HEIGHT * 0.8)
    fill_shop(shop_y)

    # startknop bovenaan in het midden
    start_button = pygame.Rect(WIDTH//2 - 100, 20, 200, 50)

def handle_event(event, arena_y, shop_y):
    global dragged_dino, offset_x, offset_y, round_counter
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # knop checken
        if start_button.collidepoint(event.pos):
            return "start"

        # shop dinos
        for i, dino in enumerate(shop_dinos):
            if dino.is_clicked(event.pos):
                if len(arena_team) < MAX_ARENA:
                    arena_team.append(dino)
                    reorder_arena(arena_y)
                    spacing = WIDTH // 5
                    if round_counter <= 2:
                        shop_dinos[i] = create_dino(starter_dinos[i], (spacing*(i+1), shop_y))
                    else:
                        shop_dinos[i] = create_dino(random.choice(dino_pool), (spacing*(i+1), shop_y))
                return
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


def draw(screen):
    # achtergrond tekenen
    screen.blit(bg_image, (0, 0))

    # posities
    arena_y = int(HEIGHT * 0.65) -100
    shop_y = int(HEIGHT * 0.85) -80

    # dinos tekenen
    for dino in shop_dinos:
        dino.draw(screen)
    for dino in arena_team:
        dino.draw(screen)

    # ronde nummer
    round_text = font.render(f"Ronde: {round_counter}", True, (0, 0, 0))
    screen.blit(round_text, (10, 10))

    # start knop (bovenaan in het midden)
    pygame.draw.rect(screen, (0, 200, 0), start_button, border_radius=10)
    text = font.render("START BATTLE", True, (255, 255, 255))
    screen.blit(text, (start_button.centerx - text.get_width()//2,
                       start_button.centery - text.get_height()//2))

    return arena_y, shop_y