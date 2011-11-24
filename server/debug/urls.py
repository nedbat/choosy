from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('debug.views',
    url(r'^settings/$', 'dump_settings'),
    url(r'^error/$', 'raise_error'),
    url(r'^email/$', 'send_email'),
    url(r'^environment/$', 'dump_environment'),
    url(r'^modules/$', 'dump_modules'),
)
