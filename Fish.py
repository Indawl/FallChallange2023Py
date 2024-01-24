from enum import Enum

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
    speed: Vector
    location: Vector

    def __init__(self, fish_id: int, color: FishColor = FishColor.UGLY, kind: FishKind = FishKind.ANGLER):
        self.fish_id = fish_id
        self.color = color
        self.kind = kind

    def __str__(self) -> str:
        return f"[{self.fish_id}] {self.color} {self.kind} {self.position} \
            V {int(self.speed.length())} {self.speed} "
