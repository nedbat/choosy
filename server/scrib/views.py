from django.contrib.auth.decorators import login_required
from django.forms import Form, FileField
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from scrib.models import Page


@login_required
def index(request):
    pages = Page.objects.filter(user=request.user)
    return render(request, 'scrib/templates/index.html', {'pages': pages})

@login_required
def show(request, pageid):
    pg = get_object_or_404(Page, id=pageid)
    if pg.user != request.user:
        return HttpResponseForbidden(json.dumps({'status': 'error'}), mimetype="application/json")
    return render(request, 'scrib/templates/show_page.html', {'pg': pg})

@login_required
def edit(request, pageid=None):
    if request.method == "POST":
        raise Exception("This isn't done!")
    else:
        if pageid:
            page = get_object_or_404(Page, id=pageid)
        else:
            page = None
        return render(request, 'scrib/templates/edit_page.html', {'page': page})


class ImportPageForm(Form):
    yamlfile = FileField(
        label='Select a YAML file',
        help_text='Some Help'
    )

@login_required
def import_(request):
    if request.method == "POST":
        form = ImportPageForm(request.POST, request.FILES)
        if form.is_valid():
            new_pg = Page.from_yaml(request.FILES['yamlfile'], user=request.user)
            new_pg.save()
            return redirect('show_page', new_pg.id)
    else:
        form = ImportPageForm()

    return render(request, 'scrib/templates/import_page.html', {'form': form})

@login_required
def delete(request, pageid):
    pass

@login_required
def yaml(request, pageid):
    pass

def read_page(request, slug):
    """Display a page for students to read."""
    pg = get_object_or_404(Page, slug=slug)
    return render(request, 'scrib/templates/read_page.html', {'pg': pg})
