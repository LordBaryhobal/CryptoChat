def getModularInverse(a: int, n: int) -> int:
    """
    Calculates the modular inverse of a number
    using the Extended Euclidean Algorithm

    Args:
        a: the number to invert
        n: the modulo
    Returns:
        the modular inverse of `a` (mod `n`)
    """

    oldR: int = a
    r: int = n

    oldS: int = 1
    s: int = 0

    oldT: int = 0
    t: int = 1

    while r != 0:
        quotient = oldR // r
        oldR, r = r, oldR - quotient * r
        oldS, s = s, oldS - quotient * s
        oldT, t = t, oldT - quotient * t

    return oldS % n


if __name__ == '__main__':
    a = 7
    n = 9
    print(getModularInverse(a, n))
