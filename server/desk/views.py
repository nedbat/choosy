from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.http import require_POST

from desk.models import Exercise
from desk.forms import ExerciseForm, ImportExerciseForm

import json


@login_required
def index(request):
    exes = Exercise.objects.filter(user=request.user)
    ctx = RequestContext(request)
    ctx['exes'] = exes
    return render_to_response('desk/templates/index.html', ctx)

@login_required
def show(request, slug):
    ex = get_object_or_404(Exercise, slug=slug)
    if ex.user != request.user:
        return HttpResponseForbidden(json.dumps({'status': 'error'}), mimetype="application/json")
    ctx = RequestContext(request)
    ctx['ex'] = ex
    return render_to_response('desk/templates/show_exercise.html', ctx)

@login_required
def edit(request, slug=None):
    if slug:
        ex = get_object_or_404(Exercise, slug=slug)
        if ex.user != request.user:
            return HttpResponseForbidden(json.dumps({'status': 'error'}), mimetype="application/json")
    else:
        ex = None
    form = ExerciseForm(request.POST or None, instance=ex)
    if form.is_valid():
        ex = form.save(user=request.user)
        return redirect('desk_show_exercise', ex.slug)

    ctx = RequestContext(request)
    ctx['form'] = form
    return render_to_response('desk/templates/edit_exercise.html', ctx)

@require_POST
@login_required
def delete(request, exid):
    ex = Exercise.objects.get(id=exid)
    if ex.user != request.user:
        return HttpResponseForbidden(json.dumps({'status': 'error'}), mimetype="application/json")
    ex.delete()
    return HttpResponse(json.dumps({'status': 'ok'}), mimetype="application/json")

@login_required
def import_(request):
    if request.method == "POST":
        form = ImportExerciseForm(request.POST, request.FILES)
        if form.is_valid():
            new_ex = Exercise.from_yaml(request.FILES['yamlfile'], user=request.user)
            new_ex.save()
            return redirect('desk_show_exercise', new_ex.slug)
    else:
        form = ImportExerciseForm()

    ctx = RequestContext(request)
    ctx['form'] = form
    return render_to_response('desk/templates/import_exercise.html', ctx)

@login_required
def yaml(request, slug):
    """Deliver the exercise as a YAML file."""
    ex = get_object_or_404(Exercise, slug=slug)
    if ex.user != request.user:
        return HttpResponseForbidden(json.dumps({'status': 'error'}), mimetype="application/json")
    response = HttpResponse(ex.as_yaml(), mimetype="text/yaml") 
    response['Content-Disposition'] = 'attachment; filename=%s.yaml' % ex.slug
    return response
