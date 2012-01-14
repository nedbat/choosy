from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('scrib.views',
    url(r'^page/$', 'index', name='page_index'),
    url(r'^page/new/$', 'edit', name='new_page'),
    url(r'^page/import/$', 'import_', name='import_page'),
    url(r'^page/(?P<pageid>\d+)/$', 'show', name='show_page'),
    url(r'^page/(?P<pageid>\d+)/edit/$', 'edit', name='edit_page'),
    url(r'^page/(?P<pageid>\d+)/delete/$', 'delete', name='delete_page'),
    url(r'^page/(?P<pageid>\d+)/yaml/$', 'yaml', name='yaml_page'),
    url(r'^(?P<slug>.+)$', 'read_page', name='read_page'),
)
