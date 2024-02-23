from client.client import Client

if __name__ == "__main__":
    print("CryptoChat - HES-SO Valais/Wallis - 2024")
    print("Alexis KUENY & Louis HEREDERO")

    client = Client("vlbelintrocrypto.hevs.ch", 6000)
    client.connect()
    input()
    client.disconnect()