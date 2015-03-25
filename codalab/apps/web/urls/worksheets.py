from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic import TemplateView

from .. import views

urlpatterns = patterns('',
    url(r'^$', views.WorksheetLandingView.as_view(), name='ws_landing_page'),
    url(r'^list/$', views.WorksheetListView.as_view(), name='ws_list'),
    url(r'^(?P<uuid>[A-Za-z0-9]+)/$', views.WorksheetDetailView.as_view(), name='ws_view'),
)
