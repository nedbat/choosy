import contextlib
import shutil
import sys
import tempfile

@contextlib.contextmanager
def patchattr(obj, attr, val):
    """A context manager for temporarily patching an attribute::

        import math

        with patchattr(math, 'pi', 3.2) as newpi:
            # Compute the wrong area of circles.

    """
    oldval = getattr(obj, attr)
    setattr(obj, attr, val)
    try:
        yield val
    finally:
        setattr(obj, attr, oldval)


@contextlib.contextmanager
def isolated_modules():
    """Used to save and restore the list of modules in a with statement."""
    mods = list(sys.modules)
    try:
        yield
    finally:
        for m in [m for m in sys.modules if m not in mods]:
            del sys.modules[m]

@contextlib.contextmanager
def tempdir(prefix='tmp'):
    """A context manager for creating and then deleting a temporary directory."""
    tmpdir = tempfile.mkdtemp(prefix=prefix)
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)

