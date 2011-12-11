from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('desk.views',
    url(r'^$', 'index', name='desk'),
    url(r'^new/$', 'edit', name='new_exercise'),
    url(r'^(?P<exid>\d+)/edit/$', 'edit', name='edit_exercise'),
)
