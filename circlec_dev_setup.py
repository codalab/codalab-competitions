from base import DevBase


class Dev(DevBase):
    """This is needed to run circleci, it should be copied to local.py"""
    ENABLE_COMPETITIONS = True
    ENABLE_WORKSHEETS = False
    # CACHES = {
    #     'default': {
    #         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    #     }
    # }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
        'compressor': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'compressor'
        }
    }

    COMPRESS_CACHE_BACKEND = 'compressor'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
