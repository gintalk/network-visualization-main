from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QFileDialog, QMessageBox, QAction
from igraph import *

from frontend.view import MainView
from backend.algorithm import get_shortest_paths
from frontend.vertexinfo import VertexInfo
from frontend.edgeinfo import EdgeInfo


class MainWindow(QMainWindow):
    DEFAULT_GRAPH = 'frontend/resource/NREN.graphml'
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
    selectedNodes = []
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

        self.info_layout = self.findChild(QGridLayout, 'infolayout')

        self.button = self.findChild(QWidget, 'pushButton')
        # self.button.clicked.connect(self.getText)
        self.button.clicked.connect(self.get_2_vertex_id)
        # Set up settings details in scene

        # Pull it up
        self.set_up(graph=self.DEFAULT_GRAPH)

        # Test: getting shortest path between node 0 and node 1120. Note that the function inside returns a list within
        # a list, hence in order to get the actual edge list we need to get the element at 0, which is a list of edges
        # on the path
        # self.highlight_path(get_shortest_paths(self.graph, 0, 1120)[0])

    def set_up(self, graph=None, layout=None, cluster=None):
        if graph is not None:
            self.set_graph(graph)

        if layout is not None:
            self.set_layout(layout)

        if cluster is not None:
            self.set_clustering_algorithm(cluster)

        # Bind action into menu button
        self.menu_action()

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

    def show_vertex_id(self, vertex):
        self.selectedNodes.append(vertex)

    def get_2_vertex_id(self):
        #selected nodes length
        snl = len(self.selectedNodes)
        print(snl)
        if snl == 0 or snl > 2:
            self.selectedNodes = []
        elif snl == 2:
            sp_edge_ids = get_shortest_paths(self.graph,self.selectedNodes[0],self.selectedNodes[1])
            self.highlight_path(sp_edge_ids[0])
            self.selectedNodes = []

    # To see shortest path, feed it a list of edges on the path
    def highlight_path(self, edge_path):
        self.view.highlight_path(edge_path)

    def save_graph(self, graph_path):
        write(self.graph, graph_path)

    # Bind action into menu button
    def menu_action(self):
        # File -> Open
        open_button = self.findChild(QAction, 'actionOpen')
        open_button.triggered.connect(self.open_file_dialog)

        # File -> Save
        save_button = self.findChild(QAction, 'actionSave')
        save_button.triggered.connect(self.save_file_dialog)

        # File -> Exit
        close_button = self.findChild(QAction, 'actionExit')
        close_button.triggered.connect(self.close)

    # File -> Open
    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "QFileDialog.getOpenFileName()", "",
            "All Files (*);;GraphML Files (*.graphml)", options=options
        )
        if file_name:
            self.set_graph(file_name)
            self.view.update_view()

    # File -> Save
    def save_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save As", "",
            "All Files (*);;GraphML Files (*.graphml)", options=options
        )
        if file_name:
            if ".graphml" not in file_name:
                file_name = file_name + ".graphml"
            self.save_graph(file_name)

    # File -> Exit and the top right 'x' button
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '', 'Are you sure want to exit the program?',
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    @staticmethod
    def clear_layout(layout):
        for i in range(layout.count()):
            layout.itemAt(i).widget().deleteLater()

    # Display vertex information
    def display_vertex(self, vertex):
        self.clear_layout(self.info_layout)
        vertex_info = VertexInfo(vertex, self)
        self.info_layout.addWidget(vertex_info)

    # Display edge information
    def display_edge(self, edge):
        self.clear_layout(self.info_layout)
        edge_info = EdgeInfo(edge, self)
        self.info_layout.addWidget(edge_info)


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exit(app.exec_())
