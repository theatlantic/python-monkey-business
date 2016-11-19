from __future__ import absolute_import

import ctypes
import sys

import six


if six.PY3:
    Py_ssize_t = ctypes.c_ssize_t
else:
    if hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
        Py_ssize_t = ctypes.c_int64
    else:
        Py_ssize_t = ctypes.c_int


__all__ = ('Py_ssize_t', 'PyObject', 'PyTypeObject', 'c_typeobj')


class PyObject(ctypes.Structure):
    pass


PyObject_fields = [
    ('ob_refcnt', Py_ssize_t),
    ('ob_type', ctypes.py_object),
]

if hasattr(sys, 'getobjects'):
    PyObject_fields = [
        ('_ob_next', ctypes.POINTER(PyObject)),
        ('_ob_prev', ctypes.POINTER(PyObject)),
    ] + PyObject_fields


PyObject._fields_ = PyObject_fields


class PyTypeObject(ctypes.Structure):
    pass


PyTypeObject._fields_ = [
    ('ob_refcnt', Py_ssize_t),
    ('ob_type', ctypes.c_void_p),
    ('ob_size', Py_ssize_t),
    ('tp_name', ctypes.c_char_p),
    ('tp_basicsize', Py_ssize_t),
    ('tp_itemsize', Py_ssize_t),
    ('tp_dealloc', ctypes.c_void_p),
    ('tp_print', ctypes.c_void_p),
    ('tp_getattr', ctypes.c_void_p),
    ('tp_setattr', ctypes.c_void_p),
    # tp_compare is tp_as_async in python 3.5, tp_reserved in earlier python 3
    ('tp_compare', ctypes.c_void_p),
    ('tp_repr', ctypes.c_void_p),
    ('tp_as_number', ctypes.c_void_p),
    ('tp_as_sequence', ctypes.c_void_p),
    ('tp_as_mapping', ctypes.c_void_p),
    ('tp_hash', ctypes.c_void_p),
    ('tp_call', ctypes.c_void_p),
    ('tp_str', ctypes.c_void_p),
    ('tp_getattro', ctypes.c_void_p),
    ('tp_setattro', ctypes.c_void_p),
    ('tp_as_buffer', ctypes.c_void_p),
    ('tp_flags', ctypes.c_long if six.PY2 else ctypes.c_ulong),
    ('tp_doc', ctypes.c_char_p),
    ('tp_traverse', ctypes.c_void_p),
    ('tp_clear', ctypes.c_void_p),
    ('tp_richcompare', ctypes.c_void_p),
    ('tp_weaklistoffset', Py_ssize_t),
    ('tp_iter', ctypes.c_void_p),
    ('tp_iternext', ctypes.c_void_p),
    ('tp_methods', ctypes.c_void_p),
    ('tp_members', ctypes.c_void_p),
    ('tp_getset', ctypes.c_void_p),
    ('tp_base', ctypes.py_object),
    ('tp_dict', ctypes.py_object),
    ('tp_descr_get', ctypes.c_void_p),
    ('tp_descr_set', ctypes.c_void_p),
    ('tp_dictoffset', Py_ssize_t),
    ('tp_init', ctypes.c_void_p),
    ('tp_alloc', ctypes.c_void_p),
    ('tp_new', ctypes.c_void_p),
    ('tp_free', ctypes.c_void_p),
    ('tp_is_gc', ctypes.c_void_p),
    ('tp_bases', ctypes.py_object),
    ('tp_mro', ctypes.py_object),
    ('tp_cache', ctypes.py_object),
    ('tp_subclasses', ctypes.py_object),
    ('tp_weaklist', ctypes.py_object),
    ('tp_del', ctypes.c_void_p),
    ('tp_version_tag', ctypes.c_uint),
]


def c_typeobj(t):
    return PyTypeObject.from_address(id(t))
