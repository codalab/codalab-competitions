from base import DevBase
from default import *
from configurations import Settings


class Dev(DevBase):
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
    

    COMPUTATION_SUBMISSION_URL = 'http://sdafsdafsadfsdaf.cloudapp.net/api/computation/'

    # CELERY CONFIG
    BROKER_URL = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND = "amqp"
    CELERY_TASK_RESULT_EXPIRES=3600
    ##

    DATABASES = {'default': {
            'ENGINE':  'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'MySQL_DevDB',                      # Or path to database file if using sqlite3.
            # The following settings are not used with sqlite3:
            'USER': 'b7850380393093',
            'PASSWORD': '04854030',
            'HOST': 'SERVERNAME.cleardb.com',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': '',                      # Set to empty string for default.
            

            }
   }
