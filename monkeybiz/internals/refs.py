from __future__ import absolute_import

from .structs import Py_ssize_t


__all__ = ('Py_INCREF', 'Py_DECREF', 'get_refcount')


def Py_INCREF(o):
    ref = Py_ssize_t.from_address(id(o))
    ref.value += 1


def Py_DECREF(o):
    ref = Py_ssize_t.from_address(id(o))
    ref.value -= 1


def get_refcount(address):
    return Py_ssize_t.from_address(address).value
