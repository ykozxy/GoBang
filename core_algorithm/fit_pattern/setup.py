from distutils.core import setup

from Cython.Build import cythonize

setup(ext_modules=cythonize("fit_pattern.pyx"))
