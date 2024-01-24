from math import sqrt, cos, sin


class Vector:
    __x: int | float
    __y: int | float

    def __init__(self, x: int | float = 0, y: int | float = 0):
        self.__x = x
        self.__y = y

    def __str__(self) -> str:
        return f"({self.__x}, {self.__y})"

    @property
    def x(self) -> int | float:
        return self.__x

    @property
    def y(self) -> int | float:
        return self.__y

    def __add__(self, other):
        return Vector(self.__x + other.__x, self.__y + other.__y)

    def __sub__(self, other):
        return Vector(self.__x - other.__x, self.__y - other.__y)

    def __mul__(self, other):
        return Vector(self.__x * other, self.__y * other)

    __rmul__ = __mul__

    def __neg__(self):
        return self * -1

    def __truediv__(self, other):
        return Vector(self.__x / other, self.__y / other)

    def __eq__(self, other):
        return self.__x == other.__x and self.__y == other.y

    def __ne__(self, other):
        return not self == other

    def offset(self, length: int | float):
        return Vector(self.__x + length, self.__y + length)

    def skew(self, other) -> int | float:
        return self.__x * other.__y - other.__x * self.__y

    def dot(self, other) -> int | float:
        return self.__x * other.__x + other.__y * self.__y

    def length2(self) -> int | float:
        return self.__x ** 2 + self.__y ** 2

    def length(self) -> float:
        return sqrt(self.length2())

    def distance2(self, other) -> int | float:
        return (self - other).length2()

    def distance(self, other) -> float:
        return sqrt(self.distance2(other))

    def normalize(self):
        return self / self.length()

    def project(self, to):
        return to * self.dot(to) / to.length2()

    def is_zero(self) -> bool:
        return self == Vector()

    def hsymm(self, x: int | float = 0):
        return Vector(2 * x - self.__x, self.__y)

    def vsymm(self, y: int | float = 0):
        return Vector(self.__x, 2 * y - self.__y)

    def round(self):
        return Vector(round(self.__x), round(self.__y))

    def epsilon_round(self):
        return Vector(round(self.__x * 10000000.0) / 10000000.0, round(self.__y * 10000000.0) / 10000000.0)

    def cross(self, d: int = 1):
        return Vector(-d * self.__y, d * self.__x)

    def rotate(self, angle: float):
        return Vector(self.__x * cos(angle) - self.__y * sin(angle),
                      self.__x * sin(angle) + self.__y * cos(angle))

    def in_range(self, r: int) -> bool:
        return self.length2() <= r ** 2

    def in_range2(self, ri: int, ro: int) -> bool:
        return ri ** 2 < self.length2() <= ro ** 2

    def in_range_vec(self, other, r: int) -> bool:
        return (other - self).in_range(r)

    def in_range_vec2(self, other, ri: int, ro: int) -> bool:
        return (other - self).in_range2(ri, ro)

    def get_closest(self, coords: list) -> list:
        closest, min_dist = [], 0

        for coord in coords:
            dist = self.distance2(coord)
            if not closest or dist < min_dist:
                closest, min_dist = [coord], dist
            else:
                closest.append(coord)

        return closest
