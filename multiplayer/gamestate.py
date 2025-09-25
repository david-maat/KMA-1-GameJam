class GameState:
    def __init__(self, players=None, phase="picking", timeRemaining=1):
        self.players = players or {}
        self.phase = phase
        self.timeRemaining = timeRemaining

    def to_dict(self):
        return {
            "players": self.players,
            "phase": self.phase,
            "timeRemaining": self.timeRemaining
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            players=data.get("players", {}),
            phase=data.get("phase", "lobby"),
            timeRemaining=data.get("timeRemaining", 1)
        )
