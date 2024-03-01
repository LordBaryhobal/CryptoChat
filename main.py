from client.client import Client

if __name__ == "__main__":
    print("CryptoChat - HES-SO Valais/Wallis - 2024")
    print("Alexis KUENY & Louis HEREDERO")

    with Client("vlbelintrocrypto.hevs.ch", 6000) as client:
        msg = input("Enter your message: ")
        client.send(msg, True)
        while True:
            try:
                msg2 = client.receive()
                print("Received: " + msg2)
            except KeyboardInterrupt:
                break
