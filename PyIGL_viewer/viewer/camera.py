import numpy as np
from .projection import perspective, lookat, normalize, magnitude, rotate


class Camera:
    def __init__(self, size):
        self.width = size.width()
        self.height = size.height()
        self.aspect_ratio = float(size.width()) / float(size.height())
        self.reset()

    def reset(self):
        self.field_of_view = 60.0
        self.near_plane = 0.01
        self.far_plane = 100.0

        self.eye = np.array([0.0, 0.0, 1.0])
        self.target = np.array([0.0, 0.0, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])

        self.current_eye = self.eye
        self.current_target = self.target
        self.current_up = self.up

    def handle_resize(self, width, height):
        self.aspect_ratio = float(width) / float(height)
        self.width = width
        self.height = height

    def handle_rotation(self, delta):
        delta = -0.2 * delta
        target_vector = self.eye - self.target
        dist_target = magnitude(target_vector)
        norm_target_vector = normalize(target_vector)
        left_vector = np.cross(self.up, norm_target_vector)
        rotation_x = rotate(delta.y(), left_vector)
        rotation_y = rotate(delta.x(), self.up)
        rotated_target = np.matmul(rotation_x, target_vector)
        rotated_target = np.array(rotated_target)[0]
        rotated_target = np.array(np.matmul(rotation_y, rotated_target))[0]
        rotated_target = normalize(rotated_target)
        rotated_left = np.array(np.matmul(rotation_y, left_vector))[0]
        self.current_up = np.cross(rotated_target, rotated_left)
        self.current_eye = self.target + dist_target * rotated_target

    def handle_translation(self, delta):
        delta.setX(delta.x() / self.width)
        delta.setY(delta.y() / self.height)
        target_vector = self.eye - self.target
        norm_target_vector = normalize(target_vector)
        left_vector = np.cross(self.up, norm_target_vector)
        self.current_eye = self.eye + delta.y() * self.up - delta.x() * left_vector
        self.current_target = (
            self.target + delta.y() * self.up - delta.x() * left_vector
        )

    def finalize_transformation(self):
        self.eye = self.current_eye
        self.target = self.current_target
        self.up = self.current_up

    def handle_zoom(self, delta):
        target_vector = self.eye - self.target
        delta = min(delta, 0.9)
        delta = max(delta, -0.9)
        self.eye += delta * target_vector

    def get_position(self):
        return self.current_eye

    def get_view_matrix(self):
        return lookat(self.current_eye, self.current_target, self.current_up)

    def get_projection_matrix(self):
        return perspective(
            self.field_of_view, self.aspect_ratio, self.near_plane, self.far_plane
        )
