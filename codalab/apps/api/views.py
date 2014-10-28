"""
Defines Django views for 'apps.api' app.
"""
import json
import logging
import traceback
import mimetypes


from . import serializers
from uuid import uuid4
from rest_framework import (permissions, status, viewsets, views, generics, filters)
from rest_framework.decorators import action, link, permission_classes
from rest_framework.exceptions import PermissionDenied, ParseError
from rest_framework.response import Response

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.http import Http404, StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils.encoding import smart_str

from apps.authenz.models import ClUser
from apps.jobs.models import Job
from apps.web import models as webmodels
from apps.web.bundles import BundleService
from apps.web.tasks import (create_competition, evaluate_submission)

from codalab.azure_storage import make_blob_sas_url, PREFERRED_STORAGE_X_MS_VERSION

logger = logging.getLogger(__name__)

def _generate_blob_sas_url(prefix, extension):
    """
    Helper to generate SAS URL for creating a BLOB.
    """
    blob_name = '{0}/{1}{2}'.format(prefix, str(uuid4()), extension)
    url = make_blob_sas_url(settings.BUNDLE_AZURE_ACCOUNT_NAME,
                            settings.BUNDLE_AZURE_ACCOUNT_KEY,
                            settings.BUNDLE_AZURE_CONTAINER,
                            blob_name,
                            permission='w',
                            duration=60)
    logger.debug("_generate_blob_sas_url: sas=%s; blob_name=%s.", url, blob_name)
    return {'url': url, 'id': blob_name, 'version': PREFERRED_STORAGE_X_MS_VERSION}

@permission_classes((permissions.IsAuthenticated,))
class CompetitionCreationSasApi(views.APIView):
    """
    Provides a web API to start the process of creating a competition.
    """
    def post(self, request):
        """
        Provides a Blob SAS that a client can use to upload the competition definition bundle.
        Returns a dictionary of the form: { 'url': <shared-access-url>, 'id': <tracking-id> }
        """
        prefix = 'competition/upload/{0}'.format(request.user.id)
        response_data = _generate_blob_sas_url(prefix, '.zip')
        return Response(response_data, status=status.HTTP_201_CREATED)

@permission_classes((permissions.IsAuthenticated,))
class CompetitionCreationApi(views.APIView):
    """
    Provides a web API to continue the process of creating a competition.
    """
    def post(self, request):
        """
        This POST method expects a file identified by the key 'file' in the set of files uploaded
        by the client in multipart MIME format ('multipart/form-data'). The uploaded file is used
        to create a competition definition bundle on behalf of the logged in user. When the bundle
        is created a job is launched to start the process of creating the competition from the
        specified definition. The job ID is returned to the client in a JSON object:
            { 'token': <value> }
        Use the token with CompetitionCreationStatusApi to track the progress of the job.
        """
        blob_name = request.DATA['id'] if 'id' in request.DATA else ''
        if len(blob_name) <= 0:
            return Response("Invalid or missing tracking ID.", status=status.HTTP_400_BAD_REQUEST)
        owner = self.request.user
        logger.debug("CompetitionCreation: owner=%s; filename=%s.", owner.id, blob_name)
        cdb = webmodels.CompetitionDefBundle.objects.create(owner=owner)
        cdb.config_bundle.name = blob_name
        cdb.save()
        logger.debug("CompetitionCreation def: owner=%s; def=%s; blob=%s.", owner.id, cdb.pk, cdb.config_bundle.name)
        job = create_competition(cdb.pk)
        logger.debug("CompetitionCreation job: owner=%s; def=%s; job=%s.", owner.id, cdb.pk, job.pk)
        return Response({'token' : job.pk}, status=status.HTTP_201_CREATED)

