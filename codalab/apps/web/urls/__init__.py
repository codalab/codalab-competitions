from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .. import views

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='web/index.html'), name='home'),
    url(r'^_ver', views.VersionView.as_view(),name='_version'),
    url(r'^my/', include('apps.web.urls.my')),
    url(r'^competitions/', include('apps.web.urls.competitions', namespace="competitions")),
    url(r'^experiments/', include('apps.web.urls.experiments')),
    url(r'^worksheets/', include('apps.web.urls.worksheets')),
    url(r'^about/', TemplateView.as_view(template_name='web/help/about.html'), name='about'),
    url(r'^help/', include('apps.web.urls.help')),
    url(r'^bundles/', include('apps.web.urls.bundles')),
)
