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

    def inverse(self, a: int) -> int:
        """
        Finds the inverse of the given number
        Args:
            a: the number to invert

        Returns:
            the inverse of `a`
        """
        return getModularInverse(a, self.modulo)
