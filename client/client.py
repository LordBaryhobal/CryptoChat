import socket
from typing import Union, Optional

from PIL import Image

from ansi import ANSI
from client.protocol import Protocol
from logger import Logger
from utils import formatException


class NotConnectedError(Exception):
    ...


class Client:
    """Simple class to send and receive messages using a TCP socket"""

    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.socket: Optional[socket.socket] = None
        self.logger = Logger("Client", styles={
            "info": [],
            "error": [ANSI.RED, ANSI.BOLD],
            "warning": [ANSI.YELLOW, ANSI.ITALIC],
            "success": [ANSI.LGREEN, ANSI.ITALIC]
        })
        self.sendListeners: list[MessageListener] = []
        self.receiveListeners: list[MessageListener] = []

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
        except socket.error as e:
            self.socket = None
            self.logger.error("An error occurred while trying to connect")
            self.logger.error(formatException(e))
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
            NotConnectedError: if the client is not connected to the server
        """

        if self.socket is None:
            raise NotConnectedError("Cannot send messages unless connected to the server")

        payload = Protocol.encode(msg, onlyServer)
        self._onSend(payload)
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
            NotConnectedError: if the client is not connected to the server
        """

        if self.socket is None:
            raise NotConnectedError("Cannot receive messages unless connected to the server")

        # Read magic bytes + type byte
        msgBytes = self.socket.recv(len(Protocol.MAGIC) + 1)
        lengthBytes = Protocol.getPayloadLengthBytesCount(msgBytes)

        # Read payload size
        msgBytes += self.socket.recv(lengthBytes)
        payloadLength = Protocol.getPayloadLength(msgBytes)

        # Read payload
        msgBytes += self.socket.recv(payloadLength)

        self._onReceive(msgBytes)

        msg = Protocol.decode(msgBytes, rawBytes)
        if isinstance(msg, (str, bytes)):
            return msg

        else:
            return f"<image ({msg.width}x{msg.height})>"

    def addOnSendListener(self, listener: "MessageListener") -> None:
        self.sendListeners.append(listener)

    def addOnReceiveListener(self, listener: "MessageListener") -> None:
        self.receiveListeners.append(listener)

    def _onReceive(self, msgBytes: bytes) -> None:
        for listener in self.receiveListeners:
            listener.onMessage(msgBytes)

    def _onSend(self, msgBytes: bytes) -> None:
        for listener in self.sendListeners:
            listener.onMessage(msgBytes)

    def reconnect(self, host: str, port: int) -> None:
        """
        Tries to reconnect to the server with the new host and port
        Args:
            host: the new host
            port: the new port
        """
        self.disconnect()
        self.host = host
        self.port = port
        self.connect()


class MessageListener:
    def onMessage(self, msgBytes: bytes) -> None:
        raise NotImplementedError