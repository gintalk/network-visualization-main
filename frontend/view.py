from PyQt5.QtWidgets import QGraphicsView
from frontend.scene import MainScene


class MainView(QGraphicsView):
    def __init__(self, parent, main_window):
        super().__init__(parent)

        self.main_window = main_window
        self._zoom = 0

    def update_view(self):
        scene = MainScene(self)
        scene.display(self.main_window.graph)
        self.setScene(scene)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1
        if self._zoom != 0:
            self.scale(factor, factor)
