import hashlib
import hmac

from secp256k1 import SECP256K1, S256Field


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
        k = self.deterministic_k(z)

        r = (k * SECP256K1.G).x.num
        k_inv = pow(k, SECP256K1.N - 2, SECP256K1.N)
        s = (z + r * self.secret) * k_inv % SECP256K1.N
        if s > SECP256K1.N / 2:
            s = SECP256K1.N - s
        return Signature(r, s)

    def deterministic_k(self, z):
        k = b'\x00' * 32
        v = b'\x01' * 32

        if z > SECP256K1.N:
            z -= SECP256K1.N

        z_bytes = z.to_bytes(32, 'big')
        secret_bytes = self.secret.to_bytes(32, 'big')

        k = hmac.new(k, v + b'\x00' + secret_bytes + z_bytes, hashlib.sha256).digest()
        v = hmac.new(k, v, hashlib.sha256).digest()
        k = hmac.new(k, v + b'\x01' + secret_bytes + z_bytes, hashlib.sha256).digest()
        v = hmac.new(k, v, hashlib.sha256).digest()

        while True:
            v = hmac.new(k, v, hashlib.sha256).digest()
            candidate = int.from_bytes(v, 'big')
            if 1 <= candidate < SECP256K1.N:
                return candidate

            k = hmac.new(k, v + b'\x00' + secret_bytes + z_bytes, hashlib.sha256).digest()
            v = hmac.new(k, v, hashlib.sha256).digest()
