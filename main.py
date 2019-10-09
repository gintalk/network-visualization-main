import numpy as np
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QFileDialog, QMessageBox, QAction, \
    QDialog, QShortcut
from PyQt5.QtWidgets import QPushButton, QComboBox
from igraph import *

from backend.algorithm import get_shortest_paths
from frontend.databar import DataBar
from frontend.edgeinfo import EdgeInfo
from frontend.vertexinfo import VertexInfo
from frontend.view import MainView


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

    file_name = 'frontend/resource/NREN.graphml'

    selectedNodes = []

    ADD_VERTEX_STATE = False
    ADD_EDGE_STATE = False

    # For add edge
    SOURCE_TARGET = []

    # MODE FOR SHORTEST PATH
    is_shortest_path_mode = False
    is_source = True

    # For gradient and thickness
    attribute = 'LinkSpeedRaw'

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

        # Pull it up
        self.set_up(graph=self.DEFAULT_GRAPH)

        # DO NOT REMOVE THIS LINE
        self.view.update_view()

        # Bind action into menu button
        self.menu_action()

        # Icon buttons
        self.button_shortest_path = self.findChild(QWidget, 'shortest_path')
        self.button_shortest_path.setToolTip("Shortest Path")
        self.button_shortest_path.setIcon(QIcon('frontend/resource/path_32.png'))
        self.button_shortest_path.clicked.connect(self.open_input_window)

        self.button_zoom_in = self.findChild(QWidget, 'zoom_in')
        self.button_zoom_in.setToolTip("Zoom In")
        self.button_zoom_in.setIcon(QIcon('frontend/resource/zoom_in.png'))
        self.button_zoom_in.clicked.connect(self.zoom_in_button)

        self.button_zoom_out = self.findChild(QWidget, 'zoom_out')
        self.button_zoom_out.setToolTip("Zoom Out")
        self.button_zoom_out.setIcon(QIcon('frontend/resource/zoom_out.png'))
        self.button_zoom_out.clicked.connect(self.zoom_out_button)

        self.button_reset_zoom = self.findChild(QWidget, 'reset_zoom')
        self.button_reset_zoom.setToolTip("Reset Zoom")
        self.button_reset_zoom.setIcon(QIcon('frontend/resource/zoom_out.png'))
        self.button_reset_zoom.clicked.connect(self.reset_zoom_button)

        self.button_add_vertex = self.findChild(QWidget, 'addvertex')
        self.button_add_vertex.setToolTip("Add Vertex")
        self.button_add_vertex.clicked.connect(self.add_vertex)

        self.button_add_edge = self.findChild(QWidget, 'addedge')
        self.button_add_edge.setToolTip("Add Edge")
        self.button_add_edge.clicked.connect(self.add_edge)

        self.input_page = Input(self)

        self.gradient_thickness_window = GradientThicknessWindow(self)

    # Check if self.attribute is an attribute in the graph or not
    def search_attribute(self):
        dictionary = self.graph.es[0].attributes()

        for key, value in dictionary.items():
            if str(key) == self.attribute:
                return True

        return False

    def open_input_window(self):
        self.is_shortest_path_mode = True
        self.input_page.show()

        # Cancel add edge mode when finding shortest path
        self.ADD_EDGE_STATE = False
        self.button_add_edge.setToolTip("Add Edge")
        self.SOURCE_TARGET = []

    def open_gradient_thickness_window(self):
        self.gradient_thickness_window.show()

    def zoom_in_button(self):
        self.view.zoom_in()

    def zoom_out_button(self):
        self.view.zoom_out()

    def reset_zoom_button(self):
        self.view.reset_view()

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

    def show_vertex_id(self, vertex):
        if self.is_shortest_path_mode is True and self.is_source is True:
            self.input_page.source_node = vertex.index
            self.input_page.source.setText(str(vertex.index))
            self.input_page.show()
        elif self.is_shortest_path_mode is True and self.is_source is False:
            self.input_page.destination_node = vertex.index
            # print(self.input_page.destination_node)
            self.input_page.destination.setText(str(vertex.index))
            self.input_page.show()

    def highlight_path(self, edge_path):
        self.view.highlight_path(edge_path)

    def save_graph(self, graph_path):
        write(self.graph, graph_path)

    # Bind action into menu button
    def menu_action(self):
        # File -> Open
        open_button = self.findChild(QAction, 'actionOpen')
        open_button.triggered.connect(self.open_file_dialog)
        open_shortcut = QShortcut(QKeySequence(self.tr("Ctrl+O", "File|Open")), self)
        open_shortcut.activated.connect(self.open_file_dialog)

        # File -> Save
        save_button = self.findChild(QAction, 'actionSave')
        save_button.triggered.connect(self.save_file_dialog)
        save_shortcut = QShortcut(QKeySequence(self.tr("Ctrl+S", "File|Save")), self)
        save_shortcut.activated.connect(self.save_file_dialog)

        # File -> Exit
        close_button = self.findChild(QAction, 'actionExit')
        close_button.triggered.connect(self.close)

        # View -> Statistics -> Bar -> Vertex Label
        vertex_label_bar_button = self.findChild(QAction, 'actionVertex_Label')
        vertex_label_bar_button.triggered.connect(self.display_vertex_label_bar)

        # View -> Statistics -> Bar -> Vertex Country
        vertex_country_bar_button = self.findChild(QAction, 'actionVertex_Country')
        vertex_country_bar_button.triggered.connect(self.display_vertex_country_bar)

        # View -> Statistics -> Bar -> Edge Link Speed Raw
        edge_linkspeedraw_bar_button = self.findChild(QAction, 'actionEdge_Link_Speed_Raw')
        edge_linkspeedraw_bar_button.triggered.connect(self.display_edge_linkspeedraw_bar)

        # View -> Statistics -> Bar -> Edge Weight
        edge_weight_bar_button = self.findChild(QAction, 'actionEdge_Weight')
        edge_weight_bar_button.triggered.connect(self.display_edge_weight_bar)

        # View -> Statistics -> Bar -> Edge Label
        edge_label_bar_button = self.findChild(QAction, 'actionEdge_Label')
        edge_label_bar_button.triggered.connect(self.display_edge_label_bar)

        # View -> Statistics -> Bar -> Vertex Label
        edge_key_bar_button = self.findChild(QAction, 'actionEdge_Key')
        edge_key_bar_button.triggered.connect(self.display_edge_key_bar)

        # View -> Gradient and Thickness
        gradient_thickness_button = self.findChild(QAction, 'actionGradient_and_Thickness')
        gradient_thickness_button.triggered.connect(self.open_gradient_thickness_window)

        # View -> Revert View
        revert_button = self.findChild(QAction, 'actionRevert')
        revert_button.triggered.connect(self.revert_view)

    # File -> Open
    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.file_name, _ = QFileDialog.getOpenFileName(
            self, "Open", "",
            "All Files (*);;GraphML Files (*.graphml)", options=options
        )
        if self.file_name:
            self.set_graph(self.file_name)
            self.clear_layout(self.info_layout)
            self.view.update_view()
            self.gradient_thickness_window = GradientThicknessWindow(self)
            self.ADD_VERTEX_STATE = False
            self.button_add_vertex.setToolTip("Add Vertex")
            self.ADD_EDGE_STATE = False
            self.button_add_edge.setToolTip("Add Edge")
            self.SOURCE_TARGET = []

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

    # File -> Exit
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '', 'Are you sure want to exit the program?',
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # View -> Statistic -> Bar -> Vertex Label
    def display_vertex_label_bar(self):
        data = self.graph.vs['label']
        self.popup_bar(data)

    # View -> Statistic -> Bar -> Vertex Country
    def display_vertex_country_bar(self):
        data = self.graph.vs['Country']
        self.popup_bar(data)

    # View -> Statistic -> Bar -> Edge Link Speed Raw
    def display_edge_linkspeedraw_bar(self):
        data = self.graph.es['LinkSpeedRaw']
        self.popup_bar(data)

    def picking_source(self):
        self.hide()
        self.parent.is_source = True

    def picking_destination(self):
        self.hide()
        self.parent.is_source = False

    def closeWindow_cancel(self):
        self.hide()
        self.parent.is_shortest_path_mode = False

    def closeWindow_ok(self):
        # Check if Source value or Destination Value is None ?
        # If 1 of them is none ,

        self.sp_edge_ids = get_shortest_paths(self.parent.graph,self.source_node,self.destination_node)
        self.parent.highlight_path(self.sp_edge_ids[0])
        self.parent.is_shortest_path_mode = False
        self.hide()

    # View -> Statistic -> Bar ->  Edge Weight
    def display_edge_weight_bar(self):
        data = self.graph.es['weight']
        self.popup_bar(data)

    # View -> Statistic -> Bar ->  Edge Label
    def display_edge_label_bar(self):
        data = self.graph.es['label']
        self.popup_bar(data)

    # View -> Statistic -> Bar ->  Edge LinkSpeedRaw
    def display_edge_key_bar(self):
        data = self.graph.es['key']
        self.popup_bar(data)

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
    def popup_bar(self, data):
        bar = DataBar(data)
        bar.show()

    def revert_view(self):
        if self.file_name:
            self.set_graph(self.file_name)
        else:
            self.set_graph(self.DEFAULT_GRAPH)
        self.view.update_view()
        self.gradient_thickness_window = GradientThicknessWindow(self)
        self.attribute = 'LinkSpeedRaw'

    def add_vertex(self):
        if not self.ADD_VERTEX_STATE:
            self.ADD_VERTEX_STATE = True
            self.button_add_vertex.setToolTip("Cancel Add Vertex")
        else:
            self.ADD_VERTEX_STATE = False
            self.button_add_vertex.setToolTip("Add Vertex")

    def add_edge(self):
        if not self.ADD_EDGE_STATE:
            self.ADD_EDGE_STATE = True
            self.button_add_edge.setToolTip("Cancel Add Edge")
        else:
            self.ADD_EDGE_STATE = False
            self.button_add_edge.setToolTip("Add Edge")
            self.SOURCE_TARGET = []

