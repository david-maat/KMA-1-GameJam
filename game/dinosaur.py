import os
import pygame
pygame.font.init() 
font = pygame.font.Font(None, 18)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

class DinoSprite:
    def __init__(self, name, hp, atk, oil_value, image_file, pos):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.oil_value = oil_value
        self.size = 80
        self.pos = list(pos)
        self.dragging = False

        path = os.path.join(ASSETS_DIR, image_file)
        img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(img, (self.size, self.size))

        def is_alive(self):
            return self.hp > 0
    
        def take_damage(self, damage):
            self.hp -= damage
            if self.hp < 0:
                self.hp = 0
    
        def attack_target(self, target):
            target.take_damage(self.atk)

    def draw(self, surface):
        x, y = self.pos
        rect = self.image.get_rect(center=(x, y))
        surface.blit(self.image, rect)

        # naam en stats erboven/onder
        text = font.render(self.name, True, (255, 255, 255))
        surface.blit(text, (x - text.get_width()//2, y - self.size//2 - 18))

        hp_text = font.render(f"HP:{self.hp}", True, (0, 255, 0))
        atk_text = font.render(f"ATK:{self.atk}", True, (255, 0, 0))
        surface.blit(hp_text, (x - 30, y + self.size//2))
        surface.blit(atk_text, (x + 10, y + self.size//2))

    def is_clicked(self, mouse_pos):
        rect = self.image.get_rect(center=self.pos)
        return rect.collidepoint(mouse_pos)