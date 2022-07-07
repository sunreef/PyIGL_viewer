import os
import sys
import numpy as np
from OpenGL import GL as gl
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtCore import Qt
from queue import Queue, Empty

from .shader import ShaderProgram
from .mouse import MouseHandler
from .camera import Camera

from ..mesh import (
    MeshGroup,
    GlMeshCoreId,
    GlMeshPrefabId,
    GlMeshInstanceId,
)


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

        self.global_uniforms = {}
        self.global_uniforms["lightDirection"] = np.array([0.0, 0.0, 1.0])
        self.global_uniforms["lightDirection"] /= np.linalg.norm(
            self.global_uniforms["lightDirection"]
        )
        self.global_uniforms["lightIntensity"] = np.array([0.95, 0.95, 0.95])
        self.global_uniforms["ambientLighting"] = np.array([0.05, 0.05, 0.05])
        self.global_uniforms["cameraPosition"] = self.camera.get_position()
        self.global_uniforms["linkLight"] = False

        self.line_width = 1
        self.point_size = 3

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
        excluded_attributes = ["position"]
        excluded_uniforms = ["mvp", "projection", "view", "model"]
        excluded_uniforms = excluded_uniforms + list(self.global_uniforms.keys())

        current_file_path = os.path.dirname(os.path.abspath(__file__))
        shader_folder = os.path.join(current_file_path, "..", "shaders")
        for dir_name, dirs, files in os.walk(shader_folder):
            for f in files:
                if f[-5:] == ".vert":
                    shader_name = f[:-5]
                    fragment_shader_name = shader_name + ".frag"
                    self.shaders[shader_name] = ShaderProgram(
                        shader_name,
                        os.path.join(dir_name, f),
                        os.path.join(dir_name, fragment_shader_name),
                        excluded_attributes,
                        excluded_uniforms,
                    )

    def initializeGL(self):
        def hex_to_rgb(value):
            value = value.lstrip("#")
            lv = len(value)
            return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))

        r, g, b = hex_to_rgb(self.main_window.viewer_palette["viewer_background"])

        self.add_shaders()
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glClearDepth(1.0)
        gl.glClearColor(float(r) / 255.0, float(g) / 255.0, float(b) / 255.0, 1.0)
        gl.glEnable(gl.GL_MULTISAMPLE)

    def bind_global_uniforms(self, shader_program):
        for key, value in self.global_uniforms.items():
            location = gl.glGetUniformLocation(shader_program, key)
            if location != -1:
                if type(value) is bool:
                    gl.glUniform1i(location, value)
                if hasattr(value, "shape"):
                    shape = value.shape
                    if len(shape) == 1:
                        if shape[0] == 1:
                            gl.glUniform1fv(location, 1, value)
                        if shape[0] == 2:
                            gl.glUniform2fv(location, 1, value)
                        if shape[0] == 3:
                            gl.glUniform3fv(location, 1, value)
                        if shape[0] == 4:
                            gl.glUniform4fv(location, 1, value)

                    if len(shape) == 2:
                        if shape[0] == shape[1] and shape[0] == 2:
                            gl.glUniformMatrix2fv(location, 1, gl.GL_FALSE, value)
                        if shape[0] == shape[1] and shape[0] == 3:
                            gl.glUniformMatrix3fv(location, 1, gl.GL_FALSE, value)
                        if shape[0] == shape[1] and shape[0] == 4:
                            gl.glUniformMatrix4fv(
                                location, 1, gl.GL_FALSE, value.transpose()
                            )

    def paintGL(self):
        self.process_mesh_events()

        gl.glPointSize(self.point_size)

        def hex_to_rgb(value):
            value = value.lstrip("#")
            lv = len(value)
            return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))

        r, g, b = hex_to_rgb(self.main_window.viewer_palette["viewer_background"])
        gl.glClearColor(float(r) / 255.0, float(g) / 255.0, float(b) / 255.0, 1.0)

        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)
        self.global_uniforms["view"] = self.camera.get_view_matrix()
        self.global_uniforms["projection"] = self.camera.get_projection_matrix()
        self.global_uniforms["cameraPosition"] = self.camera.get_position()
        for group in self.mesh_groups.values():
            for core, prefab, instance in group:
                if not instance.get_visibility():
                    continue
                shader_name = prefab.get_shader().name
                if shader_name == "wireframe" and not self.draw_wireframe:
                    continue
                if prefab.fill:
                    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
                    gl.glLineWidth(1)
                else:
                    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
                    gl.glLineWidth(self.line_width)
                shader_program = prefab.get_shader().program
                gl.glUseProgram(shader_program)

                self.bind_global_uniforms(shader_program)

                # Load projection matrix
                # projection_location = gl.glGetUniformLocation(shader_program, 'projection')
                # gl.glUniformMatrix4fv(projection_location, 1, False, projection_matrix.transpose())

                # Load view matrix
                # view_location = gl.glGetUniformLocation(shader_program, 'view')
                # gl.glUniformMatrix4fv(view_location, 1, False, view_matrix.transpose())

                # Load model matrix
                model_matrix = instance.get_model_matrix()
                if model_matrix is None:
                    instance.set_model_matrix(np.eye(4, dtype="f"))
                    model_matrix = instance.get_model_matrix()
                model_location = gl.glGetUniformLocation(shader_program, "model")
                gl.glUniformMatrix4fv(
                    model_location, 1, False, model_matrix.transpose()
                )

                mvp_location = gl.glGetUniformLocation(shader_program, "mvp")
                gl.glUniformMatrix4fv(
                    mvp_location,
                    1,
                    False,
                    (
                        self.global_uniforms["projection"]
                        * self.global_uniforms["view"]
                        * model_matrix
                    ).transpose(),
                )

                # Draw mesh
                core.bind_buffers()
                prefab.bind_vertex_attributes()
                prefab.bind_uniforms()
                gl.glDrawArrays(
                    core.drawing_mode, 0, core.element_size * core.number_elements
                )
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
            if self.main_window.linked_cameras:
                self.main_window.update_all_viewers()
            else:
                self.update()
        if e.key() == Qt.Key_W:
            self.toggle_wireframe()

    def mousePressEvent(self, e):
        self.mouse_handler.add_mouse_press_event(e)

    def mouseReleaseEvent(self, e):
        self.mouse_handler.add_mouse_release_event(e)
        self.camera.finalize_transformation()
        if self.main_window.linked_cameras:
            self.main_window.update_all_viewers()
        else:
            self.update()

    def mouseMoveEvent(self, e):
        self.mouse_handler.add_mouse_move_event(e)
        if self.mouse_handler.button_pressed(Qt.LeftButton):
            delta = self.mouse_handler.pressed_delta_mouse(Qt.LeftButton)
            self.camera.handle_rotation(delta)
            if self.main_window.linked_cameras:
                self.main_window.update_all_viewers()
            else:
                self.update()
        elif self.mouse_handler.button_pressed(Qt.RightButton):
            delta = self.mouse_handler.pressed_delta_mouse(Qt.RightButton)
            self.camera.handle_translation(delta)
            if self.main_window.linked_cameras:
                self.main_window.update_all_viewers()
            else:
                self.update()

    def wheelEvent(self, e):
        self.mouse_handler.add_scroll_event(e)
        delta = self.mouse_handler.delta_scroll()
        if delta.y() != 0:
            delta = -0.002 * delta.y() / 8.0
            self.camera.handle_zoom(delta)
            if self.main_window.linked_cameras:
                self.main_window.update_all_viewers()
            else:
                self.update()

    #################################################################################################

    #################################################################################################
    # Mesh adding, updating and removing

    def process_mesh_events(self):
        while True:
            try:
                event = self.mesh_events.get(block=False)
                event_type = event[0]
                mesh_function = getattr(self, event_type + "_")
                mesh_function(*event[1:])
            except Empty:
                return

    def add_mesh_(self, core_id, vertices, faces):
        vertices = vertices.astype(np.float32)
        faces = faces.astype(np.int32)
        self.mesh_groups[core_id.core_id] = MeshGroup(vertices, faces)

    def add_mesh(self, vertices, faces):
        core_id = GlMeshCoreId()
        self.mesh_events.put(["add_mesh", core_id, vertices, faces])
        return core_id

    def get_mesh(self, mesh_id):
        return self.mesh_groups[mesh_id.core_id]

    def get_mesh_prefab(self, prefab_id):
        return self.get_mesh(prefab_id).get_prefab(prefab_id)

    def get_mesh_instance(self, instance_id):
        return self.get_mesh(instance_id).get_instance(instance_id)

    def add_mesh_prefab_(
        self,
        prefab_id,
        shader="default",
        vertex_attributes={},
        face_attributes={},
        uniforms={},
        fill=True,
        copy_from=None,
    ):
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
                    copy_from=copy_from,
                )
            except ValueError as err:
                print(err)
                self.get_mesh(prefab_id).add_prefab(
                    prefab_id,
                    vertex_attributes,
                    face_attributes,
                    uniforms,
                    self.shaders["default"],
                    fill=fill,
                    copy_from=copy_from,
                )

    def add_mesh_prefab(
        self,
        core_id,
        shader="default",
        vertex_attributes={},
        face_attributes={},
        uniforms={},
        fill=True,
        copy_from=None,
    ):
        prefab_id = GlMeshPrefabId(core_id)
        self.mesh_events.put(
            [
                "add_mesh_prefab",
                prefab_id,
                shader,
                vertex_attributes,
                face_attributes,
                uniforms,
                fill,
                copy_from,
            ]
        )
        return prefab_id

    def add_mesh_instance_(self, instance_id, model_matrix):
        self.get_mesh(instance_id).add_instance(instance_id, model_matrix)

    def add_mesh_instance(self, prefab_id, model_matrix):
        instance_id = GlMeshInstanceId(prefab_id)
        self.mesh_events.put(["add_mesh_instance", instance_id, model_matrix])
        return instance_id

    def update_mesh_vertices_(self, core_id, vertices):
        self.get_mesh(core_id).update_vertices(vertices.astype(np.float32))

    def update_mesh_vertices(self, core_id, vertices):
        self.mesh_events.put(["update_mesh_vertices", core_id, vertices])

    def update_mesh_prefab_uniform_(self, prefab_id, name, value):
        self.get_mesh(prefab_id).get_prefab(prefab_id).update_uniform(name, value)

    def update_mesh_prefab_uniform(self, prefab_id, name, value):
        self.mesh_events.put(["update_mesh_prefab_uniform", prefab_id, name, value])

    def update_mesh_prefab_vertex_attribute_(self, prefab_id, name, value):
        self.get_mesh(prefab_id).update_prefab_vertex_attribute(prefab_id, name, value)

    def update_mesh_prefab_vertex_attribute(self, prefab_id, name, value):
        self.mesh_events.put(
            ["update_mesh_prefab_vertex_attribute", prefab_id, name, value]
        )

    def update_mesh_prefab_face_attribute_(self, prefab_id, name, value):
        self.get_mesh(prefab_id).update_prefab_face_attribute(prefab_id, name, value)

    def update_mesh_prefab_face_attribute(self, prefab_id, name, value):
        self.mesh_events.put(
            ["update_mesh_prefab_face_attribute", prefab_id, name, value]
        )

    def update_mesh_instance_model_(self, instance_id, model):
        self.get_mesh(instance_id).get_instance(instance_id).set_model_matrix(model)

    def update_mesh_instance_model(self, instance_id, model):
        self.mesh_events.put(["update_mesh_instance_model", instance_id, model])

    def set_mesh_instance_visibility_(self, instance_id, visibility):
        self.get_mesh(instance_id).get_instance(instance_id).set_visibility(visibility)

    def set_mesh_instance_visibility(self, instance_id, visibility):
        self.mesh_events.put(["set_mesh_instance_visibility", instance_id, visibility])

    def get_mesh_instance_visibility(self, instance_id):
        return self.get_mesh(instance_id).get_instance(instance_id).get_visibility()

    def remove_mesh_(self, core_id):
        self.mesh_groups.pop(core_id.core_id)

    def remove_mesh(self, core_id):
        self.mesh_events.put(["remove_mesh", core_id])

    def remove_mesh_prefab_(self, prefab_id):
        self.get_mesh(prefab_id).remove_prefab(prefab_id)

    def remove_mesh_prefab(self, prefab_id):
        self.mesh_events.put(["remove_mesh_prefab", prefab_id])

    def remove_mesh_instance_(self, instance_id):
        self.get_mesh(instance_id).remove_instance(instance_id)

    def remove_mesh_instance(self, instance_id):
        self.mesh_events.put(["remove_mesh_instance", instance_id])

    def clear_all_(self):
        self.mesh_groups.clear()

    def clear_all(self):
        self.mesh_events.put(["clear_all"])

    #################################################################################################

    #################################################################################################
    # General viewer settings

    def set_directional_light(self, direction, intensity):
        self.global_uniforms["lightDirection"] = direction / np.linalg.norm(direction)
        self.global_uniforms["lightIntensity"] = intensity

    def set_ambient_light(self, intensity):
        self.global_uniforms["ambientLighting"] = intensity

    def link_light_to_camera(self, link=True):
        self.global_uniforms["linkLight"] = link

    def toggle_wireframe(self):
        self.draw_wireframe = not self.draw_wireframe
        self.update()

    #################################################################################################

    #################################################################################################
    # Post-draw events

    def process_post_draw_events(self):
        while True:
            try:
                event = self.post_draw_events.get(block=False)
                event_type = event[0]
                mesh_function = getattr(self, event_type + "_")
                mesh_function(*event[1:])
            except Empty:
                return

    def save_screenshot_(self, path):
        current_frame = self.grabFramebuffer()
        current_frame.save(path)

    def save_screenshot(self, path):
        self.post_draw_events.put(["save_screenshot", path])
        self.update()

    #################################################################################################

    #################################################################################################

    # Convenience functions

    def display_point_cloud(
        self,
        points,
        shader="per_vertex_color",
        uniforms={},
        vertex_attributes={},
        face_attributes={},
    ):
        if not "vertexColor" in vertex_attributes:
            vertex_attributes["vertexColor"] = np.tile(
                np.array([0.8, 0.2, 0.2], dtype=np.float32), (points.shape[0], 1)
            )
        faces = np.linspace(
            0, points.shape[0], num=points.shape[0], endpoint=False, dtype=np.int32
        )[:, np.newaxis]
        mesh_id = self.add_mesh(points, faces)
        mesh_prefab_id = self.add_mesh_prefab(
            mesh_id,
            shader=shader,
            vertex_attributes=vertex_attributes,
            face_attributes=face_attributes,
            uniforms=uniforms,
        )
        mesh_instance_id = self.add_mesh_instance(mesh_prefab_id, np.eye(4))
        return mesh_instance_id

    def display_mesh(self, vertices, faces, normals):
        vertex_attributes = {}
        face_attributes = {}
        face_attributes["normal"] = normals
        uniforms = {}
        uniforms["albedo"] = np.array([0.8, 0.8, 0.8])
        mesh_id = self.add_mesh(vertices, faces)
        mesh_prefab_id = self.add_mesh_prefab(
            mesh_id,
            shader="lambert",
            vertex_attributes=vertex_attributes,
            face_attributes=face_attributes,
            uniforms=uniforms,
        )
        mesh_instance_id = self.add_mesh_instance(mesh_prefab_id, np.eye(4))
        return mesh_instance_id

    def display_quad_net(
        self,
        vertices,
        faces,
        shader="wireframe",
        uniforms={"lineColor": np.array([0.8, 0.2, 0.2])},
        vertex_attributes={},
        face_attributes={},
    ):
        mesh_id = self.add_mesh(vertices, faces)
        mesh_prefab_id = self.add_mesh_prefab(
            mesh_id,
            shader=shader,
            vertex_attributes=vertex_attributes,
            face_attributes=face_attributes,
            uniforms=uniforms,
        )
        mesh_instance_id = self.add_mesh_instance(mesh_prefab_id, np.eye(4))
        return mesh_instance_id

    def add_wireframe(self, mesh_instance_id, line_color=np.array([0.0, 0.0, 0.0])):
        self.mesh_events.put(["add_wireframe", mesh_instance_id, line_color])

    def add_wireframe_(self, mesh_instance_id, line_color):
        uniforms = {}
        uniforms["lineColor"] = line_color
        wireframe_mesh_prefab_index = self.add_mesh_prefab(
            mesh_instance_id, "wireframe", fill=False, uniforms=uniforms
        )
        wireframe_instance_index = self.add_mesh_instance(
            wireframe_mesh_prefab_index,
            self.get_mesh_instance(mesh_instance_id).get_model_matrix(),
        )
