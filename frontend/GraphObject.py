from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QRect
import igraph


class GraphObject(QWidget):
    def __init__(self):
        super().__init__()

        self.g = igraph.read('frontend/resource/Default.graphml')  # Default.graphml is an empty graph

        self.vertexToDraw = []  # List of rectangles; a rectangle represents a vertex; for recognising vertex

    # Read graph from file
    def read_graph(self, file_name):
        self.g = igraph.read(file_name)

    # Write graph to file
    def write_graph(self, file_name):
        igraph.write(self.g, file_name)

    # Draw Graph
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        # Draw event rectangle
        painter.fillRect(event.rect(), QBrush(Qt.white))

        if self.g.vs:
            # Convert negative coordinates to non-negative
            mx = min(self.g.vs['x'])
            my = min(self.g.vs['y'])
            self.g.vs['x'] = [x - mx for x in self.g.vs['x']]
            self.g.vs['y'] = [y - my for y in self.g.vs['y']]

            # Draw Vertex
            painter.setPen(QPen(Qt.black, 1))
            for v in self.g.vs:
                x = v["x"] * 16 + 100  # 16 and 100 are just temporary numbers to scale for NREN case only
                y = v["y"] * 16 + 100
                self.vertexToDraw.append(QRect(x-5, y-5, 10, 10))
                painter.drawRect(x-5, y-5, 10, 10)

        if self.g.es:
            # Draw Edge
            painter.setPen(QPen(Qt.black, 1))
            for e in self.g.es:
                source_vertex_id = e.source
                target_vertex_id = e.target
                source_vertex = self.g.vs[source_vertex_id]
                target_vertex = self.g.vs[target_vertex_id]
                x1 = source_vertex["x"] * 16 + 100
                y1 = source_vertex["y"] * 16 + 100
                x2 = target_vertex["x"] * 16 + 100
                y2 = target_vertex["y"] * 16 + 100
                painter.drawLine(x1, y1, x2, y2)

            painter.end()

    def mousePressEvent(self, event):
        # For pressing a vertex and displaying vertex information; still working on it
        for v in self.vertexToDraw:
            if v.contains(event.pos()):
                print("got this far 1")
                x = v.center().x()
                y = v.center().y()
                for vv in self.g.vs:
                    if vv["x"] * 16 + 100 == x and vv["y"] * 16 + 100 == y:
                        print("got this far 2")  # why not running?
