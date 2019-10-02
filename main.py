from PyQt5 import uic
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from igraph import Graph

from frontend.databar import DataBar
from frontend.view import MainView


class MainWindow(QMainWindow):
    DEFAULT_GRAPH = "./NREN.graphml"
    DEFAULT_CLUSTERING_ALGORITHM = "community_fastgreedy"

    def __init__(self):
        super().__init__()

        uic.loadUi('frontend/resource/GUI.ui', self)
        self.setWindowTitle("Network Visualization")

        self.central_widget = self.findChild(QWidget, 'centralwidget')
        self.view = MainView(self.central_widget, self)
        self.view.setGeometry(QRect(0, 0, self.central_widget.width(), self.central_widget.height()))

        self.graph = None
        self.clustering_algorithm = None
        self.set_graph(self.DEFAULT_GRAPH)
        self.set_clustering_algorithm(self.DEFAULT_CLUSTERING_ALGORITHM)
        self.view.update_view()

    def set_graph(self, graph_path):
        self.graph = Graph.Read_GraphML(graph_path)

    def set_clustering_algorithm(self, clustering_algorithm):
        self.clustering_algorithm = clustering_algorithm

    #pop data bar, data in list, try g.es['label']
    #stackoverflow.com/questions/940555/pyqt-sending-parameter-to-slot-when-connecting-to-a-signal
    def popupBar(self, data):
        bar = DataBar(data)
        bar.show()


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exit(app.exec_())