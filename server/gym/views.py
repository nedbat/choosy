import json

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.http import require_POST

from desk.models import Exercise
from checker.run import run_python

def index(request):
    exes = Exercise.objects.all()
    return render_to_response('gym/templates/index.html', {'exes': exes})

def exercise(request, exid, slug):
    ex = get_object_or_404(Exercise, pk=exid)
    ctx = RequestContext(request)
    ctx['ex'] = ex
    return render_to_response('gym/templates/exercise.html', ctx)

@require_POST
def run(request, exid):
    ex = get_object_or_404(Exercise, pk=exid)
    the_code = request.POST.get('code')
    check_code = ex.check
    results = run_python(the_code, check_code)
    results['status'] = 'ok'
    return HttpResponse(json.dumps(results), mimetype="application/json")
