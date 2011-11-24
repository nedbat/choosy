from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('debug.views',
    url(r'^settings/$', 'settings'),
    url(r'^error/$', 'error'),
    url(r'^email/$', 'email'),
    url(r'^environment/$', 'environment'),
    url(r'^modules/$', 'modules'),
)
