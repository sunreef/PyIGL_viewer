from .viewer import ViewerWidget

if __name__ == "__main__":
    import numpy as np
    import sys
    from PyQt5.QtWidgets import QOpenGLWidget, QApplication
    app = QApplication([])
    widget = ViewerWidget()

    vertices = np.array([[0,1,0.0],[1, 0, 0.0],[0, 0, 0.0]], dtype='f')
    normals = np.array([[0,0,1],[0, 0, 1],[0, 0, 1]], dtype='f')
    tex_coords = np.array([[0,0],[1, 1],[0, 1]], dtype='f')
    indices = np.array([[0,1,2]], dtype=np.int32)
    widget.add_mesh(vertices, indices, normals=normals, texture_coords=tex_coords)

    vertices = np.array([[0,-1,0.0],[-1, 0, 0.0],[0, 0, 0.0]], dtype='f')
    normals = np.array([[0,0,1],[1, 0, 0],[0, 1, 0]], dtype='f')
    tex_coords = np.array([[0,0],[1, 1],[0, 1]], dtype='f')
    indices = np.array([[0,1,2]], dtype=np.int32)
    widget.add_mesh(vertices, indices, normals=normals, texture_coords=tex_coords)

    widget.show()
    sys.exit(app.exec())


