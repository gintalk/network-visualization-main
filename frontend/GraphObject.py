from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QPointF, QLineF
import igraph
from math import sqrt


class GraphObject(QWidget):
    VERTEX_RADIUS = 4
    EDGE_DISTANCE = 5  # Increase this variable to make the edge easier to click

    def __init__(self, gui):
        super().__init__()
        self.gui = gui

        self.g = igraph.read('frontend/resource/Default.graphml')  # Default.graphml is an empty graph

    # Read graph from file
    def read_graph(self, file_name):
        self.g = igraph.read(file_name)

    # Write graph to file
    def write_graph(self, file_name):
        igraph.write(self.g, file_name)

    # Paint event is always running
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        # Draw event rectangle
        painter.fillRect(event.rect(), QBrush(Qt.white))

        # Paint graph
        self.paint(painter)

        painter.end()

    # Paint graph
    def paint(self, painter):
        self.convert_coordinate_to_non_negative()

        if self.g.vs:
            # The position of vertex on window is a QPointF and stored in attribute "v_pos", used for clicking check
            self.g.vs['pos'] = [QPointF(v['x'] * 9 + 50, v['y'] * 9 + 150)
                                for v in self.g.vs]  # This scale number is for NREN case only

            # Paint vertex
            painter.setPen(QPen(Qt.black, 1))
            for v in self.g.vs:
                painter.drawEllipse(v['pos'].x() - self.VERTEX_RADIUS, v['pos'].y() - self.VERTEX_RADIUS,
                                    self.VERTEX_RADIUS * 2, self.VERTEX_RADIUS * 2)

        if self.g.es:
            # The position of edge on window is a QLineF of the position of the source and target vertex
            # and stored in attribute "e_pos", used for clicking check
            self.g.es["pos"] = [QLineF(self.g.vs[e.source]["pos"], self.g.vs[e.target]["pos"]) for e in self.g.es]

            # Paint edge
            painter.setPen(QPen(Qt.black, 1))
            for e in self.g.es:
                painter.drawLine(self.g.vs[e.source]['pos'].x(), self.g.vs[e.source]['pos'].y(),
                                 self.g.vs[e.target]['pos'].x(), self.g.vs[e.target]['pos'].y())

    # Convert coordinate to non-negative
    def convert_coordinate_to_non_negative(self):
        if self.g.vs:
            mx = min(self.g.vs['x'])
            my = min(self.g.vs['y'])
            self.g.vs['x'] = [x - mx for x in self.g.vs['x']]
            self.g.vs['y'] = [y - my for y in self.g.vs['y']]

    # Handle single click
    def mousePressEvent(self, event):

        # Click a vertex or an edge to display its information
        self.click_for_information(event)

    # Click a vertex or an edge to display its information
    def click_for_information(self, event):

        # Return true if the distance between the point clicked and the center of vertex
        # is smaller than or equal to the vertex radius
        def click_vertex_check(vertex):
            return (vertex.x() - event.pos().x()) ** 2 + (vertex.y() - event.pos().y()) ** 2 <= self.VERTEX_RADIUS ** 2

        # I have no idea how this function works but it works so do not touch it
        def click_edge_check(edge):
            try:
                d = abs((edge.x2() - edge.x1()) * (edge.y1() - event.pos().y()) - (edge.x1() - event.pos().x()) *
                        (edge.y2() - edge.y1())) / sqrt((edge.x2() - edge.x1()) ** 2 + (edge.y2() - edge.y1()) ** 2)
            except ZeroDivisionError:
                return False
            return d < self.EDGE_DISTANCE and min(edge.x1(), edge.x2()) < event.pos().x() < max(edge.x1(), edge.x2())

        # Click vertex or edge
        no_vertex_clicked_check = True  # This changes to False if a vertex is clicked
        # We have to check this because the vertex circle can overlap with an edge
        # and we prioritize the vertex over the edge
        for v in self.g.vs:
            if click_vertex_check(v['pos']):
                self.gui.display_vertex(v)  # Display vertex information
                no_vertex_clicked_check = False

        if (no_vertex_clicked_check == True):
            for e in self.g.es:
                if click_edge_check(e['pos']):
                    self.gui.display_edge(e)
