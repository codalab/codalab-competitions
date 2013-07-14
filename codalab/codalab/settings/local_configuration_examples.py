"""
Examples for local configuration for various environments.

The objects ceated as here and referenced though the environment variable
"""
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


class LocalSQLAzureLinux(object):
    """
    This is the configuration that works for deploying the project on Linux on Azure.
    PyODBC is used in conjunction with FreeTDS and employing the django-pyodbc-azure
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
            'ENGINE':  DB_ENGINE, # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': DB_NAME,                      # Or path to database file if using sqlite3.
            # The following settings are not used with sqlite3:
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_SERVER,                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': DB_PORT,                      # Set to empty string for default.
            
            'OPTIONS': DB_OPTIONS,
            }
        }

