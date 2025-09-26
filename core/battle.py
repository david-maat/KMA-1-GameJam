from core.team import Team

class Battle:
    #rewrite so team a and team b are of the class Team
    def __init__ (self, team_a: Team, team_b: Team, oil_oints_a, oil_points_b):
        self.team_a = team_a
        self.team_b = team_b
        self.oil_points_a = oil_oints_a
        self.oil_points_b = oil_points_b
        self.turn_count = 0
    
    def battle_turn(self):
        attacker_a = self.team_a.get_front()
        attacker_b = self.team_b.get_front()

        if attacker_a and attacker_b:
            # Team A attacks Team B
            attacker_a.attack_target(attacker_b)
            if not attacker_b.is_alive():
                self.oil_points_a += attacker_b.oil_value
                self.team_b.remove_dead()

            # Team B attacks Team A
            if self.team_b.get_front():
                attacker_b = self.team_b.get_front()
                attacker_b.attack_target(attacker_a)
                if not attacker_a.is_alive():
                    self.oil_points_b += attacker_a.oil_value
                    self.team_a.remove_dead()

        self.turn_count += 1
    
    def is_over(self) -> bool:
        return self.team_a.is_defeated() or self.team_b.is_defeated()
