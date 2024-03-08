import json
import os


def computeFrequencies(path: str) -> dict:
    """
    Computes the frequency of every letter in a dictionary
    Args:
        path: the input file path

    Returns:
        a dictionary of each letter and its frequency of appearance
    """

    with open(path, "r") as f:
        words = f.read().splitlines()

    counts = {}
    frequencies = {}

    for word in words:
        for c in word:
            if c not in counts:
                counts[c] = 0
            counts[c] += 1

    total = sum(counts.values())
    for char, count in counts.items():
        frequencies[char] = count / total

    return frequencies


if __name__ == '__main__':
    filename = input("Dictionary file name: ")
    filename = os.path.basename(filename)
    name = os.path.splitext(filename)[0]
    inpath = os.path.abspath(filename)
    outpath = os.path.abspath(name + "_freq.json")
    frequencies = computeFrequencies(inpath)

    with open(outpath, "w") as f:
        json.dump(frequencies, f, indent=4)

    print(f"Saved in {outpath}")
