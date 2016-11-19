from __future__ import absolute_import

import ctypes

from .api import pythonapi
from .const import Py_TPFLAGS  # noqa
from .refs import Py_INCREF, Py_DECREF, get_refcount  # noqa
from .typeobject import type_set_bases, set_type, override_type, force_heap_type  # noqa
from .structs import Py_ssize_t, PyObject, PyTypeObject, c_typeobj  # noqa


DictProxyType = type(type.__dict__)


class DictProxy(PyObject):
    _fields_ = [('dict', ctypes.POINTER(PyObject))]


def mutable_class_dict(cls):
    """Returns a mutable instance of ``cls.__dict__``"""
    d = getattr(cls, '__dict__', None)
    if d is None:
        raise TypeError('given class does not have a dictionary')
    if not isinstance(d, DictProxyType):
        return d

    dp = DictProxy.from_address(id(d))
    ns = {}
    pythonapi.PyDict_SetItem(
        ctypes.py_object(ns), ctypes.py_object(cls.__name__), dp.dict)
    return ns[cls.__name__]
