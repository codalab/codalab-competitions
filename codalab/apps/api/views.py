from . import serializers
from rest_framework import (viewsets,views,permissions)
from rest_framework.decorators import action,link
from rest_framework.response import Response
from apps.web import models as webmodels
from apps.authenz import models as authmodels
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist


class CompetitionAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionDataSerial
    queryset = webmodels.Competition.objects.all()

    @action(#permission_classes=[permissions.IsAuthenticated]
            )
    def participate(self,request,pk=None):
        comp = self.get_object()
        p,cr = webmodels.CompetitionParticipant.objects.get_or_create(user=self.request.user,
                                                                   competition=comp,
                                                                   defaults={'status': webmodels.ParticipantStatus.objects.get(codename='pending'),
                                                                             'reason': None})
        return Response(status=(201 if cr else 200))
    
    @link(#permission_classes=[permissions.IsAuthenticated]
          )
    def userstatus(self,request,pk=None,participant_id=None):
        comp = self.get_object()
        resp = {}
        try:
            p = webmodels.CompetitionParticipant.objects.get(user=self.request.user,competition=comp)
            resp = {'status': p.status.codename, 'reason': p.reason}
        except ObjectDoesNotExist:
            resp = {'status': 'none', 'reason': None}
        return Response(resp,status=200)

    @action(#permission_classes=[permissions.IsAuthenticated]
          )
    def userstatus(self,request,pk=None):
        comp = self.get_object()
        resp = {}
        status = request.DATA['operation']
        part = request.DATA['participantId']
        reason = request.DATA['reason']
        try:
            p = webmodels.CompetitionParticipant.objects.get(competition=comp,
                                                   pk=part)
            p.status = webmodels.ParticipantStatus.objects.get(codename=status)
            p.reason = reason
            p.save()
        except ObjectDoesNotExist as e:
            return Response(status=400)
        resp = { 'status': status,
                 'participantId': part,
                 'reason': reason }
        return Response(resp,status=201)
            
           
    @action(#permission_classes=[permissions.IsAuthenticated]
          )
    def info(self,request,*args,**kwargs):
        comp = self.get_object()
        comp.title = request.DATA.get('title')
        comp.description = request.DATA.get('description')
        comp.save()
        return Response({"data":{"title":comp.title,"description":comp.description,"imageUrl":comp.image.url},"published":3},status=200)

competition_list =   CompetitionAPIViewset.as_view({'get':'list','post':'create','put':'update','patch': 'update_partial'})
competition_retrieve =   CompetitionAPIViewset.as_view({'get':'retrieve'})

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
