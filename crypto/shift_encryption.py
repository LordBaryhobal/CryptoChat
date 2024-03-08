from client.protocol import Protocol
from crypto.algorithm import Algorithm


class ShiftEncryption(Algorithm):
    NAME = "shift"

    def __init__(self, key: int = 0):
        super().__init__()
        self.key = key

    def __repr__(self):
        return f"<Shift(key={self.key})>"

    def encode(self, plaintext: str) -> bytes:
        out = b""

        for i in range(len(plaintext)):
            plainBytes = plaintext[i].encode("utf-8")
            value = int.from_bytes(plainBytes, "big")
            encodedValue = value + self.key

            out += encodedValue.to_bytes(Protocol.BYTE_SIZE, "big")

        return out

    def decode(self, ciphertext: bytes) -> str:
        ints = Protocol.groupBytesIntoInt(ciphertext)
        out = []

        for i in range(len(ints)):
            out.append(ints[i] - self.key)

        return bytes(out).decode("UTF-8")

    @staticmethod
    def parseTaskKey(msg: str) -> int:
        return int(msg.rsplit(" ", 1)[1])
