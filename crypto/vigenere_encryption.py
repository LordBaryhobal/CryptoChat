from typing import List
from client.protocol import Protocol

from crypto.algorithm import Algorithm


class VigenereEncryption(Algorithm):
    NAME = "vigenere"

    def __init__(self, key: str = ""):
        super().__init__()
        self.key: str = key

    def __repr__(self):
        return f"<Vigénère(key={self.key})>"

    def encode(self, plaintext: str) -> bytes:
        key = self.key
        count = 0
        out = b""
        for i in range(len(plaintext)):
            plainChar = int.from_bytes(plaintext[i].encode("utf-8"), "big")
            keyChar = int.from_bytes(key[count].encode("utf-8"), "big")

            out += ((plainChar + keyChar).to_bytes(Protocol.BYTE_SIZE, "big"))
            count += 1
            if count == len(key):
                count = 0
        return out

    def decode(self, ciphertext: bytes) -> str:
        ...

    @staticmethod
    def parseTaskKey(msg: str) -> int:
        return int(msg.rsplit(" ", 1)[1])


if __name__ == '__main__':
    key = "ISC"
    plaintext = "banana"
    vig = VigenereEncryption(key)
    print(vig.encode(plaintext))
