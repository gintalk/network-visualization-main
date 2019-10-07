from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsView

from frontend.scene import MainScene


class MainView(QGraphicsView):
    ZOOM_IN_FACTOR = 1.1
    ZOOM_IN_LIMIT = 20
    ZOOM_OUT_FACTOR = 0.9
    ZOOM_OUT_LIMIT = -4

    SETTINGS = {
        'background_color': 'light_gray',
        'point_diameter': 8,
        'point_border_width': 0.5,
        'edge_color': 'black',
        'edge_width': 1,
        'highlight_color': 'green'
    }

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.setGeometry(QRect(0, 0, self.parent().width(), self.parent().height()))

        self.scene = None
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._zoom = 0

    def update_view(self):
        self.scene = MainScene(self)
        self.main_window.bind_buttons()
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

    def keyPressEvent(self, event):
        # print(event.key())
        if event.key() == Qt.Key_PageUp:
            self.zoom_in()
        elif event.key() == Qt.Key_PageDown:
            self.zoom_out()
        elif event.key() == Qt.Key_Space:
            self.reset_view()
        elif event.key() == Qt.Key_Left:
            self.rotate_anti_clockwise()
        elif event.key() == Qt.Key_Right:
            self.rotate_clockwise()
        elif event.key() == Qt.Key_R:
            self.scene.display_edges_by_gradient()
        elif event.key() == Qt.Key_T:
            self.scene.display_edges_by_thickness()

    def zoom_in(self):
        if self._zoom <= self.ZOOM_IN_LIMIT:
            self.scale(self.ZOOM_IN_FACTOR, self.ZOOM_IN_FACTOR)
            self.setDragMode(self.drag_mode_hint())
            self._zoom += 1

    def zoom_out(self):
        if self._zoom >= self.ZOOM_OUT_LIMIT:
            self.scale(self.ZOOM_OUT_FACTOR, self.ZOOM_OUT_FACTOR)
            self.setDragMode(self.drag_mode_hint())
            self._zoom -= 1

    def rotate_clockwise(self):
        self.rotate(1)
        self.setDragMode(self.drag_mode_hint())

    def rotate_anti_clockwise(self):
        self.rotate(-1)
        self.setDragMode(self.drag_mode_hint())

    def reset_view(self):
        self.setTransform(QTransform())
        self._zoom = 0

    def drag_mode_hint(self):
        if (
                self.verticalScrollBar().value() != 0 or
                self.horizontalScrollBar().value() != 0
        ):
            return QGraphicsView.ScrollHandDrag
        else:
            return QGraphicsView.NoDrag

    def settings(self, kwargs):
        for key in kwargs.keys():
            self.SETTINGS[key] = kwargs[key]
        self.update_view()

    def highlight_path(self, edge_path):
        vertices_along_the_way = []
        for i in range(0, len(edge_path)):
            vertex_id = self.main_window.graph.es[edge_path[i]].source
            vertices_along_the_way.append(vertex_id)
        last_vertex_id = self.main_window.graph.es[edge_path[-1]].target
        vertices_along_the_way.append(last_vertex_id)

        self.scene.highlight_edges(edge_path)
        self.scene.highlight_vertices(vertices_along_the_way)
