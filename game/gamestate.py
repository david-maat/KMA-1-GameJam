from enum import Enum

class GameState(Enum):
    MENU = 1
    TEAM_SELECT = 2
    SHOP = 3
    TRANSITION = 4
    BATTLE = 5
    RESULT = 6
    GAME_OVER = 7
