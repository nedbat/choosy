"""The local code-running server for Choose Python."""

import functools
import json
import optparse
import os, os.path
import sys
import webbrowser

import bottle as b

from run import run_python

def jsonp(fn):
    """A decorator to make a view function do JSONP properly."""
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        jsfn = b.request.GET['callback']
        data = fn(*args, **kwargs)
        return "%s(%s);" % (jsfn, json.dumps(data))
    return wrapped

FILE_ROOT = None

@b.route('/_run')
@jsonp
def run():
    the_code = b.request.GET['code']
    name = b.request.GET['name']
    check_code = open(os.path.join(FILE_ROOT, "check_%s.py" % name)).read()
    output, results = run_python(the_code, check_code)
    return {
        'status': 'ok',
        'output': output,
        'results': results,
        }

@b.route('/:path#[\\w/.]+#')
def page(path):
    """Serve a page at a `path`, relative to `FILE_ROOT`."""
    filepath = os.path.join(FILE_ROOT, path)
    try:
        f = open(filepath)
    except IOError:
        if not filepath.endswith(".html"):
            f = open(filepath + ".html")
        else:
            raise
    with f:
        html = f.read()
    return b.template("exercise.html", html=html)


def main(args):
    parser = optparse.OptionParser()
    parser.add_option("-d", "--debug", dest="debug", help="Turn on debugging", default=False, action="store_true")
    options, args = parser.parse_args()

    first_page = None
    if len(args) >= 1:
        first_page = args[0]

    if not first_page:
        print "No first page specified"
        return

    global FILE_ROOT
    FILE_ROOT, first_page = os.path.split(first_page)

    port = 9000
    webbrowser.open("http://127.0.0.1:%d/%s" % (port, first_page))
    b.debug(options.debug)
    b.run(host='localhost', port=port, reloader=options.debug)

if __name__ == '__main__':
    main(sys.argv)
