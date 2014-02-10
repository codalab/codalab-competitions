from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='web/experiments/index.html'),
        name='worksheets'),
)
