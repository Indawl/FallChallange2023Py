from enum import Enum

import Properties
from Vector import Vector


class BlipType(Enum):
    TL, TR, BR, BL = range(4)


class Drone:
    drone_id: int
    player_id: int
    position: Vector
    speed: Vector
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
         V {int(self.speed.length())} B {self.battery} S {len(self.scans)}{'Broken' if self.emergency else ''}"
