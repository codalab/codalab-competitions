from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^status', views.health, name='health_status'),
    url(r'^simple_status', views.simple_health, name='health_status_simple'),
    url(r'^worker_list', views.worker_list, name='health_worker_list'),
    url(r'^worker_detail/(?P<worker_pk>\d+)$', views.worker_detail, name='health_worker_detail'),
    url(r'^email_settings', views.email_settings, name='health_status_email_settings'),
    url(r'^check_thresholds', views.check_thresholds, name='health_status_check_thresholds')
]
