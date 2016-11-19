from __future__ import absolute_import

import ctypes

from .const import Py_TPFLAGS
from .refs import Py_INCREF, Py_DECREF
from .structs import c_typeobj


class Skip(Exception):
    pass


def pmerge(acc, to_merge):
    remain = [0 for l in to_merge]
    again = True
    while again:
        again = False
        empty_cnt = 0
        for i, cur_list in enumerate(to_merge):
            try:
                if remain[i] >= len(cur_list):
                    empty_cnt += 1
                    continue
                candidate = cur_list[remain[i]]
                for j, j_lst in enumerate(to_merge):
                    if candidate in j_lst[(remain[j] + 1):]:
                        raise Skip
                acc.append(candidate)
                for j, j_lst in enumerate(to_merge):
                    if remain[j] < len(j_lst) and j_lst[remain[j]] == candidate:
                        remain[j] += 1
            except Skip:
                continue
            else:
                again = True

    if empty_cnt != len(to_merge):
        raise Exception("mro order issue")


def mro_implementation(cls):
    type = c_typeobj(cls)

    # Find a superclass linearization that honors the constraints
    # of the explicit lists of bases and the constraints implied by
    # each base class.
    #
    # to_merge is a list of lists, where each list is a superclass
    # linearization implied by a base class.  The last element of
    # to_merge is the declared list of bases.

    bases = type.tp_bases
    to_merge = []
    for base in bases:
        c_base = c_typeobj(base)
        try:
            c_base.tp_mro
        except:
            raise TypeError("Cannot extend an incomplete type '%s'" % c_base.tp_name)
        base_mro = list(c_base.tp_mro)
        to_merge.append(base_mro)

    to_merge.append(list(bases))

    result = [cls]
    pmerge(result, to_merge)
    return result


def type_mro_modified(type, bases):
    if not type.tp_flags & Py_TPFLAGS.HAVE_VERSION_TAG:
        return
    clear = False
    for base in bases:
        c_base = c_typeobj(base)
        has_version_tag = c_base.tp_flags & Py_TPFLAGS.HAVE_VERSION_TAG
        is_subtype = ctypes.pythonapi.PyType_IsSubtype(
            ctypes.byref(type), ctypes.byref(c_base))
        if not has_version_tag or not is_subtype:
            clear = True
            break

    if clear:
        type.tp_flags &= ~(Py_TPFLAGS.HAVE_VERSION_TAG |
                           Py_TPFLAGS.VALID_VERSION_TAG)


def type_subclasses(type):
    cls_list = []
    try:
        raw = type.tp_subclasses
    except:
        return cls_list
    for weakref in raw:
        ref = weakref()
        if ref is not None:
            cls_list.append(ref)
    return cls_list


def mro_hierarchy(cls, temp):
    type = c_typeobj(cls)

    old_mro = mro_internal(cls)
    if old_mro is False:
        return old_mro

    new_mro = type.tp_mro

    if old_mro:
        mro_tuple = (type, new_mro, old_mro)
    else:
        mro_tuple = (type, new_mro)

    # Py_DECREF(mro_tuple)
    Py_DECREF(old_mro)

    temp.append(mro_tuple)

    subclasses = cls.__subclasses__()
    for subclass in subclasses:
        mro_hierarchy(subclass, temp)


def mro_internal(cls):
    type = c_typeobj(cls)

    old_mro = getattr(cls, '__mro__', None)
    new_mro = tuple(mro_implementation(cls))
    if cls.__mro__ != old_mro:
        return False
    Py_INCREF(new_mro)
    type.tp_mro = new_mro

    type_mro_modified(type, type.tp_mro)
    # corner case: the super class might have been hidden from the custom MRO
    type_mro_modified(type, type.tp_bases)

    ctypes.pythonapi.PyType_Modified(ctypes.byref(type))
    # Py_DECREF(old_mro)
    return old_mro
