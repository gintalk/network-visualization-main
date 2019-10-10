from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QWidget, QComboBox, QLineEdit, QMessageBox
import numpy as np


class RandomizeDialog(QDialog):
    def __init__(self, parent, element, attribute):
        super(RandomizeDialog, self).__init__()
        self.parent = parent
        self.element = element
        self.attribute = attribute
        uic.loadUi('frontend/resource/RandomizeDialog.ui', self)
        self.setWindowTitle("Randomize value for a attribute")

        self.distributionComboBox.activated.connect(self.on_distribution_change)
        self.buttonBox.accepted.connect(self.on_click_ok)

        self.graph = self.parent.graph
        self.distribution = "Normal Distribution"

    def on_distribution_change(self):
        self.distribution = self.distributionComboBox.currentText()
        if self.distribution == "Normal Distribution":
            self.label.setText("Mean")
            self.label_2.setText("Standard Deviation")
        elif self.distribution == "Uniform Distribution":
            self.label.setText("Min")
            self.label_2.setText("Max")

    def on_click_ok(self):
        x_value = self.lineEdit.text()
        y_value = self.lineEdit_2.text()
        if not x_value.strip() or not y_value.strip():
            QMessageBox.about(self, 'Sorry', 'Attribute value should not be empty')
        else:
            x_value = float(x_value)
            y_value = float(y_value)
            if self.element == "Edge":
                if self.distribution == "Uniform Distribution":
                    value = (y_value - x_value) * np.random.rand(self.graph.ecount()) + x_value
                elif self.distribution == "Normal Distribution":
                    value = y_value * np.random.standard_normal(self.graph.ecount()) + x_value
                self.graph.es[self.attribute] = value
            elif self.element == "Vertex":
                if self.distribution == "Uniform Distribution":
                    value = (y_value - x_value) * np.random.rand(self.graph.vcount()) + x_value
                elif self.distribution == "Normal Distribution":
                    value = y_value * np.random.standard_normal(self.graph.vcount()) + x_value
                self.graph.vs[self.attribute] = value
            QMessageBox.about(self, 'Successful', 'Attribute value have been added')
