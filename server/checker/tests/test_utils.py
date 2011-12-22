"""Tests for utils.py"""

import os.path
import sys
import unittest

from checker.utils import patchattr, isolated_modules, tempdir, change_dir

class Generic(object):
    """An object we can use generically in tests."""
    pass


class PatchAttrTest(unittest.TestCase):
    """Tests of the patchattr(obj, attr, val) context manager."""

    def test_patched(self):
        # Just regular patching with successful code works.
        o = Generic()
        o.a = 17
        o.b = 23
        self.assertEqual(o.a, 17)
        self.assertEqual(o.b, 23)
        with patchattr(o, 'a', 47) as newa:
            self.assertEqual(o.a, 47)
            self.assertEqual(newa, 47)
            self.assertEqual(o.b, 23)
        self.assertEqual(o.a, 17)
        self.assertEqual(o.b, 23)

    def test_patched_with_exception(self):
        # Patching and unpatching work even in the presence of exceptions.
        o = Generic()
        o.a = 17
        o.b = 23
        self.assertEqual(o.a, 17)
        self.assertEqual(o.b, 23)
        try:
            with patchattr(o, 'a', 47) as newa:
                self.assertEqual(o.a, 47)
                self.assertEqual(newa, 47)
                self.assertEqual(o.b, 23)
                raise ValueError("OMG!")
        except ValueError:
            pass
        self.assertEqual(o.a, 17)
        self.assertEqual(o.b, 23)

class IsolatedModulesTest(unittest.TestCase):
    def test_isolated(self):
        # pickletools is just a random rarely-used module to test with.
        assert 'pickletools' not in sys.modules
        with isolated_modules():
            assert 'pickletools' not in sys.modules
            import pickletools  # something we haven't had before
            assert 'pickletools' in sys.modules
        assert 'pickletools' not in sys.modules

    def test_isolated_with_exception(self):
        # pickletools is just a random rarely-used module to test with.
        assert 'pickletools' not in sys.modules
        try:
            with isolated_modules():
                assert 'pickletools' not in sys.modules
                import pickletools  # something we haven't had before
                assert 'pickletools' in sys.modules
                raise ValueError("OMG!")
        except ValueError:
            pass
        assert 'pickletools' not in sys.modules

class TempDirTest(unittest.TestCase):
    def test_tempdir(self):
        with tempdir(prefix="testing123") as td:
            assert os.path.exists(td)
            assert os.path.isdir(td)
        assert not os.path.exists(td)

    def test_tempdir_with_exception(self):
        try:
            with tempdir(prefix="testing123") as td:
                assert os.path.exists(td)
                assert os.path.isdir(td)
                raise ValueError("OMG!")
        except ValueError:
            pass
        assert not os.path.exists(td)


class ChangeDirTest(unittest.TestCase):
    def test_changedir(self):
        then = os.getcwd()
        with tempdir(prefix="test_changedir") as td:
            with change_dir(td):
                here = os.getcwd()
                self.assertNotEqual(then, here)
        now = os.getcwd()
        self.assertEqual(now, then)

    def test_changedir_with_exception(self):
        then = os.getcwd()
        with tempdir(prefix="test_changedir") as td:
            try:
                with change_dir(td):
                    here = os.getcwd()
                    self.assertNotEqual(then, here)
                    raise ValueError("No way!")
            except ValueError:
                pass
        now = os.getcwd()
        self.assertEqual(now, then)

