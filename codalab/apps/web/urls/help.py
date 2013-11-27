from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(template_name='web/help/index.html'), name='help'),
                       url(r'^about.html', TemplateView.as_view(template_name='web/help/about.html'), name='about'),
                       url(r'^help.html', TemplateView.as_view(template_name='web/help/help.html'), name='help'),
                       url(r'^create_competition.html', TemplateView.as_view(template_name='web/help/create_competition.html'), name='help_create_competition'),
                       url(r'^glossary.html', TemplateView.as_view(template_name='web/help/glossary.html'), name='help_glossary'),
                       url(r'^faq.html', TemplateView.as_view(template_name='web/help/faq.html'), name='help_faq'),
                       url(r'^create_configure_azure.html', TemplateView.as_view(template_name='web/help/create_configure_azure.html'), name='help_configure_azure'),
                       url(r'^build_scoring_program.html', TemplateView.as_view(template_name='web/help/build_scoring_program.html'), name='help_scoring_program'),
)
