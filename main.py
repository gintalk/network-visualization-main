import time

import numpy as np
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QKeySequence, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QFileDialog, QMessageBox, QAction, \
    QDialog, QShortcut, QColorDialog, QGraphicsView

from PyQt5.QtWidgets import QPushButton, QComboBox
from igraph import *

from backend.algorithm import get_shortest_paths
from frontend.create_attribute_dialog import CreateAttributeDialog
from frontend.add_attribute_value_dialog import AddAttributeValueDialog
from frontend.databar import DataBar
from frontend.edgeinfo import EdgeInfo
from frontend.vertexinfo import VertexInfo
from frontend.view import MainView
from frontend.realtime_thread import RealTimeMode


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
    selectedNodes2 = []

    ADD_VERTEX_STATE = False
    ADD_EDGE_STATE = False

    # For add edge
    SOURCE_TARGET = []

    VERTEX_DISPLAYING = None
    EDGE_DISPLAYING = None

    SELECTION_MODE = False

    # MODE FOR SHORTEST PATH
    is_shortest_path_mode = False
    is_source = True

    # MODE FOR COLOR_CHANGE_NODE
    is_color_change_node = False

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
        self.realtimeState = False

        # Set up GUI
        self.central_widget = self.findChild(QWidget, 'centralwidget')
        self.view = MainView(self.central_widget, self)

        self.info_layout = self.findChild(QGridLayout, 'infolayout')

        # Pull it up
        self.set_up(graph=self.DEFAULT_GRAPH)
        self.initial_value = np.random.standard_normal(self.graph.ecount())

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
        self.button_add_vertex.setIcon(QIcon('frontend/resource/add_vertex.png'))
        self.button_add_vertex.clicked.connect(self.add_vertex)

        self.color_change_node = self.findChild(QWidget, 'color_change_node')
        self.color_change_node.setToolTip("Change color of node")
        self.color_change_node.setIcon(QIcon('frontend/resource/color-wheel2.png'))
        self.color_change_node.clicked.connect(self.set_color_node)

        self.button_create_attribute_dialog = self.findChild(QWidget, 'add_attribute')
        self.button_create_attribute_dialog.setToolTip("Add Attribute")
        self.button_create_attribute_dialog.setIcon(QIcon('frontend/resource/add_attribute.png'))
        self.button_create_attribute_dialog.clicked.connect(self.create_attribute)

        self.button_add_attribute_value = self.findChild(QWidget, 'add_attribute_value')
        self.button_add_attribute_value.setToolTip("Add value for attribute")
        self.button_add_attribute_value.setIcon(QIcon('frontend/resource/add_value.png'))
        self.button_add_attribute_value.clicked.connect(self.pop_add_value_dialog)

        self.button_add_edge = self.findChild(QWidget, 'addedge')
        self.button_add_edge.setToolTip("Add Edge")
        self.button_add_edge.setIcon(QIcon('frontend/resource/add_edge.png'))
        self.button_add_edge.clicked.connect(self.add_edge)

        self.button_delete_vertex = self.findChild(QWidget, 'deletevertex')
        self.button_delete_vertex.clicked.connect(self.delete_vertex)
        self.button_delete_vertex.hide()

        self.button_delete_edge = self.findChild(QWidget, 'deleteedge')
        self.button_delete_edge.clicked.connect(self.delete_edge)
        self.button_delete_edge.hide()

        self.button_selection_mode = self.findChild(QWidget, 'selectionmode')
        self.button_selection_mode.setToolTip('Selection Mode, click to switch to Drag Mode')
        self.button_selection_mode.setIcon(QIcon('frontend/resource/drag.png'))
        self.button_selection_mode.clicked.connect(self.toggle_selection_mode)

        self.cluster_button = self.findChild(QComboBox, 'cluster')
        self.cluster_button.activated.connect(self.cluster_button_clicked)

        self.layout_button = self.findChild(QComboBox, 'layout')
        self.layout_button.activated.connect(self.layout_button_clicked)

        self.button_realtime_mode = self.findChild(QWidget, 'realtime_mode')
        self.button_realtime_mode.setToolTip("Begin Realtime Mode")
        self.button_realtime_mode.setIcon(QIcon('frontend/resource/realtime.png'))
        self.button_realtime_mode.clicked.connect(self.set_realtime_mode)

        self.button_close_realtime_mode = self.findChild(QWidget, 'close_realtime_mode')
        self.button_close_realtime_mode.setToolTip("Stop Realtime Mode")
        self.button_close_realtime_mode.setIcon(QIcon('frontend/resource/realtimestop.png'))
        self.button_close_realtime_mode.clicked.connect(self.unset_realtime_mode)

        self.input_page = None
        self.gradient_thickness_window = None
        self.create_attribute_dialog = None
        self.add_attribute_value_dialog = None
        self.realtime_thread = None

    # Check if self.attribute is an attribute in the graph or not
    def search_attribute(self):
        dictionary = self.graph.es[0].attributes()

        for key, value in dictionary.items():
            if str(key) == self.attribute:
                return True

        return False

    def change_color_all_edges(self):
        color = QColorDialog.getColor()
        self.view.scene.change_color_all_edge(color)

    def show_vertex_id2(self, vertex):
        if self.is_color_change_node:
            self.selectedNodes2.append(vertex)

    def set_color_node(self):
        if self.is_color_change_node:
            color2 = QColorDialog.getColor()
            self.view.scene.change_color_nodes(color2)
            self.selectedNodes2.clear()
            self.is_color_change_node = False
        else:
            self.is_color_change_node = True
            QMessageBox.about(self, 'You are in color change mode', 'Please pick the nodes you want to change color')

    def open_input_window(self):
        self.is_shortest_path_mode = True
        self.input_page = Input(self)
        self.input_page.show()

        # Cancel add edge mode when finding shortest path
        self.ADD_EDGE_STATE = False
        self.button_add_edge.setToolTip("Add Edge")
        self.SOURCE_TARGET = []

    def open_gradient_thickness_window(self):
        self.gradient_thickness_window = GradientThicknessWindow(self)
        self.gradient_thickness_window.show()

        self.ADD_EDGE_STATE = False
        self.button_add_edge.setToolTip("Add Edge")
        self.SOURCE_TARGET = []

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

    def cluster_button_clicked(self):
        self.set_up(cluster=self.cluster_button.currentText())

        self.gradient_thickness_window = GradientThicknessWindow(self)
        self.ADD_EDGE_STATE = False
        self.button_add_edge.setToolTip("Add Edge")
        self.SOURCE_TARGET = []

    def layout_button_clicked(self):
        self.set_up(layout=self.layout_button.currentText())

        self.gradient_thickness_window = GradientThicknessWindow(self)
        self.ADD_EDGE_STATE = False
        self.button_add_edge.setToolTip("Add Edge")
        self.SOURCE_TARGET = []

    def settings(self, **kwargs):
        self.view.settings(kwargs)

    def show_vertex_id(self, vertex):
        if self.is_shortest_path_mode is True and self.is_source is True:
            self.input_page.source_node = vertex.index
            self.input_page.source.setText(str(vertex.index))
            self.input_page.show()
        elif self.is_shortest_path_mode is True and self.is_source is False:
            self.input_page.destination_node = vertex.index
            self.input_page.destination.setText(str(vertex.index))
            self.input_page.show()

    def highlight_path(self, edge_path):
        self.view.highlight_path(edge_path)

    def unhighlight_path(self):
        self.view.unhighlight_path()

    def save_graph(self, graph_path):
        write(self.graph, graph_path)

    # Bind action into menu button
    def menu_action(self):
        # File -> Open
        open_button = self.findChild(QAction, 'actionOpen')
        open_button.triggered.connect(self.open_file_dialog)
        open_button.setIcon(QIcon('frontend/resource/open.ico'))
        open_shortcut = QShortcut(QKeySequence(self.tr("Ctrl+O", "File|Open")), self)
        open_shortcut.activated.connect(self.open_file_dialog)

        # File -> Save
        save_button = self.findChild(QAction, 'actionSave')
        save_button.triggered.connect(self.save_file_dialog)
        save_button.setIcon(QIcon('frontend/resource/save.png'))
        save_shortcut = QShortcut(QKeySequence(self.tr("Ctrl+S", "File|Save")), self)
        save_shortcut.activated.connect(self.save_file_dialog)

        # File -> Exit
        close_button = self.findChild(QAction, 'actionExit')
        close_button.triggered.connect(self.close)
        close_button.setIcon(QIcon('frontend/resource/exit.png'))
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

        # View -> Availability
        availability_button = self.findChild(QAction, 'actionShow_Availability')
        availability_button.triggered.connect(self.set_availability)

        # View -> Gradient and Thickness
        gradient_thickness_button = self.findChild(QAction, 'actionGradient_and_Thickness')
        gradient_thickness_button.triggered.connect(self.open_gradient_thickness_window)

        # View -> Revert View
        revert_button = self.findChild(QAction, 'actionRevert')
        revert_button.triggered.connect(self.revert_view)
        revert_shortcut = QShortcut(QKeySequence(self.tr("Ctrl+Z", "View|Revert")), self)
        revert_shortcut.activated.connect(self.revert_view)

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
            self.button_delete_vertex.hide()
            self.button_delete_edge.hide()
            self.VERTEX_DISPLAYING = None
            self.EDGE_DISPLAYING = None

            self.ADD_VERTEX_STATE = False
            self.button_add_vertex.setToolTip("Add Vertex")
            self.ADD_EDGE_STATE = False
            self.button_add_edge.setToolTip("Add Edge")
            self.SOURCE_TARGET = []

            self.gradient_thickness_window = GradientThicknessWindow(self)
            self.is_color_change_node = False

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

    def set_availability(self):
        self.view.availability = not self.view.availability
        self.view.update_view()

    @staticmethod
    def clear_layout(layout):
        for i in range(layout.count()):
            layout.itemAt(i).widget().deleteLater()

    # Display vertex information
    def display_vertex(self, point):
        self.clear_layout(self.info_layout)
        vertex_info = VertexInfo(point, self)
        self.info_layout.addWidget(vertex_info)
        self.VERTEX_DISPLAYING = point
        self.button_delete_vertex.show()
        self.button_delete_edge.hide()

    # Display edge information
    def display_edge(self, line):
        self.clear_layout(self.info_layout)
        edge_info = EdgeInfo(line, self)
        self.info_layout.addWidget(edge_info)
        self.EDGE_DISPLAYING = line
        self.button_delete_edge.show()
        self.button_delete_vertex.hide()

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
        self.is_color_change_node = False
        self.clear_layout(self.info_layout)
        self.button_delete_vertex.hide()
        self.button_delete_edge.hide()
        self.VERTEX_DISPLAYING = None
        self.EDGE_DISPLAYING = None
        self.ADD_EDGE_STATE = False
        self.button_add_edge.setToolTip("Add Edge")
        self.SOURCE_TARGET = []

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
            QMessageBox.about(self, '', 'Please select 2 vertices to add edge')
        else:
            self.ADD_EDGE_STATE = False
            self.button_add_edge.setToolTip("Add Edge")
            self.SOURCE_TARGET = []

    def delete_vertex(self):
        reply = QMessageBox.question(self, '', 'Are you sure want to delete this vertex?',
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.view.scene.remove_point(self.VERTEX_DISPLAYING)
            self.clear_layout(self.info_layout)
            self.VERTEX_DISPLAYING = None
            self.button_delete_vertex.hide()

            self.ADD_EDGE_STATE = False
            self.button_add_edge.setToolTip("Add Edge")
            self.SOURCE_TARGET = []

            self.gradient_thickness_window = GradientThicknessWindow(self)

    def delete_edge(self):
        reply = QMessageBox.question(self, '', 'Are you sure want to delete this edge?',
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.view.scene.remove_line(self.EDGE_DISPLAYING)
            self.clear_layout(self.info_layout)
            self.EDGE_DISPLAYING = None
            self.button_delete_edge.hide()

            self.gradient_thickness_window = GradientThicknessWindow(self)

    def create_attribute(self):
        self.create_attribute_dialog = CreateAttributeDialog(self)
        self.create_attribute_dialog.show()

    def pop_add_value_dialog(self):
        self.add_attribute_value_dialog = AddAttributeValueDialog(self)
        self.add_attribute_value_dialog.show()

    def toggle_selection_mode(self):
        if self.SELECTION_MODE:
            self.SELECTION_MODE = False
            self.view.setDragMode(self.view.drag_mode_hint())
            self.button_selection_mode.setToolTip('Drag Mode, click to switch to Selection Mode')
        else:
            self.SELECTION_MODE = True
            self.view.setDragMode(QGraphicsView.NoDrag)
            self.button_selection_mode.setToolTip('Selection Mode, click to switch to Drag Mode')

    def set_realtime_mode(self):
        self.realtimeState = True
        self.realtime_thread = RealTimeMode(20, self)
        self.realtime_thread.update.connect(self.doRealTime)
        self.realtime_thread.start()

        self.button_realtime_mode.hide()
        self.button_close_realtime_mode.show()

    def unset_realtime_mode(self):
        self.realtimeState = False
        self.realtime_thread.quit()
        self.realtime_thread = None

        self.button_realtime_mode.show()
        self.button_close_realtime_mode.hide()

    def doRealTime(self):
        lines = self.view.scene.lines
        scaled_value = (np.sin(self.initial_value + time.time() * 2) + 1) / 2

        for line in lines:
            line_index = lines.index(line)
            line_pen = QPen(
                QColor(255 - scaled_value[line_index] * 255,
                       255 - scaled_value[line_index] * 255,
                       scaled_value[line_index] * 255)
            )
            line_pen.setWidthF(line.edge['edge_width'])
            line.setPen(line_pen)


# Input window for shortest path
class Input(QDialog):
    def __init__(self, parent=None):
        super(Input, self).__init__()
        self.parent = parent
        uic.loadUi('frontend/resource/INPUT.ui', self)
        self.setWindowTitle("Input")

        self.source_node = None
        self.destination_node = None

        self.button = self.findChild(QWidget, 'buttonBox')
        self.button.rejected.connect(self.closeWindow_cancel)
        self.button.accepted.connect(self.closeWindow_ok)

        self.source_button = self.findChild(QWidget, 'pushButton')
        self.source_button.clicked.connect(self.picking_source)
        self.destination_button = self.findChild(QWidget, 'pushButton_2')
        self.destination_button.clicked.connect(self.picking_destination)

        self.stop_button = self.findChild(QWidget, 'stop_button')
        self.stop_button.clicked.connect(self.parent.unhighlight_path)
        self.stop_button.setToolTip("Stop highlight")
        self.stop_button.setIcon(QIcon('frontend/resource/stop.png'))

        self.source = self.findChild(QWidget, 'lineEdit')
        self.source.setReadOnly(True)
        self.destination = self.findChild(QWidget, 'lineEdit_2')
        self.destination.setReadOnly(True)

        self.sp_edge_ids = None

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
        if self.source_node == self.destination_node:
            QMessageBox.about(self, "Wrong Input", "Please choose 2 different nodes.")
        elif self.source_node is None or self.destination_node is None:
            QMessageBox.about(self, "Wrong Input", "Please choose 2 nodes to highlight the shortest path")
        elif self.source_node is not None and self.destination_node is not None:
            if self.sp_edge_ids:
                self.parent.unhighlight_path()

            self.sp_edge_ids = get_shortest_paths(self.parent.graph, self.source_node, self.destination_node)
            self.parent.highlight_path(self.sp_edge_ids[0])
            self.parent.is_shortest_path_mode = False
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
