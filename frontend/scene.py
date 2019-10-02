from PyQt5.QtCore import *
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsScene
from igraph import VertexDendrogram, Graph

from frontend.utils import *
from frontend.vertex import MainVertex
from frontend.edge import MainEdge
from frontend.event_filter import EventFilter


class MainScene(QGraphicsScene):
    COLORS = {
        'black': QColor(Qt.black), 'white': QColor(Qt.white), 'red': QColor(Qt.red),
        'green': QColor(Qt.green), 'blue': QColor(Qt.blue), 'bark_red': QColor(Qt.darkRed),
        'dark_green': QColor(Qt.darkGreen), 'dark_blue': QColor(Qt.darkBlue), 'cyan': QColor(Qt.cyan),
        'magenta': QColor(Qt.magenta), 'yellow': QColor(Qt.yellow), 'gray': QColor(Qt.gray),
        'dark_cyan': QColor(Qt.darkCyan), 'dark_magenta': QColor(Qt.darkMagenta), 'dark_yellow': QColor(Qt.darkYellow),
        'dark_gray': QColor(Qt.darkGray), 'light_gray': QColor(Qt.lightGray)
    }

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # Variables
        self.graph_to_display = None
        self.clustering_algorithm = None
        self.graph_center = None
        self.scale_factor = None
        self.scene_graph_rect = None
        self.points = []
        self.lines = []

        self.event_filter = EventFilter()
        self.addItem(self.event_filter)
        self.init_variables()

    def init_variables(self):
        self.graph_to_display = self.parent.main_window.graph
        self.clustering_algorithm = self.parent.main_window.clustering_algorithm

        graph_rect = QRectF(
            QPointF(min(self.graph_to_display.vs['x']), min(self.graph_to_display.vs['y'])),
            QPointF(max(self.graph_to_display.vs['x']), max(self.graph_to_display.vs['y']))
        )
        self.graph_center = QPointF(graph_rect.center())
        self.scale_factor = scale_factor_hint(self.parent.geometry(), graph_rect, 1.05)

        self.init_edge_color_to_default()
        self.set_background_color()

    def init_edge_color_to_default(self, ):
        for edge in self.graph_to_display.es:
            edge['edge_color'] = self.parent.SETTINGS['edge_color']

    def set_background_color(self):
        background_color = QBrush(QColor(self.COLORS[self.parent.SETTINGS['background_color']]))
        self.setBackgroundBrush(background_color)

    def display(self):
        def assign_color_to_vertex():
            colors = list(self.COLORS.keys())

            for v in self.graph_to_display.vs:
                color_index = v['cluster'] % len(colors)
                if colors[color_index] == self.parent.SETTINGS['highlight_color']:  # highlighted items will stand out
                    color_index = (color_index + 1) % len(colors)
                q_color = self.COLORS[colors[color_index]]
                cluster_color = QBrush(q_color)
                v['color'] = cluster_color

        def assign_vertex_to_cluster():
            for v in self.graph_to_display.vs:
                for cluster in clusters:
                    # If elements of clusters are not lists, then clusters had been a VertexDendrogram object, which
                    # gives a "list" of igraph.Graph objects when subgraphed. The VertexClustering object, on the other
                    # hand, gives a list of lists of vertex ids when subgraphed
                    if isinstance(cluster, Graph) and v['id'] in cluster.vs['id']:
                        v['cluster'] = clusters.index(cluster)
                        break
                    elif isinstance(cluster, list) and v.index in cluster:
                        v['cluster'] = clusters.index(cluster)
                        break

        clusters = getattr(self.graph_to_display, self.clustering_algorithm)()
        # Some clustering algorithms return VertexDendrogram, some return VertexClustering, and VertexDendrogram object
        # has to be transformed into VertexClustering (as_clustering()) before it can be subgraphed
        if isinstance(clusters, VertexDendrogram):
            clusters = clusters.as_clustering()
        clusters = clusters.subgraphs()
        assign_vertex_to_cluster()
        assign_color_to_vertex()  # based on the cluster it belongs to

        self.display_vertices()
        self.display_edges()

    def display_vertices(self):
        point_pen = QPen(self.COLORS['black'])
        point_pen.setWidth(self.parent.SETTINGS['point_border_width'])
        d = self.parent.SETTINGS['point_diameter']
        for vertex in self.graph_to_display.vs:
            x, y = dilate(vertex['x'], vertex['y'], self.graph_center, self.scale_factor)
            vertex['pos'] = {'x': x, 'y': y}
            point = MainVertex(vertex, d, point_pen, vertex['color'], self)
            self.addItem(point)
            self.points.append(point)
            point.installSceneEventFilter(self.event_filter)

    def display_edges(self):
        for edge in self.graph_to_display.es:
            point_a = self.points[edge.source]
            point_b = self.points[edge.target]
            line_pen = QPen(self.COLORS[edge['edge_color']])
            line_pen.setWidth(self.parent.SETTINGS['edge_width'])
            line = MainEdge(edge, point_a, point_b, line_pen, self)
            self.addItem(line)
            self.lines.append(line)
            line.installSceneEventFilter(self.event_filter)

    def highlight_edges(self, edge_path):
        for edge_id in edge_path:
            line = self.lines[edge_id]
            line.highlight_self()

    def highlight_vertices(self, vertex_path):
        for vertex_id in vertex_path:
            point = self.points[vertex_id]
            point.highlight_self()

    def update_vertex(self, point):
        dilated_x, dilated_y = point.x(), point.y()
        original_x, original_y = undilate(dilated_x, dilated_y, self.graph_center, self.scale_factor
                                          )
        point.vertex.update_attributes(x=original_x, y=original_y, pos={'x': dilated_x, 'y': dilated_y})
