from field import Field
from point import Point


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
