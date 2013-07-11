from . import serializers
from rest_framework import (viewsets,views)
from apps.web import models as webmodels
from apps.authenz import models as authmodels
from django.contrib.contenttypes.models import ContentType

class CompetitionAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionDataSerial
    queryset = webmodels.Competition.objects.all()


class CompetitionParticipantAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionParticipantSerial
    queryset = webmodels.CompetitionParticipant.objects.all()


class CompetitionPhaseAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionPhaseSerial
    queryset = webmodels.CompetitionPhase.objects.all()
    
    def get_query_set(self):
        # The pk (primary key) is for the competition, not the phase.
        # rest framework could use a little extension to provide more 
        # flexibility.
        competition_id = self.kwargs.get('pk',None)
        phasenumber = self.kwargs.get('phasenumber',None)
        kw = {}
        if competition_id:
            kw['competition_id'] = competition_id
        if number:
            kw['phasenumber'] = phasenumber
        return self.queryset.filter(**kw)

competitionphase_list = CompetitionPhaseAPIViewset.as_view({'get':'list','post':'create','put':'update'})
competitionphase_retrieve = CompetitionPhaseAPIViewset.as_view({'get':'retrieve'})

class ContentContainerViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ContentContainerSerial
    queryset = webmodels.ContentContainer.objects.filter()

contentcontainer_list = ContentContainerViewSet.as_view({'get':'list'})

class CompetitionPageViewSet(viewsets.ModelViewSet):
    ## TODO: Turn the custom logic here into a mixin for other content
    serializer_class = serializers.PageSerial
    content_type = ContentType.objects.get_for_model(webmodels.Competition)
    queryset = webmodels.Page.objects.filter(pagecontainer__content_type=content_type)
    pagecontainer = None

    def get_serializer_context(self):
        ctx = super(CompetitionPageViewSet,self).get_serializer_context()
        ctx.update({ 'content_type': self.content_type,
                     'pagecontainer': self.pagecontainer })
        return ctx
        
    def create(self,request,*args,**kwargs):

        if 'entity_label' in self.kwargs:
            self.pagecontainer,cr = webmodels.PageContainer.objects.get_or_create(
                entity=webmodels.ContentEntity.objects.get(codename=kwargs.get('entity_label')),
                content_type = self.content_type, 
                object_id=kwargs.get('pk')
                )
        return  super(CompetitionPageViewSet,self).create(request,*args,**kwargs)
    

competition_page_list = CompetitionPageViewSet.as_view({'get':'list','post':'create','put':'update'})


competition_page = CompetitionPageViewSet.as_view({'get':'retrieve'})
