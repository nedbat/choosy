from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('gym.views',
    url(r'^$', 'index', name='gym'),
    url(r'^run/(?P<exid>\d+)/$', 'run', name='gym_run'),
    url(r'^run/$', 'run', name='gym_run_anon'),
    url(r'^(?P<exid>\d+)/(?P<slug>.*)$', 'exercise', name='gym_show_exercise'),
)

