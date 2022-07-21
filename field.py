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
        if isinstance(other, int):
            return self.__class__(self.num + other)

        if type(self) is not type(other):
            raise TypeError(f'Cannot add two numbers in different Fields ({self.base} and {other.base})')

        return self.__class__(self.num + other.num)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, int):
            return self.__class__(self.num - other)

        if type(self) is not type(other):
            raise TypeError(f'Cannot add two numbers in different Fields ({self.base} and {other.base})')

        return self.__class__(self.num - other.num)

    def __rsub__(self, other):
        if isinstance(other, int):
            return self.__class__(other - self.num)

        if type(self) is not type(other):
            raise TypeError(f'Cannot add two numbers in different Fields ({self.base} and {other.base})')

        return self.__class__(other.num - self.num)

    def __mul__(self, other):
        if isinstance(other, int):
            return self.__class__(self.num * other)

        if type(self) is not type(other):
            raise TypeError(f'Cannot add two numbers in different Fields ({self.base} and {other.base})')

        return self.__class__(self.num * other.num)

    def __rmul__(self, other):
        if isinstance(other, int):
            return self.__class__(self.num * other)

    def __truediv__(self, other):
        if type(self) is not type(other):
            raise TypeError(f'Cannot add two numbers in different Fields ({self.base} and {other.base})')

        inverse = other ** (self.base - 2)
        return self * inverse

    def __pow__(self, power, modulo=None):
        return self.__class__(pow(self.num, power % (self.base - 1), self.base))

    def __eq__(self, other):
        if isinstance(other, int):
            return self.num == other % self.base

        return type(self) is type(other) and self.num == other.num

    def __repr__(self):
        return f'FieldElement object {self.num}_{self.base}'
