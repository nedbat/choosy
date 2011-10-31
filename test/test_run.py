"""Tests for run.py"""

import os.path
import sys
import unittest

from run import Checker, run_python


class CheckerTest(unittest.TestCase):
    """Test the run.Checker context mananger class."""

    def test_success(self):
        c = Checker()
        try:
            with c.expect("This should work"):
                pass
        except Checker.Done:
            self.fail("Shouldn't have raised Done here.")
        self.assertEqual(c.results, [('OK', "This should work")])

    def test_failure(self):
        c = Checker()
        try:
            with c.expect("This should work"):
                c.fail("It failed!")
                self.fail("We shouldn't have run past a c.fail")
            self.fail("We shouldn't have continued after a failed c.should")
        except Checker.Done:
            pass
        self.assertEqual(c.results, [('FAIL', "This should work", "It failed!")])

    def test_failure_with_continue_on_fail(self):
        c = Checker()
        try:
            with c.expect("This should work", continue_on_fail=True):
                c.fail("It failed!")
                self.fail("We shouldn't have run past a c.fail")
            with c.expect("Also this one"):
                pass
        except Checker.Done:
            self.fail("Shouldn't have raised Done here.")
        self.assertEqual(c.results, [('FAIL', "This should work", "It failed!"), ('OK', "Also this one")])

    def test_test(self):
        c = Checker()
        try:
            with c.expect("This should definitely work"):
                c.test(True, "This one was ok")
                c.test(False, "Oops, this was bad")
                raise Exception("Shouldn't have gotten to here")
        except Checker.Done:
            pass
        self.assertEqual(c.results, [('FAIL', "This should definitely work", "Oops, this was bad")])

    def test_error(self):
        class MyException(Exception): 
            pass
        c = Checker()
        saw_exc = False
        try:
            with c.expect("Everything will be fine"):
                raise MyException("It wasn't fine!")
        except Checker.Done:
            pass
        except MyException:
            saw_exc = True
        self.assertEqual(c.results, [('ERROR', "Everything will be fine", "It wasn't fine!")])
        self.assertEqual(saw_exc, True)


class RunPythonTest(unittest.TestCase):
    def test_output(self):
        out, res = run_python("""print 'hello!'""", "")
        self.assertEqual(out, "hello!\n")

    def test_syntax_error_in_user_code(self):
        out, res = run_python("""a = 1'hello'""", "")
        self.assertIn("""1'hello'""", out)
        self.assertIn("SyntaxError", out)

    def test_error_in_check_code(self):
        out, res = run_python("""a = 17""", """1'hello'""")
        self.assertEqual("", out)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], "ERROR")
        self.assertIn("1'hello'", res[0][2])
        self.assertIn("SyntaxError", res[0][2])
