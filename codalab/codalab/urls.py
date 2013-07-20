from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^starter/', TemplateView.as_view(template_name="foundation/starter.html")),
    url(r'', include('apps.web.urls')),
    (r'^accounts/', include('allauth.urls')),
    (r'^search/', include('haystack.urls')),
    (r'^api/', include('apps.api.routers')),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns(
    '',
    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse'),
)


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
