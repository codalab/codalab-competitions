from . import serializers
from rest_framework import (viewsets,views,permissions)
from rest_framework.decorators import action,link
from rest_framework.response import Response
from rest_framework import renderers
from apps.web import models as webmodels
from apps.authenz import models as authmodels
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

class CompetitionAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionDataSerial
    #serializer_class = serializers.CSerial
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
    
    def _get_userstatus(self,request,pk=None,participant_id=None):
        comp = self.get_object()
        resp = {}
        try:
            p = webmodels.CompetitionParticipant.objects.get(user=self.request.user,competition=comp)
            resp = {'status': p.status.codename, 'reason': p.reason}
        except ObjectDoesNotExist:
            resp = {'status': 'none', 'reason': None}
        return Response(resp,status=200)

    @action(methods=['POST','PUT','GET'], #permission_classes=[permissions.IsAuthenticated]
          )
    def userstatus(self,request,pk=None):
        if request.method == 'GET':
            return self._get_userstatus(request,pk)
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
        return Response({"data":{"title":comp.title,"description":comp.description,"imageUrl":comp.image.url if comp.image else None},"published":3},status=200)

competition_list =   CompetitionAPIViewset.as_view({'get':'list','post':'create','put':'update','patch': 'update_partial'})
competition_retrieve =   CompetitionAPIViewset.as_view({'get':'retrieve'})

class CompetitionPhaseEditView(views.APIView):
    renderer_classes = (renderers.JSONRenderer,renderers.BrowsableAPIRenderer)

    def post(self,request,*args,**kwargs):
        serial = serializers.CompetitionPhasesEditSerial(data=request.DATA)
        if not serial.is_valid():
            raise Exception(serial.errors)
        comp = webmodels.Competition.objects.get(pk=kwargs.get('competition_id'))
        if serial.data['end_date']:
            comp.end_date = serial.data['end_date']
            comp.save()
        for p in serial.data['phases']:
            if p['phase_id']:
                phase = webmodels.CompetitionPhase.objects.get(pk = p['phase_id'],competition=comp)
            else:
                phase = webmodels.CompetitionPhase.objects.create(competition=comp,label=p['label'],
                                                                  start_date=p['start_date'],
                                                                  phasenumber=p['phasenumber'],
                                                                  max_submissions=p['max_submissions'])
        return Response(status=200)

class CompetitionParticipantAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionParticipantSerial
    queryset = webmodels.CompetitionParticipant.objects.all()


class CompetitionPhaseAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionPhaseSerial
    queryset = webmodels.Competition.objects.all()
    
    def get_query_set(self):
        # The pk (primary key) is for the competition, not the phase.
        # rest framework could use a little extension to provide more 
        # flexibility.
        competition_id = self.kwargs.get('pk',None)
        phasenumber = self.kwargs.get('phasenumber',None)
        kw = {}
        if competition_id:
            kw['pk'] = competition_id
        if number:
            kw['phases__phasenumber'] = phasenumber
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

    def get_serializer(self,instance=None, data=None,
                       files=None, many=False, partial=False,**kwargs):
        if self.pagecontainer:
            if instance:
                instance.pagecontainer = self.pagecontainer                
            if data:
                data['pagecontainer'] = self.pagecontainer.pk
        return super(CompetitionPageViewSet,self).get_serializer(instance=instance, data=data,
                       files=files, many=many, partial=partial, **kwargs)

    def get_serializer_context(self):
        ctx = super(CompetitionPageViewSet,self).get_serializer_context()
        ctx.update({ 'content_type': self.content_type,
                     'pagecontainer': self.pagecontainer })
        return ctx

    def get_object(self,queryset=None):
        container = self.kwargs.get('entity',None)
        page_id = self.kwargs.get('pk',None)
        competition_id = self.kwargs.get('competition_id')
        
        kw = {}
        if container:
            kw['pagecontainer__entity__pk'] = container
        if page_id:
            kw['pk'] = page_id
        if competition_id:
            kw['pagecontainer__object_id'] = competition_id
        try:
            o =  self.queryset.filter(**kw).get()
        except ObjectDoesNotExist:
            raise Http404
        return o

    def get_queryset(self):
        q = self.queryset.filter(pagecontainer__object_id=self.kwargs.get('container_id'))
        if 'entity' in self.kwargs:
            q = q.filter(pagecontainer__entity__pk=self.kwargs.get("entity"))           
        return q
        
    def create(self,request,*args,**kwargs):
        if 'entity' in self.kwargs:
            self.pagecontainer,cr = webmodels.PageContainer.objects.get_or_create(
                entity=webmodels.ContentEntity.objects.get(pk=self.kwargs.get('entity')),
                content_type = self.content_type, 
                object_id=kwargs.get('competition_id')
                )
        return  super(CompetitionPageViewSet,self).create(request,*args,**kwargs)

    def update(self,request,*args,**kwargs):
        self.pagecontainer = webmodels.PageContainer.objects.get(content_type = self.content_type, 
                                                                 object_id=kwargs.get('competition_id'),
                                                                 entity__pk=self.kwargs.get('entity'))
        
        return  super(CompetitionPageViewSet,self).update(request,*args,**kwargs)
    

competition_page_list = CompetitionPageViewSet.as_view({'get':'list','post':'create','put':'update'})


competition_page = CompetitionPageViewSet.as_view({'get':'retrieve'})
