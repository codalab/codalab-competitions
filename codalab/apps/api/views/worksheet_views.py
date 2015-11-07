"""
Defines Django views for 'apps.api' app for worksheets.
"""
import json
import logging
import traceback
import mimetypes

from uuid import uuid4

from rest_framework import (permissions, status, viewsets, views, generics, filters)
from rest_framework.decorators import action, link, permission_classes
from rest_framework.exceptions import PermissionDenied, ParseError
from rest_framework.response import Response

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.http import Http404, StreamingHttpResponse
from django.template import Context
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_str

from apps.api import serializers
from apps.authenz.models import ClUser
from apps.jobs.models import Job
from apps.web import models as webmodels
from apps.web.bundles import BundleService
from apps.web.tasks import (create_competition, evaluate_submission)

from codalab.azure_storage import make_blob_sas_url, PREFERRED_STORAGE_X_MS_VERSION

logger = logging.getLogger(__name__)

def log_exception(func, exception, traceback):
    logging.error(func.__str__())
    logging.error(smart_str(exception))
    logging.error('')
    logging.error('-------------------------')
    logging.error(traceback)
    logging.error('-------------------------')

class WorksheetsListApi(views.APIView):
    """
    get: returns a list of worksheets.
    post: creates a new worksheet.
    """
    def get(self, request):
        user_id = self.request.user.id
        logger.debug("WorksheetsListApi: user_id=%s.", user_id)
        service = BundleService(self.request.user)
        try:
            worksheets = service.worksheets()
            return Response(worksheets)
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)

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
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)


class WorksheetsAddApi(views.APIView):
    """
    Provides a web API to add a bundle to a worksheet
    """
    def post(self, request):
        user = self.request.user
        if not user.id:
            return Response(None, status=401)
        data = json.loads(request.body)
        if not (data.get('worksheet_uuid', None) and data.get('bundle_uuid', None)):
            return Response("Must have worksheet uuid and bundle uuid", status=status.HTTP_400_BAD_REQUEST)
        logger.debug("WorksheetAdd: user=%s; name=%s", user.id, data['worksheet_uuid'])
        service = BundleService(self.request.user)
        try:
            data = service.add_worksheet_item(data['worksheet_uuid'], data['bundle_uuid'])
            return Response({
                'success': True,
                'data': data
                })
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)

class WorksheetsDeleteApi(views.APIView):
    """
    Provides a web API to add a bundle to a worksheet
    """
    def post(self, request):
        user = self.request.user
        if not user.id:
            return Response(None, status=401)
        data = json.loads(request.body)
        if not data.get('worksheet_uuid', None):
            return Response("Must have worksheet uuid", status=status.HTTP_400_BAD_REQUEST)
        logger.debug("Worksheetdelete: user=%s; name=%s", user.id, data['worksheet_uuid'])
        service = BundleService(self.request.user)
        try:
            data = service.delete_worksheet(data['worksheet_uuid'])
            return Response({
                'success': True,
                'data': data
                })
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)

class WorksheetsSearchApi(views.APIView):
    """
    Provides a web API to obtain a bundle's primary information.
    """
    def get(self, request):
        user_id = self.request.user.id
        search_string = request.GET.get('search_string', '')
        logger.debug("WorksheetSearch: user_id=%s; search_string=%s.", user_id, search_string)
        service = BundleService(self.request.user)
        try:
            worksheet_infos = service.search_worksheets(search_string.split(' '))
            data = {
                "worksheets": worksheet_infos,
                "search_string": search_string
            }
            return Response(data, content_type="application/json")
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)

class WorksheetsGetUUIDApi(views.APIView):
    """
    Provides a web API to obtain a bundle's primary information.
    """
    def get(self, request):
        user_id = self.request.user.id
        search_string = request.GET.get('spec', '')
        logger.debug("WorksheetsGetUUIDApi: user_id=%s; spec=%s.", user_id, search_string)
        service = BundleService(self.request.user)
        try:
            worksheet_uuid = service.get_worksheet_uuid(search_string)
            return Response({'uuid': worksheet_uuid}, content_type="application/json")
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)


class WorksheetsGetBundleListApi(views.APIView):
    """
    Provides a web API to obtain a bundle's primary information.
    """
    def get(self, request):
        user_id = self.request.user.id
        worksheet_uuid = request.GET.get('worksheet_uuid', '')
        logger.debug("WorksheetsGetBundleListApi: user_id=%s; worksheet_uuid=%s.", user_id, worksheet_uuid)
        service = BundleService(self.request.user)
        try:
            bundle_list = service.get_worksheet_bundles(worksheet_uuid)
            return Response({'bundles': bundle_list}, content_type="application/json")
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)


class WorksheetContentApi(views.APIView):
    '''
    get: get worksheet info (with all items)
    post: save worksheet info
    '''
    def get(self, request, uuid):
        user_id = self.request.user.id
        logger.debug("WorksheetContent: user_id=%s; uuid=%s.", user_id, uuid)
        service = BundleService(self.request.user)
        try:
            worksheet = service.full_worksheet(uuid)
            return Response(worksheet)
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)

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
            return Response(None, status=403)

        logger.debug("WorksheetUpdate: owner=%s; name=%s; uuid=%s", owner_id, worksheet_name, uuid)
        service = BundleService(self.request.user)
        try:
            service.parse_and_update_worksheet(worksheet_uuid, lines)
            return Response({})
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)

