from django.conf import settings
from social_core.backends.oauth import BaseOAuth2

BASE_URL = settings.SOCIAL_AUTH_CHAHUB_BASE_URL


class ChahubOAuth2(BaseOAuth2):
    """Chahub OAuth authentication backend"""
    name = 'chahub'
    API_URL = '{}/api/v1/'.format(BASE_URL)
    AUTHORIZATION_URL = '{}/oauth/authorize/'.format(BASE_URL)
    ACCESS_TOKEN_URL = '{}/oauth/token/'.format(BASE_URL)
    ACCESS_TOKEN_METHOD = 'POST'
    ID_KEY = 'id'

    def get_user_id(self, details, response):
        return details.get('id')

    def get_user_details(self, response):
        access_token = response['access_token']
        my_profile_url = "{}my_profile/".format(self.API_URL)
        data = self.get_json(my_profile_url, headers={'Authorization': 'Bearer {}'.format(access_token)})

        return {
            'username': data.get('username'),
            'email': data.get('email'),
            'name': data.get('name') if data.get('name') else '',
            'id': data.get('id'),
        }
