from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from .. import views



urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(template_name='web/bundle/index.html'), name='bundle'),
)
