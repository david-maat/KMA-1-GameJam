import pygame
import random
import time
from game.dinosaur import DinoSprite
from game.team import Team

class BattleSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.battle_log = []
        self.current_turn = 0  # 0 = player, 1 = enemy
        self.battle_phase = "idle"  # idle, attacking, battle_over
        self.selected_attacker = None
        self.selected_target = None
        self.animation_timer = 0
        self.battle_result = None  # "player_wins", "enemy_wins", "world_ends", None
        self.turn_delay = 0
        
        # Carbon meter system
        self.max_carbon = 20  # Maximum carbon before world ends
        self.player_carbon = 0  # Carbon from enemy deaths
        self.enemy_carbon = 0   # Carbon from player deaths
        
        # Battle UI elements
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.large_font = pygame.font.SysFont("Arial", 36, bold=True)
        
        # Available dinosaur templates for random enemy teams
        # Match the shop/arena scale (rendering.dino_pool): hp 2-5, atk 1-2 (some 3), oil ~2-3
        self.dinosaur_templates = [
            {"name": "T-Rex", "hp": 3, "atk": 2, "oil_value": 2, "image": "trex.png"},
            {"name": "Spinosaurus", "hp": 4, "atk": 2, "oil_value": 3, "image": "Spinosaurus.png"},
            {"name": "Triceratops", "hp": 4, "atk": 1, "oil_value": 2, "image": "Triceratops.png"},
            {"name": "Stegosaurus", "hp": 4, "atk": 1, "oil_value": 2, "image": "Stegosaurus.png"},
            {"name": "Ankylosaurus", "hp": 5, "atk": 1, "oil_value": 3, "image": "Ankylosaurus.png"},
            {"name": "Brachiosaurus", "hp": 5, "atk": 1, "oil_value": 3, "image": "Brachiosaurus.png"},
            {"name": "Diplodocus", "hp": 5, "atk": 1, "oil_value": 3, "image": "Diplodocus.png"},
            {"name": "Velociraptor", "hp": 2, "atk": 2, "oil_value": 2, "image": "Velociraptor.png"},
            {"name": "Parasaurolophus", "hp": 3, "atk": 1, "oil_value": 2, "image": "Parasaurolophus.png"},
            {"name": "Pterodactyl", "hp": 2, "atk": 2, "oil_value": 2, "image": "Pterodactyl.png"},
        ]
    
    def generate_random_enemy_team(self, team_size=None):
        """Generate a random enemy team with varying sizes and compositions"""
        if team_size is None:
            team_size = random.randint(3, 6)  # Random team size between 3-6
        
        # Create different difficulty tiers
        difficulty = random.choice(["easy", "medium", "hard"])
        
        selected_dinos = []
        available_templates = self.dinosaur_templates.copy()
        
        for i in range(team_size):
            if not available_templates:
                available_templates = self.dinosaur_templates.copy()
            
            template = random.choice(available_templates)
            available_templates.remove(template)  # Avoid duplicates in same team
            
            # Adjust stats based on difficulty
            hp_modifier = 1.0
            atk_modifier = 1.0
            
            if difficulty == "easy":
                hp_modifier = random.uniform(0.9, 1.0)
                atk_modifier = random.uniform(0.9, 1.0)
            elif difficulty == "medium":
                hp_modifier = random.uniform(1.0, 1.1)
                atk_modifier = random.uniform(1.0, 1.1)
            elif difficulty == "hard":
                hp_modifier = random.uniform(1.05, 1.2)
                atk_modifier = random.uniform(1.05, 1.2)
            
            # Create dinosaur with modified stats
            modified_hp = int(template["hp"] * hp_modifier)
            modified_atk = int(template["atk"] * atk_modifier)
            
            # Position on right side of screen
            x_pos = self.screen_width - 150 - (i * 80)
            y_pos = self.screen_height // 2 + random.randint(-50, 50)
            
            dino = DinoSprite(
                name=template["name"],
                hp=modified_hp,
                atk=modified_atk,
                oil_value=template["oil_value"],
                image_file=template["image"],
                pos=(x_pos, y_pos)
            )
            
            selected_dinos.append(dino)
        
        self.add_to_log(f"Enemy team generated! Difficulty: {difficulty.upper()}")
        self.add_to_log(f"Enemy team size: {team_size} dinosaurs")
        
        return Team(selected_dinos)
    
    def start_battle(self, player_team, enemy_team=None, starting_player: int = 0):
        """Initialize a new battle"""
        self.player_team = player_team
        # Scale enemy team size to player's team size (1-6)
        desired_size = max(1, min(len(self.player_team.dinosaurs), 6))
        self.enemy_team = enemy_team if enemy_team else self.generate_random_enemy_team(team_size=desired_size)
        self.battle_log = []
        self.current_turn = starting_player  # 0 = player, 1 = enemy
        self.battle_phase = "idle"
        self.selected_attacker = None
        self.selected_target = None
        self.animation_timer = 0
        self.battle_result = None
        self.turn_delay = 0
        # Reset carbon meters
        self.player_carbon = 0
        self.enemy_carbon = 0
        # Reset coin award flag
        if hasattr(self, 'coins_awarded'):
            delattr(self, 'coins_awarded')
        
        # Position teams
        self.position_teams()
        
        self.add_to_log("Battle begins!")
        self.add_to_log("Front dinosaurs attack in turns!")
    
    def position_teams(self):
        """Position dinosaurs on the battlefield"""
        # Position player team on the left
        if self.player_team.dinosaurs:
            base_y = self.screen_height // 2
            for i, dino in enumerate(self.player_team.dinosaurs):
                x = 150 + (i * 80)
                y = base_y
                dino.pos = [x, y]
        
        # Position enemy team on the right
        if self.enemy_team.dinosaurs:
            base_y = self.screen_height // 2
            for i, dino in enumerate(self.enemy_team.dinosaurs):
                x = self.screen_width - 150 - (i * 80)
                y = base_y
                dino.pos = [x, y]
    
    def add_to_log(self, message):
        """Add a message to the battle log"""
        self.battle_log.append(message)
        if len(self.battle_log) > 8:  # Keep only last 8 messages
            self.battle_log.pop(0)
    
    def handle_click(self, mouse_pos):
        """Clicks are ignored in auto-battle mode"""
        return
    
    def execute_attack(self, attacker, target):
        """Execute an attack between two dinosaurs"""
        if not attacker.is_alive() or not target.is_alive():
            return
        
        # Calculate damage with some randomness
        base_damage = attacker.atk
        damage = random.randint(int(base_damage * 0.8), int(base_damage * 1.2))
        # Guarantee at least 1 damage so battles always progress
        damage = max(1, damage)
        
        # Apply damage
        target.take_damage(damage)
        
        self.add_to_log(f"{attacker.name} attacks {target.name} for {damage} damage!")
        
        if not target.is_alive():
            self.add_to_log(f"{target.name} has been defeated!")
            # Add carbon based on the dead dinosaur's max HP
            carbon_added = target.max_hp
            if self.current_turn == 0:  # Player killed enemy dino
                self.player_carbon += carbon_added
                self.add_to_log(f"Player carbon +{carbon_added} (total: {self.player_carbon})")
            else:  # Enemy killed player dino
                self.enemy_carbon += carbon_added
                self.add_to_log(f"Enemy carbon +{carbon_added} (total: {self.enemy_carbon})")
        
        # Start attack animation
        self.battle_phase = "attacking"
        self.animation_timer = 50  # slower: 50 frames of animation

    def auto_take_turn(self):
        """Perform one automatic turn where front dinosaurs attack each other in order"""
        if self.battle_phase in ("attacking", "battle_over"):
            return
        
        # Determine attacker and target based on current_turn
        if self.current_turn == 0:
            attacker = self.player_team.get_front()
            target = self.enemy_team.get_front()
        else:
            attacker = self.enemy_team.get_front()
            target = self.player_team.get_front()

        if attacker and target:
            self.execute_attack(attacker, target)
    
    def update(self):
        """Update battle state"""
        # Handle turn delays
        if self.turn_delay > 0:
            self.turn_delay -= 1
            return

        # If idle and not animating, perform the next automatic turn
        if self.battle_phase == "idle" and self.animation_timer == 0:
            # If battle already over, stop
            if self.check_battle_end():
                return
            self.auto_take_turn()

        # Handle animations
        if self.animation_timer > 0:
            self.animation_timer -= 1
            if self.animation_timer == 0:
                # Animation finished, check battle state
                if self.check_battle_end():
                    return
                
                # Switch turns and add a brief delay
                if self.current_turn == 0:
                    self.current_turn = 1
                else:
                    self.current_turn = 0
                self.battle_phase = "idle"
                self.turn_delay = 40  # slower delay between turns
                
                # Reset selections
                self.selected_attacker = None
                self.selected_target = None
        
    
    def check_battle_end(self):
        """Check if battle has ended"""
        # Check carbon levels first - world ending takes priority
        if self.player_carbon >= self.max_carbon or self.enemy_carbon >= self.max_carbon:
            self.battle_result = "world_ends"
            self.battle_phase = "battle_over"
            self.add_to_log("CARBON OVERLOAD! The world ends!")
            self.add_to_log("Global warming has destroyed everything!")
            return True
        
        player_alive = any(d.is_alive() for d in self.player_team.dinosaurs)
        enemy_alive = any(d.is_alive() for d in self.enemy_team.dinosaurs)
        
        if not player_alive:
            self.battle_result = "enemy_wins"
            self.battle_phase = "battle_over"
            self.add_to_log("DEFEAT! Enemy team wins!")
            return True
        elif not enemy_alive:
            self.battle_result = "player_wins"
            self.battle_phase = "battle_over"
            self.add_to_log("VICTORY! Player team wins!")
            return True
        
        return False
    
    def draw_health_bar(self, surface, dino, x, y, width=60, height=8):
        """Draw a health bar for a dinosaur"""
        if not hasattr(dino, 'max_hp'):
            dino.max_hp = dino.hp  # Store initial HP as max HP if missing
        max_hp = dino.max_hp if dino.max_hp > 0 else 1
        
        # Background (red)
        pygame.draw.rect(surface, (255, 0, 0), (x, y, width, height))
        
        # Health (green)
        health_width = int((dino.hp / max_hp) * width)
        if health_width > 0:
            pygame.draw.rect(surface, (0, 255, 0), (x, y, health_width, height))
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)
    
    def draw_selection_indicator(self, surface, dino, color):
        """Draw a selection indicator around a dinosaur"""
        x, y = dino.pos
        size = dino.size + 10
        rect = pygame.Rect(x - size//2, y - size//2, size, size)
        pygame.draw.rect(surface, color, rect, 3)
    
    def draw_carbon_meters(self, surface):
        """Draw carbon meters for both players"""
        meter_width = 200
        meter_height = 20
        
        # Player carbon meter (left side)
        player_x = 50
        player_y = self.screen_height - 60
        
        # Background
        pygame.draw.rect(surface, (50, 50, 50), (player_x, player_y, meter_width, meter_height))
        
        # Carbon fill
        player_ratio = self.player_carbon / self.max_carbon if self.max_carbon > 0 else 0
        player_ratio = max(0.0, min(1.0, player_ratio))  # clamp 0..1
        player_fill_width = int(player_ratio * meter_width)
        if player_fill_width > 0:
            # Color changes from green to red as it fills
            red = int(255 * player_ratio)
            green = int(255 * (1 - player_ratio))
            # Clamp color channels
            red = max(0, min(255, red))
            green = max(0, min(255, green))
            color = (red, green, 0)
            pygame.draw.rect(surface, color, (player_x, player_y, player_fill_width, meter_height))
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (player_x, player_y, meter_width, meter_height), 2)
        
        # Label
        player_label = self.font.render(f"Player Carbon: {self.player_carbon}/{self.max_carbon}", True, (255, 255, 255))
        surface.blit(player_label, (player_x, player_y - 25))
        
        # Enemy carbon meter (right side)
        enemy_x = self.screen_width - meter_width - 50
        enemy_y = self.screen_height - 60
        
        # Background
        pygame.draw.rect(surface, (50, 50, 50), (enemy_x, enemy_y, meter_width, meter_height))
        
        # Carbon fill
        enemy_ratio = self.enemy_carbon / self.max_carbon if self.max_carbon > 0 else 0
        enemy_ratio = max(0.0, min(1.0, enemy_ratio))  # clamp 0..1
        enemy_fill_width = int(enemy_ratio * meter_width)
        if enemy_fill_width > 0:
            # Color changes from green to red as it fills
            red = int(255 * enemy_ratio)
            green = int(255 * (1 - enemy_ratio))
            # Clamp color channels
            red = max(0, min(255, red))
            green = max(0, min(255, green))
            color = (red, green, 0)
            pygame.draw.rect(surface, color, (enemy_x, enemy_y, enemy_fill_width, meter_height))
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (enemy_x, enemy_y, meter_width, meter_height), 2)
        
        # Label
        enemy_label = self.font.render(f"Enemy Carbon: {self.enemy_carbon}/{self.max_carbon}", True, (255, 255, 255))
        surface.blit(enemy_label, (enemy_x, enemy_y - 25))
    
    def draw(self, surface):
        """Draw the battle scene"""
        # Clear screen with battlefield background
        surface.fill((101, 67, 33))  # Brown battlefield
        
        # Draw battlefield elements
        pygame.draw.line(surface, (139, 69, 19), (self.screen_width//2, 0), 
                        (self.screen_width//2, self.screen_height), 4)
        
        # Draw teams
        for dino in self.player_team.dinosaurs:
            if dino.is_alive():
                dino.draw(surface)
                # Draw health bar
                x, y = dino.pos
                self.draw_health_bar(surface, dino, x - 30, y - 50)
        
        for dino in self.enemy_team.dinosaurs:
            if dino.is_alive():
                dino.draw(surface)
                # Draw health bar
                x, y = dino.pos
                self.draw_health_bar(surface, dino, x - 30, y - 50)
        
        # Draw carbon meters
        self.draw_carbon_meters(surface)
        
        # Draw UI
        self.draw_ui(surface)
    
    def draw_ui(self, surface):
        """Draw battle UI elements"""
        # Battle log background
        log_rect = pygame.Rect(10, 10, 400, 200)
        pygame.draw.rect(surface, (0, 0, 0, 128), log_rect)
        pygame.draw.rect(surface, (255, 255, 255), log_rect, 2)
        
        # Battle log text
        for i, message in enumerate(self.battle_log):
            text = self.small_font.render(message, True, (255, 255, 255))
            surface.blit(text, (15, 15 + i * 22))
        
        # Turn indicator
        turn_text = "Player Turn" if self.current_turn == 0 else "Enemy Turn"
        turn_color = (0, 255, 0) if self.current_turn == 0 else (255, 0, 0)
        turn_surface = self.large_font.render(turn_text, True, turn_color)
        surface.blit(turn_surface, (self.screen_width//2 - turn_surface.get_width()//2, 10))
        
        # Phase indicator
        phase_text = ""
        if self.battle_phase == "attacking":
            phase_text = "Attack in progress..."
        elif self.battle_phase == "battle_over":
            phase_text = "Battle Over! Press ENTER to continue"
        else:
            phase_text = "Front dinos attack automatically"
        
        if phase_text:
            phase_surface = self.font.render(phase_text, True, (255, 255, 255))
            surface.blit(phase_surface, (self.screen_width//2 - phase_surface.get_width()//2, 50))
        
        # Team status
        player_alive = sum(1 for d in self.player_team.dinosaurs if d.is_alive())
        enemy_alive = sum(1 for d in self.enemy_team.dinosaurs if d.is_alive())
        
        status_text = f"Player: {player_alive} alive | Enemy: {enemy_alive} alive"
        status_surface = self.font.render(status_text, True, (255, 255, 255))
        surface.blit(status_surface, (self.screen_width//2 - status_surface.get_width()//2, 
                                    self.screen_height - 30))
