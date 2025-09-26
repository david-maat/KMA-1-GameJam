import pygame
import os

# --- Pad naar assets ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# --- Fonts laden ---
def load_fonts():
    try:
        cartoon_font_path = os.path.join(ASSETS_DIR, "cartoon.ttf")
        vs_font = pygame.font.Font(cartoon_font_path, 100)
        label_font = pygame.font.Font(cartoon_font_path, 50)
    except:
        vs_font = pygame.font.SysFont("comic sans ms", 100, bold=True)
        label_font = pygame.font.SysFont("comic sans ms", 50, bold=True)
    return vs_font, label_font

# --- Dino class ---
class Dino:
    def __init__(self, name, atk, hp, image_file, flip=False):
        self.name = name
        self.atk = atk
        self.hp = hp
        self.size = 80
        self.pos = (0, 0)

        path = os.path.join(ASSETS_DIR, image_file)
        img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(img, (self.size, self.size))

        if flip:  # spiegel horizontaal voor enemy team
            self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, surface):
        x, y = self.pos
        rect = self.image.get_rect(center=(x, y))
        surface.blit(self.image, rect)

# --- Enemy team factory ---
def create_enemy_team():
    return [
        Dino("Spinosaurus", 11, 50, "Spinosaurus.png", flip=True),
        Dino("Ankylosaurus", 7, 65, "Ankylosaurus.png", flip=True),
        Dino("Parasaurolophus", 6, 55, "Parasaurolophus.png", flip=True),
        Dino("Pterodactyl", 8, 45, "Pterodactyl.png", flip=True),
        Dino("Triceratops", 8, 55, "Triceratops.png", flip=True),
        Dino("Velociraptor", 9, 35, "Velociraptor.png", flip=True),
    ]

# --- Helpers ---
def position_teams(player_team, enemy_team, path_y, screen_width):
    # Links (player)
    if player_team:
        left_margin = 80
        right_margin = screen_width // 2 - 80
        spacing_left = (right_margin - left_margin) // (len(player_team) - 1 if len(player_team) > 1 else 1)
        for i, dino in enumerate(player_team):
            dino.pos = (left_margin + i * spacing_left, path_y)

    # Rechts (enemy)
    if enemy_team:
        left_margin = screen_width // 2 + 80
        right_margin = screen_width - 80
        spacing_right = (right_margin - left_margin) // (len(enemy_team) - 1 if len(enemy_team) > 1 else 1)
        for i, dino in enumerate(enemy_team):
            dino.pos = (left_margin + i * spacing_right, path_y)

