from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('gym.views',
    url(r'^$', 'index', name='gym'),
    url(r'^run/(?P<exid>\d+)/$', 'run'),
    url(r'^(?P<exid>\d+)/(?P<slug>.*)$', 'exercise', name='show_exercise'),
)

