from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsEllipseItem


class MainVertex(QGraphicsEllipseItem):
    def __init__(self, vertex, radius, pen, brush):
        self.vertex = vertex
        self.radius = radius
        self.rect = QRectF(
            QPointF(self.vertex['pos']['x'] - self.radius/2.0, self.vertex['pos']['y'] - self.radius/2.0),
            QSizeF(self.radius, self.radius)
        )
        super().__init__(self.rect.x(), self.rect.y(), self.radius, self.radius)

        self.setPen(pen)
        self.setBrush(brush)
        self.lines = []

    def attach_line(self, line):
        self.lines.append(line)

    def x(self):
        return self.rect.x() + self.radius/2

    def y(self):
        return self.rect.y() + self.radius/2

    def mousePressEvent(self, event):
        print(self.x(), self.y())

    def mouseMoveEvent(self, event):
        cursor_pos = event.scenePos()
        adjusted_cursor_pos = QPointF(cursor_pos.x() - self.radius/2, float(cursor_pos.y() - self.radius/2))

        self.rect.moveTopLeft(adjusted_cursor_pos)
        self.rect.setTopLeft(adjusted_cursor_pos)

        self.setRect(self.rect)
        [line.mouseMoveEvent(event) for line in self.lines]

    def mouseReleaseEvent(self, event):
        pass
