from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QFileDialog, QAction
from PyQt5 import uic
from frontend.GraphObject import GraphObject
from frontend.VertexInfo import VertexInfo
from frontend.EdgeInfo import EdgeInfo


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Import ui
        uic.loadUi('frontend/resource/Demo.ui', self)

        # Layout for displaying graph
        self.main_layout = self.findChild(QVBoxLayout, 'mainLayout')
        self.graph_object = GraphObject(self)  # Create a GraphObject object
        self.main_layout.addWidget(self.graph_object)

        # Layout for displaying vertex or edge information
        self.sub_layout = self.findChild(QVBoxLayout, 'subLayout')

        # Bind action into menu button
        self.menu_action()

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
            self.graph_object.read_graph(file_name)
            self.update()
            self.clear_layout(self.sub_layout)

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
            self.graph_object.write_graph(file_name)

    # Clear layout
    @staticmethod
    def clear_layout(layout):
        for i in range(layout.count()):
            layout.itemAt(i).widget().deleteLater()

    # Display vertex information
    def display_vertex(self, vertex):
        self.clear_layout(self.sub_layout)
        vertex_info = VertexInfo(vertex, self.graph_object)
        self.sub_layout.addWidget(vertex_info)

    # Display edge information
    def display_edge(self, edge):
        self.clear_layout(self.sub_layout)
        edge_info = EdgeInfo(edge, self.graph_object)
        self.sub_layout.addWidget(edge_info)
