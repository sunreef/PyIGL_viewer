import os
import numpy as np
from OpenGL import GL as gl
from PyQt5.QtWidgets import QOpenGLWidget, QApplication

from shader import ShaderProgram


class ViewerWidget(QOpenGLWidget):
    def __init__(self):
        super(ViewerWidget, self).__init__()

        self.vertex_buffers = []
        self.element_buffers = []

        self.shaders = []


    def add_default_shader(self):       
        self.shaders.append(ShaderProgram(os.path.join("shaders", "default_vertex_shader.vert"),
            os.path.join("shaders", "default_fragment_shader.frag")))

    def initializeGL(self):
        self.add_default_shader()


    def add_triangle(self):
        vertices = np.array([[0,1,0],[-1,-1,0],[1,-1,0]], dtype='f')
        self.vertex_buffers.append(gl.arrays.vbo.VBO(vertices))

        indices = np.array([[0,1,2]], dtype=np.int32)
        self.element_buffers.append(gl.arrays.vbo.VBO(indices, target=gl.GL_ELEMENT_ARRAY_BUFFER))

    def paintGL(self):
        gl.glUseProgram(self.shaders[0].program)
        self.vertex_buffers[0].bind()
        self.element_buffers[0].bind()
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)

        gl.glDrawElements(gl.GL_TRIANGLES, 3, gl.GL_UNSIGNED_INT, None)


if __name__ == "__main__":
    app = QApplication([])
    widget = ViewerWidget()
    widget.add_triangle()
    widget.show()
    app.exec_()
