from utils import patchattr, isolated_modules, tempdir, change_dir
import exerciser

import cStringIO as StringIO
import json
import os
import sys
import textwrap
import traceback

USE_PYPY = bool(os.environ.get('USE_PYPY', False))

def run_python(exercise, check):
    """Run exercise python code, and then check it with check code.
    
    Returns the same value as `exerciser.run_exercise`.

    """
    # We write the exercise and check code to files in a new temporary
    # directory, then invoke exerciser.run_exercise.
    with tempdir(prefix='choosy-') as tmpdir:
        with change_dir(tmpdir):
            with open("exercise.py", "w") as f:
                f.write(exercise)

            with open("check.py", "w") as f:
                f.write(check)

            if USE_PYPY:
                return run_exercise_in_sandbox(tmpdir)
            else:
                return exerciser.run_exercise(tmpdir)

if USE_PYPY:
    from pypy.tool.lib_pypy import LIB_ROOT
    from pypy.translator.sandbox import pypy_interact
    from pypy.translator.sandbox.vfs import Dir, RealDir, RealFile

    PYPY_SANDBOX = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pypy-sandbox'))

    class ChoosySandboxedProc(pypy_interact.PyPySandboxedProc):
        def build_virtual_root(self):
            # build a virtual file system:
            # * can access its own executable
            # * can access the pure Python libraries
            # * can access the temporary usession directory as /tmp
            exclude_pyc = ['.pyc', '.pyo']
            assert self.tmpdir
            libroot = str(LIB_ROOT)

            return Dir({
                'bin': Dir({
                    'pypy-c': RealFile(self.executable),
                    'lib-python': RealDir(os.path.join(libroot, 'lib-python'), exclude=exclude_pyc), 
                    'lib_pypy': RealDir(os.path.join(libroot, 'lib_pypy'), exclude=exclude_pyc),
                    }),
                'tmp': RealDir(self.tmpdir, exclude=exclude_pyc),
                'choosy': RealDir(os.path.dirname(self.executable)),
                })

    def run_exercise_in_sandbox(tmpdir):

        code = textwrap.dedent("""\
            import json, sys
            sys.path[:0] = ['/choosy']
            import exerciser

            results = exerciser.run_exercise('.')
            print json.dumps(results)
            """)
        args = [
            '--heapsize', '8000000',    # 15m is about the minimum, but this is what I really want.
            '-S',                       # Don't try to import the non-existent 'site' module
            '-c', code,                 # Run this code
            ]
        sandproc = ChoosySandboxedProc(PYPY_SANDBOX, args, tmpdir='.', debug=False)
        #if timeout is not None:
        #    sandproc.settimeout(timeout, interrupt_main=True)
        try:
            code_output = StringIO.StringIO()
            code_error = StringIO.StringIO()
            retcode = sandproc.interact(stdout=code_output, stderr=code_error)
            if retcode == 0:
                output = code_output.getvalue()
                try:
                    result = json.loads(output)
                except ValueError:
                    result = ["", [('ERROR', "", "Bad json: %r" % output)]]
            else:
                result = ["", [('ERROR', "", "Process ended with %s: %s" % (retcode, code_error.getvalue()))]]
            return result
        finally:
            sandproc.kill()
