from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.analytics_detail, name='analytics_detail'),
]
