import os
import sys
import math
import threading
import numpy as np
from OpenGL import GL as gl
from PyQt5.QtWidgets import QOpenGLWidget, QApplication
from PyQt5.QtCore import Qt

from shader import ShaderProgram
from mouse import MouseHandler
from camera import Camera
from projection import perspective, lookat, normalize, rotate

class ViewerWidget(QOpenGLWidget):
    def __init__(self):
        super(ViewerWidget, self).__init__()

        # Global viewer attributes
        self.camera = Camera(self.size())

        # Available shaders
        self.shaders = {}

        # Mesh attributes
        self.vertex_buffers = []
        self.normal_buffers = []
        self.texture_buffers = []
        self.element_buffers = []
        self.shader_names = []
        self.model_matrices = []

        self.mouse_handler = MouseHandler()
        self.setMouseTracking(True)

    def add_default_shader(self):       
        self.shaders['default'] = ShaderProgram(os.path.join("shaders", "default_vertex_shader.vert"),
            os.path.join("shaders", "default_fragment_shader.frag"))

    def initializeGL(self):
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glClearDepth(1.0)
        gl.glClearColor(0.5, 0.5, 0.65, 1.0)
        self.add_default_shader()

    def paintGL(self):
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)
        view_matrix = self.camera.get_view_matrix()
        projection_matrix = self.camera.get_projection_matrix()
        for (vertex_buffer, normal_buffer, texture_buffer, element_buffer, shader_name) in zip(
                self.vertex_buffers, 
                self.normal_buffers, 
                self.texture_buffers, 
                self.element_buffers,
                self.shader_names):
            shader_program = self.shaders[shader_name].program
            gl.glUseProgram(shader_program)

            # Load projection matrix
            projection_location = gl.glGetUniformLocation(shader_program, 'projection')
            gl.glUniformMatrix4fv(projection_location, 1, False, projection_matrix.transpose())

            # Load view matrix
            view_location = gl.glGetUniformLocation(shader_program, 'view')
            gl.glUniformMatrix4fv(view_location, 1, False, view_matrix.transpose())

            # Load mesh attributes
            gl.glEnableVertexAttribArray(0)
            vertex_buffer.bind()
            gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)

            if normal_buffer is not None:
                gl.glEnableVertexAttribArray(1)
                normal_buffer.bind()
                gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, False, 0, None)
            if texture_buffer is not None:
                gl.glEnableVertexAttribArray(2)
                texture_buffer.bind()
                gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, False, 0, None)
            element_buffer.bind()
            gl.glDrawElements(gl.GL_TRIANGLES, 3, gl.GL_UNSIGNED_INT, None)

            gl.glDisableVertexAttribArray(0)
            gl.glDisableVertexAttribArray(1)
            gl.glDisableVertexAttribArray(2)

    def resizeGL(self, width, height):
        self.camera.handle_resize(width, height)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            sys.stdout.close()
            sys.stderr.close()
            exit()

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

    def add_mesh(self, vertices, faces, normals=None, texture_coords=None):
        self.vertex_buffers.append(gl.arrays.vbo.VBO(vertices))
        self.element_buffers.append(gl.arrays.vbo.VBO(faces, target=gl.GL_ELEMENT_ARRAY_BUFFER))
        if normals is not None:
            self.normal_buffers.append(gl.arrays.vbo.VBO(normals))
        else:
            self.normal_buffers.append(None)
        if texture_coords is not None:
            self.texture_buffers.append(gl.arrays.vbo.VBO(texture_coords))
        else:
            self.texture_buffers.append(None)
        self.shader_names.append('default')
        return len(self.vertex_buffers) - 1


if __name__ == "__main__":
    app = QApplication([])
    widget = ViewerWidget()

    vertices = np.array([[0,1,0.0],[1, 0, 0.0],[0, 0, 0.0]], dtype='f')
    normals = np.array([[0,0,1],[0, 0, 1],[0, 0, 1]], dtype='f')
    tex_coords = np.array([[0,0],[1, 1],[0, 1]], dtype='f')
    indices = np.array([[0,1,2]], dtype=np.int32)
    widget.add_mesh(vertices, indices, normals=normals, texture_coords=tex_coords)

    vertices = np.array([[0,-1,0.0],[-1, 0, 0.0],[0, 0, 0.0]], dtype='f')
    normals = np.array([[0,0,1],[1, 0, 0],[0, 1, 0]], dtype='f')
    tex_coords = np.array([[0,0],[1, 1],[0, 1]], dtype='f')
    indices = np.array([[0,1,2]], dtype=np.int32)
    widget.add_mesh(vertices, indices, normals=normals, texture_coords=tex_coords)

    widget.show()
    sys.exit(app.exec())



