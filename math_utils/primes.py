from math import sqrt


def getLargestPrime(maxValue: int) -> int:
    """
    Finds the largest prime number <= maxValue
    Args:
        maxValue: the maximum value
    Returns:
        the largest prime <= `maxValue`
    """

    # If `maxValue` is even, change to the previous odd value
    if maxValue % 2 == 0:
        maxValue -= 1

    # Only check odd numbers
    for i in range(maxValue, 2, -2):
        if isPrime(i):
            return i

    return 2


def isPrime(n: int) -> bool:
    """
    Checks whether the given number is prime
    Args:
        n: the number to check
    Returns:
        True if the number is prime, False otherwise
    """

    if n <= 1:
        return False

    # Only check up to the square root for more efficiency
    for j in range(2, int(sqrt(n))):
        if n % j == 0:
            return False

    return True


def areCoprimes(a: int, b: int) -> bool:
    """
    Checks whether two numbers are coprime
    Args:
        a: the first number
        b: the second number
    Returns:
        True if the numbers are coprime, False otherwise
    """

    # Only check up to the smallest number for more efficiency
    for i in range(2, min(a, b)):
        # If `i` is a factor of `a` and a factor of `b`
        if a % i == 0 and b % i == 0:
            return False

    return True


def gcd(a: int, b: int) -> int:
    """
    Calculates the greatest common divisor of two numbers
    using the Euclidean algorithm
    
    Args:
        a: the first number
        b: the second number
    Returns:
        the greatest common divisor of `a` and `b`
    """

    while b != 0:
        a, b = b, a % b

    return a


if __name__ == '__main__':
    print(gcd(144, 60))
    print(gcd(15, 40))
