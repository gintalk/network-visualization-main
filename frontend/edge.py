from PyQt5.QtWidgets import QGraphicsLineItem


class MainEdge(QGraphicsLineItem):
    def __init__(self, edge, point_a, point_b, pen, parent):
        x_a, y_a = (point_a.x(), point_a.y())
        x_b, y_b = (point_b.x(), point_b.y())
        super().__init__(x_a, y_a, x_b, y_b)

        self.parent = parent
        self.setPen(pen)

        self.edge = edge
        self.point_a = point_a
        self.point_b = point_b
        point_a.attach_line(self)
        point_b.attach_line(self)

    def mousePressEvent(self, event):
        self.parent.parent.main_window.display_edge(self.edge)

    def mouseMoveEvent(self, event):
        self.setLine(self.point_a.x(), self.point_a.y(), self.point_b.x(), self.point_b.y())

    def mouseReleaseEvent(self, event):
        pass
