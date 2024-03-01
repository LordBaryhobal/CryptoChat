import socket
from typing import Union

from PIL import Image

from client.protocol import Protocol


class Client:
    """Simple class to send and receive messages using a TCP socket"""

    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.socket: Union[socket.socket, None] = None

    def connect(self) -> bool:
        """
        Tries to connect to the server

        Returns:
            `True` if the connection was successful, `False` otherwise
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

    def send(self, msg: Union[str, Image.Image], onlyServer: bool = False) -> None:
        """
        Sends a message
        Args:
            msg: the message to send
            onlyServer: (for text message) whether this message is only sent to the server or broadcast to everyone
        Raises:
            TypeError: if the payload is neither a string nor a PIL Image
            ValueError: if the payload is an image exceeding the size limitations
        """

        payload = Protocol.encode(msg, onlyServer)
        self.socket.send(payload)

    def receive(self) -> str:
        """
        Waits and reads a message from the server

        Returns:
            the received message, or an empty string if the format is incorrect
        Raises:
            ProtocolError: if the payload is malformed (missing magic bytes, invalid message type, etc.
        """

        msgBytes = self.socket.recv(4096)

        msg = Protocol.decode(msgBytes)
        if isinstance(msg, str):
            return msg

        else:
            return f"<image ({msg.width}x{msg.height})>"
