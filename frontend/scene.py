from __future__ import division

import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import QPen, QColor, QBrush, QTransform
from PyQt5.QtWidgets import QGraphicsScene, QRubberBand, QGraphicsView
from igraph import VertexDendrogram, Graph

from backend.edge import create_edges
from backend.vertex import create_vertices
from frontend.edge import MainEdge
from frontend.utils import *
from frontend.vertex import MainVertex


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
        self.default_graph = None
        self.clustering_algorithm = None
        self.graph_center = None
        self.scale_factor = None
        self.scene_graph_rect = None

        self.points = []
        self.lines = []
        self.show_availability = False
        self.vertex_to_display = []
        self.edge_to_display = []

        self._move = False
        self.highlighted_item = None
        self.selected_item = None
        self.rb_selected_points = SelectedList()
        self.rb_origin = None
        self.rubber_band = None

        self.init_variables()

    def init_variables(self):
        self.graph_to_display = self.parent.main_window.graph
        self.default_graph = self.graph_to_display.copy()
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

    def display_edges(self):
        for edge in self.graph_to_display.es:
            point_a = self.points[edge.source]
            point_b = self.points[edge.target]
            line_pen = QPen(self.COLORS[edge['edge_color']])
            line_pen.setWidth(edge['edge_width'])
            line = MainEdge(edge, point_a, point_b, line_pen, self)
            self.addItem(line)
            self.lines.append(line)

    def scalling(self):
        bandwidth = []
        attribute = self.parent.main_window.attribute

        for edge in self.graph_to_display.es:
            bandwidth.append(edge[attribute])

        max_value = max(bandwidth)
        min_value = min(bandwidth)
        max_min = max_value - min_value
        for i in range(len(bandwidth)):
            bandwidth[i] = (bandwidth[i] - min_value) / max_min

        return bandwidth

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

    def change_color_all_edge(self ,the_color):
        for edge in self.graph_to_display.es:
            line = self.lines[edge.index]
            line.edge['edge_color'] = the_color
            line_pen = QPen(line.edge['edge_color'])
            line_pen.setWidthF(line.edge['edge_width'])
            line.setPen(line_pen)
            line._pen = line_pen

    # def change_color_nodes(self):
    #     for vertex in self.parent.main_window.selectedNodes2:
    #         vertex.setBrush("red")
    #         self.parent.view.update_view()

    def change_color_nodes(self, color):
        for point in self.points:
            if point.vertex in self.parent.main_window.selectedNodes2:
                point.setBrush(color)
        # self.parent.view.update()


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

    def crop(self):
        lines_to_keep = []
        for point in self.rb_selected_points:
            for line in point.lines:
                if line not in lines_to_keep and \
                        (self.rb_selected_points.contains(line.point_a) and self.rb_selected_points.contains(
                            line.point_b)):
                    lines_to_keep.append(line)

        for item in self.items():
            if item not in lines_to_keep and not self.rb_selected_points.contains(item):
                self.removeItem(item)

        self.rb_selected_points.clear()
        self.save_cropped()

    def reverse_crop(self):
        for point in self.rb_selected_points:
            if point in self.items():
                for line in point.lines:
                    if line in self.items():
                        self.removeItem(line)
                self.removeItem(point)

        self.rb_selected_points.clear()
        self.save_cropped()

    def save_cropped(self):
        graph = Graph()
        items = self.items()

        point_index = 0
        for point in self.points:
            if point in items:
                create_vertices(graph, 1)

                created_vertex = graph.vs[point_index]
                created_vertex.update_attributes(point.vertex.attributes())

                point_index += 1

        line_index = 0
        for line in self.lines:
            if line in items:
                st_tuple = [0, 0]
                for vertex in graph.vs:
                    if vertex['id'] == line.point_a.vertex['id']:
                        st_tuple[0] = vertex.index
                        break
                for vertex in graph.vs:
                    if vertex['id'] == line.point_b.vertex['id']:
                        st_tuple[1] = vertex.index
                        break
                st_tuple = [tuple(st_tuple)]
                create_edges(graph, st_tuple)

                created_edge = graph.es[line_index]
                created_edge.update_attributes(line.edge.attributes())
                line_index += 1

        self.parent.main_window.graph = graph
        self.graph_to_display = self.parent.main_window.graph

    def revert_to_default(self):
        items = self.items()

        for point in self.points:
            if point not in items:
                self.addItem(point)

        for line in self.lines:
            if line not in items:
                self.addItem(line)

        self.rb_selected_points.clear()

        self.graph_to_display = self.default_graph.copy()
        self.parent.main_window.graph = self.graph_to_display

    def remove_point(self, point):
        self.removeItem(point)
        for line in point.lines:
            self.removeItem(line)

        self.save_cropped()

    # For add vertex
    def mouseDoubleClickEvent(self, event):
        if self.parent.main_window.ADD_VERTEX_STATE:
            self.parent.main_window.graph = create_vertices(self.parent.main_window.graph, 1)

            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['x'], \
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['y'] = \
                undilate(event.scenePos().x(), event.scenePos().y(), self.graph_center, self.scale_factor)

            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['pos'] = \
                {'x': event.scenePos().x(), 'y': event.scenePos().y()}

            # Set default value for new vertex
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['geocode_country'] = ""
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['hyperedge'] = ""
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['Network'] = ""
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['GeoLocation'] = ""
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['Country'] = ""
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['NetworkDate'] = ""
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['geocode_id'] = ""
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['label'] = ""
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['Internal'] = 1.0
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['Longitude'] = 20.0
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['Latitude'] = 20.0
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['type'] = ""
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['asn'] = ""
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['availability'] = np.random.randint(2)
            self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1]['cluster'] = ""

            self.vertex_to_display.append(self.parent.main_window.graph.vs[self.parent.main_window.graph.vcount() - 1])

            point_pen = QPen(self.COLORS['black'])
            point_pen.setWidth(self.parent.SETTINGS['point_border_width'])
            d = self.parent.SETTINGS['point_diameter']
            point = MainVertex(self.vertex_to_display[-1], d, point_pen, QColor(Qt.darkMagenta), self)
            self.addItem(point)
            self.points.append(point)

            self.parent.main_window.ADD_VERTEX_STATE = False
            self.parent.main_window.button_add_vertex.setToolTip("Add Vertex")

    # For add edge
    def real_add_edge(self, vertex):
        if len(self.parent.main_window.SOURCE_TARGET) == 0:
            self.parent.main_window.SOURCE_TARGET.append(vertex)

        elif len(self.parent.main_window.SOURCE_TARGET) == 1:
            self.parent.main_window.SOURCE_TARGET.append(vertex)

            self.parent.main_window.graph = create_edges(
                self.parent.main_window.graph, [(int(self.parent.main_window.SOURCE_TARGET[0].index),
                                                 int(self.parent.main_window.SOURCE_TARGET[1].index))])

            # Set default value for new edge
            self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['edge_color'] = ""
            self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['weight'] = 1000.0
            self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['LinkType'] = ""
            self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['LinkNote'] = ""
            self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['LinkSpeedUnits'] = "G"
            self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['label'] = "1000.0 MBit/s"
            self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['LinkLabel'] = ""
            self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['edge_width'] = 1
            self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['LinkSpeedRaw'] = 1000000000.0
            self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['key'] = 0.0
            self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['zorder'] = 1.0

            # Check for attribute delay, if it exists set default value for new edge
            dictionary = self.parent.main_window.graph.es[0].attributes()
            for key, value in dictionary.items():
                if str(key) == "delay":
                    self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1]['delay'] = 50.0

            self.edge_to_display.append(self.parent.main_window.graph.es[self.parent.main_window.graph.ecount() - 1])

            point_a = self.points[self.edge_to_display[-1].source]
            point_b = self.points[self.edge_to_display[-1].target]
            line_pen = QPen(self.COLORS['black'])
            line_pen.setWidth(1)
            line = MainEdge(self.edge_to_display[-1], point_a, point_b, line_pen, self)
            self.addItem(line)
            self.lines.append(line)

            self.parent.main_window.SOURCE_TARGET = []
            self.parent.main_window.ADD_EDGE_STATE = False
            self.parent.main_window.button_add_edge.setToolTip("Add Edge")

    def mousePressEvent(self, event):
        self.rb_selected_points.clear()

        cursor_pos = event.scenePos().toPoint()
        item_under_cursor = self.itemAt(cursor_pos, QTransform())

        if item_under_cursor is not None:
            if self.highlighted_item is not None:
                self.highlighted_item.unhighlight_self()
            if self.selected_item is not None:
                self.selected_item.unhighlight_self()

            self.selected_item = item_under_cursor
            self.selected_item.mousePressEvent(event)
            self.highlighted_item = item_under_cursor
            self.highlighted_item.highlight_self()
            self._move = True
        elif self.parent.main_window.SELECTION_MODE:
            # Clicking else where resets any selection previously made
            self.selected_item = None
            if self.highlighted_item is not None:
                self.highlighted_item.unhighlight_self()
                self.highlighted_item = None

            # Initializing rubber band
            self.rb_origin = self.parent.mapFromScene(cursor_pos)
            self.rubber_band = QRubberBand(QRubberBand.Rectangle, self.parent)
            self.rubber_band.setGeometry(QRect(self.rb_origin, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        cursor_pos = event.scenePos().toPoint()

        if self.selected_item is not None and self._move:
            self.selected_item.highlight_self()
            self.selected_item.mouseMoveEvent(event)
        elif self.parent.main_window.SELECTION_MODE and self.rb_origin is not None:
            if self.rb_origin is not None:
                adjusted_cursor_pos = self.parent.mapFromScene(cursor_pos)
                self.rubber_band.setGeometry(QRect(self.rb_origin, adjusted_cursor_pos).normalized())
        elif not self.parent.main_window.SELECTION_MODE:
            item_under_cursor = self.itemAt(cursor_pos, QTransform())

            if item_under_cursor is None and self.highlighted_item is not None:
                # When mouse moves out of an item into background
                self.parent.setDragMode(self.parent.drag_mode_hint())

                if self.highlighted_item != self.selected_item:
                    self.highlighted_item.unhighlight_self()
                self.highlighted_item = item_under_cursor
            elif item_under_cursor is not None and self.highlighted_item is None:
                # Whe mouse moves from background into an item
                self.parent.setDragMode(QGraphicsView.NoDrag)

                self.highlighted_item = item_under_cursor
                self.highlighted_item.highlight_self()
            elif item_under_cursor is not None and self.highlighted_item is not None:
                # When mouse moves out of one item into another item
                if self.highlighted_item != self.selected_item:
                    self.highlighted_item.unhighlight_self()
                self.highlighted_item = item_under_cursor
                self.highlighted_item.highlight_self()

    def mouseReleaseEvent(self, event):
        if self.selected_item is not None:
            self._move = False
        elif self.parent.main_window.SELECTION_MODE and self.rb_origin is not None:
            self.rubber_band.hide()
            rect = self.rubber_band.geometry()
            rect_scene = self.parent.mapToScene(rect).boundingRect()
            selected = self.items(rect_scene)
            for item in selected:
                if isinstance(item, MainVertex):
                    self.rb_selected_points.append(item)

            self.rb_origin = None
            self.rubber_band = None


class SelectedList:
    SELECTED = None

    def __init__(self):
        self.SELECTED = []
        self.index = 0

    def __next__(self):
        if self.index < len(self.SELECTED):
            index = self.index
            self.index += 1
            return self.SELECTED[index]
        raise StopIteration()

    def __iter__(self):
        return self

    def append(self, item):
        self.SELECTED.append(item)

        if isinstance(item, MainVertex):
            item.highlight_self()

    def contains(self, item):
        return item in self.SELECTED

    def clear(self):
        for item in self.SELECTED:
            if isinstance(item, MainVertex):
                item.unhighlight_self()

        self.SELECTED.clear()
        self.index = 0
