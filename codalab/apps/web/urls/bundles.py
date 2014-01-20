from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from apps.web import views


urlpatterns = patterns('',
    url(r'^$', views.BundleListView.as_view(template_name='web/bundles/bundle_list.html'), name='bundles'),
    #url(r'^create_bundle$', views.BundleCreateView.as_view(template_name='web/bundles/bundle_form.html'), name="createbundle"),
    url(r'^(?P<uuid>[A-Za-z0-9]+)$', views.BundleDetailView.as_view(template_name='web/bundles/bundle_detail.html'), name="bundle_detail"),
)