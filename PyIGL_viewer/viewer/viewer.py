import os
import sys
import math
import threading
import numpy as np
from OpenGL import GL as gl
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5 import QtOpenGL, QtCore
from PyQt5.QtGui import QOpenGLVersionProfile, QSurfaceFormat
from PyQt5.QtCore import Qt, pyqtSignal

from .shader import ShaderProgram
from .mouse import MouseHandler
from .camera import Camera

from ..mesh import GlMesh, GlMeshInstance

class ViewerWidget(QOpenGLWidget):
    add_mesh_signal = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray, str)
    update_mesh_signal = pyqtSignal(int, np.ndarray)

    def __init__(self):
        super(ViewerWidget, self).__init__()

        # Add antialiasing
        format = QSurfaceFormat()
        format.setSamples(16)
        self.setFormat(format)

        # Global viewer attributes
        self.camera = Camera(self.size())

        # Available shaders
        self.shaders = {}

        # Mesh attributes
        self.meshes = []
        self.mesh_instances = []

        # Mouse input handling
        self.mouse_handler = MouseHandler()
        self.setMouseTracking(True)

        # Mesh signal connections
        self.add_mesh_signal.connect(self.add_mesh_)
        self.update_mesh_signal.connect(self.update_mesh_)


    def add_shaders(self):       
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        shader_folder = os.path.join(current_file_path, "..", "shaders")
        for dir_name, dirs, files in os.walk(shader_folder):
            for f in files:
                if f[-19:] == '_vertex_shader.vert':
                    shader_name = f[:-19]
                    fragment_shader_name = shader_name + '_fragment_shader.frag'
                    self.shaders[shader_name] = ShaderProgram(os.path.join(dir_name, f),
                        os.path.join(dir_name, fragment_shader_name))

    def initializeGL(self):
        self.add_shaders()

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glClearDepth(1.0)
        gl.glClearColor(0.5, 0.5, 0.65, 1.0)
        gl.glEnable(gl.GL_MULTISAMPLE)

    def paintGL(self):
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)
        view_matrix = self.camera.get_view_matrix()
        projection_matrix = self.camera.get_projection_matrix()
        for mesh_instance in self.mesh_instances:
            shader_name = mesh_instance.get_shader_name()
            if shader_name == 'wireframe':
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            shader_program = self.shaders[mesh_instance.get_shader_name()].program
            gl.glUseProgram(shader_program)

            # Load projection matrix
            projection_location = gl.glGetUniformLocation(shader_program, 'projection')
            gl.glUniformMatrix4fv(projection_location, 1, False, projection_matrix.transpose())

            # Load view matrix
            view_location = gl.glGetUniformLocation(shader_program, 'view')
            gl.glUniformMatrix4fv(view_location, 1, False, view_matrix.transpose())

            # Draw mesh
            mesh_instance.bind_vertex_attributes()
            gl.glDrawElements(gl.GL_TRIANGLES, 3 * mesh_instance.number_elements(), gl.GL_UNSIGNED_INT, None)
            if shader_name == 'wireframe':
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    def resizeGL(self, width, height):
        self.camera.handle_resize(width, height)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            sys.stdout.close()
            sys.stderr.close()
            exit()
        if e.key() == Qt.Key_R:
            self.camera.reset()
            self.update()

    def mousePressEvent(self, e):
        self.mouse_handler.add_mouse_press_event(e)

    def mouseReleaseEvent(self, e):
        self.mouse_handler.add_mouse_release_event(e)

    def mouseMoveEvent(self, e):
        self.mouse_handler.add_mouse_move_event(e)
        if self.mouse_handler.button_pressed(Qt.LeftButton):
            delta = -0.2 * self.mouse_handler.delta_mouse()
            self.camera.handle_rotation(delta)
            self.update()

    def add_mesh_(self, vertices, faces, normals=None, texture_coords=None, shader='default'):
        self.meshes.append(GlMesh(vertices, faces, normals, texture_coords))
        self.mesh_instances.append(GlMeshInstance(self.meshes[-1], None, shader))
        self.mesh_instances.append(GlMeshInstance(self.meshes[-1], None, 'wireframe'))
        self.update()

    def add_mesh(self, vertices, faces, normals=np.array([]), texture_coords=np.array([]), shader='default'):
        self.add_mesh_signal.emit(vertices, faces, normals, texture_coords, shader)
        return len(self.meshes)

    def update_mesh_(self, index, vertices, normals=None, texture_coords=None):
        self.meshes[index].update_vertices(vertices)
        self.update()

    def update_mesh(self, index, vertices, normals=None, texture_coords=None):
        self.update_mesh_signal.emit(index, vertices)




