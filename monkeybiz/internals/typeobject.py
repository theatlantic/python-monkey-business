from __future__ import absolute_import

import contextlib
import ctypes
from ctypes import py_object

import six

from .api import pythonapi
from .const import Py_TPFLAGS
from .mro import mro_hierarchy
from .refs import Py_INCREF, Py_DECREF
from .structs import PyObject, c_typeobj


NULL = py_object()


def add_subclass(base, cls):
    c_base = c_typeobj(base)
    subclasses_type = dict if six.PY3 else list
    try:
        subclasses = c_base.tp_subclasses
    except:
        subclasses = c_base.tp_subclasses = subclasses_type()
        Py_INCREF(subclasses)
    newobj = pythonapi.PyWeakref_NewRef(cls, NULL)
    if six.PY3:
        subclasses[id(cls)] = newobj
    else:
        for i in six.moves.range(len(subclasses) - 1, -1, -1):
            if subclasses[i]() is None:
                subclasses[i] = newobj
                return
        subclasses.append(newobj)


def remove_subclass(base, cls):
    c_base = c_typeobj(base)
    subclasses = c_base.tp_subclasses
    if six.PY3:
        try:
            del subclasses[id(cls)]
        except KeyError:
            pass
    else:
        for i in six.moves.range(len(subclasses) - 1, -1, -1):
            weakref = subclasses[i]
            ref = weakref()
            if ref is cls:
                pythonapi.PySequence_DelItem(subclasses, i)
                Py_DECREF(ref)
                return


def is_heap_type(cls):
    c_cls = c_typeobj(cls)
    return bool(c_cls.tp_flags & Py_TPFLAGS.HEAPTYPE)


@contextlib.contextmanager
def force_heap_type(cls):
    c_cls = c_typeobj(cls)
    heap_flag = (c_cls.tp_flags & Py_TPFLAGS.HEAPTYPE) ^ Py_TPFLAGS.HEAPTYPE
    c_cls.tp_flags |= heap_flag
    yield
    c_cls.tp_flags &= ~heap_flag


def get_tp_base(cls):
    c_cls = c_typeobj(cls)
    try:
        return c_cls.tp_base
    except ValueError:
        return None


def type_is_subtype_base_chain(a, b):
    while True:
        if a is b:
            return True
        a = get_tp_base(a)
        if a is None:
            break
    return b is object


def extra_ivars(cls, base):
    c_type = c_typeobj(cls)
    c_base = c_typeobj(base)
    t_size = c_type.tp_basicsize
    b_size = c_base.tp_basicsize

    sizeof_pyobj = ctypes.sizeof(ctypes.py_object)

    if c_type.tp_itemsize or c_base.tp_itemsize:
        return t_size != b_size or c_type.tp_itemsize != c_base.tp_itemsize

    if is_heap_type(cls):
        if c_type.tp_weaklistoffset and c_base.tp_weaklistoffset == 0:
            if c_type.tp_weaklistoffset + sizeof_pyobj == t_size:
                t_size -= sizeof_pyobj
        if c_type.tp_dictoffset and c_base.tp_dictoffset == 0:
            if c_type.tp_dictoffset + sizeof_pyobj == t_size:
                t_size -= sizeof_pyobj

    return t_size != b_size


def solid_base(cls):
    tp_base = get_tp_base(cls)
    if tp_base is None:
        base = object
    else:
        base = solid_base(tp_base)
    return cls if extra_ivars(cls, base) else base


def best_base(bases):
    base = None
    winner = None
    for base_i in bases:
        candidate = solid_base(base_i)
        if winner is None:
            winner = candidate
            base = base_i
        elif issubclass(winner, candidate):
            pass
        elif issubclass(candidate, winner):
            winner = candidate
            base = base_i
    return base


def type_set_bases(cls, new_bases):
    c_cls = c_typeobj(cls)

    if not isinstance(new_bases, tuple):
        raise TypeError(
            "can only assign tuple to %s.__bases__, not %s", (
                cls.__name__, type(new_bases).__name__))

    if len(new_bases) == 0:
        raise TypeError("can only assign non-empty tuple to %s.__bases__, not ()" % cls.__name__)

    for base in new_bases:
        if not isinstance(base, type):
            raise TypeError(
                "%s.__bases__ must be tuple of classes, not '%s'" % (
                    cls.__name__, type(base).__name__))
        base_mro = getattr(base, '__mro__', None)
        if issubclass(base, cls) or base_mro and type_is_subtype_base_chain(base, cls):
            raise TypeError("a __bases__ item causes an inheritance cycle")

    new_base = best_base(new_bases)

    Py_INCREF(new_bases)
    Py_INCREF(new_base)

    old_bases = c_cls.tp_bases
    old_base = get_tp_base(cls)

    c_cls.tp_bases = new_bases
    c_cls.tp_base = new_base

    temp = []
    mro_hierarchy(cls, temp)

    if c_cls.tp_bases == new_bases:
        for ob in (set(old_bases) - set(new_bases)):
            remove_subclass(ob, cls)
        for ob in (set(new_bases) - set(old_bases)):
            add_subclass(ob, cls)

        # super hacky, but allows updating of slots
        with force_heap_type(cls):
            cls.__bases__ = tuple(list(cls.__bases__))

    Py_DECREF(old_bases)
    Py_DECREF(old_base)


def set_type(obj, new_type):
    try:
        obj.__class__ = new_type
    except TypeError:
        old_type = obj.__class__
        if is_heap_type(new_type):
            Py_INCREF(new_type)
        c_obj = PyObject.from_address(id(obj))
        c_obj.ob_type = new_type
        if is_heap_type(old_type):
            Py_DECREF(old_type)


@contextlib.contextmanager
def override_type(obj, new_type):
    old_type = obj.__class__
    if old_type is new_type:
        yield
    else:
        try:
            set_type(obj, new_type)
            yield
        finally:
            set_type(obj, old_type)
