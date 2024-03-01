from crypto.algorithm import Algorithm


class ShiftEncryption(Algorithm):
    def __init__(self, key: int = 0):
        super().__init__()
        self.key = key

    def __repr__(self):
        return f"<Shift(key={self.key})>"

    def encode(self, plaintext: str) -> str:
        ...

    def decode(self, ciphertext: str) -> str:
        ...
