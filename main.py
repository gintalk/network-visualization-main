from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QFileDialog, QMessageBox, QAction, \
    QPushButton
from igraph import *
import numpy as np

from frontend.databar import DataBar
from frontend.view import MainView
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

    ADD_VERTEX_STATE = False
    ADD_EDGE_STATE = False

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

        self.add_vertex_button = self.findChild(QPushButton, 'addvertex')
        self.add_vertex_button.clicked.connect(lambda: self.add_vertex())

        self.add_edge_button = self.findChild(QPushButton, 'addedge')
        self.add_edge_button.clicked.connect(lambda: self.add_edge())

        # Bind action into menu button
        self.menu_action()

        # Pull it up
        self.set_up(graph=self.DEFAULT_GRAPH)
        self.view.update_view()

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

        np.random.seed(0)
        self.graph.vs["availability"] = np.random.randint(2, size=len(self.graph.vs))
        self.graph.vs["attribute"] = [None] * len(self.graph.vs)
        self.graph.vs["max"] = sys.maxsize * np.ones(len(self.graph.vs))
        # self.graph.vs["min"] = (-sys.maxint - 1) * np.ones(len(self.graph.vs))

        self.view.update()

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

    def save_graph(self, graph_path):
        write(self.graph, graph_path)

    # Bind action into menu button
    def menu_action(self):
        # File -> Open
        open_button = self.findChild(QAction, 'actionOpen')
        open_button.triggered.connect(lambda: self.open_file_dialog())

        # File -> Save
        save_button = self.findChild(QAction, 'actionSave')
        save_button.triggered.connect(lambda: self.save_file_dialog())

        # File -> Exit
        close_button = self.findChild(QAction, 'actionExit')
        close_button.triggered.connect(self.close)

        # Layout -> Default
        default_button = self.findChild(QAction, 'actionDefault')
        default_button.triggered.connect(lambda: self.set_up(graph=self.DEFAULT_GRAPH))

        # Layout -> Circle
        circle_button = self.findChild(QAction, 'actionCircle')
        circle_button.triggered.connect(lambda: self.set_up(graph=self.DEFAULT_GRAPH, layout='Circle'))

        # Layout -> Distributed Recursive
        drl_button = self.findChild(QAction, 'actionDistributed_Recursive')
        drl_button.triggered.connect(lambda: self.set_up(graph=self.DEFAULT_GRAPH, layout='Distributed Recursive Layout'))

    # File -> Open
    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open", "",
            "All Files (*);;GraphML Files (*.graphml)", options=options
        )
        if file_name:
            self.set_graph(file_name)
            self.clear_layout(self.info_layout)
            self.view.update_view()

    # File -> Save
    def save_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save", "",
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

    # pop data bar, data in list, try g.es['label']
    # stackoverflow.com/questions/940555/pyqt-sending-parameter-to-slot-when-connecting-to-a-signal
    def popupBar(self, data):
        bar = DataBar(data)
        bar.show()

    def add_vertex(self):
        if self.ADD_VERTEX_STATE == False:
            self.ADD_VERTEX_STATE = True
            self.add_vertex_button.setText("Exit Add Vertex Mode")
            self.ADD_EDGE_STATE = False
            self.add_edge_button.setText("Enter Add Edge Mode")
        else:
            self.ADD_VERTEX_STATE = False
            self.add_vertex_button.setText("Enter Add Vertex Mode")

    def add_edge(self):
        if self.ADD_EDGE_STATE == False:
            self.ADD_EDGE_STATE = True
            self.add_edge_button.setText("Exit Add Edge Mode")
            self.ADD_VERTEX_STATE = False
            self.add_vertex_button.setText("Enter Add Vertex Mode")
        else:
            self.ADD_EDGE_STATE = False
            self.add_edge_button.setText("Enter Add Edge Mode")

if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exit(app.exec_())
