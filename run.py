from utils import patchattr, isolated_modules, tempdir

import cStringIO as StringIO
import os
import sys
import traceback

class Checker(object):
    class Failure(Exception):
        pass
    
    class Done(Exception):
        pass

    def __init__(self):
        self.results = []

    def expect(self, msg, continue_on_fail=False):
        self.msg = msg
        self.continue_on_fail = continue_on_fail
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is self.Failure:
            self.results.append(("BAD", self.msg, "%s" % exc_value))
            if self.continue_on_fail:
                return True
            else:
                raise self.Done()
        elif exc_type:
            self.results.append(("FAIL", self.msg, "%s" % exc_value))
            return False
        else:
            self.results.append(("OK", self.msg))

    def fail(self, msg=""):
        raise self.Failure(msg)

    def test(self, cond, msg=""):
        if not cond:
            self.fail(msg)


def run_python(py, check):
    """Run a chunk of python code, and then check it with check code.
    
    Returned tuple is `(stdout, results)`: `results` is a list of 
    tuples::
    
        [
            ('OK', 'You should have a variable named a'),
            ('BAD', 'a should equal 17', 'Your a equals 43'),
        ]

    The first element of each tuple is a status ('OK', 'BAD', or 'FAIL').  
    The second element is the text of the `expect` call, what was expected.
    A third element, if present, is what actually happened.

    """
    output, results = "", []
    with tempdir(prefix='choosepy_') as tmpdir:
        with open(os.path.join(tmpdir, "exercise.py"), "w") as f:
            f.write(py)

        with open(os.path.join(tmpdir, "check.py"), "w") as f:
            f.write(check)

        with \
            patchattr(sys, 'stdout', StringIO.StringIO()) as stdout, \
            patchattr(sys, 'path', [tmpdir]+sys.path):
            with isolated_modules():
                try:
                    import exercise
                except SystemExit:
                    # The user code called sys.exit(), it's ok.
                    pass
                except Exception as e:
                    tb = traceback.format_exc()
                    tb = tb.replace(tmpdir + os.sep, "")
                    stdout.write(tb)
                else:
                    try:
                        c = Checker()
                        import check
                        try:
                            check.check(exercise, output, c)
                        except c.Done:
                            pass
                        results = c.results
                    except Exception as e:
                        # Something went wrong in the checking code.
                        tb = traceback.format_exc()
                        results = [('FAIL', '', tb)]
                finally:
                    output = stdout.getvalue()

    return output, results
