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
        self._highlighted = False
        self._persistent = False
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
        self.parent.parent.main_window.display_vertex(self)
        self.parent.parent.main_window.get_shortest_path_nodes(self.vertex)
        self.parent.parent.main_window.get_recolor_nodes(self)

        if self.parent.parent.main_window.MODE_ADD_LINK:
            self.parent.real_add_edge(self.vertex)

    def mouseMoveEvent(self, event):
        cursor_pos = event.scenePos()
        adjusted_cursor_pos = QPointF(cursor_pos.x() - self.diameter / 2, float(cursor_pos.y() - self.diameter / 2))

        self.rect.moveTopLeft(adjusted_cursor_pos)
        self.rect.setTopLeft(adjusted_cursor_pos)

        self.setRect(self.rect)
        self.parent.update_vertex(self)
        [line.stick() for line in self.lines]

        self.parent.parent.main_window.display_vertex(self)

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

    def update_default_pen(self):
        self._pen = self.pen()

    def update_default_brush(self):
        self._brush = self.brush()

    def setPersistent(self, boolean):
        self._persistent = boolean

    def isPersistent(self):
        return self._persistent

    def setHighlighted(self, boolean):
        self._highlighted = boolean

    def isHighlighted(self):
        return self._highlighted