class WorksheetsCommandApi(views.APIView):
    """
    Run an arbitrary CLI command.
    """
    def post(self, request):
        user = self.request.user
        data = json.loads(request.body)
        service = BundleService(self.request.user)
        if data.get('raw_command', None):
            data['command'] = service.get_command(data['raw_command'])
        if not data.get('worksheet_uuid', None) or not data.get('command', None):
            return Response("Must have worksheet uuid and command", status=status.HTTP_400_BAD_REQUEST)

        service = BundleService(self.request.user)

        # If 'autocomplete' field is set, return a list of completions instead
        if data.get('autocomplete', False):
            return Response({
                'completions': service.complete_command(data['worksheet_uuid'], data['command'])
            })

        result = service.general_command(data['worksheet_uuid'], data['command'])
        if result['exception'] is None:
            return Response({
                'success': True,
                'data': result,
                'input_data': data
                })
        else:
            return Response(result['exception'], status=500)

############################################################

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
            if bundle_info is None:
                return Response({'error': 'The bundle is not availble'})
            bundle_info.update(service.get_bundle_contents(uuid))
            return Response(bundle_info, content_type="application/json")
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)

    def post(self, request, uuid):
        '''
        Save metadata information for a bundle.
        '''
        user_id = self.request.user.id
        logger.debug("BundleInfo: user_id=%s; uuid=%s.", user_id, uuid)
        service = BundleService(self.request.user)
        try:
            bundle_info = service.get_bundle_info(uuid)
            # Save only if we're the owner.
            if bundle_info['edit_permission']:
                data = json.loads(request.body)
                new_metadata = data['metadata']

                # TODO: do this generally based on the CLI specs.
                # Remove generated fields.
                for key in ['data_size', 'created', 'time', 'memory', 'exitcode', 'actions']:
                    if key in new_metadata:
                        del new_metadata[key]

                # Convert to arrays
                for key in ['tags', 'language', 'architectures']:
                    if key in new_metadata and isinstance(new_metadata[key], basestring):
                        new_metadata[key] = new_metadata[key].split(',')

                # Convert to ints
                for key in ['request_cpus', 'request_gpus', 'request_priority']:
                    if key in new_metadata:
                        new_metadata[key] = int(new_metadata[key])

                service.update_bundle_metadata(uuid, new_metadata)
                bundle_info = service.get_bundle_info(uuid)
                return Response(bundle_info, content_type="application/json")
            else:
                return Response({'error': 'Can\'t save unless you\'re the owner'})
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({'error': smart_str(e)})

class BundleSearchApi(views.APIView):
    """
    Provides a web API to obtain a bundle's primary information.
    """
    def get(self, request):
        user_id = self.request.user.id
        search_string = request.GET.get('search_string', '')
        worksheet_uuid = request.GET.get('worksheet_uuid', None) #if you want to filter it down to worksheet
        logger.debug("BundleSearch: user_id=%s; search_string=%s.", user_id, search_string)
        service = BundleService(self.request.user)
        try:
            bundle_infos = service.search_bundles(search_string.split(' '), worksheet_uuid)
            data = {
                "bundles": bundle_infos,
                "search_string": search_string
            }
            return Response(data, content_type="application/json")
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)

class BundleGetUUIDApi(views.APIView):
    """
    Provides a web API to obtain a bundle's primary information.
    """
    def get(self, request):
        user_id = self.request.user.id
        bundle_spec = request.GET.get('spec', '')
        worksheet_uuid = request.GET.get('worksheet_uuid', None)
        logger.debug("BundleGetUUIDApi: user_id=%s; spec=%s. worksheet_uuid=%s", user_id, bundle_spec, worksheet_uuid)
        service = BundleService(self.request.user)
        try:
            bundle_uuid = service.get_bundle_uuid(bundle_spec, worksheet_uuid)
            return Response({'uuid': bundle_uuid}, content_type="application/json")
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)

class BundleUploadApi(views.APIView):
    """
    Upload a bundle.
    """
    def post(self, request):
        user_id = self.request.user.id
        service = BundleService(self.request.user)
        try:
            source_file = request.FILES['file']
            bundle_type = request.POST['bundle_type']
            worksheet_uuid = request.POST['worksheet_uuid']
            new_bundle_uuid = service.upload_bundle(source_file, bundle_type, worksheet_uuid)
            return Response({'uuid': new_bundle_uuid}, content_type="application/json")
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)

class BundleContentApi(views.APIView):
    """
    Return files (map from file name to list of lines) inside the bundle.
    If |path| is unspecified, then return stdout and stderr for a bundle.
    """
    def get(self, request, uuid, path=''):
        user_id = self.request.user.id
        logger.debug("BundleContent: user_id=%s; uuid=%s; path=%s.", user_id, uuid, path)
        service = BundleService(self.request.user)
        try:
            target = (uuid, path)
            info = service.get_target_info(target)
            return Response(info)
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({'error': smart_str(e)})

class BundleFileContentApi(views.APIView):
    """
    Return a stream corresponding to the contents of a file in a bundle.
    """
    def get(self, request, uuid, path):
        service = BundleService(self.request.user)
        try:
            stream, name, content_type = service.read_target((uuid, path))
            response = StreamingHttpResponse(stream, content_type=content_type)
            response['Content-Disposition'] = 'filename="%s"' % name
            return response
        except Exception as e:
            tb = traceback.format_exc()
            log_exception(self, e, tb)
            return Response({"error": smart_str(e)}, status=500)
