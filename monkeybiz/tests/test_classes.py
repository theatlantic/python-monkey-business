import unittest

import monkeybiz


def complex_builtin_patch():
    """
    Patches the ``complex`` builtin , adding an ``@property(is_patched)`` and
    patching complex.conjugate to always return 0 for the real part.

    Why ``complex``? It's very unlikely to be used by the test runner (or
    anything else in the stdlib for that matter), so the chance that patching
    it causes unintended consequences is low.
    """
    class ComplexPatch(monkeybiz.patch_class(complex)):
        patched = True

        @property
        def is_patched(self):
            return True

        def conjugate(self):
            conj = super(ComplexPatch, self).conjugate()
            return complex(0, conj.imag)

    return ComplexPatch


class PatchClassesTestCase(unittest.TestCase):

    def test_patch_builtin_bases(self):
        ComplexPatch = complex_builtin_patch()
        self.assertEqual(complex.__bases__, (object,))
        try:
            ComplexPatch.patch()
            self.assertNotEqual(complex.__bases__, (object,))
        finally:
            ComplexPatch.unpatch()
        self.assertEqual(complex.__bases__, (object,))

    def test_patch_builtin(self):
        ComplexPatch = complex_builtin_patch()
        num = (-1 - 1j)
        try:
            ComplexPatch.patch()
            self.assertTrue(getattr((-1 - 3j), 'patched', False))
            self.assertEqual((-1 - 2j).conjugate(), 2j)
            self.assertEqual(num.conjugate(), 1j)
        finally:
            ComplexPatch.unpatch()
        self.assertEqual(num.conjugate(), -1 + 1j)
        self.assertEqual((-1 - 4j).conjugate(), (-1 + 4j))
