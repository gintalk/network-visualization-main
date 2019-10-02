from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget ,QInputDialog, QLineEdit
from igraph import Graph

from frontend.view import MainView
from backend.algorithm import get_shortest_paths


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
        self.set_up(self.DEFAULT_GRAPH, None, self.DEFAULT_CLUSTERING_ALGORITHM)

        # Set up GUI
        self.central_widget = self.findChild(QWidget, 'centralwidget')
        self.view = MainView(self.central_widget, self)

        self.button = self.findChild(QWidget, 'pushButton')
        self.button.clicked.connect(self.getText)
        # Set up settings details in scene
        # self.choose_settings()

        self.view.update_view()



        # Test: getting shortest path between node 0 and node 1120. Note that the function inside returns a list within
        # a list, hence in order to get the actual edge list we need to get the element at 0, which is a list of edges
        # on the path
        self.highlight_path(get_shortest_paths(self.graph, 0, 1120)[0])

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

    def show_vertex_id(self, vertex):
        # print(vertex)
        # print(vertex)
        print("Hahaha")

    def choose_settings(
            self, background_color=None, point_diameter=None, point_border_width=None,
            edge_color=None, edge_width=None, highlight_color=None
    ):
        self.view.settings(
            background_color, point_diameter, point_border_width,
            edge_color, edge_width, highlight_color
        )

    # To see shortest path, feed it a list of edges on the path
    def highlight_path(self, edge_path):
        self.view.highlight_path(edge_path)

    ## input id
    def getText(self):
        x, okPressed = QInputDialog.getText(self, "Get Source Node","Source:", QLineEdit.Normal, "")
        y, okPressed = QInputDialog.getText(self, "Get Destination Node","Destination:", QLineEdit.Normal, "")
        if okPressed and x != '' and y != '':
            print({x,y})




if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exit(app.exec_())
