from PyQt5.QtCore import Qt, QPointF, QPoint
from collections import deque


class MouseHandler:
    def __init__(self):
        self.previous_pos = None
        self.current_pos = None
        self.position_history = deque(5 * [QPointF(0.0, 0.0)], 5)
        self.button_press_timestamp = {
            Qt.LeftButton: 0,
            Qt.RightButton: 0,
            Qt.MiddleButton: 0,
        }
        self.button_press_position = {
            Qt.LeftButton: QPoint(),
            Qt.RightButton: QPoint(),
            Qt.MiddleButton: QPoint(),
        }
        self.scroll_delta_history = deque(5 * [QPoint()], 5)

    def add_mouse_move_event(self, e):
        self.position_history.appendleft(e.localPos())

    def add_mouse_press_event(self, e):
        self.button_press_timestamp[e.button()] = e.timestamp()
        self.button_press_position[e.button()] = e.localPos()

    def add_mouse_release_event(self, e):
        self.button_press_timestamp[e.button()] = 0

    def add_scroll_event(self, e):
        self.scroll_delta_history.appendleft(e.angleDelta())

    def pressed_delta_mouse(self, button):
        return self.position_history[0] - self.button_press_position[button]

    def delta_mouse(self):
        return self.position_history[0] - self.position_history[1]

    def delta_scroll(self):
        return self.scroll_delta_history[0]

    def button_pressed(self, b):
        return self.button_press_timestamp[b] != 0
