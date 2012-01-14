from django.contrib.auth.decorators import login_required
from django.forms import Form, FileField
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.http import require_POST

from scrib.models import Page


@login_required
def index(request):
    pages = Page.objects.filter(user=request.user)
    ctx = RequestContext(request)
    ctx['pages'] = pages
    return render_to_response('scrib/templates/index.html', ctx)

@login_required
def show(request, pageid):
    pg = get_object_or_404(Page, id=pageid)
    if pg.user != request.user:
        return HttpResponseForbidden(json.dumps({'status': 'error'}), mimetype="application/json")
    ctx = RequestContext(request)
    ctx['pg'] = pg
    return render_to_response('scrib/templates/show_page.html', ctx)

@login_required
def edit(request, pageid=None):
    if request.method == "POST":
        pass
    else:
        if pageid:
            page = get_object_or_404(Page, id=pageid)
        else:
            page = None
        ctx = RequestContext(request)
        ctx['page'] = page
        return render_to_response('scrib/templates/edit_page.html', ctx)


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

    ctx = RequestContext(request)
    ctx['form'] = form
    return render_to_response('scrib/templates/import_page.html', ctx)

@login_required
def delete(request, pageid):
    pass

@login_required
def yaml(request, pageid):
    pass

def read_page(request, slug):
    """Display a page for students to read."""
    pg = get_object_or_404(Page, slug=slug)
    ctx = RequestContext(request)
    ctx['pg'] = pg
    return render_to_response('scrib/templates/read_page.html', ctx)