@permission_classes((permissions.IsAuthenticated,))
class CompetitionCreationStatusApi(views.APIView):
    """
    Provides a web API to track progress of a 'create' operation started with CompetitionCreationApi.
    """
    def get(self, request, token):
        """
        Returns the operation status:
           { 'status': <value> }
        where <value> is status of the job as defined by the 'code_name' in apps.jobs.models.Job.STATUS_BY_CODE.
        """
        user_id = self.request.user.id
        logger.debug("CompetitionCreationStatus: requestor=%s; token=%s.", user_id, token)
        try:
            job = Job.objects.get(pk=token)
        except Job.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        logger.debug("CompetitionCreationStatus: requestor=%s; job=%s; job.status:%s.", user_id, job.pk, job.status)
        data = {'status' : job.get_status_code_name()}
        info = job.get_task_info()
        logger.debug("CompetitionCreationStatus: info=%s", info)
        if 'competition_id' in info:
            data['id'] = info['competition_id']
        if 'error' in info:
            data['error'] = info['error']
        return Response(data)

class CompetitionAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionSerial
    queryset = webmodels.Competition.objects.all()
    filter_class = serializers.CompetitionFilter
    filter_backends = (filters.DjangoFilterBackend,filters.SearchFilter,)
    filter_fields = ('creator')
    search_fields = ("title", "description", "=creator__username")

    @method_decorator(login_required)
    def destroy(self, request, pk, *args, **kwargs):
        """
        Cleanup the destruction of a competition.

        This requires removing phases, submissions, and participants. We should try to design
        the models to make the cleanup simpler if we can.
        """
        # Get the competition
        c = webmodels.Competition.objects.get(id=pk)

        # Create a blank response
        response = {}
        if self.request.user == c.creator:
            c.delete()
            response['id'] = pk
        else:
            response['status'] = 403

        return Response(json.dumps(response), content_type="application/json")

    @action(methods=['GET'], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk):
        """
        Publish a competition.
        """
        c = webmodels.Competition.objects.get(id=pk)
        response = {}
        if self.request.user == c.creator or self.request.user in c.admins.all():
            phases_needing_reference_data = webmodels.CompetitionPhase.objects.filter(competition=c, reference_data='').count()

            if phases_needing_reference_data > 0:
                response = {
                    "error": "Not all phases have reference data, it is required for each phase before publishing."
                }
                return Response(json.dumps(response), status=400, content_type="application/json")

            c.published = True
            c.save()
            response['id'] = pk
            response['status'] = 200
        else:
            response['status'] = 403
        return Response(json.dumps(response), content_type="application/json")

    @action(methods=['GET'], permission_classes=[permissions.IsAuthenticated])
    def unpublish(self, request, pk):
        """
        Unpublish a competition.
        """
        c = webmodels.Competition.objects.get(id=pk)
        response = {}
        if self.request.user == c.creator:
            c.published = False
            c.save()
            response['id'] = pk
            response['status'] = 200
        else:
            response['status'] = 403
        return Response(json.dumps(response), content_type="application/json")

    def _send_mail(self, context_data, from_email=None, html_file=None, text_file=None, subject=None, to_email=None):
        from_email = from_email if from_email else settings.DEFAULT_FROM_EMAIL

        context_data["site"] = Site.objects.get_current()

        context = Context(context_data)
        text = render_to_string(text_file, context)
        html = render_to_string(html_file, context)

        message = EmailMultiAlternatives(subject, text, from_email, [to_email])
        message.attach_alternative(html, 'text/html')
        message.send()

    @action(permission_classes=[permissions.IsAuthenticated])
    def participate(self, request, pk=None):
        comp = self.get_object()

        # If there is no registration required we just check to make sure they have agreed to the terms and conditions
        # which is done by the javascript before the ajax call, during form validation.
        if comp.has_registration:
            status = webmodels.ParticipantStatus.objects.get(codename=webmodels.ParticipantStatus.PENDING)
        else:
            status = webmodels.ParticipantStatus.objects.get(codename=webmodels.ParticipantStatus.APPROVED)

        p, cr = webmodels.CompetitionParticipant.objects.get_or_create(user=self.request.user,
                                                                       competition=comp,
                                                                       defaults={'status': status, 'reason': None})

        response_data = {
            'result' : 201 if cr else 200,
            'id' : p.id
        }

        status_text = str(status)

        if status_text.lower() == webmodels.ParticipantStatus.PENDING.lower():
            if self.request.user.participation_status_updates:
                self._send_mail(
                    {
                        'competition': comp,
                        'user': self.request.user,
                    },
                    subject='Application to %s sent' % comp,
                    html_file="emails/notifications/participation_requested.html",
                    text_file="emails/notifications/participation_requested.txt",
                    to_email=self.request.user.email
                )

            if comp.creator.organizer_status_updates:
                self._send_mail(
                    {
                        'competition': comp,
                        'participant': p,
                        'user': comp.creator,
                    },
                    subject='%s applied to your competition' % p.user,
                    html_file="emails/notifications/organizer_participation_requested.html",
                    text_file="emails/notifications/organizer_participation_requested.txt",
                    to_email=comp.creator.email
                )
        elif status_text == webmodels.ParticipantStatus.APPROVED:
            if self.request.user.participation_status_updates:
                self._send_mail(
                    {
                        'competition': comp,
                        'user': self.request.user,
                    },
                    subject='Accepted into %s!' % comp,
                    html_file="emails/notifications/participation_accepted.html",
                    text_file="emails/notifications/participation_accepted.txt",
                    to_email=self.request.user.email
                )

            if comp.creator.organizer_status_updates:
                self._send_mail(
                    {
                        'competition': comp,
                        'participant': p,
                        'user': comp.creator
                    },
                    subject='%s accepted into your competition!' % p.user,
                    html_file="emails/notifications/organizer_participation_accepted.html",
                    text_file="emails/notifications/organizer_participation_accepted.txt",
                    to_email=comp.creator.email
                )

        return Response(json.dumps(response_data), content_type="application/json")

    def _get_userstatus(self, request, pk=None, participant_id=None):
        comp = self.get_object()
        resp = {}
        status = 200
        try:
            p = webmodels.CompetitionParticipant.objects.get(user=self.request.user, competition=comp)
            resp = {'status': p.status.codename, 'reason': p.reason}
        except ObjectDoesNotExist:
            resp = {'status': None, 'reason': None}
            status = 400
        return Response(resp, status=status)

    @link(permission_classes=[permissions.IsAuthenticated])
    def mystatus(self, request, pk=None):
        return self._get_userstatus(request, pk)

    @action(methods=['POST', 'PUT'], permission_classes=[permissions.IsAuthenticated])
    def participation_status(self, request, pk=None):
        comp = self.get_object()
        resp = {}
        status = request.DATA['status']
        part = request.DATA['participant_id']
        reason = request.DATA['reason']

        if comp.creator != request.user and request.user not in comp.admins.all():
            raise PermissionDenied()

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

            if status == webmodels.ParticipantStatus.PENDING:
                pass
            elif status == webmodels.ParticipantStatus.APPROVED:
                if self.request.user.participation_status_updates:
                    self._send_mail(
                        {
                            'competition': comp,
                            'user': self.request.user,
                        },
                        subject='Accepted into %s!' % comp,
                        html_file="emails/notifications/participation_accepted.html",
                        text_file="emails/notifications/participation_accepted.txt",
                        to_email=self.request.user.email
                    )

                if comp.creator.organizer_status_updates:
                    self._send_mail(
                        {
                            'competition': comp,
                            'participant': p,
                            'user': comp.creator,
                        },
                        subject='%s accepted into your competition!' % p.user,
                        html_file="emails/notifications/organizer_participation_accepted.html",
                        text_file="emails/notifications/organizer_participation_accepted.txt",
                        to_email=comp.creator.email
                    )
            elif status == webmodels.ParticipantStatus.DENIED:
                if self.request.user.participation_status_updates:
                    self._send_mail(
                        {
                            'competition': comp,
                            'user': self.request.user,
                        },
                        subject='Permission revoked from %s!' % comp,
                        html_file="emails/notifications/participation_revoked.html",
                        text_file="emails/notifications/participation_revoked.txt",
                        to_email=self.request.user.email
                    )

                if comp.creator.organizer_status_updates:
                    self._send_mail(
                        {
                            'competition': comp,
                            'participant': p,
                            'user': comp.creator,
                        },
                        subject="%s's permission revoked from your competition!" % p.user,
                        html_file="emails/notifications/organizer_participation_revoked.html",
                        text_file="emails/notifications/organizer_participation_revoked.txt",
                        to_email=comp.creator.email
                    )

        except ObjectDoesNotExist as e:
            resp = {
                'status' : 400
                }

        return Response(json.dumps(resp), content_type="application/json")

    @action(permission_classes=[permissions.IsAuthenticated])
    def info(self, request, *args, **kwargs):
        comp = self.get_object()
        comp.title = request.DATA.get('title')
        comp.description = request.DATA.get('description')
        comp.save()
        return Response({"data": {
                             "title": comp.title,
                             "description": comp.description,
                             "imageUrl": comp.image.url if comp.image else None},
                         "published": 3}, status=200)

