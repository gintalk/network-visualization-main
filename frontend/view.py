from PyQt5.QtGui import QTransform
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
        old_cursor_pos = self.mapToScene(event.pos())

        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)

        if event.angleDelta().y() > 0:  # > 0: scroll up, < 0: scroll down
            self.zoom_in()
        else:
            self.zoom_out()

        new_cursor_pos = self.mapToScene(event.pos())
        delta = new_cursor_pos - old_cursor_pos
        self.translate(delta.x(), delta.y())

        if self._zoom > 0:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        else:
            self.setDragMode(QGraphicsView.NoDrag)

    def keyPressEvent(self, event):
        # print(event.key())
        if event.key() == 16777238:  # page up
            self.zoom_in()
        elif event.key() == 16777239:  # page down
            self.zoom_out()
        elif event.key() == 32:  # space bar
            self.reset_zoom()

    def zoom_in(self):
        self.scale(self.ZOOM_IN_FACTOR, self.ZOOM_IN_FACTOR)
        self._zoom += 1

    def zoom_out(self):
        self.scale(self.ZOOM_OUT_FACTOR, self.ZOOM_OUT_FACTOR)
        self._zoom -= 1

    def reset_zoom(self):
        self.setTransform(QTransform())
