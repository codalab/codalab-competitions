"""
local.py

Examples for local configuration for various environments.

The objects ceated as here and referenced though the environment variable

"""
from base import DevBase
from default import *

from configurations import Settings

import os

class LocalEnvironment(object):
    """
    This creates the settings from environment variables that are set on the host.
    """
    DB_ENGINE = os.environ.get('DB_ENGINE')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_SERVER = os.environ.get('DB_SERVER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')

class LocalAzureBlobstore(object):
    DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
    AZURE_ACCOUNT_NAME = "accountname"
    AZURE_ACCOUNT_KEY = 'xaedadsf34fCjHpYAKOpRE1uSw3y37MaRSUtUYkj+o2..aoHg5YwasdfGCUgRXoT2WPNt+iaaz/6KB2Oiyz8Y7GT4=='
    AZURE_CONTAINER = 'containerx'


class LocalSQLAzureLinux(object):
    # See the docs at https://github.com/michiya/django-pyodbc-azure
    """
    This is the configuration that works for deploying the project on Linux on Azure.
    PyODBC is used in conjunction with FreeTDS and employing the django-pyodbc-azure
    FreeTDS and ODBC Connection definitons are required to connect.
    """

    DB_ENGINE = 'sql_server.pyodbc'
    DB_NAME = '_db_name_'
    DB_USER = '_user_name_@_host_name_'
    DB_SERVER = '_host_name_'
    DB_PASSWORD = '********'
    DB_HOST = '_host_name_.database.windows.net'
    DB_PORT = '1433'
    DB_OPTIONS =  {
        'driver': 'FreeTDS',
        'host_is_server': False
        }
  
    DATABASES = {
        'default': {
            'ENGINE':  DB_ENGINE, 
            'NAME': DB_NAME,                      
            
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_SERVER,                     
            'PORT': DB_PORT,                      # Set to empty string for default.
            
            'OPTIONS': DB_OPTIONS,
            }
        }

class LocalSQLAzureWindows(object):
    """
    This is the configuration that works for deploying the project on Windows on Azure.
    PyODBC is used as the bridge to the Windows ODBC connector. Also uses django-pyodbc-azure
    """
    # See the docs at https://github.com/michiya/django-pyodbc-azure
    DB_ENGINE = 'sql_server.pyodbc'
    DB_NAME = 'djangodb' # Database name for django
    DB_USER = 'db_user@xoagbc6d42' # Azure required usename@servername for db use
    DB_SERVER = 'xoagbc6d42'
    DB_PASSWORD = '********' 
    DB_HOST = 'xoagbc6d42.database.windows.net' # The Hostname of the SQL Server hosted on Azure
    DB_PORT = '1433'
    DB_OPTIONS =  {
        'driver': 'SQL Server Native Client 10.0', # The driver as specified by the Azure Management Console
	'dsn': 'codalab2', # This is the DSN defined in the ODBC Configuration
 	'extra_params': 'Encrypt=yes;Connection Timeout=30;', # The Extra params as specified by Azure

        }
  
    DATABASES = {
        'default': {
            'ENGINE':  DB_ENGINE, 
            'NAME': DB_NAME,                     
            
            'HOST': DB_HOST,                     
            # 'PORT': DB_PORT,                      # Set to empty string for default.
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'OPTIONS': DB_OPTIONS,
            }
        }


class Dev(DevBase,LocalSQLAzureLinux):
    ### https://docs.djangoproject.com/en/1.5/topics/settings/
    ### https://github.com/jezdez/django-configurations/blob/master/docs/index.rst

    ### https://docs.djangoproject.com/en/1.5/topics/email/#email-backends
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    #EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    #EMAIL_HOST = 'localhost'
    #EMAIL_PORT = '123'
    #EMAIL_HOST_USER = 'user'
    #EMAIL_HOST_PASSWORD = 'password'
    #EMAIL_USE_TLS = True

    
