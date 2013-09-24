import json
from . import serializers
from rest_framework import (viewsets,views,permissions)
from rest_framework import renderers
from rest_framework.decorators import action,link,permission_classes
from rest_framework.exceptions import PermissionDenied, ParseError
from rest_framework.response import Response
from apps.web import models as webmodels
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404


class CompetitionAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionSerial
    queryset = webmodels.Competition.objects.all()

    def destroy(self, request, pk):
        """
        Cleanup the destruction of a competition.

        This requires removing phases, submissions, and participants. We should try to design 
        the models to make the cleanup simpler if we can.
        """
        # Get the competition
        c = webmodels.Competition.objects.get(id=pk)

        # Create a blank response
        response = {}
        if self.request.user is not None and self.request.user == c.creator:
            c.delete()
            response['id'] = pk
        else:
            response['status'] = 403

        return Response(json.dumps(response), content_type="application/json")

    @action(permission_classes=[permissions.IsAuthenticated])
    def participate(self,request,pk=None):
        comp = self.get_object()
        terms = request.DATA['agreed_terms']
        status = webmodels.ParticipantStatus.objects.get(codename=webmodels.ParticipantStatus.PENDING)
        p,cr = webmodels.CompetitionParticipant.objects.get_or_create(user=self.request.user,
                                                                   competition=comp,
                                                                   defaults={'status': status,
                                                                             'reason': None})
        response_data = {
            'result' : 201 if cr else 200,
            'id' : p.id
        }

        return Response(json.dumps(response_data), content_type="application/json")
    
    def _get_userstatus(self,request,pk=None,participant_id=None):
        comp = self.get_object()
        resp = {}
        status = 200
        try:
            p = webmodels.CompetitionParticipant.objects.get(user=self.request.user,competition=comp)
            resp = {'status': p.status.codename, 'reason': p.reason}
        except ObjectDoesNotExist:
            resp = {'status': None, 'reason': None}
            status = 400
        return Response(resp,status=status)

    @link(permission_classes=[permissions.IsAuthenticated])
    def mystatus(self,request,pk=None):
        return self._get_userstatus(request,pk)

    @action(methods=['POST','PUT'], permission_classes=[permissions.IsAuthenticated])
    def participation_status(self,request,pk=None):
        comp = self.get_object()
        resp = {}
        status = request.DATA['status']
        part = request.DATA['participant_id']
        reason = request.DATA['reason']

        try:
            p = webmodels.CompetitionParticipant.objects.get(competition=comp, pk=part)
            p.status = webmodels.ParticipantStatus.objects.get(codename=status)
            p.reason = reason
            p.save()
            resp = { 
                'status': status,
                'participantId': part,
                'reason': reason 
                }
        except ObjectDoesNotExist as e:
            resp = {
                'status' : 400
                }      
        
        return Response(json.dumps(resp), content_type="application/json")
            
    @action(permission_classes=[permissions.IsAuthenticated])
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
    
    def get_queryset(self):
        competition_id = self.kwargs.get('competition_id',None)
        return self.queryset.filter(competition__pk=competition_id)

class CompetitionPhaseAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionPhaseSerial
    queryset = webmodels.Competition.objects.all()
    
    def get_queryset(self):
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

competition_page_list = CompetitionPageViewSet.as_view({'get':'list','post':'create'})
competition_page = CompetitionPageViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update'})


