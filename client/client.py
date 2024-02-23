import socket
from typing import Union


class Client:
    """Simple class to send and receive messages using a TCP socket"""

    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.socket: Union[socket.socket, None] = None

    def connect(self) -> bool:
        """
        Tries to connect to the server

        Returns: True if the connection was successful, False otherwise
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.host, self.port))
        except socket.error:
            self.socket = None
            print("An error occurred while trying to connect")
            return False

        return True

    def disconnect(self) -> None:
        """
        Closes the connection with the server
        """

        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def send(self, msg: str, msgType: str = "t") -> None:
        """
        Sends a message with the given message type
        Args:
            msg: the message to send
            msgType: the message type (one of 't', 'i' or 's')
        """

        payload = b"ISC" + msgType.encode("utf-8")
        length = len(msg)
        payload += length.to_bytes(2, "big")

        msgBytes = msg.encode("utf-8")
        for b in msgBytes:
            payload += bytes([0, 0, 0, b])

        self.socket.send(payload)

    def receive(self) -> str:
        """
        Waits and reads a message from the server

        Returns: the received message, or an empty string
        if the format is incorrect
        """

        msgBytes = self.socket.recv(4096)

        if msgBytes[0:3] != b"ISC":
            print(f"Format error: the payload does not start with ISC but {msgBytes[0:3]}")
            return ""

        msgType = msgBytes[3:4].decode("utf-8")

        if msgType not in ["t", "i", "s"]:
            print(f"Format error: the message type is '{msgType}'")
            return ""

        length = int.from_bytes(msgBytes[4:6], "big")

        msg = b""
        for i in range(0, length):
            offset = 9 + i * 4
            msg += msgBytes[offset:offset + 1]

        return msg.decode("utf-8")
