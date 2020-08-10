import os
import numpy as np
import igl
from PyQt5.QtWidgets import QApplication
from PyIGL_viewer import Viewer

script_folder = os.path.dirname(__file__)
path_to_obj_file = os.path.join(script_folder, 'assets', 'cube.obj')
# Path to your OBJ file stored in path_to_obj_file 
vertices, faces = igl.read_triangle_mesh(path_to_obj_file)

bbox_min = np.min(vertices, axis=0)
bbox_max = np.max(vertices, axis=0)
scaling_factor = 1.0 / np.max(bbox_max - bbox_min)
center = np.mean(vertices, axis=0)
vertices -= center
vertices *= scaling_factor

# Create Qt application and our viewer window
viewer_app = QApplication(["IGL viewer"])
viewer = Viewer()
viewer.show()
viewer.set_column_stretch(0, 1)

# Add a viewer widget to visualize 3D meshes to our viewer window
viewer_widget, _ = viewer.add_viewer_widget(0, 0)
viewer_widget.show()

# Add a screenshot button
def screenshot_function():
    viewer.save_screenshot(os.path.join('screenshot.png'))
viewer.add_ui_button("Take Screenshot", screenshot_function)

# Add a mesh to our viewer widget
# This requires three steps:
# - Adding the mesh vertices and faces
# - Adding a mesh prefab that contains shader attributes and uniform values
# - Adding an instance of our prefab whose position is defined by a model matrix
mesh_index = viewer_widget.add_mesh(vertices, faces)
mesh_prefab_index = viewer_widget.add_mesh_prefab(mesh_index, 'default')
instance_index = viewer_widget.add_mesh_instance(mesh_prefab_index, np.eye(4, dtype='f'))

# Add the wireframe for our mesh 
# The wireframe shader expect a uniform attribute called lineColor that specifies the color of the wireframe lines.
viewer_widget.add_wireframe(instance_index, line_color=np.array([0.1, 0.1, 0.1]))

# Launch the Qt application
viewer_app.exec()
