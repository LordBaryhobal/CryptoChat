import re
from typing import Optional

from crypto.algorithm import Algorithm


class RSAEncryption(Algorithm):
    NAME = "rsa"

    def __init__(self, pubKey: tuple[int, int], privKey: tuple[int, int]):
        super().__init__()
        self.pubKey: tuple[int, int] = pubKey
        self.privKey: tuple[int, int] = privKey

    def __repr__(self):
        return f"<RSA(public={self.pubKey}, private={self.privKey})>"

    def encode(self, plaintext: str) -> bytes:
        ...

    def decode(self, ciphertext: bytes) -> str:
        ...

    @staticmethod
    def parseTaskKey(msg: str) -> tuple[int, int]:
        m: Optional[re.Match[str]] = re.match(r"n=(\d+), e=(\d+)", msg)

        n: int = int(m.group(1))
        e: int = int(m.group(2))

        pubKey = (n, e)

        return pubKey

    @staticmethod
    def generateKeyPair() -> tuple[tuple[int, int], tuple[int, int]]:
        # TODO: find 2 large prime numbers p and q, with a large difference
        # TODO: compute n = p * q -> n should be smaller than 2^32 (max value on 4 bytes)
        # TODO: compute lambda = |(p-1)(q-1)| / gcd(p-1, q-1)
        # TODO: choose a number e in ]1; lambda[ such that e and lambda are coprime
        # TODO: find d, the modular inverse of e (mod lambda)
        # priv = (n, d)
        # pub = (n, e)
        ...
