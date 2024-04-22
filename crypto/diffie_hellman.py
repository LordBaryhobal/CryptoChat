import random

from math_utils.primes import getLargestPrime, getPrimeFactors
from math_utils.ring import Ring


class DiffieHellman:
    NAME = "DifHel"

    def __init__(self):
        self.p = getLargestPrime(random.randint(2, 5000))
        print(f"p = {self.p}")
        self.ring = Ring(self.p)

        self.prime_factor_list = set(getPrimeFactors(self.p - 1))
        print(f"prime factors = {self.prime_factor_list}")

        self.g = self.find_generator()
        print(f"g = {self.g}")

        self.a = random.randint(2, 5000)
        print(f"a = {self.a}")

        self.gA = self.ring.fastPow(self.g, self.a)

    def compute_secret(self, gB: int) -> int:
        return self.ring.fastPow(gB, self.a)

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
