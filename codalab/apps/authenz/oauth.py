"""
Implements CodaLab-specific requirements for OAuth.
"""

import logging

from datetime import timedelta
from django.utils import timezone
from oauth2_provider.models import (
    AccessToken,
    Application,
)
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.settings import oauth2_settings
from oauthlib.common import generate_token

logger = logging.getLogger(__name__)

#
# Customized OAuth validator
#

class Validator(OAuth2Validator):
    """
    Customizes the default validator.
    """

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        """
        Ensure required scopes are permitted (as specified in the settings file)
        """
        allowed_scopes = []
        if client.authorization_grant_type == Application.GRANT_CLIENT_CREDENTIALS:
            allowed_scopes = ['token-validation']
        return set(scopes).issubset(allowed_scopes)

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        return []

#
# Helpers to create a default client to allow any CodaLab user to use their web site credentials
# to connect their CLI client tool to the bundle service via OAuth protocol.
#

def cli_client_id(user):
    """Provides the default CLI Client ID associated with the given user in the OAuth provider store."""
    return 'cli_client_{0}'.format(user.username)

def get_or_create_cli_client(user):
    """
    Get or create a default OAuth client that the given user can use to authorize his CLI application.
    """
    client_id = cli_client_id(user)
    try:
        logger.debug("Attempting to create cli client %s", client_id)
        client, created = Application.objects.get_or_create(
                            client_id=client_id,
                            user=user,
                            client_type=Application.CLIENT_CONFIDENTIAL,
                            authorization_grant_type=Application.GRANT_PASSWORD,
                            client_secret='',
                            name=client_id)
        if created:
            logger.info("Created CLI client %s", client_id)
        else:
            logger.info("CLI client %s existed already", client_id)
        return client, created
    except:
        logger.exception("Failed to create CLI client %s.", client_id)
        return None, False

def get_user_token(user):
    """
    Returns an access token for the given user. This function facilitates
    interactions with the bundle service.
    """
    if user is None or not user.is_authenticated():
        return None

    client = Application.objects.get(client_id=cli_client_id(user))
    tokens = AccessToken.objects.filter(application_id=client.id,
                                        expires__gt=timezone.now() + timedelta(minutes=5))
    access_token = None
    for token in tokens:
        if token.is_valid([]):
            access_token = token
            break

    if access_token is None:
        access_token = AccessToken(
            user=user,
            scope='',
            expires=timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
            token=generate_token(),
            application=client)
        access_token.save()

    return str(access_token.token)
