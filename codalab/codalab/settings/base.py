from configurations import Settings
from configurations.utils import uppercase_attributes
import os,sys


class Base(Settings):
   SETTINGS_DIR=os.path.dirname(os.path.abspath(__file__))
   PROJECT_APP_DIR=os.path.dirname(SETTINGS_DIR)
   PROJECT_DIR=os.path.dirname(PROJECT_APP_DIR)
   ROOT_DIR=os.path.dirname(PROJECT_DIR)


   # Hosts/domain names that are valid for this site; required if DEBUG is False
   # See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
   ALLOWED_HOSTS = []
   DEBUG = True
   TEMPLATE_DEBUG = DEBUG
   SERVER_NAME = 'localhost'
   DOMAIN_NAME = 'localhost'
   PORT = '8000'

   ADMINS = (
      # ('Your Name', 'your_email@example.com'),
   )

   MANAGERS = ADMINS

   DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
         'NAME': 'dev_db.sqlite',                      # Or path to database file if using sqlite3.
         # The following settings are not used with sqlite3:
         'USER': '',
         'PASSWORD': '',
         'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
         'PORT': '',                      # Set to empty string for default.
     }
   }


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
   TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
   LANGUAGE_CODE = 'en-us'

   SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
   USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
   USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
   USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
   MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
   MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
   STATIC_ROOT = os.path.join(PROJECT_DIR,'static/')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
   STATIC_URL = '/static/'

# Additional locations of static files
   STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
   )

# List of finder classes that know how to find static files in
# various locations.
   STATICFILES_FINDERS = (
      'django.contrib.staticfiles.finders.FileSystemFinder',
      'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
      'compressor.finders.CompressorFinder',
   )

# Make this unique, and don't share it with anybody.
   SECRET_KEY = '+3_81$xxm9@3p5*wo3qpm7-4i2ixc8y4dl7do$p3-y63ynhxob'

# List of callables that know how to import templates from various sources.
   TEMPLATE_LOADERS = (
      'django.template.loaders.filesystem.Loader',
      'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
   )

   MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
   )

   ROOT_URLCONF = 'codalab.urls'

# Python dotted path to the WSGI application used by Django's runserver.
   WSGI_APPLICATION = 'codalab.wsgi.application'

   TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
   )

   TEMPLATE_CONTEXT_PROCESSORS = Settings.TEMPLATE_CONTEXT_PROCESSORS + (
     "allauth.account.context_processors.account",
     "allauth.socialaccount.context_processors.socialaccount",
   )

   AUTHENTICATION_BACKENDS = (
      "django.contrib.auth.backends.ModelBackend",
      "allauth.account.auth_backends.AuthenticationBackend",
      'guardian.backends.ObjectPermissionBackend',
     )

   INSTALLED_APPS = (
    
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    'django_config_gen',
    'compressor',
    'django_extensions',
    'django_js_reverse',
    'rest_framework',
    'guardian',
    'publish',


    'haystack',
    'apps.api',
    'apps.authenz', 
    'apps.web',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'debug_toolbar',
   )
   INTERNAL_IPS = ('127.0.0.1',)
   DEBUG_TOOLBAR_CONFIG = {
      'SHOW_TEMPLATE_CONTEXT': True,
      
      'ENABLE_STACKTRACES' : True,
      }
   LOGIN_REDIRECT_URL = '/my'

   AUTH_USER_MODEL = 'authenz.User'
   ANONYMOUS_USER_ID = -1

   ACCOUNT_AUTHENTICATION_METHOD='email'
   ACCOUNT_EMAIL_REQUIRED=True
   ACCOUNT_EMAIL_VERIFICATION='none'

   COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
    ('text/typescript', 'tsc {infile} --out {outfile}'),
    )
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
   LOGGING = {
      'version': 1,
      'disable_existing_loggers': False,
      'filters': {
          'require_debug_false': {
              '()': 'django.utils.log.RequireDebugFalse'
          }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
   }

   @classmethod
   def pre_setup(cls):
      try:
         import local_configuration
         lcls = getattr(local_configuration,os.environ.get('LOCAL_CONFIGURATION','Local'))
         for name,value in uppercase_attributes(lcls).items():
            setattr(cls,name,value)
      except ImportError as e:
         print e        
      if hasattr(cls,'ADDITIONAL_APPS'):
         cls.INSTALLED_APPS += cls.ADDITIONAL_APPS
      if hasattr(cls,'OPTIONAL_APPS'):
         for a in cls.OPTIONAL_APPS:
            try:
               __import__(a)
            except ImportError as e:
               print e               
            else:
               cls.INSTALLED_APPS += (a,)




