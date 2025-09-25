# ui.py
import pygame

pygame.init()
font_small = pygame.font.SysFont("arial", 12)
font_medium = pygame.font.SysFont("arial", 16)

# --- HP-bar tekenen ---
def draw_hp_bar(surface, animal, offset_y=35):
    """Tekent een HP-bar boven het dier."""
    x, y = animal.pos
    bar_width = 50
    bar_height = 6
    hp_ratio = max(animal.hp / animal.max_hp, 0)  # gebruik max_hp van het dier
    # achtergrond
    bg_rect = pygame.Rect(x - bar_width // 2, y - offset_y, bar_width, bar_height)
    pygame.draw.rect(surface, (100, 100, 100), bg_rect)

    hp_ratio = max(animal.hp / animal.max_hp, 0)
    text = font_small.render(f"{animal.hp}/{animal.max_hp} HP", True, (255, 255, 255))

    # HP
    hp_rect = pygame.Rect(x - bar_width // 2, y - offset_y, int(bar_width * hp_ratio), bar_height)
    pygame.draw.rect(surface, (200, 50, 50), hp_rect)
    # HP tekst
    text = font_small.render(f"{animal.hp}/{animal.max_hp} HP", True, (255, 255, 255))
    surface.blit(text, (x - text.get_width() // 2, y - offset_y - 12))

# --- Oliepunten tekenen ---
def draw_oil_points(surface, animal, offset_y=25):
    """Tekent oliepunten boven het dier."""
    x, y = animal.pos
    text = font_small.render(f"Oil: {animal.oil}", True, (255, 255, 0))
    surface.blit(text, (x - text.get_width() // 2, y - offset_y))

# --- Knoppen class ---
class Button:
    def __init__(self, rect, text, callback, color=(70, 130, 180), hover_color=(100, 160, 210)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2, border_radius=5)
        text_surf = font_medium.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.centerx - text_surf.get_width() // 2,
                                 self.rect.centery - text_surf.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

# --- Voorbeeld callbacks ---
def start_game():
    print("Game gestart!")

def retry_game():
    print("Retry!")

# --- Knoppen setup ---
def create_ui_buttons():
    start_btn = Button((650, 20, 120, 40), "Start", start_game)
    retry_btn = Button((650, 70, 120, 40), "Retry", retry_game)
    return [start_btn, retry_btn]

# --- Tekenen van alle UI elementen ---
def draw_ui(surface, animals, buttons):
    for animal in animals:
        draw_hp_bar(surface, animal)
        draw_oil_points(surface, animal)
    for btn in buttons:
        btn.draw(surface)

# --- Event handling voor buttons ---
def handle_ui_events(event, buttons):
    for btn in buttons:
        btn.handle_event(event)




