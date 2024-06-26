import os
import sys
import threading
import time
from typing import Union

import qdarktheme
from PyQt5 import uic, QtCore
from PyQt5.QtCore import QTimer, QTextStream, QFile
from PyQt5.QtWidgets import QApplication, QListWidgetItem

from ansi import ANSI
from client.client import Client, MessageListener, NotConnectedError
from client.protocol import Protocol, ProtocolError
from config import Config
from crypto.diffie_hellman import DiffieHellman
from crypto.rsa_encryption import RSAEncryption
from crypto.shift_encryption import ShiftEncryption
from crypto.vigenere_encryption import VigenereEncryption
from logger import Logger
from res.config import Ui_Dialog
from res.main import Ui_MainWindow
from utils import getRootPath, formatException, relpath


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
        self.running = True

        qdarktheme.setup_theme(Config.THEME)
        self.win: Ui_MainWindow = uic.loadUi(os.path.join(getRootPath(), "res/main.ui"))
        self.win.setWindowTitle("CryptoChat")
        self.client: Client = client
        self.messageQueue: list[tuple[bool, bytes]] = []
        self.serverMessageQueue: list[bytes] = []
        self.displayedMessages: list[tuple[float, bool, str, str]] = []
        self.receiveTimer = QTimer()

        self.receiveThread = threading.Thread(target=self.receiveMessages)

        self.initListeners()

        self.win.show()

        self.receiveThread.daemon = True
        self.receiveThread.start()
        self.receiveTimer.start(500)

        self.exec()
        self.running = False

    def initListeners(self) -> None:
        """
        Initializes the listeners (UI, client, etc.)
        """

        self.win.chatSendBtn.clicked.connect(self.chatMessage)
        self.win.chatMsg.returnPressed.connect(self.chatMessage)
        self.win.shiftTaskBtn.clicked.connect(self.doShiftTask)
        self.win.vigenereTaskBtn.clicked.connect(self.doVigenereTask)
        self.win.rsaTaskBtn.clicked.connect(self.doRSATask)
        self.win.difhelTaskBtn.clicked.connect(self.doDifHelTask)

        self.win.actionOptions.triggered.connect(self.openOptions)
        self.win.actionQuit.triggered.connect(self.quit)
        self.win.actionClear.triggered.connect(self.clearMessages)
        self.win.actionExport.triggered.connect(self.exportMessages)

        self.client.addOnReceiveListener(ReceivedMessageListener(self))
        self.client.addOnSendListener(SentMessageListener(self))

        self.receiveTimer.timeout.connect(self.collectMessages)

    def clearMessages(self) -> None:
        self.win.messagesList.clear()
        self.displayedMessages = []

    def addMessage(self, message: str) -> None:
        """
        Adds a message to the list
        Args:
            message: the message to add
        """

        item = QListWidgetItem()
        item.setText(message)
        item.setToolTip(time.strftime("%H:%M:%S"))
        self.win.messagesList.addItem(item)
        self.win.messagesList.scrollToBottom()

    def chatMessage(self) -> None:
        """
        Sends a plaintext message to everybody
        """

        senderMsg = self.win.chatMsg.text()
        self.client.send(senderMsg)
        self.win.chatMsg.setText("")

    def receiveMessages(self) -> None:
        """
        Loop to receive messages
        """

        while self.running:
            try:
                self.client.receive(True)
            except ProtocolError as e:
                self.logger.error("Received invalid message")
                self.logger.error(formatException(e))
                input("Press Enter to continue")
            except NotConnectedError:
                self.logger.error("You have been disconnected")
                self.running = False


    def waitForMessage(self, rawBytes: bool = False) -> Union[bytes, str]:
        """
        Waits for a message to be received
        Args:
            rawBytes: if true, the payload will not be decoded and raw bytes will be returned
        Returns:
            the decoded message (either a string or bytes)
        Raises:
            ProtocolError: if the payload is malformed (missing magic bytes, invalid message type, etc.)
        """

        while True:
            if len(self.serverMessageQueue) != 0:
                break

            time.sleep(0.1)

        msg = Protocol.decode(self.serverMessageQueue.pop(0), rawBytes)
        return msg

    def collectMessages(self) -> None:
        """
        Collects messages in the queue and displays them on the GUI
        """

        for i in range(len(self.messageQueue)):
            isSent, messageBytes = self.messageQueue.pop(0)
            messageType = Protocol.getMessageType(messageBytes).decode("utf-8")
            messageText = "> " if isSent else "< "
            messageText += f"[{messageType}] "
            try:
                content = Protocol.decode(messageBytes)

            except:
                payloadBytes = Protocol.decode(messageBytes, True)
                content = "(encrypted) " + payloadBytes.hex()

            messageText += content
            self.addMessage(messageText)
            self.displayedMessages.append((time.time(), isSent, messageType, content))

    def doShiftTask(self) -> None:
        self.win.shiftDebugSuccess.setText("-")
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
        self.win.shiftDebugMessage.setText(plaintextMsg)
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
            self.win.shiftDebugSuccess.setText("Success !")
        else:
            self.logger.warn("Oops, it didn't work")
            self.win.shiftDebugSuccess.setText("Failed !")

    def doRSATask(self) -> None:
        encrypt = self.win.rsaEncryptRadio.isChecked()

        dataLength = self.win.rsaDataLen.text()

        message = f"task {RSAEncryption.NAME} {'encode' if encrypt else 'decode'} {dataLength}"
        self.client.send(message, True)

        if encrypt:
            self.win.rsaDebugSuccess.setText("-")
            self.win.rsaDebugN.setText("-")
            self.win.rsaDebugE.setText("-")
            self.win.rsaDebugD.setText("-")

            # Parse the encryption key from the server's message
            keyMsg = self.waitForMessage()
            self.logger.log(keyMsg, "server")
            key = RSAEncryption.parseTaskKey(keyMsg)
            self.win.rsaDebugN.setText(str(key[0]))
            self.win.rsaDebugE.setText(str(key[1]))
            self.logger.log(f"key = {key}", "task")

            # Get the message to encrypt
            plaintextMsg = self.waitForMessage()
            self.logger.log(plaintextMsg, "server")
            self.logger.log(f"plaintext = {plaintextMsg}", "task")

            # Encrypt the message and send the result
            transcoder = RSAEncryption(key)
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
                self.win.rsaDebugSuccess.setText("Success !")
            else:
                self.logger.warn("Oops, it didn't work")
                self.win.rsaDebugSuccess.setText("Failed !")

        else:
            taskMsg = self.waitForMessage()
            self.logger.log(taskMsg, "server")

            RSAEncryption.decryptTask(taskMsg, self.client.send, self.waitForMessage)

            successMsg = self.client.receive()
            self.logger.log(successMsg, "server")
            success = self.parseDecodeSuccess(successMsg)

            if success:
                self.logger.log("Success !", "success")
            else:
                self.logger.warn("Oops, it didn't work")

    def doVigenereTask(self) -> None:
        self.win.vigenereDebugSuccess.setText("-")
        dataLength = self.win.vigenereDataLen.text()

        message = f"task {VigenereEncryption.NAME} encode {dataLength}"
        self.client.send(message, True)

        # Parse the encryption key from the server's message
        keyMsg = self.waitForMessage()
        self.logger.log(keyMsg, "server")
        key = VigenereEncryption.parseTaskKey(keyMsg)
        self.win.vigenereDebugKey.setText(str(key))
        self.logger.log(f"key = {key}", "task")

        # Get the message to encrypt
        plaintextMsg = self.waitForMessage()
        self.win.vigenereDebugMessage.setText(plaintextMsg)
        self.logger.log(plaintextMsg, "server")
        self.logger.log(f"plaintext = {plaintextMsg}", "task")

        # Encrypt the message and send the result
        transcoder = VigenereEncryption(key)
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
            self.win.vigenereDebugSuccess.setText("Success !")
        else:
            self.logger.warn("Oops, it didn't work")
            self.win.vigenereDebugSuccess.setText("Failed !")

    def doDifHelTask(self) -> None:
        message = f"task {DiffieHellman.NAME}"
        self.client.send(message, True)

        taskMsg = self.waitForMessage()
        self.logger.log(taskMsg, "server")

        diffieHellman = DiffieHellman()
        self.logger.log(f"p = {diffieHellman.p}", "task")
        self.logger.log(f"g = {diffieHellman.g}", "task")
        self.win.difHelP.setText(str(diffieHellman.p))
        self.win.difHelG.setText(str(diffieHellman.g))
        self.win.difHelA.setText(str(diffieHellman.a))
        self.win.difHelGA.setText(str(diffieHellman.gA))

        spaceMsg = f"{diffieHellman.p},{diffieHellman.g}"
        self.client.send(spaceMsg, True)

        taskMsg = self.waitForMessage()
        self.logger.log(taskMsg, "server")
        halfBMsg = self.waitForMessage()
        halfB = int(halfBMsg)
        self.logger.log(halfBMsg, "server")
        self.logger.log(f"g^B = {halfB}", "task")
        self.win.difHelGB.setText(halfBMsg)

        secret = diffieHellman.compute_secret(halfB)
        self.logger.log(f"secret = {secret}", "task")
        self.win.difHelDebugSecret.setText(str(secret))

        halfAMsg = str(diffieHellman.gA)
        self.client.send(halfAMsg, True)

        taskMsg = self.waitForMessage()
        self.logger.log(taskMsg, "server")

        secretMsg = str(secret)
        self.client.send(secretMsg, True)

        successMsg = self.waitForMessage()
        self.logger.log(successMsg, "server")
        success = self.parseDiffieHellmanSuccess(successMsg)

        if success:
            self.logger.log("Success !", "success")
            self.win.difHelDebugSuccess.setText("Success !")
        else:
            self.logger.warn("Oops, it didn't work")
            self.win.difHelDebugSuccess.setText("Failed !")


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

    def parseDecodeSuccess(self, msg: str) -> bool:
        """
        Parses the server's reply and determines the success of the last task
        Args:
            msg: the server's reply message
        Returns:
            true if it is a success, false otherwise
        """

        if msg == "he message is correct !":
            return True

        if msg != "The message is incorrect !":
            self.logger.warn(f"Unrecognized success message: {msg}")

        return False

    def parseDiffieHellmanSuccess(self, msg: str) -> bool:
        """
        Parses the server's reply and determines the success of the last task
        Args:
            msg: the server's reply message
        Returns:
            true if it is a success, false otherwise
        """
        if msg == "The shared secret has been validated !":
            return True

        if msg != "The shared secret is not the same as the server, try again":
            self.logger.warn(f"Unrecognized success message: {msg}")

        return False

    def openOptions(self) -> None:
        dialog: Ui_Dialog = uic.loadUi(os.path.join(getRootPath(), "res/config.ui"))
        dialog.host.setText(Config.HOST)
        dialog.port.setValue(Config.PORT)
        dialog.themes.setCurrentText(Config.THEME.title())

        dialog.accepted.connect(lambda: self.saveConfig(dialog))
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.exec_()

    def saveConfig(self, dialog: Ui_Dialog) -> None:
        Config.HOST = dialog.host.text()
        Config.PORT = dialog.port.value()
        Config.THEME = dialog.themes.currentText().lower()
        Config.save()
        qdarktheme.setup_theme(Config.THEME)
        if Config.HOST != self.client.host or Config.PORT != self.client.port:
            self.client.reconnect(Config.HOST, Config.PORT)

    def exportMessages(self) -> None:
        folder = os.path.join(getRootPath(), "exports")
        path = os.path.join(folder, time.strftime("messages_%Y%m%d_%H%M%S.csv"))

        if not os.path.isdir(folder):
            os.mkdir(folder)

        with open(path, "w") as f:
            f.write('"timestamp","sent","type","message"\n')
            for ts, sent, type_, content in self.displayedMessages:
                f.write(f"{ts},{'true' if sent else 'false'},\"{type_}\",\"{content}\"\n")

            self.logger.log(f"Exported messages to {relpath(path)}", "success")


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

    with Client(Config.HOST, Config.PORT) as client:
        GUI(client)
