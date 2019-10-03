from __future__ import division
from PyQt5.QtCore import *
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsScene
from igraph import VertexDendrogram, Graph

from frontend.utils import *
from frontend.vertex import MainVertex
from frontend.edge import MainEdge


class MainScene(QGraphicsScene):
    COLORS = {
        # Yellow is used as highlight color for nodes
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

        self.init_variables()

    def init_variables(self):
        self.graph_to_display = self.parent.main_window.graph

        self.clustering_algorithm = self.parent.main_window.clustering_algorithm

        graph_rect = QRect(
            QPoint(min(self.graph_to_display.vs['x']), min(self.graph_to_display.vs['y'])),
            QPoint(max(self.graph_to_display.vs['x']), max(self.graph_to_display.vs['y']))
        )
        self.graph_center = QPoint(graph_rect.center())
        self.scale_factor = scale_factor_hint(self.parent.geometry(), graph_rect, 1.05)

        self.init_edge_color_to_black()
        self.set_background_color()

    def init_edge_color_to_black(self, ):
        for edge in self.graph_to_display.es:
            edge['edge_color'] = self.parent.edge_color

    def set_background_color(self):
        background_color = QBrush(QColor(self.COLORS[self.parent.background_color]))
        self.setBackgroundBrush(background_color)

    def display(self):
        def assign_color_to_vertex():
            colors = list(self.COLORS.keys())

            for v in self.graph_to_display.vs:
                color_index = v['cluster'] % len(colors)
                if colors[color_index] == self.parent.highlight_color:  # so that node color won't match highlight color
                    color_index = (color_index+1) % len(colors)
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
        self.display_edges_by_gradient  ()

    def display_thickness(self):
        def assign_color_to_vertex():
            colors = list(self.COLORS.keys())

            for v in self.graph_to_display.vs:
                color_index = v['cluster'] % len(colors)
                if colors[color_index] == self.parent.highlight_color:  # so that node color won't match highlight color
                    color_index = (color_index+1) % len(colors)
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
        self.display_edges_thickness()


    def display_vertices(self):
        point_pen = QPen(self.COLORS['black'])
        point_pen.setWidth(self.parent.point_border_width)
        d = self.parent.point_diameter
        for vertex in self.graph_to_display.vs:
            x, y = dilate(vertex['x'], vertex['y'], self.graph_center, self.scale_factor)
            vertex['pos'] = {'x': x, 'y': y}
            point = MainVertex(vertex, d, point_pen, vertex['color'], self)
            self.addItem(point)
            self.points.append(point)

    def display_edges(self):
        for edge in self.graph_to_display.es:
            point_a = self.points[edge.source]
            point_b = self.points[edge.target]
            line_pen = QPen(self.COLORS[edge['edge_color']])
            line_pen.setWidthF(self.parent.edge_width)
            line = MainEdge(edge, point_a, point_b, line_pen, self)
            self.addItem(line)
            self.lines.append(line)

    # #This function is fixed for showing thickness
    def display_edges_thickness(self):
        #scalling graph attribute by min-max scalling
        bandwidth = []
        n = 0

        for edge in self.graph_to_display.es:
            bandwidth.append(edge["delay"])

        max_value = max(bandwidth)
        min_value = min(bandwidth)
        max_min = max_value - min_value
        for i in range(len(bandwidth)):
            bandwidth[i] = (bandwidth[i] - min_value) / max_min

        # set the thickness of QPen according to the attribute value
        for edge in self.graph_to_display.es:
            point_a = self.points[edge.source]
            point_b = self.points[edge.target]
            line_pen = QPen(self.COLORS[edge['edge_color']])
            line_pen.setWidthF(self.parent.edge_width*bandwidth[n]*5)
            n += 1
            line = MainEdge(edge, point_a, point_b, line_pen, self)
            self.addItem(line)
            self.lines.append(line)

    # #This function is for showing gradient but it can only show few shades of colors
    # def display_edges_thickness(self):
    #     #scalling graph attribute by min-max scalling
    #     bandwidth = []
    #     n = 0
    #     for edge in self.graph_to_display.es:
    #         bandwidth.append(edge["weight"])
    #
    #     max_value = max(bandwidth)
    #     min_value = min(bandwidth)
    #     max_min = max_value - min_value
    #     for i in range(len(bandwidth)):
    #         bandwidth[i] = (bandwidth[i] - min_value) / max_min
    #
    #     # set the thickness of QPen according to the attribute value
    #     for edge in self.graph_to_display.es:
    #         point_a = self.points[edge.source]
    #         point_b = self.points[edge.target]
    #         line_pen = QPen(self.COLORS[edge['edge_color']])
    #         if bandwidth[n] <0.2:
    #             line_pen = QPen(QColor('#ff0000'))
    #         if bandwidth[n] >= 0.2 and bandwidth[n] <0.4:
    #             line_pen = QPen(QColor('#924b00'))
    #         if bandwidth[n] >= 0.4 and bandwidth[n] < 0.6:
    #             line_pen = QPen(QColor('#696a00'))
    #         if bandwidth[n] >= 0.6 and bandwidth[n] < 0.8:
    #             line_pen = QPen(QColor('#4f7b00'))
    #         if bandwidth[n] >= 0.8:
    #             line_pen = QPen(QColor('#00b500'))
    #         line_pen.setWidthF(self.parent.edge_width)
    #         n += 1
    #         line = MainEdge(edge, point_a, point_b, line_pen, self)
    #         self.addItem(line)
    #         self.lines.append(line)

    #This is a more complete way of showing gradient in the edge
    def display_edges_by_gradient(self):
        #scalling graph attribute by min-max scalling
        bandwidth = []
        n = 0
        for edge in self.graph_to_display.es:
            bandwidth.append(edge["delay"])

        max_value = max(bandwidth)
        min_value = min(bandwidth)
        max_min = max_value - min_value
        for i in range(len(bandwidth)):
            bandwidth[i] = (bandwidth[i] - min_value) / max_min

        # set the thickness of QPen according to the attribute value
        for edge in self.graph_to_display.es:
            point_a = self.points[edge.source]
            point_b = self.points[edge.target]
            line_pen = QPen(QColor(255-bandwidth[n]*255, bandwidth[n]*255, 0))
            line_pen.setWidthF(self.parent.edge_width)
            n += 1
            line = MainEdge(edge, point_a, point_b, line_pen, self)
            self.addItem(line)
            self.lines.append(line)

    def highlight_edges(self, edge_path):
        for edge_id in edge_path:
            line = self.lines[edge_id]
            line_pen = QPen(self.COLORS[self.parent.highlight_color])
            line_pen.setWidth(self.parent.edge_width * 5)
            line.setPen(line_pen)

    def highlight_vertices(self, vertex_path):
        for vertex_id in vertex_path:
            point = self.points[vertex_id]
            point.setBrush(QBrush(QColor(self.COLORS[self.parent.highlight_color])))
            point.setPen(QPen(self.COLORS[self.parent.highlight_color]))

    def update_vertex(self, point):
        dilated_x, dilated_y = point.x(), point.y()
        original_x, original_y = undilate(dilated_x, dilated_y, self.graph_center, self.scale_factor
                                          )
        point.vertex.update_attributes(x=original_x, y=original_y, pos={'x': dilated_x, 'y': dilated_y})