# Input window for shortest path
class Input(QDialog):
    def __init__(self, parent=None):
        super(Input, self).__init__()
        self.parent = parent
        uic.loadUi('frontend/resource/INPUT.ui', self)
        self.setWindowTitle("Input")

        self.source_node = 0
        self.destination_node = 0

        self.button = self.findChild(QWidget, 'buttonBox')
        self.button.rejected.connect(self.closeWindow_cancel)
        self.button.accepted.connect(self.closeWindow_ok)

        self.source_button = self.findChild(QWidget, 'pushButton')
        self.source_button.clicked.connect(self.picking_source)
        self.destination_button = self.findChild(QWidget, 'pushButton_2')
        self.destination_button.clicked.connect(self.picking_destination)

        self.source = self.findChild(QWidget, 'lineEdit')
        self.source.setReadOnly(True)
        self.destination = self.findChild(QWidget, 'lineEdit_2')
        self.destination.setReadOnly(True)

    def picking_source(self):
        self.hide()
        self.parent.is_source = True

    def picking_destination(self):
        self.hide()
        self.parent.is_source = False

    def closeWindow_cancel(self):
        self.hide()
        self.parent.is_shortest_path_mode = False

    def closeWindow_ok(self):
        # Check if Source value or Destination Value is None ?
        # If 1 of them is none ,

        self.sp_edge_ids = get_shortest_paths(self.parent.graph, self.source_node, self.destination_node)
        self.parent.highlight_path(self.sp_edge_ids[0])
        # self.parent.is_shortest_path_mode = False
        self.hide()


# Window for gradient and thickness
class GradientThicknessWindow(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        uic.loadUi('frontend/resource/GRATHIC.ui', self)
        self.setWindowTitle("Gradient and Thickness")

        self.gradient_button = self.findChild(QPushButton, 'drawgradient_button')
        self.gradient_button.clicked.connect(self.parent.view.scene.display_edges_by_gradient)

        self.thickness_button = self.findChild(QPushButton, 'drawthickness_button')
        self.thickness_button.clicked.connect(self.parent.view.scene.display_edges_by_thickness)

        self.combobox_button = self.findChild(QComboBox, 'comboBox')
        self.combobox_button.activated.connect(self.selection_change)

    def selection_change(self):
        self.parent.attribute = self.combobox_button.currentText()
        if not self.parent.search_attribute():
            QMessageBox.about(self, 'Sorry', 'This attribute is not available for this graph')


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exit(app.exec_())
