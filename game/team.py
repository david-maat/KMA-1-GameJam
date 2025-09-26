from game.dinosaur import DinoSprite as Dinosaur
class Team:
    def __init__(self, dinosaurs: list[Dinosaur]):
        self.dinosaurs = dinosaurs

    def add_dinosaur(self, dinosaur: Dinosaur):
        self.dinosaurs.append(dinosaur)


    def get_front(self) -> Dinosaur | None:
        # Attack from back to front - return last alive dinosaur
        for dinosaur in reversed(self.dinosaurs):
            if dinosaur.is_alive():
                return dinosaur
        return None

    def remove_dead(self):
        self.dinosaurs = [d for d in self.dinosaurs if d.is_alive()]

    def is_defeated(self) -> bool:
        return all(not d.is_alive() for d in self.dinosaurs)