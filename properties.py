from typing import Final

from game_math import Vector
from game_objects import FishKind

MAX_TURN: Final = 201

MAP_SIZE: Final = 10000
SURFACE: Final = 500
CENTER: Final = Vector(MAP_SIZE - 1, MAP_SIZE - 1) / 2

FISH_SPEED: Final = 200
FISH_FRIGHTENED_SPEED: Final = 400

MONSTER_SPEED: Final = 270
MONSTER_ATTACK_SPEED: Final = 540
MONSTER_ATTACK_RADIUS: Final = 500

DRONE_MAX_SPEED: Final = 600
DRONE_SINK_SPEED: Final = 300
DRONE_EMERGENCY_SPEED: Final = 300

DELTA_RADIUS: Final = 3
DARK_SCAN_RADIUS: Final = 800
LIGHT_SCAN_RADIUS: Final = 2000
MONSTER_DETECTED_RADIUS_ADD: Final = 300
MOTOR_RANGE: Final = 1400

BATTERY_DRAIN: Final = 5
BATTERY_RECHARGE: Final = 1
MAX_BATTERY: Final = 30

MIN_DISTANCE_BT_FISH: Final = 600
MIN_DISTANCE_BT_MONSTER: Final = 600
MONSTER_MIN_START_Y: Final = 5000

HABITAT: Final = {
    FishKind.ANGLER: (2500, 10000),
    FishKind.JELLY: (2500, 5000),
    FishKind.FISH: (5000, 7500),
    FishKind.CRAB: (7500, 10000)
}

REWARDS: Final = {
    FishKind.JELLY: 1,
    FishKind.FISH: 2,
    FishKind.CRAB: 3
}
REWARDS_COLOR: Final = 3
REWARDS_TYPE: Final = 4
