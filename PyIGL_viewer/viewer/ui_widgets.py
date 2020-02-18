from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel

class PropertyWidget(QWidget):
    def __init__(self, text, initial_value):
        super().__init__()
        self.value = str(initial_value)

        label = QLabel(text, self)
        self.line_edit = QLineEdit(str(initial_value), self)
        self.line_edit.setAutoFillBackground(True)
        self.line_edit.setAlignment(Qt.AlignLeft)
        self.line_edit.editingFinished.connect(self.set_value)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(label)
        horizontal_layout.setAlignment(label, Qt.AlignLeft)
        horizontal_layout.addWidget(self.line_edit)
        horizontal_layout.setAlignment(self.line_edit, Qt.AlignLeft)
        self.setLayout(horizontal_layout)

    def set_value(self):
        self.value = self.line_edit.text()
