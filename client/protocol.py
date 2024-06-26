from typing import Union

from PIL import Image


class ProtocolError(Exception):
    ...


class Protocol:
    """Simple class to encode and decode message according to the established protocol"""

    MAGIC = b"ISC"
    TEXT = b"t"
    IMAGE = b"i"
    SERVER = b"s"

    BYTE_SIZE = 4
    MAX_IMAGE_WIDTH = 128
    MAX_IMAGE_HEIGHT = 128

    @staticmethod
    def getPayloadLengthBytesCount(magicAndType: bytes) -> int:
        """
        Returns the number of bytes to read for the payload length
        Args:
            magicAndType: initial magic and type bytes

        Returns:
            the number of bytes to read for the payload length
        Raises:
            ProtocolError: if the payload is malformed (missing magic bytes, invalid message type, etc.)
        """

        magicLen = len(Protocol.MAGIC)
        if magicAndType[:magicLen] != Protocol.MAGIC:
            raise ProtocolError(f"Payload must start with {Protocol.MAGIC} (not {magicAndType[:magicLen]})")

        typeByte = magicAndType[magicLen:magicLen+1]

        if typeByte == Protocol.TEXT or typeByte == Protocol.SERVER:
            return 2

        if typeByte == Protocol.IMAGE:
            return 2

        raise ProtocolError(f"Unrecognized payload type {typeByte}")

    @staticmethod
    def getPayloadLength(headerBytes: bytes) -> int:
        """
        Returns the number of bytes to read for the payload
        Args:
            headerBytes: the initial header bytes (magic + type + payload size)
        Returns:
            the number of bytes to read for the payload
        Raises:
            ProtocolError: if the payload is malformed (missing magic bytes, invalid message type, etc.)
        """

        magicLen = len(Protocol.MAGIC)
        typeByte = headerBytes[magicLen:magicLen+1]

        if typeByte == Protocol.TEXT or typeByte == Protocol.SERVER:
            return int.from_bytes(headerBytes[magicLen+1:magicLen+3], "big") * Protocol.BYTE_SIZE

        if typeByte == Protocol.IMAGE:
            width = int.from_bytes(headerBytes[magicLen+1:magicLen+2], "big")
            height = int.from_bytes(headerBytes[magicLen+2:magicLen+3], "big")
            return width * height * 3

        raise ProtocolError(f"Unrecognized payload type {typeByte}")


    @staticmethod
    def encode(payload: Union[str, Image.Image, bytes], onlyServer: bool = False) -> bytes:
        """
        Encodes a payload into bytes to send to the server
        Args:
            payload: the payload to encode. Can be either a string or an PIL Image
            onlyServer: (for text message) whether this message is only sent to the server or broadcast to everyone

        Returns:
            the encoded payload bytes to be sent to the server

        Raises:
            TypeError: if the payload is neither a string nor a PIL Image
            ValueError: if the payload is an image exceeding the size limitations
        """

        if isinstance(payload, str):
            payloadBytes = Protocol.encodeTextPayload(payload)
            typeByte = Protocol.SERVER if onlyServer else Protocol.TEXT

        elif isinstance(payload, Image.Image):
            if onlyServer:
                print("[WARNING] Server-only mode ignored when sending image")

            payloadBytes = Protocol.encodeImagePayload(payload)
            typeByte = Protocol.IMAGE

        elif isinstance(payload, bytes):
            length = len(payload) // Protocol.BYTE_SIZE
            payloadBytes = length.to_bytes(2, "big") + payload
            typeByte = Protocol.SERVER if onlyServer else Protocol.TEXT

        else:
            raise TypeError(f"Unsupported payload type '{type(payload)}', must be either a str or an Image")

        return Protocol.MAGIC + typeByte + payloadBytes

    @staticmethod
    def encodeTextPayload(payload: str) -> bytes:
        """
        Encodes a text message into bytes using the correct format
        Args:
            payload: the text message to encode

        Returns:
            the encoded message bytes (only contains length and message)
        """

        byteList = []

        byteList += len(payload).to_bytes(2, "big")

        for char in payload:
            charBytes = char.encode("utf-8").rjust(Protocol.BYTE_SIZE, b"\0")
            byteList += charBytes

        return bytes(byteList)

    @staticmethod
    def encodeImagePayload(payload: Image.Image) -> bytes:
        """
        Encodes an image into bytes using the correct format
        Args:
            payload: the image to encode

        Returns:
            the encoded image bytes (only contains size and pixel data)

        Raises:
            ValueError: if the image is too big
        """

        maxW, maxH = Protocol.MAX_IMAGE_WIDTH, Protocol.MAX_IMAGE_HEIGHT
        if payload.width > maxW or payload.height > maxH:
            raise ValueError(f"Image is too big (max {maxW}x{maxH})")

        byteList = []

        byteList.append(payload.width)
        byteList.append(payload.height)

        for y in range(payload.height):
            for x in range(payload.width):
                byteList += payload.getpixel((x, y))

        return bytes(byteList)

    @staticmethod
    def decode(payloadBytes: bytes, rawBytes: bool = False) -> Union[str, Image.Image, bytes]:
        """
        Decodes payload bytes into the correct message
        Args:
            payloadBytes: the encoded payload bytes
            rawBytes: if true, the payload will not be decoded and raw bytes will be returned
        Returns:
            the decoded message (either a string or a PIL Image)
        Raises:
            ProtocolError: if the payload is malformed (missing magic bytes, invalid message type, etc.)
        """

        magicLen = len(Protocol.MAGIC)
        if payloadBytes[:magicLen] != Protocol.MAGIC:
            raise ProtocolError(f"Payload must start with {Protocol.MAGIC} (not {payloadBytes[:magicLen]})")

        typeByte = payloadBytes[magicLen:magicLen+1]

        if rawBytes:
            return payloadBytes[magicLen+1:]

        if typeByte == Protocol.TEXT or typeByte == Protocol.SERVER:
            return Protocol.decodeTextPayload(payloadBytes[magicLen+1:])

        if typeByte == Protocol.IMAGE:
            return Protocol.decodeImagePayload(payloadBytes[magicLen+1:])

        raise ProtocolError(f"Unrecognized payload type {typeByte}")

    @staticmethod
    def decodeTextPayload(payloadBytes: bytes) -> str:
        """
        Decodes bytes as a text payload
        Args:
            payloadBytes: the encoded payload bytes

        Returns:
            the decoded text message
        """

        length = int.from_bytes(payloadBytes[:2], "big")
        textBytes = []
        for i in range(length):
            pos = 2 + i * Protocol.BYTE_SIZE
            charBytes = payloadBytes[pos:pos + Protocol.BYTE_SIZE].lstrip(b"\0")
            textBytes += charBytes

        return bytes(textBytes).decode("utf-8")

    @staticmethod
    def decodeImagePayload(payloadBytes: bytes) -> Image.Image:
        """
        Decodes bytes as an image payload
        Args:
            payloadBytes: the encoded payload bytes

        Returns:
            the decoded image
        """

        width = payloadBytes[0]
        height = payloadBytes[1]

        img = []

        for y in range(height):
            line = []
            for x in range(width):
                pos = x + y * width
                rgb = payloadBytes[pos * 3:pos * 3 + 3]
                line.append(rgb)

            img.append(line)

        return Image.fromarray(img, "RGB")

    @staticmethod
    def groupBytesIntoInt(payloadBytes: bytes) -> list[int]:
        """
        Groups padded bytes into ints according to the byte size
        Args:
            payloadBytes: the payload bytes

        Returns:
            the array of ints
        """

        ints = []
        for i in range(0, len(payloadBytes), Protocol.BYTE_SIZE):
            value = int.from_bytes(payloadBytes[i:i + Protocol.BYTE_SIZE], "big")
            ints.append(value)

        return ints

    @staticmethod
    def intToPaddedBytes(value: int) -> bytes:
        """
        Converts an int into its padded-bytes representation
        Args:
            value: the int to convert
        Returns:
            the bytes representation
        """
        return value.to_bytes(Protocol.BYTE_SIZE, "big")

    @staticmethod
    def bytesToInt(value: bytes) -> int:
        """
        Converts padded bytes into an int
        Args:
            value: the bytes
        Returns:
            the int value
        """
        return int.from_bytes(value, "big")

    @staticmethod
    def charToInt(char: str) -> int:
        charBytes = char.encode("utf-8")
        return Protocol.bytesToInt(charBytes)

    @staticmethod
    def getMessageType(messageBytes: bytes) -> bytes:
        magicLen = len(Protocol.MAGIC)
        return messageBytes[magicLen:magicLen+1]
