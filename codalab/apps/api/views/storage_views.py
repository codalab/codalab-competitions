import datetime

from rest_framework import (permissions, status, views)
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.authenz.models import ClUser
from apps.health.models import CompetitionStorageDataPoint, UserStorageDataPoint, StorageSnapshot, StorageUsageHistory


@permission_classes((permissions.IsAuthenticated,))
class GetExistingStorageAnalytics(views.APIView):
    """
    Gets the last record of the storage analytics
    """
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")

        # Snapshot info
        data = {
            'created_at': None,
            'bucket': None,
            'total_usage': 0,
            'submissions_usage': 0,
            'datasets_usage': 0,
            'dumps_usage': 0,
            'bundle_usage': 0,
            'competitions_details': [],
            'users_details': []
        }
        last_storage_snapshot = StorageSnapshot.objects.order_by('id').last()
        if last_storage_snapshot:
            # Basic info
            data['created_at'] = last_storage_snapshot.created_at
            data['bucket'] = last_storage_snapshot.bucket_name
            data['total_usage'] = last_storage_snapshot.total_use

            # Competitions details
            competitions_details = []
            for competition_detail in list(CompetitionStorageDataPoint.objects.all()):
                data_point = {
                    'id': competition_detail.competition_id,
                    'title': competition_detail.title,
                    'creator': competition_detail.creator,
                    'is_active': competition_detail.is_active,
                    'submissions': competition_detail.submissions,
                    'datasets': competition_detail.datasets,
                    'dumps': competition_detail.dumps,
                    'bundle': competition_detail.bundle,
                    'total': competition_detail.total
                }
                competitions_details.append(data_point)
                data['submissions_usage'] += competition_detail.submissions
                data['datasets_usage'] += competition_detail.datasets
                data['dumps_usage'] += competition_detail.dumps
                data['bundle_usage'] += competition_detail.bundle
            data['competitions_details'] = competitions_details

            # Users details
            users_details = []
            for user_detail in list(UserStorageDataPoint.objects.all()):
                data_point = {
                    'id': user_detail.user_id,
                    'email': user_detail.email,
                    'username': user_detail.username,
                    'competitions': user_detail.competitions_total,
                    'datasets': user_detail.datasets_total,
                    'submissions': user_detail.submissions_total,
                    'total': user_detail.total
                }
                users_details.append(data_point)
            data['users_details'] = users_details

        return Response(data, status=status.HTTP_200_OK)


@permission_classes((permissions.IsAuthenticated,))
class GetStorageUsageHistory(views.APIView):
    """
    Gets the storage usage timeline between the 2 provided dates
    """
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")

        storage_usage_history = {}
        last_storage_snapshot = StorageSnapshot.objects.order_by('id').last()
        if last_storage_snapshot:
            date_from = self.request.query_params.get('from', (datetime.datetime.today() - datetime.timedelta(weeks=4)).strftime('%Y-%m-%d'))
            date_to = self.request.query_params.get('to', datetime.datetime.today().strftime('%Y-%m-%d'))
            query = StorageUsageHistory.objects.filter(bucket_name=last_storage_snapshot.bucket_name, at_date__gte=date_from, at_date__lt=date_to).order_by('-at_date')
            for su in query.order_by('-at_date'):
                storage_usage_history[su.at_date.isoformat()] = su.usage

        return Response(storage_usage_history, status=status.HTTP_200_OK)


@permission_classes((permissions.IsAuthenticated,))
class GetUserStorageAnalytics(views.APIView):
    """
    Gets storage use for users
    """
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")

        user_list = []
        qs = ClUser.objects.order_by('?').exclude(id=-1).exclude(username='AnonymousUser')
        for user in qs:
            user_list.append(user.get_storage_use_data())

        return Response(user_list, status=status.HTTP_200_OK)
