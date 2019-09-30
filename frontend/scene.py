from PyQt5.QtCore import *
from PyQt5.QtGui import QPen, QColor, QBrush, QTransform
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView
from frontend.vertex import MainVertex
from frontend.edge import MainEdge
from igraph import Graph


class MainScene(QGraphicsScene):
    DEFAULT_GRAPH = "./NREN.graphml"
    RADIUS = 10

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.g = Graph.Read_GraphML(self.DEFAULT_GRAPH)
        self.points = []
        self.lines = []
        self.draw(self.g)

    def draw(self, g):
        def dilate(_x, _y, origin, dilate_factor):
            new_x = origin.x() + dilate_factor * (_x - origin.x())
            new_y = origin.y() + dilate_factor * (_y - origin.y())
            return new_x, new_y

        def scale_factor_hint(outer_rect, inner_rect, ratio):
            return (outer_rect.width() / ratio) / inner_rect.size().width()

        graph_rect = QRect(QPoint(min(g.vs['x']), min(g.vs['y'])), QPoint(max(g.vs['x']), max(g.vs['y'])))
        graph_center = QPoint(graph_rect.center())
        scale_factor = scale_factor_hint(self.parent.geometry(), graph_rect, 1.1)

        pen = QPen(QColor(Qt.green))
        brush = QBrush(pen.color().darker(150))
        r = self.RADIUS
        for vertex in g.vs:
            x, y = dilate(vertex['x'], vertex['y'], graph_center, scale_factor)
            vertex['pos'] = {'x': x, 'y': y}
            point = MainVertex(vertex, r, pen, brush)
            self.addItem(point)
            self.points.append(point)

        pen = QPen(QColor(Qt.black))
        for edge in g.es:
            point_a = self.points[edge.source]
            point_b = self.points[edge.target]
            line = MainEdge(point_a, point_b, r, pen)
            self.addItem(line)

    # def mousePressEvent(self, event):
    #     self.parent.setDragMode(QGraphicsView.ScrollHandDrag)