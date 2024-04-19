import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel

from client.client import Client, MessageListener
from client.protocol import Protocol
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
        self.client.addOnReceiveListener(SentMessageListener(self))
        self.client.addOnSendListener(SentMessageListener(self))
        self.exec()

    def addMessage(self, message: str) -> None:
        newLabel = QLabel(message)
        self.win.messagesScroller.layout().addWidget(newLabel)

    def chatMessage(self) -> None:
        senderMsg = self.win.chatMsg.text()
        self.client.send(senderMsg)

class SentMessageListener(MessageListener):
    def __init__(self,gui):
        self.gui = gui
    def onMessage(self, msgBytes: bytes) -> None:
        self.gui.addMessage("> " + Protocol.decode(msgBytes))

if __name__ == '__main__':
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)


    sys.excepthook = except_hook

    with Client("vlbelintrocrypto.hevs.ch", 6000) as client:
        GUI(client)
