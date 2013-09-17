from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(template_name='web/help/index.html'), name='help'),
                       url(r'^about.html', TemplateView.as_view(template_name='web/help/about.html'), name='about'),
                       url(r'^create_competition$', TemplateView.as_view(template_name='web/help/create_competition.html'), name='help_create_competition'),
                       url(r'^configure_azure$', TemplateView.as_view(template_name='web/help/create_configure_azure.html'), name='help_configure_azure'),
)
