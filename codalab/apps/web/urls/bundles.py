from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from apps.web import views


urlpatterns = patterns('',
    url(r'^$', views.BundleListView.as_view(), name='bundle_list'),
    url(r'^(?P<uuid>[-A-Za-z0-9_]+)/$', views.BundleDetailView.as_view(), name="bundle_detail"),
)