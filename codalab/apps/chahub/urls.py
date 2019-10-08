from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import ChaHubProvider


urlpatterns = default_urlpatterns(ChaHubProvider)
