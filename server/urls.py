from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^gym/', include('gym.urls')),
    url(r'^desk/', include('desk.urls')),
    url(r'^debug/', include('debug.urls')),
    url(r'^accounts/', include('allauth.urls')),
)
