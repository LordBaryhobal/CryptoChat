from typing import Type, Optional

from client.client import Client
from crypto.algorithm import Algorithm
from crypto.rsa_encryption import RSAEncryption
from crypto.shift_encryption import ShiftEncryption
from crypto.vigenere_encryption import VigenereEncryption
from utils import formatException


class CLI:
    """
    Class to provide a console interface for executing the different tasks
    """

    ACTIONS: list[list[str, Type[Algorithm], bool]] = [
        ["Manual message", None, False],
        ["Shift (encryption)", ShiftEncryption, False],
        ["Shift (decryption)", ShiftEncryption, True],
        #["XOR (encryption)", XOREncryption, False],
        #["XOR (decryption)", XOREncryption, True],
        ["Vigénère (encryption)", VigenereEncryption, False],
        ["Vigénère (decryption)", VigenereEncryption, True],
        ["RSA (encryption)", RSAEncryption, False],
        ["RSA (decryption)", RSAEncryption, True],
        ["Quit", None, False],
    ]

    def __init__(self, client: Client):
        self.running = True
        self.client = client

    def mainloop(self) -> None:
        """
        Main excution loop, displaying menus in the console, letting the user
        send messages and perform tasks
        """

        while self.running:
            action = self.chooseAction()

            # Quit
            if action == len(self.ACTIONS) - 1:
                self.running = False

            # Manual message
            elif action == 0:
                print("Choose a mode:")
                print("  1) Broadcast")
                print("  2) Server")
                choice = self.readInt(1, 2)

                print("Message:")
                msg = self.readStr()
                try:
                    self.client.send(msg, choice == 2)

                    answer = self.client.receive()
                    print(f"[SERVER] {answer}")
                    if choice == 2:
                        answer = self.client.receive(True)
                        print(f"[SERVER] {answer}")
                except Exception as e:
                    print(f"[ERROR] An error occurred while trying to send manual message")
                    print(f"[ERROR] {formatException(e)}")

            # Crypto task
            else:
                try:
                    self.startTask(action)
                except Exception as e:
                    print(f"[ERROR] An error occurred while trying to execute the task")
                    print(f"[ERROR] {formatException(e)}")

    def chooseAction(self) -> int:
        """
        Displays the main menu and lets the use choose one of the action
        Returns:
            the chosen action index
        """

        print("Choose an action:")

        for i, (name, algo, decrypt) in enumerate(self.ACTIONS):
            print(f"  {i+1}) {name}")

        choice = self.readInt(1, len(self.ACTIONS))

        return choice - 1

    def startTask(self, action: int) -> None:
        """
        Starts the given task
        Args:
            action: the index of the task to perform
        """

        actionInfo = self.ACTIONS[action]
        algorithm: Type[Algorithm] = actionInfo[1]
        decrypt: bool = actionInfo[2]

        print("[TASK] Length of input data:")
        size = self.readInt(1, 10_000)

        message = f"task {algorithm.NAME} {'decode' if decrypt else 'encode'} {size}"
        self.client.send(message, True)

        if not decrypt:
            # Parse the encryption key from the server's message
            keyMsg = self.client.receive()
            print(f"[SERVER] {keyMsg}")
            key = algorithm.parseTaskKey(keyMsg)
            print(f"[TASK] key = {key}")

            # Get the message to encrypt
            plaintextMsg = self.client.receive()
            print(f"[SERVER] {plaintextMsg}")
            print(f"[TASK] plaintext = {plaintextMsg}")

            # Encrypt the message and send the result
            transcoder = algorithm(key)
            print(f"[TASK] transcoder = {transcoder}")

            encrypted = transcoder.encode(plaintextMsg)
            print(f"[TASK] encrypted bytes = {encrypted}")
            self.client.send(encrypted, True)

            # Parse the answer and determine if it was a success
            successMsg = self.client.receive()
            print(f"[SERVER] {successMsg}")
            success = self.parseEncodeSuccess(successMsg)

            print("Success !" if success else "Oops, it didn't work")

        else:
            taskMsg = self.client.receive()
            print(f"[SERVER] {taskMsg}")

            algorithm.decryptTask(taskMsg, self.client)

            successMsg = self.client.receive()
            print(f"[SERVER] {successMsg}")
            success = self.parseDecodeSuccess(successMsg)

            print("Success !" if success else "Oops, it didn't work")

    def readInt(self, minVal: Optional[int] = None, maxVal: Optional[int] = None) -> int:
        """
        Reads an integer from the console
        Args:
            minVal: the minimum value (incl.). If None, there is no lower bound on the value
            maxVal: the maximum value (incl.). If None, there is no upper bound on the value
        Returns:
            the value given by the user
        """

        while True:
            try:
                val = int(input("> "))
                if minVal is not None:
                    assert val >= minVal

                if maxVal is not None:
                    assert val <= maxVal
            except:
                continue

            return val

    def readFloat(self, minVal: Optional[float] = None, maxVal: Optional[float] = None) -> float:
        """
        Reads a float from the console
        Args:
            minVal: the minimum value (incl.). If None, there is no lower bound on the value
            maxVal: the maximum value (incl.). If None, there is no upper bound on the value
        Returns:
            the value given by the user
        """

        while True:
            try:
                val = float(input("> "))
                if minVal is not None:
                    assert val >= minVal

                if maxVal is not None:
                    assert val <= maxVal
            except:
                continue

            return val

    def readStr(self, maxLen: Optional[int] = None) -> str:
        """
        Reads a string from the console
        Args:
            maxLen: the maximum length of the string. If None, there is no limit
        Returns:
            the string given by the user
        """

        while True:
            try:
                val = input("> ")

                if maxLen is not None:
                    assert len(val) <= maxLen
            except:
                continue

            return val

    def parseEncodeSuccess(self, msg: str) -> bool:
        """
        Parses the server's reply and determines the success of the last task
        Args:
            msg: the server's reply message
        Returns:
            true if it is a success, false otherwise
        """

        if msg == "The encoding is correct !":
            return True

        if msg != "The encoding is invalid !":
            print(f"[WARNING] Unrecognized success message: {msg}")

        return False
