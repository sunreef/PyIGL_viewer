from PyQt5.QtCore import Qt, QPointF
from collections import deque

class MouseHandler:
    def __init__(self):
        self.previous_pos = None
        self.current_pos = None

        self.position_history = deque(5*[QPointF(0.0, 0.0)], 5)
        self.button_press_timestamp = {
                Qt.LeftButton: 0,
                Qt.RightButton: 0,
                Qt.MiddleButton: 0,
            }

    def add_mouse_move_event(self, e):
        self.position_history.appendleft(e.localPos())

    def add_mouse_press_event(self, e):
        self.button_press_timestamp[e.button()] = e.timestamp()

    def add_mouse_release_event(self, e):
        self.button_press_timestamp[e.button()] = 0

    def delta_mouse(self):
        return self.position_history[0] - self.position_history[1]

    def button_pressed(self, b):
        return self.button_press_timestamp[b] != 0