@permission_classes((permissions.IsAuthenticated,))
class CompetitionSubmissionViewSet(viewsets.ModelViewSet):
    queryset = webmodels.CompetitionSubmission.objects.all()
    serializer_class = serializers.CompetitionSubmissionSerial
    _file = None

    def get_queryset(self):
        return self.queryset.filter(phase__competition__pk=self.kwargs['competition_id'])

    def pre_save(self,obj):
        try:
            obj.participant = webmodels.CompetitionParticipant.objects.filter(competition=self.kwargs['competition_id'], user=self.request.user).get()
        except ObjectDoesNotExist:
            raise PermissionDenied()
        if not obj.participant.is_approved:
            raise PermissionDenied()
        for phase in webmodels.CompetitionPhase.objects.filter(competition=self.kwargs['competition_id']):
            if phase.is_active is True:
                break
        if phase is None or phase.is_active is False:
            raise PermissionDenied(detail = 'Competition phase is closed.')
        obj.phase = phase        

    def handle_exception(self, exc):
        if type(exc) is DjangoPermissionDenied:
            exc = PermissionDenied(detail = str(exc))
        return super(CompetitionSubmissionViewSet, self).handle_exception(exc)

    @action(methods=["DELETE"])
    def removeFromLeaderboard(self, request, pk=None, competition_id=None):
        try:
            participant = webmodels.CompetitionParticipant.objects.filter(competition=self.kwargs['competition_id'], user=self.request.user).get()
        except ObjectDoesNotExist:
            raise PermissionDenied()
        if not participant.is_approved:
            raise PermissionDenied()
        submission = webmodels.CompetitionSubmission.objects.get(id=pk)
        if submission.phase.is_active is False:
            raise PermissionDenied(detail = 'Competition phase is closed.')
        if submission.participant.user != self.request.user:
            raise ParseError(detail = 'Invalid submission')
        response = dict()
        lb = webmodels.PhaseLeaderBoard.objects.get(phase=submission.phase)
        lbe = webmodels.PhaseLeaderBoardEntry.objects.get(board=lb, result=submission)
        lbe.delete()
        response['status'] = lbe.id
        return Response(response, status=response['status'], content_type="application/json")

    @action(methods=["POST"])
    def addToLeaderboard(self, request, pk=None, competition_id=None):
        try:
            participant = webmodels.CompetitionParticipant.objects.filter(competition=self.kwargs['competition_id'], user=self.request.user).get()
        except ObjectDoesNotExist:
            raise PermissionDenied()
        if not participant.is_approved:
            raise PermissionDenied()
        submission = webmodels.CompetitionSubmission.objects.get(id=pk)
        if submission.phase.is_active is False:
            raise PermissionDenied(detail = 'Competition phase is closed.')
        if submission.participant.user != self.request.user:
            raise ParseError(detail = 'Invalid submission')
        response = dict()
        lb,_ = webmodels.PhaseLeaderBoard.objects.get_or_create(phase=submission.phase)
        # Currently we only allow one submission into the leaderboard although the leaderboard
        # is setup to accept multiple submissions from the same participant.
        entries = webmodels.PhaseLeaderBoardEntry.objects.filter(board=lb, result__participant=participant)
        for entry in entries:
            entry.delete()
        lbe,cr = webmodels.PhaseLeaderBoardEntry.objects.get_or_create(board=lb, result=submission)
        response['status'] = (201 if cr else 200)
        return Response(response, status=response['status'], content_type="application/json")

competition_submission_retrieve = CompetitionSubmissionViewSet.as_view({'get':'retrieve'})
competition_submission_create = CompetitionSubmissionViewSet.as_view({'post':'create'})
competition_submission_leaderboard = CompetitionSubmissionViewSet.as_view({'post':'addToLeaderboard', 'delete':'removeFromLeaderboard'})

class LeaderBoardViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.LeaderBoardSerial
    queryset = webmodels.PhaseLeaderBoard.objects.all()

    def get_queryset(self):
        kw = {}
        competition_id = self.kwargs.get('competition_id',None)
        phase_id = self.kwargs.get('phase_id',None)
        if phase_id:
            kw['phase__pk'] = phase_id
        if competition_id:
            kw['phase__competition__pk'] = competition_id
        return self.queryset.filter(**kw)

leaderboard_list = LeaderBoardViewSet.as_view({'get':'list','post':'create'} )
leaderboard_retrieve = LeaderBoardViewSet.as_view( {'get':'retrieve','put':'update','patch':'partial_update'} )

class DefaultContentViewSet(viewsets.ModelViewSet):
    queryset = webmodels.DefaultContentItem.objects.all()
    serializer_class = serializers.DefaultContentSerial
    
class SubmissionScoreViewSet(viewsets.ModelViewSet):
    queryset = webmodels.CompetitionSubmission.objects.all()
    serializer_class = serializers.CompetitionScoresSerial

    def get_queryset(self):
        kw = {}
        competition_id = self.kwargs.get('competition_id',None)
        phase_id = self.kwargs.get('phase_id',None)
        participant_id = self.kwargs.get('participant_id',None)
        if competition_id:
            kw['submission__phase__competition__pk'] = competition_id
        if phase_id:
            kw['submission__phase__pk'] = phase_id
        if participant_id:
            kw['submission__participant__pk'] = participant_id
        return self.queryset.filter(**kw)
        
competition_scores_list = SubmissionScoreViewSet.as_view( {'get':'list'} )
