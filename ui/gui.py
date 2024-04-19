import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication

from client.client import Client
from utils import getRootPath


class GUI(QApplication):
    """
    Class to provide a graphical interface for executing the different tasks
    """

    def __init__(self, client: Client):
        super(GUI, self).__init__([])
        self.win: QMainWindow = uic.loadUi(os.path.join(getRootPath(), "res/main.ui"))
        self.win.chatSendBtn.clicked.connect(self.chatMessage)

        self.win.show()
        self.client: Client = client
        self.exec()

    def addMessage(self, message: str) -> None:
        raise NotImplementedError

    def chatMessage(self) -> None:
        senderMsg = self.win.chatMsg.text()
        self.client.send(senderMsg)


if __name__ == '__main__':
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)


    sys.excepthook = except_hook

    with Client("vlbelintrocrypto.hevs.ch", 6000) as client:
        GUI(client)