competition_list = CompetitionAPIViewSet.as_view({'get':'list', 'post': 'participate'})
competition_retrieve = CompetitionAPIViewSet.as_view({'get':'retrieve', 'put':'update', 'patch': 'partial_update'})

class CompetitionParticipantAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionParticipantSerial
    queryset = webmodels.CompetitionParticipant.objects.all()

    def get_queryset(self):
        competition_id = self.kwargs.get('competition_id', None)
        return self.queryset.filter(competition__pk=competition_id)

class CompetitionPhaseAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionPhaseSerial
    queryset = webmodels.Competition.objects.all()

    def get_queryset(self):
        competition_id = self.kwargs.get('pk', None)
        phasenumber = self.kwargs.get('phasenumber', None)
        kw = {}
        if competition_id:
            kw['pk'] = competition_id
        if phasenumber:
            kw['phases__phasenumber'] = phasenumber
        return self.queryset.filter(**kw)

competitionphase_list = CompetitionPhaseAPIViewset.as_view({'get':'list', 'post':'create'})
competitionphase_retrieve = CompetitionPhaseAPIViewset.as_view({'get':'retrieve',
                                                                'put':'update',
                                                                'patch':'partial_update'})


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

    def dispatch(self, request, *args, **kwargs):
        if 'competition_id' in kwargs:
            self._pagecontainer_q = webmodels.PageContainer.objects.filter(object_id=kwargs['competition_id'],
                                                                           content_type=self.content_type)
        return super(CompetitionPageViewSet, self).dispatch(request, *args, **kwargs)

    @property
    def pagecontainer(self):
        if self._pagecontainer_q is not None and self._pagecontainer is None:
            try:
                self._pagecontainer = self._pagecontainer_q.get()
            except ObjectDoesNotExist:
                self._pagecontainer = None
        return self._pagecontainer

    def new_pagecontainer(self, competition_id):
        try:
            competition = webmodels.Competition.objects.get(pk=competition_id)
        except ObjectDoesNotExist:
            raise Http404
        self._pagecontainer = webmodels.PageContainer.objects.create(object_id=competition_id,
                                                                     content_type=self.content_type)
        return self._pagecontainer

    def get_serializer_context(self):
        ctx = super(CompetitionPageViewSet, self).get_serializer_context()
        if 'competition_id' in self.kwargs:
            ctx.update({'container': self.pagecontainer})
        return ctx

    def create(self, request, *args, **kwargs):
        container = self.pagecontainer
        if not container:
            container = self.new_pagecontainer(self.kwargs.get('competition_id'))
        return  super(CompetitionPageViewSet, self).create(request, *args, **kwargs)

