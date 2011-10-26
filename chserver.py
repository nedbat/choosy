"""The local code-running server for Choose Python."""

import functools
import json
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

EXER_ROOT = os.path.join(os.path.dirname(__file__), "exercises")

@b.route('/run')
@jsonp
def run():
    the_code = b.request.GET['code']
    name = b.request.GET['name']
    check_code = open(os.path.join(EXER_ROOT, "check_%s.py" % name)).read()
    output, results = run_python(the_code, check_code)
    return {
        'status': 'ok',
        'output': output,
        'results': results,
        }

@b.route('/exer/:name')
def exer(name):
    html = open(os.path.join(EXER_ROOT, name+".html")).read()
    return b.template("exercise.html", name=name, html=html)


def main(args):
    port = 9000
    webbrowser.open("http://127.0.0.1:%d/exer/first" % port)
    b.debug(True)
    b.run(host='localhost', port=port, reloader=True)

if __name__ == '__main__':
    main(sys.argv)

