from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView
from frontend.scene import MainScene


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('frontend/resource/GUI.ui', self)
        self.setWindowTitle("Network Visualization")
        # self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)

        # self.graphLayout = 'large'
        self._zoom = 0

        self.view = self.findChild(QGraphicsView, 'graphicsView')
        self.scene = MainScene(self.view)
        self.view.setScene(self.scene)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1
        if self._zoom != 0:
            self.view.scale(factor, factor)
        else:
            self._zoom = 0


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exit(app.exec_())
