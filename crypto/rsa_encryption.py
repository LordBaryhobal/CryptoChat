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
