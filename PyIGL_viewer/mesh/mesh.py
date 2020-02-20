from OpenGL import GL as gl
from ..viewer.shader import ShaderProgram


class GlMesh:
    def __init__(self, vertices, faces, shader='default'):
        self.number_vertices = vertices.shape[0]
        self.number_elements = faces.shape[0]
        self.vertex_buffer = gl.arrays.vbo.VBO(vertices)
        self.element_buffer = gl.arrays.vbo.VBO(faces, target=gl.GL_ELEMENT_ARRAY_BUFFER)

    def bind_buffers(self):
        gl.glEnableVertexAttribArray(0)
        self.vertex_buffer.bind()
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)
        self.element_buffer.bind()

    def update_vertices(self, vertices):
        self.vertex_buffer.set_array(vertices)


class GlMeshInstance:
    def __init__(self, mesh_prefab, model_matrix, attributes, uniforms, shader, fill):
        self.fill = fill
        self.mesh = mesh_prefab
        self.model_matrix = model_matrix
        self.shader = shader
        self.attributes = attributes
        self.uniforms = uniforms

        self.vertex_buffers = {}
        for attribute in self.shader.attributes:
            if not attribute in attributes:
                raise ValueError(f'Attribute {attribute} missing from mesh instance data')
            else:
                self.vertex_buffers[attribute] = (gl.arrays.vbo.VBO(attributes[attribute]), attributes[attribute].shape[1])

        self.uniform_values = {}
        for uniform in self.shader.uniforms:
            if not uniform in uniforms:
                raise ValueError(f'Uniform {uniform} missing from mesh instance data')
            else:
                self.uniform_values[uniform] = uniforms[uniform]

    def number_vertices(self):
        return self.mesh.number_vertices

    def number_elements(self):
        return self.mesh.number_elements

    def set_model_matrix(self, new_model):
        self.model_matrix = new_model

    def get_model_matrix(self):
        return self.model_matrix

    def get_shader(self):
        return self.shader

    def bind_vertex_attributes(self):
        self.mesh.bind_buffers()
        for attribute in self.vertex_buffers:
            attribute_location = self.shader.attributes[attribute]
            gl.glEnableVertexAttribArray(attribute_location)
            attribute_buffer = self.vertex_buffers[attribute][0]
            attribute_size = self.vertex_buffers[attribute][1]
            attribute_buffer.bind()
            gl.glVertexAttribPointer(attribute_location, attribute_size, gl.GL_FLOAT, False, 0, None)

    def bind_uniform_(self, location, value):
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
                gl.glUniformMatrix4fv(location, 1, gl.GL_FALSE, value)

    def bind_uniforms(self):
        for uniform in self.uniform_values:
            uniform_location = self.shader.uniforms[uniform]
            self.bind_uniform_(uniform_location, self.uniform_values[uniform])

