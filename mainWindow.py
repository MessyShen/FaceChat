import sys
import time
import argparse
from videoChat import Video_Client, Video_Server
from audioChat import Audio_Client, Audio_Server
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QTextEdit, QLineEdit, QPushButton, QMessageBox, QButtonGroup, QRadioButton

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.IPLable = QLabel('IP地址')
        self.PortLable = QLabel('端口')
        self.QualityLable = QLabel('画质')

        self.IPEdit = QLineEdit()
        self.IPEdit.setInputMask('000.000.000.000;_')
        self.PortEdit = QLineEdit()
        self.PortEdit.setPlaceholderText('18818')
        self.QualityInfo = ''

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(self.IPLable, 1, 0)
        self.grid.addWidget(self.IPEdit, 1, 1, 1, 3)
        self.grid.addWidget(self.PortLable, 2, 0)
        self.grid.addWidget(self.PortEdit, 2, 1, 1, 3)

        self.grid.addWidget(self.QualityLable, 3, 0)
        self.qualBt11 = QRadioButton('高',self)
        self.qualBt12 = QRadioButton('中',self)
        self.qualBt13 = QRadioButton('低',self)
        self.QualityGroup = QButtonGroup(self)
        self.QualityGroup.addButton(self.qualBt11, 11)
        self.QualityGroup.addButton(self.qualBt12, 12)
        self.QualityGroup.addButton(self.qualBt13, 13)
        self.QualityGroup.buttonClicked.connect(self.rbclicked)
        self.grid.addWidget(self.qualBt11, 3, 1)
        self.grid.addWidget(self.qualBt12, 3, 2)
        self.grid.addWidget(self.qualBt13, 3, 3)

        self.connectButton = QPushButton('连接')
        self.connectButton.clicked.connect(self.handleButton)
        self.grid.addWidget(self.connectButton, 4, 1, 1, 2)

        self.setGeometry(300, 300, 400, 200)
        self.setLayout(self.grid)

        self.setWindowTitle('FaceChat')
        with open('style.qss') as file:
            str = file.readlines()
            str =''.join(str).strip('\n')
        self.setStyleSheet(str)

        self.show()

    def rbclicked(self):
        sender = self.sender()
        if sender == self.QualityGroup:
            if self.QualityGroup.checkedId() == 11:
                self.QualityInfo = '0'
            elif self.QualityGroup.checkedId() == 12:
                self.QualityInfo = '1'
            elif self.QualityGroup.checkedId() == 13:
                self.QualityInfo = '2'
            else:
                self.QualityInfo = ''

    def handleButton(self):
        if (self.IPEdit.text() == ''):
            QMessageBox.information(self, '警告', '请输入IP和端口')
        else:
            self.startChat()

    def startChat(self):
        ip = self.IPEdit.text()
        try:
            port = int(self.PortEdit.text())
        except:
            port = 18818
        qual = int(self.QualityInfo)
        vclient = Video_Client(ip, port, qual)
        vserver = Video_Server(port)
        aclient = Audio_Client(ip, port+1)
        aserver = Audio_Server(port+1)
        vclient.start()
        aclient.start()
        time.sleep(1)
        vserver.start()
        aserver.start()
        while True:
            time.sleep(1)
            if not vserver.isRunning() or not vclient.isRunning():
                sys.exit(app.exec_())
            if not aserver.isRunning() or not aclient.isRunning():
                sys.exit(app.exec_())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
