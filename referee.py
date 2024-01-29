from game_math import Vector
from game_objects import GameState, Fish


class Referee:
    state: GameState

    def __init__(self, state: GameState):
        self.state = state

    def update_positions(self, fishes: list[Fish] = None) -> None:
        pass

    def update_speed(self, fishes: list[Fish] = None) -> None:
        pass

    def get_fish_speed(self, fish: Fish) -> Vector:
        pass