competition_page_list = CompetitionPageViewSet.as_view({'get':'list', 'post':'create'})
competition_page = CompetitionPageViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update'})


@permission_classes((permissions.IsAuthenticated,))
class CompetitionSubmissionSasApi(views.APIView):
    """
    Provides a web API to start the process of making a submission to a competition.
    """
    def post(self, request, competition_id=''):
        """
        Provides a Blob SAS that a client can use to upload a submission.
        Returns a dictionary of the form: { 'url': <shared-access-url>, 'id': <tracking-id> }
        """
        if len(competition_id) <= 0:
            raise ParseError(detail='Invalid competition ID.')
        prefix = 'competition/{0}/submission/{1}'.format(competition_id, request.user.id)
        response_data = _generate_blob_sas_url(prefix, '.zip')
        return Response(response_data, status=status.HTTP_201_CREATED)

@permission_classes((permissions.IsAuthenticated,))
class CompetitionSubmissionViewSet(viewsets.ModelViewSet):
    queryset = webmodels.CompetitionSubmission.objects.all()
    serializer_class = serializers.CompetitionSubmissionSerial
    _file = None

    def get_queryset(self):
        return self.queryset.filter(phase__competition__pk=self.kwargs['competition_id'])

    def pre_save(self, obj):
        try:
            obj.participant = webmodels.CompetitionParticipant.objects.filter(
                                competition=self.kwargs['competition_id'], user=self.request.user).get()
        except ObjectDoesNotExist:
            raise PermissionDenied()
        if not obj.participant.is_approved:
            raise PermissionDenied()
        for phase in webmodels.CompetitionPhase.objects.filter(competition=self.kwargs['competition_id']):
            if phase.is_active is True:
                break
        if phase is None or phase.is_active is False:
            raise PermissionDenied(detail='Competition phase is closed.')
        if phase.auto_migration and not phase.is_migrated:
            raise PermissionDenied(detail="Failed, competition phase is being migrated, please try again in a few minutes")
        obj.phase = phase

        blob_name = self.request.DATA['id'] if 'id' in self.request.DATA else ''
        if len(blob_name) <= 0:
            raise ParseError(detail='Invalid or missing tracking ID.')
        obj.file.name = blob_name

    def create(self, request, **kwargs):
        response = super(CompetitionSubmissionViewSet, self).create(request, **kwargs)
        self.object.description = request.QUERY_PARAMS.get('description', None)
        self.object.save()
        return response

    def post_save(self, obj, created):
        if created:
            evaluate_submission(obj.pk, obj.phase.is_scoring_only)

    def handle_exception(self, exc):
        if type(exc) is DjangoPermissionDenied:
            exc = PermissionDenied(detail=str(exc))
        return super(CompetitionSubmissionViewSet, self).handle_exception(exc)

    @action(methods=["DELETE"])
    def removeFromLeaderboard(self, request, pk=None, competition_id=None):
        try:
            participant = webmodels.CompetitionParticipant.objects.filter(competition=self.kwargs['competition_id'],
                                                                          user=self.request.user).get()
        except ObjectDoesNotExist:
            raise PermissionDenied()
        if not participant.is_approved:
            raise PermissionDenied()
        submission = webmodels.CompetitionSubmission.objects.get(id=pk)
        if not submission.phase.is_active:
            raise PermissionDenied(detail='Competition phase is closed.')
        if submission.phase.is_blind:
            raise PermissionDenied(detail='Competition phase does not allow participants to modify the leaderboard.')
        if submission.participant.user != self.request.user:
            raise ParseError(detail='Invalid submission')
        response = dict()
        lb = webmodels.PhaseLeaderBoard.objects.get(phase=submission.phase)
        lbe = webmodels.PhaseLeaderBoardEntry.objects.get(board=lb, result=submission)
        lbe.delete()
        response['status'] = lbe.id
        return Response(response, status=response['status'], content_type="application/json")

    @action(methods=["POST"])
    def addToLeaderboard(self, request, pk=None, competition_id=None):
        try:
            participant = webmodels.CompetitionParticipant.objects.filter(competition=self.kwargs['competition_id'],
                                                                          user=self.request.user).get()
        except ObjectDoesNotExist:
            raise PermissionDenied()
        if not participant.is_approved:
            raise PermissionDenied()
        submission = webmodels.CompetitionSubmission.objects.get(id=pk)
        if not submission.phase.is_active:
            raise PermissionDenied(detail='Competition phase is closed.')
        if submission.phase.is_blind:
            raise PermissionDenied(detail='Competition phase does not allow participants to modify the leaderboard.')
        if submission.participant.user != self.request.user:
            raise ParseError(detail='Invalid submission')
        response = dict()
        _, cr = webmodels.add_submission_to_leaderboard(submission)
        response['status'] = (201 if cr else 200)
        return Response(response, status=response['status'], content_type="application/json")

