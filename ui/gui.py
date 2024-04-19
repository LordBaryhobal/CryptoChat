import os
import sys
import threading
import time
from typing import Union

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel

from ansi import ANSI
from client.client import Client, MessageListener
from client.protocol import Protocol
from crypto.shift_encryption import ShiftEncryption
from logger import Logger
from utils import getRootPath


class GUI(QApplication):
    """
    Class to provide a graphical interface for executing the different tasks
    """

    def __init__(self, client: Client):
        super(GUI, self).__init__([])

        self.logger = Logger("CLI", styles={
            "info": [],
            "error": [ANSI.RED, ANSI.BOLD],
            "warning": [ANSI.YELLOW, ANSI.ITALIC],
            "success": [ANSI.LGREEN, ANSI.ITALIC],
            "server": [ANSI.LMAGENTA, ANSI.ITALIC],
            "task": [ANSI.LBLUE]
        })

        self.win: QMainWindow = uic.loadUi(os.path.join(getRootPath(), "res/main.ui"))
        self.win.chatSendBtn.clicked.connect(self.chatMessage)
        self.win.shiftTaskBtn.clicked.connect(self.doShiftTask)
        self.win.show()
        self.client: Client = client
        self.client.addOnReceiveListener(ReceivedMessageListener(self))
        self.client.addOnSendListener(SentMessageListener(self))

        self.messageQueue: list[tuple[bool, bytes]] = []
        self.serverMessageQueue: list[bytes] = []

        self.receiveThread = threading.Thread(target=self.receiveMessages)
        self.receiveThread.start()

        self.receiveTimer = QTimer()
        self.receiveTimer.timeout.connect(self.collectMessages)
        self.receiveTimer.start(500)

        self.exec()

    def addMessage(self, message: str) -> None:
        newLabel = QLabel(message)
        self.win.messagesScroller.layout().addWidget(newLabel)

    def chatMessage(self) -> None:
        senderMsg = self.win.chatMsg.text()
        self.client.send(senderMsg)

    def receiveMessages(self) -> None:
        while True:
            try:
                self.client.receive(True)
            except:
                self.logger.error("Received invalid message")

    def waitForMessage(self, rawBytes: bool = False) -> Union[bytes, str]:
        while True:
            if len(self.serverMessageQueue) != 0:
                break

            time.sleep(0.1)

        msg = Protocol.decode(self.serverMessageQueue.pop(0), rawBytes)
        return msg

    def collectMessages(self) -> None:
        for i in range(len(self.messageQueue)):
            isSent, messageBytes = self.messageQueue.pop(0)
            messageType = Protocol.getMessageType(messageBytes)
            messageText = "> " if isSent else "< "
            messageText += f"[{messageType.decode('utf-8')}] "
            try:
                decodedMessage = Protocol.decode(messageBytes)
                messageText += decodedMessage

            except:
                payloadBytes = Protocol.decode(messageBytes, True)
                messageText += "(encrypted) " + payloadBytes.hex()

            self.addMessage(messageText)

    def doShiftTask(self) -> None:
        self.win.shiftSuccess.setText("-")
        dataLength = self.win.shiftDataLen.text()

        message = f"task {ShiftEncryption.NAME} encode {dataLength}"
        self.client.send(message, True)

        # Parse the encryption key from the server's message
        keyMsg = self.waitForMessage()
        self.logger.log(keyMsg, "server")
        key = ShiftEncryption.parseTaskKey(keyMsg)
        self.win.shiftDebugKey.setText(str(key))
        self.logger.log(f"key = {key}", "task")

        # Get the message to encrypt
        plaintextMsg = self.waitForMessage()
        self.win.shiftMsgLabel.setText(plaintextMsg)
        self.logger.log(plaintextMsg, "server")
        self.logger.log(f"plaintext = {plaintextMsg}", "task")

        # Encrypt the message and send the result
        transcoder = ShiftEncryption(key)
        self.logger.log(f"transcoder = {transcoder}", "task")

        encrypted = transcoder.encode(plaintextMsg)
        self.logger.log(f"encrypted bytes = {encrypted}", "task")
        self.client.send(encrypted, True)

        # Parse the answer and determine if it was a success
        successMsg = self.waitForMessage()
        self.logger.log(successMsg, "server")
        success = self.parseEncodeSuccess(successMsg)

        if success:
            self.logger.log("Success !", "success")
            self.win.shiftSuccess.setText("Success !")
        else:
            self.logger.warn("Oops, it didn't work")
            self.win.shiftSuccess.setText("Failed !")

    def parseEncodeSuccess(self, msg: str) -> bool:
        """
        Parses the server's reply and determines the success of the last task
        Args:
            msg: the server's reply message
        Returns:
            true if it is a success, false otherwise
        """

        if msg == "The encoding is correct !":
            return True

        if msg != "The encoding is invalid !":
            self.logger.warn(f"Unrecognized success message: {msg}")

        return False


class SentMessageListener(MessageListener):
    def __init__(self, gui: GUI):
        self.gui: GUI = gui

    def onMessage(self, msgBytes: bytes) -> None:
        self.gui.messageQueue.append((True, msgBytes))

class ReceivedMessageListener(MessageListener):
    def __init__(self, gui: GUI):
        self.gui: GUI = gui

    def onMessage(self, msgBytes: bytes) -> None:
        messageType = Protocol.getMessageType(msgBytes)

        if messageType == Protocol.SERVER:
            self.gui.serverMessageQueue.append(msgBytes)

        self.gui.messageQueue.append((False, msgBytes))

if __name__ == '__main__':
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)


    sys.excepthook = except_hook

    with Client("vlbelintrocrypto.hevs.ch", 6000) as client:
        GUI(client)
