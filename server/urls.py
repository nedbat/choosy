from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', direct_to_template, { 'template': 'choosy/templates/home.html' }, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^gym/', include('gym.urls')),
    url(r'^desk/', include('desk.urls')),
    url(r'^account/you$', direct_to_template, { 'template': 'choosy/templates/you.html' }, name='account_you'), 
    url(r'^account/', include('allauth.urls')),

    url(r'^debug/', include('debug.urls')),

    url(r'', include('scrib.urls')),
)
