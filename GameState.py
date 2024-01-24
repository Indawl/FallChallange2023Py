from Drone import Drone
from Fish import Fish


class GameState:
    score: tuple[int, int]
    scans: tuple[set[int], set[int]]
    drones: dict[int, Drone]
    fishes: dict[int, Fish]
    monsters: dict[int, Fish]
    lost_fishes: dict[int, Fish]
    visible_fishes: set[int]
