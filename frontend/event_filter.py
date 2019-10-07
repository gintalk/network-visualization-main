from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItem


class EventFilter(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.setVisible(False)

    def sceneEventFilter(self, item, event):
        # print(event.type())
        event_type = event.type()
        if event_type == 161:               # hover enter
            item.highlight_self()
        elif event_type == 162:             # hover leave
            item.unhighlight_self()
        elif event_type == 155:             # mouse move
            item.mouseMoveEvent(event)
        elif event_type == 186:             # mouse press
            item.mousePressEvent(event)
        # elif event_type == 187:             # mouse release
            # print('mouse release')

        return True

    def boundingRect(self):
        return QRectF()
