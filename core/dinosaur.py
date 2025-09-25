class Dinosaur:
    def __init__(self, name, hp, attack, oil_value):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.oil_value = oil_value

    def is_alive(self):
        return self.hp > 0
    
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
    
    def attack_target(self, target):
        target.take_damage(self.attack)