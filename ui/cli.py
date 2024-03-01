from typing import Type, Optional

from client.client import Client
from crypto.algorithm import Algorithm
from crypto.shift_encryption import ShiftEncryption
from crypto.xor_encryption import XOREncryption
from utils import formatException


class CLI:
    ACTIONS: list[list[str, Type[Algorithm], bool]] = [
        ["Manual message", None, False],
        ["Shift (encryption)", ShiftEncryption, False],
        ["Shift (decryption)", ShiftEncryption, True],
        ["XOR (encryption)", XOREncryption, False],
        ["XOR (decryption)", XOREncryption, True],
        ["Quit", None, False],
    ]

    def __init__(self, client: Client):
        self.running = True
        self.client = client

    def mainloop(self) -> None:
        while self.running:
            action = self.chooseAction()
            if action == len(self.ACTIONS) - 1:
                self.running = False

            elif action == 0:
                print("Choose a mode:")
                print("  1) Broadcast")
                print("  2) Server")
                choice = self.readInt(1, 2)

                print("Message:")
                msg = self.readStr()
                try:
                    self.client.send(msg, choice == 2)

                    ans = self.client.receive()
                    print(f"[SERVER] {ans}")
                    if choice == 2:
                        ans = self.client.receive(True)
                        print(f"[SERVER] {ans}")
                except Exception as e:
                    print(f"[ERROR] An error occurred while trying to send manual message")
                    print(f"[ERROR] {formatException(e)}")

            else:
                try:
                    self.startTask(action)
                except Exception as e:
                    print(f"[ERROR] An error occurred while trying to execute the task")
                    print(f"[ERROR] {formatException(e)}")

    def chooseAction(self) -> int:
        print("Choose an action:")

        for i, (name, algo, decrypt) in enumerate(self.ACTIONS):
            print(f"  {i+1}) {name}")

        choice = self.readInt(1, len(self.ACTIONS))

        return choice - 1

    def startTask(self, action: int) -> None:
        actionInfo = self.ACTIONS[action]
        algorithm: Type[Algorithm] = actionInfo[1]
        decrypt: bool = actionInfo[2]

        print("[TASK] Length of input data:")
        size = self.readInt(1, 10_000)

        message = f"task {algorithm.NAME} {'decode' if decrypt else 'encode'} {size}"
        self.client.send(message, True)

        if not decrypt:
            keyMsg = self.client.receive()
            print(f"[SERVER] {keyMsg}")
            key = algorithm.parseTaskKey(keyMsg)
            print(f"[TASK] key = {key}")

            plaintextMsg = self.client.receive()
            print(f"[SERVER] {plaintextMsg}")
            print(f"[TASK] plaintext = {plaintextMsg}")

            transcoder = algorithm(key)
            print(f"[TASK] transcoder = {transcoder}")

            encrypted = transcoder.encode(plaintextMsg)
            print(f"[TASK] encrypted bytes = {encrypted}")
            self.client.send(encrypted, True)

            successMsg = self.client.receive()
            print(f"[SERVER] {successMsg}")
            success = self.parseEncodeSuccess(successMsg)

            print("Success !" if success else "Oops, it didn't work")

        else:
            taskMsg = self.client.receive()
            print(f"[SERVER] {taskMsg}")
            ciphertextMsg = self.client.receive(True)
            print(f"[SERVER] {ciphertextMsg}")
            print(f"[TASK] ciphertext = {ciphertextMsg}")

    def readInt(self, minVal: Optional[int] = None, maxVal: Optional[int] = None) -> int:
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
        while True:
            try:
                val = input("> ")

                if maxLen is not None:
                    assert len(val) <= maxLen
            except:
                continue

            return val

    def parseEncodeSuccess(self, msg: str) -> bool:
        if msg == "The encoding is correct !":
            return True

        if msg != "The encoding is invalid !":
            print(f"[WARNING] Unrecognized success message: {msg}")

        return False
