def point(cls):
    def cur_point(_a, _b):
        class SubPoint(cls):
            a = _a
            b = _b

            @staticmethod
            def _check(x, y):
                return y * y == x ** 3 + _a * x + _b

        return SubPoint

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
        if type(self) is not type(other):
            raise TypeError(f'Points {self}, {other} is not on the same curve')

        if self.x is None:
            return other

        if other.x is None:
            return self

        if self == other:
            if self.y == 0:
                self.__class__(None, None)

            s = (3 * self.x ** 2 + self.a) / (2 * self.y)
            x = s * s - 2 * self.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y)

        if self.x == other.x:
            return self.__class__(None, None)

        s = (self.y - other.y) / (self.x - other.x)
        x = s * s - self.x - other.x
        y = s * (self.x - x) - self.y
        return self.__class__(x, y)

    def __rmul__(self, coefficient):
        coef = coefficient
        current = self
        result = self.__class__(None, None)
        while coef:
            if coef & 1:
                result += current
            current += current
            coef >>= 1
        return result

    def __mul__(self, other):
        if isinstance(other, int):
            return self.__rmul__(other)

    def __eq__(self, other):
        return type(self) is type(other) and self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Point ({self.x}, {self.y})'