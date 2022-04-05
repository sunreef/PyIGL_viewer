import os
import numpy as np
import igl
from PyQt5.QtWidgets import QApplication
from PyIGL_viewer import Viewer


script_folder = os.path.dirname(__file__)
path_to_obj_file = os.path.join(script_folder, "assets", "cube.obj")
vertices, faces = igl.read_triangle_mesh(path_to_obj_file)

viewer_app = QApplication(["IGL viewer"])
viewer = Viewer()
viewer.show()

# The stretch values give the relative size of the different viewer widgets
# By setting them all to 1, we make sure our widgets all have the same dimensions.
viewer.set_column_stretch(0, 1)
viewer.set_column_stretch(1, 1)
viewer.set_row_stretch(0, 1)
viewer.set_row_stretch(1, 1)


def screenshot_function():
    viewer.save_screenshot(os.path.join("screenshot.png"))


# Linking all cameras means that all widgets will have the same point of view.
def toggle_linking():
    if viewer.linked_cameras:
        viewer.unlink_all_cameras()
    else:
        viewer.link_all_cameras()


viewer.add_ui_button("Take Screenshot", screenshot_function)
viewer.add_ui_button("Toggle Camera Linking", toggle_linking)

viewer_widgets = [
    viewer.add_viewer_widget(index / 2, index % 2)[0] for index in range(4)
]
for widget in viewer_widgets:
    widget.show()
    widget.link_light_to_camera(True)
viewer.link_all_cameras()


def display_mesh(index, vertices, faces):
    viewer_widget = viewer_widgets[index]
    mesh_index = viewer_widget.add_mesh(vertices, faces)
    mesh_prefab_index = viewer_widget.add_mesh_prefab(mesh_index, "default")
    instance_index = viewer_widget.add_mesh_instance(
        mesh_prefab_index, np.eye(4, dtype="f")
    )
    viewer_widget.add_wireframe(instance_index)


for index in range(0, 4):
    display_mesh(index, vertices, faces)

viewer_app.exec()
