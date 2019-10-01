from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsView

from frontend.scene import MainScene


class MainView(QGraphicsView):
    ZOOM_IN_FACTOR = 1.1
    ZOOM_OUT_FACTOR = 0.9

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window

        self.scene = None
        self._zoom = 0

        # Constants to be passed to scene
        self.point_diameter = 8
        self.point_border_width = 0.5
        self.edge_color = 'black'
        self.edge_width = 0.5

    def update_view(self):
        self.scene = MainScene(self)
        self.setScene(self.scene)
        self.scene.display()

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
        self._zoom = 0

    def settings(self, point_diameter, point_border_width, edge_color, edge_width):
        if point_diameter is not None:
            self.point_diameter = point_diameter

        if point_border_width is not None:
            self.point_border_width = point_border_width

        if edge_color is not None:
            self.edge_color = edge_color

        if edge_width is not None:
            self.edge_width = edge_width
