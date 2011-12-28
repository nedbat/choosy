from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.http import require_POST
from django.forms import FileField, Form, ModelForm

from desk.models import Exercise
from desk.forms import ExerciseForm

class ImportForm(Form):
    yamlfile = FileField(
        label='Select a YAML file',
        help_text='Some Help'
    )

def index(request):
    exes = Exercise.objects.all()

    ctx = RequestContext(request)
    ctx['exes'] = exes
    return render_to_response('desk/templates/index.html', ctx)

def show(request, slug):
    exercise = get_object_or_404(Exercise, slug=slug)
    ctx = RequestContext(request)
    ctx['ex'] = exercise
    return render_to_response('desk/templates/show_exercise.html', ctx)

def edit(request, slug=None):
    if slug:
        exercise = get_object_or_404(Exercise, slug=slug)
    else:
        exercise = None
    form = ExerciseForm(request.POST or None, instance=exercise)
    if form.is_valid():
        exercise = form.save()
        return redirect('desk_show_exercise', exercise.slug)

    ctx = RequestContext(request)
    ctx['form'] = form
    return render_to_response('desk/templates/edit_exercise.html', ctx)

def import_(request):
    if request.method == "POST":
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            new_ex = Exercise.from_yaml(request.FILES['yamlfile'])
            new_ex.save()
            return redirect('desk_show_exercise', new_ex.slug)
    else:
        form = ImportForm()

    ctx = RequestContext(request)
    ctx['form'] = form
    return render_to_response('desk/templates/import_exercise.html', ctx)

def yaml(request, slug):
    """Deliver the exercise as a YAML file."""
    exercise = get_object_or_404(Exercise, slug=slug)
    response = HttpResponse(exercise.as_yaml(), mimetype="text/yaml") 
    response['Content-Disposition'] = 'attachment; filename=%s.yaml' % exercise.slug
    return response
