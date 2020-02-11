from setuptools import setup, find_packages

setup(name='IGL_viewer',
      version='0.1',
      description='Python IGL viewer',
      long_description='Because sometimes Matplotlib is not enough.',
      url='https://TBD',
      classifiers=[
        'Programming Language :: Python :: 3.7',
      ],
      keywords='igl viewer opengl mesh display',
      author='Victor Cornillère',
      author_email='covictor@inf.ethz.ch',
      packages=find_packages(),
      install_requires=[
          "PyOpenGL", 
          "glfw",
      ],
      include_package_data=True,
      zip_safe=False)
