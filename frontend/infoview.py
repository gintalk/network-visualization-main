from PyQt5.QtWidgets import QGraphicsView
from frontend.infoscene import InfoScene


class InfoView(QGraphicsView):
    def __init__(self, parent, main_window):
        super().__init__(parent)

        self.main_window = main_window

    def update_view(self):
        scene = InfoScene(self)
        scene.display(self.main_window.graph)
        self.setScene(scene)