from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsEllipseItem


class MainVertex(QGraphicsEllipseItem):
    def __init__(self, vertex, diameter, pen, brush):
        self.vertex = vertex
        self.diameter = diameter
        self.rect = QRectF(QPointF(self.vertex['pos']['x'], self.vertex['pos']['y']), QSizeF(self.diameter, self.diameter))
        super().__init__(self.rect.x(), self.rect.y(), diameter, diameter)

        self.setPen(pen)
        self.setBrush(brush)
        self.lines = []

    def vertex(self):
        return self.vertex

    def attach_line(self, line):
        self.lines.append(line)

    def x(self):
        return self.rect.x() + self.diameter/2

    def y(self):
        return self.rect.y() + self.diameter/2

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        cursor_pos = event.scenePos()
        adjusted_cursor_pos = QPointF(cursor_pos.x() - self.diameter/2, cursor_pos.y() - self.diameter/2)

        self.rect.moveTopLeft(adjusted_cursor_pos)
        self.rect.setTopLeft(adjusted_cursor_pos)

        self.setRect(self.rect)
        [line.mouseMoveEvent(event) for line in self.lines]

    def mouseReleaseEvent(self, event):
        pass
