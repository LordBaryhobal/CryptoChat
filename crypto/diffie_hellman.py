import random

from math_utils.primes import getLargestPrime, getPrimeFactors


class DiffieHellman(Algorithm):
    NAME = "Diffie-Hellman"

    def __init__(self):
        p = getLargestPrime(5000)
        primeFactorList = set(getPrimeFactors(p - 1))

    def findGenerator(self, primeFactorList, n):
        for g in range(2, n - 1):

    def checkValidGenerator(self, primeFactorList,g, n):
        for i in primeFactorList:

