import sys

from .viewer_widget import ViewerWidget
from .ui_widgets import PropertyWidget

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QLineEdit, QLabel



viewer_palette = {
        'viewer_background': '#7f7f9b',
        'menu_background': '#888888',
        'ui_element_background': '#bbbbbb',
        }



class Viewer(QMainWindow):
    close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setAutoFillBackground(True)
        self.setStyleSheet(f"background-color: {viewer_palette['viewer_background']}")

        self.main_layout = QGridLayout()
        self.main_layout.setHorizontalSpacing(2)
        self.main_layout.setVerticalSpacing(2)
        widget = QWidget()
        widget.setLayout(self.main_layout)

        menu_widget = QWidget()
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setAlignment(Qt.AlignTop)
        menu_widget.setLayout(self.menu_layout)
        self.main_layout.addWidget(menu_widget, 0, 0, -1, 1)

        self.viewer_widgets = []
        self.menu_properties = {}

        menu_widget.setStyleSheet(f"background-color: {viewer_palette['menu_background']}")

        self.setCentralWidget(widget)

    def add_viewer_widget(self, x, y, row_span=1, column_span=1):
        viewer_widget = ViewerWidget()
        viewer_widget.setFocusPolicy(Qt.ClickFocus)
        self.main_layout.addWidget(viewer_widget, x, y+1, row_span, column_span)
        viewer_widget.show()
        self.viewer_widgets.append(viewer_widget)
        return viewer_widget, len(self.viewer_widgets) - 1

    def get_viewer_widget(self, index):
        if len(self.viewer_widgets) > index:
            return self.viewer_widgets[index]
        else:
            return None

    def add_ui_button(self, text, function, color=viewer_palette['ui_element_background']):
        button = QPushButton(text, self)
        button.clicked.connect(function)
        button.setAutoFillBackground(True)
        button.setStyleSheet(f"background-color: {color}")
        self.menu_layout.addWidget(button)
        self.menu_layout.setAlignment(button, Qt.AlignTop)
        return button

    def add_ui_property(self, property_name, text, initial_value):
        widget = PropertyWidget(text, initial_value)
        self.menu_properties[property_name] = widget
        self.menu_layout.addWidget(widget)

    def get_float_property(self, name):
        if name in self.menu_properties:
            try:
                float_property = float(self.menu_properties[name].value)
                return float_property
            except ValueError:
                return None
        else:
            return None

    def set_column_stretch(self, column, stretch):
        self.main_layout.setColumnStretch(column + 1, stretch)

    def set_row_stretch(self, row, stretch):
        self.main_layout.setRowStretch(row, stretch)

    def keyPressEvent(self, e):
        pass

    def closeEvent(self, event):
        self.close_signal.emit()



