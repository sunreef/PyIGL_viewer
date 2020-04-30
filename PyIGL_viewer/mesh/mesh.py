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

        self.element_size = faces.shape[1]
        if self.element_size == 1:
            self.drawing_mode = gl.GL_POINTS 
        elif self.element_size == 3:
            self.drawing_mode = gl.GL_TRIANGLES 
        else:
            self.drawing_mode = gl.GL_LINES 
            new_faces = np.zeros((self.number_elements, 2 * self.element_size), dtype=np.int32)
            for s in range(self.element_size):
                new_faces[:, 2 * s] = faces[:, s]
                new_faces[:, 2 * s - 1] = faces[:, s]
            faces = new_faces
            self.element_size *= 2

        self.elements = faces.reshape((-1,))
        flat_vertices = self.flatten_vertex_attribute(vertices)
        self.flat_vertex_buffer = gl.arrays.vbo.VBO(flat_vertices)

    def flatten_vertex_attribute(self, attribute):
        flat_attribute = attribute[self.elements]
        return flat_attribute

    def flatten_face_attribute(self, attribute):
        flat_attribute = np.repeat(attribute, self.element_size, axis=0)
        return flat_attribute

    def bind_buffers(self):
        gl.glEnableVertexAttribArray(0)
        self.flat_vertex_buffer.bind()
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)

    def update_vertices(self, vertices):
        flat_vertices = self.flatten_vertex_attribute(vertices)
        self.flat_vertex_buffer.set_array(flat_vertices)

#################################################################################################
        
#################################################################################################
# A mesh prefab contains a shader program as well as the necessary vertex attributes and uniform values for this shader.
# It defines the appearance of a given mesh.

class GlMeshPrefabId:
    def __init__(self, core_id):
        self.core_id = core_id.core_id
        self.prefab_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + str(uuid.uuid4())

class GlMeshPrefab:
    def __init__(self, attributes, uniforms, shader, fill, copy_from=None):
        self.fill = fill
        self.shader = shader
        self.attributes = attributes
        self.uniforms = uniforms

        self.vertex_buffers = {}
        for attribute in self.shader.attributes:
            if not attribute in attributes:
                if copy_from is not None and attribute in copy_from.vertex_buffers:
                    self.vertex_buffers[attribute] = copy_from.vertex_buffers[attribute]
                else:
                    raise ValueError(f'Attribute {attribute} missing from mesh prefab data')
            else:
                self.vertex_buffers[attribute] = (gl.arrays.vbo.VBO(attributes[attribute]), attributes[attribute].shape[1])

        self.uniform_values = {}
        for uniform in self.shader.uniforms:
            if not uniform in uniforms:
                if copy_from is not None and uniform in copy_from.uniform_values:
                    self.uniform_values[uniform] = copy_from.uniform_values[uniform]
                else:
                    raise ValueError(f'Uniform {uniform} missing from mesh prefab data')
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

    def update_uniform(self, name, value):
        self.uniform_values[name] = value

    def update_attribute(self, name, value):
        self.vertex_buffers[name] = (gl.arrays.vbo.VBO(value), value.shape[1])

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

    def add_prefab(self, prefab_id, vertex_attributes, face_attributes, uniforms, shader, fill, copy_from):
        attributes = {}
        for key in vertex_attributes:
            attributes[key] = self.mesh_core.flatten_vertex_attribute(vertex_attributes[key])
        for key in face_attributes:
            attributes[key] = self.mesh_core.flatten_face_attribute(face_attributes[key])

        self.mesh_prefabs[prefab_id.prefab_id] = GlMeshPrefab(attributes, uniforms, shader, fill, copy_from)
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

    def update_prefab_vertex_attribute(self, prefab_id, name, value):
        flat_value = self.mesh_core.flatten_vertex_attribute(value)
        self.get_prefab(prefab_id).update_attribute(name, flat_value)

    def update_prefab_face_attribute(self, prefab_id, name, value):
        flat_value = self.mesh_core.flatten_face_attribute(value)
        self.get_prefab(prefab_id).update_attribute(name, flat_value)

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
