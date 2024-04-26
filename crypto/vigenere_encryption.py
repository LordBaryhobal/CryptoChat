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
        vig_key = self.key
        count = 0
        out = b""
        for i in range(len(plaintext)):
            plainChar = Protocol.charToInt(plaintext[i])
            keyChar = Protocol.charToInt(vig_key[count])

            encodedValue = plainChar + keyChar
            out += Protocol.intToPaddedBytes(encodedValue)
            count += 1
            if count == len(vig_key):
                count = 0
        return out

    def decode(self, ciphertext: bytes) -> str:
        vig_key = self.key
        ints = Protocol.groupBytesIntoInt(ciphertext)
        out = []
        count = 0

        for i in range(len(ints)):
            keyChar = int.from_bytes(vig_key[count].encode("utf-8"), "big")
            out.append(ints[i] - keyChar)
            count += 1
            if count == len(vig_key):
                count = 0

        return bytes(out).decode("UTF-8")

    @staticmethod
    def parseTaskKey(msg: str) -> str:
        return msg.rsplit(" ", 1)[1]


if __name__ == '__main__':
    key = "ISC"
    plaintext = "banana"
    vig = VigenereEncryption(key)
    ciphertext = vig.encode(plaintext)
    print(ciphertext)
    print(vig.decode(ciphertext))
