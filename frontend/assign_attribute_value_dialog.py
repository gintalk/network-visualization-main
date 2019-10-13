from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
from frontend.randomize_dialog import RandomizeDialog
import numpy as np


class AssignAttributeValueDialog(QDialog):
    def __init__(self, parent=None):
        super(AssignAttributeValueDialog, self).__init__()
        self.parent = parent
        uic.loadUi('frontend/resource/AssignAttributeValueDialog.ui', self)
        self.setWindowTitle("Add Attribute Value")

        self.componentComboBox.activated.connect(self.on_element_change)
        self.attributeComboBox.activated.connect(self.on_attribute_change)
        self.buttonBox.accepted.connect(self.on_click_ok)

        self.graph = self.parent.graph
        self.attributeComboBox.addItems(self.graph.es.attributes())

        self.element = "Edge"
        self.attribute = self.attributeComboBox.currentText()

    def on_element_change(self):
        self.element = self.componentComboBox.currentText()
        if self.element == "Edge":
            self.attributeComboBox.clear()
            self.attributeComboBox.addItems(self.graph.es.attributes())
        elif self.element == "Vertex":
            self.attributeComboBox.clear()
            self.attributeComboBox.addItems(self.graph.vs.attributes())

    def on_attribute_change(self):
        self.attribute = self.attributeComboBox.currentText()

    def on_click_ok(self):
        if self.randomizeButton.isChecked():
            self.randomizeDialog = RandomizeDialog(self, self.element, self.attribute)
            self.randomizeDialog.show()
        elif self.addFileButton.isChecked():
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Open", "",
                "All Files (*);;GraphML Files (*.graphml)", options=options
            )
            value = np.load(file_name)

            if self.element == "Edge":
                self.graph.es[self.attribute] = value
                print(value)
            elif self.element == "Vertex":
                self.graph.vs[self.attribute] = value
            QMessageBox.about(self, 'Successful', 'Attribute value have been added')
