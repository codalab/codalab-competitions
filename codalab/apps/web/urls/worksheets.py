from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='web/worksheets/worksheet_list.html'), name='worksheets'),
    url(r'^(?P<uuid>[A-Za-z0-9]+)$', TemplateView.as_view(template_name='web/worksheets/worksheet_detail.html'), name="worksheet_detail"),
)