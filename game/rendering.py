import pygame
import sys
import random

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Extinct Animals - Arena")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 14)

# --- Achtergrond genereren ---
def generate_mountains(layers=3):
    """Genereer vaste bergen in de bovenste helft."""
    mountains = []
    step = 150
    base_heights = [160, 200, 240]  # bergen in bovenste helft
    colors = [(90, 140, 90), (110, 170, 110), (140, 200, 140)]
    for i in range(layers):
        color = colors[i]
        points = []
        for x in range(0, WIDTH + step, step):
            peak_y = base_heights[i] + random.randint(-30, 30)
            points.append((x, peak_y))
        points.append((WIDTH, HEIGHT // 2))
        points.append((0, HEIGHT // 2))
        mountains.append((color, points))
    return mountains

mountain_layers = generate_mountains()

def draw_background(surface):
    # --- lucht ---
    surface.fill((135, 206, 235))  # Sky blue

    # --- bergen (bovenste helft) ---
    for color, points in mountain_layers:
        pygame.draw.polygon(surface, color, points)

    # --- grasstrook (onderste helft) ---
    pygame.draw.rect(surface, (34, 139, 34), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

    # --- arena pad ---
    arena_y_top = HEIGHT * 0.60
    arena_height = 80
    pygame.draw.rect(surface, (205, 170, 125), (0, arena_y_top, WIDTH, arena_height))
    pygame.draw.line(surface, (120, 90, 60), (0, arena_y_top), (WIDTH, arena_y_top), 4)

    # --- shop pad ---
    shop_y_top = HEIGHT * 0.78
    shop_height = 80
    pygame.draw.rect(surface, (222, 184, 135), (0, shop_y_top, WIDTH, shop_height))
    pygame.draw.line(surface, (120, 90, 60), (0, shop_y_top), (WIDTH, shop_y_top), 4)

    return arena_y_top + arena_height // 2, shop_y_top + shop_height // 2


# --- Dino class ---
class ExtinctAnimal:
    def __init__(self, name, attack, hp, oil, color, pos, shape="circle"):
        self.name = name
        self.attack = attack
        self.hp = hp
        self.oil = oil
        self.color = color
        self.pos = list(pos)
        self.size = 25
        self.shape = shape
        self.dragging = False

    def draw(self, surface):
        x, y = self.pos
        if self.shape == "circle":
            pygame.draw.circle(surface, self.color, (x, y), self.size)
        elif self.shape == "square":
            rect = pygame.Rect(x - self.size, y - self.size, self.size * 2, self.size * 2)
            pygame.draw.rect(surface, self.color, rect)
        elif self.shape == "triangle":
            points = [(x, y - self.size), (x - self.size, y + self.size), (x + self.size, y + self.size)]
            pygame.draw.polygon(surface, self.color, points)

        # Naam erboven
        text = font.render(self.name, True, (255, 255, 255))
        surface.blit(text, (x - text.get_width() // 2, y - self.size - 18))

    def is_clicked(self, mouse_pos):
        x, y = self.pos
        mx, my = mouse_pos
        return (x - self.size <= mx <= x + self.size) and (y - self.size <= my <= y + self.size)


# --- Dino Pool (10 soorten) ---
dino_pool = [
    ("T-Rex", 10, 50, 20, (200, 50, 50), "circle"),
    ("Mammoth", 7, 60, 15, (150, 100, 50), "square"),
    ("Dodo", 3, 20, 5, (100, 200, 250), "triangle"),
    ("Saber-tooth", 8, 40, 12, (250, 200, 50), "circle"),
    ("Triceratops", 6, 55, 18, (0, 150, 0), "square"),
    ("Pterosaur", 5, 30, 10, (180, 180, 255), "triangle"),
    ("Glyptodon", 4, 70, 14, (120, 80, 40), "square"),
    ("Megalodon", 12, 45, 22, (50, 100, 200), "circle"),
    ("Ankylosaurus", 7, 65, 19, (160, 160, 60), "square"),
    ("Gastornis", 5, 35, 8, (220, 140, 180), "triangle"),
]

# --- Eerste vaste dinos (ronde 1-2) ---
starter_dinos = [
    ("T-Rex", 10, 50, 20, (200, 50, 50), "circle"),
    ("Mammoth", 7, 60, 15, (150, 100, 50), "square"),
    ("Dodo", 3, 20, 5, (100, 200, 250), "triangle"),
    ("Saber-tooth", 8, 40, 12, (250, 200, 50), "circle"),
]

# --- Functies ---
def create_random_dino(x, y):
    name, atk, hp, oil, color, shape = random.choice(dino_pool)
    return ExtinctAnimal(name, atk, hp, oil, color, (x, y), shape)

arena_team = []
shop_dinos = []
round_counter = 1  # start bij ronde 1

def fill_shop(shop_y):
    """Vul de shop afhankelijk van de ronde."""
    shop_dinos.clear()
    spacing = WIDTH // 5
    if round_counter <= 2:
        for i, data in enumerate(starter_dinos):
            name, atk, hp, oil, color, shape = data
            shop_dinos.append(ExtinctAnimal(name, atk, hp, oil, color, (spacing * (i + 1), shop_y), shape))
    else:
        for i in range(4):
            shop_dinos.append(create_random_dino(spacing * (i + 1), shop_y))

def update_arena_positions(arena_y):
    """Zet arena dieren netjes verdeeld op arena-pad."""
    if not arena_team:
        return
    spacing = WIDTH // (len(arena_team) + 1)
    for i, animal in enumerate(arena_team):
        if not animal.dragging:
            x = spacing * (i + 1)
            animal.pos = [x, arena_y]

def reorder_arena(arena_y):
    """Sorteer arena_team op basis van x-positie."""
    global arena_team
    arena_team.sort(key=lambda a: a.pos[0])
    update_arena_positions(arena_y)


# --- Init shop ---
_, shop_y_init = draw_background(screen)
fill_shop(shop_y_init)

# --- Main loop ---
dragged_animal = None
offset_x = 0
offset_y = 0
MAX_ARENA = 6

while True:
    arena_y, shop_y = draw_background(screen)  # geeft Y-posities terug

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # check shop dinos
            for i, animal in enumerate(shop_dinos):
                if animal.is_clicked(event.pos):
                    if len(arena_team) < MAX_ARENA:
                        arena_team.append(animal)
                        reorder_arena(arena_y)
                        spacing = WIDTH // 5
                        if round_counter <= 2:
                            # zelfde soort terugzetten
                            data = starter_dinos[i]
                            name, atk, hp, oil, color, shape = data
                            shop_dinos[i] = ExtinctAnimal(name, atk, hp, oil, color, (spacing * (i + 1), shop_y), shape)
                        else:
                            # random vanaf ronde 3
                            shop_dinos[i] = create_random_dino(spacing * (i + 1), shop_y)
                    break

            # check arena dinos
            for animal in arena_team:
                if animal.is_clicked(event.pos):
                    dragged_animal = animal
                    animal.dragging = True
                    offset_x = animal.pos[0] - event.pos[0]
                    offset_y = animal.pos[1] - event.pos[1]
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragged_animal:
                dragged_animal.dragging = False
                dragged_animal = None
                reorder_arena(arena_y)

        elif event.type == pygame.MOUSEMOTION:
            if dragged_animal and dragged_animal.dragging:
                dragged_animal.pos[0] = event.pos[0] + offset_x
                dragged_animal.pos[1] = event.pos[1] + offset_y

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                round_counter += 1
                fill_shop(shop_y)  # vernieuw shop bij nieuwe ronde
                print(f"Nieuwe ronde: {round_counter}")

    # --- tekenen ---
    draw_background(screen)
    for animal in shop_dinos:
        animal.draw(screen)
    for animal in arena_team:
        animal.draw(screen)

    # toon ronde nummer
    round_text = font.render(f"Ronde: {round_counter}", True, (0, 0, 0))
    screen.blit(round_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)
