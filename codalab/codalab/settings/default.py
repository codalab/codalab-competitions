import os
from .base import DevBase

__all__ = ['Dev']


class Dev(DevBase):
    # pass
    LOGIN_REDIRECT_URL = '/'
    ANONYMOUS_USER_ID = -1
    ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_USERNAME_REQUIRED = True
    ACCOUNT_EMAIL_VERIFICATION = os.environ.get('ACCOUNT_EMAIL_VERIFICATION', 'mandatory')
    ACCOUNT_SIGNUP_FORM_CLASS = 'apps.authenz.forms.CodalabSignupForm'
    ACCOUNT_LOGOUT_ON_GET = True

