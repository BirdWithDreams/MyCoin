import hashlib
import hmac
from io import BytesIO

from helper import encode_base58_checksum
from secp256k1 import SECP256K1, S256Field, S256Point


class Signature:

    def __init__(self, r, s):
        self.r = S256Field(r) if isinstance(r, int) else r
        self.s = S256Field(s) if isinstance(s, int) else s

    def __repr__(self):
        return f'Signature ({self.r}, {self.s})'

    def der(self):
        rbin = self.r.to_bytes(32, byteorder='big')
        rbin = rbin.lstrip(b'\x00')

        if rbin[0] & 0x80:
            rbin = b'\x00' + rbin

        result = bytes([2, len(rbin)]) + rbin
        sbin = self.s.to_bytes(32, byteorder='big')
        sbin = sbin.lstrip(b'\x00')

        if sbin[0] & 0x80:
            sbin = b'\x00' + sbin

        result += bytes([2, len(sbin)]) + sbin
        return bytes([0x30, len(result)]) + result

    @classmethod
    def parse(cls, signature_bin):
        s = BytesIO(signature_bin)
        compound = s.read(1)[0]

        if compound != 0x30:
            raise SyntaxError("Bad Signature")

        length = s.read(1)[0]
        if length + 2 != len(signature_bin):
            raise SyntaxError("Bad Signature Length")

        marker = s.read(1)[0]
        if marker != 0x02:
            raise SyntaxError("Bad Signature")

        rlength = s.read(1)[0]
        r = int.from_bytes(s.read(rlength), 'big')
        marker = s.read(1)[0]

        if marker != 0x02:
            raise SyntaxError("Bad Signature")

        slength = s.read(1)[0]
        s = int.from_bytes(s.read(slength), 'big')

        if len(signature_bin) != 6 + rlength + slength:
            raise SyntaxError("Signature too long")
        return cls(r, s)


class PrivateKey:
    def __init__(self, secret):
        self.secret = secret
        self.point: S256Point = secret * SECP256K1.G

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

    def wif(self, compressed=True, testnet=False):
        secret_bytes = self.secret.to_bytes(32, 'big')

        if testnet:
            prefix = b'\xef'
        else:
            prefix = b'\x80'
        if compressed:
            suffix = b'\x01'
        else:
            suffix = b''

        return encode_base58_checksum(prefix + secret_bytes + suffix)
