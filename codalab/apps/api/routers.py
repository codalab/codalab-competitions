from rest_framework import routers
from . import views
from django.conf.urls import patterns, url
router = routers.DefaultRouter()


router.register(r'competition/participant', views.CompetitionParticipantAPIViewset)
router.register(r'competition', views.CompetitionAPIViewset)
urlpatterns = router.urls

urlpatterns += (
    url(r'competition/(?P<pk>\d+)/phases/(?P<phasenumber>\d+)$',views.competitionphase_retrieve,name='api_competitionphase'),
    url(r'competition/(?P<pk>\d+)/phases/$',views.competitionphase_list,name='api_competitionphases_list'),
    
)
