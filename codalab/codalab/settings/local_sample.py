"""
Provide a template to define local configuration settings. Make a copy of this
file named 'local.py' and set appropriate values for the settings.
"""
from base import DevBase
from default import *
from configurations import Settings

import sys
from os.path import dirname, abspath, join
from pkgutil import extend_path
import codalab

class Dev(DevBase):

    # Azure storage
    DEFAULT_FILE_STORAGE = 'codalab.azure_storage.AzureStorage'
    AZURE_ACCOUNT_NAME = 'your_account_name'
    AZURE_ACCOUNT_KEY = 'your_key_RE1uSw3y37MaRSUtUYkj+o2//AaoHv5YwcqGCUgRXoT2WPNt+iaaz/6KB2Oiyz8Y7FPA=='
    AZURE_CONTAINER = 'name_of_your_container_for_public_blobs'

    BUNDLE_AZURE_ACCOUNT_NAME = AZURE_ACCOUNT_NAME
    BUNDLE_AZURE_ACCOUNT_KEY = AZURE_ACCOUNT_KEY
    BUNDLE_AZURE_CONTAINER = 'name_of_your_private_container_for_bundles'

    # Bundle service: leave this URL blank to by-pass this functionality
    BUNDLE_SERVICE_URL = ""
    # Following config is necessary to use a bundle service
    # CODE_PATH points to local source code for bundles repo. Path is relative to this file.
    BUNDLE_SERVICE_CODE_PATH = "..\\..\\..\\..\\bundles"
    if len(BUNDLE_SERVICE_CODE_PATH) > 0:
        sys.path.append(join(dirname(abspath(__file__)), BUNDLE_SERVICE_CODE_PATH))
        codalab.__path__ = extend_path(codalab.__path__, codalab.__name__)
    # Bundle service DB information. These settings are used to generate the bundle
    # server config (see config\templats\bundle_server_config.json) using the command
    # 'python manage.py config_gen'
    BUNDLE_DB_NAME = 'bundles_db_name'
    BUNDLE_DB_USER = 'bundles_db_user'
    BUNDLE_DB_PASSWORD = 'bundles_db_password'

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
