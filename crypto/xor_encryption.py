from crypto.algorithm import Algorithm


class XOREncryption(Algorithm):
    NAME = "xor"

    def __init__(self, key: int = 0):
        super().__init__()
        self.key = key

    def __repr__(self):
        return f"<XOR(key={self.key})>"

    def encode(self, plaintext: str) -> str:
        ...

    def decode(self, ciphertext: str) -> str:
        ...

    @staticmethod
    def parseTaskKey(msg: str) -> int:
        return int(msg.rsplit(" ", 1)[1])
