from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class ChaHubAccount(ProviderAccount):
    pass


class ChaHubProvider(OAuth2Provider):
    """Chahub OAuth authentication backend"""

    id = 'chahub'
    name = 'ChaHub'
    account_class = ChaHubAccount
    package = 'apps.chahub'

    def get_default_scope(self):
        return ['read', 'write']


providers.registry.register(ChaHubProvider)
