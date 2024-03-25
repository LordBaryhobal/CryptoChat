import random
import re
from typing import Optional

from client.client import Client
from client.protocol import Protocol
from crypto.algorithm import Algorithm
from math_utils.modulo import extendedGCD
from math_utils.primes import areCoprimes, getLargestPrime
from math_utils.ring import Ring


class RSAEncryption(Algorithm):
    NAME = "RSA"

    def __init__(self, publicKey: tuple[int, int], privateKey: Optional[tuple[int, int]] = None):
        super().__init__()
        self.publicKey: tuple[int, int] = publicKey
        self.privateKey: Optional[tuple[int, int]] = privateKey

    def __repr__(self):
        return f"<RSA(public={self.publicKey}, private={self.privateKey})>"

    def encode(self, plaintext: str) -> bytes:
        out = b""

        n, e = self.publicKey
        ring = Ring(n)
        for i in range(len(plaintext)):
            value = Protocol.charToInt(plaintext[i])
            encodedValue = ring.fastPow(value, e)
            out += Protocol.intToPaddedBytes(encodedValue)

        return out

    def decode(self, ciphertext: bytes) -> str:
        if self.privateKey is None:
            raise Exception("Cannot decode without a private key")

        ints = Protocol.groupBytesIntoInt(ciphertext)
        out = []

        n, d = self.privateKey
        ring = Ring(n)
        for i in range(len(ints)):
            encodedValue = ints[i]
            value = ring.fastPow(encodedValue, d)
            out.append(value)

        return bytes(out).decode("UTF-8")

    @staticmethod
    def parseTaskKey(msg: str) -> tuple[int, int]:
        m: Optional[re.Match[str]] = re.search(r"n=(\d+), e=(\d+)", msg)

        n: int = int(m.group(1))
        e: int = int(m.group(2))

        publicKey = (n, e)

        return publicKey

    @staticmethod
    def generateKeyPair() -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Generates a public/private key pair
        Returns:
            a tuple containing the public and private key (in this order)
        """

        # Find 2 large prime numbers p and q, with a large difference
        maxP: int = random.randint(15_000, 20_000)
        p: int = getLargestPrime(maxP)

        maxQ: int = 10 * p
        q: int = getLargestPrime(maxQ)

        # Compute n = p * q -> n should be smaller than 2^32 (max value on 4 bytes)
        n: int = p * q

        k: int = (p - 1) * (q - 1)

        for e in range(k - 2, 1, -1):
            if areCoprimes(e, k):
                break

        else:
            raise Exception("Could not find e coprime with k")

        bezoutA, bezoutB, _, _, _ = extendedGCD(e, k)
        if bezoutA < 0:
            bezoutA += k

        d: int = bezoutA

        publicKey = (n, e)
        privateKey = (n, d)

        return (publicKey, privateKey)

    @staticmethod
    def decryptTask(taskMsg: str, client: Client) -> None:
        # Generate key pair
        public, private = RSAEncryption.generateKeyPair()
        publicStr = f"{public[0]},{public[1]}"
        decryptor = RSAEncryption(public, private)
        print(decryptor)
        print("message sent to server: " + publicStr)

        # Send public key (as n,e)
        client.send(publicStr, True)

        # Rreceive encrypted message
        encryptedMessage = client.receive(True)
        print(encryptedMessage)

        # Decrypt message using private key
        decryptedMessage = decryptor.decode(encryptedMessage)
        print(decryptedMessage)

        # Send decrypted message
        client.send(decryptedMessage, True)


if __name__ == "__main__":
    public, private = RSAEncryption.generateKeyPair()
    print(public, private)

    rsa = RSAEncryption(public, private)
    msg = "banana"
    encoded = rsa.encode(msg)
    print(encoded)
    decoded = rsa.decode(encoded)
    print(decoded)
