from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTransform, QKeySequence
from PyQt5.QtWidgets import QGraphicsView
from frontend.scene import MainScene


class MainView(QGraphicsView):
    ZOOM_IN_FACTOR = 1.1
    ZOOM_OUT_FACTOR = 0.9

    def __init__(self, parent, main_window):
        super().__init__(parent)

        self.main_window = main_window
        self._zoom = 0

    def update_view(self):
        scene = MainScene(self)
        scene.display(self.main_window.graph)
        self.setScene(scene)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:  # > 0: scroll up, < 0: scroll down
            self.zoom_in()
        else:
            self.zoom_out()

    def keyPressEvent(self, event):
        if event.key() == 16777238:  # page up
            self.zoom_in()
        elif event.key() == 16777239:   # page down
            self.zoom_out()
        if event.key() == 32:   # space bar
            self.reset_zoom()

    def zoom_in(self):
        self.scale(self.ZOOM_IN_FACTOR, self.ZOOM_IN_FACTOR)

    def zoom_out(self):
        self.scale(self.ZOOM_OUT_FACTOR, self.ZOOM_OUT_FACTOR)

    def reset_zoom(self):
        self.setTransform(QTransform())
