from OpenGL import GL as gl

from ..viewer.shader import ShaderProgram

class GlMesh:
    def __init__(self, vertices, faces, normals=None, texture_coords=None, shader='default'):
        self.number_vertices = vertices.shape[0]
        self.number_elements = faces.shape[0]
        self.vertex_buffer = gl.arrays.vbo.VBO(vertices)
        self.element_buffer = gl.arrays.vbo.VBO(faces, target=gl.GL_ELEMENT_ARRAY_BUFFER)
        if normals.shape[0] > 0:
            self.normal_buffer = gl.arrays.vbo.VBO(normals)
        else:
            self.normal_buffer = None
        if texture_coords.shape[0] > 0:
            self.texture_buffer = gl.arrays.vbo.VBO(texture_coords)
        else:
            self.texture_buffer = None

    def bind_buffers(self):
        gl.glEnableVertexAttribArray(0)
        self.vertex_buffer.bind()
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)
        if self.normal_buffer is not None:
            gl.glEnableVertexAttribArray(1)
            self.normal_buffer.bind()
            gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, False, 0, None)
        if self.texture_buffer is not None:
            gl.glEnableVertexAttribArray(2)
            self.texture_buffer.bind()
            gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, False, 0, None)
        self.element_buffer.bind()

    def update_vertices(self, vertices):
        self.vertex_buffer.set_array(vertices)

class GlMeshInstance:
    def __init__(self, mesh_prefab, model_matrix, albedo, shader_name):
        self.mesh = mesh_prefab
        self.model_matrix = model_matrix
        self.shader_name = shader_name
        self.albedo = albedo

    def number_vertices(self):
        return self.mesh.number_vertices

    def number_elements(self):
        return self.mesh.number_elements

    def get_model_matrix(self):
        return self.model_matrix

    def get_albedo(self):
        return self.albedo

    def get_shader_name(self):
        return self.shader_name


    def bind_vertex_attributes(self):
        self.mesh.bind_buffers()
