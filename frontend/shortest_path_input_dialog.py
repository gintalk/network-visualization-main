from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QPushButton, QLineEdit, QMessageBox


# noinspection PyCallByClass
class ShortestPathInputDialog(QDialog):
    def __init__(self, parent):
        super().__init__(flags=Qt.WindowCloseButtonHint)
        self.parent = parent

        uic.loadUi('frontend/resource/uis/dialogShortestPathInput.ui', self)
        self.setWindowTitle("Calculate shortest paths")

        self.source_node = None
        self.destination_node = None

        self.button_box = self.findChild(QDialogButtonBox, 'buttonBox')
        self.button_box.rejected.connect(self.closeWindow_cancel)
        self.button_box.accepted.connect(self.closeWindow_ok)

        self.button_source = self.findChild(QPushButton, 'source')
        self.button_source.clicked.connect(self.choose_source)
        self.button_destination = self.findChild(QPushButton, 'destination')
        self.button_destination.clicked.connect(self.choose_destination)

        self.textbox_source = self.findChild(QLineEdit, 'sourceText')
        self.textbox_source.setReadOnly(True)
        self.textbox_destination = self.findChild(QLineEdit, 'destinationText')
        self.textbox_destination.setReadOnly(True)

    def choose_source(self):
        self.parent.SP_SOURCE_AND_TARGET_INDEX = 0
        self.hide()

    def choose_destination(self):
        self.parent.SP_SOURCE_AND_TARGET_INDEX = 1
        self.hide()

    def closeWindow_cancel(self):
        self.parent.stop_shortest_path_mode()
        self.hide()

    def closeWindow_ok(self):
        if self.source_node == self.destination_node:
            QMessageBox.about(self, "Invalid Input", "Source and destination cannot be the same node")
        elif self.source_node is None or self.destination_node is None:
            QMessageBox.about(self, "Invalid Input", "Either source or destination is missing")
        elif self.source_node is not None and self.destination_node is not None:
            self.parent.show_path()
            self.hide()
