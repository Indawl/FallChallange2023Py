from enum import Enum

from RectangleRange import RectangleRange
from Vector import Vector


class FishColor(Enum):
    UGLY, PINK, YELLOW, GREEN, BLUE = range(-1, 4)


class FishKind(Enum):
    ANGLER, JELLY, FISH, CRAB = range(-1, 3)


class Fish:
    fish_id: int
    color: FishColor
    kind: FishKind
    position: Vector
    speed: Vector | None
    location: RectangleRange

    def __init__(self, fish_id: int, color: FishColor = FishColor.UGLY, kind: FishKind = FishKind.ANGLER):
        self.fish_id = fish_id
        self.color = color
        self.kind = kind
        self.position = Vector()
        self.speed = None
        self.location = RectangleRange(Vector(), Vector())

    def __str__(self):
        s = f"[{self.fish_id}] {self.color.name} {self.kind.name} {self.position}"
        if self.speed is not None:
            s += f" V {int(self.speed.length())} {self.speed}"
        return s
