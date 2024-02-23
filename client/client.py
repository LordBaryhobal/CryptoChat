import socket

class Client:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.socket: socket.socket = None

    def connect(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.host, self.port))
        except:
            print("Une erreur est survenue lors de la connexion")
            return

    def disconnect(self) -> None:
        self.socket.close()

    def send(self, msg: str, msgType: str = "t") -> None:
        payload = b"ISC" + msgType.encode("utf-8")
        length = len(msg)
        payload += length.to_bytes(2, "big")

        msgBytes = msg.encode("utf-8")
        for b in msgBytes:
            payload += bytes([0, 0, 0, b])

        self.socket.send(payload)

    def receive(self) -> str:
        msgBytes = self.socket.recv(4096)

        if msgBytes[0:3] != b"ISC":
            print(f"Erreur de format: ne commence par ISC mais par {msgBytes[0:3]}")
            return ""

        msgType = msgBytes[3:4].decode("utf-8")

        if msgType not in ["t", "i", "s"]:
            print(f"Erreur de format: le type de message est '{msgType}'")
            return ""

        length = int.from_bytes(msgBytes[4:6], "big")

        msg = b""
        for i in range(0, length):
            offset = 9 + i * 4
            msg += msgBytes[offset:offset+1]

        return msg.decode("utf-8")