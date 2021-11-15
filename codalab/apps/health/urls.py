from django.conf.urls import include, url

from apps.health import views


urlpatterns = [
    url(r'^status', views.health, name='health_status'),
    url(r'^simple_status', views.simple_health, name='health_status_simple'),
    url(r'^download_simple_status', views.simple_health_csv, name='health_status_simple_csv'),
    url(r'^email_settings', views.email_settings, name='health_status_email_settings'),
    url(r'^check_thresholds', views.check_thresholds, name='health_status_check_thresholds'),
    url(r'^storage', views.storage_analytics, name='health_storage_analytics')
]
