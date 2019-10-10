from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QWidget, QMessageBox, QRadioButton, QComboBox


class AddAttributeValueDialog(QDialog):
    def __init__(self, parent=None):
        super(AddAttributeValueDialog, self).__init__()
        self.parent = parent
        uic.loadUi('frontend/resource/AddAttributeValueDialog.ui', self)
        self.setWindowTitle("Add Attribute Value")

        self.randomizeButton = self.findChild(QRadioButton, 'randomizeButton')
        self.randomizeButton.toggled.connect(self.on_randomize_clicked)

        self.addFileButton = self.findChild(QRadioButton, 'addFileButton')
        self.addFileButton.toggled.connect(self.on_add_file_clicked)

        self.componentComboBox = self.findChild(QComboBox, 'componentComboBox')
        self.componentComboBox.activated.connect(self.on_element_change)

        self.attributeComboBox = self.findChild(QComboBox, 'attributeComboBox')
        self.attributeComboBox.activated.connect(self.on_attribute_change)

        self.button = self.findChild(QWidget, 'buttonBox')
        self.button.accepted.connect(self.on_click_ok)

        self.graph = self.parent.graph

        self.attributeComboBox.addItems(self.graph.es.attributes())

        self.element = "Edge"
        self.attribute = self.attributeComboBox.currentText()

    def on_element_change(self):
        self.element = self.componentComboBox.currentText()

    def on_attribute_change(self):
        self.attribute = self.attributeComboBox.currentText()

    def on_click_ok(self):
        attribute_name = self.textEdit.toPlainText()
        if not attribute_name.strip():
            QMessageBox.about(self, 'Sorry', 'Attribute name should not be empty')
        else:

            if self.element == "Edge":
                if attribute_name in self.graph.es.attributes():
                    QMessageBox.about(self, 'Sorry', 'Edge already have this attribute. Please choose another name.')
                else:
                    if self.dataType == "String":
                        self.graph.es[attribute_name] = ""
                    elif self.dataType == "Integer":
                        self.graph.es[attribute_name] = -1
                    elif self.dataType == "Float":
                        self.graph.es[attribute_name] = -1.
                    QMessageBox.about(self, 'Created', 'Edge attribute created')

            elif self.element == "Vertex":
                if attribute_name in self.graph.vs.attributes():
                    QMessageBox.about(self, 'Sorry', 'Vertex already have this attribute. Please choose another name.')
                else:
                    if self.dataType == "String":
                        self.graph.vs[attribute_name] = ""
                    elif self.dataType == "Integer":
                        self.graph.vs[attribute_name] = -1
                    elif self.dataType == "Float":
                        self.graph.vs[attribute_name] = -1.
                    QMessageBox.about(self, 'Created', 'Vertex attribute created')

    def on_randomize_clicked(self):
        pass

    def on_add_file_clicked(self):
        pass
