import gc
import sys
import unittest

from monkeybiz.internals import mutable_class_dict, set_type, type_set_bases


def a_factory(set_b_base=False):
    base = b_factory() if set_b_base else object
    return type("A", (base,), {"name": lambda self: "A"})


def b_factory():
    return type("A", (object,), {"name": lambda self: "B"})


def c_factory():
    class C_Base(object):
        """
        A trivial base class, because overriding __bases__ is different (and more
        complicated) for classes that extend only ``object``"""
    return type("C", (C_Base,), {"name": lambda self: "C"})


def xyz_factory():
    class X(object):
        def name(self): return "X"  # noqa: E704

    class Y(X):
        def name(self): return "Y"  # noqa: E704
        def super_plus_name(self):  # noqa: E306
            """Returns XY"""
            return "%s%s" % (super(Y, self).name(), self.name())

    class Z(Y):
        def name(self): return "Z"  # noqa: E704
        def super_plus_name(self):  # noqa: E306
            """Returns XYZ"""
            return "%s%s" % (super(Z, self).name(), self.name())

    return X, Y, Z


class InternalsTestCase(unittest.TestCase):

    def test_cls_dict_mutate(self):
        A = a_factory()
        a_dict = mutable_class_dict(A)
        a_dict['foo'] = 'bar'
        self.assertIn('foo', A.__dict__)

    def test_set_type(self):
        A = a_factory()
        B = b_factory()
        a = A()
        set_type(a, B)
        self.assertEqual(type(a), B)

    def test_set_bases(self):
        A = a_factory()
        B = b_factory()
        type_set_bases(A, (B,))
        self.assertEqual(A.__bases__, (B,))

    def test_set_bases_mro(self):
        A = a_factory()
        B = b_factory()
        type_set_bases(A, (B,))
        self.assertEqual(A.__mro__, (A, B, object))

    def test_set_bases_subclasses(self):
        A = a_factory()
        B = b_factory()
        type_set_bases(A, (B,))
        self.assertEqual(B.__subclasses__(), [A])

    def test_set_bases_refcount(self):
        def normally_set_base():
            return a_factory(set_b_base=True)

        A_normal = normally_set_base()
        gc.collect()
        normal_ref_count = sys.getrefcount(A_normal.__bases__[0])

        def patch_set_base():
            A = a_factory()
            B = b_factory()
            type_set_bases(A, (B,))
            return A

        A_patch = patch_set_base()

        gc.collect()
        patch_ref_count = sys.getrefcount(A_patch.__bases__[0])

        self.assertEqual(normal_ref_count, patch_ref_count)

    def test_set_bases_mro_refcount(self):
        def normally_set_base():
            return a_factory(set_b_base=True)

        A_normal = normally_set_base()
        gc.collect()
        normal_ref_count = sys.getrefcount(A_normal.__mro__)

        def patch_set_base():
            A = a_factory()
            B = b_factory()
            type_set_bases(A, (B,))
            return A

        A_patch = patch_set_base()

        gc.collect()
        patch_ref_count = sys.getrefcount(A_patch.__mro__)
        self.assertEqual(normal_ref_count, patch_ref_count)

    def test_set_multiple_bases(self):
        B = b_factory()
        C = c_factory()
        X, Y, Z = xyz_factory()
        type_set_bases(Z, (B, C))
        self.assertEqual(Z.__bases__, (B, C))

    def test_set_multiple_bases_mro(self):
        B = b_factory()
        C = c_factory()
        C_Base = C.__bases__[0]
        X, Y, Z = xyz_factory()
        type_set_bases(Z, (B, C))
        self.assertEqual(Z.__mro__, (Z, B, C, C_Base, object))

    def test_set_multiple_bases_subclasses(self):
        B = b_factory()
        C = c_factory()
        C_Base = C.__bases__[0]
        X, Y, Z = xyz_factory()
        type_set_bases(Z, (B, C_Base))
        self.assertEqual(C_Base.__subclasses__(), [C, Z])

    def test_subclasses_lost_ref(self):
        X = type("X", (object,), {})
        Y = type("Y", (X,), {})

        def add_z_base():
            Z = type("Z", (object,), {})
            type_set_bases(Z, (X,))

        add_z_base()
        gc.collect()
        self.assertEqual(X.__subclasses__(), [Y])
