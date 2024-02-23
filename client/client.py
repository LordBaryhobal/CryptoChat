import socket

class Client:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket: socket.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.host, self.port))
        except:
            print("Une erreur est survenue lors de la connexion")
            return

    def disconnect(self):
        self.socket.close()