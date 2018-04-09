import uuid

from pyrabbit.api import Client

from django.conf import settings
from pyrabbit.http import HTTPError, NetworkError


def _get_rabbit_connection():
    """Helper giving us a rabbit connection from settings.BROKER_URL"""
    host_with_port = "{}:{}/api/".format(settings.RABBITMQ_HOST, settings.RABBITMQ_MANAGEMENT_PORT)
    scheme = 'https' if settings.BROKER_USE_SSL else 'http'
    return Client(host_with_port, settings.RABBITMQ_DEFAULT_USER, settings.RABBITMQ_DEFAULT_PASS, scheme=scheme)


def check_user_needs_initialization(user):
    conn = _get_rabbit_connection()

    try:
        conn.get_user_permissions(user.rabbitmq_username)
        # We found the user, no need to initialize
        return False
    except (HTTPError, NetworkError):
        # User not found, needs initialization
        return True


def initialize_user(user):
    """Check whether user has a rabbitmq account already, creates it if not."""
    print("Making new rabbitmq user for {}".format(user))
    user.rabbitmq_username = uuid.uuid4()
    user.rabbitmq_password = uuid.uuid4()

    conn = _get_rabbit_connection()
    conn.create_user(str(user.rabbitmq_username), str(user.rabbitmq_password))

    # Give user permissions to send submission updates
    conn.set_vhost_permissions(
        '/',
        str(user.rabbitmq_username),
        '.*',
        '.*submission-updates.*',
        '.*submission-updates.*'
    )

    # Was successful, save now
    user.save()


def create_queue(user):
    """Create a new queue with a random name and give full permissions to the owner AND our base account"""
    vhost = str(uuid.uuid4())
    conn = _get_rabbit_connection()
    conn.create_vhost(vhost)

    # Set permissions for our end user
    conn.set_vhost_permissions(
        vhost,
        user.rabbitmq_username,
        '.*',
        '.*',
        '.*'
    )

    # Set permissions for ourselves
    conn.set_vhost_permissions(
        vhost,
        settings.RABBITMQ_DEFAULT_USER,
        '.*',
        '.*',
        '.*'
    )

    return vhost


def delete_vhost(vhost):
    conn = _get_rabbit_connection()
    conn.delete_vhost(vhost)
