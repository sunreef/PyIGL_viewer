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
from queue import Queue, Empty

from .shader import ShaderProgram
from .mouse import MouseHandler
from .camera import Camera

from ..mesh import GlMeshCore, GlMeshPrefab, GlMeshInstance, MeshGroup, GlMeshCoreId, GlMeshPrefabId, GlMeshInstanceId

class ViewerWidget(QOpenGLWidget):
    def __init__(self, parent):
        super(ViewerWidget, self).__init__(parent)

        self.main_window = parent

        # Add antialiasing
        format = QSurfaceFormat()
        format.setSamples(8)
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
        self.mesh_groups = {}
        self.draw_wireframe = True

        # Mouse input handling
        self.mouse_handler = MouseHandler()
        self.setMouseTracking(True)

        # Event queues
        self.mesh_events = Queue()
        self.post_draw_events = Queue()

    def add_shaders(self):       
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        shader_folder = os.path.join(current_file_path, "..", "shaders")
        for dir_name, dirs, files in os.walk(shader_folder):
            for f in files:
                if f[-5:] == '.vert':
                    shader_name = f[:-5]
                    fragment_shader_name = shader_name + '.frag'
                    self.shaders[shader_name] = ShaderProgram(shader_name, os.path.join(dir_name, f),
                        os.path.join(dir_name, fragment_shader_name))

    def initializeGL(self):
        self.add_shaders()
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glClearDepth(1.0)
        gl.glClearColor(0.498, 0.498, 0.6078, 1.0)
        gl.glEnable(gl.GL_MULTISAMPLE)

        gl.glPointSize(3)

    def paintGL(self):
        self.process_mesh_events()

        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)
        view_matrix = self.camera.get_view_matrix()
        projection_matrix = self.camera.get_projection_matrix()
        for group in self.mesh_groups.values():
            for core, prefab, instance in group:
                if not instance.get_visibility():
                    continue
                shader_name = prefab.get_shader().name
                if shader_name == 'wireframe' and not self.draw_wireframe:
                    continue
                if prefab.fill:
                    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
                    gl.glLineWidth(1)
                else:
                    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
                    gl.glLineWidth(3)
                shader_program = prefab.get_shader().program
                gl.glUseProgram(shader_program)

                # Load projection matrix
                projection_location = gl.glGetUniformLocation(shader_program, 'projection')
                gl.glUniformMatrix4fv(projection_location, 1, False, projection_matrix.transpose())

                # Load view matrix
                view_location = gl.glGetUniformLocation(shader_program, 'view')
                gl.glUniformMatrix4fv(view_location, 1, False, view_matrix.transpose())

                # Load model matrix
                model_matrix = instance.get_model_matrix()
                if model_matrix is None:
                    instance.set_model_matrix(np.eye(4, dtype='f'))
                    model_matrix = instance.get_model_matrix()
                model_location = gl.glGetUniformLocation(shader_program, 'model')
                gl.glUniformMatrix4fv(model_location, 1, False, model_matrix.transpose())

                mvp_location = gl.glGetUniformLocation(shader_program, 'mvp')
                gl.glUniformMatrix4fv(mvp_location, 1, False, (projection_matrix * view_matrix * model_matrix).transpose())

                # Draw mesh
                core.bind_buffers()
                prefab.bind_vertex_attributes()
                prefab.bind_uniforms()
                gl.glDrawArrays(core.drawing_mode, 0, core.element_size * core.number_elements)
        self.process_post_draw_events()

    def resizeGL(self, width, height):
        self.camera.handle_resize(width, height)

    #################################################################################################
    # Event handling

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            sys.stdout.close()
            sys.stderr.close()
            self.main_window.close_signal.emit()
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
        self.camera.finalize_transformation()
        self.update()

    def mouseMoveEvent(self, e):
        self.mouse_handler.add_mouse_move_event(e)
        if self.mouse_handler.button_pressed(Qt.LeftButton):
            delta = self.mouse_handler.pressed_delta_mouse(Qt.LeftButton)
            self.camera.handle_rotation(delta)
            self.update()
        elif self.mouse_handler.button_pressed(Qt.RightButton):
            delta = self.mouse_handler.pressed_delta_mouse(Qt.RightButton)
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

    def process_mesh_events(self):
        while True:
            try:
                event = self.mesh_events.get(block=False)
                event_type = event[0]
                mesh_function = getattr(self, event_type + '_')
                mesh_function(*event[1:])
            except Empty:
                return

    def add_mesh_(self, core_id, vertices, faces):
        self.mesh_groups[core_id.core_id] = MeshGroup(vertices, faces)

    def add_mesh(self, vertices, faces):
        core_id = GlMeshCoreId()
        self.mesh_events.put(['add_mesh', core_id, vertices, faces])
        return core_id

    def get_mesh(self, mesh_id):
        return self.mesh_groups[mesh_id.core_id]

    def get_mesh_prefab(self, prefab_id):
        return self.get_mesh(prefab_id).get_prefab(prefab_id)

    def get_mesh_instance(self, instance_id):
        return self.get_mesh(instance_id).get_instance(instance_id)

    def add_mesh_prefab_(self, prefab_id, shader='default', vertex_attributes={}, face_attributes={}, uniforms={}, fill=True, copy_from=None):
        uniforms['lightDirection'] = self.light_direction
        uniforms['lightIntensity'] = self.light_intensity
        uniforms['ambientLighting'] = self.ambient_lighting
        if shader in self.shaders:
            try:
                if copy_from is not None:
                    copy_from = self.get_mesh_prefab(copy_from)
                self.get_mesh(prefab_id).add_prefab(
                        prefab_id, 
                        vertex_attributes, 
                        face_attributes, 
                        uniforms, 
                        self.shaders[shader], 
                        fill=fill, 
                        copy_from=copy_from)
            except ValueError as err:
                print(err)
                self.get_mesh(prefab_id).add_prefab(
                        prefab_id, 
                        vertex_attributes, 
                        face_attributes, 
                        uniforms, 
                        self.shaders['default'], 
                        fill=fill, 
                        copy_from=copy_from)

    def add_mesh_prefab(self, core_id, shader='default', vertex_attributes={}, face_attributes={}, uniforms={}, fill=True, copy_from=None):
        prefab_id = GlMeshPrefabId(core_id)
        self.mesh_events.put(['add_mesh_prefab', prefab_id, shader, vertex_attributes, face_attributes, uniforms, fill, copy_from])
        return prefab_id

    def add_mesh_instance_(self, instance_id, model_matrix):
        self.get_mesh(instance_id).add_instance(instance_id, model_matrix)

    def add_mesh_instance(self, prefab_id, model_matrix):
        instance_id = GlMeshInstanceId(prefab_id)
        self.mesh_events.put(['add_mesh_instance', instance_id, model_matrix])
        return instance_id

    def update_mesh_vertices_(self, core_id, vertices):
        self.get_mesh(core_id).update_vertices(vertices)

    def update_mesh_vertices(self, core_id, vertices):
        self.mesh_events.put(['update_mesh_vertices', core_id, vertices])

    def update_mesh_prefab_uniform_(self, prefab_id, name, value):
        self.get_mesh(prefab_id).get_prefab(prefab_id).update_uniform(name, value)

    def update_mesh_prefab_uniform(self, prefab_id, name, value):
        self.mesh_events.put(['update_mesh_prefab_uniform', prefab_id, name, value])

    def update_mesh_prefab_vertex_attribute_(self, prefab_id, name, value):
        self.get_mesh(prefab_id).update_prefab_vertex_attribute(prefab_id, name, value)

    def update_mesh_prefab_vertex_attribute(self, prefab_id, name, value):
        self.mesh_events.put(['update_mesh_prefab_vertex_attribute', prefab_id, name, value])

    def update_mesh_prefab_face_attribute_(self, prefab_id, name, value):
        self.get_mesh(prefab_id).update_prefab_face_attribute(prefab_id, name, value)

    def update_mesh_prefab_face_attribute(self, prefab_id, name, value):
        self.mesh_events.put(['update_mesh_prefab_face_attribute', prefab_id, name, value])

    def update_mesh_instance_model_(self, instance_id, model):
        self.get_mesh(instance_id).get_instance(instance_id).set_model_matrix(model)

    def update_mesh_instance_model(self, instance_id, model):
        self.mesh_events.put(['update_mesh_instance_model', instance_id, model])

    def set_mesh_instance_visibility_(self, instance_id, visibility):
        self.get_mesh(instance_id).get_instance(instance_id).set_visibility(visibility)

    def set_mesh_instance_visibility(self, instance_id, visibility):
        self.mesh_events.put(['set_mesh_instance_visibility', instance_id, visibility])

    def get_mesh_instance_visibility(self, instance_id):
        return self.get_mesh(instance_id).get_instance(instance_id).get_visibility()

    def remove_mesh_(self, core_id):
        self.mesh_groups.pop(core_id.core_id)

    def remove_mesh(self, core_id):
        self.mesh_events.put(['remove_mesh', core_id])

    def remove_mesh_prefab_(self, prefab_id):
        self.get_mesh(prefab_id).remove_prefab(prefab_id)

    def remove_mesh_prefab(self, prefab_id):
        self.mesh_events.put(['remove_mesh_prefab', prefab_id])

    def remove_mesh_instance_(self, instance_id):
        self.get_mesh(instance_id).remove_instance(instance_id)

    def remove_mesh_instance(self, instance_id):
        self.mesh_events.put(['remove_mesh_instance', instance_id])

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

    def process_post_draw_events(self):
        while True:
            try:
                event = self.post_draw_events.get(block=False)
                event_type = event[0]
                mesh_function = getattr(self, event_type + '_')
                mesh_function(*event[1:])
            except Empty:
                return

    def save_screenshot_(self, path):
        current_frame = self.grabFramebuffer()
        current_frame.save(path)

    def save_screenshot(self, path):
        self.post_draw_events.put(['save_screenshot', path])
        self.update()

    #################################################################################################



