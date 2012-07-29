"""Tests for run.py"""

import os.path
import sys
import textwrap
import unittest

from checker.exerciser import Checker
from checker.run import run_python


class CheckerTestCase(unittest.TestCase):

    def clean_results(self, results):
        """Remove often-changed data from the tracebacks in results."""
        for d in results:
            if 'exception' in d:
                for frame in d['exception']['traceback']:
                    frame['file'] = os.path.relpath(frame['file']).replace('\\', '/')
                    frame['line'] = 0
        return results


class CheckerTest(CheckerTestCase):
    """Test the run.Checker context mananger class."""

    def test_success(self):
        c = Checker()
        try:
            with c.expect("This should work"):
                pass
        except Checker.Done:    # pragma: nocover
            self.fail("Shouldn't have raised Done here.")
        self.assertEqual(c.results, [
            {'status': 'OK', 'expect': "This should work"},
            ])

    def test_failure(self):
        c = Checker()
        try:
            with c.expect("This should work"):
                c.fail("It failed!")
                self.fail("We shouldn't have run past a c.fail")    # pragma: nocover
            self.fail("We shouldn't have continued after a failed c.should")    # pragma: nocover
        except Checker.Done:
            pass
        self.assertEqual(c.results, [
            {'status':'FAIL', 'expect':"This should work", 'did':"It failed!"},
            ])

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
        self.assertEqual(c.results, [
            {'status':'FAIL', 'expect':"This should work", 'did':"It failed!"},
            {'status':'OK', 'expect':"Also this one"},
            ])

    def test_test(self):
        c = Checker()
        try:
            with c.expect("This should definitely work"):
                c.test(True, "This one was ok")
                c.test(False, "Oops, this was bad")
                raise Exception("Shouldn't have gotten to here")    # pragma: nocover
        except Checker.Done:
            pass
        self.assertEqual(c.results, [
            {'status':'FAIL', 'expect':"This should definitely work", 'did':"Oops, this was bad"},
            ])

    def test_error(self):
        class MyException(Exception): 
            pass
        c = Checker()
        with self.assertRaises(MyException):
            with c.expect("Everything will be fine"):
                raise MyException("It wasn't fine!")
        self.assertEqual(self.clean_results(c.results), [
            {'status':'ERROR', 'expect':"Everything will be fine", 'did':"It wasn't fine!",
                'exception': {
                    'type': "MyException",
                    'message': "It wasn't fine!",
                    'traceback': [
                        {'file':'checker/tests/test_run.py', 'line':0, 'function':'test_error', 'text':'raise MyException("It wasn\'t fine!")'},
                        ]},
                    },
            ])

    def test_quiet_expects(self):
        c = Checker()
        with c.expect("It isn't even worth mentioning.", quiet=True):
            pass
        with c.expect("Let's talk about this."):
            pass
        self.assertEqual(c.results, [
            {'status':'OK', 'expect':"Let's talk about this."},
            ])


