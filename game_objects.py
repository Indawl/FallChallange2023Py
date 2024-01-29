from enum import Enum

import properties
from game_math import Vector, RectangleRange


class FishColor(Enum):
    UGLY, PINK, YELLOW, GREEN, BLUE = range(-1, 4)


class FishKind(Enum):
    ANGLER, JELLY, FISH, CRAB = range(-1, 3)


class Fish:
    __fish_id: int
    __color: FishColor
    __kind: FishKind
    position: Vector
    speed: Vector | None
    location: RectangleRange
    last_seen: int

    @property
    def fish_id(self):
        return self.__fish_id

    @property
    def color(self):
        return self.__color

    @property
    def kind(self):
        return self.__kind

    def __init__(self, fish_id: int, color: FishColor = FishColor.UGLY, kind: FishKind = FishKind.ANGLER):
        self.__fish_id = fish_id
        self.__color = color
        self.__kind = kind
        self.position = Vector()
        self.speed = None
        self.location = RectangleRange(Vector(), Vector())
        self.last_seen = properties.MAX_TURN

    def __str__(self):
        s = f"[{self.__fish_id}] {self.__color.name} {self.__kind.name} {self.position}"
        if self.speed is not None:
            s += f" V {int(self.speed.length())} {self.speed}"
        return s


class BlipType(Enum):
    TL, TR, BR, BL = range(4)


class Drone:
    __drone_id: int
    __player_id: int
    position: Vector
    speed: Vector
    emergency: bool
    battery: int
    light_radius: int
    lighting: bool
    motor_on: bool
    scans: set[int]
    new_scans: set[int]
    radar_blips: dict[int, BlipType]

    @property
    def drone_id(self):
        return self.__drone_id

    @property
    def player_id(self):
        return self.__player_id

    def __init__(self, drone_id: int, player_id: int):
        self.__drone_id = drone_id
        self.__player_id = player_id
        self.position = Vector()
        self.speed = Vector()
        self.emergency = False
        self.battery = properties.MAX_BATTERY
        self.light_radius = properties.DARK_SCAN_RADIUS
        self.lighting = False
        self.motor_on = False
        self.scans = set()
        self.new_scans = set()
        self.radar_blips = {}

    def __str__(self):
        return f"[{self.__drone_id}] {'My' if self.__player_id == 0 else 'Enemy'} Drone {self.position} \
         V {int(self.speed.length())} B {self.battery} S {len(self.scans)}{'Broken' if self.emergency else ''}"

    def get_range_by_radar(self, fish_id: int) -> RectangleRange:
        x, y, to_x, to_y = 0, 0, properties.MAP_SIZE - 1, properties.MAP_SIZE - 1
        blip = self.radar_blips[fish_id]

        if blip == BlipType.BL or blip == BlipType.TL:
            to_x = self.position.x
        else:
            x = self.position.x + 1

        if blip == BlipType.TL or blip == BlipType.TR:
            to_y = self.position.y
        else:
            y = self.position.y + 1

        return RectangleRange(Vector(x, y), Vector(to_x, to_y))


class GameState:
    turn: int
    score: tuple[int, int]
    scans: tuple[set[int], set[int]]
    drones: dict[int, Drone]
    fishes: dict[int, Fish]
    lost_fishes: dict[int, Fish]

    def __init__(self):
        self.turn = 0
        self.score = 0, 0
        self.scans = set(), set()
        self.drones = {}
        self.fishes = {}
        self.lost_fishes = {}

    def get_symmetric_fish(self, fish: Fish) -> Fish:
        return self.fishes.get(fish.fish_id + (1 if fish.fish_id % 2 == 0 else -1))
