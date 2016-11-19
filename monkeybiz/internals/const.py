from __future__ import absolute_import


__all__ = ('Py_TPFLAGS',)


class Py_TPFLAGS(object):

    # PyBufferProcs contains bf_getcharbuffer
    HAVE_GETCHARBUFFER = (1 << 0)

    # PySequenceMethods contains sq_contains
    HAVE_SEQUENCE_IN = (1 << 1)

    # This is here for backwards compatibility.  Extensions that use the old GC
    # API will still compile but the objects will not be tracked by the GC.
    GC = 0  # used to be (1 << 2)

    # PySequenceMethods and PyNumberMethods contain in-place operators
    HAVE_INPLACEOPS = (1 << 3)

    # PyNumberMethods do their own coercion
    CHECKTYPES = (1 << 4)

    # tp_richcompare is defined
    HAVE_RICHCOMPARE = (1 << 5)

    # Objects which are weakly referencable if their tp_weaklistoffset is >0
    HAVE_WEAKREFS = (1 << 6)

    # tp_iter is defined
    HAVE_ITER = (1 << 7)

    # New members introduced by Python 2.2 exist
    HAVE_CLASS = (1 << 8)

    # Set if the type object is dynamically allocated
    HEAPTYPE = (1 << 9)

    # Set if the type allows subclassing
    BASETYPE = (1 << 10)

    # Set if the type is 'ready' -- fully initialized
    READY = (1 << 12)

    # Set while the type is being 'readied', to prevent recursive ready calls
    READYING = (1 << 13)

    # Objects support garbage collection (see objimp.h)
    HAVE_GC = (1 << 14)

    # Objects support nb_index in PyNumberMethods
    HAVE_INDEX = (1 << 17)

    # Objects support type attribute cache
    HAVE_VERSION_TAG = (1 << 18)
    VALID_VERSION_TAG = (1 << 19)

    # Type is abstract and cannot be instantiated
    IS_ABSTRACT = (1 << 20)

    # Has the new buffer protocol
    HAVE_NEWBUFFER = (1 << 21)

    # These flags are used to determine if a type is a subclass.
    INT_SUBCLASS = (1 << 23)
    LONG_SUBCLASS = (1 << 24)
    LIST_SUBCLASS = (1 << 25)
    TUPLE_SUBCLASS = (1 << 26)
    STRING_SUBCLASS = (1 << 27)
    UNICODE_SUBCLASS = (1 << 28)
    DICT_SUBCLASS = (1 << 29)
    BASE_EXC_SUBCLASS = (1 << 30)
    TYPE_SUBCLASS = (1 << 31)