competition_submission_retrieve = CompetitionSubmissionViewSet.as_view({'get':'retrieve'})
competition_submission_create = CompetitionSubmissionViewSet.as_view({'post':'create'})
competition_submission_leaderboard = CompetitionSubmissionViewSet.as_view(
                                        {'post':'addToLeaderboard', 'delete':'removeFromLeaderboard'})

class LeaderBoardViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.LeaderBoardSerial
    queryset = webmodels.PhaseLeaderBoard.objects.all()

    def get_queryset(self):
        kw = {}
        competition_id = self.kwargs.get('competition_id', None)
        phase_id = self.kwargs.get('phase_id', None)
        if phase_id:
            kw['phase__pk'] = phase_id
        if competition_id:
            kw['phase__competition__pk'] = competition_id
        return self.queryset.filter(**kw)

leaderboard_list = LeaderBoardViewSet.as_view({'get':'list', 'post':'create'})
leaderboard_retrieve = LeaderBoardViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update'})

class LeaderBoardDataViewSet(views.APIView):
    """
    Provides a web API to get the leaderboard data for a phase of a competition
    """
    def get(self, request, *args, **kwargs):
        competition_id = self.kwargs.get('competition_id', None)
        phase_id = self.kwargs.get('phase_id', None)
        competition = webmodels.Competition.objects.get(pk=competition_id)
        phase = webmodels.CompetitionPhase.objects.filter(competition=competition, phasenumber=phase_id)[0]
        if phase.is_blind:
            return Response(status=403)
        groups = phase.scores()
        response = Response(groups, status=status.HTTP_200_OK)
        return response


