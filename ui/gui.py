import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication
import sys
from client.client import Client
from utils import relpath, getRootPath


class GUI(QApplication):
    """
    Class to provide a graphical interface for executing the different tasks
    """

    def __init__(self, client: Client):
        super(GUI, self).__init__([])
        self.win: QMainWindow = uic.loadUi(os.path.join(getRootPath(), "res/main.ui"))
        self.win.show()
        self.client: Client = client
        self.exec()


if __name__ == '__main__':
    GUI(None)
