import json
import os

from client.protocol import Protocol
from crypto.algorithm import Algorithm
from crypto.shift_encryption import ShiftEncryption
from utils import getRootPath, formatException


def sortingCriterion(pair: tuple[str, float]) -> float:
    return pair[1]

class FrequencyAnalysis(Algorithm):
    def letter_counter(self, ciphertext: list[int]) -> dict:
        counts = {}
        frequencies = {}

        for i in ciphertext:
            if i not in counts:
                counts[i] = 0
            counts[i] += 1
        total = sum(counts.values())
        for char, count in counts.items():
            frequencies[char] = count / total
        return frequencies

    def compare(self, ciphertextBytes: bytes, dictFrequency: dict) -> int:
        ciphertextInts = Protocol.groupBytesIntoInt(ciphertextBytes)

        cipher_frequency = self.letter_counter(ciphertextInts)
        charFrequencyPairs = cipher_frequency.items()
        charFrequencyPairs = sorted(charFrequencyPairs, key = sortingCriterion, reverse = True)
        print(charFrequencyPairs)
        dictFrequencyPairs = dictFrequency.items()
        dictFrequencyPairs = sorted(dictFrequencyPairs, key=sortingCriterion, reverse=True)
        print(dictFrequencyPairs)

        # Comparing first letter

        bestKey = None
        bestAverage = None

        # For each encrypted letter
        for j in range(len(charFrequencyPairs)):
            cipherLetterValue = charFrequencyPairs[j][0]

            # For each letter in dictionary
            for i in range(len(dictFrequencyPairs)):
                plainLetterValue = int.from_bytes(dictFrequencyPairs[i][0].encode("UTF-8"), "big")
                key = cipherLetterValue - plainLetterValue
                if key < 0:
                    continue
                print(f"Trying key {key}")

                try:
                    decoder = ShiftEncryption(key)
                    decodedMessage = decoder.decode(ciphertextBytes)
                    new_cipher_frequency = self.mapFrequencies(cipher_frequency, ciphertextInts, decodedMessage)

                    average = self.get_average_diff(new_cipher_frequency, dictFrequency)
                    if bestAverage is None or average < bestAverage:
                        bestAverage = average
                        bestKey = key

                except Exception as e:
                    if key == 1:
                        print(formatException(e))

        print(f"Best key: {bestKey}")
        print(f"Best average: {bestAverage}")
        return bestKey

    def mapFrequencies(self, charFrequencies: dict[int, float], ciphertext: list[int], decodedMessage: str) -> dict[str, float]:
        newFrequencies = {}

        for i in range(len(ciphertext)):
            encrypted_letter = ciphertext[i]
            decrypted_letter = decodedMessage[i]
            frequency = charFrequencies[encrypted_letter]
            newFrequencies[decrypted_letter] = frequency

        return newFrequencies

    def get_average_diff(self, cipher_frequencies: dict[str, float], dict_frequencies: dict[str, float]) -> float:
        total = 0
        count = 0

        for i in cipher_frequencies.keys():
            if i in dict_frequencies:
                frequencyA = cipher_frequencies[i]
                frequencyB = dict_frequencies[i]
                diff = abs(frequencyA - frequencyB) / frequencyB
                total += diff
                count += 1

        average = total / count
        print(average)
        return average

if __name__ == '__main__':
    dictPath = os.path.join(getRootPath(), "res", "francais_freq.json")
    file = open(dictPath, "r")

    dictFrequency = json.load(file)

    file.close()

    encrypter = ShiftEncryption(1)
    rawText = "banana"
    rawText = """La taille des selles animales varie fortement suivant la corpulence de l'animal.

Celles des lapins font generalement 1,2 cm de diametre et sont seches au toucher.

Les fientes aviaires resultent d'un melange d'urine et de feces au niveau du cloaque, sont liees a l'absence de vessie urinaire chez les oiseaux, laquelle peut etre interpretee comme une adaptation au vol (en) (les organes les plus lourds etant rassembles au centre du corps). Elles sont composees d'urine liquide tres concentree (economie d'eau, adaptation a la conquete des airs), d'acides uriques (precipitant sous forme d'urates, sels d'acide urique qui protegent les tubules renaux de la cristallisation de ces acides) et de feces."""
    ciphertext = encrypter.encode(rawText)

    test = FrequencyAnalysis()
    test.letter_counter("banana")

    key = test.compare(ciphertext, dictFrequency)
    decoder = ShiftEncryption(key)
    decodedMessage = decoder.decode(ciphertext)
    print(f"Decoded as: {decodedMessage}")