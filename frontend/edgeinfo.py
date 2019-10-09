from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

from frontend.vertexinfo import EditLabel
from backend.edge import update_edge


class EdgeInfo(QWidget):
    def __init__(self, edge, parent):
        super().__init__()
        self.edge = edge
        self.parent = parent

        # Dictionary to store edge information
        self.dictionary = edge.attributes()

        # Create grid layout
        layout = QGridLayout(self)

        # Title label
        title_label = QLabel('EDGE INFORMATION')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("QLabel { font-size: 20px; color: #000000 }")
        layout.addWidget(title_label, 0, 0, 1, 2)

        self.value_items = []
        self.edit_items = []

        count = 2
        for key, value in self.dictionary.items():
            # Key label
            key_label = QLabel(str(key) + ":")
            key_label.setStyleSheet("QLabel {  font-size: 11px; color: #000000 }")
            layout.addWidget(key_label, count, 0)

            # Value label
            value_label_edit = QLineEdit()
            value_label = EditLabel(value_label_edit)
            self.value_items.append(value_label)
            self.edit_items.append(value_label_edit)

            value_label.setText(str(value))
            value_label_edit.setText(str(value))

            value_label.setAlignment(Qt.AlignCenter)
            value_label_edit.setAlignment(Qt.AlignCenter)

            layout.addWidget(value_label, count, 1)
            layout.addWidget(value_label_edit, count, 1)

            count = count + 1

        for i in range(len(self.edit_items)):
            f = self.text_edited(self.value_items[i], self.edit_items[i])
            self.edit_items[i].editingFinished.connect(f)
            self.edit_items[i].editingFinished.connect(self.save_info)

    @staticmethod
    def text_edited(value, edit):
        def f():
            if edit.text():
                value.setText(str(edit.text()))
                edit.hide()
                value.show()
            else:
                edit.hide()
                value.show()
        return f

    def save_info(self):
        for i, count in zip(self.edge.attributes(), range(len(self.value_items))):
            new_value = self.value_items[count].text()
            try:
                new_value = float(new_value)
            except ValueError:
                pass
            self.edge[i] = new_value

        update_edge(self.parent.graph, self.edge)
        self.parent.view.update_view()
