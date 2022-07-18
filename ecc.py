def field(cls):
    def sub_field(_base):
        if not isinstance(_base, int) or _base <= 0:
            raise ValueError(f'The number {_base} cannot be the base of the field')

        class SubField(cls):
            base = _base

        return SubField

    return sub_field


@field
class Field:
    def __init__(self, num):
        self.num = num % self.base

    def __add__(self, other):
        if self.base != other.base:
            raise TypeError(f'Cannot add two numbers in different Fields ({self.base} and {other.base})')

        return self.__class__((self.num + other.num) % self.base)

    def __mul__(self, other):
        if isinstance(other, int):
            pass

        if self.base != other.base:
            raise TypeError(f'Cannot add two numbers in different Fields ({self.base} and {other.base})')

        return self.__class__((self.num * other.num) % self.base)

    def __truediv__(self, other):
        if self.base != other.base:
            raise TypeError(f'Cannot add two numbers in different Fields ({self.base} and {other.base})')

        inverse = other ** (self.base - 2)
        return self * inverse

    def __pow__(self, power, modulo=None):
        return self.__class__(pow(self.num, power % (self.base - 1), self.base))

    def __eq__(self, other):
        return self.num == other.num and self.base == other.base

    def __repr__(self):
        return f'FieldElement object {self.num}_{self.base}'


def point(cls):
    def cur_point(a, b):
        @staticmethod
        def _check(x, y):
            return y * y == x ** 3 + a * x + b

        setattr(cls, '_check', _check)
        return cls

    return cur_point


@point
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        if x is None and y is None:
            return

        if not self._check(x, y):
            raise ValueError(f'({x}, {y}) is not on the curve')

    def __add__(self, other):
        if self.a != other.a or self.b != other.b:
            raise TypeError(f'Points {self}, {other} is not on the same curve')

        if self.x is None:
            return other

        if other.x is None:
            return self

        if self == other:
            s = (3 * self.x ** 2 + self.a) / (2 * self.y)
            x = s * s - 2 * self.x
            y = s(self.x - x) - self.y
            return self.__class__(x, y)

        if self.x == other.x:
            return self.__class__(None, None)

        s = (self.y - other.y) / (self.x - other.x)
        x = s * s - self.x - other.x
        y = s * (self.x - x) - self.y
        return self.__class__(x, y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Point ({self.x}, {self.y})'


p1 = Point(5, 7)
p2 = Point(0, 7)
f = p1(-1, -1)
g = p1(2, 5)
print(f+g)
print(f+f)
