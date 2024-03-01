from crypto.algorithm import Algorithm


class ShiftEncryption(Algorithm):
    def __init__(self, key: int = 0):
        super().__init__()
        self.key = key

    def __repr__(self):
        return f"<Shift(key={self.key})>"

    def encode(self, plaintext: str) -> bytes:
        out = list(plaintext.encode("UTF-8"))
        for i in range(len(plaintext)):
            out[i] = out[i] + self.key
        return bytes(out)

    def decode(self, ciphertext: str) -> str:
        ciphertext = list(ciphertext)
        for i in range(len(ciphertext)):
            ciphertext[i] = ciphertext[i] - self.key
        return bytes(ciphertext).decode("UTF-8")
