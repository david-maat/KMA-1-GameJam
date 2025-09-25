import pygame
import sys
import math

pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle Arena")
clock = pygame.time.Clock()

# Kleuren
SKY = (140, 200, 255)
GRASS = (60, 160, 60)
DIRT = (210, 180, 140)
DIRT_DARK = (170, 140, 100)
STONE_DARK = (70, 50, 40)
STONE_MED = (100, 70, 50)
STONE_LIGHT = (140, 100, 70)
BLUE_LIGHT = (120, 170, 255)
BLUE_DARK = (70, 110, 180)

font = pygame.font.SysFont("arial", 16)

# --- Dino class ---
class Dino:
    def __init__(self, name, atk, hp, color, shape="circle"):
        self.name = name
        self.atk = atk
        self.hp = hp
        self.color = color
        self.shape = shape
        self.size = 20
        self.pos = (0, 0)

    def draw(self, surface):
        x, y = self.pos
        # figuur
        if self.shape == "circle":
            pygame.draw.circle(surface, self.color, (x, y), self.size)
        elif self.shape == "square":
            pygame.draw.rect(surface, self.color, (x - self.size, y - self.size, self.size * 2, self.size * 2))
        elif self.shape == "triangle":
            points = [(x, y - self.size), (x - self.size, y + self.size), (x + self.size, y + self.size)]
            pygame.draw.polygon(surface, self.color, points)

        # stats
        atk_text = font.render(str(self.atk), True, (255, 0, 0))
        hp_text = font.render(str(self.hp), True, (0, 200, 0))
        surface.blit(atk_text, (x - 12, y + self.size + 3))
        surface.blit(hp_text, (x + 4, y + self.size + 3))


# --- Teams (voorbeeld) ---
player_team = [
    Dino("T-Rex", 10, 40, (200, 50, 50), "circle"),
    Dino("Mammoth", 7, 60, (150, 100, 50), "square"),
    Dino("Dodo", 3, 20, (100, 200, 250), "triangle"),
    Dino("Triceratops", 6, 50, (0, 150, 0), "square"),
]

enemy_team = [
    Dino("Saber", 8, 35, (250, 200, 50), "circle"),
    Dino("Pterosaur", 5, 25, (180, 180, 255), "triangle"),
    Dino("Ankylo", 7, 55, (160, 160, 60), "square"),
    Dino("Megalodon", 12, 45, (50, 100, 200), "circle"),
]

# --- Posities berekenen ---
def position_teams(path_y):
    spacing = 90
    for i, dino in enumerate(player_team):
        dino.pos = (100 + i * spacing, path_y)
    for i, dino in enumerate(enemy_team):
        dino.pos = (WIDTH - (100 + (len(enemy_team) - 1 - i) * spacing), path_y)

# --- Achtergrond tekenen ---
def draw_left(surface):
    # lucht
    surface.fill(SKY, (0, 0, WIDTH // 2, HEIGHT))

    # bergen
    pygame.draw.polygon(surface, (80, 160, 80), [(0, HEIGHT // 2), (150, 150), (300, HEIGHT // 2)])
    pygame.draw.polygon(surface, (100, 180, 100), [(200, HEIGHT // 2), (350, 100), (500, HEIGHT // 2)])
    pygame.draw.polygon(surface, (60, 120, 60), [(400, HEIGHT // 2), (500, 180), (WIDTH // 2, HEIGHT // 2)])

    # grasstrook
    for i in range(0, WIDTH // 2, 40):
        pygame.draw.circle(surface, GRASS, (i, HEIGHT // 2), 30)
    pygame.draw.rect(surface, GRASS, (0, HEIGHT // 2, WIDTH // 2, 50))

    # pad
    path_top = HEIGHT // 2 + 50
    path_height = 120
    # golvende bovenkant
    wave_points = []
    for x in range(0, WIDTH // 2 + 40, 40):
        y = path_top + 10 * math.sin(x / 40)
        wave_points.append((x, y))
    wave_points += [(WIDTH // 2, HEIGHT), (0, HEIGHT)]
    pygame.draw.polygon(surface, DIRT, wave_points)
    pygame.draw.line(surface, DIRT_DARK, (0, path_top), (WIDTH // 2, path_top), 3)

    return path_top + path_height // 2 - 30  # midden van pad


def draw_right(surface):
    # basis grot
    pygame.draw.rect(surface, STONE_DARK, (WIDTH // 2, 0, WIDTH // 2, HEIGHT))

    # contouren
    pygame.draw.polygon(surface, STONE_MED, [
        (WIDTH // 2, 0), (WIDTH // 2 + 100, 100), (WIDTH - 150, 50),
        (WIDTH, 200), (WIDTH, HEIGHT // 2), (WIDTH // 2, HEIGHT // 2)
    ])
    pygame.draw.polygon(surface, STONE_LIGHT, [
        (WIDTH // 2, HEIGHT // 2), (WIDTH, HEIGHT // 2),
        (WIDTH, HEIGHT), (WIDTH // 2, HEIGHT)
    ])

    # stalactieten
    for x in [WIDTH // 2 + 80, WIDTH // 2 + 200, WIDTH // 2 + 320]:
        pygame.draw.polygon(surface, STONE_MED, [(x, 0), (x + 30, 0), (x + 15, 80)])

    # lichtopeningen
    pygame.draw.circle(surface, BLUE_LIGHT, (WIDTH // 2 + 180, 160), 60)
    pygame.draw.circle(surface, BLUE_DARK, (WIDTH - 200, 220), 90)

    # pad
    path_top = HEIGHT // 2 + 50
    path_height = 120
    pygame.draw.rect(surface, STONE_LIGHT, (WIDTH // 2, path_top, WIDTH // 2, path_height))
    pygame.draw.line(surface, STONE_MED, (WIDTH // 2, path_top), (WIDTH, path_top), 3)

    return path_top + path_height // 2 - 30  # midden van pad


# --- Main loop ---
while True:
    path_left = draw_left(screen)
    path_right = draw_right(screen)

    # beide teams krijgen hun pad-middenhoogte
    position_teams(path_left)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # middenlijn
    pygame.draw.line(screen, (0, 0, 0), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 4)

    # dinos
    for d in player_team:
        d.draw(screen)
    for d in enemy_team:
        d.draw(screen)

    pygame.display.flip()
    clock.tick(60)
