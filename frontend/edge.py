from PyQt5.QtWidgets import QGraphicsLineItem


class MainEdge(QGraphicsLineItem):
    def __init__(self, point_a, point_b, pen):
        x_a, y_a = (point_a.x(), point_a.y())
        x_b, y_b = (point_b.x(), point_b.y())
        super().__init__(x_a, y_a, x_b, y_b)

        self.setPen(pen)

        self.point_a = point_a
        self.point_b = point_b
        point_a.attach_line(self)
        point_b.attach_line(self)

    def mouseMoveEvent(self, event):
        self.setLine(self.point_a.x(), self.point_a.y(), self.point_b.x(), self.point_b.y())
