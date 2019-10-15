from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QPushButton, QComboBox, QMessageBox


class GradientAndThicknessDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        uic.loadUi('frontend/resource/uis/dialogGradientAndThickness.ui', self)
        self.setWindowTitle("Gradient and Thickness")

        self.gradient_button = self.findChild(QPushButton, 'drawGradient')
        self.gradient_button.clicked.connect(self.parent.view.scene.display_edges_by_gradient)

        self.thickness_button = self.findChild(QPushButton, 'drawThickness')
        self.thickness_button.clicked.connect(self.parent.view.scene.display_edges_by_thickness)

        self.combobox_button = self.findChild(QComboBox, 'comboBox')
        self.combobox_button.activated.connect(self.selection_change)

    def selection_change(self):
        self.parent.attribute = self.combobox_button.currentText()
        if not self.parent.contains_attribute():
            QMessageBox.about(self, 'Sorry', 'This attribute is not available for this graph')