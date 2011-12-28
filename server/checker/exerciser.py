"""Glue code running in Choosy's sandbox.

This file is the bulk of the code running in the sandbox to execute the 
student's code, and then the teacher's checking code.  Because it runs
in the sandbox, it may be limited, for example, no file writing.

"""

from cStringIO import StringIO
import json
import os
import sys
import traceback

from utils import patchattr, isolated_modules, tempdir

class Checker(object):
    class Failure(Exception):
        pass
    
    class Done(Exception):
        pass

    def __init__(self):
        self.results = []

    def expect(self, desc, continue_on_fail=False, continue_on_error=False, quiet=False):
        """Declare an expectation.

        `desc` is the description of what is expected.
    
        If `continue_on_fail` is true, then a failure in this expectation 
        won't end the check function, but will continue with the next 
        expectation.

        If `continue_on_error` is true, then an exception during execution 
        won't end the check function, but will continue with the next 
        expectation.

        If `quiet` is true, then a message will only be shown to the user if 
        the expectation fails, nothing will be displayed if it succeeds. This
        is useful for initial sanity checks that all students will pass.
        
        """
        self.desc = desc
        self.continue_on_fail = continue_on_fail
        self.continue_on_error = continue_on_error
        self.quiet = quiet
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is self.Failure:
            self.add_result("FAIL", expect=self.desc, did=str(exc_value))
            if self.continue_on_fail:
                return True
            else:
                raise self.Done()
        elif exc_type:
            self.add_result("ERROR", expect=self.desc, did=str(exc_value), exc=(exc_type, exc_value, exc_tb))
            return self.continue_on_error
        elif not self.quiet:
            self.add_result("OK", expect=self.desc)

    def add_result(self, status, expect=None, did=None, exc=None):
        """Add a result."""
        d = { 'status': status }
        if expect:
            d['expect'] = expect
        if did:
            d['did'] = did
        if exc:
            exc_type, exc_value, exc_tb = exc
            tb = [
                {'file':f, 'line':l, 'function':fn, 'text':t} 
                    for f, l, fn, t in traceback.extract_tb(exc_tb)
                ]
            msg = str(exc_value)
            d['exception'] = {
                'type': exc_type.__name__, 
                'message': msg,
                'traceback': tb,
                }
            args = exc_value.args
            if isinstance(args, tuple) and len(args) == 1 and args[0] == msg:
                args = None
            if args is not None:
                d['exception']['args'] = args
        self.results.append(d)

    def fail(self, message=""):
        """Fail an expectation with a `message` to the user."""
        raise self.Failure(message)

    def test(self, condition, message=""):
        """Test a `condition`, and if false, fail with a `message`."""
        if not condition:
            self.fail(message)

    def function_returns(self, exercise, fn_name, in_outs):
        """Check that a function behaves as expected.

        `exercise` is the exercise module produced by the student. `fn_name`
        is the name of the function in that module to test.

        `in_outs` is a list of tuples.  Each tuple represents one function
        call: the last value in the tuple is the expected return value if 
        all-but-the-last values in the tuple are passed to the function::

            c.function_returns(t.module, 'square', [
                (1, 1),
                (2, 4),
                (10, 100),
                (-3, 9),
                ])

        """
        with self.expect("""You should have a function named %s.""" % fn_name, quiet=True):
            fn = getattr(exercise, fn_name, None)
            if not fn or not callable(fn):
                self.fail()
        for in_out in in_outs:
            inputs, output = in_out[:-1], in_out[-1]
            nice_inputs = ", ".join("%r" % i for i in inputs)
            with self.expect("%s(%s) should return %r." % (fn_name, nice_inputs, output), continue_on_fail=True, continue_on_error=True):
                actual_output = fn(*inputs)
                if actual_output != output:
                    self.fail("You returned %r." % actual_output)


class Trial(object):
    """One trial by the student to get the right answer."""
    def __init__(self, module, stdout):
        self.module = module
        self.stdout = stdout

    def names(self):
        """Return the list of names defined by the user in the module."""
        return [n for n in dir(self.module) if not (n.startswith('__') and n.endswith('__'))]


def run_exercise(tmpdir):
    """Run the student and teacher code.

    `tmpdir` is the path to a directory containing "exercise.py" and 
    "check.py", which will be imported to execute them.

    Returns a dictionary `results`.

    results['stdout'] is the stdout of the exercise.

    results['checks'] is a list of dicts::
    
        [
            {'status':'OK', 'expect':'You should have a variable named a'),
            {'status':'FAIL', 'expect':'a should equal 17', 'did':'Your a equals 43'},
        ]

    `status` is one of 'OK', 'FAIL', or 'ERROR'.  'OK' means the expectation 
    was met, 'FAIL' means it wasn't met, and 'ERROR' means an exception was
    encountered.  `expect` is the text of the `expect` call, what was expected.
    `did` is a message about what actually happened.  `traceback` is a list of
    tuples, the traceback, if any, in the form produced by `traceback.extract_tb`.

    """
    results = {'stdout': '', 'checks': []}
    with patchattr(sys, 'stdout', StringIO()) as stdout, \
        patchattr(sys, 'path', ['.']+sys.path):
        with isolated_modules():
            c = None
            try:
                import exercise
            except SystemExit:
                # The user code called sys.exit(), it's ok.
                pass
            except Exception:
                tb = traceback.format_exc()
                tb = tb.replace(tmpdir + os.sep, "")
                stdout.write(tb)
            else:
                try:
                    t = Trial(module=exercise, stdout=stdout.getvalue())
                    c = Checker()
                    import check
                    try:
                        check.check(t, c)
                    except c.Done:
                        pass
                except Exception:
                    # Something went wrong in the checking code.
                    c.add_result('ERROR', exc=sys.exc_info())
            finally:
                results['stdout'] = stdout.getvalue()
                if c:
                    results['checks'] = c.results

    return results
