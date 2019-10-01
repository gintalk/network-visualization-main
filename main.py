from PyQt5 import uic
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from igraph import Graph

from frontend.view import MainView


class MainWindow(QMainWindow):
    DEFAULT_GRAPH = './NREN.graphml'
    DEFAULT_LAYOUT = 'large'
    DEFAULT_CLUSTERING_ALGORITHM = 'community_fastgreedy'

    CLUSTERING_ALGORITHMS = {
        'Fastgreedy': 'community_fastgreedy', 'Infomap': 'community_infomap',
        'Label Propagation': 'community_label_propagation', 'Multilevel': 'community_multilevel',
        'Edge Betweenness': 'community_edge_betweenness', 'Walktrap': 'community_walktrap'
    }

    LAYOUTS = {
        'Circle': 'circle', 'Distributed Recursive Layout': 'drl',
        'Fruchterman Reingold': 'fr', 'Fruchterman Reingold 3D': 'fr3d',
        'Kamada Kawai': 'kk', 'Kamada Kawai 3D': 'kk3d',
        'Large Graph Layout': 'large', 'Random': 'random',
        'Random 3D': 'random3d', 'Reingold Tilford': 'rt',
        'Reingold Tilford Circular': 'rt_circular', 'Sphere': 'sphere'
    }

    def __init__(self):
        super().__init__()

        uic.loadUi('frontend/resource/GUI.ui', self)
        self.setWindowTitle("Network Visualization")

        # Set up data to work with
        self.graph = None
        self.clustering_algorithm = None

        # Set up GUI
        self.central_widget = self.findChild(QWidget, 'centralwidget')
        self.view = MainView(self.central_widget, self)
        self.view.setGeometry(QRect(0, 0, self.central_widget.width(), self.central_widget.height()))
        self.set_up(self.DEFAULT_GRAPH, None, self.DEFAULT_CLUSTERING_ALGORITHM)

        # Set up small details in scene
        self.set_details(edge_color='Red')

        self.view.update_view()

    def set_up(self, graph=None, layout=None, cluster=None):
        if graph is None:
            self.set_graph(self.DEFAULT_GRAPH)
        else:
            self.set_graph(graph)

        if layout is None:
            if 'x' not in self.graph.vs.attributes():
                self.set_layout(self.DEFAULT_LAYOUT)
        else:
            self.set_layout(layout)

        if cluster is None:
            self.clustering_algorithm = self.DEFAULT_CLUSTERING_ALGORITHM
        else:
            self.set_clustering_algorithm(cluster)

    def set_graph(self, graph_path):
        self.graph = Graph.Read_GraphML(graph_path)

    def set_layout(self, layout):
        graph_layout = self.graph.layout(layout=layout)
        for c, v in zip(graph_layout.coords, self.graph.vs):
            v['x'] = c[0]
            v['y'] = c[1]

    def set_clustering_algorithm(self, clustering_algorithm):
        self.clustering_algorithm = clustering_algorithm

    def set_details(self, point_diameter=None, point_border_width=None, edge_color=None, edge_width=None):
        self.view.set_details(point_diameter, point_border_width, edge_color, edge_width)


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exit(app.exec_())
