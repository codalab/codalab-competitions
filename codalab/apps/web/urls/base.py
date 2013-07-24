from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .. import views

urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(template_name='web/index.html'), name='home'),
                       url(r'^about/$', TemplateView.as_view(template_name='web/about/index.html'), name='about'),
                       url(r'^my/', include('apps.web.urls.my')),
                       url(r'^competitions/', include('apps.web.urls.competitions')),                       
                       url(r'^worksheets/', include('apps.web.urls.worksheets')),
                       url(r'^help/', include('apps.web.urls.help')),
                       url(r'^bundle/', include('apps.web.urls.bundle')),
                       )
