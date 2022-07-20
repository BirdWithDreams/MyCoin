import hashlib
from random import randint


def hash256(s):
    """two rounds of sha256"""
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()


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


class SECP256K1:
    A = 0
    B = 7
    P = 2 ** 256 - 2 ** 32 - 977
    N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141


class S256Field(Field(SECP256K1.P)):
    def __repr__(self):
        return f'{self.num:x}'


class S256Point(Point(S256Field(SECP256K1.A), S256Field(SECP256K1.B))):
    def verify(self, z, sig):
        s_inv = pow(sig.s.num, SECP256K1.N - 2, SECP256K1.N)
        u = z * s_inv % SECP256K1.N
        v = sig.r.num * s_inv % SECP256K1.N
        total = u * G + v * self
        return total.x.num == sig.r


G = S256Point(
    S256Field(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798),
    S256Field(0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)
)

SECP256K1.G = G


class Signature:

    def __init__(self, r, s):
        self.r = S256Field(r) if isinstance(r, int) else r
        self.s = S256Field(s) if isinstance(s, int) else s

    def __repr__(self):
        return f'Signature ({self.r}, {self.s})'


class PrivateKey:
    def __init__(self, secret):
        self.secret = secret
        self.point = secret * SECP256K1.G

    def hex(self):
        return f'{self.secret:x}'.zfill(64)

    def sign(self, z):
        k = randint(0, SECP256K1.N)

        r = (k * G).x.num
        k_inv = pow(k, SECP256K1.N - 2, SECP256K1.N)
        s = (z + r * self.secret) * k_inv % SECP256K1.N
        if s > SECP256K1.N / 2:
            s = SECP256K1.N - s
        return Signature(r, s)


key = PrivateKey(12345)
z = int.from_bytes(hash256(b'Programming Bitcoin!'), 'big')
sign = key.sign(z)
print(sign)
print(key.point.verify(z, sign))


