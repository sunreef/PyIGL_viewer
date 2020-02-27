from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QLineEdit, QLabel

class PropertyWidget(QWidget):
    def __init__(self, text, initial_value, read_only=False):
        super().__init__()
        self.value = str(initial_value)

        label = QLabel(text, self)
        if not read_only:
            self.line_edit = QLineEdit(str(initial_value), self)
            self.line_edit.setAutoFillBackground(True)
            self.line_edit.setStyleSheet("background-color: #eeeeee")
            self.line_edit.setAlignment(Qt.AlignLeft)
            self.line_edit.editingFinished.connect(self.update_value)
        else:
            self.line_edit = QLabel(str(initial_value), self)
            self.line_edit.setAutoFillBackground(True)
            self.line_edit.setAlignment(Qt.AlignLeft)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(label)
        horizontal_layout.setAlignment(label, Qt.AlignLeft)
        horizontal_layout.addWidget(self.line_edit)
        horizontal_layout.setAlignment(self.line_edit, Qt.AlignLeft)
        horizontal_layout.setContentsMargins(2, 1, 2, 1)
        self.setLayout(horizontal_layout)

    def update_value(self):
        self.value = self.line_edit.text()

    def set_value(self, new_value):
        self.line_edit.setText(str(new_value))

class LegendWidget(QWidget):
    def __init__(self, names, colors):
        super().__init__()
        legend_layout = QGridLayout()
        legend_layout.setContentsMargins(2, 0, 2, 0)
        for index, (name, color) in enumerate(zip(names, colors)):
            legend_widget = QWidget()
            legend_color = QLabel("   ", self)
            legend_color.setStyleSheet(f"background-color: {color}")
            legend_name = QLabel(name, self)

            horizontal_layout = QHBoxLayout()
            horizontal_layout.setContentsMargins(1, 0, 0, 0)
            horizontal_layout.addWidget(legend_color)
            # horizontal_layout.setAlignment(legend_color, Qt.AlignLeft)
            horizontal_layout.addWidget(legend_name)
            horizontal_layout.setAlignment(legend_name, Qt.AlignLeft)

            horizontal_layout.setStretch(0, 1)
            horizontal_layout.setStretch(1, 4)
            legend_widget.setLayout(horizontal_layout)
            legend_layout.addWidget(legend_widget, index // 2, index % 2)
        self.setLayout(legend_layout)
        
