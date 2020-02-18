import sys

from .viewer_widget import ViewerWidget

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QPushButton



viewer_palette = {
        'viewer_background': '#7f7f9b',
        'menu_background': '#a9bcd0',
        'ui_element_background': '#bbbbbb',
        }



class Viewer(QMainWindow):

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
        self.menu_layout = QGridLayout()
        menu_widget.setLayout(self.menu_layout)
        self.main_layout.addWidget(menu_widget, 0, 0, -1, 1)

        menu_widget.setStyleSheet(f"background-color: {viewer_palette['menu_background']}")

        self.setCentralWidget(widget)

    def add_viewer_widget(self, x, y, row_span=1, column_span=1):
        viewer_widget = ViewerWidget()
        viewer_widget.setFocusPolicy(Qt.ClickFocus)
        self.main_layout.addWidget(viewer_widget, x, y+1, row_span, column_span)
        viewer_widget.show()
        return viewer_widget


    def add_ui_button(self, text, function, color=viewer_palette['ui_element_background']):
        button = QPushButton(text, self)
        button.clicked.connect(function)
        button.setAutoFillBackground(True)
        button.setStyleSheet(f"background-color: {color}")
        self.menu_layout.addWidget(button, 0, 0)
        self.menu_layout.setAlignment(button, Qt.AlignTop)

    def set_column_stretch(self, column, stretch):
        self.main_layout.setColumnStretch(column + 1, stretch)

    def set_row_stretch(self, row, stretch):
        self.main_layout.setRowStretch(row, stretch)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            sys.stdout.close()
            sys.stderr.close()
            exit()


