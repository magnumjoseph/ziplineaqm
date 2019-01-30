from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

EXT_MODULES = [Extension("_equities", ["_equities.pyx"], include_dirs=[numpy.get_include()])]

setup(
    name = 'equities' ,
    cmdclass = {'build_ext': build_ext},
    ext_modules = EXT_MODULES
)
