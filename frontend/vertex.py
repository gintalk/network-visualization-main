from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsEllipseItem


class MainVertex(QGraphicsEllipseItem):
    def __init__(self, vertex, diameter, pen, brush, parent):
        self.vertex = vertex
        self.diameter = diameter
        self.rect = QRectF(QPointF(self.vertex['pos']['x'] - self.diameter / 2,
                                   self.vertex['pos']['y'] - self.diameter / 2), QSizeF(self.diameter, self.diameter))
        super().__init__(self.rect.x(), self.rect.y(), self.diameter, self.diameter)

        self.parent = parent

        self.setPen(pen)
        self.setBrush(brush)
        self.lines = []

        self.setAcceptHoverEvents(True)
        self._pen = self.pen()
        self._brush = self.brush()
        self._rect = self.rect

    def attach_line(self, line):
        self.lines.append(line)

    def x(self):
        return self.rect.x() + self.diameter / 2

    def y(self):
        return self.rect.y() + self.diameter / 2

    def mousePressEvent(self, event):
        self.parent.parent.main_window.display_vertex(self.vertex)
        self.parent.parent.main_window.show_vertex_id(self.vertex)

    def mouseMoveEvent(self, event):
        cursor_pos = event.scenePos()
        adjusted_cursor_pos = QPointF(cursor_pos.x() - self.diameter / 2, float(cursor_pos.y() - self.diameter / 2))

        self.rect.moveTopLeft(adjusted_cursor_pos)
        self.rect.setTopLeft(adjusted_cursor_pos)

        self.setRect(self.rect)
        self.parent.update_vertex(self)
        [line.stick() for line in self.lines]

        self.parent.parent.main_window.display_vertex(self.vertex)
    def mouseReleaseEvent(self, event):
        pass

    def highlight_self(self):
        pen = self.pen()
        pen.setColor(self.parent.COLORS['red'])
        pen.setWidth(self.parent.parent.SETTINGS['point_border_width'] * 4)
        self.setPen(pen)
        self.setBrush(self.parent.COLORS[self.parent.parent.SETTINGS['highlight_color']])

    def unhighlight_self(self):
        self.setPen(self._pen)
        self.setBrush(self._brush)
