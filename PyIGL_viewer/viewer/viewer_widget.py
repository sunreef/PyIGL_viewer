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
    add_mesh_signal = pyqtSignal(np.ndarray, np.ndarray)
    add_mesh_instance_signal = pyqtSignal(int, str, dict, dict, bool)
    update_mesh_vertices_signal = pyqtSignal(int, np.ndarray)
    update_mesh_instance_model_signal = pyqtSignal(int, np.ndarray)

    def __init__(self, parent):
        super(ViewerWidget, self).__init__(parent)

        # Add antialiasing
        format = QSurfaceFormat()
        format.setSamples(16)
        self.setFormat(format)

        # Global viewer attributes
        self.camera = Camera(self.size())
        self.light_direction = np.array([-0.1, -0.1, 1.0])
        self.light_direction /= np.linalg.norm(self.light_direction)
        self.light_intensity = np.array([1.5, 1.5, 1.5])
        self.ambient_lighting = np.array([0.1, 0.1, 0.1])

        # Available shaders
        self.shaders = {}

        # Mesh attributes
        self.next_mesh = 0
        self.next_mesh_instance = 0
        self.meshes = []
        self.mesh_instances = []
        self.draw_wireframe = True

        # Mouse input handling
        self.mouse_handler = MouseHandler()
        self.setMouseTracking(True)

        # Mesh signal connections
        self.add_mesh_lock = threading.Lock()
        self.add_mesh_signal.connect(self.add_mesh_)

        self.add_mesh_instance_lock = threading.Lock()
        self.add_mesh_instance_signal.connect(self.add_mesh_instance_)

        self.update_mesh_vertices_signal.connect(self.update_mesh_vertices_)

        self.update_mesh_instance_model_signal.connect(self.update_mesh_instance_model_)

    def add_shaders(self):       
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        shader_folder = os.path.join(current_file_path, "..", "shaders")
        for dir_name, dirs, files in os.walk(shader_folder):
            for f in files:
                if f[-19:] == '_vertex_shader.vert':
                    shader_name = f[:-19]
                    fragment_shader_name = shader_name + '_fragment_shader.frag'
                    self.shaders[shader_name] = ShaderProgram(shader_name, os.path.join(dir_name, f),
                        os.path.join(dir_name, fragment_shader_name))

    def initializeGL(self):
        self.add_shaders()
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glClearDepth(1.0)
        gl.glClearColor(0.498, 0.498, 0.6078, 1.0)
        gl.glEnable(gl.GL_MULTISAMPLE)

    def paintGL(self):
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)
        view_matrix = self.camera.get_view_matrix()
        projection_matrix = self.camera.get_projection_matrix()
        for mesh_instance in self.mesh_instances:
            shader_name = mesh_instance.get_shader().name
            if shader_name == 'wireframe' and not self.draw_wireframe:
                continue
            if mesh_instance.fill:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
            else:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            shader_program = mesh_instance.get_shader().program
            gl.glUseProgram(shader_program)

            # Load projection matrix
            projection_location = gl.glGetUniformLocation(shader_program, 'projection')
            gl.glUniformMatrix4fv(projection_location, 1, False, projection_matrix.transpose())

            # Load view matrix
            view_location = gl.glGetUniformLocation(shader_program, 'view')
            gl.glUniformMatrix4fv(view_location, 1, False, view_matrix.transpose())

            # Load model matrix
            model_matrix = mesh_instance.get_model_matrix()
            if model_matrix is None:
                mesh_instance.set_model_matrix(np.eye(4, dtype='f'))
                model_matrix = mesh_instance.get_model_matrix()
            model_location = gl.glGetUniformLocation(shader_program, 'model')
            gl.glUniformMatrix4fv(model_location, 1, False, model_matrix.transpose())

            # Draw mesh
            mesh_instance.bind_vertex_attributes()
            mesh_instance.bind_uniforms()
            gl.glDrawElements(gl.GL_TRIANGLES, 3 * mesh_instance.number_elements(), gl.GL_UNSIGNED_INT, None)

    def resizeGL(self, width, height):
        self.camera.handle_resize(width, height)

    #################################################################################################
    # Event handling

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            sys.stdout.close()
            sys.stderr.close()
            self.parent.close_signal.emit()
            exit()
        if e.key() == Qt.Key_R:
            self.camera.reset()
            self.update()
        if e.key() == Qt.Key_W:
            self.toggle_wireframe()

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
        elif self.mouse_handler.button_pressed(Qt.RightButton):
            delta = self.mouse_handler.delta_mouse()
            self.camera.handle_translation(delta)
            self.update()

    def wheelEvent(self, e):
        self.mouse_handler.add_scroll_event(e)
        delta = self.mouse_handler.delta_scroll()
        if delta.y() != 0:
            delta = -0.002 * delta.y() / 8.0
            self.camera.handle_zoom(delta)
            self.update()

    #################################################################################################

    #################################################################################################
    # Mesh adding, updating and removing

    def add_mesh_(self, vertices, faces):
        self.meshes.append(GlMesh(vertices, faces))

    def add_mesh(self, vertices, faces):
        self.add_mesh_lock.acquire()
        self.add_mesh_signal.emit(vertices, faces)
        mesh_index = self.next_mesh
        self.next_mesh += 1
        self.add_mesh_lock.release()
        return mesh_index

    def add_mesh_instance_(self, mesh_index, shader='default', attributes={}, uniforms={}, fill=True):
        uniforms['lightDirection'] = self.light_direction
        uniforms['lightIntensity'] = self.light_intensity
        uniforms['ambientLighting'] = self.ambient_lighting
        if shader in self.shaders:
            try:
                self.mesh_instances.append(GlMeshInstance(self.meshes[mesh_index], None, attributes, uniforms, self.shaders[shader], fill=fill))
            except ValueError as err:
                print(err)
                self.mesh_instances.append(GlMeshInstance(self.meshes[mesh_index], None, attributes, uniforms, self.shaders['default'], fill=fill))
        # if 'wireframe' in self.shaders and fill and add_wireframe:
            # self.mesh_instances.append(GlMeshInstance(self.meshes[mesh_index], None, attributes, uniforms, self.shaders['wireframe'], fill=False))
        self.update()

    def add_mesh_instance(self, mesh_index, shader='default', attributes={}, uniforms={}, fill=True):
        self.add_mesh_instance_lock.acquire()
        self.add_mesh_instance_signal.emit(mesh_index, shader, attributes, uniforms, fill)
        instance_index = self.next_mesh_instance
        self.next_mesh_instance += 1
        self.add_mesh_instance_lock.release()
        return instance_index

    def update_mesh_vertices(self, index, vertices):
        self.meshes[index].update_vertices(vertices)
        self.update()

    def update_mesh_vertices_(self, index, vertices):
        self.update_mesh_vertices_signal.emit(index, vertices)

    def update_mesh_instance_model(self, instance_index, model):
        self.update_mesh_instance_model_signal.emit(instance_index, model)

    def update_mesh_instance_model_(self, instance_index, model):
        self.mesh_instances[instance_index].set_model_matrix(model)
        self.update()

    def remove_mesh(self, mesh_index):
        if len(self.meshes) > mesh_index:
            mesh_to_remove = self.meshes[mesh_index]
            self.meshes[mesh_index] = None
            for index, instance in enumerate(self.mesh_instances):
                if self.mesh == mesh_to_remove:
                    self.mesh_instances[index] = None

    #################################################################################################

    #################################################################################################
    # General viewer settings

    def set_directional_light(self, direction, intensity):
        self.light_direction = direction
        self.light_intensity = intensity

    def set_ambient_light(self, intensity):
        self.ambient_lighting = intensity

    def toggle_wireframe(self):
        self.draw_wireframe = not self.draw_wireframe
        self.update()

    #################################################################################################



