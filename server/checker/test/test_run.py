"""Tests for run.py"""

import os.path
import sys
import textwrap
import unittest

from checker.exerciser import Checker
from checker.run import run_python


class CheckerTest(unittest.TestCase):
    """Test the run.Checker context mananger class."""

    def test_success(self):
        c = Checker()
        try:
            with c.expect("This should work"):
                pass
        except Checker.Done:    # pragma: nocover
            self.fail("Shouldn't have raised Done here.")
        self.assertEqual(c.results, [('OK', "This should work")])

    def test_failure(self):
        c = Checker()
        try:
            with c.expect("This should work"):
                c.fail("It failed!")
                self.fail("We shouldn't have run past a c.fail")    # pragma: nocover
            self.fail("We shouldn't have continued after a failed c.should")    # pragma: nocover
        except Checker.Done:
            pass
        self.assertEqual(c.results, [('FAIL', "This should work", "It failed!")])

    def test_failure_with_continue_on_fail(self):
        c = Checker()
        try:
            with c.expect("This should work", continue_on_fail=True):
                c.fail("It failed!")
                self.fail("We shouldn't have run past a c.fail")    # pragma: nocover
            with c.expect("Also this one"):
                pass
        except Checker.Done:    # pragma: nocover
            self.fail("Shouldn't have raised Done here.")
        self.assertEqual(c.results, [('FAIL', "This should work", "It failed!"), ('OK', "Also this one")])

    def test_test(self):
        c = Checker()
        try:
            with c.expect("This should definitely work"):
                c.test(True, "This one was ok")
                c.test(False, "Oops, this was bad")
                raise Exception("Shouldn't have gotten to here")    # pragma: nocover
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
            raise Exception("Shouldn't get here")   # pragma: nocover
        except MyException:
            saw_exc = True
        self.assertEqual(c.results, [('ERROR', "Everything will be fine", "It wasn't fine!")])
        self.assertEqual(saw_exc, True)

    def test_quiet_expects(self):
        c = Checker()
        with c.expect("It isn't even worth mentioning.", quiet=True):
            pass
        with c.expect("Let's talk about this."):
            pass
        self.assertEqual(c.results, [('OK', "Let's talk about this.")])


class FunctionReturnsTest(unittest.TestCase):

    def simple(self, x):
        return x*2

    def test_simple(self):
        c = Checker()
        c.function_returns(self, 'simple', [(1, 2), (2, 4)])
        self.assertEqual(c.results, 
            [('OK', 'simple(1) &rarr; 2'), ('OK', 'simple(2) &rarr; 4')]
            )

    def test_no_such_function(self):
        c = Checker()
        with self.assertRaises(Checker.Done):
            c.function_returns(self, 'nothing', [(1, 2), (2, 4)])
        self.assertEqual(c.results, 
            [('FAIL', 'You should have a function named nothing', '')]
            )

    def test_not_callable(self):
        c = Checker()
        self.mylist = []
        with self.assertRaises(Checker.Done):
            c.function_returns(self, 'mylist', [(1, 2), (2, 4)])
        self.assertEqual(c.results,
            [('FAIL', 'You should have a function named mylist', '')]
            )

    def test_wrong_answers(self):
        c = Checker()
        c.function_returns(self, 'simple', [(1, 2), (2, 17), (3, 6)])
        self.assertEqual(c.results,
            [('OK', 'simple(1) &rarr; 2'),
             ('FAIL', 'simple(2) &rarr; 17', 'You returned 4'),
             ('OK', 'simple(3) &rarr; 6'),
            ])

    def add3(self, a, b, c):
        return a + b + c

    def test_multiple_arguments(self):
        c = Checker()
        c.function_returns(self, 'add3', [(1, 2, 3, 6), (1, 1, 1, 3), (10, 11, 12, 33)])
        self.assertEqual(c.results,
            [('OK', 'add3(1, 2, 3) &rarr; 6'),
             ('OK', 'add3(1, 1, 1) &rarr; 3'),
             ('OK', 'add3(10, 11, 12) &rarr; 33'),
            ])

    class Flake(Exception):
        pass

    def flaky(self, x):
        if x % 2:
            raise self.Flake("Oops")
        return x

    def test_flaky_function(self):
        c = Checker()
        c.function_returns(self, 'flaky', [(2, 2), (3, 3), (4, 4)])
        self.assertEqual(c.results,
            [('OK', 'flaky(2) &rarr; 2'),
             ('ERROR', "flaky(3) &rarr; 3", 'Oops'),
             ('OK', 'flaky(4) &rarr; 4'),
            ])


class RunPythonTest(unittest.TestCase):
    def run_python_dedented(self, a, b):
        return run_python(textwrap.dedent(a), textwrap.dedent(b))

    def test_output(self):
        results = run_python("""print 'hello!'""", "")
        self.assertEqual(results['stdout'], "hello!\n")

    def test_syntax_error_in_user_code(self):
        results = run_python("""a = 1'hello'""", "")
        self.assertIn("""1'hello'""", results['stdout'])
        self.assertIn("SyntaxError", results['stdout'])

    def test_error_in_check_code(self):
        results = run_python("""a = 17""", """1'hello'""")
        self.assertEqual("", results['stdout'])
        checks = results['checks']
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0][0], "ERROR")
        self.assertIn("1'hello'", checks[0][2])
        self.assertIn("SyntaxError", checks[0][2])

    def test_check_function(self):
        results = self.run_python_dedented("""\
            a = 17
            print 'Hi there, dudes!'
            """, """\
            def check(t, c):
                with c.expect("Your a is 17"):
                    c.test(t.module.a == 17, "Your a is %r" % t.module.a)
                with c.expect("You printed 'dudes'"):
                    c.test('dudes' in t.stdout)
                with c.expect("Your a is 34"):
                    c.test(t.module.a == 34, "Your a is %r" % t.module.a)
            """)
        self.assertEqual(results['stdout'], "Hi there, dudes!\n")
        self.assertEqual(results['checks'], [
            ('OK', 'Your a is 17'),
            ('OK', 'You printed \'dudes\''),
            ('FAIL', 'Your a is 34', 'Your a is 17'),
            ])
