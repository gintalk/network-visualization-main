from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QComboBox, QWidget, QTextEdit, QMessageBox


class CreateAttributeDialog(QDialog):
    def __init__(self, parent=None):
        super(CreateAttributeDialog, self).__init__()
        self.parent = parent
        uic.loadUi('frontend/resource/CreateAttributeDialog.ui', self)
        self.setWindowTitle("Create Attribute")

        self.comboboxButton = self.findChild(QComboBox, 'comboBox')
        self.comboboxButton.activated.connect(self.on_element_change)

        self.textEdit = self.findChild(QTextEdit, 'textEdit')

        self.button = self.findChild(QWidget, 'buttonBox')
        self.button.accepted.connect(self.on_click_ok)

        self.graph = self.parent.graph

        self.element = "Edge"

    def on_element_change(self):
        self.element = self.comboboxButton.currentText()

    def on_click_ok(self):
        attribute_name = self.textEdit.toPlainText()
        if not attribute_name.strip():
            QMessageBox.about(self, 'Sorry', 'Attribute name should not be empty')
        else:

            if self.element == "Edge":
                if attribute_name in self.graph.es.attributes():
                    QMessageBox.about(self, 'Sorry', 'Edge already have this attribute. Please choose another name.')
                else:
                    self.graph.es[attribute_name] = None
                    QMessageBox.about(self, 'Created', 'Edge attribute created')

            elif self.element == "Vertex":
                if attribute_name in self.graph.vs:
                    QMessageBox.about(self, 'Sorry', 'Vertex already have this attribute. Please choose another name.')
                else:
                    self.graph.vs[attribute_name] = None
                    QMessageBox.about(self, 'Created', 'Vertex attribute created')
