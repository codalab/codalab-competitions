from base import DevBase
from default import *
from configurations import Settings


class Dev(DevBase):

    # Azure storage
    DEFAULT_FILE_STORAGE = 'codalab.azure_storage.AzureStorage'
    AZURE_ACCOUNT_NAME = "accname"
    AZURE_ACCOUNT_KEY = 'asdfsdfsdafpRE1uSw3y37MaRSUtUYkj+o2//AaoHv5YwcqGCUgRXoT2WPNt+iaaz/6KB2Oiyz8Y7FPA=='
    AZURE_CONTAINER = 'containername'

    PRIVATE_FILE_STORAGE = 'codalab.azure_storage.AzureStorage'
    PRIVATE_AZURE_ACCOUNT_NAME = "acctname"
    PRIVATE_AZURE_ACCOUNT_KEY = "asdfsadfsadfdsalA8og4ApxsvZfiiWTsvthEiLmuJLyWrZ1VyDauwXDLClj+SZyKozFF65ZwnvQg=="
    PRIVATE_AZURE_CONTAINER = "containername"
    
    BUNDLE_AZURE_CONTAINER = "bundles"
    BUNDLE_AZURE_ACCOUNT_NAME = PRIVATE_AZURE_ACCOUNT_NAME
    BUNDLE_AZURE_ACCOUNT_KEY = PRIVATE_AZURE_ACCOUNT_KEY

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
