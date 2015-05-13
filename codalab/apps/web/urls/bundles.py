from django.conf.urls import patterns, url
from apps.web import views


urlpatterns = patterns('',
    url(r'^$', views.BundleListView.as_view(), name='bundle_list'),
    url(r'^(?P<uuid>[-A-Za-z0-9_]+)/$', views.BundleDetailView.as_view(), name="bundle_detail"),
    url(r'^(?P<uuid>[-A-Za-z0-9_]+)/download/$', views.BundleDownload, name="bundle_detail"),
)
