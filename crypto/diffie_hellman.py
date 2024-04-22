import random

from crypto.algorithm import Algorithm
from math_utils.primes import getLargestPrime, getPrimeFactors
from math_utils.ring import Ring


class DiffieHellman(Algorithm):
    NAME = "Diffie-Hellman"
    p = 0
    g = 0
    a = 0
    B = 1
    secret = 0
    prime_factor_list = ()

    def __init__(self):
        super().__init__()
        self.p = getLargestPrime(random.randint(2, 5000))
        print(f"p = {self.p}")
        self.ring = Ring(self.p)

        self.prime_factor_list = set(getPrimeFactors(self.p - 1))
        print(f"prime factors = {self.prime_factor_list}")

        self.g = self.find_generator()
        print(f"g = {self.g}")

        self.a = random.randint(2, 5000)
        print(f"a = {self.a}")

        # todo: insert code to fetch secret number B = g^b mod p from server
        secret = self.ring.fastPow(self.B, self.a)
        print(f"secret = {secret}")

    def find_generator(self):
        for g in range(2, self.p):
            if self.check_valid_generator(g):
                return g

    def check_valid_generator(self, g) -> bool:
        check = False
        for f in self.prime_factor_list:
            a = (self.p - 1) // f
            if self.ring.fastPow(g, a) == 1:
                return False
            else:
                check = True
        return check


if __name__ == '__main__':
    DiffieHellman()
