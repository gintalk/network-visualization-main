import time

import numpy as np
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QFileDialog, QMessageBox, QAction, \
    QShortcut, QColorDialog, QGraphicsView, QPushButton, QComboBox

from igraph import Graph, write

from backend.algorithm import get_shortest_paths
from backend.edge import create_edges
from backend.vertex import create_vertices
from frontend.create_attribute_dialog import CreateAttributeDialog
from frontend.assign_attribute_value_dialog import AssignAttributeValueDialog
from frontend.databar import DataBar
from frontend.edgeinfo import EdgeInfo
from frontend.gradient_and_thickness_dialog import GradientAndThicknessDialog
from frontend.selection_list import SelectionList
from frontend.utils import undilate
from frontend.vertexinfo import VertexInfo
from frontend.view import MainView
from frontend.thread import MainThread

# noinspection PyArgumentList,PyCallByClass
from frontend.shortest_path_input_dialog import ShortestPathInputDialog


# noinspection PyCallByClass
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

    # FILE = 'frontend/resource/NREN.graphml'

    # Operation modes
    MODE_ADD_NODE = False
    MODE_ADD_LINK = False
    MODE_RUBBER_BAND = False
    MODE_SHORTEST_PATH = False
    MODE_RECOLOR_NODE = False
    MODE_REAL_TIME = False

    # Currently displayed items
    VERTEX_DISPLAYING = None
    EDGE_DISPLAYING = None

    def __init__(self):
        super().__init__(parent=None, flags=Qt.WindowCloseButtonHint)

        # Load .ui file generated by Qt Designer
        uic.loadUi('frontend/resource/uis/GUI.ui', self)
        self.setWindowTitle("Network Visualization - Team Red")

        # Set up data to work with
        self.graph = None
        self.layout = self.DEFAULT_LAYOUT
        self.clustering_algorithm = self.DEFAULT_CLUSTERING_ALGORITHM

        # Set up GUI
        self.central_widget = self.findChild(QWidget, 'centralWidget')
        self.view = MainView(self.central_widget, self)
        self.info_layout = self.findChild(QGridLayout, 'infoLayout')

        # Pull it up
        self.set_up(graph=self.DEFAULT_GRAPH)

        # DO NOT REMOVE THIS LINE
        self.view.update_view()

        # Bind action into menu button_box
        self.bind_menu_actions()
        self.bind_buttons()

    # ADD ATTRIBUTE
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ADD_ATTRIBUTE_DIALOG = None
    ASSIGN_ATTRIBUTE_DIALOG = None

    def add_attribute(self):
        self.ADD_ATTRIBUTE_DIALOG = CreateAttributeDialog(self)
        self.ADD_ATTRIBUTE_DIALOG.show()

    def pop_assign_value_dialog(self):
        self.ASSIGN_ATTRIBUTE_DIALOG = AssignAttributeValueDialog(self)
        self.ASSIGN_ATTRIBUTE_DIALOG.show()

    # ------------------------------------------------------------------------------------------------------------------

    # AUXILIARY FUNCTIONS
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    GRADIENT_AND_THICKNESS_DIALOG = None
    DEFAULT_ATTRIBUTE = 'LinkSpeedRaw'

    def change_color_all_links(self):
        color = QColorDialog.getColor()
        self.view.scene.change_color_all_links(color)

    @staticmethod
    def clear_layout(layout):
        for i in range(layout.count()):
            layout.itemAt(i).widget().deleteLater()

    def contains_attribute(self):
        attributes = self.graph.es[0].attributes()

        for attr in attributes:
            if attr == self.DEFAULT_ATTRIBUTE:
                return True

        return False

    def open_gradient_thickness_window(self):
        self.GRADIENT_AND_THICKNESS_DIALOG = GradientAndThicknessDialog(self)
        self.GRADIENT_AND_THICKNESS_DIALOG.show()

    def revert_view(self):
        if self.FILE:
            self.set_graph(self.FILE)
        else:
            self.set_graph(self.DEFAULT_GRAPH)
        self.view.update_view()
        self.GRADIENT_AND_THICKNESS_DIALOG = GradientAndThicknessDialog(self)
        # self.attribute = 'LinkSpeedRaw'
        self.MODE_RECOLOR_NODE = False
        self.clear_layout(self.info_layout)
        self.BUTTON_DELETE_NODE.hide()
        self.BUTTON_DELETE_LINK.hide()
        self.VERTEX_DISPLAYING = None
        self.EDGE_DISPLAYING = None

    def set_availability_mode(self):
        self.view.availability = not self.view.availability
        if self.BUTTON_AVAILABILITY.text() == "Show Availability":
            self.BUTTON_AVAILABILITY.setText("Exit Availability")
        else:
            self.BUTTON_AVAILABILITY.setText("Show Availability")
        self.view.update_view()

    # ------------------------------------------------------------------------------------------------------------------

    # BINDING BUTTONS TO THEIR RESPECTIVE FUNCTIONALITY
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    BUTTON_ADD_NODE = None
    BUTTON_ADD_LINK = None
    BUTTON_DELETE_NODE = None
    BUTTON_DELETE_LINK = None
    BUTTON_ADD_ATTRIBUTE = None
    BUTTON_ASSIGN_ATTRIBUTE_VALUE = None
    BUTTON_ZOOM_IN = None
    BUTTON_ZOOM_OUT = None
    BUTTON_RESET_ZOOM = None
    BUTTON_CHANGE_NODE_COLOR = None
    BUTTON_SHORTEST_PATH = None
    BUTTON_SELECTION_MODE = None
    BUTTON_CROP = None
    BUTTON_REVERSE_CROP = None
    BUTTON_CLUSTERING = None
    BUTTON_LAYOUT = None
    BUTTON_REAL_TIME_MODE = None

    def bind_buttons(self):
        self.BUTTON_ADD_NODE = self.findChild(QPushButton, 'addNode')
        self.BUTTON_ADD_NODE.setToolTip("Add a new node by double clicking on any empty spot on the canvas")
        self.BUTTON_ADD_NODE.setIcon(QIcon('frontend/resource/icons/iconAddNode.png'))
        self.BUTTON_ADD_NODE.clicked.connect(self.start_add_node_mode)

        self.BUTTON_ADD_LINK = self.findChild(QPushButton, 'addLink')
        self.BUTTON_ADD_LINK.setToolTip("Add a link by clicking two nodes consecutively")
        self.BUTTON_ADD_LINK.setIcon(QIcon('frontend/resource/icons/iconAddLink.png'))
        self.BUTTON_ADD_LINK.clicked.connect(self.start_add_link_mode)

        self.BUTTON_DELETE_NODE = self.findChild(QPushButton, 'deleteNode')
        self.BUTTON_DELETE_NODE.clicked.connect(self.delete_node)
        self.BUTTON_DELETE_NODE.hide()

        self.BUTTON_DELETE_LINK = self.findChild(QPushButton, 'deleteLink')
        self.BUTTON_DELETE_LINK.clicked.connect(self.delete_link)
        self.BUTTON_DELETE_LINK.hide()

        self.BUTTON_ADD_ATTRIBUTE = self.findChild(QPushButton, 'addAttribute')
        self.BUTTON_ADD_ATTRIBUTE.setToolTip("Add a new attribute to nodes or links")
        self.BUTTON_ADD_ATTRIBUTE.setIcon(QIcon('frontend/resource/icons/iconAddAttribute.png'))
        self.BUTTON_ADD_ATTRIBUTE.clicked.connect(self.add_attribute)

        self.BUTTON_ASSIGN_ATTRIBUTE_VALUE = self.findChild(QPushButton, 'assignAttributeValue')
        self.BUTTON_ASSIGN_ATTRIBUTE_VALUE.setToolTip("Assign value to an attribute")
        self.BUTTON_ASSIGN_ATTRIBUTE_VALUE.setIcon(QIcon('frontend/resource//icons/iconAssignValue.png'))
        self.BUTTON_ASSIGN_ATTRIBUTE_VALUE.clicked.connect(self.pop_assign_value_dialog)

        self.BUTTON_ZOOM_IN = self.findChild(QPushButton, 'zoomIn')
        self.BUTTON_ZOOM_IN.setToolTip("Zoom in")
        self.BUTTON_ZOOM_IN.setIcon(QIcon('frontend/resource/icons/iconZoomIn.png'))
        self.BUTTON_ZOOM_IN.clicked.connect(self.zoom_in_button)

        self.BUTTON_ZOOM_OUT = self.findChild(QPushButton, 'zoomOut')
        self.BUTTON_ZOOM_OUT.setToolTip("Zoom out")
        self.BUTTON_ZOOM_OUT.setIcon(QIcon('frontend/resource/icons/iconZoomOut.png'))
        self.BUTTON_ZOOM_OUT.clicked.connect(self.zoom_out_button)

        self.BUTTON_RESET_ZOOM = self.findChild(QPushButton, 'resetZoom')
        self.BUTTON_RESET_ZOOM.setToolTip("Reset zoom")
        self.BUTTON_RESET_ZOOM.setIcon(QIcon('frontend/resource/icons/iconResetZoom.png'))
        self.BUTTON_RESET_ZOOM.clicked.connect(self.reset_zoom_button)

        self.BUTTON_CHANGE_NODE_COLOR = self.findChild(QPushButton, 'changeNodeColor')
        self.BUTTON_CHANGE_NODE_COLOR.setToolTip("Change node(s) color")
        self.BUTTON_CHANGE_NODE_COLOR.setIcon(QIcon('frontend/resource/icons/iconRecolorNode.png'))
        self.BUTTON_CHANGE_NODE_COLOR.clicked.connect(self.start_recolor_node_mode)

        self.BUTTON_SHORTEST_PATH = self.findChild(QPushButton, 'shortestPath')
        self.BUTTON_SHORTEST_PATH.setToolTip("Find the shortest path between 2 nodes")
        self.BUTTON_SHORTEST_PATH.setIcon(QIcon('frontend/resource/icons/iconShortestPath.png'))
        self.BUTTON_SHORTEST_PATH.clicked.connect(self.start_shortest_path_mode)

        self.BUTTON_CLUSTERING = self.findChild(QComboBox, 'cluster')
        self.BUTTON_CLUSTERING.activated.connect(self.cluster_button_clicked)

        self.BUTTON_LAYOUT = self.findChild(QComboBox, 'layout')
        self.BUTTON_LAYOUT.activated.connect(self.layout_button_clicked)

        self.BUTTON_SELECTION_MODE = self.findChild(QPushButton, 'selectionMode')
        self.BUTTON_SELECTION_MODE.setToolTip('Drag Mode. Click to switch to Selection Mode')
        self.BUTTON_SELECTION_MODE.setIcon(QIcon('frontend/resource/icons/iconRubberBandMode.png'))
        self.BUTTON_SELECTION_MODE.clicked.connect(self.toggle_selection_mode)

        self.BUTTON_CROP = self.findChild(QPushButton, 'Crop')
        self.BUTTON_CROP.setToolTip('Remove all but selected nodes')
        self.BUTTON_CROP.setIcon(QIcon('frontend/resource/icons/iconCrop.png'))
        self.BUTTON_CROP.clicked.connect(self.crop)

        self.BUTTON_REVERSE_CROP = self.findChild(QPushButton, 'reverseCrop')
        self.BUTTON_REVERSE_CROP.setToolTip('Remove selected nodes')
        self.BUTTON_REVERSE_CROP.setIcon(QIcon('frontend/resource/icons/iconReverseCrop.png'))
        self.BUTTON_REVERSE_CROP.clicked.connect(self.reverse_crop)

        self.BUTTON_REAL_TIME_MODE = self.findChild(QPushButton, 'realTimeMode')
        self.BUTTON_REAL_TIME_MODE.setToolTip("Start Real Time Mode")
        self.BUTTON_REAL_TIME_MODE.setIcon(QIcon('frontend/resource/icons/iconRealTimeMode.png'))
        self.BUTTON_REAL_TIME_MODE.clicked.connect(self.start_real_time_mode)

    # ------------------------------------------------------------------------------------------------------------------

    # BINDING MENU ACTIONS TO THEIR RESPECTIVE FUNCTIONALITY
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    BUTTON_AVAILABILITY = None

    def bind_menu_actions(self):
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
        self.BUTTON_AVAILABILITY = self.findChild(QAction, 'actionShow_Availability')
        self.BUTTON_AVAILABILITY.triggered.connect(self.set_availability_mode)

        # View -> Gradient and Thickness
        gradient_thickness_button = self.findChild(QAction, 'actionGradient_and_Thickness')
        gradient_thickness_button.triggered.connect(self.open_gradient_thickness_window)

        # View -> Revert View
        revert_button = self.findChild(QAction, 'actionRevert')
        revert_button.triggered.connect(self.revert_view)
        revert_shortcut = QShortcut(QKeySequence(self.tr("Ctrl+Z", "View|Revert")), self)
        revert_shortcut.activated.connect(self.revert_view)

    # ------------------------------------------------------------------------------------------------------------------

    # CROPPING
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def crop(self):
        self.view.crop()

    def reverse_crop(self):
        self.view.reverse_crop()

    # ------------------------------------------------------------------------------------------------------------------

    # LINKS
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    LINK_ENDS = None

    def start_add_link_mode(self):
        self.MODE_ADD_LINK = True
        self.LINK_ENDS = SelectionList()

        self.BUTTON_ADD_LINK.clicked.disconnect()
        self.BUTTON_ADD_LINK.clicked.connect(self.stop_add_link_mode)
        self.BUTTON_ADD_LINK.setIcon(QIcon('frontend/resource/icons/iconStopMode.png'))

    def get_add_link_nodes(self, point):
        if self.MODE_ADD_LINK:
            self.LINK_ENDS.append(point)

            if self.LINK_ENDS.length() >= 2:
                self.add_link()

    def add_link(self):
        source_id = self.LINK_ENDS[0].vertex.index
        target_id = self.LINK_ENDS[1].vertex.index

        existed_edge = self.graph.get_eid(source_id, target_id, error=False)
        if existed_edge == -1:
            self.graph = create_edges(self.graph, [(source_id, target_id)])
            new_edge = self.graph.es[self.graph.ecount() - 1]

            attributes = self.graph.es[0].attributes()
            for attr in attributes:
                if attr == 'edge_width':
                    value = self.view.SETTINGS['edge_width']
                elif attr == 'edge_color':
                    value = self.view.SETTINGS['edge_color']
                elif attr == 'LinkSpeedRaw':
                    value = 1000000000.0
                elif attr == 'delay':
                    value = 50.0
                else:
                    value = ''

                new_edge[attr] = value

            self.view.add_link(new_edge)

        self.LINK_ENDS.clear()

    def delete_link(self):
        reply = QMessageBox.question(self, '', 'Are you sure want to delete this edge?',
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.view.scene.remove_line(self.EDGE_DISPLAYING)
            self.clear_layout(self.info_layout)
            self.EDGE_DISPLAYING = None
            self.BUTTON_DELETE_LINK.hide()

    def display_link(self, line):
        self.clear_layout(self.info_layout)
        edge_info = EdgeInfo(line, self)
        self.info_layout.addWidget(edge_info)
        self.EDGE_DISPLAYING = line
        self.BUTTON_DELETE_LINK.show()
        self.BUTTON_DELETE_NODE.hide()

    def stop_add_link_mode(self):
        self.MODE_ADD_LINK = False
        self.LINK_ENDS = None

        self.BUTTON_ADD_LINK.clicked.disconnect()
        self.BUTTON_ADD_LINK.clicked.connect(self.start_add_link_mode)
        self.BUTTON_ADD_LINK.setIcon(QIcon('frontend/resource/icons/iconAddLink.png'))

    # ------------------------------------------------------------------------------------------------------------------

    # LOAD/SAVE FILE
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    FILE = None

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.FILE, _ = QFileDialog.getOpenFileName(
            self, "Open", "",
            "All Files (*);;GraphML Files (*.graphml)", options=options
        )
        if self.FILE:
            self.set_graph(self.FILE)
            self.clear_layout(self.info_layout)
            self.view.update_view()
            self.BUTTON_DELETE_NODE.hide()
            self.BUTTON_DELETE_LINK.hide()
            self.VERTEX_DISPLAYING = None
            self.EDGE_DISPLAYING = None

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

    def save_graph(self, graph_path):
        write(self.graph, graph_path)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '', 'Are you sure want to exit the program?',
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # ------------------------------------------------------------------------------------------------------------------

    # NODES
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def start_add_node_mode(self):
        self.MODE_ADD_NODE = True

        self.BUTTON_ADD_NODE.clicked.disconnect()
        self.BUTTON_ADD_NODE.clicked.connect(self.stop_add_node_mode)
        self.BUTTON_ADD_NODE.setIcon(QIcon('frontend/resource/icons/iconStopMode.png'))

    def add_node(self, event, graph_center, scale_factor):
        self.graph = create_vertices(self.graph, 1)
        new_vertex = self.graph.vs[self.graph.vcount() - 1]

        new_vertex['pos'] = {'x': event.scenePos().x(), 'y': event.scenePos().y()}
        new_vertex['x'], new_vertex['y'] = undilate(
            new_vertex['pos']['x'], new_vertex['pos']['y'], graph_center, scale_factor
        )

        attributes = self.graph.vs[0].attributes()
        for attr in attributes:
            if attr == 'Longitude' or attr == 'x':
                value = new_vertex['x']
            elif attr == 'Latitude' or attr == 'y':
                value = new_vertex['y']
            elif attr == 'pos':
                value = new_vertex['pos']
            elif attr == 'availability':
                value = np.random.randint(2)
            elif attr == 'id':
                value = 'n' + str(new_vertex.index)
            elif attr == 'color':
                value = QColor(Qt.red)
            else:
                value = ''

            new_vertex[attr] = value

        self.view.add_node(new_vertex)

    def delete_node(self):
        reply = QMessageBox.question(self, '', 'Are you sure want to delete this vertex?',
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.view.scene.remove_point(self.VERTEX_DISPLAYING)
            self.clear_layout(self.info_layout)
            self.VERTEX_DISPLAYING = None
            self.BUTTON_DELETE_NODE.hide()

    def display_node(self, point):
        self.clear_layout(self.info_layout)
        vertex_info = VertexInfo(point, self)
        self.info_layout.addWidget(vertex_info)
        self.VERTEX_DISPLAYING = point
        self.BUTTON_DELETE_NODE.show()
        self.BUTTON_DELETE_LINK.hide()

    def stop_add_node_mode(self):
        self.MODE_ADD_NODE = False

        self.BUTTON_ADD_NODE.clicked.disconnect()
        self.BUTTON_ADD_NODE.clicked.connect(self.start_add_node_mode)
        self.BUTTON_ADD_NODE.setIcon(QIcon('frontend/resource/icons/iconAddNode.png'))

    # ------------------------------------------------------------------------------------------------------------------

    # REAL TIME
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    THREAD = None
    INITIAL_VALUE = None

    def start_real_time_mode(self):
        self.MODE_REAL_TIME = True
        self.INITIAL_VALUE = np.random.standard_normal(self.graph.ecount())

        self.THREAD = MainThread(fps=20, parent=self)
        self.THREAD.update.connect(self.morph)
        self.THREAD.start()

        self.BUTTON_REAL_TIME_MODE.clicked.disconnect()
        self.BUTTON_REAL_TIME_MODE.clicked.connect(self.stop_real_time_mode)
        self.BUTTON_REAL_TIME_MODE.setIcon(QIcon('frontend/resource/icons/iconStopMode.png'))

    def morph(self):
        lines = self.view.scene.lines
        scaled_value = (np.sin(self.INITIAL_VALUE + time.time() * 2) + 1) / 2

        for line in lines:
            line_index = lines.index(line)
            line_pen = QPen(
                QColor(255 - scaled_value[line_index] * 255,
                       255 - scaled_value[line_index] * 255,
                       scaled_value[line_index] * 255)
            )
            line_pen.setWidthF(line.edge['edge_width'])
            line.setPen(line_pen)

    def stop_real_time_mode(self):
        self.MODE_REAL_TIME = False
        self.THREAD.terminate()
        self.THREAD = None
        # self.INITIAL_VALUE = None

        self.BUTTON_REAL_TIME_MODE.clicked.disconnect()
        self.BUTTON_REAL_TIME_MODE.clicked.connect(self.start_real_time_mode)
        self.BUTTON_REAL_TIME_MODE.setIcon(QIcon('frontend/resource/icons/iconRealTimeMode.png'))

    # ------------------------------------------------------------------------------------------------------------------

    # RECOLOR NODE(S)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    RECOLOR_SELECTED = None

    def start_recolor_node_mode(self):
        self.MODE_RECOLOR_NODE = True
        self.RECOLOR_SELECTED = SelectionList()

        QMessageBox.about(self, 'You are in Node Recoloring mode', 'Pick the nodes you want to recolor')
        self.BUTTON_CHANGE_NODE_COLOR.clicked.disconnect()
        self.BUTTON_CHANGE_NODE_COLOR.clicked.connect(self.set_node_color)
        self.BUTTON_CHANGE_NODE_COLOR.setIcon(QIcon('frontend/resource/icons/iconSetNodeColor.png'))

    def get_recolor_nodes(self, node):
        if self.MODE_RECOLOR_NODE:
            if not self.RECOLOR_SELECTED.contains(node):
                self.RECOLOR_SELECTED.append(node)
            else:
                self.RECOLOR_SELECTED.remove(node)

    def set_node_color(self):
        color = QColorDialog.getColor()

        for point in self.RECOLOR_SELECTED:
            point.setBrush(color)
            point.update_default_brush()

        self.stop_recolor_node_mode()

    def stop_recolor_node_mode(self):
        self.MODE_RECOLOR_NODE = False
        self.RECOLOR_SELECTED.clear()
        self.RECOLOR_SELECTED = None

        self.BUTTON_CHANGE_NODE_COLOR.clicked.disconnect()
        self.BUTTON_CHANGE_NODE_COLOR.clicked.connect(self.start_recolor_node_mode)
        self.BUTTON_CHANGE_NODE_COLOR.setIcon(QIcon('frontend/resource/icons/iconRecolorNode.png'))

    # ------------------------------------------------------------------------------------------------------------------

    # RUBBER BAND - DRAG
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def toggle_selection_mode(self):
        if self.MODE_RUBBER_BAND:
            self.MODE_RUBBER_BAND = False
            self.view.setDragMode(self.view.drag_mode_hint())

            self.BUTTON_SELECTION_MODE.setIcon(QIcon('frontend/resource/icons/iconRubberBandMode.png'))
        else:
            self.MODE_RUBBER_BAND = True
            self.view.setDragMode(QGraphicsView.NoDrag)

            self.BUTTON_SELECTION_MODE.setIcon(QIcon('frontend/resource/icons/iconDragMode.png'))

    # ------------------------------------------------------------------------------------------------------------------

    # SETTING UP
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_up(self, graph=None, layout=None, cluster=None):
        if graph is not None:
            self.set_graph(graph)

        if layout is not None:
            self.set_layout(layout)

        if cluster is not None:
            self.set_clustering_algorithm(cluster)

    def settings(self, **kwargs):
        self.view.settings(kwargs)

    def set_graph(self, graph_path):
        self.graph = Graph.Read_GraphML(graph_path)

        if 'x' not in self.graph.vs.attributes() or 'nan' in str(self.graph.vs['x']):
            self.set_layout('Random')

        self.setup_availability()

        self.view.update()

    def setup_availability(self):
        np.random.seed(0)
        self.graph.vs["availability"] = np.random.randint(2, size=len(self.graph.vs))

    def set_layout(self, layout):
        graph_layout = self.graph.layout(layout=self.LAYOUTS[layout])
        for c, v in zip(graph_layout.coords, self.graph.vs):
            v['x'] = c[0]
            v['y'] = c[1]
        self.view.update_view()

    def layout_button_clicked(self):
        self.set_up(layout=self.BUTTON_LAYOUT.currentText())

    def set_clustering_algorithm(self, clustering_algorithm):
        self.clustering_algorithm = self.CLUSTERING_ALGORITHMS[clustering_algorithm]
        self.view.update_view()

    def cluster_button_clicked(self):
        self.set_up(cluster=self.BUTTON_CLUSTERING.currentText())

    # ------------------------------------------------------------------------------------------------------------------

    # SHORTEST PATH (SP)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    SP_INPUT_DIALOG = None
    SP_SOURCE_AND_TARGET = None
    SP_SOURCE_AND_TARGET_INDEX = 0
    SP_THREAD = None

    def start_shortest_path_mode(self):
        # Only show one path at a time
        if self.MODE_SHORTEST_PATH:
            self.stop_shortest_path_mode()

        # Initialization steps
        self.MODE_SHORTEST_PATH = True
        self.SP_INPUT_DIALOG = ShortestPathInputDialog(self)
        self.SP_INPUT_DIALOG.show()

        # Disable any other modes that might cause conflict
        self.stop_add_link_mode()

        # Store source and destination vertex ids in a list. -1 means no choice has been made
        self.SP_SOURCE_AND_TARGET = [-1, -1]

    def get_shortest_path_nodes(self, point):
        if self.MODE_SHORTEST_PATH:
            if self.SP_SOURCE_AND_TARGET_INDEX == 0:
                self.SP_SOURCE_AND_TARGET[self.SP_SOURCE_AND_TARGET_INDEX] = point.vertex.index

                self.SP_INPUT_DIALOG.source_node = point.vertex.index
                self.SP_INPUT_DIALOG.textbox_source.setText(str(point.vertex.index))
            else:
                self.SP_SOURCE_AND_TARGET[self.SP_SOURCE_AND_TARGET_INDEX] = point.vertex.index

                self.SP_INPUT_DIALOG.destination_node = point.vertex.index
                self.SP_INPUT_DIALOG.textbox_destination.setText(str(point.vertex.index))

            self.SP_SOURCE_AND_TARGET_INDEX = 1 - self.SP_SOURCE_AND_TARGET_INDEX
            self.SP_INPUT_DIALOG.show()
            self.unhighlight_path()

    def show_path(self):
        edge_path = get_shortest_paths(self.graph, self.SP_SOURCE_AND_TARGET[0], self.SP_SOURCE_AND_TARGET[1])[0]
        self.highlight_path(edge_path)

    def highlight_path(self, edge_path):
        self.view.set_edge_path(edge_path)

        self.SP_THREAD = MainThread(fps=1, parent=self)
        self.SP_THREAD.update.connect(self.view.real_time_highlight)
        self.SP_THREAD.start()

    def unhighlight_path(self):
        if self.SP_THREAD is not None:
            self.SP_THREAD.terminate()
            self.view.unhighlight_path()

    def stop_shortest_path_mode(self):
        self.MODE_SHORTEST_PATH = False
        self.unhighlight_path()

        self.SP_INPUT_DIALOG = None
        self.SP_SOURCE_AND_TARGET = None
        self.SP_SOURCE_AND_TARGET_INDEX = 0
        self.SP_THREAD = None

    # ------------------------------------------------------------------------------------------------------------------

    # STATISTICS
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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

    @staticmethod
    def popup_bar(data):
        bar = DataBar(data)
        bar.show()

    # ------------------------------------------------------------------------------------------------------------------

    # ZOOMING
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def zoom_in_button(self):
        self.view.zoom_in()

    def zoom_out_button(self):
        self.view.zoom_out()

    def reset_zoom_button(self):
        self.view.reset_view()

    # ------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exit(app.exec_())
