import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from desk.models import Exercise
from checker.run import run_python

def index(request):
    exes = Exercise.objects.all()
    return render(request, 'gym/templates/index.html', {'exes': exes})

def exercise(request, exid, slug):
    ex = get_object_or_404(Exercise, pk=exid)
    return render(request, 'gym/templates/exercise.html', {'ex': ex})

@require_POST
def run(request, exid=None):
    the_code = request.POST.get('code')
    if exid:
        ex = get_object_or_404(Exercise, pk=exid)
        check_code = ex.check
    else:
        check_code = request.POST.get('check', '')
    if not check_code:
        return HttpResponse("No check code to run", status=400)
    results = run_python(the_code, check_code)
    results['status'] = 'ok'
    return HttpResponse(json.dumps(results), mimetype="application/json")
