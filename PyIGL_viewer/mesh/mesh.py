from OpenGL import GL as gl
from ..viewer.shader import ShaderProgram
from itertools import chain
import numpy as np

import datetime
import uuid


#################################################################################################
# A mesh core contains the vertex positions and the topology of the triangle mesh.

class GlMeshCoreId:
    def __init__(self):
        self.core_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + str(uuid.uuid4())


class GlMeshCore:
    def __init__(self, vertices, faces):
        self.number_vertices = vertices.shape[0]
        self.number_elements = faces.shape[0]

        self.face_size = faces.shape[1]
        if self.face_size == 3:
            self.drawing_mode = gl.GL_TRIANGLES 
        else:
            self.drawing_mode = gl.GL_LINES 
            new_faces = np.zeros((self.number_elements, 2 * self.face_size), dtype=np.int32)
            for s in range(self.face_size):
                new_faces[:, 2 * s] = faces[:, s]
                new_faces[:, 2 * s - 1] = faces[:, s]
            faces = new_faces
            self.face_size *= 2

        self.vertex_buffer = gl.arrays.vbo.VBO(vertices)
        self.element_buffer = gl.arrays.vbo.VBO(faces, target=gl.GL_ELEMENT_ARRAY_BUFFER)

    def bind_buffers(self):
        gl.glEnableVertexAttribArray(0)
        self.vertex_buffer.bind()
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)
        self.element_buffer.bind()

    def update_vertices(self, vertices):
        self.vertex_buffer.set_array(vertices)

#################################################################################################
        
#################################################################################################
# A mesh prefab contains a shader program as well as the necessary vertex attributes and uniform values for this shader.
# It defines the appearance of a given mesh.

class GlMeshPrefabId:
    def __init__(self, core_id):
        self.core_id = core_id.core_id
        self.prefab_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + str(uuid.uuid4())

class GlMeshPrefab:
    def __init__(self, attributes, uniforms, shader, fill):
        self.fill = fill
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

    def get_shader(self):
        return self.shader

    def bind_vertex_attributes(self):
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

#################################################################################################

#################################################################################################
# A mesh instance contains the mesh model matrix that gives its position and orientation in the world.
# It also contains a visibility flag that determines whether the mesh will be drawn or not.

class GlMeshInstanceId:
    def __init__(self, prefab_id):
        self.core_id = prefab_id.core_id
        self.prefab_id = prefab_id.prefab_id
        self.instance_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + str(uuid.uuid4())


class GlMeshInstance:
    def __init__(self, model_matrix):
        self.model_matrix = model_matrix
        self.visibility= True

    def set_model_matrix(self, new_model):
        self.model_matrix = new_model

    def get_model_matrix(self):
        return self.model_matrix

    def get_visibility(self):
        return self.visibility

    def set_visibility(self, visibility):
        self.visibility = visibility

#################################################################################################

#################################################################################################
# A mesh group contains all the prefabs and instances related to a mesh core.

class MeshGroup:
    def __init__(self, vertices, faces):
        self.mesh_core = GlMeshCore(vertices, faces)
        self.mesh_prefabs = {}
        self.mesh_instances = {}

    def add_prefab(self, prefab_id, attributes, uniforms, shader, fill):
        self.mesh_prefabs[prefab_id.prefab_id] = GlMeshPrefab(attributes, uniforms, shader, fill)
        self.mesh_instances[prefab_id.prefab_id] = {}

    def add_instance(self, instance_id, model_matrix):
        # if instance_id.prefab_id not in self.mesh_instances:
            # self.mesh_instances[instance_id.prefab_id] = {}
        self.mesh_instances[instance_id.prefab_id][instance_id.instance_id] = GlMeshInstance(model_matrix)

    def get_prefab(self, prefab_id):
        return self.mesh_prefabs[prefab_id.prefab_id]

    def get_instance(self, instance_id):
        return self.mesh_instances[instance_id.prefab_id][instance_id.instance_id]

    def remove_prefab(self, prefab_id):
        self.mesh_prefabs.pop(prefab_id.prefab_id)
        self.mesh_instances.pop(prefab_id.prefab_id)

    def remove_instance(self, instance_id):
        self.mesh_instances[instance_id.prefab_id].pop(instance_id.instance_id)

    def get_prefab_length(self):
        return len(self.mesh_prefabs)

    def get_instance_length(self, prefab_id):
        return len(self.mesh_instances[prefab_id.prefab_id])

    def number_vertices(self):
        return self.mesh_core.number_vertices

    def number_elements(self):
        return self.mesh_core.number_elements
    
    def bind_vertex_attributes(self):
        self.mesh_core.bind_buffers()

    def update_vertices(self, vertices):
        self.mesh_core.update_vertices(vertices)

    def __iter__(self):
        iterators = []
        for prefab_id, prefab in self.mesh_prefabs.items():
            count_instances = len(self.mesh_instances[prefab_id])
            cores = [self.mesh_core] * count_instances
            prefabs = [prefab] * count_instances
            instances = self.mesh_instances[prefab_id].values()
            iterators.append(zip(cores, prefabs, instances))
        return chain(*iterators)

#################################################################################################
