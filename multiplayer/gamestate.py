import json
import time
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional


class GamePhase(Enum):
    WAITING = "waiting"
    PICKING = "picking"
    BATTLE = "battle"
    FINISHED = "finished"


@dataclass
class Player:
    id: int
    name: str = ""
    ready: bool = False
    selected_character: Optional[str] = None
    health: int = 100
    position: Dict[str, float] = None

    def __post_init__(self):
        if self.position is None:
            self.position = {"x": 0, "y": 0}


@dataclass
class PickingPhaseData:
    time_remaining: float
    available_characters: List[str]
    player_selections: Dict[int, Optional[str]]


@dataclass
class BattlePhaseData:
    turn_number: int
    current_turn_player: int
    battle_log: List[str]
    game_over: bool = False
    winner: Optional[int] = None


class GameState:
    def __init__(self):
        self.phase = GamePhase.WAITING
        self.players: Dict[int, Player] = {}
        self.picking_data = PickingPhaseData(
            time_remaining=30.0,
            available_characters=["warrior", "mage", "archer", "rogue"],
            player_selections={}
        )
        self.battle_data = BattlePhaseData(
            turn_number=1,
            current_turn_player=1,
            battle_log=[]
        )
        self.last_update = time.time()

    def add_player(self, player_id: int, name: str = ""):
        self.players[player_id] = Player(id=player_id, name=name or f"Player{player_id}")
        self.picking_data.player_selections[player_id] = None

    def remove_player(self, player_id: int):
        self.players.pop(player_id, None)
        self.picking_data.player_selections.pop(player_id, None)

    def set_phase(self, phase: GamePhase):
        self.phase = phase
        self.last_update = time.time()

        if phase == GamePhase.PICKING:
            self.picking_data.time_remaining = 30.0
        elif phase == GamePhase.BATTLE:
            self._initialize_battle()

    def _initialize_battle(self):
        # Set initial positions for players
        positions = [{"x": -50, "y": 0}, {"x": 50, "y": 0}]
        for i, (player_id, player) in enumerate(self.players.items()):
            if i < len(positions):
                player.position = positions[i]
            player.health = 100
            player.ready = False

    def update_picking_timer(self, delta_time: float):
        if self.phase == GamePhase.PICKING:
            self.picking_data.time_remaining = max(0, self.picking_data.time_remaining - delta_time)
            if self.picking_data.time_remaining <= 0:
                self.set_phase(GamePhase.BATTLE)

    def select_character(self, player_id: int, character: str) -> bool:
        if (self.phase == GamePhase.PICKING and
                character in self.picking_data.available_characters and
                player_id in self.players):
            self.picking_data.player_selections[player_id] = character
            self.players[player_id].selected_character = character
            return True
        return False

    def set_player_ready(self, player_id: int, ready: bool = True):
        if player_id in self.players:
            self.players[player_id].ready = ready

    def all_players_ready(self) -> bool:
        return len(self.players) > 0 and all(player.ready for player in self.players.values())

    def get_picking_state(self) -> Dict[str, Any]:
        """Returns state data for picking phase (sent via UDP frequently)"""
        return {
            "phase": self.phase.value,
            "time_remaining": round(self.picking_data.time_remaining, 1),
            "available_characters": self.picking_data.available_characters,
            "player_selections": self.picking_data.player_selections,
            "timestamp": time.time()
        }

    def get_battle_state(self) -> Dict[str, Any]:
        """Returns complete state data for battle phase (sent via TCP)"""
        return {
            "phase": self.phase.value,
            "players": {pid: asdict(player) for pid, player in self.players.items()},
            "battle_data": asdict(self.battle_data),
            "timestamp": time.time()
        }

    def get_full_state(self) -> Dict[str, Any]:
        """Returns complete game state"""
        return {
            "phase": self.phase.value,
            "players": {pid: asdict(player) for pid, player in self.players.items()},
            "picking_data": asdict(self.picking_data),
            "battle_data": asdict(self.battle_data),
            "timestamp": time.time()
        }

    def to_json(self, state_type: str = "full") -> str:
        if state_type == "picking":
            return json.dumps(self.get_picking_state())
        elif state_type == "battle":
            return json.dumps(self.get_battle_state())
        else:
            return json.dumps(self.get_full_state())