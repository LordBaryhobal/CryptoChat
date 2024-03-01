import socket
from typing import Union, Optional

from PIL import Image

from client.protocol import Protocol


class NotConnectedError(Exception):
    ...


class Client:
    """Simple class to send and receive messages using a TCP socket"""

    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.socket: Optional[socket.socket] = None

    def __enter__(self) -> "Client":
        success = self.connect()
        return self

    def __exit__(self, *args) -> None:
        self.disconnect()

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

    def send(self, msg: Union[bytes, str, Image.Image], onlyServer: bool = False) -> None:
        """
        Sends a message
        Args:
            msg: the message to send
            onlyServer: (for text message) whether this message is only sent to the server or broadcast to everyone
        Raises:
            TypeError: if the payload is neither a string nor a PIL Image
            ValueError: if the payload is an image exceeding the size limitations
        """

        if self.socket is None:
            raise NotConnectedError("Cannot send messages unless connected to the server")

        payload = Protocol.encode(msg, onlyServer)
        self.socket.send(payload)

    def receive(self, rawBytes: bool = False) -> Union[str, bytes]:
        """
        Waits and reads a message from the server

        Args:
            rawBytes: whether to receive a structured message (text or image) or raw bytes (i.e. not decoded)
        Returns:
            the received message, or an empty string if the format is incorrect
        Raises:
            ProtocolError: if the payload is malformed (missing magic bytes, invalid message type, etc.)
        """

        if self.socket is None:
            raise NotConnectedError("Cannot receive messages unless connected to the server")

        msgBytes = self.socket.recv(4096)

        msg = Protocol.decode(msgBytes, rawBytes)
        if isinstance(msg, (str, bytes)):
            return msg

        else:
            return f"<image ({msg.width}x{msg.height})>"
