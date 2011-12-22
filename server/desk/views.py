from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.http import require_POST

from gym.models import Exercise
from desk.forms import ExerciseForm

def index(request):
    exes = Exercise.objects.all()
    return render_to_response('desk/templates/index.html', {'exes': exes})

def show(request, exid):
    exercise = get_object_or_404(Exercise, pk=exid)
    ctx = RequestContext(request)
    ctx['ex'] = exercise
    return render_to_response('desk/templates/show_exercise.html', ctx)

def edit(request, exid=None):
    if exid:
        exercise = get_object_or_404(Exercise, pk=exid)
    else:
        exercise = None
    form = ExerciseForm(request.POST or None, instance=exercise)
    if form.is_valid():
        exercise = form.save()
        return redirect('show_exercise', exercise.id)

    ctx = RequestContext(request)
    ctx['form'] = form
    return render_to_response('desk/templates/edit_exercise.html', ctx)
