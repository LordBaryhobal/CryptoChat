from math_utils.modulo import getModularInverse


class Ring:
    """Class representing a ring"""

    def __init__(self, modulo: int) -> None:
        self.modulo: int = modulo

    def add(self, a: int, b: int) -> int:
        """
        Adds two numbers
        Args:
            a: the first number
            b: the second number

        Returns:
            the sum of `a` and `b`
        """
        return (a + b) % self.modulo

    def sub(self, a: int, b: int) -> int:
        """
        Subtracts two numbers
        Args:
            a: the first number
            b: the second number

        Returns:
            the difference of `a` and `b`
        """
        return (a - b) % self.modulo

    def multiply(self, a: int, b: int) -> int:
        """
        Multiplies two numbers
        Args:
            a: the first number
            b: the second number

        Returns:
            the product of the `a` and `b`
        """
        return (a * b) % self.modulo

    def pow(self, a: int, b: int) -> int:
        """
        Raises a number to the given power
        Args:
            a: the base
            b: the exponent

        Returns:
            the exponentiation of `a` to the power of `b`
        """

        r: int = 1

        for _ in range(b):
            r = self.multiply(r, a)

        return r

    def fastPow(self, a: int, b: int) -> int:
        """
        Raises a number to the given power using a fast algorithm
        Args:
            a: the base
            b: the exponent
        Returns:
            the exponentiation of `a` to the power of `b`
        """

        result = 1
        currentPower: int = a % self.modulo
        powerSelect: int = b

        while powerSelect != 0:
            if powerSelect & 1:
                result = self.multiply(result, currentPower)

            currentPower = self.multiply(currentPower, currentPower)
            powerSelect >>= 1

        return result

    def inverse(self, a: int) -> int:
        """
        Finds the inverse of the given number
        Args:
            a: the number to invert

        Returns:
            the inverse of `a`
        """
        return getModularInverse(a, self.modulo)

if __name__ == "__main__":
    ring = Ring(17)
    import time
    t1 = time.time()
    print(ring.pow(120, 23000875))
    t2 = time.time()
    print(ring.fastPow(120, 23000875))
    t3 = time.time()
    print(f"pow: {t2-t1:.5f}s")
    print(f"fast pow: {t3-t2:.5f}s")