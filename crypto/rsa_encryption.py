import random
import re
from typing import Optional

from crypto.algorithm import Algorithm
from math_utils.modulo import getModularInverse
from math_utils.primes import areCoprimes, getLargestPrime, gcd


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
        """
        Generates a public/private key pair
        Returns:
            a tuple containing the private and public key (in this order)
        """

        # Find 2 large prime numbers p and q, with a large difference
        maxP: int = random.randint(15_000, 20_000)
        p: int = getLargestPrime(maxP)

        maxQ: int = 10 * p
        q: int = getLargestPrime(maxQ)

        # Compute n = p * q -> n should be smaller than 2^32 (max value on 4 bytes)
        n: int = p * q

        # Compute lambda = |(p-1)(q-1)| / gcd(p-1, q-1)
        lambda_: int = abs((p - 1) * (q - 1)) // gcd(p - 1, q - 1)

        # Choose a number e in ]1; lambda[ such that e and lambda are coprime
        for e in range(lambda_ - 1, 1, -1):
            if areCoprimes(e, lambda_):
                break

        else:
            raise Exception("Could not find e coprime with lambda")

        # Find d, the modular inverse of e (mod n)
        d: int = getModularInverse(e, n)

        privateKey = (n, d)
        publicKey = (n, e)

        return (privateKey, publicKey)


if __name__ == "__main__":
    private, public = RSAEncryption.generateKeyPair()
    print(private, public)
