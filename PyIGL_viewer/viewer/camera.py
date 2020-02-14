import numpy as np
from .projection import perspective, lookat, normalize, rotate

class Camera:
    def __init__(self, size):
        self.aspect_ratio = float(size.width()) / float(size.height())
        self.reset()

    def reset(self):
        self.field_of_view = 60.0
        self.near_plane = 0.01
        self.far_plane = 100.0

        self.eye = np.array([0.0, 0.0, 1.0])
        self.target = np.array([0.0, 0.0, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])

    def handle_resize(self, width, height):
        self.aspect_ratio = float(width) / float(height)

    def handle_rotation(self, delta):
        target_vector = self.eye - self.target
        norm_target_vector = normalize(target_vector)
        left_vector = np.cross(self.up, norm_target_vector)
        rotation_x = rotate(delta.y(), left_vector)
        rotation_y = rotate(delta.x(), self.up)
        rotated_target = np.matmul(rotation_x, target_vector)
        rotated_target = np.array(rotated_target)[0]
        rotated_target = np.array(np.matmul(rotation_y, rotated_target))[0]
        rotated_up_vector = np.array(np.matmul(rotation_x, self.up))[0]
        self.eye = self.target + rotated_target
        self.up = rotated_up_vector

    def handle_translation(self, delta):
        target_vector = self.eye - self.target
        norm_target_vector = normalize(target_vector)
        left_vector = np.cross(self.up, norm_target_vector)
        self.eye += delta.y() * self.up - delta.x() * left_vector
        self.target += delta.y() * self.up - delta.x() * left_vector

    def handle_zoom(self, delta):
        target_vector = self.eye - self.target
        delta = min(delta, 0.9)
        delta = max(delta, -0.9)
        self.eye += delta * target_vector

    def get_view_matrix(self):
        return lookat(self.eye, self.target, self.up)

    def get_projection_matrix(self):
        return perspective(self.field_of_view, self.aspect_ratio, self.near_plane, self.far_plane)
