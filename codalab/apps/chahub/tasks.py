import json
import logging
from datetime import timedelta

import requests
from celery.task import task
from django.db import models
from django.db.models import Count
from django.utils import timezone

from django.conf import settings

from apps.authenz.models import ClUser
from apps.chahub.models import ChaHubSaveMixin
from apps.chahub.utils import ChahubException
from apps.web.models import Competition, ParticipantStatus, OrganizerDataSet, CompetitionParticipant, \
    CompetitionSubmission
from apps.web.utils import inheritors

logger = logging.getLogger(__name__)


def _send(endpoint, data):
    url = "{}{}".format(settings.CHAHUB_API_URL, endpoint)
    headers = {
        'Content-type': 'application/json',
        'X-CHAHUB-API-KEY': settings.CHAHUB_API_KEY,
    }
    logger.info("ChaHub :: Sending to ChaHub ({}) the following data: \n{}".format(url, data))
    return requests.post(url=url, data=json.dumps(data), headers=headers)


def get_obj(app_label, model_name, pk, include_deleted=False):
    Model = models.get_model(app_label, model_name)

    try:
        if include_deleted:
            obj = Model.objects.all_objects().get(pk=pk)
        else:
            obj = Model.objects.get(pk=pk)
    except Model.DoesNotExist:
        raise ChahubException("Could not find {} with pk: {}".format(app_label, pk))
    return obj


@task(queue='site-worker')
def send_to_chahub(app_label, model_name, pk, data, data_hash):
    """
    Does a post request to the specified API endpoint on chahub with the inputted data.
    """
    if not settings.CHAHUB_API_URL:
        raise ChahubException("CHAHUB_API_URL env var required to send to Chahub")
    if not settings.CHAHUB_API_KEY:
        raise ChahubException("No ChaHub API Key provided")

    obj = get_obj(app_label, model_name, pk)

    try:
        resp = _send(obj.get_chahub_endpoint(), data)
    except requests.exceptions.RequestException:
        resp = None

    if resp and resp.status_code in (200, 201):
        logger.info("ChaHub :: Received response {} {}".format(resp.status_code, resp.content))
        obj.chahub_timestamp = timezone.now()
        obj.chahub_data_hash = data_hash
        obj.chahub_needs_retry = False
    else:
        status = getattr(resp, 'status_code', 'N/A')
        body = getattr(resp, 'content', 'N/A')
        logger.info("ChaHub :: Error sending to chahub, status={}, body={}".format(status, body))
        obj.chahub_needs_retry = True
    obj.save(send=False)


@task(queue='site-worker')
def delete_from_chahub(app_label, model_name, pk):
    if not settings.CHAHUB_API_URL:
        raise ChahubException("CHAHUB_API_URL env var required to send to Chahub")
    if not settings.CHAHUB_API_KEY:
        raise ChahubException("No ChaHub API Key provided")

    obj = get_obj(app_label, model_name, pk, include_deleted=True)

    url = "{}{}{}/".format(settings.CHAHUB_API_URL, obj.get_chahub_endpoint(), pk)
    logger.info("ChaHub :: Sending to ChaHub ({}) delete message".format(url))

    headers = {'X-CHAHUB-API-KEY': settings.CHAHUB_API_KEY}

    try:
        resp = requests.delete(url=url, headers=headers)
    except requests.exceptions.RequestException:
        resp = None

    if resp and resp.status_code == 204:
        logger.info("ChaHub :: Received response {} {}".format(resp.status_code, resp.content))
        obj.delete()
    else:
        status = getattr(resp, 'status_code', 'N/A')
        body = getattr(resp, 'content', 'N/A')
        logger.info("ChaHub :: Error sending to chahub, status={}, body={}".format(status, body))
        obj.chahub_needs_retry = True
        obj.save(force_to_chahub=False)


