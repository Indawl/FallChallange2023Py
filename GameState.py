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

    def __init__(self):
        self.score = 0, 0
        self.scans = set(), set()
        self.drones = {}
        self.fishes = {}
        self.monsters = {}
        self.lost_fishes = {}
        self.visible_fishes = set()

    def get_fish(self, fish_id: int) -> Fish:
        fish = self.fishes.get(fish_id)
        if fish is None:
            fish = self.monsters.get(fish_id)
            if fish is None:
                fish = self.lost_fishes[fish_id]
        return fish