class DefaultContentViewSet(viewsets.ModelViewSet):
    queryset = webmodels.DefaultContentItem.objects.all()
    serializer_class = serializers.DefaultContentSerial

#
# Worksheets
#
class WorksheetsInfoApi(views.APIView):
    """
    Provides a web API to retrieve worksheets information.
    """
    def get(self, request):
        user = self.request.user
        logger.debug("WorksheetsApi: user_id=%s.", user.id)
        info = {
            'config': {
                'beta' : settings.SHOW_BETA_FEATURES,
                'preview' : getattr(settings, 'PREVIEW_WORKSHEETS', False),
                'loginUrl' : settings.LOGIN_URL,
                'logoutUrl' : settings.LOGOUT_URL,
            },
            'user': {
                'authenticated': user.id != None,
                'name': user.username,
            }
        }
        return Response(info, status=status.HTTP_201_CREATED)

class WorksheetsListApi(views.APIView):
    """
    Provides a web API for worksheet entries.
    """
    def get(self, request):
        user_id = self.request.user.id
        logger.debug("WorksheetsListApi: user_id=%s.", user_id)
        service = BundleService(self.request.user)
        try:
            worksheets = service.worksheets()
            user_ids = []
            user_id_to_worksheets = {}
            for worksheet in worksheets:
                owner_id = worksheet['owner_id']
                if owner_id in user_id_to_worksheets:
                    user_id_to_worksheets[owner_id].append(worksheet)
                else:
                    user_id_to_worksheets[owner_id] = [worksheet]
                    user_ids.append(owner_id)
            if len(user_ids) > 0:
                users = ClUser.objects.filter(id__in=user_ids)
                for user in users:
                    for worksheet in user_id_to_worksheets[str(user.id)]:
                        worksheet['owner'] = user.username
            return Response(worksheets)
        except Exception as e:
            logging.error(self.__str__())
            logging.error(smart_str(e))
            logging.error('')
            logging.debug('-------------------------')
            tb = traceback.format_exc()
            logging.error(tb)
            logging.debug('-------------------------')
            return Response(status=service.http_status_from_exception(e))

    """
    Provides a web API to create a worksheet.
    """
    def post(self, request):
        owner = self.request.user
        if not owner.id:
            return Response(None, status=401)
        data = json.loads(request.body)
        worksheet_name = data['name'] if 'name' in data else ''
        logger.debug("WorksheetCreation: owner=%s; name=%s", owner.id, worksheet_name)
        if len(worksheet_name) <= 0:
            return Response("Invalid name.", status=status.HTTP_400_BAD_REQUEST)
        service = BundleService(self.request.user)
        try:
            data["uuid"] = service.create_worksheet(worksheet_name)
            logger.debug("WorksheetCreation def: owner=%s; name=%s; uuid", owner.id, data["uuid"])
            return Response(data)
        except Exception as e:
            logging.error(self.__str__())
            logging.error(smart_str(e))
            logging.error('')
            logging.debug('-------------------------')
            tb = traceback.format_exc()
            logging.error(tb)
            logging.debug('-------------------------')
            return Response(status=service.http_status_from_exception(e))

