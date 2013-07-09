from rest_framework import routers
from . import views
from django.conf.urls import patterns, url
router = routers.DefaultRouter()


router.register(r'competition/participant', views.CompetitionParticipantAPIViewset)
router.register(r'competition', views.CompetitionAPIViewset)
router.register(r'contentcontainers', views.ContentContainerViewSet)

urlpatterns = router.urls

urlpatterns += (
    url(r'competition/(?P<pk>\d+)/phases/(?P<phasenumber>\d+)$',views.competitionphase_retrieve,name='api_competitionphase'),
    url(r'competition/(?P<pk>\d+)/phases/$',views.competitionphase_list,name='api_competitionphases_list'),
    #url(r'competition/details/(?P<pk>\d+)/pages/$',views.competitionpage_list,name='api_competitionpage_list'),
    #url(r'competition/details/(?P<pk>\d+)/page/(?P<pagenumber>\d+)$',views.competitionpage_retrieve,name='api_competitionpage'),
    
    #url(r'pages/(?P<pagecontainer>[\w\d\-\_]+)/
    
    
)
