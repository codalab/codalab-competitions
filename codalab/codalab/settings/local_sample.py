from base import DevBase
from default import *
from configurations import Settings


class Dev(DevBase):

    # Azure storage
    DEFAULT_FILE_STORAGE = 'codalab.azure_storage.AzureStorage'
    AZURE_ACCOUNT_NAME = 'accname'
    AZURE_ACCOUNT_KEY = 'asdfsdfsdafpRE1uSw3y37MaRSUtUYkj+o2//AaoHv5YwcqGCUgRXoT2WPNt+iaaz/6KB2Oiyz8Y7FPA=='
    AZURE_CONTAINER = 'containername'

    BUNDLE_AZURE_ACCOUNT_NAME = 'accname'
    BUNDLE_AZURE_ACCOUNT_KEY = 'asdfsdfsdafpRE1uSw3y37MaRSUtUYkj+o2//AaoHv5YwcqGCUgRXoT2WPNt+iaaz/6KB2Oiyz8Y7FPA=='
    BUNDLE_AZURE_CONTAINER = 'bundles'

    # Bundle service
    BUNDLE_SERVICE_URL = ""
    BUNDLE_SERVICE_CODE_PATH = "..\\..\\..\\..\\bundles" # path relative to this file
    if len(BUNDLE_SERVICE_CODE_PATH) > 0:
        sys.path.append(join(dirname(abspath(__file__)), BUNDLE_SERVICE_CODE_PATH))
        codalab.__path__ = extend_path(codalab.__path__, codalab.__name__)

    # Service Bus
    SBS_NAMESPACE = '<enter name>'
    SBS_ISSUER = 'owner'
    SBS_ACCOUNT_KEY = '<enter key>'
    SBS_RESPONSE_QUEUE = '<enter queue name>' # incoming queue for site worker
    SBS_COMPUTE_QUEUE = '<enter queue name>'  # incoming queue for Windows compute worker

    DATABASES = {
        'default': {
            'ENGINE':  'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'MySQL_DevDB',                 # Or path to database file if using sqlite3.
            # The following settings are not used with sqlite3:
            'USER': 'someuser',
            'PASSWORD': 'somepassword',
            'HOST': 'someserver', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': '',           # Set to empty string for default.
        }
    }