class WorksheetContentApi(views.APIView):
    """
    Provides a web API to fetch the content of a worksheet.
    """
    def get(self, request, uuid):
        user_id = self.request.user.id
        logger.debug("WorksheetContent: user_id=%s; uuid=%s.", user_id, uuid)
        service = BundleService(self.request.user)
        try:
            worksheet = service.worksheet(uuid, interpreted=True)
            owner = ClUser.objects.filter(id=worksheet['owner_id'])
            if owner:
                owner = owner[0]
                worksheet['owner'] = owner.username
            else:
                worksheet['owner'] = None
            return Response(worksheet)
        except Exception as e:
            logging.error(self.__str__())
            logging.error(smart_str(e))
            logging.error('')
            logging.debug('-------------------------')
            tb = traceback.format_exc()
            logging.error(tb)
            logging.debug('-------------------------')
            return Response(status=service.http_status_from_exception(e))

    """
    Provides a web API to update a worksheet.
    """
    def post(self, request, uuid):
        user = self.request.user
        if not user.id:
            return Response(None, status=401)
        data = json.loads(request.body)

        worksheet_name = data['name']
        worksheet_uuid = data['uuid']
        owner_id = data['owner_id']
        lines = data['lines']

        if not (worksheet_uuid == uuid):
            print "uui"
            return Response(None, status=403)

        logger.debug("WorksheetUpdate: owner=%s; name=%s; uuid=%s", owner_id, worksheet_name, uuid)
        service = BundleService(self.request.user)
        try:
            service.parse_and_update_worksheet(worksheet_uuid, lines)
            return Response({})
        except Exception as e:
            logging.error(self.__str__())
            logging.error(smart_str(e))
            logging.error('')
            logging.debug('-------------------------')
            tb = traceback.format_exc()
            logging.error(tb)
            logging.debug('-------------------------')
            return Response({'error': smart_str(e)})


