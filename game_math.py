from __future__ import annotations
from math import sqrt, cos, sin


class Vector:
    __x: int | float
    __y: int | float

    def __init__(self, x: int | float = 0, y: int | float = 0):
        self.__x = x
        self.__y = y

    def __str__(self):
        return f"({self.__x}, {self.__y})"

    @property
    def x(self) -> int | float:
        return self.__x

    @property
    def y(self) -> int | float:
        return self.__y

    def __mul__(self, other: int | float) -> Vector:
        return Vector(self.__x * other, self.__y * other)

    __rmul__ = __mul__

    def __neg__(self) -> Vector:
        return self * -1

    def __truediv__(self, other: int | float) -> Vector:
        return Vector(self.__x / other, self.__y / other)

    def __add__(self, other: Vector | int | float) -> Vector:
        if isinstance(other, Vector):
            return Vector(self.__x + other.__x, self.__y + other.__y)
        else:
            return Vector(self.__x + other, self.__y + other)

    def __sub__(self, other: Vector | int | float) -> Vector:
        return self + (-other)

    def __eq__(self, other: Vector) -> bool:
        return self.__x == other.__x and self.__y == other.y

    def __ne__(self, other: Vector) -> bool:
        return not self == other

    def skew(self, other: Vector) -> int | float:
        return self.__x * other.__y - other.__x * self.__y

    def dot(self, other: Vector) -> int | float:
        return self.__x * other.__x + other.__y * self.__y

    def length2(self) -> int | float:
        return self.__x ** 2 + self.__y ** 2

    def length(self) -> float:
        return sqrt(self.length2())

    def distance2(self, other: Vector) -> int | float:
        return (self - other).length2()

    def distance(self, other: Vector) -> float:
        return sqrt(self.distance2(other))

    def normalize(self):
        return self / self.length()

    def project(self, to: Vector):
        return to * self.dot(to) / to.length2()

    def is_zero(self) -> bool:
        return self == Vector()

    def hsymm(self, x: int | float = 0) -> Vector:
        return Vector(2 * x - self.__x, self.__y)

    def vsymm(self, y: int | float = 0) -> Vector:
        return Vector(self.__x, 2 * y - self.__y)

    def round(self) -> Vector:
        return Vector(round(self.__x), round(self.__y))

    def epsilon_round(self) -> Vector:
        return Vector(round(self.__x * 10000000.0) / 10000000.0, round(self.__y * 10000000.0) / 10000000.0)

    def cross(self, d: int = 1) -> Vector:
        return Vector(-d * self.__y, d * self.__x)

    def rotate(self, angle: float) -> Vector:
        return Vector(self.__x * cos(angle) - self.__y * sin(angle),
                      self.__x * sin(angle) + self.__y * cos(angle))

    def in_range(self, r: int) -> bool:
        return self.length2() <= r ** 2

    def in_range2(self, ri: int, ro: int) -> bool:
        return ri ** 2 < self.length2() <= ro ** 2

    def in_range_vec(self, other: Vector, r: int) -> bool:
        return (other - self).in_range(r)

    def in_range_vec2(self, other: Vector, ri: int, ro: int) -> bool:
        return (other - self).in_range2(ri, ro)

    def get_closest(self, coords: list[Vector]) -> list[Vector]:
        closest, min_dist = [], 0

        for coord in coords:
            dist = self.distance2(coord)
            if not closest or dist < min_dist:
                closest, min_dist = [coord], dist
            else:
                closest.append(coord)

        return closest


class RectangleRange:
    __from: Vector
    __to: Vector

    def __init__(self, from_: Vector, to: Vector):
        self.__from = from_
        self.__to = to

    def __str__(self):
        return f"({self.__from} {self.__to})"

    @property
    def from_(self):
        return self.__from

    @property
    def to(self):
        return self.__to

    @property
    def center(self) -> Vector:
        return (self.__from + self.__to) / 2

    def __add__(self, other: Vector) -> RectangleRange:
        return RectangleRange(self.__from + other, self.__to + other)

    def __sub__(self, other: Vector) -> RectangleRange:
        return RectangleRange(self.__from - other, self.__to - other)

    def __eq__(self, other: RectangleRange) -> bool:
        return self.__from == other.__from and self.__to == other.__to

    def __ne__(self, other: RectangleRange) -> bool:
        return not self == other

    def hsymm(self, x: int | float = 0) -> RectangleRange:
        return RectangleRange(self.__to.hsymm(x), self.__from.hsymm(x))

    def in_range(self, coord: Vector) -> bool:
        return self.__from.x <= coord.x <= self.__to.x and self.__from.y <= coord.y <= self.__to.y

    def intersect(self, rectangle: RectangleRange) -> RectangleRange:
        x = max(self.__from.x, rectangle.__from.x)
        y = max(self.__from.y, rectangle.__from.y)
        to_x = min(self.__to.x, rectangle.__to.x)
        to_y = min(self.__to.y, rectangle.__to.y)

        if x > to_x or y > to_y:
            return self
        return RectangleRange(Vector(x, y), Vector(to_x, to_y))

    def intersect_line(self, coord: Vector, in_rect: Vector) -> Vector:
        d = coord - in_rect

        if d.x == 0:
            return Vector(in_rect.x, self.__from.y if d.y < 0 else self.__to.y)
        if d.y == 0:
            return Vector(self.__from.x if d.x < 0 else self.__to.x, in_rect.y)

        x = self.__from.x if d.x < 0 else self.__to.x
        y = d.y / d.x * (x - in_rect.x) + in_rect.y

        if y < self.__from.y or y > self.__to.y:
            y = self.__from.y if d.y < 0 else self.__to.y
            x = d.x / d.y * (y - in_rect.y) + in_rect.x

        return Vector(x, y)

    def intersect_radius(self, coord: Vector, r: int) -> RectangleRange:
        return self.intersect(RectangleRange(coord - r, coord + r))

    def scale(self, koef: int | float) -> RectangleRange:
        return RectangleRange(self.__from - koef, self.__to + koef)
