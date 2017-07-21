import functools
import types

import six

from .internals import mutable_class_dict, type_set_bases, override_type


def patch_class(target_cls):
    """
    Used to create a class that, when extended, turns the extending class
    into a context manager that injects its attributes onto the ``target_cls``,
    while moving any overridden attributes into a newly created base class
    (so that they can be accessed with super()).

    Example usage:

    .. code-block:: python

        class A(object):
            def name(self):
                return 'A'


        class PatchedA(monkeybiz.patch_class(A)):
            def name(self):
                return 'Patched %s!' % super(PatchedA, self).name()

        a = A()

        print(a.name())  # Prints 'A'

        with PatchedA:
            print(a.name())  # Prints 'Patched A!'

        print(a.name())  # Prints 'A'
    """
    class_dict = mutable_class_dict(target_cls)
    orig_dict = {}
    patch_attrs = {}

    class PatchBase(object):
        pass

    # A wrapper around methods so that self.__class__ gets redefined,
    # allowing super() calls to work.
    def method_wrapper(f, new_cls):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            if isinstance(f, classmethod) and self is target_cls:
                return f(new_cls, *args, **kwargs)
            orig_type = type(self)
            with override_type(self, new_cls if orig_type is target_cls else orig_type):
                return f(self, *args, **kwargs)
        return wrapper

    class meta(type(target_cls)):

        def __new__(cls, name, bases, attrs):
            method_attrs = {}

            for k, v in six.iteritems(attrs):
                if k in ('__module__', '__doc__'):
                    continue
                if k in class_dict:
                    orig_dict[k] = class_dict[k]
                if isinstance(v, (types.FunctionType, classmethod)):
                    method_attrs[k] = v
                patch_attrs[k] = v

            patch_base = type('%sPatch' % name, (PatchBase,), orig_dict)
            bases = (patch_base,) + bases
            new_cls = super(meta, cls).__new__(cls, name, bases, attrs)
            for k, v in six.iteritems(method_attrs):
                patch_attrs[k] = method_wrapper(v, new_cls)
            return new_cls

        def patch(cls):
            patch_base_attrs = {}
            for k, v in six.iteritems(patch_attrs):
                if not hasattr(target_cls, k):
                    patch_base_attrs[k] = v
                else:
                    class_dict[k] = v

            patch_base = type("%sPatch" % target_cls.__name__, (PatchBase,), patch_base_attrs)
            type_set_bases(target_cls, (patch_base,) + target_cls.__bases__)

        def unpatch(cls):
            class_dict = mutable_class_dict(target_cls)
            for k, v in six.iteritems(patch_attrs):
                if k in class_dict:
                    del class_dict[k]
                if k in orig_dict:
                    class_dict[k] = orig_dict[k]
            bases = target_cls.__bases__
            reset_bases = tuple([b for b in bases if not issubclass(b, PatchBase)])
            type_set_bases(target_cls, reset_bases)

        def __enter__(cls):
            cls.patch()

        def __exit__(cls, exc_type, exc_value, traceback):
            cls.unpatch()

    return six.with_metaclass(meta, target_cls)
