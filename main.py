from PyQt5 import uic
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from igraph import Graph
from frontend.view import MainView


class MainWindow(QMainWindow):
    DEFAULT_GRAPH = "./NREN.graphml"

    def __init__(self):
        super().__init__()

        uic.loadUi('frontend/resource/GUI.ui', self)
        self.setWindowTitle("Network Visualization")

        self.central_widget = self.findChild(QWidget, 'centralwidget')
        self.view = MainView(self.central_widget, self)
        self.view.setGeometry(QRect(0, 0, self.central_widget.width(), self.central_widget.height()))

        self.graph = None
        self.set_graph(self.DEFAULT_GRAPH)

    def set_graph(self, graph_path):
        self.graph = Graph.Read_GraphML(graph_path)
        self.view.update_view()


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exit(app.exec_())