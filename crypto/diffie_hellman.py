import random

from crypto.algorithm import Algorithm
from math_utils.primes import getLargestPrime, getPrimeFactors, isPrime


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
        while True:
            self.p = random.randint(2, getLargestPrime(5000))
            if isPrime(self.p): break
        print("p = " + str(self.p))
        self.prime_factor_list = set(getPrimeFactors(self.p - 1))
        print(self.prime_factor_list)
        self.g = self.find_generator()
        print(self.g)
        self.a = random.randint(0,5000)
        # todo: insert code to fetch secret number B = g^b mod p from server
        secret = (self.g ** self.a % self.p) * self.B

    def find_generator(self):
        for g in range(2, self.p):
            self.check_valid_generator(g)
            if self.check_valid_generator(g):
                return g

    def check_valid_generator(self, g) -> bool:
        check = False
        for f in self.prime_factor_list:
            a = (self.p - 1) / f
            if (g ** a) % 7 == 1 % self.p:
                return False
            else:
                check = True
        return check


if __name__ == '__main__':
    DiffieHellman()
