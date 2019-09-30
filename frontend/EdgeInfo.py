from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtCore import Qt


class EdgeInfo(QWidget):
    def __init__(self, edge, graph_object):
        super().__init__()
        self.edge = edge
        self.graph_object = graph_object

        # Dictionary to store edge information
        self.dictionary = edge.attributes()

        # Create grid layout
        layout = QGridLayout(self)

        # Title label
        title_label = QLabel('EDGE INFORMATION')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("QLabel { font-size: 20px; color: #000000 }")
        layout.addWidget(title_label, 0, 0, 1, 2)

        count = 2
        for x, y in self.dictionary.items():
            # Key label
            key_label = QLabel(str(x) + ":")
            key_label.setWordWrap(True)
            key_label.setStyleSheet("QLabel {  font-size: 11px; color: #000000 }")
            layout.addWidget(key_label, count, 0)

            # Value label
            value_label = QLabel(str(y))
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setWordWrap(True)
            value_label.setStyleSheet("QLabel {  font-size: 11px; color: #000000; border: 1px solid #000000 }")
            layout.addWidget(value_label, count, 1)

            count = count + 1
