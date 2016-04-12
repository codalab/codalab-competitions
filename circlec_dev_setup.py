"""
Provide a template to define local configuration settings. Make a copy of this
file named 'local.py' and set appropriate values for the settings.
"""
from base import DevBase


class Dev(DevBase):
    '''
    This is needed to run circleci, it should be copied to local.py
    '''
    ENABLE_COMPETITIONS = True

    ENABLE_WORKSHEETS = False

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': '',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }
