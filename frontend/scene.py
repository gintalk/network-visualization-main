from PyQt5.QtCore import *
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsScene

from frontend.utils import *
from frontend.vertex import MainVertex
from frontend.edge import MainEdge


class MainScene(QGraphicsScene):
    RADIUS = 10

    def __init__(self, parent):
        super().__init__(parent)

        self.graph_center = None
        self.scale_factor = 1
        self.points = []
        self.lines = []

    def display(self, g):
        graph_rect = QRect(QPoint(min(g.vs['x']), min(g.vs['y'])), QPoint(max(g.vs['x']), max(g.vs['y'])))
        self.graph_center = QPoint(graph_rect.center())
        self.scale_factor = scale_factor_hint(self.parent().geometry(), graph_rect, 1.1)

        pen = QPen(QColor(Qt.green))
        brush = QBrush(pen.color().darker(150))
        r = self.RADIUS
        for vertex in g.vs:
            x, y = dilate(vertex['x'], vertex['y'], self.graph_center, self.scale_factor)
            vertex['pos'] = {'x': x, 'y': y}
            point = MainVertex(vertex, r, pen, brush, self)
            self.addItem(point)
            self.points.append(point)

        pen = QPen(QColor(Qt.black))
        for edge in g.es:
            point_a = self.points[edge.source]
            point_b = self.points[edge.target]
            line = MainEdge(edge, point_a, point_b, pen, self)
            self.addItem(line)

    def update_vertex(self, point):
        dilated_x, dilated_y = point.x(), point.y()
        original_x, original_y = undilate(dilated_x, dilated_y, self.graph_center, self.scale_factor
                                          )
        point.vertex.update_attributes(x=original_x, y=original_y, pos={'x': dilated_x, 'y': dilated_y})