from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from apps.web import views


urlpatterns = patterns('',
    url(r'^$', views.RunListView.as_view(template_name='web/runs/run_list.html'), name='runs'),
    url(r'^create_run$', views.RunCreateView.as_view(template_name='web/runs/run_form.html'), name="createrun"),
    url(r'^(?P<pk>\d+)$', views.RunDetailView.as_view(template_name='web/runs/run_detail.html'), name="run_detail"),
)