from client.client import Client
from ui.cli import CLI

if __name__ == "__main__":
    print("CryptoChat - HES-SO Valais/Wallis - 2024")
    print("Alexis KUENY & Louis HEREDERO")

    with Client("vlbelintrocrypto.hevs.ch", 6000) as client:
        cli = CLI(client)
        print(client)

        cli.mainloop()
