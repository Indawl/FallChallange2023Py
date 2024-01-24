from enum import Enum
from numpy import ndarray
from numpy.linalg import norm
import Properties


class BlipType(Enum):
    TL, TR, BR, BL = range(4)


class Drone:
    drone_id: int
    player_id: int
    position: ndarray
    speed: ndarray
    emergency: bool
    battery: int = Properties.MAX_BATTERY
    light_radius: int
    lighting: bool
    motor_on: bool
    scans: set[int]
    new_scans: set[int]
    radar_blips: dict[int, BlipType]

    def __init__(self, drone_id: int, player_id: int):
        self.drone_id = drone_id
        self.player_id = player_id

    def __str__(self) -> str:
        return f"[{self.drone_id}] {'My' if self.player_id == 0 else 'Enemy'} Drone {self.position} \
         V {int(norm(self.speed, ord=2))} B {self.battery} S {len(self.scans)}{'Broken' if self.emergency else ''}"
