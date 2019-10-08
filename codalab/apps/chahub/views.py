import requests
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView
from django.conf import settings

from .provider import ChaHubProvider

BASE_URL = settings.SOCIAL_AUTH_CHAHUB_BASE_URL


class ChaHubOAuth2Adapter(OAuth2Adapter):
    provider_id = ChaHubProvider.id

    api_url = '{}/api/v1/'.format(BASE_URL)
    authorize_url = '{}/oauth/authorize/'.format(BASE_URL)
    access_token_url = '{}/oauth/token/'.format(BASE_URL)
    identity_url = "{}my_profile/".format(api_url)

    supports_state = True

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token.token)
        uid = str(extra_data['id'])
        user = get_adapter().populate_new_user(
            email=extra_data.get('email'),
            username=extra_data.get('login'),
            name=extra_data.get('name')
        )
        account = SocialAccount(
            user=user,
            uid=uid,
            extra_data=extra_data,
            provider=self.provider_id
        )
        return SocialLogin(account)

    def get_data(self, token):
        data = requests.get(self.identity_url, headers={'Authorization': 'Bearer {}'.format(token)})
        data = data.json()
        return {
            'username': data.get('username'),
            'email': data.get('email'),
            'name': data.get('name', ''),
            'id': data.get('id'),
            'github_info': data.get('github_info', {})
        }


oauth2_login = OAuth2LoginView.adapter_view(ChaHubOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(ChaHubOAuth2Adapter)
