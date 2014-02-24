"""
View-related customatizations for auth.
"""

import json

from django.dispatch import receiver
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from allauth.account.signals import user_signed_up
from allauth.account.signals import user_logged_in

from oauth2_provider.models import AccessToken
from oauth2_provider.views.generic import ScopedProtectedResourceView

from apps.authenz.oauth import get_or_create_cli_client

#
# Implements hooks for additional processing post sign-up and post log-in.
#

@receiver(user_signed_up)
def new_user_signup(sender, **kwargs):
    """
    Handles bookkeeping after a user signs up.
    """
    user = kwargs['user']
    get_or_create_cli_client(user)

@receiver(user_logged_in)
def on_user_logged_in(sender, **kwargs):
    """
    Handles bookkeeping after a user signs up.
    """
    user = kwargs['user']
    # Backwards compatibility: do this for user who signed up before OAuth was added.
    get_or_create_cli_client(user)

#
# OAuth token validation API
#

class ValidationApi(ScopedProtectedResourceView):
    """
    Translates an OAuth token into information about the associated CodaLab user.
    """
    required_scopes = ['token-validation']

    @staticmethod
    def _translate_token(token, scopes):
        """
        When users try to access resources, check that provided token is valid
        """
        if token is None or len(token) <= 0:
            return {'code': 400}
        try:
            access_token = AccessToken.objects.select_related("application", "user").get(token=token)
            if access_token.is_valid(scopes):
                return {
                    'code': 200,
                    'user': {'id': access_token.user.id, 'name': access_token.user.username}
                }
            return {'code': 403}
        except AccessToken.DoesNotExist:
            return {'code': 404}
        except:
            return {'code': 500}

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ValidationApi, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        d = request.REQUEST
        token = d['token'] if 'token' in d else None
        scopes = d['scopes'] if 'scopes' in d else None
        response_data = ValidationApi._translate_token(token, scopes)
        return HttpResponse(json.dumps(response_data), content_type="application/json")
