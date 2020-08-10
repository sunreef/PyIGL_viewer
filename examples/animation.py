import os
import threading
import time
import numpy as np
import igl
from PyQt5.QtWidgets import QApplication
from PyIGL_viewer import Viewer

script_folder = os.path.dirname(__file__)
path_to_obj_file = os.path.join(script_folder, 'assets', 'cube.obj')
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

def animate_func():
    global vertices, faces
    for t in range(1000):
        moved_vertices = vertices + t * 0.002 * np.ones_like(vertices)
        viewer_widget.update_mesh_vertices(mesh_index, moved_vertices.astype(np.float32))
        viewer_widget.update()
        time.sleep(0.02)

# This animation needs to run in its own thread to not block the rendering on the main thread.
def animate_func_async():
    animating_thread = threading.Thread(target=animate_func, args=())
    animating_thread.start()

viewer.add_ui_button("Animate", animate_func_async)


# Add the wireframe for our mesh 
viewer_widget.add_wireframe(instance_index, line_color=np.array([0.1, 0.1, 0.1]))

# Launch the Qt application
viewer_app.exec()
