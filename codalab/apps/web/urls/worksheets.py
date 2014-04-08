from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic import TemplateView

from .. import views

urlpatterns = patterns('',
    url(r'^$', views.WorksheetListView.as_view(), name='list'),
    url(r'^(?P<uuid>[A-Za-z0-9]+)$', views.WorksheetDetailView.as_view(), name='view'),
)
