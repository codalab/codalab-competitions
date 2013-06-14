from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

import views

urlpatterns = patterns('apps.web',
                       url(r'^$', TemplateView.as_view(template_name='web/index.html'), name='home'),
                       url(r'^about/$', TemplateView.as_view(template_name='web/about.html'), name='about'),
                       url(r'^my/$', TemplateView.as_view(template_name='web/my_codalab.html'), name='my_codalab'),
                       url(r'^competitions', TemplateView.as_view(template_name='web/competitions.html'), name='competitions'),
                       url(r'^worksheets', TemplateView.as_view(template_name='web/worksheets.html'), name='worksheets'),
                       )
