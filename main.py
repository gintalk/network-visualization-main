from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from igraph import Graph

from frontend.view import MainView
from backend.algorithm import get_shortest_paths


class MainWindow(QMainWindow):
    DEFAULT_GRAPH = './NREN.graphml'
    DEFAULT_LAYOUT = 'random'
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
        self.layout = self.DEFAULT_LAYOUT
        self.clustering_algorithm = self.DEFAULT_CLUSTERING_ALGORITHM

        # Set up GUI
        self.central_widget = self.findChild(QWidget, 'centralwidget')
        self.view = MainView(self.central_widget, self)

        # Pull it up
        self.set_up(graph=self.DEFAULT_GRAPH)

        # Test: getting shortest path between node 0 and node 1120. Note that the function inside returns a list within
        # a list, hence in order to get the actual edge list we need to get the element at 0, which is a list of edges
        # on the path
        self.highlight_path(get_shortest_paths(self.graph, 0, 1120)[0])

    def set_up(self, graph=None, layout=None, cluster=None):
        if graph is not None:
            self.set_graph(graph)

        if layout is not None:
            self.set_layout(layout)

        if cluster is not None:
            self.set_clustering_algorithm(cluster)

    def set_graph(self, graph_path):
        self.graph = Graph.Read_GraphML(graph_path)

        if 'x' not in self.graph.vs.attributes() or 'nan' in str(self.graph.vs['x']):
            self.set_layout('Random')
        else:
            self.view.update_view()

    def set_layout(self, layout):
        graph_layout = self.graph.layout(layout=self.LAYOUTS[layout])
        for c, v in zip(graph_layout.coords, self.graph.vs):
            v['x'] = c[0]
            v['y'] = c[1]
        self.view.update_view()

    def set_clustering_algorithm(self, clustering_algorithm):
        self.clustering_algorithm = self.CLUSTERING_ALGORITHMS[clustering_algorithm]
        self.view.update_view()

    def settings(self, **kwargs):
        self.view.settings(kwargs)

    # To see shortest path, feed it a list of edges on the path
    def highlight_path(self, edge_path):
        self.view.highlight_path(edge_path)


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exit(app.exec_())
