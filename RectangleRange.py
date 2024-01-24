from __future__ import annotations

from Vector import Vector


class RectangleRange:
    __fr: Vector
    __to: Vector

    def __init__(self, fr: Vector, to: Vector):
        self.__fr = fr
        self.__to = to

    def __str__(self):
        return f"({self.__fr} {self.__to})"

    @property
    def fr(self):
        return self.__fr

    @property
    def to(self):
        return self.__to

    def __add__(self, other: Vector) -> RectangleRange:
        return RectangleRange(self.__fr + other, self.__to + other)

    def __sub__(self, other: Vector) -> RectangleRange:
        return RectangleRange(self.__fr - other, self.__to - other)

    def __eq__(self, other: RectangleRange) -> bool:
        return self.__fr == other.__fr and self.__to == other.__to

    def __ne__(self, other: RectangleRange) -> bool:
        return not self == other

    def hsymm(self, x: int | float = 0) -> RectangleRange:
        return RectangleRange(self.__to.hsymm(x), self.__fr.hsymm(x))

    def in_range(self, coord: Vector) -> bool:
        return self.__fr.x <= coord.x <= self.__to.x and self.__fr.y <= coord.y <= self.__to.y

    def intersect(self, rectangle: RectangleRange) -> RectangleRange:
        x = max(self.__fr.x, rectangle.__fr.x)
        y = max(self.__fr.y, rectangle.__fr.y)
        to_x = min(self.__to.x, rectangle.__to.x)
        to_y = min(self.__to.y, rectangle.__to.y)

        if x > to_x or y > to_y:
            return self
        return RectangleRange(Vector(x, y), Vector(to_x, to_y))

    def intersect_line(self, coord: Vector, in_rect: Vector) -> Vector:
        d = coord - in_rect

        if d.x == 0:
            return Vector(in_rect.x, self.__fr.y if d.y < 0 else self.__to.y)
        if d.y == 0:
            return Vector(self.__fr.x if d.x < 0 else self.__to.x, in_rect.y)

        x = self.__fr.x if d.x < 0 else self.__to.x
        y = d.y / d.x * (x - in_rect.x) + in_rect.y

        if y < self.__fr.y or y > self.__to.y:
            y = self.__fr.y if d.y < 0 else self.__to.y
            x = d.x / d.y * (y - in_rect.y) + in_rect.x

        return Vector(x, y)

    def intersect_radius(self, coord: Vector, r: int) -> RectangleRange:
        return self.intersect(RectangleRange(coord.offset(-r), coord.offset(r)))

    def scale(self, koef: int | float) -> RectangleRange:
        return RectangleRange(self.__fr.offset(koef), self.__to.offset(koef))
