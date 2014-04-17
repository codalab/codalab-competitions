from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='web/help/help.html'), name='help'),
    url(r'^glossary', TemplateView.as_view(template_name='web/help/glossary.html'), name='help_glossary'),
    url(r'^faq', TemplateView.as_view(template_name='web/help/faq.html'), name='help_faq'),
    url(r'^azure', TemplateView.as_view(template_name='web/help/create_configure_azure.html'), name='help_configure_azure'),
    url(r'^competition/create', TemplateView.as_view(template_name='web/help/create_competition.html'), name='help_create_competition'),
    url(r'^competition/scoring', TemplateView.as_view(template_name='web/help/build_scoring_program.html'), name='help_scoring_program')
)