# --- Battle scherm tekenen ---
def draw_battle(screen, player_team, enemy_team, vs_font, label_font, path_y):
    WIDTH, HEIGHT = screen.get_size()

    # Achtergronden tekenen
    bg_left = pygame.image.load(os.path.join(ASSETS_DIR, "classic.jpg"))
    bg_right = pygame.image.load(os.path.join(ASSETS_DIR, "desert.jpg"))
    bg_left = pygame.transform.scale(bg_left, (WIDTH // 2, HEIGHT))
    bg_right = pygame.transform.scale(bg_right, (WIDTH // 2, HEIGHT))
    screen.blit(bg_left, (0, 0))
    screen.blit(bg_right, (WIDTH // 2, 0))

    # middenlijn
    pygame.draw.line(screen, (0, 0, 0), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 4)

    # VS tekst
    vs_text = vs_font.render("VS", True, (0, 0, 0))
    screen.blit(vs_text, (WIDTH // 2 - vs_text.get_width() // 2, 60))

    # Player labels
    p1_text = label_font.render("Player 1", True, (0, 0, 0))
    screen.blit(p1_text, (200, 70))
    p2_text = label_font.render("Player 2", True, (0, 0, 0))
    screen.blit(p2_text, (WIDTH - p2_text.get_width() - 200, 70))

    # Zet teams netjes verdeeld
    position_teams(player_team, enemy_team, path_y, WIDTH)

    # Dinos tekenen
    for d in player_team:
        d.draw(screen)
    for d in enemy_team:
        d.draw(screen)



    # # dinos tekenen
    # stat_font = pygame.font.SysFont("arial", 16)
    # for d in player_te
    #am:
    #     d.draw(screen)
    # for d in enemy_team:
    #     d.draw(screen)


# import pyg
#ame
# import sys
# import os
#
# pygame.init()
# WIDTH, HEIGHT = 1200, 700
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Battle Arena")
# clock = pygame.time.Clock()
#
# font = pygame.font.SysFont("arial", 16)
#
# # --- Pad naar assets ---
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # ga 1 map omhoog vanaf /game
# ASSETS_DIR = os.path.join(BASE_DIR, "assets")
#
# # --- Cartoon font laden ---
# try:
#     cartoon_font_path = os.path.join(ASSETS_DIR, "cartoon.ttf")  # zorg dat dit bestaat
#     vs_font = pygame.font.Font(cartoon_font_path, 100)
#     label_font = pygame.font.Font(cartoon_font_path, 50)
# except:
#     vs_font = pygame.font.SysFont("comic sans ms", 100, bold=True)
#     label_font = pygame.font.SysFont("comic sans ms", 50, bold=True)
#
# # --- Dino class (alleen sprites) ---
# class Dino:
#     def __init__(self, name, atk, hp, image_file, flip=False):
#         self.name = name
#         self.atk = atk
#         self.hp = hp
#         self.size = 80
#         self.pos = (0, 0)
#
#         path = os.path.join(ASSETS_DIR, image_file)
#         img = pygame.image.load(path).convert_alpha()
#         self.image = pygame.transform.scale(img, (self.size, self.size))
#
#         if flip:  # spiegel horizontaal voor enemy team
#             self.image = pygame.transform.flip(self.image, True, False)
#
#     def draw(self, surface):
#         x, y = self.pos
#         rect = self.image.get_rect(center=(x, y))
#         surface.blit(self.image, rect)
#
#         # # stats eronder
#         # atk_text = font.render(str(self.atk), True, (255, 0, 0))
#         # hp_text = font.render(str(self.hp), True, (0, 200, 0))
#         # surface.blit(atk_text, (x - 20, y + self.size // 2))
#         # surface.blit(hp_text, (x + 10, y + self.size // 2))
#
#
# # --- Teams ---
# player_team = [
#     Dino("T-Rex", 10, 40, "trex.png"),
#     Dino("Triceratops", 8, 55, "Triceratops.png"),
#     Dino("Stegosaurus", 6, 60, "Stegosaurus.png"),
#     Dino("Brachiosaurus", 7, 70, "Brachiosaurus.png"),
#     Dino("Diplodocus", 5, 80, "Diplodocus.png"),
#     Dino("Velociraptor", 9, 35, "Velociraptor.png"),
# ]
#
# enemy_team = [
#     Dino("Spinosaurus", 11, 50, "Spinosaurus.png", flip=True),
#     Dino("Ankylosaurus", 7, 65, "Ankylosaurus.png", flip=True),
#     Dino("Parasaurolophus", 6, 55, "Parasaurolophus.png", flip=True),
#     Dino("Pterodactyl", 8, 45, "Pterodactyl.png", flip=True),
#     Dino("Triceratops", 8, 55, "Triceratops.png", flip=True),
#     Dino("Velociraptor", 9, 35, "Velociraptor.png", flip=True),
# ]
#
# # --- Achtergrond ---
# try:
#     bg_left = pygame.image.load(os.path.join(ASSETS_DIR, "classic.jpg"))
#     bg_right = pygame.image.load(os.path.join(ASSETS_DIR, "desert.jpg"))
# except pygame.error as e:
#     print("Kon de achtergrondafbeeldingen niet laden:", e)
#     pygame.quit()
#     sys.exit()
#
# bg_left = pygame.transform.scale(bg_left, (WIDTH // 2, HEIGHT))
# bg_right = pygame.transform.scale(bg_right, (WIDTH // 2, HEIGHT))
#
# # --- Posities berekenen ---
# def position_teams(path_y):
#     # Links team
#     left_margin = 80
#     right_margin = WIDTH // 2 - 80
#     spacing_left = (right_margin - left_margin) // (len(player_team) - 1)
#     for i, dino in enumerate(player_team):
#         dino.pos = (left_margin + i * spacing_left, path_y)
#
#     # Rechts team
#     left_margin = WIDTH // 2 + 80
#     right_margin = WIDTH - 80
#     spacing_right = (right_margin - left_margin) // (len(enemy_team) - 1)
#     for i, dino in enumerate(enemy_team):
#         dino.pos = (left_margin + i * spacing_right, path_y)
#
# # Dino’s op bovenste pad
# PATH_Y = HEIGHT // 2
#
# # --- Main loop ---
# while True:
#     screen.blit(bg_left, (0, 0))
#     screen.blit(bg_right, (WIDTH // 2, 0))
#
#     # middenlijn
#     pygame.draw.line(screen, (0, 0, 0), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 4)
#
#     # VS
#     vs_text = vs_font.render("VS", True, (0, 0, 0))
#     screen.blit(vs_text, (WIDTH // 2 - vs_text.get_width() // 2, 40))
#
#     # Player labels
#     p1_text = label_font.render("Player 1", True, (0, 0, 0))
#     screen.blit(p1_text, (200, 70))
#
#     p2_text = label_font.render("Player 2", True, (0, 0, 0))
#     screen.blit(p2_text, (WIDTH - p2_text.get_width() - 200, 70))
#
#     # posities zetten
#     position_teams(PATH_Y)
#
#     for e in pygame.event.get():
#         if e.type == pygame.QUIT:
#             pygame.quit()
#             sys.exit()
#
#     for d in player_team:
#         d.draw(screen)
#     for d in enemy_team:
#         d.draw(screen)
#
#     pygame.display.flip()
#     clock.tick(60)
