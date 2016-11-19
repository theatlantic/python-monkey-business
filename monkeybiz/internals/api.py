from __future__ import absolute_import

import ctypes
from ctypes import py_object
import os
import sys

from .structs import Py_ssize_t


# Load our own copy of the python library, so that changes to
# argtypes and restype don't have global effects
if os.name in ("nt", "ce"):
    pythonapi = ctypes.PyDLL("python dll", None, sys.dllhandle)
elif sys.platform == "cygwin":
    pythonapi = ctypes.PyDLL("libpython%d.%d.dll" % sys.version_info[:2])
else:
    pythonapi = ctypes.PyDLL(None)


pythonapi.PyWeakref_NewRef.argtypes = [py_object, py_object]
pythonapi.PyWeakref_NewRef.restype = py_object

pythonapi.PySequence_DelItem.argtypes = [py_object, Py_ssize_t]
pythonapi.PySequence_DelItem.restype = ctypes.c_int