class FunctionReturnsTest(CheckerTestCase):

    def simple(self, x):
        return x*2

    def test_simple(self):
        c = Checker()
        c.function_returns(self, 'simple', [(1, 2), (2, 4)])
        self.assertEqual(c.results, [
            {'status':'OK', 'expect':'simple(1) should return 2.'},
            {'status':'OK', 'expect':'simple(2) should return 4.'},
            ])

    def test_no_such_function(self):
        c = Checker()
        with self.assertRaises(Checker.Done):
            c.function_returns(self, 'nothing', [(1, 2), (2, 4)])
        self.assertEqual(c.results, [ 
            {'status':'FAIL', 'expect':'You should have a function named nothing.'},
            ])

    def test_not_callable(self):
        c = Checker()
        self.mylist = []
        with self.assertRaises(Checker.Done):
            c.function_returns(self, 'mylist', [(1, 2), (2, 4)])
        self.assertEqual(c.results, [
            {'status':'FAIL', 'expect':'You should have a function named mylist.'},
            ])

    def test_wrong_answers(self):
        c = Checker()
        c.function_returns(self, 'simple', [(1, 2), (2, 17), (3, 6)])
        self.assertEqual(c.results, [
            {'status':'OK', 'expect':'simple(1) should return 2.'},
            {'status':'FAIL', 'expect':'simple(2) should return 17.', 'did':'You returned 4.'},
            {'status':'OK', 'expect':'simple(3) should return 6.'},
            ])

    def add3(self, a, b, c):
        return a + b + c

    def test_multiple_arguments(self):
        c = Checker()
        c.function_returns(self, 'add3', [(1, 2, 3, 6), (1, 1, 1, 3), (10, 11, 12, 33)])
        self.assertEqual(c.results, [
            {'status':'OK', 'expect':'add3(1, 2, 3) should return 6.'},
            {'status':'OK', 'expect':'add3(1, 1, 1) should return 3.'},
            {'status':'OK', 'expect':'add3(10, 11, 12) should return 33.'},
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
        self.assertEqual(self.clean_results(c.results), [
            {'status':'OK', 'expect':'flaky(2) should return 2.'},
            {'status':'ERROR', 'expect':"flaky(3) should return 3.", 'did':'Oops',
                'exception': {
                    'type': 'Flake',
                    'message': 'Oops',
                    'traceback': [
                        {'file':'checker/exerciser.py', 'line':0, 'function':'function_returns', 'text':'actual_output = fn(*inputs)'},
                        {'file':'checker/tests/test_run.py', 'line':0, 'function':'flaky', 'text':'raise self.Flake("Oops")'},
                        ]},
                    },
            {'status':'OK', 'expect':'flaky(4) should return 4.'},
            ])


class RunPythonTest(CheckerTestCase):
    def run_python_dedented(self, a, b):
        return run_python(textwrap.dedent(a), textwrap.dedent(b))

    def test_output(self):
        results = run_python("""print 'hello!'""", "")
        self.assertEqual(results['stdout'], "hello!\n")

    def test_syntax_error_in_user_code(self):
        results = run_python("""a = 1'hello'""", "")
        self.assertEqual("", results['stdout'])
        checks = results['checks']
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]['status'], "EXCEPTION")
        self.assertEqual("SyntaxError", checks[0]['exception']['type'])
        self.assertEqual("a = 1'hello'", checks[0]['exception']['traceback'][-1]['text'])
        self.assertEqual(12, checks[0]['exception']['traceback'][-1]['offset'])

    def test_indentation_error_in_user_code(self):
        results = run_python("""a = 1\n  b = 2""", "")
        self.assertEqual("", results['stdout'])
        checks = results['checks']
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]['status'], "EXCEPTION")
        self.assertEqual("IndentationError", checks[0]['exception']['type'])
        self.assertEqual("b = 2", checks[0]['exception']['traceback'][-1]['text'])
        self.assertEqual(2, checks[0]['exception']['traceback'][-1]['offset'])

    def test_error_in_check_code(self):
        results = run_python("""a = 17""", """b = 1/0""")
        self.assertEqual("", results['stdout'])
        checks = results['checks']
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]['status'], "ERROR")
        self.assertEqual("ZeroDivisionError", checks[0]['exception']['type'])
        self.assertEqual("b = 1/0", checks[0]['exception']['traceback'][-1]['text'])

    def test_syntaxerror_in_check_code(self):
        results = run_python("""a = 17""", """1'hello'""")
        self.assertEqual("", results['stdout'])
        checks = results['checks']
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]['status'], "ERROR")
        self.assertEqual("SyntaxError", checks[0]['exception']['type'])
        self.assertEqual('invalid syntax', checks[0]['exception']['args'][0])
        self.assertEqual((1, 8, "1'hello'\n"), checks[0]['exception']['args'][1][1:])

    def test_names(self):
        results = self.run_python_dedented("""\
            a = _a = __a = a_ = a__ = 1
            """, """\
            def check(t, c):
                with c.expect("t.names() works."):
                    c.test(t.names() == "__a _a a a_ a__".split(), repr(t.names()))
            """)
        self.assertEqual(results['checks'], [
            {'status':'OK', 'expect':'t.names() works.'},
            ])

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
            {'status':'OK', 'expect':'Your a is 17'},
            {'status':'OK', 'expect':'You printed \'dudes\''},
            {'status':'FAIL', 'expect':'Your a is 34', 'did':'Your a is 17'},
            ])
