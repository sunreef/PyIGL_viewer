import ctypes
import OpenGL.GL as gl
from OpenGL.GL import shaders

class ShaderProgram:
    def __init__(self, name, vertex_shader_path, fragment_shader_path, excluded_attributes=[], excluded_uniforms=[]):
        self.name = name
        with open(vertex_shader_path, 'r') as vertex_file:
            vertex_shader_text = vertex_file.read()
            vertex_shader = shaders.compileShader(vertex_shader_text, gl.GL_VERTEX_SHADER)

        with open(fragment_shader_path, 'r') as fragment_file:
            fragment_shader_text = fragment_file.read()
            fragment_shader = shaders.compileShader(fragment_shader_text, gl.GL_FRAGMENT_SHADER)

        self.program = shaders.compileProgram(vertex_shader, fragment_shader)

        count_attributes = gl.glGetProgramiv(self.program, gl.GL_ACTIVE_ATTRIBUTES)
        self.attributes = {}
        for i in range(count_attributes):
            bufsize = 256
            length = (ctypes.c_int*1)()
            size = (ctypes.c_int*1)()
            type = (ctypes.c_uint*1)()
            name = ctypes.create_string_buffer(bufsize)
            gl.glGetActiveAttrib(self.program, i, bufsize, length, size, type, name)
            name = name[:length[0]].decode('utf-8')
            if name in excluded_attributes:
                continue
            attribute_location = gl.glGetAttribLocation(self.program, name)
            self.attributes[name] = attribute_location

        count_uniforms = gl.glGetProgramiv(self.program, gl.GL_ACTIVE_UNIFORMS)
        self.uniforms = {}
        for i in range(count_uniforms):
            name, size, type = gl.glGetActiveUniform(self.program, i)
            name = name.decode('utf-8')
            if name in excluded_uniforms:
                continue
            uniform_location = gl.glGetUniformLocation(self.program, name)
            self.uniforms[name] = uniform_location



