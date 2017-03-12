import uuid
from urlparse import urlparse

from pyrabbit.api import Client

from django.conf import settings
from pyrabbit.http import HTTPError


def _extract_details_from_broker_url(broker_url):
    """Extracts the username and password from a broker url, in the form of:
    pyamqp://guest:guest@rabbit//"""
    # Start with 'pyamqp://name:pass@rabbit:123//'
    parts = urlparse(broker_url)
    # Grab 'name:pass@rabbit:123'
    netloc = parts.netloc
    # Grab 'name:pass' and 'rabbit:123'
    user_details, host = netloc.split('@')
    # Grab 'name' and 'pass'
    username, password = user_details.split(':')
    # Grab host without port 'rabbit'
    host_without_port = host.split(':')[0]
    host_with_port = "{}:{}".format(host_without_port, settings.RABBITMQ_MANAGEMENT_PORT)
    return host_with_port, username, password


def _get_rabbit_connection():
    """Helper giving us a rabbit connection from settings.BROKER_URL"""
    return Client(*_extract_details_from_broker_url(settings.BROKER_URL))


def check_user_needs_initialization(user):
    rabbit = _get_rabbit_connection()

    try:
        rabbit.get_user_permissions(user.rabbitmq_username)
        # We found the user, no need to initialize
        return False
    except HTTPError:
        # User not found, needs initialization
        return True


def initialize_user(user):
    """Check whether user has a rabbitmq account already, creates it if not."""
    print("Making new rabbitmq user for {}".format(user))
    user.rabbitmq_username = uuid.uuid4()
    user.rabbitmq_password = uuid.uuid4()

    rabbit = _get_rabbit_connection()
    rabbit.create_user(str(user.rabbitmq_username), str(user.rabbitmq_password))

    # Give user permissions to send submission updates
    rabbit.set_vhost_permissions(
        '/',
        user.rabbitmq_username,
        '.*',
        '.*submission-updates.*',
        '.*submission-updates.*'
    )

    # Was successful, save now
    user.save()


def create_queue(user):
    """Create a new queue with a random name and give full permissions to the owner AND our base account"""
    vhost = str(uuid.uuid4())
    rabbit = _get_rabbit_connection()
    rabbit.create_vhost(vhost)

    # Set permissions for our end user
    rabbit.set_vhost_permissions(
        vhost,
        user.rabbitmq_username,
        '.*',
        '.*',
        '.*'
    )

    # Set permissions for ourselves
    _, codalab_user, _ = _extract_details_from_broker_url(settings.BROKER_URL)
    rabbit.set_vhost_permissions(
        vhost,
        codalab_user,
        '.*',
        '.*',
        '.*'
    )

    return vhost


def delete_vhost(vhost):
    rabbit = _get_rabbit_connection()
    rabbit.delete_vhost(vhost)
