from PyQt5.QtCore import *
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsScene

from frontend.utils import *
from frontend.vertex import MainVertex
from frontend.edge import MainEdge


class MainScene(QGraphicsScene):
    RADIUS = 10

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.graph_to_display = None
        self.clustering_algorithm = None
        self.graph_center = None
        self.scale_factor = None
        self.points = []
        self.lines = []

        self.init_variables()

    def init_variables(self):
        self.graph_to_display = self.parent.main_window.graph
        self.clustering_algorithm = self.parent.main_window.clustering_algorithm

        graph_rect = QRect(
            QPoint(min(self.graph_to_display.vs['x']), min(self.graph_to_display.vs['y'])),
            QPoint(max(self.graph_to_display.vs['x']), max(self.graph_to_display.vs['y']))
        )
        self.graph_center = QPoint(graph_rect.center())
        self.scale_factor = scale_factor_hint(self.parent.geometry(), graph_rect, 1.1)

    def display(self):
        def assign_color_to_cluster():
            colors = [
                (255, 255, 255), (255, 0, 0), (255, 128, 0), (255, 255, 0),     # white, red, orange, yellow
                (128, 255, 0), (160, 160, 160), (0, 255, 255), (0, 128, 255),   # green, gray, light blue, medium blue
                (0, 0, 255), (128, 0, 255), (255, 0, 255), (255, 0, 128),       # blue, purple, pink, burgundy
                (0, 0, 0)                                                       # black
            ]
            color_index = 0

            for cluster in clusters:
                rgb = colors[color_index]
                cluster.color = QBrush(QColor(rgb[0], rgb[1], rgb[2]))
                color_index += 1
                if color_index >= len(colors):
                    color_index = 0

        def assign_vertex_to_cluster():
            for v in self.graph_to_display.vs:
                for cluster in clusters:
                    if v['id'] in cluster.vs['id']:
                        v['color'] = cluster.color
                        break

        clusters = getattr(self.graph_to_display, self.clustering_algorithm)()
        clusters = clusters.as_clustering().subgraphs()
        assign_color_to_cluster()
        assign_vertex_to_cluster()

        pen = QPen(QColor(Qt.black))
        r = self.RADIUS

        for vertex in self.graph_to_display.vs:
            x, y = dilate(vertex['x'], vertex['y'], self.graph_center, self.scale_factor)
            vertex['pos'] = {'x': x, 'y': y}
            point = MainVertex(vertex, r, pen, vertex['color'], self)
            self.addItem(point)
            self.points.append(point)

        for edge in self.graph_to_display.es:
            point_a = self.points[edge.source]
            point_b = self.points[edge.target]
            line = MainEdge(edge, point_a, point_b, pen, self)
            self.addItem(line)

    def update_vertex(self, point):
        dilated_x, dilated_y = point.x(), point.y()
        original_x, original_y = undilate(dilated_x, dilated_y, self.graph_center, self.scale_factor
                                          )
        point.vertex.update_attributes(x=original_x, y=original_y, pos={'x': dilated_x, 'y': dilated_y})
