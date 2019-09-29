from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QFileDialog, QAction
from PyQt5 import uic
from frontend.GraphObject import GraphObject


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Import ui
        uic.loadUi('frontend/resource/Demo.ui', self)

        # Layout for displaying graph
        self.mainLayout = self.findChild(QVBoxLayout, 'mainLayout')
        self.graph_object = GraphObject()  # Create a GraphObject object
        self.mainLayout.addWidget(self.graph_object)

        # Layout for displaying vertex or edge information
        self.subLayout = self.findChild(QVBoxLayout, 'subLayout')

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

        # View -> Zoom In
        self.findChild(QAction, 'actionZoom_In').triggered.connect(self.graph_object.zoomInEvent)

        # View -> Zoom Out
        self.findChild(QAction, 'actionZoom_Out').triggered.connect(self.graph_object.zoomOutEvent)

        # View -> Reset Zoom
        self.findChild(QAction, 'actionReset_Zoom').triggered.connect(self.graph_object.zoomResetEvent)

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