def batch_send_to_chahub(model, limit=None, retry_only=False):
    qs = model.objects.all()
    if retry_only:
        qs = qs.filter(chahub_needs_retry=True)
    if limit is not None:
        qs = qs[:limit]

    endpoint = model.get_chahub_endpoint()
    data = [obj.get_chahub_data() for obj in qs if obj.get_chahub_is_valid()]
    if not data:
        logger.info('Nothing to send to Chahub at {}'.format(endpoint))
        return
    try:
        logger.info("Sending all data to Chahub at {}".format(endpoint))
        resp = _send(endpoint=endpoint, data=data)
        logger.info("Response Status Code: {}".format(resp.status_code))
        if resp.status_code != 201:
            logger.warning('ChaHub Response Content: {}'.format(resp.content))
    except ChahubException:
        logger.info("There was a problem reaching Chahub. Retry again later")


def chahub_is_up():
    if not settings.CHAHUB_API_URL:
        return False

    logger.info("Checking whether ChaHub is online before sending retries")
    try:
        response = requests.get(settings.CHAHUB_API_URL)
        if response.ok:
            logger.info("ChaHub is online")
            return True
        else:
            logger.info("Bad Status from ChaHub")
            return False
    except requests.exceptions.RequestException:
        # This base exception works for HTTP errors, Connection errors, etc.
        logger.info("Request Exception trying to access ChaHub")
        return False


def get_chahub_models():
    return inheritors(ChaHubSaveMixin)


@task(queue='site-worker')
def do_chahub_retries(limit=None):
    if not chahub_is_up():
        return
    chahub_models = get_chahub_models()
    logger.info('Retrying for ChaHub models: {}'.format(chahub_models))

    chahub_models = inheritors(ChaHubSaveMixin)
    for model in chahub_models:
        needs_retry = model.objects.filter(chahub_needs_retry=True)
        if limit:
            needs_retry = needs_retry[:limit]
        for instance in needs_retry:
            # Saving forces chahub update
            instance.save(force_to_chahub=True)

        # then delete all objects that need to be deleted
        objects_to_be_deleted = model.objects.all_objects().filter(
            chahub_timestamp__isnull=False,
            chahub_needs_retry=False,
            deleted=True
        )
        if limit is not None:
            objects_to_be_deleted = objects_to_be_deleted[:limit]
        for obj in objects_to_be_deleted:
            obj.delete(real_delete=True)


@task(queue='site-worker')
def send_everything_to_chahub(limit=None):
    if not chahub_is_up():
        return
    chahub_models = get_chahub_models()
    for model in chahub_models:
        batch_send_to_chahub(model, limit=limit)


@task(queue='site-worker')
def send_chahub_general_stats():
    if settings.DATABASES.get('default').get('ENGINE') == 'django.db.backends.postgresql_psycopg2':
        # Only Postgres supports 'distinct', so if we can use the database, if not use some Python Set magic
        organizer_count = Competition.objects.all().distinct('creator').count()
    else:
        users_with_competitions = list(ClUser.objects.filter(competitioninfo_creator__isnull=False))
        user_set = set(users_with_competitions)
        # Only unique users that have competitions
        organizer_count = len(user_set)
    approved_status = ParticipantStatus.objects.get(codename=ParticipantStatus.APPROVED)
    data = {
        'competition_count': Competition.objects.filter(published=True).count(),
        'dataset_count': OrganizerDataSet.objects.count(),
        'participant_count': CompetitionParticipant.objects.filter(status=approved_status).count(),
        'submission_count': CompetitionSubmission.objects.count(),
        'user_count': ClUser.objects.count(),
        'organizer_count': organizer_count
    }

    try:
        send_to_chahub('producers/{}/'.format(settings.CHAHUB_PRODUCER_ID), data)
    except requests.ConnectionError:
        logger.info("There was a problem reaching Chahub, it is currently offline. Re-trying in 5 minutes.")
        send_chahub_general_stats.apply_async(eta=timezone.now() + timedelta(minutes=5))


@task(queue='site-worker')
def send_chahub_updates():
    competitions = Competition.objects.filter(published=True).annotate(participant_count=Count('participants'))
    for comp in competitions:
        # saving generates new participant_count -- will be sent if it is different from
        # what was sent last time.
        comp.save()
