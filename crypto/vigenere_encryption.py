from crypto.algorithm import Algorithm


class VigenereEncryption(Algorithm):
    NAME = "vigenere"

    def __init__(self, key: str = ""):
        super().__init__()
        self.key: str = key

    def __repr__(self):
        return f"<Vigénère(key={self.key})>"

    def encode(self, plaintext: str) -> bytes:
        ...

    def decode(self, ciphertext: bytes) -> str:
        ...

    @staticmethod
    def parseTaskKey(msg: str) -> int:
        return int(msg.rsplit(" ", 1)[1])