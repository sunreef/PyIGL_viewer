import OpenGL.GL as gl
from OpenGL.GL import shaders

class ShaderProgram:
    def __init__(self, vertex_shader_path, fragment_shader_path):
        with open(vertex_shader_path, 'r') as vertex_file:
            vertex_shader_text = vertex_file.read()
            vertex_shader = shaders.compileShader(vertex_shader_text, gl.GL_VERTEX_SHADER)

        with open(fragment_shader_path, 'r') as fragment_file:
            fragment_shader_text = fragment_file.read()
            fragment_shader = shaders.compileShader(fragment_shader_text, gl.GL_FRAGMENT_SHADER)

        self.program = shaders.compileProgram(vertex_shader, fragment_shader)


