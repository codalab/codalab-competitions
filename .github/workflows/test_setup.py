from .base import DevBase


class Test(DevBase):
    """This is used by GitHub actions, it should be copied to local.py"""
    ENABLE_COMPETITIONS = True
    ENABLE_WORKSHEETS = False
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    #DATABASES = {
    #    'default': {
    #        'ENGINE': 'django.db.backends.sqlite3',
    #        'NAME': ':memory:',
    #    }
    #}
