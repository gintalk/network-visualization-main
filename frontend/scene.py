from __future__ import division
from PyQt5.QtCore import *
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsScene, QMessageBox
from igraph import VertexDendrogram, Graph

from frontend.utils import *
from frontend.vertex import MainVertex
from frontend.edge import MainEdge
from frontend.event_filter import EventFilter
from backend.vertex import create_vertices


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
        self.show_availability = False
        self.vertex_to_display = []
        self.edge_to_display = []

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
            edge['edge_width'] = self.parent.SETTINGS['edge_width']
            edge['edge_color'] = self.parent.SETTINGS['edge_color']

    def set_background_color(self):
        background_color = QBrush(QColor(self.COLORS[self.parent.SETTINGS['background_color']]))
        self.setBackgroundBrush(background_color)

    def display(self):
        def availability_color_to_vertex():
            for v in self.graph_to_display.vs:
                if v['availability']:
                    v['color'] = QBrush(self.COLORS['green'])
                else:
                    v['color'] = QBrush(self.COLORS['red'])

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
        if self.show_availability:
            availability_color_to_vertex()

        for vertex in self.graph_to_display.vs:
            # if vertex["attribute"] and vertex["min"] <= vertex[vertex["attribute"]] <= vertex["max"]:
            #     self.vertex_to_display.append(vertex)
            # else:
                self.vertex_to_display.append(vertex)

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
            line_pen.setWidth(edge['edge_width'])
            line = MainEdge(edge, point_a, point_b, line_pen, self)
            self.addItem(line)
            self.lines.append(line)
            line.installSceneEventFilter(self.event_filter)
    # def attribute(self):
    #     a_attribute

    def scalling(self):

        bandwidth = []
        n = 0
        attribute = self.parent.main_window.get_attribute()
        if not self.parent.main_window.search_attribute():
            attribute = 'LinkSpeedRaw'
            # if not hasattr(self.graph_to_display, attribute):
        #     QMessageBox.about(self, 'Sorry bruh', 'This attribute is not available for this graph')

        # print(attribute)
        for edge in self.graph_to_display.es:
            bandwidth.append(edge[attribute])

        max_value = max(bandwidth)
        min_value = min(bandwidth)
        max_min = max_value - min_value
        for i in range(len(bandwidth)):
            bandwidth[i] = (bandwidth[i] - min_value) / max_min
        return bandwidth

    def display_edges_by_thickness(self):
        if not self.parent.main_window.search_attribute():
            return
        bandwidth = self.scalling()
        n = 0

        # set the thickness of QPen according to the attribute value
        for edge in self.graph_to_display.es:
            line = self.lines[edge.index]
            line.edge['edge_width'] = self.parent.SETTINGS['edge_width'] * bandwidth[n] * 2
            # line_pen = QPen(self.COLORS[edge['edge_color']])
            line_pen = QPen(QColor('black'))
            line_pen.setWidthF(line.edge['edge_width'])
            line.setPen(line_pen)
            line._pen = line_pen
            n += 1


    # This is a more complete way of showing gradient in the edge
    def display_edges_by_gradient(self):
        if not self.parent.main_window.search_attribute():
            return
        bandwidth = self.scalling()
        n = 0

        # set the thickness of QPen according to the attribute value
        for edge in self.graph_to_display.es:
            line = self.lines[edge.index]
            line.edge['edge_color'] = QColor(255 - bandwidth[n] * 255, 0, bandwidth[n] * 255)
            line_pen = QPen(line.edge['edge_color'])
            line_pen.setWidthF(line.edge['edge_width'])
            line.setPen(line_pen)
            line._pen = line_pen
            n += 1


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

    def set_availability(self, availability):
        self.show_availability = True

    def unset_availability(self, availability):
        self.show_availability = False


    def mouseDoubleClickEvent(self, event):
        if self.parent.main_window.ADD_VERTEX_STATE == True:
            self.parent.main_window.graph = create_vertices(self.parent.main_window.graph, 1)

            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['x'], \
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['y'] = \
                undilate(event.scenePos().x(), event.scenePos().y(), self.graph_center, self.scale_factor)

            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['pos'] = \
                {'x': event.scenePos().x(), 'y': event.scenePos().y()}

            self.vertex_to_display.append(self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1])

            point_pen = QPen(self.COLORS['black'])
            point_pen.setWidth(self.parent.SETTINGS['point_border_width'])
            d = self.parent.SETTINGS['point_diameter']
            point = MainVertex(self.vertex_to_display[-1], d, point_pen, QColor(Qt.darkMagenta), self)
            self.addItem(point)
            self.points.append(point)
            point.installSceneEventFilter(self.event_filter)
