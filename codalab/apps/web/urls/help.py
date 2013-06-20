from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(template_name='web/help/index.html'), name='help'),
                       url(r'^create_competition$', TemplateView.as_view(template_name='web/help/create_competition.html'), name='help_create_competition'),
)