class BundleInfoApi(views.APIView):
    """
    Provides a web API to obtain a bundle's primary information.
    """
    def get(self, request, uuid):
        user_id = self.request.user.id
        logger.debug("BundleInfo: user_id=%s; uuid=%s.", user_id, uuid)
        service = BundleService(self.request.user)
        try:
            bundle_info = service.get_bundle_info(uuid)
            print bundle_info
            bundle_info['edit_permission'] = False
            if bundle_info['owner_id'] == str(self.request.user.id):
                bundle_info['edit_permission'] = True
            return Response(bundle_info, content_type="application/json")
        except Exception as e:
            logging.error(self.__str__())
            logging.error(smart_str(e))
            logging.error('')
            logging.debug('-------------------------')
            tb = traceback.format_exc()
            logging.error(tb)
            logging.debug('-------------------------')
            return Response(status=service.http_status_from_exception(e))

    def post(self, request, uuid):
        user_id = self.request.user.id
        logger.debug("BundleInfo: user_id=%s; uuid=%s.", user_id, uuid)
        service = BundleService(self.request.user)

        try:
            bundle_info = service.get_bundle_info(uuid)
            if bundle_info['owner_id'] == str(self.request.user.id):
                data = json.loads(request.body)
                new_metadata = data['metadata']
                #clean up stuff
                if new_metadata.get('data_size', None):
                    new_metadata.pop('data_size')
                if new_metadata.get('created', None):
                    new_metadata.pop('created')
                if new_metadata.get('time', None):
                    new_metadata.pop('time')

                if new_metadata.get('tags', None):
                    tags = new_metadata['tags']
                    tags = tags.split(',')
                    new_metadata['tags'] = tags
                else:
                    new_metadata['tags'] = []

                if new_metadata.get('language', None) or new_metadata.get('language') ==  u'':
                    language = new_metadata['language']
                    language = language.split(',')
                    new_metadata['language'] = language

                if new_metadata.get('architectures', None):
                    architectures = new_metadata['architectures']
                    architectures = architectures.split(',')
                    new_metadata['architectures'] = architectures

                # update and return
                print new_metadata
                service.update_bundle_metadata(uuid, new_metadata)
                bundle_info = service.get_bundle_info(uuid)
            return Response(bundle_info, content_type="application/json")
        except Exception as e:
            logging.error(self.__str__())
            logging.error(smart_str(e))
            logging.error('')
            logging.debug('-------------------------')
            tb = traceback.format_exc()
            logging.error(tb)
            logging.debug('-------------------------')
            return Response({'error': smart_str(e)})

class BundleContentApi(views.APIView):
    """
    Provides a web API to browse the content of a bundle.
    """
    def get(self, request, uuid, path=''):
        user_id = self.request.user.id
        logger.debug("BundleContent: user_id=%s; uuid=%s; path=%s.", user_id, uuid, path)
        service = BundleService(self.request.user)
        try:
            target = (uuid, path)
            items = service.get_target_info(target, 2) # 2 is the depth to retrieve
            return Response(items)
        except Exception as e:
            logging.error(self.__str__())
            logging.error(smart_str(e))
            logging.error('')
            logging.debug('-------------------------')
            tb = traceback.format_exc()
            logging.error(tb)
            logging.debug('-------------------------')
            return Response({'error': smart_str(e)})
            #return Response(status=service.http_status_from_exception(e))

class BundleFileContentApi(views.APIView):
    """
    Provides a web API to read the content of a file in a bundle.
    """

    def get(self, request, uuid, path):
        # user_id = self.request.user.id
        service = BundleService(self.request.user)
        try:
            content_type, _encoding = mimetypes.guess_type(path)
            if not content_type:
                content_type = 'text/plain'
            return StreamingHttpResponse(service.read_file(uuid, path), content_type=content_type)
        except Exception as e:
            logging.error(self.__str__())
            logging.error(smart_str(e))
            logging.error('')
            logging.debug('-------------------------')
            tb = traceback.format_exc()
            logging.error(tb)
            logging.debug('-------------------------')
            return Response(status=service.http_status_from_exception(e))
