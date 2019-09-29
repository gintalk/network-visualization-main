from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QRect, QPointF, QLineF, QRectF
import igraph


class GraphObject(QWidget):
    def __init__(self):
        super().__init__()

        self.g = igraph.read('frontend/resource/Default.graphml')  # Default.graphml is an empty graph

        self.vertexToDraw = []  # List of rectangles; a rectangle represents a vertex; for recognising vertex
        self.zoom = None

        # self.initView()

    # Read graph from file
    def read_graph(self, file_name):
        self.g = igraph.read(file_name)

    # Write graph to file
    def write_graph(self, file_name):
        igraph.write(self.g, file_name)

    # Draw Graph
    def paintEvent(self, event):
        # self.updateView()
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

    def initView(self):
        g = self.g

        # use translation to convert negative coordinates to non-negative
        mx = min(g.vs['x'])
        my = min(g.vs['y'])
        g.vs['x'] = [x - mx for x in g.vs['x']]
        g.vs['y'] = [y - my for y in g.vs['y']]

        mx = max(g.vs['x'])
        my = max(g.vs['y'])
        self.ratio = mx / my
        size = self.sizeHint()

        # convert init coordinates to coordinates on window
        g.vs['x'] = [x / mx * size.width() for x in g.vs['x']]
        g.vs['y'] = [y / my * size.height() for y in g.vs['y']]

        # Init
        self.backgroundDragging = self.pointDragging = None
        self.selectedLines = self.selectedPoints = []
        self.center = QPointF(size.width() / 2, size.height() / 2)
        self.zoom = 1
        self.viewRect = self.pointsToDraw = self.linesToDraw = None
        self.updateView()

    def updateView(self):
        size = self.size()
        w = size.width()
        h = size.height()
        viewRectWidth = w / self.zoom
        viewRectHeight = h / self.zoom
        viewRectX = self.center.x() - viewRectWidth / 2
        viewRectY = self.center.y() - viewRectHeight / 2
        self.viewRect = QRectF(viewRectX, viewRectY, viewRectWidth, viewRectHeight)

        viewRectLines = [
            QLineF(0, 0, w, 0),
            QLineF(w, 0, w, h),
            QLineF(w, h, 0, h),
            QLineF(0, h, 0, 0)
        ]

        def intersectWithViewRect(line):
            return any([line.intersect(vrl, QPointF()) == 1 for vrl in viewRectLines])

        screenRect = QRectF(0, 0, w, h)

        def inScreen(edge):
            return screenRect.contains(self.g.vs[edge.source]['pos']) or screenRect.contains(
                self.g.vs[edge.target]['pos'])

        self.g.vs['pos'] = [QPointF(
            (v['x'] - viewRectX) * self.zoom,
            (v['y'] - viewRectY) * self.zoom
        ) for v in self.g.vs]

        self.g.es['line'] = [QLineF(
            self.g.vs[e.source]['pos'],
            self.g.vs[e.target]['pos'],
        ) for e in self.g.es]

        self.pointsToDraw = [v for v in self.g.vs if self.viewRect.contains(v['x'], v['y'])]

        linesInScreen = {e for e in self.g.es if inScreen(e)}
        linesIntersectScreen = {e for e in self.g.es if intersectWithViewRect(e['line'])}
        self.linesToDraw = linesInScreen.union(linesIntersectScreen)

    def zoomInEvent(self):
        self.zoom *= 1.2
        self.update()

    def zoomOutEvent(self):
        self.zoom /= 1.2
        self.update()

    def zoomResetEvent(self):
        self.zoom = 1
        self.update()

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
