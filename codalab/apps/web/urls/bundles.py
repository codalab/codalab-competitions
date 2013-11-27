from django.conf.urls import patterns
from django.conf.urls import url
from apps.web import views


urlpatterns = patterns('',
                       url(r'^$', views.BundleListView.as_view(
                           template_name='web/bundles/bundle_list.html'), name='bundles'),
                       url(r'^create_bundle$', views.BundleCreateView.as_view(
                           template_name='web/bundles/bundle_form.html'), name="createbundle"),
                       url(r'^(?P<pk>\d+)$', views.BundleDetailView.as_view(template_name='web/bundles/bundle_detail.html'),
                           name="bundle_detail"),
                       )
