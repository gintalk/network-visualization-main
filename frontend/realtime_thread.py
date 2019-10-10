from threading import Thread
from time import sleep
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPen, QColor
from sklearn.preprocessing import MinMaxScaler
import time


class RealTimeMode(QThread):
    update = pyqtSignal()

    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.fps = 20

    def run(self):
        while self.parent.realtimeState:
            time.sleep(1.0 / self.fps)
            self.update.emit()
