from igraph import read, write
from PyQt5 import uic
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QAction, QFileDialog, QGridLayout
from frontend.view import MainView
from frontend.infoview import InfoView


class MainWindow(QMainWindow):
    DEFAULT_GRAPH = "frontend/resource/NREN.graphml"

    def __init__(self):
        super().__init__()

        uic.loadUi('frontend/resource/GUI.ui', self)
        self.setWindowTitle("Network Visualization")

        self.central_widget = self.findChild(QWidget, 'centralwidget')
        self.view = MainView(self.central_widget, self)
        self.view.setGeometry(QRect(0, 0, self.central_widget.width(), self.central_widget.height()))

        self.info_widget = self.findChild(QWidget, 'infowidget')
        self.info_view = InfoView(self.info_widget, self)
        self.info_view.setGeometry(QRect(self.central_widget.width(), 0, self.info_widget.width(), self.info_widget.height()))

        self.graph = None
        self.set_graph(self.DEFAULT_GRAPH)

        # Bind action into menu button
        self.menu_action()

    def set_graph(self, graph_path):
        self.graph = read(graph_path)
        self.view.update_view()

    def get_graph(self, graph_path):
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
            self.get_graph(file_name)


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exit(app.exec_())