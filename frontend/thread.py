from PyQt5.QtCore import QThread, pyqtSignal
import time


class MainThread(QThread):
    update = pyqtSignal()

    def __init__(self, fps, parent):
        super().__init__()

        self.parent = parent
        self.fps = fps

    def run(self):
        while True:
            self.update.emit()
            time.sleep(1.0 / self.fps)
