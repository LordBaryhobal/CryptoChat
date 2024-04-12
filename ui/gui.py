from client.client import Client


class GUI:
    """
    Class to provide a graphical interface for executing the different tasks
    """

    def __init__(self, client: Client):
        self.client: Client = client
