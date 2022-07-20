import hashlib
from random import randint
from secp256k1 import SECP256K1, S256Field, S256Point


def hash256(s):
    """two rounds of sha256"""
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()


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


