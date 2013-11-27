from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic import TemplateView


urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(
                           template_name='web/help/index.html'), name='help'),
                       url(r'^about.html', TemplateView.as_view(
                           template_name='web/help/about.html'), name='about'),
                       url(r'^help.html', TemplateView.as_view(
                           template_name='web/help/help.html'), name='help'),
                       )
