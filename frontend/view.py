from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QTransform, QColor
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

        self.availability = False
        self._sp_colors = [QColor(Qt.red), QColor(Qt.green)]
        self._sp_color_index = 0
        self._edge_path = None
        self._vertex_path = None
        self._zoom = 0

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

        self.setDragMode(self.drag_mode_hint())

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
        elif event.key() == Qt.Key_D:
            self.translate(-5, 0)
        elif event.key() == Qt.Key_A:
            self.translate(5, 0)
        elif event.key() == Qt.Key_W:
            self.translate(0, 5)
        elif event.key() == Qt.Key_S:
            self.translate(0, -5)
        elif event.key() == Qt.Key_M:
            self.scene.crop()
        elif event.key() == Qt.Key_N:
            self.scene.reverse_crop()
        elif event.key() == Qt.Key_B:
            self.scene.revert_to_default()
        elif event.key() == Qt.Key_L:
            self.unhighlight_path()
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
        ) and not self.main_window.MODE_RUBBER_BAND:
            return QGraphicsView.ScrollHandDrag
        else:
            return QGraphicsView.NoDrag

    def settings(self, kwargs):
        for key in kwargs.keys():
            self.SETTINGS[key] = kwargs[key]
        self.update_view()

    # SHORTEST PATH
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_edge_path(self, edge_path):
        self._edge_path = edge_path
        self._vertex_path = []

        for i in range(0, len(edge_path)):
            source_vertex_id = self.main_window.graph.es[edge_path[i]].source
            if source_vertex_id not in self._vertex_path:
                self._vertex_path.append(source_vertex_id)

            target_vertex_id = self.main_window.graph.es[edge_path[i]].target
            if target_vertex_id not in self._vertex_path:
                self._vertex_path.append(target_vertex_id)

    def real_time_highlight(self):
        if self._sp_color_index == 0:
            self._sp_color_index = 1
        else:
            self._sp_color_index = 0

        for edge_id in self._edge_path:
            line = self.scene.lines[edge_id]
            pen = line.pen()
            pen.setColor(self._sp_colors[self._sp_color_index])
            line.setPen(pen)

        for vertex_id in self._vertex_path:
            point = self.scene.points[vertex_id]
            point.setBrush(self._sp_colors[self._sp_color_index])

    def unhighlight_path(self):
        self.scene.unhighlight_edges(self._edge_path)
        self.scene.unhighlight_vertices(self._vertex_path)
    # ------------------------------------------------------------------------------------------------------------------

    # ADD NODE
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def add_node(self, vertex):
        self.scene.add_node(vertex)
    # ------------------------------------------------------------------------------------------------------------------

    # ADD LINK
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def add_link(self, edge):
        self.scene.add_link(edge)
    # ------------------------------------------------------------------------------------------------------------------
