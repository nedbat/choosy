from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('desk.views',
    url(r'^$', 'index', name='desk'),
    url(r'^new/$', 'edit', name='new_exercise'),
    url(r'^import/$', 'import_', name='import_exercise'),
    url(r'^(?P<slug>[-\w]+)/$', 'show', name='desk_show_exercise'),
    url(r'^(?P<slug>[-\w]+)/edit/$', 'edit', name='edit_exercise'),
    url(r'^(?P<slug>[-\w]+)/yaml/$', 'yaml', name='yaml_exercise'),
)
