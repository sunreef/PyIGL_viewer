import sys
import copy

from .viewer_widget import ViewerWidget
from .ui_widgets import PropertyWidget, LegendWidget

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QLineEdit, QLabel




class Viewer(QMainWindow):
    close_signal = pyqtSignal()
    screenshot_signal = pyqtSignal(str)
    legend_signal = pyqtSignal(list, list)

    def __init__(self):
        super().__init__()
        self.viewer_palette = {
            'viewer_background': '#7f7f9b',
            'viewer_widget_border_color': '#555555',
            'menu_background': '#bbbbbf',
            'ui_element_background': '#cccccc',
            'ui_group_border_color': '#777777',
        }

        self.setAutoFillBackground(True)
        self.setStyleSheet(f"background-color: {self.viewer_palette['viewer_background']}")

        self.main_layout = QGridLayout()
        self.main_layout.setHorizontalSpacing(2)
        self.main_layout.setVerticalSpacing(2)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)

        menu_widget = QFrame(self)
        menu_widget.setFrameStyle(QFrame.Panel | QFrame.Raised)
        menu_widget.setStyleSheet(f"background-color: {self.viewer_palette['menu_background']}")
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setAlignment(Qt.AlignTop)
        menu_widget.setLayout(self.menu_layout)
        self.main_layout.addWidget(menu_widget, 0, 0, -1, 1)
        self.menu_layout.setContentsMargins(2, 2, 2, 2)

        self.viewer_widgets = []
        self.linked_cameras = False
        self.menu_properties = {}
        self.current_menu_layout = self.menu_layout

        self.setCentralWidget(self.central_widget)

        self.screenshot_signal.connect(self.save_screenshot_)
        self.legend_signal.connect(self.add_ui_legend_)

    def add_viewer_widget(self, x, y, row_span=1, column_span=1):
        group_layout = QVBoxLayout()
        group_layout.setSpacing(0)
        group_layout.setContentsMargins(0, 0, 0, 0)
        widget = QFrame(self)
        widget.setLineWidth(2)
        widget.setLayout(group_layout)
        widget.setObjectName('groupFrame')
        widget.setStyleSheet("#groupFrame { border: 1px solid " +
                             self.viewer_palette['viewer_widget_border_color'] + "; }")

        viewer_widget = ViewerWidget(self)
        viewer_widget.setFocusPolicy(Qt.ClickFocus)
        group_layout.addWidget(viewer_widget)
        self.main_layout.addWidget(widget, x, y+1, row_span, column_span)
        viewer_widget.show()
        self.viewer_widgets.append(viewer_widget)
        return viewer_widget, len(self.viewer_widgets) - 1

    def get_viewer_widget(self, index):
        if len(self.viewer_widgets) > index:
            return self.viewer_widgets[index]
        else:
            return None

    def link_all_cameras(self):
        if len(self.viewer_widgets) > 0:
            self.camera = self.viewer_widgets[0].camera
            self.linked_cameras = True
            for widget in self.viewer_widgets:
                widget.camera = self.camera
            self.update_all_viewers()

    def unlink_all_cameras(self):
        if len(self.viewer_widgets) > 0:
            self.linked_cameras = False
            for widget in self.viewer_widgets:
                widget.camera = copy.deepcopy(widget.camera)
            self.update_all_viewers()

    def update_all_viewers(self):
        for widget in self.viewer_widgets:
            widget.update()

    def start_ui_group(self, name):
        group_layout = QVBoxLayout()
        widget = QFrame(self)
        widget.setLineWidth(2)
        widget.setLayout(group_layout)
        widget.setObjectName('groupFrame')
        widget.setStyleSheet("#groupFrame { border: 1px solid " +
                             self.viewer_palette['ui_group_border_color'] + "; }")
        group_label = QLabel(name, widget)
        group_layout.addWidget(group_label)
        group_layout.setAlignment(group_label, Qt.AlignHCenter)
        group_layout.setContentsMargins(2, 2, 2, 2)
        self.menu_layout.addWidget(widget)
        self.current_menu_layout = group_layout

    def finish_ui_group(self):
        self.current_menu_layout = self.menu_layout

    def add_ui_button(self, text, function, color=None):
        if color == None:
            color=self.viewer_palette['ui_element_background']
        button = QPushButton(text, self)
        button.clicked.connect(function)
        button.setAutoFillBackground(True)
        button.setStyleSheet(f"background-color: {color}")
        self.current_menu_layout.addWidget(button)
        return button

    def add_ui_property(self, property_name, text, initial_value, read_only=False):
        widget = PropertyWidget(text, initial_value, read_only)
        self.menu_properties[property_name] = widget
        self.current_menu_layout.addWidget(widget)

    def add_ui_legend_(self, names, colors):
        legend_widget = LegendWidget(names, colors)
        self.current_menu_layout.addWidget(legend_widget)

    def add_ui_legend(self, names, colors):
        self.legend_signal.emit(names, colors)

    def set_float_property(self, name, new_value):
        if name in self.menu_properties:
            try:
                self.menu_properties[name].set_value(new_value)
            except ValueError:
                return
        else:
            return

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

    def set_background_color(self, color):
        self.viewer_palette['viewer_background'] = color
        self.setStyleSheet(f"background-color: {self.viewer_palette['viewer_background']}")

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            sys.stdout.close()
            sys.stderr.close()
            self.close_signal.emit()
            exit()

    def closeEvent(self, event):
        self.close_signal.emit()

    def save_screenshot_(self, path):
        screenshot = QApplication.primaryScreen().grabWindow(self.central_widget.winId())
        screenshot.save(path, 'png')

    def save_screenshot(self, path):
        self.screenshot_signal.emit(path)
