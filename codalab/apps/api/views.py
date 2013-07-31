from . import serializers
from rest_framework import (viewsets,views,permissions)
from rest_framework.decorators import action,link
from rest_framework.response import Response
from rest_framework import renderers
from apps.web import models as webmodels
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

class CompetitionAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionSerial
    queryset = webmodels.Competition.objects.all()


    @action(permission_classes=[permissions.IsAuthenticated]
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

    @action(methods=['POST','PUT','GET'], permission_classes=[permissions.IsAuthenticated]
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
            
           
    @action(permission_classes=[permissions.IsAuthenticated]
          )
    def info(self,request,*args,**kwargs):
        comp = self.get_object()
        comp.title = request.DATA.get('title')
        comp.description = request.DATA.get('description')
        comp.save()
        return Response({"data":{"title":comp.title,"description":comp.description,"imageUrl":comp.image.url if comp.image else None},"published":3},status=200)

competition_list =   CompetitionAPIViewSet.as_view({'get':'list','post':'create', 'post': 'participate',})
competition_retrieve =   CompetitionAPIViewSet.as_view({'get':'retrieve','put':'update', 'patch': 'partial_update'})

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

class CompetitionParticipantAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionParticipantSerial
    queryset = webmodels.CompetitionParticipant.objects.all()


class CompetitionPhaseAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionPhaseSerial
    queryset = webmodels.Competition.objects.all()
    
    def get_query_set(self):
        competition_id = self.kwargs.get('pk',None)
        phasenumber = self.kwargs.get('phasenumber',None)
        kw = {}
        if competition_id:
            kw['pk'] = competition_id
        if phasenumber:
            kw['phases__phasenumber'] = phasenumber
        return self.queryset.filter(**kw)

competitionphase_list = CompetitionPhaseAPIViewset.as_view({'get':'list','post':'create'})
competitionphase_retrieve = CompetitionPhaseAPIViewset.as_view({'get':'retrieve','put':'update','patch':'partial_update'})


class CompetitionPageViewSet(viewsets.ModelViewSet):
    ## TODO: Turn the custom logic here into a mixin for other content
    serializer_class = serializers.PageSerial  
    content_type = ContentType.objects.get_for_model(webmodels.Competition)
    queryset = webmodels.Page.objects.all()
    _pagecontainer = None
    _pagecontainer_q = None

    def get_queryset(self):
        kw = {}
        if 'competition_id' in self.kwargs:
            kw['container__object_id'] = self.kwargs['competition_id']
            kw['container__content_type'] = self.content_type
        if 'category' in self.kwargs:
            kw['category__codename'] = self.kwargs['category']
        if kw:
            return self.queryset.filter(**kw)
        else:
            return self.queryset

    def dispatch(self,request,*args,**kwargs):        
        if 'competition_id' in kwargs:
            self._pagecontainer_q = webmodels.PageContainer.objects.filter(object_id=kwargs['competition_id'],
                                                                           content_type=self.content_type)
        return super(CompetitionPageViewSet,self).dispatch(request,*args,**kwargs)

    @property
    def pagecontainer(self):
        if self._pagecontainer_q is not None and self._pagecontainer is None: 
            try:
                self._pagecontainer = self._pagecontainer_q.get()
            except ObjectDoesNotExist:
                self._pagecontainer = None
        return self._pagecontainer
    
    def new_pagecontainer(self,competition_id):
        try:
            competition=webmodels.Competition.objects.get(pk=competition_id)
        except ObjectDoesNotExist:
            raise Http404
        self._pagecontainer = webmodels.PageContainer.objects.create(object_id=competition_id,
                                                                     content_type=self.content_type)
        return self._pagecontainer

    def get_serializer_context(self):
        ctx = super(CompetitionPageViewSet,self).get_serializer_context()
        if 'competition_id' in self.kwargs:
            ctx.update({'container': self.pagecontainer})
        return ctx

    def create(self,request,*args,**kwargs):        
        container = self.pagecontainer
        if not container:
            container = self.new_pagecontainer(self.kwargs.get('competition_id'))           
        return  super(CompetitionPageViewSet,self).create(request,*args,**kwargs)

competition_page_list = CompetitionPageViewSet.as_view({'get':'list','post':'create','put':'update','patch':'partial_update'})
competition_page = CompetitionPageViewSet.as_view({'get':'retrieve'})

class CompetitionSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionSubmissionSerial
    queryset = webmodels.CompetitionSubmission.objects.all()

    def pre_save(self,obj):
        if not obj.status:
            obj.status = webmodels.CompetitionSubmissionStatus.objects.get(codename='submitted')
        if not obj.participant:
            obj.participant = self.request.user
        
class DefaultContentViewSet(viewsets.ModelViewSet):
    queryset = webmodels.DefaultContentItem.objects.all()
    serializer_class = serializers.DefaultContentSerial
    
